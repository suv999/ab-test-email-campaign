"""Evaluate targeting policies ("which e-mail does each segment get?") using the randomized experiment.

Because customers were randomly assigned, the customers in a given arm and segment are a fair sample of that
whole segment. So the average outcome *if every customer in segment s got arm a* is estimated by the observed
mean in that (segment, arm) cell, and a policy's value is the share-weighted average over segments.
"""
import numpy as np

ARMS = ["control", "mens", "womens"]


def cell_means(df, seg, metric):
    """Mean outcome per segment level (rows) and arm (columns)."""
    return df.groupby([seg, "treatment"], observed=True)[metric].mean().unstack()[ARMS]


def policy_value(df, seg, metric, policy):
    """Average outcome per customer if each segment level gets the arm named in `policy` (level -> arm)."""
    means = cell_means(df, seg, metric)
    shares = df[seg].value_counts(normalize=True)
    return sum(shares[level] * means.loc[level, arm] for level, arm in policy.items())


def uniform_policy(df, seg, arm):
    """Send the same arm to every segment level."""
    return {level: arm for level in df[seg].dropna().unique()}


def best_arm_policy(df, seg, metric, arms=ARMS):
    """Data-driven rule: give each segment level the arm with the highest observed mean."""
    return cell_means(df, seg, metric)[arms].idxmax(axis=1).to_dict()


def bootstrap_policy_difference(df, seg, metric, policy_a, policy_b, n_boot, rng):
    """Bootstrap draws of value(policy_a) - value(policy_b), resampling customers within each arm.

    Segment shares are held at their full-sample values (the customer base is known); only the
    per-cell outcome means are resampled.
    """
    levels = list(df[seg].cat.categories)
    codes = df[seg].cat.codes.to_numpy()
    y = df[metric].to_numpy(float)
    shares = np.bincount(codes, minlength=len(levels)) / len(df)
    w_a = {arm: np.array([shares[i] * (policy_a[l] == arm) for i, l in enumerate(levels)]) for arm in ARMS}
    w_b = {arm: np.array([shares[i] * (policy_b[l] == arm) for i, l in enumerate(levels)]) for arm in ARMS}

    diffs = np.zeros(n_boot)
    for arm in ARMS:
        weights = w_a[arm] - w_b[arm]
        if not weights.any():
            continue
        in_arm = (df.treatment == arm).to_numpy()
        c, v = codes[in_arm], y[in_arm]
        for b in range(n_boot):
            idx = rng.integers(0, len(v), len(v))
            sums = np.bincount(c[idx], weights=v[idx], minlength=len(levels))
            counts = np.bincount(c[idx], minlength=len(levels))
            diffs[b] += weights @ (sums / counts)
    return diffs


def crossfit_gain(df, seg, metric, baseline_arm, n_rep, rng, arms=ARMS):
    """Honest estimate of a data-driven rule's gain over sending `baseline_arm` to everyone.

    Each repetition splits customers 50/50 at random, learns the best-arm rule on one half and measures its
    gain on the other half, so the rule is never judged on the data that picked it.
    """
    gains = np.empty(n_rep)
    for r in range(n_rep):
        train_mask = rng.random(len(df)) < 0.5
        train, test = df[train_mask], df[~train_mask]
        rule = best_arm_policy(train, seg, metric, arms)
        gains[r] = (policy_value(test, seg, metric, rule)
                    - policy_value(test, seg, metric, uniform_policy(test, seg, baseline_arm)))
    return gains
