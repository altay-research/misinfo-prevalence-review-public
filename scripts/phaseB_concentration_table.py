#!/usr/bin/env python3
"""phaseB_concentration_table.py — concentration reported PER THRESHOLD, with study counts.

WHY. The review previously reported concentration as a sequence — "top 1% -> 70%, top 10% -> ~88%,
top 20% -> ~75%" — which reads as one Lorenz curve. It is not. Each threshold rests on a DIFFERENT
and small set of studies, which is why the sequence is non-monotonic: the top-20% figure is lower
than the top-10% figure because they come from different papers, not because concentration falls.
Presenting incomparable thresholds as a curve reproduces exactly the error this review documents
elsewhere, so this script reports each threshold band separately WITH its k, and never interpolates.

Two further corrections:
  * USER and SOURCE concentration are reported separately (a claim about people is not a claim
    about domains), following the v1.4.11 taxonomy split.
  * Studies contributing at multiple thresholds are counted once per band and flagged, so a single
    panel dataset cannot silently supply several "independent" data points.

Inputs : data/synth/phaseB/concentration_standardized.csv
Outputs: data/synth/phaseB/concentration_by_threshold.csv

Run: python3 scripts/phaseB_concentration_table.py
"""

import csv
import os
import statistics as st
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data/synth/phaseB/concentration_standardized.csv")
DST = os.path.join(ROOT, "data/synth/phaseB/concentration_by_threshold.csv")

# Bands chosen to match how studies actually report, not to make a smooth curve.
# "top =1%" is the STRICT band (exactly 1%): the 2026-08-12 internal review showed the <=1% band
# mixes thresholds spanning 0.0013%-1%, so the strict band carries the headline and the wide band
# is supporting evidence.
BANDS = [("top =1%", 0.999999, 1.0), ("top <=1%", 0.0, 1.0), ("top 1-5%", 1.0, 5.0),
         ("top 5-15%", 5.0, 15.0), ("top 15-35%", 15.0, 35.0)]


def main():
    rows = list(csv.DictReader(open(SRC, encoding="utf-8")))
    out = []
    for unit in ("user", "source"):
        sub = [r for r in rows if (r.get("unit") or "").strip() == unit]
        unbanded = []
        for label, lo, hi in BANDS:
            band = []
            for r in sub:
                t = (r.get("top_pct_people") or "").strip()
                if not t:
                    continue
                try:
                    tv = float(t)
                except ValueError:
                    continue
                if lo < tv <= hi:
                    band.append(r)
            if not band:
                continue
            # STUDY-LEVEL median (one point per study = median of its estimates), matching the
            # paper's primary statistic everywhere else — the old estimate-level median sat next
            # to a study count (2026-08-12 internal review, item 2)
            per_study = defaultdict(list)
            for r in band:
                per_study[r["id"]].append(float(r["activity_share_pct"]))
            sl = [st.median(v) for v in per_study.values()]
            vals = [float(r["activity_share_pct"]) for r in band]
            studies = set(per_study)
            out.append({
                "unit": unit, "threshold_band": label, "k_studies": len(studies),
                "n_estimates": len(band),
                "median_activity_share_pct": round(st.median(sl), 1),
                "min": round(min(vals), 1), "max": round(max(vals), 1),
                "studies": "; ".join(sorted(studies)),
                "caution": ("SINGLE STUDY — not a summary" if len(studies) == 1 else
                            "few studies; do not read across bands as a curve" if len(studies) < 4
                            else ""),
            })
        # estimates with no stated population share cannot be banded at all
        nb = [r for r in sub if not (r.get("top_pct_people") or "").strip()]
        if nb:
            vals = [float(r["activity_share_pct"]) for r in nb]
            out.append({
                "unit": unit, "threshold_band": "threshold NOT STATED", "k_studies": len({r["id"] for r in nb}),
                "n_estimates": len(nb),
                "median_activity_share_pct": round(st.median(vals), 1),
                "min": round(min(vals), 1), "max": round(max(vals), 1),
                "studies": "; ".join(sorted({r["id"] for r in nb})),
                "caution": "no population share reported — cannot enter any threshold comparison",
            })

    with open(DST, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["unit", "threshold_band", "k_studies", "n_estimates",
                                          "median_activity_share_pct", "min", "max",
                                          "caution", "studies"])
        w.writeheader()
        w.writerows(out)

    print(f"{'unit':7} {'band':22} {'k':>3} {'n':>3} {'median':>8} {'range':>14}  caution")
    print("-" * 92)
    for r in out:
        print(f"{r['unit']:7} {r['threshold_band']:22} {r['k_studies']:>3} {r['n_estimates']:>3} "
              f"{r['median_activity_share_pct']:>7}% {f'{r['min']}-{r['max']}':>14}  {r['caution']}")
    # how many studies appear in more than one band (dependence check)
    seen = defaultdict(set)
    for r in out:
        for s in r["studies"].split("; "):
            seen[s].add(r["threshold_band"])
    multi = {s: b for s, b in seen.items() if len(b) > 1}
    print(f"\n{len(multi)} study/studies contribute at more than one threshold "
          f"(their bands are NOT independent): {sorted(multi)[:5]}")
    print(f"wrote {os.path.relpath(DST, ROOT)}")


if __name__ == "__main__":
    main()
