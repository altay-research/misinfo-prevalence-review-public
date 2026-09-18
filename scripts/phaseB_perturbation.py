#!/usr/bin/env python3
"""How much construct miscoding would it take to change the review's conclusion?

THE OBJECTION. The corpus was coded by an AI-assisted pipeline, so every reliability figure in the
paper invites the same reply: the checks were also run by models, and a systematic error would
survive them all. The four grades of check answer how much error was FOUND. This answers a different
question, which no agreement statistic can: how much error would have to be there, undetected, for
the review's central comparison to break.

THE METHOD. Take the released main-analysis set and corrupt it on purpose. A fraction f of estimates
is reassigned to a different construct drawn uniformly from the other five, which is harsher than
any plausible confusion: real coder disagreement concentrates on adjacent pairs (reach against
recall, content against quality), while uniform reassignment moves exposure rows into recall as
readily as into reach. The six study-level medians are then recomputed exactly as the paper computes
them. f runs from 0 to 0.5 and each level is replicated, so what is reported is a distribution, not
one draw.

WHAT IT DECIDES. Two things are checked at every level: whether the construct ordering that the
Results state still holds, and what the exposure-to-recall ratio becomes. The gap is 44-fold at
f = 0. If it survives corrupting a third of the codes, the "an LLM coded it" objection is bounded
rather than open, and bounded by a number the reader can see.

Inputs : the frozen dataset, via docs/FROZEN.md
Outputs: data/synth/phaseB/perturbation.csv   (one row per corruption level)
         data/synth/phaseB/perturbation.json  (the summary the manuscript quotes)

Run: python3 scripts/phaseB_perturbation.py
"""

import csv
import json
import os
import random
import re
import statistics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data/synth/phaseB")
SEED = 20260915
N_REPS = 200
LEVELS = [0.0, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50]
SIX = ["EXPOSURE", "REACH", "SHARING", "CONTENT", "RECALL", "CONCENTRATION"]
# The ordering the Results state, lowest to highest. CONCENTRATION is a distributional quantity on a
# different denominator and is not part of the ordering claim.
ORDER = ["EXPOSURE", "REACH", "SHARING", "CONTENT", "RECALL"]


def frozen_rows():
    spec = open(os.path.join(ROOT, "docs/FROZEN.md"), encoding="utf-8").read()
    path = re.search(r"File:\s*(\S+)", spec).group(1)
    return list(csv.DictReader(open(os.path.join(ROOT, path), encoding="utf-8")))


def medians(rows):
    """Study-level median per construct: median within a study, then median across studies."""
    per = {c: {} for c in SIX}
    for cons, sid, val in rows:
        if cons in per:
            per[cons].setdefault(sid, []).append(val)
    out = {}
    for c in SIX:
        if per[c]:
            out[c] = statistics.median(statistics.median(v) for v in per[c].values())
    return out


def main():
    rng = random.Random(SEED)
    base = [(r["construct"], r["id"], float(r["value_pct"]))
            for r in frozen_rows()
            if r["value_kind"] == "proportion" and not r["demographic_group"].strip()
            and r["construct"] in SIX and r["value_pct"].strip()]
    print(f"main-set rows in the six constructs: {len(base)}")

    m0 = medians(base)
    print("  baseline: " + " · ".join(f"{c} {m0[c]:.1f}" for c in SIX if c in m0))

    rows = []
    for f in LEVELS:
        ratios, ordered_ok, med_by_c, pair_ok = [], 0, {c: [] for c in SIX}, {}
        for _ in range(N_REPS):
            pert = []
            for cons, sid, val in base:
                if f and rng.random() < f:
                    cons = rng.choice([c for c in SIX if c != cons])
                pert.append((cons, sid, val))
            m = medians(pert)
            for c in SIX:
                if c in m:
                    med_by_c[c].append(m[c])
            if "EXPOSURE" in m and "RECALL" in m and m["EXPOSURE"] > 0:
                ratios.append(m["RECALL"] / m["EXPOSURE"])
            present = [c for c in ORDER if c in m]
            ordered_ok += all(m[a] < m[b] for a, b in zip(present, present[1:]))
            for a, b in zip(present, present[1:]):
                pair_ok[f"{a}<{b}"] = pair_ok.get(f"{a}<{b}", 0) + (1 if m[a] < m[b] else 0)
        row = {"corruption": f,
               "ordering_held_pct": round(100 * ordered_ok / N_REPS, 1),
               "recall_over_exposure_median": round(statistics.median(ratios), 1) if ratios else None,
               "recall_over_exposure_min": round(min(ratios), 1) if ratios else None,
               "n_reps": N_REPS}
        for c in SIX:
            row[f"median_{c}"] = round(statistics.median(med_by_c[c]), 1) if med_by_c[c] else None
        # The full five-construct ordering is only as strong as its weakest adjacent pair, so report
        # every pair: that is where a reader learns WHICH comparison the review can lean on.
        for k, v in pair_ok.items():
            row[f"pair_{k}"] = round(100 * v / N_REPS, 1)
        rows.append(row)
        pairs = " ".join(f"{k}:{row['pair_' + k]:.0f}%" for k in pair_ok)
        print(f"  f = {f:<5} full ordering {row['ordering_held_pct']:>5}% | "
              f"recall/exposure x{row['recall_over_exposure_median']:<5} | {pairs}")

    breaks = [r["corruption"] for r in rows if r["ordering_held_pct"] < 95]
    summary = {
        "seed": SEED, "n_reps": N_REPS, "n_rows": len(base),
        "baseline_medians": {c: round(v, 1) for c, v in m0.items()},
        "baseline_ratio": round(m0["RECALL"] / m0["EXPOSURE"], 1),
        "ordering_tested": ORDER,
        "first_level_ordering_breaks": breaks[0] if breaks else None,
        "ratio_at_30pct": next(r["recall_over_exposure_median"] for r in rows if r["corruption"] == 0.30),
        "ratio_min_at_30pct": next(r["recall_over_exposure_min"] for r in rows if r["corruption"] == 0.30),
        "levels": rows,
    }
    with open(os.path.join(OUT, "perturbation.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(OUT, "perturbation.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)
    print(f"\nordering first fails to hold in 95% of draws at f = {summary['first_level_ordering_breaks']}")
    print(f"wrote perturbation.csv / .json")


if __name__ == "__main__":
    main()
