#!/usr/bin/env python3
"""Give every record of the September behavioural arm a terminal PRISMA state.

WHY THIS EXISTS. The arm (OpenAlex method-term query, run 2026-09-07) contributed 20 studies to the
freeze, 4.5% of the corpus, and appeared nowhere in the identification account: `prisma_counts.json`
described the four June streams only. The flow still reconciled, because validate_prisma.py folds
the frozen study set into the assessed pool directly, but a reader could not see where those 20
studies came from and PRISMA item 6 asks for every source with its last-searched date. Sacha ruled
on 2026-09-14 to fold the arm in as a fifth identification stream (ruling P1, FOLD_IN). The Google
Scholar recall check stays out and is reported as a probe of recall, not a search arm, which is how
the supplementary concentration query is already handled.

The arm kept a decision file at every stage, so nothing here is invented; this script reads them and
writes one terminal state per record. The funnel reconciles exactly:

    5,382 net-new records screened at title (6,972 returned, the rest already in the corpus)
      -  499 within-arm duplicates collapsed        -> 4,883 unique records screened
      -4,321 excluded at title
      =  562 sought for retrieval  (485 MAYBE + 77 INCLUDE)
      -  374 excluded at abstract adjudication
      =  188 sought at full text
      -   99 not retrieved
      =   89 assessed at full text
      -   61 excluded (55 EXCLUDE + 6 UNCERTAIN)
      =   28 to extraction
      -    4 yielded no codeable estimate
      -    4 removed by the pre-merge rulings (K1, K3, K6, K8)
      =   20 in the released dataset

Inputs : data/extract_v2/qa/behavioural_arm/openalex_2026-09/**  (the arm's own decision files)
         the current freeze, via docs/FROZEN.md
Output : data/extract_v2/qa/behavioural_arm_dispositions.csv   (id, disposition, stage, title)
         data/extract_v2/qa/behavioural_arm_funnel.json        (the counts above, for the figure)

Run: python3 scripts/make_behavioural_arm_dispositions.py
"""

import csv
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARM = os.path.join(ROOT, "data/extract_v2/qa/behavioural_arm/openalex_2026-09")
QA = os.path.join(ROOT, "data/extract_v2/qa")


def rows(*parts):
    p = os.path.join(ARM, *parts)
    with open(p, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def frozen_ids():
    spec = open(os.path.join(ROOT, "docs/FROZEN.md"), encoding="utf-8").read()
    path = re.search(r"File:\s*(\S+)", spec).group(1)
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return {r["id"] for r in csv.DictReader(f)}


def main():
    manifest = json.load(open(os.path.join(ARM, "MANIFEST.json")))
    screened_all = rows("screen_all.csv")              # 5,382 net-new, before within-arm dedup
    unique = rows("screen_unique.csv")                 # 4,883 unique records, one title decision each
    retrieval = rows("retrieval_list.csv")             # 562 advanced past the title screen
    adjudicated = rows("adjudication", "ruled_all.csv")        # the 485 MAYBEs, re-read one by one
    to_fulltext = rows("adjudication", "retrieval_final.csv")  # 188 sought at full text
    fulltext = rows("fulltext", "screen", "screened_all.csv")  # 89 assessed
    extracted = rows("extraction", "rows.csv")                 # 40 rows / 24 studies
    titles = {r["oaid"]: r.get("title", "") for r in unique}

    frozen = frozen_ids()
    adv = {r["oaid"] for r in retrieval}
    ft_sought = {r["oaid"] for r in to_fulltext}
    ft_seen = {r["oaid"]: r["ruling"] for r in fulltext}
    extracted_ids = {r["id"] for r in extracted}

    out = []
    for oaid in sorted(adv):
        if oaid in frozen:
            state, stage = "ARM_INCLUDED_FROZEN", "included"
        elif oaid in extracted_ids:
            # extracted, then removed by a pre-merge ruling (K1, K3, K6, K8)
            state, stage = "ARM_EXCLUDED_AT_RULING", "extraction"
        elif oaid in ft_seen and ft_seen[oaid] == "INCLUDE":
            state, stage = "ARM_INCLUDED_NO_DATA", "extraction"
        elif oaid in ft_seen:
            state, stage = "ARM_EXCLUDED_FULL_TEXT", "full text"
        elif oaid in ft_sought:
            state, stage = "ARM_NOT_RETRIEVED", "retrieval"
        else:
            state, stage = "ARM_EXCLUDED_ABSTRACT", "abstract"
        out.append({"id": oaid, "disposition": state, "stage": stage,
                    "title": titles.get(oaid, "")})

    path = os.path.join(QA, "behavioural_arm_dispositions.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "disposition", "stage", "title"])
        w.writeheader()
        w.writerows(out)

    counts = {}
    for r in out:
        counts[r["disposition"]] = counts.get(r["disposition"], 0) + 1
    title_dec = {}
    for r in unique:
        title_dec[r["decision"]] = title_dec.get(r["decision"], 0) + 1

    funnel = {
        "search_run": "2026-09-07",
        "source": manifest["source"],
        "records_returned": manifest["n_total"],
        "records_netnew": manifest["n_new"],
        "records_screened_rows": len(screened_all),
        "duplicates_collapsed": len(screened_all) - len(unique),
        "records_screened_unique": len(unique),
        "title_screen": title_dec,
        "sought_for_retrieval": len(adv),
        "abstract_adjudicated": len(adjudicated),
        "sought_at_full_text": len(ft_sought),
        "not_retrieved": len(ft_sought) - len(ft_seen),
        "assessed_at_full_text": len(ft_seen),
        "terminal_states": counts,
        "studies_in_freeze": counts.get("ARM_INCLUDED_FROZEN", 0),
    }
    with open(os.path.join(QA, "behavioural_arm_funnel.json"), "w", encoding="utf-8") as f:
        json.dump(funnel, f, indent=2)

    # The partition must be exact: every advanced record gets one state, and the states sum to the
    # number that advanced. A gap here means a stage file has moved and the ledger is stale.
    assert sum(counts.values()) == len(adv), (counts, len(adv))
    assert len(adv) == sum(v for k, v in title_dec.items() if k != "EXCLUDE"), (title_dec, len(adv))

    print(f"{len(out)} advanced records dispositioned, {len(unique)} unique records screened")
    for k in sorted(counts):
        print(f"  {k:26} {counts[k]:>4}")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
