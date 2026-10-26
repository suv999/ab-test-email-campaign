"""Shared plotting style so every chart in the project uses the same arm order and colours."""
import matplotlib.pyplot as plt
import seaborn as sns

# Raw `segment` values, in the order they should appear in tables and charts (control first).
ARM_ORDER = ["No E-Mail", "Mens E-Mail", "Womens E-Mail"]

# Short labels for charts and tables.
ARM_LABELS = {
    "No E-Mail": "Control (no e-mail)",
    "Mens E-Mail": "Men's e-mail",
    "Womens E-Mail": "Women's e-mail",
}

# One fixed colour per arm, used everywhere. Control is neutral grey.
ARM_COLORS = {
    "No E-Mail": "#8c8c8c",
    "Mens E-Mail": "#2a6fdb",
    "Womens E-Mail": "#e8853d",
}

FIG_DPI = 150


def set_style():
    """Apply the project-wide matplotlib/seaborn look."""
    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams.update({
        "figure.dpi": 100,
        "savefig.dpi": FIG_DPI,
        "savefig.bbox": "tight",
        "axes.titleweight": "bold",
        "axes.spines.top": False,
        "axes.spines.right": False,
    })
