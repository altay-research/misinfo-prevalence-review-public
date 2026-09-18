#!/usr/bin/env python3
"""Supplementary Data 1: every included study, its characteristics, its results and its risk of bias.

WHY. PRISMA 2020 items 17 to 19 ask a review to report the characteristics of each included study,
its risk of bias, and its results. This review reported none of the three per study, which is what
made every "did you miss study X" and "which studies are behind the 1.3%" question unanswerable: a
referee could not identify a single one of the 18 exposure studies behind the headline. Sacha ruled
on 2026-09-15 to ship them.

Everything here is a JOIN of files the pipeline already regenerates on every freeze. Nothing is
hand-entered, so this file cannot drift from the dataset:
  - the included-study list and bibliography  (si_included_studies.csv, from make_si_lists.py)
  - the appraisal                             (risk_of_bias_v3_master.csv, from aggregate_rob_v3.py)
  - the estimates themselves                  (the frozen dataset, via docs/FROZEN.md)

One row per study, with its per-construct study-level values, so a reader can go from any median in
the paper to the studies behind it and back.

Output: data/synth/phaseB/si_study_characteristics.csv   (Supplementary Data 1)

Run: python3 scripts/make_si_characteristics.py
"""

import csv
import os
import re
import statistics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYN = os.path.join(ROOT, "data/synth/phaseB")
SIX = ["EXPOSURE", "REACH", "SHARING", "CONTENT", "RECALL", "CONCENTRATION"]


def frozen():
    spec = open(os.path.join(ROOT, "docs/FROZEN.md"), encoding="utf-8").read()
    path = re.search(r"File:\s*(\S+)", spec).group(1)
    return list(csv.DictReader(open(os.path.join(ROOT, path), encoding="utf-8")))


def main():
    rows = frozen()
    inc = {r["study_id"]: r for r in
           csv.DictReader(open(os.path.join(SYN, "si_included_studies.csv"), encoding="utf-8"))}
    rob = {r["study_id"]: r for r in
           csv.DictReader(open(os.path.join(ROOT, "data/rob/risk_of_bias_v3_master.csv"),
                               encoding="utf-8"))}

    # study-level value per construct, on the main analysis set, exactly as the paper computes it
    per = {}
    meta = {}
    for r in rows:
        sid = r["id"]
        meta.setdefault(sid, r)
        if r["value_kind"] != "proportion" or r["demographic_group"].strip():
            continue
        if r["construct"] not in SIX or not r["value_pct"].strip():
            continue
        per.setdefault(sid, {}).setdefault(r["construct"], []).append(float(r["value_pct"]))

    out = []
    for sid in sorted(inc, key=lambda s: (inc[s]["first_author"], inc[s]["year"])):
        i, m = inc[sid], meta.get(sid, {})
        row = {
            "study_id": sid,
            "first_author": i["first_author"], "year": i["year"], "title": i["title"],
            "venue": i["venue"], "doi": i["doi"],
            "country": m.get("country_norm") or m.get("country", ""),
            "platform": m.get("platform_norm") or m.get("platform", ""),
            "n_reported": m.get("n", ""),
            "ground_truth": m.get("ground_truth", ""),
            "identification_level": m.get("classification_level", ""),
            "definition_breadth": m.get("breadth", ""),
            "constructs": i["constructs"], "n_estimates": i["n_estimates"],
            "read_from": i["text_basis"],
            "risk_of_bias": rob.get(sid, {}).get("overall_ruling_corrected", "not appraised"),
            "rob_item6_case_definition": rob.get(sid, {}).get("item6", ""),
            "rob_item10_numerator_denominator": rob.get(sid, {}).get("item10", ""),
        }
        for c in SIX:
            vals = per.get(sid, {}).get(c)
            row[f"study_level_{c.lower()}_pct"] = round(statistics.median(vals), 2) if vals else ""
        out.append(row)

    # Every included study must appear, with an appraisal: these two are the claims the paper makes.
    assert len(out) == len(inc), f"{len(out)} rows for {len(inc)} included studies"
    missing_rob = [r["study_id"] for r in out if r["risk_of_bias"] == "not appraised"]
    assert not missing_rob, f"studies with no appraisal: {missing_rob[:5]}"

    path = os.path.join(SYN, "si_study_characteristics.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)

    by_rob = {}
    for r in out:
        by_rob[r["risk_of_bias"]] = by_rob.get(r["risk_of_bias"], 0) + 1
    print(f"wrote {os.path.relpath(path, ROOT)}: {len(out)} studies")
    print("  risk of bias: " + ", ".join(f"{k} {v}" for k, v in sorted(by_rob.items())))
    for c in SIX:
        n = sum(1 for r in out if r[f"study_level_{c.lower()}_pct"] != "")
        print(f"  {c:14s} {n:>3} studies carry a study-level value")


if __name__ == "__main__":
    main()
