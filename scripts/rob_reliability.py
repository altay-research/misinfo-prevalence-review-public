#!/usr/bin/env python3
"""
Risk-of-bias inter-rater reliability, reported with paradox-robust coefficients.

Cohen's kappa collapses when categories are skewed (the "kappa paradox"): with a
HIGH-heavy base rate, chance-agreement is inflated and kappa reads low even when
raters almost never disagree. For skewed nominal/ordinal ratings the accepted
fixes are Gwet's AC1 and PABAK (prevalence-adjusted, bias-adjusted). This script
reports all of them + raw and within-1-level agreement so the RoB reliability can
be stated honestly instead of hidden behind a misleadingly low kappa.

Pass 1 = data/rob/risk_of_bias_master.csv (LLM first pass, all studies)
Pass 2 = data/kappa/rob_p2_*.csv          (LLM blind second pass, subsample)
Paired on `eid`; coefficients computed on the shared studies.

Read-only. Usage: python3 scripts/rob_reliability.py
"""
import csv, os, glob
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)

DIMENSIONS = ["overall", "denominator", "sampling", "definition",
              "measurement", "sample_size"]
# ordinal scale for within-1-level (overall only)
ORDER = {"LOW": 0, "MODERATE": 1, "HIGH": 2}


def load(path_or_glob):
    out = {}
    for p in sorted(glob.glob(path_or_glob)):
        for r in csv.DictReader(open(p)):
            out[r["eid"]] = r
    return out


def cohen_kappa(pairs):
    cats = sorted({a for a, b in pairs} | {b for a, b in pairs})
    n = len(pairs)
    po = sum(1 for a, b in pairs if a == b) / n
    ca = Counter(a for a, b in pairs)
    cb = Counter(b for a, b in pairs)
    pe = sum((ca[c] / n) * (cb[c] / n) for c in cats)
    return (po - pe) / (1 - pe) if pe != 1 else 1.0, po, cats


def pabak(po, q):
    # Byrt et al., generalized to q categories: (q*po - 1)/(q - 1)
    return (q * po - 1) / (q - 1)


def gwet_ac1(pairs):
    cats = sorted({a for a, b in pairs} | {b for a, b in pairs})
    n = len(pairs)
    q = len(cats)
    po = sum(1 for a, b in pairs if a == b) / n
    # pk = mean proportion of category k across the two raters
    ca = Counter(a for a, b in pairs)
    cb = Counter(b for a, b in pairs)
    pk = {c: ((ca[c] / n) + (cb[c] / n)) / 2 for c in cats}
    pe = sum(pk[c] * (1 - pk[c]) for c in cats) / (q - 1) if q > 1 else 0
    return (po - pe) / (1 - pe) if pe != 1 else 1.0


def within_one(pairs):
    scored = [(ORDER.get(a), ORDER.get(b)) for a, b in pairs
              if a in ORDER and b in ORDER]
    if not scored:
        return None
    return sum(1 for a, b in scored if abs(a - b) <= 1) / len(scored)


def main():
    p1 = load(P("data/rob/risk_of_bias_master.csv"))
    p2 = load(P("data/kappa/rob_p2_*.csv"))
    shared = [e for e in p2 if e in p1]

    print("=" * 70)
    print("RISK-OF-BIAS INTER-RATER RELIABILITY (LLM pass 1 vs blind pass 2)")
    print("=" * 70)
    print(f"paired studies: {len(shared)} (pass2={len(p2)}, pass1={len(p1)})\n")
    print(f"{'dimension':14} {'n':>4} {'raw':>6} {'cohenK':>8} {'PABAK':>7} "
          f"{'AC1':>7} {'w/in1':>7}")
    print("-" * 70)

    for dim in DIMENSIONS:
        pairs = [(p1[e].get(dim, "").strip(), p2[e].get(dim, "").strip())
                 for e in shared]
        pairs = [(a, b) for a, b in pairs if a and b]
        if not pairs:
            continue
        k, po, cats = cohen_kappa(pairs)
        pab = pabak(po, len(cats))
        ac1 = gwet_ac1(pairs)
        w1 = within_one(pairs)
        w1s = f"{w1*100:5.0f}%" if w1 is not None else "   -- "
        print(f"{dim:14} {len(pairs):>4} {po*100:5.0f}% {k:8.2f} {pab:7.2f} "
              f"{ac1:7.2f} {w1s:>7}")

    print("-" * 70)
    # category distribution for `overall` — shows the skew driving the paradox
    dist = Counter(p1[e].get("overall") for e in shared)
    print("overall base-rate (pass1):", dict(dist))
    print("\nReading: Cohen's K is deflated by the HIGH-heavy skew; PABAK and Gwet's")
    print("AC1 are the paradox-robust figures to report alongside raw + within-1.")


if __name__ == "__main__":
    main()
