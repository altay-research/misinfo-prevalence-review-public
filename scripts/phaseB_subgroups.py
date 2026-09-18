#!/usr/bin/env python3
"""Descriptive statistics for the demographic-subgroup rows (Section 2.9).

Subgroup rows never enter a pooled statistic; this reports them as their own descriptive track, with
the coverage figure that frames them. Regenerated with every freeze like the rest of Phase B.

Out: data/synth/phaseB/subgroups.csv (per-row), subgroups_summary.json (the numbers the section cites)
Run: python3 scripts/phaseB_subgroups.py
"""
import csv, json, os, re, statistics as st
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = open(os.path.join(ROOT, "docs/FROZEN.md"), encoding="utf-8").read()
FROZEN = os.path.join(ROOT, re.search(r"File:\s*(\S+)", spec).group(1))
rows = list(csv.DictReader(open(FROZEN, encoding="utf-8")))

sub = [r for r in rows if (r["demographic_group"] or "").strip() and r["value_kind"] == "proportion"]
# "Behavioural" is the risk-of-bias-derived MEASUREMENT field, the same one Figure 4's bands and the
# section 2.6 measurement moderator use, read off regression_data.csv so the three cannot diverge.
# It replaced a local definition (sampling_frame in panel_trace/full_census OR question_type ==
# "exposure") whose second clause is a survey question-type field: that version counted 93
# self-report recall surveys as behavioural designs, the opposite of what the section claims.
beh_ids = {r["study_id"] for r in
           csv.DictReader(open(os.path.join(ROOT, "data/synth/phaseB/regression_data.csv"), encoding="utf-8"))
           if r["measurement"] == "BEHAVIOURAL"}
sub_ids = {r["id"] for r in sub}

# pair the political rows: which side of a contrast is higher, and by how much
# Labels are free text with a "<dimension>=<value>" prefix, and the value wording varies by study
# ("Trump supporters", "registered Republican", "Extreme right (R*)"). Match on normalised keywords
# rather than exact strings, or the contrasts silently come back empty.
def side(label):
    l = label.lower()
    if any(k in l for k in ("republican", "trump", "conservative", "right", "far right", "extreme right")):
        return "right"
    if any(k in l for k in ("democrat", "biden", "harris", "liberal", "left", "socialiste", "insoumise")):
        return "left"
    # oldest and youngest bands as the studies print them (65+, 60+, 60-69; 18-29, 20-29, 16-24);
    # the first version matched only "65+" and "18-29" and silently dropped three of the four studies
    if any(k in l for k in ("65+", "60+", "60-69", "65 years", "older")): return "older"
    if any(k in l for k in ("18-29", "18–29", "16-24", "18-24", "20-29", "younger")): return "younger"
    return ""
PAIR = {"political": [("right", "left")], "age": [("older", "younger")]}
gaps = defaultdict(list)
by_study = defaultdict(dict)
for r in sub:
    sd = side(r["demographic_group"])
    if sd:
        by_study[(r["id"], r["construct"], r["measure_type"][:40])].setdefault(sd, []).append(float(r["value_pct"]))
for key, groups in by_study.items():
    for dim, pairs in PAIR.items():
        for hi, lo in pairs:
            if hi in groups and lo in groups:
                a, b = max(groups[hi]), max(groups[lo])
                if b > 0:
                    gaps[dim].append((a / b, key[0], hi, lo, a, b))

summary = {
 "n_subgroup_rows": len(sub),
 "n_subgroup_studies": len(sub_ids),
 "n_studies_total": len({r["id"] for r in rows}),
 "n_behavioural_studies": len(beh_ids),
 "n_behavioural_with_subgroups": len(beh_ids & sub_ids),
 "by_dimension": dict(Counter(r["demographic_dimension"] for r in sub).most_common()),
 "by_construct": dict(Counter(r["construct"] for r in sub).most_common()),
 "political_ratios": sorted(round(g[0], 2) for g in gaps["political"]),
 "political_ratio_median": round(st.median([g[0] for g in gaps["political"]]), 2) if gaps["political"] else None,
 "age_ratios": sorted(round(g[0], 2) for g in gaps["age"]),
 "age_ratio_median": round(st.median([g[0] for g in gaps["age"]]), 2) if gaps["age"] else None,
 # Section 2.9 states how many STUDIES carry a usable contrast and how the directions split. Those
 # counts were written by hand and went stale twice: the prose said eight political contrasts when
 # there were ten, and four age contrasts when there were six. Derived here so the checker can
 # assert them.
 "n_studies_with_subgroup_dimension": {d: len({r["id"] for r in sub if r["demographic_dimension"] == d})
                                       for d in sorted({r["demographic_dimension"] for r in sub})},
 "political_contrast_studies": len({g[1] for g in gaps["political"]}),
 "political_contrast_reversals": sum(1 for g in gaps["political"] if g[0] < 1),
 "age_contrast_studies": len({g[1] for g in gaps["age"]}),
 "age_contrast_older_higher": sorted(round(g[0], 2) for g in gaps["age"] if g[0] > 1),
 "age_contrast_older_lower": sorted(round(g[0], 2) for g in gaps["age"] if g[0] < 1),
}
with open(os.path.join(ROOT, "data/synth/phaseB/subgroups.csv"), "w", newline="", encoding="utf-8") as f:
    cols = ["id", "construct", "demographic_dimension", "demographic_group", "value_pct", "measure_type"]
    w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(sub)
json.dump(summary, open(os.path.join(ROOT, "data/synth/phaseB/subgroups_summary.json"), "w",
                        encoding="utf-8"), indent=1)
for k, v in summary.items(): print(f"  {k}: {v}")
print("\nwithin-study contrasts found:")
for dim, gs in gaps.items():
    for ratio, sid, hi, lo, a, b in sorted(gs, key=lambda x: -x[0]):
        print(f"  {dim:10s} {hi} {a} vs {lo} {b}  = {ratio:.2f}x   ({sid})")
