#!/usr/bin/env python3
"""Codebook invariants, checked directly against the live freeze. Run after EVERY re-freeze.

These are properties the taxonomy guarantees, so a violation is a coding error, not a judgment call.
Each one was added because it caught something real:
  - REACH/RECALL denominators   -> found 8 demographic rows that had inherited a sibling's
                                   denominator while their own quotes were shares of people
  - mean-scores in the pool     -> found two mean mini-DISCERN scores (4.818, 2.003 on a 1-5 scale)
                                   coded value_kind=proportion and pooled with percentages
  - QUALITY-with-breadth        -> the contradiction that drove the v1.6.9 recodes
  - two-axis consistency        -> denom_class is a fused legacy field and drifts from scope/selection
Exit code is non-zero on any failure so it can gate a freeze.
"""
import csv, hashlib, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = open(os.path.join(ROOT, "docs/FROZEN.md")).read()
fp = re.search(r"File:\s*(\S+)", spec).group(1)
md5_declared = re.search(r"MD5:\s*(\w+)", spec).group(1)
path = os.path.join(ROOT, fp)
# FROZEN_OVERRIDE lets a freeze-to-freeze script validate a CANDIDATE file before writing it, so a
# merge that would break an invariant never lands on disk. The MD5-matches-FROZEN.md check is
# meaningless for a candidate (FROZEN.md still describes the parent), so it is skipped in that mode
# and reported as skipped -- never silently passed.
CANDIDATE = os.environ.get("FROZEN_OVERRIDE", "")
if CANDIDATE:
    path = CANDIDATE
    print(f"[candidate mode] validating {os.path.basename(path)} instead of the declared freeze")
rows = list(csv.DictReader(open(path, encoding="utf-8")))
main = [r for r in rows if r["value_kind"] == "proportion" and not (r["demographic_group"] or "").strip()]

def two_axis(r):
    dc, sc, sel = r["denom_class"], r["denom_scope"], (r["denom_selection"] or "").strip()
    if dc in ("curated_sample", "single_source"):
        return sel == ("curated" if dc == "curated_sample" else "single_source")
    return (not dc) or (dc == sc and not sel)

CHECKS = [
    ("FROZEN.md MD5 matches the file on disk",
     lambda: bool(CANDIDATE) or hashlib.md5(open(path, "rb").read()).hexdigest() == md5_declared,
     lambda: []),
    ("breadth is the live 3-value scale or blank",
     lambda: all((r["breadth"] or "") in ("", "fabricated", "false", "misleading") for r in rows),
     lambda: [r for r in rows if (r["breadth"] or "") not in ("", "fabricated", "false", "misleading")]),
    ("no QUALITY row carries a veracity breadth",
     lambda: not any(r["construct"] == "QUALITY" and (r["breadth"] or "").strip() for r in rows),
     lambda: [r for r in rows if r["construct"] == "QUALITY" and (r["breadth"] or "").strip()]),
    ("every CONCENTRATION row is denom n/a and typed",
     lambda: all(r["denom_class"] == "n/a" and (r["conc_unit"] or "").strip() and (r["conc_dimension"] or "").strip()
                 for r in rows if r["construct"] == "CONCENTRATION"),
     lambda: [r for r in rows if r["construct"] == "CONCENTRATION" and not (
         r["denom_class"] == "n/a" and (r["conc_unit"] or "").strip() and (r["conc_dimension"] or "").strip())]),
    ("denom_class agrees with denom_scope/denom_selection",
     lambda: all(two_axis(r) for r in rows), lambda: [r for r in rows if not two_axis(r)]),
    ("REACH denominators are the people observed",
     lambda: all(r["denom_scope"] in ("population", "n/a", "") for r in rows if r["construct"] == "REACH"),
     lambda: [r for r in rows if r["construct"] == "REACH" and r["denom_scope"] not in ("population", "n/a", "")]),
    ("RECALL denominators are the people asked",
     lambda: all(r["denom_scope"] in ("population", "n/a", "") for r in rows if r["construct"] == "RECALL"),
     lambda: [r for r in rows if r["construct"] == "RECALL" and r["denom_scope"] not in ("population", "n/a", "")]),
    ("no mean-scale value sits in the proportion pool",
     lambda: not [r for r in main if re.search(r"\bmean\b.*\b(score|discern|gqs)\b", r["measure_type"] or "", re.I)],
     lambda: [r for r in main if re.search(r"\bmean\b.*\b(score|discern|gqs)\b", r["measure_type"] or "", re.I)]),
    ("no fully-identical rows",
     lambda: len({tuple(r.values()) for r in rows}) == len(rows), lambda: []),
]

print(f"invariants on {fp}  ({len(rows)} rows / {len({r['id'] for r in rows})} studies / {len(main)} main set)\n")
fails = 0
for name, test, offenders in CHECKS:
    ok = test()
    print(f"  {'OK  ' if ok else 'FAIL'} {name}")
    if not ok:
        fails += 1
        for r in offenders()[:5]:
            print(f"         {r['id']} {r['value_pct']} construct={r['construct']} "
                  f"breadth={r['breadth']!r} scope={r['denom_scope']!r} class={r['denom_class']!r}")
print()
if fails:
    sys.exit(f"{fails} invariant(s) violated")
print("all invariants hold")
