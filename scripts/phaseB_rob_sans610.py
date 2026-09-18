#!/usr/bin/env python3
"""phaseB_rob_sans610.py — RoB summary rating recomputed WITHOUT items 6 and 10.

WHY THIS EXISTS. The pre-specified summary rule weights items 6 (case definition) and 10
(numerator/denominator) — the two Hoy items that encode this review's own thesis. That creates a
circularity objection: "bias tracks the number" and the exclude-HIGH sensitivity could be partly
analytic consequences of an instrument tuned to the claim. This script answers it by recomputing
the overall rating as an UNWEIGHTED count over the eight remaining items (1–5 and 7–9),
with thresholds scaled from the 10-item rule (LOW <= 2 high, MODERATE 3–4,
HIGH >= 5; UNCLEAR counts as high, as in the instrument), then re-running:

  (a) the by-study %-HIGH-per-construct gradient (the §2.6 claim), and
  (b) the exclude-HIGH sensitivity (the §2.9 claim),

so both can be shown to survive with the thesis-encoding items removed.

Inputs : docs/FROZEN.md pointer, data/rob/risk_of_bias_v3_master.csv
Outputs: data/synth/phaseB/rob_sans610.csv

Run: python3 scripts/phaseB_rob_sans610.py
"""

import csv
import os
import random
import re
import statistics as st
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data/synth/phaseB")
SEED, BOOT = 20260723, 2000
random.seed(SEED)
CONSTRUCTS = ["EXPOSURE", "REACH", "SHARING", "CONTENT", "RECALL"]
ITEMS = [1, 2, 3, 4, 5, 7, 8, 9]          # Hoy items minus 6 and 10


def frozen():
    spec = open(os.path.join(ROOT, "docs/FROZEN.md"), encoding="utf-8").read()
    fp = re.search(r"File:\s*(\S+)", spec).group(1)
    return list(csv.DictReader(open(os.path.join(ROOT, fp), encoding="utf-8")))


def rating(row):
    # UNCLEAR counts as high risk, as in the main instrument; NA is not counted either way.
    n_high = sum(1 for i in ITEMS if row[f"item{i}"] in ("HIGH", "UNCLEAR"))
    return "LOW" if n_high <= 2 else ("MODERATE" if n_high <= 4 else "HIGH"), n_high


def study_points(rows):
    by = defaultdict(list)
    for r in rows:
        by[r["id"]].append(float(r["value_pct"]))
    return [(st.median(v), sid) for sid, v in by.items()]


def boot_ci(pts, B=BOOT):
    by = defaultdict(list)
    for p in pts:
        by[p[1]].append(p)
    sids = list(by)
    if len(sids) < 3:
        return ("", "")
    est = []
    for _ in range(B):
        samp = []
        for _ in range(len(sids)):
            samp += by[random.choice(sids)]
        est.append(st.median([v for v, _ in samp]))
    est.sort()
    return round(est[int(.025 * B)], 1), round(est[int(.975 * B)], 1)


def main():
    rob = {r["study_id"]: rating(r) for r in
           csv.DictReader(open(os.path.join(ROOT, "data/rob/risk_of_bias_v3_master.csv"),
                               encoding="utf-8"))}
    pool = [r for r in frozen() if r["value_kind"] == "proportion"
            and not (r["demographic_group"] or "").strip()]

    out = []
    print(f"sans-6/10 rating over {len(rob)} studies "
          f"(HIGH {sum(1 for v in rob.values() if v[0]=='HIGH')}, "
          f"MODERATE {sum(1 for v in rob.values() if v[0]=='MODERATE')}, "
          f"LOW {sum(1 for v in rob.values() if v[0]=='LOW')})")
    for c in CONSTRUCTS:
        sub = [r for r in pool if r["construct"] == c]
        studies = {r["id"] for r in sub}
        rated = [s for s in studies if s in rob]
        pct_high = 100 * sum(1 for s in rated if rob[s][0] == "HIGH") / len(rated)
        keep = [r for r in sub if rob.get(r["id"], ("HIGH",))[0] != "HIGH"]
        pts = study_points(keep)
        med = round(st.median([v for v, _ in pts]), 1)
        lo, hi = boot_ci(pts)
        all_pts = study_points(sub)
        out.append({"construct": c, "k_studies_rated": len(rated),
                    "pct_high_sans610": round(pct_high, 1),
                    "median_all": round(st.median([v for v, _ in all_pts]), 1),
                    "k_excl_high": len({p[1] for p in pts}),
                    "median_excl_high": med, "ci_lo": lo, "ci_hi": hi})
        print(f"  {c:9s} %HIGH(sans-6/10)={pct_high:5.1f}  "
              f"median {out[-1]['median_all']:5.1f} -> excl-HIGH {med:5.1f} (k={len({p[1] for p in pts})})")

    with open(os.path.join(OUT, "rob_sans610.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print("wrote data/synth/phaseB/rob_sans610.csv")


if __name__ == "__main__":
    main()
