#!/usr/bin/env python3
"""Aggregate the RoB v3 shard appraisals into a master, with the required sensitivities.

WHAT THIS HANDLES THAT A NAIVE CONCAT WOULD NOT

1. **Ruling drift between shards.** Shards 00-19 were appraised BEFORE the 2026-07-23 ruling
   that a published source-level credibility list satisfies item 6; shards 20-31 after. Silently
   concatenating them would mix two instruments and inflate the HIGH share. This script tags every
   row with `ruling_applied`, flags the specific pre-ruling rows known to be affected, and reports
   the distribution both as-appraised and with those rows corrected -- so the inconsistency is
   visible rather than buried. The corrected figure is the one to report, and the affected rows
   remain queued for actual re-appraisal.

2. **The abstract-only sensitivity.** The instrument treats UNCLEAR as HIGH in the summary rating.
   For studies read only at abstract level, many items are UNCLEAR simply because an abstract does
   not describe sampling or reliability -- so those studies are pushed toward HIGH by missing
   information rather than by demonstrated bias. Multiple appraisers flagged this independently.
   The script therefore reports the full set AND a full-text-only sensitivity.

3. **Reconciliation to the frozen study list.** The v2 master carried 261 records for studies no
   longer in the corpus and was missing 88 that were. Coverage against the current freeze is
   asserted here, not assumed.

Outputs also include the per-item distribution (which items actually discriminate) and the
RoB x construct cross-tab that the review's "bias tracks the number inversely" claim rests on.

Inputs : data/rob/v3out/shard_*.csv
         frozen dataset via docs/FROZEN.md
Outputs: data/rob/risk_of_bias_v3_master.csv
         data/rob/rob_v3_summary.csv
         data/rob/rob_v3_by_construct.csv
         data/rob/rob_v3_item_distribution.csv

Run: python3 scripts/aggregate_rob_v3.py
"""

import csv
import glob
import os
import re
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "data/rob")
ITEMS = [f"item{i}" for i in range(1, 11)]

# Shards appraised before the source-level-list ruling was written into the instrument.
PRE_RULING_SHARDS = set(range(0, 20))

# Rows identified (scripts + docs/rob_checklist_v3.md) as rated item 6 HIGH/UNCLEAR on a
# source-level list under the pre-ruling wording. Under the ruling item 6 becomes LOW.
AFFECTED_BY_RULING = {
    "2-s2.0-85038621544", "2-s2.0-85066887935", "2-s2.0-85074511992",
    "2-s2.0-85074596916", "2-s2.0-85078014559", "2-s2.0-85092033301",
    "2-s2.0-85131073869", "2-s2.0-85164694763",
}


# Rows where the appraiser deliberately departed from the anchor, with the reason. These keep the
# appraised rating; every other departure is re-banded to the anchor and listed in the deviations
# file. Adding an id here is a documented judgement, not a way to keep an arithmetic slip.
APPRAISER_OVERRIDES = {
    # Empty by design. W4210350805 was proposed here (an appraiser rated it HIGH against a
    # MODERATE anchor because its tables look constructed: 100.0% exposure, zero non-exposed,
    # every row totalling 332). Sacha ruled MODERATE on 2026-09-14: the study is a self-report
    # recall survey about one named rumour, so a ceiling is a plausible reading of a salient
    # local story, and the instrument should not be overridden on suspicion.
}


def summary_rating(items):
    """Pre-specified anchor from docs/rob_checklist_v3.md. UNCLEAR counts as HIGH."""
    eff = {k: ("HIGH" if v == "UNCLEAR" else v) for k, v in items.items()}
    n_high = sum(1 for k in ITEMS if eff.get(k) == "HIGH")
    i6, i10 = eff.get("item6"), eff.get("item10")
    if i6 == "HIGH" and i10 == "HIGH":
        return "HIGH", n_high
    if n_high >= 6:
        return "HIGH", n_high
    if n_high >= 3 or i6 == "HIGH" or i10 == "HIGH":
        return "MODERATE", n_high
    return "LOW", n_high


def frozen_rows():
    path = re.search(r"File:\s*(\S+)", open(os.path.join(ROOT, "docs/FROZEN.md")).read()).group(1)
    return list(csv.DictReader(open(os.path.join(ROOT, path), encoding="utf-8")))


