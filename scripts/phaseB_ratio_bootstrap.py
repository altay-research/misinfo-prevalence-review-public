#!/usr/bin/env python3
"""phaseB_ratio_bootstrap.py -- bootstrap CIs for the BETWEEN-construct ratios.

The manuscript's headline contrast is stated as a multiplier ("the share of people who
report seeing misinformation is ~20x the share of the diet that is misinformation").
Until now that multiplier was a point ratio of two medians with no uncertainty attached.
This script gives each headline ratio a study-cluster bootstrap 95% CI, using EXACTLY the
same primary set, study-median logic, seed policy and resampling scheme as
phaseB_uncertainty.py (resample studies, not estimates).

Ratios reported (numerator median / denominator median per bootstrap replicate):
  RECALL / EXPOSURE            -- perception vs measured diet share
  CONTENT / EXPOSURE           -- curated-sample content share vs measured diet share
  RECALL / WHOLE-DIET backbone -- perception vs the broadest audience-diet quantity
  CONTENT / WHOLE-DIET backbone

Statistical notes:
 - Groups are resampled INDEPENDENTLY. A few studies contribute estimates to more than
   one construct, so replicates are not perfectly independent across groups; the effect
   on a ratio CI is second-order and conservative directionality is not affected.
 - Percentile CI, 2000 replicates, fixed seed (same constants as phaseB_uncertainty.py).

Input : frozen dataset resolved from docs/FROZEN.md (never hardcoded)
Output: data/synth/phaseB/ratio_bootstrap.csv

Run: python3 scripts/phaseB_ratio_bootstrap.py
"""

import csv
import random
import re
import statistics as st
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/synth/phaseB"
SEED = 20260723
BOOT = 2000
random.seed(SEED)

WHOLE_DIET_DENOM = {"all_media", "news_diet", "population", "political_news"}


def load_main_set():
    """Identical filter to phaseB_uncertainty.load_main_set()."""
    frozen_path = re.search(r"File:\s*(\S+)", (ROOT / "docs/FROZEN.md").read_text()).group(1)
    fr = list(csv.DictReader(open(ROOT / frozen_path, encoding="utf-8")))
    out = []
    for r in fr:
        if r["value_kind"] != "proportion" or r["demographic_group"].strip() or not r["value_pct"].strip():
            continue
        out.append({"study_id": r["id"], "construct": r["construct"], "recall_subtype": r.get("recall_subtype",""),
                    "denom_class": r["denom_class"], "value_pct": float(r["value_pct"])})
    return out


def study_medians(rows):
    by = defaultdict(list)
    for r in rows:
        by[r["study_id"]].append(r["value_pct"])
    return [st.median(v) for v in by.values()]


def boot_ratio(num_pts, den_pts):
    """Study-cluster bootstrap of median(num)/median(den), percentile 95% CI."""
    ratios = []
    for _ in range(BOOT):
        num = [num_pts[random.randrange(len(num_pts))] for _ in num_pts]
        den = [den_pts[random.randrange(len(den_pts))] for _ in den_pts]
        d = st.median(den)
        if d > 0:
            ratios.append(st.median(num) / d)
    ratios.sort()
    lo = ratios[int(0.025 * len(ratios))]
    hi = ratios[int(0.975 * len(ratios)) - 1]
    return lo, hi


def main():
    rows = load_main_set()

    def grp(construct):
        return study_medians([r for r in rows if r["construct"] == construct])

    backbone = study_medians([r for r in rows
                              if r["denom_class"] in WHOLE_DIET_DENOM
                              and r["construct"] in ("EXPOSURE", "REACH")])
    groups = {"EXPOSURE": grp("EXPOSURE"), "CONTENT": grp("CONTENT"),
              "RECALL": grp("RECALL"),
              "RECALL-seen": study_medians([r for r in rows if r["construct"]=="RECALL" and r["recall_subtype"]=="exposure"]),
              "WHOLE-DIET backbone": backbone}

    pairs = [("RECALL", "EXPOSURE"), ("RECALL-seen", "EXPOSURE"), ("CONTENT", "EXPOSURE"),
             ("RECALL", "WHOLE-DIET backbone"), ("CONTENT", "WHOLE-DIET backbone")]

    out_rows = []
    for num, den in pairs:
        np_, dp = groups[num], groups[den]
        point = st.median(np_) / st.median(dp)
        lo, hi = boot_ratio(np_, dp)
        out_rows.append({"numerator": num, "denominator": den,
                         "k_num": len(np_), "k_den": len(dp),
                         "point_ratio": round(point, 1),
                         "boot95_lo": round(lo, 1), "boot95_hi": round(hi, 1)})
        print(f"{num} / {den}: {point:.1f}x  [{lo:.1f}, {hi:.1f}]  (k={len(np_)}/{len(dp)})")

    with open(OUT / "ratio_bootstrap.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)
    print(f"\nWrote {OUT/'ratio_bootstrap.csv'}")


if __name__ == "__main__":
    main()
