"""Loading, verifying and cleaning the Hillstrom data. The raw CSV is only ever read, never written."""
import hashlib
from pathlib import Path

import pandas as pd

from src.style import ARM_ORDER

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "hillstrom_email_experiment.csv"
CLEAN_PATH = ROOT / "data" / "processed" / "hillstrom_clean.csv"

# Published checksum of the raw file (see data/README.md).
RAW_SHA256 = "0e5893329d8b93cefecc571777672028290ab69865718020c78c7284f291aece"

HISTORY_SEGMENT_ORDER = [
    "1) $0 - $100",
    "2) $100 - $200",
    "3) $200 - $350",
    "4) $350 - $500",
    "5) $500 - $750",
    "6) $750 - $1,000",
    "7) $1,000 +",
]
ZIP_ORDER = ["Urban", "Suburban", "Rural"]
CHANNEL_ORDER = ["Phone", "Web", "Multichannel"]
TREATMENT_MAP = {"No E-Mail": "control", "Mens E-Mail": "mens", "Womens E-Mail": "womens"}

PRE_TREATMENT_NUMERIC = ["recency", "history", "mens", "womens", "newbie"]
PRE_TREATMENT_CATEGORICAL = ["history_segment", "zip_code", "channel"]
OUTCOMES = ["visit", "conversion", "spend"]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_raw():
    """Read the raw CSV as-is."""
    return pd.read_csv(RAW_PATH)


def _apply_dtypes(df):
    df["segment"] = pd.Categorical(df["segment"], categories=ARM_ORDER, ordered=False)
    df["treatment"] = pd.Categorical(df["treatment"], categories=list(TREATMENT_MAP.values()))
    df["history_segment"] = pd.Categorical(df["history_segment"], categories=HISTORY_SEGMENT_ORDER, ordered=True)
    df["zip_code"] = pd.Categorical(df["zip_code"], categories=ZIP_ORDER)
    df["channel"] = pd.Categorical(df["channel"], categories=CHANNEL_ORDER)
    return df


def clean(raw):
    """Return a cleaned copy: fixed 'Surburban' typo, ordered categories, treatment flags."""
    df = raw.copy()
    df["zip_code"] = df["zip_code"].replace({"Surburban": "Suburban"})
    df["treatment"] = df["segment"].map(TREATMENT_MAP)
    df["emailed"] = (df["treatment"] != "control").astype(int)
    return _apply_dtypes(df)


def load_clean():
    """Read the processed CSV and restore categorical dtypes (CSV does not store them)."""
    return _apply_dtypes(pd.read_csv(CLEAN_PATH))


# Segment variables for the targeting analysis: column -> readable name.
# Small groups are merged so each segment has roughly 1,000+ customers per arm.
SEGMENTS = {
    "purchase_history": "Past purchases",
    "history_tier": "Spend in past year",
    "recency_band": "Months since last purchase",
    "channel": "Purchase channel",
    "zip_code": "Area",
    "customer_type": "Customer type",
}
HISTORY_TIER_MAP = {
    "1) $0 - $100": "under $100",
    "2) $100 - $200": "$100–350", "3) $200 - $350": "$100–350",
    "4) $350 - $500": "$350–750", "5) $500 - $750": "$350–750",
    "6) $750 - $1,000": "$750+", "7) $1,000 +": "$750+",
}


def add_segments(df):
    """Add the readable segment columns defined in SEGMENTS (built only from pre-treatment variables)."""
    df = df.copy()
    purchase = pd.Series("Both", index=df.index)
    purchase[(df.mens == 1) & (df.womens == 0)] = "Men's only"
    purchase[(df.mens == 0) & (df.womens == 1)] = "Women's only"
    df["purchase_history"] = pd.Categorical(purchase, categories=["Men's only", "Women's only", "Both"])
    df["history_tier"] = pd.Categorical(df.history_segment.astype(str).map(HISTORY_TIER_MAP),
                                        categories=["under $100", "$100–350", "$350–750", "$750+"])
    df["recency_band"] = pd.cut(df.recency, [0, 3, 6, 9, 12],
                                labels=["1–3 months", "4–6 months", "7–9 months", "10–12 months"])
    df["customer_type"] = pd.Categorical(df.newbie.map({0: "Existing", 1: "New (past 12 months)"}),
                                         categories=["Existing", "New (past 12 months)"])
    return df