def main():
    frozen_ids = {r["id"] for r in frozen_rows()}
    rows, seen, orphaned = [], {}, []
    for f in sorted(glob.glob(os.path.join(OUTDIR, "v3out/shard_*.csv"))):
        # repair shards are named shard_rNN (2026-09); number them 6NN so shard ids stay unique
        m = re.search(r"shard_(r?)(\d+)", f)
        shard = int(("6" if m.group(1) else "") + m.group(2))
        for r in csv.DictReader(open(f, encoding="utf-8")):
            sid = r["study_id"].strip()
            if sid in seen:                      # never silently double-count
                continue
            if sid not in frozen_ids:            # appraisal of a study no longer in the corpus
                orphaned.append(sid)             # (e.g. a deduplicated ID) — master mirrors freeze
                continue
            seen[sid] = shard
            r["shard"] = shard
            r["ruling_applied"] = "no" if shard in PRE_RULING_SHARDS else "yes"
            r["needs_reappraisal"] = ("yes" if (shard in PRE_RULING_SHARDS
                                                and sid in AFFECTED_BY_RULING) else "")
            rows.append(r)

    # ---- corrected variant: apply the ruling to the known affected pre-ruling rows ----
    # Every other row is re-banded from its own item ratings with the instrument's anchor, so the
    # reported column cannot inherit an appraiser's arithmetic. Two appraisers, working on different
    # shards the same day, read the UNCLEAR convention in opposite directions; the instrument
    # (rob_checklist_v3.md, "rate UNCLEAR and treat as HIGH in the overall") settles it, and 69 of
    # the 72 UNCLEAR-carrying rows already followed it. Deviations are listed, not silently taken.
    deviations = []
    for r in rows:
        if r["needs_reappraisal"] == "yes":
            items = {k: r[k] for k in ITEMS}
            items["item6"] = "LOW"
            r["overall_ruling_corrected"], r["n_high_corrected"] = summary_rating(items)
            continue
        anchored, n_anchored = summary_rating({k: r[k] for k in ITEMS})
        if r["study_id"] in APPRAISER_OVERRIDES and anchored != r["overall"]:
            r["overall_ruling_corrected"] = r["overall"]        # deliberate, documented override
            r["n_high_corrected"] = r["n_high"]
            deviations.append({"study_id": r["study_id"], "shard": r["shard"],
                               "as_appraised": r["overall"], "anchored": anchored,
                               "resolution": "appraiser override kept",
                               "note": APPRAISER_OVERRIDES[r["study_id"]]})
            continue
        if anchored != r["overall"]:
            deviations.append({"study_id": r["study_id"], "shard": r["shard"],
                               "as_appraised": r["overall"], "anchored": anchored,
                               "resolution": "re-banded to the anchor",
                               "note": "items " + "/".join(r[k] for k in ITEMS)})
        r["overall_ruling_corrected"] = anchored
        r["n_high_corrected"] = n_anchored
    with open(os.path.join(OUTDIR, "rob_v3_band_deviations.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["study_id", "shard", "as_appraised", "anchored",
                                          "resolution", "note"])
        w.writeheader()
        w.writerows(deviations)

    cols = (["study_id", "shard", "ruling_applied", "needs_reappraisal"] + ITEMS +
            ["n_high", "overall", "n_high_corrected", "overall_ruling_corrected",
             "source_read", "quote_item6", "quote_item10", "notes"])
    with open(os.path.join(OUTDIR, "risk_of_bias_v3_master.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    # ---- coverage against the frozen study list ----
    fr = frozen_rows()
    frozen_ids = {r["id"] for r in fr}
    appraised = {r["study_id"] for r in rows}
    missing = sorted(frozen_ids - appraised)
    orphan = sorted(appraised - frozen_ids)

    # ---- distributions: as-appraised, ruling-corrected, full-text-only ----
    def dist(subset, field):
        c = Counter(r[field] for r in subset)
        n = len(subset)
        return {k: f"{c.get(k,0)} ({c.get(k,0)/n:.0%})" for k in ("LOW", "MODERATE", "HIGH")} | {"n": n}

    full_text = [r for r in rows if r["source_read"] == "full_text"]
    summary = [
        {"variant": "as appraised (mixed instrument)", **dist(rows, "overall")},
        {"variant": "RULING-CORRECTED (report this)", **dist(rows, "overall_ruling_corrected")},
        {"variant": "full-text only (abstract-only sensitivity)",
         **dist(full_text, "overall_ruling_corrected")},
    ]
    with open(os.path.join(OUTDIR, "rob_v3_summary.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["variant", "n", "LOW", "MODERATE", "HIGH"])
        w.writeheader()
        w.writerows(summary)

    # ---- per-item discrimination ----
    item_rows = []
    for it in ITEMS:
        c = Counter(r[it] for r in rows)
        item_rows.append({"item": it, "LOW": c.get("LOW", 0), "HIGH": c.get("HIGH", 0),
                          "UNCLEAR": c.get("UNCLEAR", 0), "NA": c.get("NA", 0),
                          "pct_HIGH_of_rated": round(
                              c.get("HIGH", 0) / max(1, c.get("HIGH", 0) + c.get("LOW", 0)) * 100, 1)})
    with open(os.path.join(OUTDIR, "rob_v3_item_distribution.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["item", "LOW", "HIGH", "UNCLEAR", "NA", "pct_HIGH_of_rated"])
        w.writeheader()
        w.writerows(item_rows)

    # ---- RoB x construct (the "bias tracks the number" cross-tab) ----
    rob_by_study = {r["study_id"]: r["overall_ruling_corrected"] for r in rows}
    by_con = defaultdict(Counter)
    for r in fr:
        rb = rob_by_study.get(r["id"])
        if rb and r["value_kind"] == "proportion" and not r["demographic_group"].strip():
            by_con[r["construct"]][rb] += 1
    con_rows = []
    for con, c in sorted(by_con.items(), key=lambda x: -sum(x[1].values())):
        n = sum(c.values())
        con_rows.append({"construct": con, "n_estimates": n,
                         "LOW": c["LOW"], "MODERATE": c["MODERATE"], "HIGH": c["HIGH"],
                         "pct_HIGH": round(c["HIGH"] / n * 100, 1)})
    with open(os.path.join(OUTDIR, "rob_v3_by_construct.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["construct", "n_estimates", "LOW", "MODERATE", "HIGH", "pct_HIGH"])
        w.writeheader()
        w.writerows(con_rows)

    # ---- report ----
    print(f"RoB v3 master: {len(rows)} studies from {len(set(r['shard'] for r in rows))} shards")
    print(f"  coverage vs frozen ({len(frozen_ids)} studies): "
          f"{len(frozen_ids & appraised)} matched, {len(missing)} MISSING, {len(orphan)} orphan")
    if missing:
        print(f"    missing: {missing[:6]}{' ...' if len(missing) > 6 else ''}")
    n_corr = sum(1 for r in rows if r["needs_reappraisal"] == "yes")
    print(f"  pre-ruling shards: {sum(1 for r in rows if r['ruling_applied']=='no')} studies; "
          f"{n_corr} corrected for the item-6 ruling")
    print(f"\n{'variant':44} {'n':>4}  {'LOW':>10} {'MODERATE':>11} {'HIGH':>11}")
    for s in summary:
        print(f"{s['variant']:44} {s['n']:>4}  {s['LOW']:>10} {s['MODERATE']:>11} {s['HIGH']:>11}")
    print(f"\nper-item % HIGH (of items actually rated LOW/HIGH):")
    for i in item_rows:
        print(f"  {i['item']:7} {i['pct_HIGH_of_rated']:>5}%   (unclear {i['UNCLEAR']}, n/a {i['NA']})")
    print(f"\nRoB x construct (ruling-corrected, main-set estimates):")
    print(f"  {'construct':16} {'n':>5} {'%HIGH':>7}")
    for c in con_rows:
        print(f"  {c['construct']:16} {c['n_estimates']:>5} {c['pct_HIGH']:>6}%")
    print(f"\nwrote 4 files to data/rob/")


if __name__ == "__main__":
    main()
