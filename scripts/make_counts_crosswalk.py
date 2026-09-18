#!/usr/bin/env python3
"""Counts crosswalk — one authoritative table, plus an active drift check across the repo.

WHY. Before this, five different corpus counts were simultaneously visible to a reader:
the manuscript said 317 studies / 679 estimates, prisma_flow.svg said 408 / 695,
METHODS_PROVENANCE said 329 / 590, data_quality_methods said v1.4.5 / 680, and
figure_contrast.svg said n=695. Each was correct when written; none was correct together. For a
review whose entire pitch is deterministic reproducibility, that is the most damaging kind of
error, because a reviewer can find it with a calculator and no domain knowledge.

This script does two things:
  1. Emits docs/counts_crosswalk.md — the canonical definitions, so "included study" vs
     "record assessed" vs "clean estimate" can never again be silently conflated.
  2. SCANS the repo's documents for numbers that contradict the canonical ones and reports
     them, so drift is caught mechanically rather than by eye. It is a check, not a rewriter --
     it never edits prose, because a stale number sometimes belongs in a historical passage and
     only a human can tell.

Exit status is non-zero if contradictions are found in current (non-archival) documents.

Inputs : docs/FROZEN.md (freeze pointer), the frozen CSV, data/synth/prisma_counts.json,
         data/synth/phaseB/*.csv, data/rob/risk_of_bias_v3_master.csv
Outputs: docs/counts_crosswalk.md

Run: python3 scripts/make_counts_crosswalk.py
"""

import csv
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Documents that legitimately contain historical counts and must NOT be flagged.
# These record superseded values BY DESIGN -- FROZEN.md and dataset_provenance.md are the
# version history, research_log.md is the append-only audit trail, and the punchlists are
# historical worklists. Flagging them would train the reader to ignore the check.
ARCHIVAL = ("FROZEN.md", "research_log.md", "DECISIONS_REGISTER.md", "RESUME_HERE.md",
            "counts_crosswalk.md", "llm_provenance.md", "dataset_provenance.md",
            "v1.2_punchlist.md", "v1.2_newrows_worklist.md", "blind_reextraction_results.md")


def canonical():
    spec = open(os.path.join(ROOT, "docs/FROZEN.md"), encoding="utf-8").read()
    fp = re.search(r"File:\s*(\S+)", spec).group(1)
    ver = re.search(r"v([\d.]+)_frozen", os.path.basename(fp)).group(1)
    md5 = re.search(r"MD5:\s*([0-9a-f]{32})", spec).group(1)
    rows = list(csv.DictReader(open(os.path.join(ROOT, fp), encoding="utf-8")))
    studies = {r["id"] for r in rows}
    main = [r for r in rows if r["value_kind"] == "proportion"
            and not r["demographic_group"].strip()]
    SIX = ("CONTENT", "EXPOSURE", "REACH", "SHARING", "RECALL", "CONCENTRATION")
    six_set = [r for r in main if r["construct"] in SIX]
    pc = json.load(open(os.path.join(ROOT, "data/synth/prisma_counts.json"), encoding="utf-8"))
    ident = pc["identified"]
    rob = list(csv.DictReader(open(os.path.join(ROOT, "data/rob/risk_of_bias_v3_master.csv"),
                                   encoding="utf-8")))
    return {
        "n_six_set": len(six_set),
        "version": ver, "md5": md5, "frozen_path": fp,
        "n_estimates": len(rows), "n_studies": len(studies),
        "n_main_set": len(main),
        "n_main_studies": len({r["id"] for r in main}),
        # All FOUR database streams. Until 2026-09-18 this summed only the three June ones and
        # reported 25,576 under the label "databases", while the manuscript reported 30,958 for the
        # same words — the September behavioural arm is a database stream too. Both numbers were
        # right for their own stream set, which is exactly the failure this file exists to prevent,
        # so the June subtotal is now its own row instead of standing in for the total.
        "n_records_db": (ident["scopus_corpus"] + ident["openalex_netnew"]
                         + ident["pubmed_netnew"] + ident["behavioural_arm_netnew"]),
        "n_records_db_june": ident["scopus_corpus"] + ident["openalex_netnew"] + ident["pubmed_netnew"],
        "n_records_behavioural_arm": ident["behavioural_arm_netnew"],
        "n_records_other": ident["snowball_advancing"],
        "n_assessed": pc["included_or_staged_to_reconcile"],
        # Both not-retrieved states, or the crosswalk reports 46 while the PRISMA figure reports
        # 145: folding the September behavioural arm into the funnel (ruling P1) gave its 99
        # unretrieved records their own terminal state, and this count did not learn about it.
        "n_not_retrieved": (pc["terminal_states"].get("INCLUDED_NOT_RETRIEVED", 0)
                            + pc["terminal_states"].get("ARM_NOT_RETRIEVED", 0)),
        "n_rob": len(rob),
    }


