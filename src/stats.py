"""Statistical helpers for comparing two experiment arms."""
import numpy as np
from scipy import stats
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import confint_proportions_2indep, proportions_ztest


def two_proportion_test(y_a, y_b, alpha=0.05):
    """Compare the rate of a 0/1 outcome in arm A vs arm B.

    p-value: two-proportion z-test. CI on the difference: Newcombe (Wilson-based, reliable for small rates).
    CI on the relative lift: log-ratio method.
    """
    x = np.array([y_a.sum(), y_b.sum()])
    n = np.array([len(y_a), len(y_b)])
    p_a, p_b = x / n
    _, p_value = proportions_ztest(x, n)
    diff_lo, diff_hi = confint_proportions_2indep(x[0], n[0], x[1], n[1], method="newcomb",
                                                  compare="diff", alpha=alpha)
    ratio_lo, ratio_hi = confint_proportions_2indep(x[0], n[0], x[1], n[1], method="log",
                                                    compare="ratio", alpha=alpha)
    return {
        "value_a": p_a, "value_b": p_b, "diff": p_a - p_b, "diff_ci_low": diff_lo, "diff_ci_high": diff_hi,
        "rel_lift": p_a / p_b - 1, "rel_ci_low": ratio_lo - 1, "rel_ci_high": ratio_hi - 1, "p_value": p_value,
    }


def bootstrap_means(values, n_boot, rng, chunk=500):
    """Means of `n_boot` bootstrap resamples (sampling customers with replacement)."""
    values = np.asarray(values, dtype=float)
    out = np.empty(n_boot)
    for start in range(0, n_boot, chunk):
        stop = min(start + chunk, n_boot)
        idx = rng.integers(0, len(values), size=(stop - start, len(values)))
        out[start:stop] = values[idx].mean(axis=1)
    return out


def mean_difference_test(y_a, y_b, rng, n_boot=10_000, alpha=0.05):
    """Compare the mean of a continuous outcome (e.g. spend) in arm A vs arm B.

    CIs: percentile bootstrap (no distribution assumptions). p-value: Welch's t-test.
    Also returns the Welch CI as a cross-check and the bootstrap draws for plotting.
    """
    y_a, y_b = np.asarray(y_a, float), np.asarray(y_b, float)
    boot_a, boot_b = bootstrap_means(y_a, n_boot, rng), bootstrap_means(y_b, n_boot, rng)
    diffs, rel = boot_a - boot_b, boot_a / boot_b - 1
    q = [100 * alpha / 2, 100 * (1 - alpha / 2)]
    welch = stats.ttest_ind(y_a, y_b, equal_var=False)
    welch_ci = welch.confidence_interval(confidence_level=1 - alpha)
    return {
        "value_a": y_a.mean(), "value_b": y_b.mean(), "diff": y_a.mean() - y_b.mean(),
        "diff_ci_low": np.percentile(diffs, q[0]), "diff_ci_high": np.percentile(diffs, q[1]),
        "rel_lift": y_a.mean() / y_b.mean() - 1,
        "rel_ci_low": np.percentile(rel, q[0]), "rel_ci_high": np.percentile(rel, q[1]),
        "p_value": welch.pvalue, "welch_ci_low": welch_ci.low, "welch_ci_high": welch_ci.high,
        "boot_diffs": diffs,
    }


def holm(p_values, alpha=0.05):
    """Holm-adjusted p-values and reject flags for one family of comparisons."""
    reject, p_adj, _, _ = multipletests(p_values, alpha=alpha, method="holm")
    return p_adj, reject
