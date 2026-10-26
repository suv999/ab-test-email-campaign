# CLAUDE.md — Hillstrom E-Mail A/B Test Case Study

## Project
A portfolio A/B testing case study for a Data/Business Analyst job search in Sweden. Hiring managers and analysts
will read it, so write in clear English with the business answer first. Every result should say what it means for
the retailer.

**Business question:** should the retailer send the **men's e-mail**, the **women's e-mail**, or **target each
campaign at specific customer segments**?

## Data
- Raw file: `data/raw/hillstrom_email_experiment.csv`. This is the real Hillstrom MineThatData e-mail experiment
  (2008): 64,000 customers, 12 columns, no missing values.
- Three randomized arms (`segment`): Mens E-Mail (21,307), Womens E-Mail (21,387), No E-Mail (21,306, control).
- **Read `data/README.md` first.** It has the column dictionary, the SHA-256 checksum, the published validation
  figures, and analysis notes.
- Key facts:
  - Outcomes (`visit`, `conversion`, `spend`) cover the 2 weeks after the e-mail.
  - `spend` is heavily zero-inflated: only 578 customers bought anything.
  - Amounts are USD from 2008.
  - `zip_code` uses the original spelling "Surburban" (sic). Keep that spelling in raw data, and relabel only in
    processed data or charts.

## Hard rules
1. **Never modify the raw CSV.** Do not overwrite, re-save, or edit anything in `data/raw/`. Read it only.
   Before analysis, check its SHA-256 against the value in `data/README.md`.
2. **Save cleaned or derived data to `data/processed/`** (create the folder if it is missing). Use descriptive names,
   e.g. `data/processed/hillstrom_clean.parquet`.
3. **Explain every statistical choice in plain English** in a markdown cell next to the code: what the method is,
   why it fits here (and why the obvious alternatives don't), and how to read the result in business terms.
   Assume the reader is a smart non-statistician.
4. **Sanity-check the data:** reproduce the validation table in `data/README.md` (visit rate, conversion rate,
   spend per customer by arm) before doing anything else.

## Environment
- Python 3.12 venv at `C:\Users\manuj\.venv`, with pandas, numpy, scipy, statsmodels, matplotlib, seaborn,
  JupyterLab, and nbconvert.
  - Interpreter: `C:\Users\manuj\.venv\Scripts\python.exe`
  - Jupyter: `C:\Users\manuj\.venv\Scripts\jupyter.exe lab`
  - Run a notebook headless: `C:\Users\manuj\.venv\Scripts\jupyter.exe nbconvert --to notebook --execute --inplace notebooks/<name>.ipynb`
- Write multi-line Python to a `.py` file and run that file. Do not pipe inline code into `python -c`.
- Install new packages only after asking the user.

## Layout
```
data/raw/          original CSV (read-only)
data/processed/    cleaned / derived datasets
notebooks/         numbered analysis notebooks, e.g. 01_data_check, 02_ab_test, 03_segments
src/               reusable helpers (stats functions, plotting style) imported by notebooks
figures/           exported charts (PNG)
reports/           stakeholder-facing summary / recommendation
```
Notebooks must run top to bottom without errors. Before committing, clear stale outputs or re-execute.

## Analysis conventions
- Set `ALPHA = 0.05` and a fixed random seed (e.g. `SEED = 42`) at the top of each notebook.
- **Randomization checks:**
  - Sample-ratio mismatch (SRM) test on arm sizes (chi-square goodness of fit).
  - Covariate balance on the pre-treatment variables (`recency`, `history`, `mens`, `womens`, `zip_code`,
    `newbie`, `channel`), reported as standardized mean differences plus chi-square tests for categoricals.
- **Metrics:** visit rate, conversion rate, and spend per customer. Report each as absolute lift (percentage
  points or $) and relative lift vs control, with 95% CIs.
- **Tests:**
  - Binary outcomes: two-proportion z-test with a CI on the difference.
  - Spend: bootstrap CIs (and Welch's t-test as a cross-check). Do not use a plain Student t-test on the raw,
    skewed spend.
- **Multiple comparisons:** three pairwise comparisons (Mens vs control, Womens vs control, Mens vs Womens),
  adjusted with Holm.
- **Variance reduction (optional):** CUPED or regression adjustment on pre-treatment covariates. Explain it as
  "removing noise we could already predict".
- **Targeting / segments:**
  - Estimate heterogeneous treatment effects across `mens`/`womens` purchase history, `history_segment`,
    `channel`, `zip_code`, `newbie`, and `recency`.
  - Prefer regression with treatment × segment interaction terms (statsmodels) over many separate tests.
  - Correct for multiplicity.
  - Label subgroup findings as **exploratory**, i.e. hypotheses to confirm in a follow-up test.
- **Business framing:** lead with effect sizes and money (e.g. incremental revenue per 1,000 e-mails sent), not only
  p-values. Separate statistical significance from practical significance.

## Charts
- Use matplotlib/seaborn. Give every chart a descriptive title, labeled axes with units, and CI error bars where
  relevant.
- Keep arm colors the same across all charts (define them once in `src/`).
- Save to `figures/` as PNG at ≥150 dpi with descriptive filenames.

## Deliverable
End with a clear recommendation that answers the business question: men's e-mail, women's e-mail, or a targeting
rule. Back it with the numbers and state the caveats:
- the data is from 2008
- the outcome window is only 2 weeks
- there is no e-mail cost or margin data, so state any cost assumptions explicitly
- segment findings are exploratory

Put the stakeholder summary in `reports/`.