def write_doc(c):
    p = os.path.join(ROOT, "docs/counts_crosswalk.md")
    rows_md = "\n".join([
        f"| Records identified — databases | {c['n_records_db']:,} | Scopus + OpenAlex keyword + PubMed + the September behavioural arm, de-duplicated across streams |",
        f"| — of which, the three June streams | {c['n_records_db_june']:,} | Scopus + OpenAlex keyword + PubMed, the corpus as it stood before the behavioural arm |",
        f"| — of which, the behavioural arm | {c['n_records_behavioural_arm']:,} | OpenAlex trace-terms query, run 2026-09-07 |",
        f"| Records identified — other methods | {c['n_records_other']:,} | OpenAlex citation snowballing, records advancing to screening |",
        f"| Reports sought for retrieval | {c['n_assessed']:,} | the reconciliation set; partitioned exactly by terminal states |",
        f"| Not retrieved | {c['n_not_retrieved']:,} | documented limitation |",
        f"| **Included studies** | **{c['n_studies']:,}** | a distinct STUDY contributing >=1 coded estimate |",
        f"| **Estimates (all)** | **{c['n_estimates']:,}** | one row per study x country x platform x measure |",
        f"| Estimates in the main analysis set | {c['n_main_set']:,} | `value_kind = proportion` and not a demographic subgroup row |",
        f"| Studies in the main analysis set | {c['n_main_studies']:,} | studies contributing >=1 main-set estimate (some studies hold only subgroup or non-proportion rows) |",
        f"| Studies with a risk-of-bias appraisal | {c['n_rob']:,} | RoB v3, Hoy-adapted; must equal included studies |",
    ])
    open(p, "w", encoding="utf-8").write(f"""# Counts crosswalk — one number, one meaning

**Generated by `scripts/make_counts_crosswalk.py`. Do not hand-edit.**
Canonical freeze: **v{c['version']}** (`{c['frozen_path']}`, MD5 `{c['md5']}`).

Five different corpus counts were once simultaneously visible across the manuscript, the PRISMA
diagram, the methods docs and the figures. Each had been correct when written; none was correct
together. This table fixes what each number means so they cannot be conflated again.

| Quantity | Value | Definition |
|---|---:|---|
{rows_md}

## The distinctions that caused the drift

- **Record vs study.** A *record* is one search result. A *study* is one piece of research. The
  reconciliation set ({c['n_assessed']:,}) counts records; the corpus ({c['n_studies']:,}) counts
  studies. They can never be compared directly.
- **Study vs estimate.** One study contributes many estimates — a paper reporting four countries
  on two platforms yields eight rows. This is deliberate: within-study variation is the review's
  subject, so "n" is meaningless without saying n of *what*.
- **All estimates vs the main analysis set.** Pooled statistics use only
  `value_kind = proportion` and exclude demographic-subgroup rows, so {c['n_main_set']:,} < {c['n_estimates']:,}.
  Quality-scale scores, per-capita intensity counts and ranges are stored but never pooled.
- **Superseded counts.** Any figure quoting 408 studies, 695 estimates, 329 studies or 590/680
  estimates predates the current freeze and is wrong for this version. Historical values remain in
  `FROZEN.md` and `research_log.md` on purpose — that is the audit trail, not an inconsistency.

## Drift check
This script also scans current documents for numbers contradicting the table above and fails if it
finds any. Archival files ({', '.join(ARCHIVAL)}) are exempt, since they are supposed to record
superseded values.
""")
    return p


