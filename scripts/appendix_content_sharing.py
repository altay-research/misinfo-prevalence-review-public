#!/usr/bin/env python3
"""APPENDIX ANALYSIS — is the CONTENT vs SHARING gap about the phenomenon, or about measurement?

The headline construct table shows CONTENT well above SHARING. This asks whether that gap survives
holding the measurement approach fixed, and whether the CONTENT/SHARING split carves the data at all
compared with the other coded moderators.

Two tests:
  1. STRATIFIED CONTRAST. Study-level medians for CONTENT vs SHARING within each level of
     classification_level and ground_truth, with a study-cluster bootstrap on the difference.
  2. WHAT CARVES THE POOL. Merge CONTENT+SHARING and compute eta^2 (one-way, on study-level logit
     medians) for every candidate moderator, so the construct can be ranked against them rather than
     assumed to be primary.

Writes data/synth/phaseB/appendix_content_sharing.csv and prints the tables.
Run: python3 scripts/appendix_content_sharing.py
"""
import csv, math, os, random, re, statistics

random.seed(7)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fp = re.search(r"File:\s*(\S+)", open(os.path.join(ROOT, "docs/FROZEN.md")).read()).group(1)
ROWS = [r for r in csv.DictReader(open(os.path.join(ROOT, fp), encoding="utf-8"))
        if r["construct"] in ("CONTENT", "SHARING") and r["value_kind"] == "proportion"
        and not (r["demographic_group"] or "").strip()]


def study_medians(pred):
    by = {}
    for r in ROWS:
        if not pred(r):
            continue
        try:
            v = float(r["value_pct"])
        except ValueError:
            continue
        by.setdefault(r["id"], []).append(v)
    return [statistics.median(v) for v in by.values() if v]


def boot_diff(a, b, n=4000):
    """Study-cluster bootstrap on the difference of medians; None if either arm is too small.

    The POINT estimate is the observed difference median(a) - median(b) — not the median of the
    bootstrap distribution, which is biased for medians on small strata and made the table's
    difference column disagree with its own two median columns (a referee-spottable inconsistency
    caught at the 2026-08-11 code review). The bootstrap supplies only the CI."""
    if len(a) < 3 or len(b) < 3:
        return None
    d = sorted(statistics.median([random.choice(a) for _ in a])
               - statistics.median([random.choice(b) for _ in b]) for _ in range(n))
    return statistics.median(a) - statistics.median(b), d[int(.025 * n)], d[int(.975 * n)]


def eta2(field):
    """Share of between-study variance in logit(prevalence) explained by one grouping."""
    def logit(p):
        p = min(max(p / 100, 0.001), 0.999)
        return math.log(p / (1 - p))
    by = {}
    for r in ROWS:
        g = (r.get(field) or "").strip() or "(blank)"
        try:
            v = float(r["value_pct"])
        except ValueError:
            continue
        by.setdefault((g, r["id"]), []).append(v)
    pts = {}
    for (g, sid), vs in by.items():
        pts.setdefault(g, []).append(logit(statistics.median(vs)))
    pts = {g: v for g, v in pts.items() if len(v) >= 3}          # ignore singleton levels
    if len(pts) < 2:
        return None
    allv = [x for v in pts.values() for x in v]
    gm = statistics.mean(allv)
    ssb = sum(len(v) * (statistics.mean(v) - gm) ** 2 for v in pts.values())
    sst = sum((x - gm) ** 2 for x in allv)
    return (ssb / sst if sst else 0.0), len(pts), len(allv)


out = []
print("1. DOES THE CONTENT-SHARING GAP SURVIVE HOLDING MEASUREMENT FIXED?\n")
for field, levels in [("classification_level", ["claim_level", "source_level"]),
                      ("ground_truth", ["researcher_coding", "fact_checker", "domain_list", "classifier"])]:
    for lvl in levels:
        a = study_medians(lambda r, f=field, l=lvl: r["construct"] == "CONTENT" and r[f] == l)
        b = study_medians(lambda r, f=field, l=lvl: r["construct"] == "SHARING" and r[f] == l)
        if not a or not b:
            print(f"  {lvl:18} k too small (CONTENT {len(a)}, SHARING {len(b)})")
            out.append({"test": "stratified", "stratum": lvl, "content_k": len(a), "sharing_k": len(b),
                        "content_median": "", "sharing_median": "", "diff": "", "ci_lo": "", "ci_hi": ""})
            continue
        d = boot_diff(a, b)
        ci = f"[{d[1]:+.1f}, {d[2]:+.1f}]" if d else "n too small"
        print(f"  {lvl:18} CONTENT {statistics.median(a):5.1f}% (k={len(a):3})   "
              f"SHARING {statistics.median(b):5.1f}% (k={len(b):2})   diff {d[0] if d else float('nan'):+.1f} pp {ci}")
        out.append({"test": "stratified", "stratum": lvl, "content_k": len(a), "sharing_k": len(b),
                    "content_median": round(statistics.median(a), 1), "sharing_median": round(statistics.median(b), 1),
                    "diff": round(d[0], 1) if d else "", "ci_lo": round(d[1], 1) if d else "",
                    "ci_hi": round(d[2], 1) if d else ""})

print("\n2. WHAT ACTUALLY CARVES THE MERGED POOL? (eta^2, study-level logit medians)\n")
res = []
for f in ["ground_truth", "topic", "platform_norm", "sampling_frame", "classification_level",
          "breadth", "denom_scope", "unit", "construct", "denom_selection"]:
    e = eta2(f)
    if e:
        res.append((e[0], f, e[1], e[2]))
for e, f, g, n in sorted(res, reverse=True):
    mark = "   <-- the CONTENT/SHARING split itself" if f == "construct" else ""
    print(f"  {f:22} eta2={e:.3f}  ({g} groups, {n} studies){mark}")
    out.append({"test": "eta2", "stratum": f, "content_k": g, "sharing_k": n,
                "content_median": round(e, 3), "sharing_median": "", "diff": "", "ci_lo": "", "ci_hi": ""})

p = os.path.join(ROOT, "data/synth/phaseB/appendix_content_sharing.csv")
with open(p, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
print(f"\nwrote {os.path.relpath(p, ROOT)}")
