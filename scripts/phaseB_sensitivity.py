#!/usr/bin/env python3
"""phaseB_sensitivity.py — the sensitivity analyses the manuscript claims.

WHY THIS EXISTS. manuscript_draft.md sec 2.8 states "Sensitivity analyses test exclusion of
borderline falsity/quality estimates and single- versus double-extraction", and sec 2.6 promises
that ambiguous falsity/quality cases were "flagged for a sensitivity analysis". No such code
existed. A claimed-but-uncoded analysis is the worst kind of reproducibility failure, because a
reviewer who asks for the script finds nothing. This implements them, plus two more that the
appraisal campaign made available.

FOUR ANALYSES, each re-running the primary statistic (study-level median, study-cluster bootstrap CI)
on a restricted set so the headline's fragility is visible rather than asserted:

  A. FALSITY-QUALITY BOUNDARY. The review's operational rule counts an estimate as CONTENT only if
     it judges verifiable falsity against external ground truth; usefulness/quality ratings become
     QUALITY and are excluded from prevalence. That single rule is contestable and moves the number.
     Reported three ways: as-specified; excluding rows explicitly flagged borderline; and the
     adversarial case, FOLDING QUALITY INTO CONTENT — i.e. what the content-prevalence figure would
     be if the field's common practice (counting low-quality as misinformation) were adopted.

  B. EXTRACTION ROBUSTNESS. A blind 10% re-extraction (33 studies, fresh agents, no access to the
     frozen coding) exists at qa/blind_reliability.csv. This compares the headline computed on the
     independently-reproduced studies against the full set.

  C. ABSTRACT-ONLY EXCLUSION. 32 studies were appraised from abstracts alone; the RoB instrument
     treats UNCLEAR as HIGH, so those studies are pushed toward HIGH by missing information rather
     than demonstrated bias. Recomputes the headline on full-text studies only.

  D. HIGH RISK-OF-BIAS EXCLUSION. Recomputes on LOW+MODERATE studies only. If the review's claim is
     that alarming numbers come from weak designs, dropping the weak designs should move CONTENT
     down and leave EXPOSURE roughly alone -- a directional prediction the paper can be held to.

Inputs : current freeze (docs/FROZEN.md pointer), data/synth/phaseB/regression_data.csv,
         data/rob/risk_of_bias_v3_master.csv, data/extract_v2/qa/blind_reliability.csv
Outputs: data/synth/phaseB/sensitivity.csv

Run: python3 scripts/phaseB_sensitivity.py
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
WHOLE_DIET = {"all_media", "news_diet", "population", "political_news"}


def frozen():
    spec = open(os.path.join(ROOT, "docs/FROZEN.md"), encoding="utf-8").read()
    fp = re.search(r"File:\s*(\S+)", spec).group(1)
    return list(csv.DictReader(open(os.path.join(ROOT, fp), encoding="utf-8")))


def study_points(rows):
    """One point per study: the median of its estimates."""
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


def summarise(label, rows, note=""):
    out = []
    for c in CONSTRUCTS:
        sub = [r for r in rows if r["construct"] == c]
        pts = study_points(sub)
        if len(pts) < 3:
            continue
        lo, hi = boot_ci(pts)
        out.append({"analysis": label, "group": c, "k_studies": len(pts),
                    "median_pct": round(st.median([v for v, _ in pts]), 1),
                    "ci_lo": lo, "ci_hi": hi, "note": note})
    wd = [r for r in rows if r["denom_class"] in WHOLE_DIET
          and r["construct"] in ("EXPOSURE", "REACH")]
    pts = study_points(wd)
    if len(pts) >= 3:
        lo, hi = boot_ci(pts)
        out.append({"analysis": label, "group": "WHOLE-DIET backbone", "k_studies": len(pts),
                    "median_pct": round(st.median([v for v, _ in pts]), 1),
                    "ci_lo": lo, "ci_hi": hi, "note": note})
    return out


def main():
    rows = frozen()
    # primary analysis set: real proportions, general public
    main_set = [r for r in rows if r["value_kind"] == "proportion"
                and not r["demographic_group"].strip() and r["value_pct"].strip()]

    rob = {r["study_id"]: r["overall_ruling_corrected"] for r in csv.DictReader(
        open(os.path.join(ROOT, "data/rob/risk_of_bias_v3_master.csv"), encoding="utf-8"))}
    src = {r["study_id"]: r["source_read"] for r in csv.DictReader(
        open(os.path.join(ROOT, "data/rob/risk_of_bias_v3_master.csv"), encoding="utf-8"))}
    blind_ids = {r["id"] for r in csv.DictReader(
        open(os.path.join(ROOT, "data/extract_v2/qa/blind_reliability.csv"), encoding="utf-8"))}

    res = []
    res += summarise("PRIMARY (as specified)", main_set, "headline")

    # ---- A. falsity/quality boundary ----
    BORDER = re.compile(r"borderline|quality_?(rating|score)_not_falsity|falsity.?quality", re.I)
    no_border = [r for r in main_set if not BORDER.search(r["flag"])]
    res += summarise("A1 exclude borderline falsity/quality rows", no_border,
                     f"drops {len(main_set)-len(no_border)} flagged rows")
    folded = []
    for r in main_set:
        r2 = dict(r)
        if r2["construct"] == "QUALITY":
            r2["construct"] = "CONTENT"        # adversarial: count quality AS misinformation
        folded.append(r2)
    res += summarise("A2 fold QUALITY into CONTENT (adversarial)", folded,
                     "what CONTENT would be under the field's looser common practice")

    # ---- B. extraction robustness ----
    blind = [r for r in main_set if r["id"] in blind_ids]
    res += summarise("B blind re-extraction subset", blind,
                     f"{len({r['id'] for r in blind})} independently re-extracted studies")

    # ---- C. abstract-only exclusion ----
    ft = [r for r in main_set if src.get(r["id"]) == "full_text"]
    res += summarise("C full-text-appraised studies only", ft,
                     f"drops {len({r['id'] for r in main_set}) - len({r['id'] for r in ft})} abstract-only studies")

    # ---- D. high-RoB exclusion ----
    lowmod = [r for r in main_set if rob.get(r["id"]) in ("LOW", "MODERATE")]
    res += summarise("D exclude HIGH risk-of-bias studies", lowmod,
                     "directional prediction: CONTENT should fall, EXPOSURE should not")

    with open(os.path.join(OUT, "sensitivity.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["analysis", "group", "k_studies", "median_pct",
                                          "ci_lo", "ci_hi", "note"])
        w.writeheader()
        w.writerows(res)

    prim = {r["group"]: r for r in res if r["analysis"].startswith("PRIMARY")}
    print(f"{'analysis':42} {'group':21} {'k':>4} {'median':>8} {'95% CI':>14} {'vs primary':>11}")
    print("-" * 104)
    for r in res:
        d = ""
        if not r["analysis"].startswith("PRIMARY") and r["group"] in prim:
            d = f"{r['median_pct'] - prim[r['group']]['median_pct']:+.1f} pp"
        ci = f"{r['ci_lo']}-{r['ci_hi']}" if r["ci_lo"] != "" else ""
        print(f"{r['analysis']:42} {r['group']:21} {r['k_studies']:>4} "
              f"{r['median_pct']:>7}% {ci:>14} {d:>11}")
    print(f"\nwrote {os.path.relpath(os.path.join(OUT,'sensitivity.csv'), ROOT)}")


if __name__ == "__main__":
    main()
