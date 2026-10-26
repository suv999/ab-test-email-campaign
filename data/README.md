# Dataset: Hillstrom E-Mail Marketing Experiment (MineThatData, 2008)

**File:** `raw/hillstrom_email_experiment.csv` — 64,000 rows × 12 columns, no missing values
**SHA-256:** `0e5893329d8b93cefecc571777672028290ab69865718020c78c7284f291aece`

## What it is
Real customer data released by Kevin Hillstrom (former VP of Database Marketing, Nordstrom / Eddie Bauer) for the
*MineThatData E-Mail Analytics and Data Mining Challenge* (March 2008). It comes from a real retailer: 64,000
customers who had purchased within the last 12 months were **randomly assigned** to one of three groups:

| Group (`segment`) | Customers | Treatment |
|---|---|---|
| Mens E-Mail | 21,307 | Received an e-mail campaign featuring men's merchandise |
| Womens E-Mail | 21,387 | Received an e-mail campaign featuring women's merchandise |
| No E-Mail | 21,306 | Control: received nothing |

Outcomes were tracked for the **two weeks** following the e-mail.

## Columns
| Column | Type | Meaning |
|---|---|---|
| `recency` | int 1–12 | Months since last purchase |
| `history_segment` | category | Bucketed dollars spent in the past year (7 bins) |
| `history` | float | Actual dollars spent in the past year |
| `mens` | 0/1 | Bought men's merchandise in the past year |
| `womens` | 0/1 | Bought women's merchandise in the past year |
| `zip_code` | category | Urban / Surburban (sic) / Rural |
| `newbie` | 0/1 | New customer in the past 12 months |
| `channel` | category | Channels purchased from in the past year: Phone / Web / Multichannel |
| `segment` | category | **Treatment group** (see above) |
| `visit` | 0/1 | Visited the website within 2 weeks |
| `conversion` | 0/1 | Purchased within 2 weeks |
| `spend` | float | Dollars spent within 2 weeks (0 for non-buyers; max $499) |

## Validation (matches published challenge figures)
| Group | Visit rate | Conversion rate | Spend / customer |
|---|---|---|---|
| Mens E-Mail | 18.28% | 1.25% | $1.42 |
| Womens E-Mail | 15.14% | 0.88% | $1.08 |
| No E-Mail | 10.62% | 0.57% | $0.65 |

## Notes for the analysis
- **Spend is extremely skewed:** only 578 of 64,000 customers (0.9%) bought anything. Use bootstrap CIs or
  Welch's t-test with care, not a plain t-test on raw means.
- Three arms → multiple comparisons (Mens vs control, Womens vs control, Mens vs Womens); apply Holm/Bonferroni.
- Pre-treatment covariates (`recency`, `history`, `mens`, `womens`, `zip_code`, `newbie`, `channel`) allow a
  balance check and CUPED-style variance reduction.
- Data is from 2008 and in USD; the retailer is unnamed.

## Sources
- Original challenge announcement: https://blog.minethatdata.com/2008/03/minethatdata-e-mail-analytics-and-data.html
- scikit-uplift dataset docs: https://www.uplift-modeling.com/en/latest/api/datasets/fetch_hillstrom.html
- Kaggle mirror: https://www.kaggle.com/datasets/bofulee/kevin-hillstrom-minethatdata-e-mailanalytics/data
- Copy obtained from GitHub mirror: https://github.com/yifanl6/hillstrom-email-ab-test (`data/hillstrom.csv`)