def drift_check(c):
    """Scan current docs for contradicting counts. Returns a list of (file, line, text)."""
    # Compare against the CANONICAL values rather than a hardcoded blocklist of known-stale ones.
    # The blocklist version silently passed v1.6.9's manuscript, which still said 675 estimates /
    # 314 studies: those were the PREVIOUS freeze's counts and had never been added to the list.
    # A blocklist can only catch drift someone remembered to enumerate; this catches all of it.
    # LEGIT holds counts that are genuinely different quantities, not drift.
    LEGIT_STUDIES = {str(c["n_studies"]), str(c["n_rob"]), str(c["n_main_studies"])}
    LEGIT_ESTIMATES = {str(c["n_estimates"]), str(c["n_main_set"]), str(c["n_main_studies"])}
    # Subsets are legitimate, not drift: the meta-regression runs on a restricted set and says so.
    reg = os.path.join(ROOT, "data/synth/phaseB/regression_data.csv")
    if os.path.exists(reg):
        rr = list(csv.DictReader(open(reg, encoding="utf-8")))
        LEGIT_ESTIMATES.add(str(len(rr)))
        LEGIT_STUDIES.add(str(len({r["id"] for r in rr if "id" in r})))
    # Only counts NEAR the canonical one can be drift. A stale corpus total is always a few rows
    # off (675 vs 673); a number far away (470 estimates in the metareg, 118 in a review page) is a
    # different quantity that happens to share the noun. Without this the check cried wolf on every
    # subset and would have been ignored -- the failure mode it exists to prevent.
    # Phrases that make a three-digit "N studies/estimates" about something other than this corpus:
    # other people's reviews, the grey-literature track, and per-construct or per-arm subsets.
    NON_CORPUS = ("grey", "claims", "meta-analys", "other review", "previous review", "their corpus",
                  "records", "search returned", "screened", "retrieved", "of the studies that",
                  "per construct", "subset", "excluded")
    # the main-analysis set and its six-construct subset are canonical quantities in their own right
    LEGIT_MAINSET = {str(c["n_main_set"])}
    LEGIT_SIXSET = {str(c["n_six_set"])}
    hits = []
    # Counts are captured as 3-4 digits: the corpus passed 1,000 estimates at v1.7.x, and a
    # three-digit capture silently reads "1048 estimates" as "048" and reports a CURRENT document
    # as stale. Caught 2026-09-18 on a document that stated the right number.
    # Match the CORPUS-TOTAL idioms only. Scanning every "N studies" flags each legitimate subset
    # count in the QA docs (a cross-check batch, a repair wave, an RA package) and buries the one
    # line that matters; scanning only near-misses lets gross staleness through, which is how
    # "315 studies contribute 675 estimates" survived a freeze. These patterns say "this number IS
    # the corpus", which is the only claim that can be stale in the dangerous way.
    pats = [(re.compile(r"(\d{3,4})\s+studies\s+contribute", re.I), LEGIT_STUDIES, "studies"),
            (re.compile(r"studies\s+contribute\s+(\d{3,4})\s+estimates", re.I), LEGIT_ESTIMATES, "estimates"),
            (re.compile(r"(?:systematic\s+review|review)\s+of\s+(\d{3,4})\s+studies", re.I), LEGIT_STUDIES, "studies"),
            (re.compile(r"(\d{3,4})\s+studies\s+reporting\s+\d{3,4}\s+(?:quantitative\s+)?estimates", re.I), LEGIT_STUDIES, "studies"),
            (re.compile(r"studies\s+reporting\s+(\d{3,4})\s+(?:quantitative\s+)?estimates", re.I), LEGIT_ESTIMATES, "estimates"),
            (re.compile(r"(?:frozen\s+dataset|corpus)\s*\((\d{3,4})\s+estimates", re.I), LEGIT_ESTIMATES, "estimates"),
            (re.compile(r"(\d{3,4})\s+estimates\s*/\s*\d{3,4}\s+studies", re.I), LEGIT_ESTIMATES, "estimates"),
            (re.compile(r"\d{3,4}\s+estimates\s*/\s*(\d{3,4})\s+studies", re.I), LEGIT_STUDIES, "studies"),
            (re.compile(r"n\s*=\s*(\d{3,4})\s+included\s+studies", re.I), LEGIT_STUDIES, "studies"),
            (re.compile(r"(?:corpus|included)\s+(?:of\s+)?(\d{3,4})\s+studies", re.I), LEGIT_STUDIES, "studies"),
            # 2026-09-04: two more corpus-total idioms that hid stale numbers through several freezes.
            # The main-analysis-set size sat at 571/537 and the RoB coverage at "all 315 studies"
            # while canonical was 871/837/456. Neither is phrased as "N studies contribute", so the
            # idiom list above did not see them; both are nonetheless claims about the whole corpus.
            (re.compile(r"appraised\s+for\s+all\s+(\d{3,4})\s+studies", re.I), LEGIT_STUDIES, "studies"),
            (re.compile(r"risk\s+of\s+bias[^.]{0,60}?(\d{3,4})\s+studies", re.I), LEGIT_STUDIES, "studies"),
            (re.compile(r"main[- ]analysis\s+set[^.]{0,80}?\((\d{3,4})\s+in\s+total\)", re.I), LEGIT_MAINSET, "estimates"),
            (re.compile(r"computed\s+on\s+the\s+(\d{3,4})\s+of\s+these", re.I), LEGIT_SIXSET, "estimates")]
    # docs/ plus the repo-root markdown. README.md was outside the scan until 2026-09-07 and had
    # sat on v1.7.9's counts for seven freezes -- and it is the first file any reproducer reads.
    # Anything else at the root that states a corpus count is caught for the same reason.
    scanned = (glob.glob(os.path.join(ROOT, "docs/**/*.*"), recursive=True)
               + glob.glob(os.path.join(ROOT, "*.md"))
               + glob.glob(os.path.join(ROOT, "data/**/README.md"), recursive=True))
    for f in sorted(set(scanned)):
        base = os.path.basename(f)
        rel = os.path.relpath(f, ROOT)
        # Skip archived material: superseded artefacts live in Old/ or archive/ precisely so
        # their stale counts are out of circulation. Flagging them would make the check noisy
        # and train the reader to ignore it.
        if any(part in ("Old", "archive", ".backups") for part in rel.split(os.sep)):
            continue
        if base in ARCHIVAL or not base.endswith((".md", ".html", ".svg")):
            continue
        try:
            txt = open(f, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for ln_no, line in enumerate(txt.splitlines(), 1):
            # A count that names its freeze ("v1.5.2 (679 estimates / 317 studies)") or explicitly
            # marks itself historical is provenance, not drift -- that is the audit trail working.
            # Only UNQUALIFIED counts claim to describe the current corpus.
            if re.search(r"v1\.\d+(\.\d+)?|then in the dataset|superseded|historical|at the time", line, re.I):
                continue
            for rx, legit, kind in pats:
                for m in rx.finditer(line):
                    if line[:m.start()].rstrip().endswith(("<", ">", "\u2264", "\u2265")):
                        continue   # "~all <300 studies" is a threshold, not a corpus count
                    v = m.group(1)
                    if v in legit:
                        continue
                    # NOTE 2026-09-04. This used to skip anything more than NEAR (20) away from the
                    # canonical count, on the theory that a distant three-digit number was about
                    # something else. That inverted the check: it caught near-misses and waved
                    # through GROSS staleness, which is the dangerous kind. The manuscript sat for
                    # a freeze reading "315 studies contribute 675 estimates" -- both 300 away from
                    # canonical, both silently exempt. Every unqualified corpus count is now flagged
                    # unless it is a known non-corpus quantity.
                    if any(k in line.lower() for k in NON_CORPUS):
                        continue
                    hits.append((os.path.relpath(f, ROOT), ln_no, kind,
                                 m.group(1), line.strip()[:100]))
    return hits


def main():
    c = canonical()
    p = write_doc(c)
    print(f"canonical: v{c['version']} — {c['n_studies']} studies / {c['n_estimates']} estimates "
          f"({c['n_main_set']} in the main analysis set)")
    print(f"RoB coverage: {c['n_rob']}/{c['n_studies']} "
          f"{'[OK]' if c['n_rob'] == c['n_studies'] else '[MISMATCH]'}")
    print(f"wrote {os.path.relpath(p, ROOT)}\n")

    hits = drift_check(c)
    if not hits:
        print("DRIFT CHECK: clean — no current document contradicts the canonical counts.")
        return 0
    print(f"DRIFT CHECK: {len(hits)} contradiction(s) in current documents:")
    for f, ln, kind, val, snip in hits:
        print(f"  {f}:{ln}  stale {kind}={val}  | {snip}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
