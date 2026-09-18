#!/usr/bin/env python3
"""Is misinformation MORE concentrated than news, or just rarer?

THE OBJECTION. Section 2.8 reports that the top 1% of users account for a median 70% of
misinformation activity against 31% of general-news activity, and reads the gap as a fact about
misinformation. A rarer behaviour is more concentrated by construction: if every user were equally
likely to touch misinformation, the users who happen to touch it at all would still be the heaviest
users, and thinning a heavy-tailed activity distribution adds sampling noise that concentrates the
top further. Part of the 2x could be arithmetic rather than behaviour. The review has to run that
null rather than assume it away.

THE NULL. Users' total activity is lognormal, calibrated so the top 1% hold the share of general
news the comparison panels actually report (~31%). Every item a user touches is misinformation with
the SAME probability p, independent of the user: misinformation propensity is held constant by
construction, so any concentration gap the simulation produces is pure base-rate arithmetic. p is
swept across the range of misinformation base rates the corpus reports. For each p the simulation
records the share of misinformation activity held by the top 1% of users ranked by misinformation
count, and the ratio of that to the general-news share.

WHAT IT DECIDES. If the observed within-panel ratios (1.5, 2.3, 2.5, 2.6; median 2.4, from
review_matched_concentration.csv) sit inside the null's range, section 2.8's claim is not
supportable. If they sit above it, the claim survives and the null is the evidence for it.

Inputs : data/synth/phaseB/review_matched_concentration.csv (the observed within-panel ratios)
Outputs: data/synth/phaseB/concentration_null.csv   (one row per p, with the null ratio)
         data/synth/phaseB/concentration_null.json  (the summary the manuscript quotes)

Run: python3 scripts/phaseB_concentration_null.py
"""

import csv
import json
import math
import os
import random
import statistics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data/synth/phaseB")

SEED = 20260915
N_USERS = 20_000          # a large behavioural panel; the result is insensitive above a few thousand
MEAN_ITEMS = 120          # mean news items per user over a study window
TARGET_GENERAL = 0.31     # top-1% share of general-news activity the comparison panels report
P_GRID = [0.005, 0.01, 0.02, 0.05, 0.10, 0.13, 0.20]
N_REPS = 40               # replications per p; the spread across reps is reported, not hidden


def top_share(counts, frac=0.01):
    """Share of total activity held by the top `frac` of users, ranked by that same activity."""
    ordered = sorted(counts, reverse=True)
    k = max(1, int(round(len(ordered) * frac)))
    total = sum(ordered)
    return (sum(ordered[:k]) / total) if total else 0.0


def calibrate_sigma(rng, target, lo=0.5, hi=4.0, tol=0.002):
    """Find the lognormal sigma whose top-1% activity share matches the observed general-news one."""
    for _ in range(40):
        mid = (lo + hi) / 2
        mu = math.log(MEAN_ITEMS) - mid * mid / 2
        act = [rng.lognormvariate(mu, mid) for _ in range(N_USERS)]
        s = top_share(act)
        if abs(s - target) < tol:
            return mid, s
        if s < target:
            lo = mid
        else:
            hi = mid
    return mid, s


def main():
    rng = random.Random(SEED)
    sigma, general_share = calibrate_sigma(rng, TARGET_GENERAL)
    mu = math.log(MEAN_ITEMS) - sigma * sigma / 2

    rows = []
    for p in P_GRID:
        shares = []
        for _ in range(N_REPS):
            # One draw of user activity, then a constant-propensity thinning into misinformation.
            act = [max(1, int(rng.lognormvariate(mu, sigma))) for _ in range(N_USERS)]
            misinfo = [sum(1 for _ in range(a) if rng.random() < p) for a in act]
            shares.append(top_share(misinfo))
        rows.append({
            "p_misinfo": p,
            "null_top1_misinfo_share_pct": round(100 * statistics.median(shares), 1),
            "null_min_pct": round(100 * min(shares), 1),
            "null_max_pct": round(100 * max(shares), 1),
            "null_ratio": round(statistics.median(shares) / general_share, 2),
            "n_reps": N_REPS,
        })

    obs_path = os.path.join(OUT, "review_matched_concentration.csv")
    observed = []
    if os.path.exists(obs_path):
        for r in csv.DictReader(open(obs_path, encoding="utf-8")):
            if r["study"].startswith("MEDIAN"):
                continue          # the file carries its own summary row; counting it double-counts
            for key in ("matched_ratio", "ratio", "ratio_misinfo_over_general"):
                if r.get(key):
                    observed.append(float(r[key]))
                    break

    null_ratios = [r["null_ratio"] for r in rows]
    summary = {
        "seed": SEED, "n_users": N_USERS, "mean_items": MEAN_ITEMS, "n_reps": N_REPS,
        "calibrated_sigma": round(sigma, 3),
        "general_top1_share_pct": round(100 * general_share, 1),
        "null_ratio_min": min(null_ratios), "null_ratio_max": max(null_ratios),
        "observed_ratios": sorted(observed),
        "observed_median": round(statistics.median(observed), 2) if observed else None,
        "observed_min": min(observed) if observed else None,
        "verdict": ("observed ratios lie above the null" if observed and min(observed) > max(null_ratios)
                    else "observed ratios overlap the null — the claim is not supportable as stated"),
    }

    with open(os.path.join(OUT, "concentration_null.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(OUT, "concentration_null.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"calibrated sigma {sigma:.3f} -> general-news top 1% = {100*general_share:.1f}% "
          f"(target {100*TARGET_GENERAL:.0f}%)")
    for r in rows:
        print(f"  p = {r['p_misinfo']:<6} top 1% holds {r['null_top1_misinfo_share_pct']:>5}% "
              f"of misinformation  (ratio x{r['null_ratio']})")
    print(f"null ratio range: x{min(null_ratios)} to x{max(null_ratios)}")
    if observed:
        print(f"observed within-panel ratios: {sorted(observed)} (median "
              f"x{statistics.median(observed):.2f})")
    print(summary["verdict"])


if __name__ == "__main__":
    main()
