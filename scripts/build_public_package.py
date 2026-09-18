#!/usr/bin/env python3
"""
build_public_package.py — assemble the public (OSF/Zenodo) replication package.

The working repository cannot be made public. Its history holds ~2.5 GB of publisher PDFs
(`data/fulltext/`, `PDFs/`), 1,102 extracted article bodies and Scopus record dumps, none of
which may be redistributed. The public release is therefore a FRESH curated tree built by this
script, never this repository with its history rewritten.

    python3 scripts/build_public_package.py                 # -> ../misinfo-prevalence-review-public
    python3 scripts/build_public_package.py --out DIR       # anywhere OUTSIDE the repo
    python3 scripts/build_public_package.py --dry-run       # list what would ship, copy nothing

What ships is defined by ALLOW (below), which is derived from `docs/replication_package.md` and
from the promises the manuscript makes about the package (`docs/package_promises_2026-09-14.md`).
What must never ship is defined by DENY, which is applied twice: once as each file is selected,
and once as a full re-scan of the built tree (`--- final scan ---`). A hit in the re-scan is a
build failure, not a warning: the point of the second pass is that a widened ALLOW rule cannot
quietly let a PDF or a licensed record dump through. The same scan runs under `--dry-run`, against
the source files, so a dry run answers the same questions as a build without writing anything.

Three things fail a build: a denied file in the output, a third-party email address in shipped
text, and an absolute /Users/<name> path (that last one downgradeable with --allow-user-paths).

The freeze is resolved from the `File:` line of the TOP block of `docs/FROZEN.md`, like every
other script in the pipeline, so the package tracks the freeze automatically.

Outputs written by this script (not copied): README.md, LICENSE, MANIFEST.txt,
data/identifiers/*.csv and searches/README.md.
"""
import argparse
import csv
import fnmatch
import hashlib
import json
import os
import re
import shutil
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------------------------
# DENY — the redistribution boundary. Enforced on selection AND on a full re-scan of the output.
# ---------------------------------------------------------------------------------------------

MAX_BYTES = 50 * 1024 * 1024          # GitHub/OSF-friendly ceiling; nothing legitimate is close

DENY_DIR_PREFIXES = [                 # whole trees that never leave the repo
    # Publisher PDFs and extracted article bodies. `data/fulltext/abstract/` (29 files) is held
    # back with the rest of the tree, deliberately and after review, even though Supplementary
    # Note C3 promises those abstracts as re-checkable. They are complete verbatim abstracts, not
    # the one-sentence quotations LICENSE section 3 covers as quotation; most were lifted from
    # `data/abstracts/abstracts.jsonl`, a fetched-record store this list denies twice over; and a
    # few are scraped publisher pages, navigation chrome and all. Shipping them means carving an
    # exception into the strongest rule here and into the re-scan whose whole purpose is that a
    # widened ALLOW cannot open one. The promise is corrected in the manuscript instead: see
    # docs/package_promises_2026-09-14.md. Every abstract-only study is still identified, with its
    # DOI, in data/extract_v2/qa/abstract_only_list.json, so the abstract can be fetched from
    # source in one click, and the coded value and its quotation ship in the freeze.
    "data/fulltext/",
    "data/abstracts/",                # fetched OpenAlex abstract records (also gitignored)
    "PDFs/",                          # the paper library
    "literature/",                    # source documents (theses, reports) held for reading
    ".work/", ".backups/", ".git/",   # Claude-internal and VCS
    "docs/Old/",                      # superseded drafts
    "Submissions/",                   # journal submission bundles
    # The wave-3 prompt files paste the WHOLE extracted body of each reviewed paper (30-95 kB
    # apiece) under the extraction instructions. They are `data/fulltext/` content that happens to
    # sit in docs/, third-party copyright and corresponding-author contact details included. The
    # wave's evidentiary value is in `returns/` (the model's answers) and in the scored
    # disputes/KEY tables under data/extract_v2/qa/, all of which ship.
    "docs/gpt_check_2026-09_wave3/batches/",
]

DENY_GLOBS = [                        # licensed record exports and secrets
    # iCloud duplicates. Desktop and Documents are synced, so a file written while a sync is in
    # flight comes back as "name 2.py", "name 3.py". Fifteen were sitting in the package on
    # 2026-09-18: fourteen byte-identical to their originals, one a superseded September draft
    # of an RA coding page. They are never intentional and must not ship.
    "* [0-9].*", "* [0-9][0-9].*",
    "*.pdf", "*.PDF",
    "*.key", ".secrets", "*.secrets",
    "data/corpus_*.jsonl",            # Scopus strict_v2 result set (Elsevier API terms)
    "data/*_netnew.jsonl",            # raw OpenAlex / PubMed record dumps
    "data/*_adjudicate.jsonl",
    "searches/scopus_*.json",         # Scopus record exports
    "searches/*.jsonl",               # OpenAlex / PubMed record dumps
    "searches/.*",                    # retrieval checkpoints
    "*.rds",
    "*_abstracts.jsonl",              # any worklist carrying fetched abstracts
    # The coder material under each RA_package round: the papers themselves, handed to the coders.
    # Almost all are publisher PDFs, already denied by *.pdf, but where no PDF existed the paper
    # was handed over as an HTML text extraction (V070) carrying the full article body and the
    # corresponding author's email address. The rule is on the tree, not the extension, so the
    # next non-PDF dropped in a papers/ folder cannot ship either.
    "docs/RA_package/*/papers/*",
    # Internal adjudication pages that embed each disputed paper's front matter (authors,
    # postal addresses, phone numbers, corresponding-author emails) inside expandable cards.
    # The rulings they record ship as data/extract_v2/qa/gpt_check_*_disputes.csv.
    "docs/gpt_check_*/disputes_*.html",
]

# Filename fragments that mark human-subjects or contact material. None of it exists in this
# project (there are no participants), but the check is the standing house rule and it is cheap.
DENY_NAME_FRAGMENTS = ["email_list", "contacts", "participant", "consent", "respondent"]

USER_PATH_RE = re.compile(r"/Users/[A-Za-z0-9._-]+")

# Third-party contact details reach shipped text one way: a sentence quoted out of an article
# swallows its CONTACT / Correspondence line. The scan reports every address that is not on this
# list, and a hit fails the build; the fix is to redact at the source, or in the generator that
# wrote the file, never to widen the list. Listed here are the author's own two published
# addresses (the OpenAlex and Crossref polite-pool contact in the retrieval scripts, and the
# corresponding-author line of the manuscript) and one institutional mailbox from a public
# call for papers, quoted in the append-only research log, which cannot be edited after the fact.
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
ALLOWED_EMAILS = {
    "sachayesilaltay@gmail.com",      # author, polite-pool contact in the retrieval scripts
    "sacha.altay@gmail.com",          # author, corresponding-author line of the manuscript
    "journee-etudes@arcom.fr",        # Arcom's public submission mailbox (research_log.md)
    # Two strings the research log QUOTES while recording how the correspondence line was fixed
    # (2026-09-18): an address that never existed and a transposition of the author's own. Neither
    # is a third party's, and the log is append-only, so they are allowed rather than edited out.
    "sacha.altay@uzh.ch",
    "sahca.altay@gmail.com",
}

TEXT_SUFFIXES = {".md", ".txt", ".csv", ".tsv", ".json", ".jsonl", ".py", ".R", ".r", ".sh",
                 ".html", ".svg", ".yml", ".yaml", ".bib", ".cfg", ".toml"}


# The only PDF that may ship. Every other one is a publisher's and cannot be redistributed, which
# is what the blanket *.pdf denial is for; this one is the author's own preprint, and the site
# offers it for download. Named explicitly so the denial stays blanket for everything else.
# Both the repo path and the published path: selection tests the repo-relative path, the stale
# sweep tests the output-relative one, and site/ is remapped to companion/site/ between them.
ALLOWED_PDFS = {
    "docs/preprint/Altay_Systematic_Review_Misinfo.pdf",
    "site/downloads/Altay_Systematic_Review_Misinfo.pdf",
    "companion/site/downloads/Altay_Systematic_Review_Misinfo.pdf",
}


def denied(rel, size=None):
    """Return a reason string if `rel` (a repo-relative posix path) must not ship, else None."""
    if rel in ALLOWED_PDFS:
        return None
    low = rel.lower()
    base = os.path.basename(low)
    for p in DENY_DIR_PREFIXES:
        if low.startswith(p.lower()):
            return f"under denied tree {p}"
    for g in DENY_GLOBS:
        if fnmatch.fnmatch(rel, g) or fnmatch.fnmatch(base, g):
            return f"matches denied pattern {g}"
    for frag in DENY_NAME_FRAGMENTS:
        if frag in low:
            return f"filename contains '{frag}'"
    if size is not None and size > MAX_BYTES:
        return f"file is {size/1e6:.1f} MB (> {MAX_BYTES/1e6:.0f} MB)"
    return None


# ---------------------------------------------------------------------------------------------
# ALLOW — what the package contains. From docs/replication_package.md.
#
#   ("file", rel)              one file; missing -> hard error
#   ("opt",  rel)              one file; missing -> skipped with a note
#   ("glob", pattern)          every repo-relative match
#   ("tree", dir, [globs])     the directory, recursively, keeping only names matching a glob
#                              (empty list = keep everything the DENY rules allow)
# ---------------------------------------------------------------------------------------------

# The ~35 scripts docs/PIPELINE.md calls the live pipeline, plus the retrieval/search layer and
# the three builders the guards read. Everything else in scripts/ (the ~73 freeze-history
# one-offs, the ~89 QA-round one-offs) is deliberately left out: each names one freeze or one
# coding round and cannot be replayed. FROZEN.md records which script built each freeze.
PIPELINE_SCRIPTS = [
    "run_phaseB.sh",
    # the public companion site
    "build_site.py", "check_site.py", "lib_slices.py", "serve_site.sh",
    # stage 1-4
    "aggregate_rob_v3.py", "phaseB_prep_regression.py", "phaseB_descriptives.py",
    "phaseB_slices.py", "phaseB_platform_construct.py", "phaseB_precision.py",
    "phaseB_uncertainty.py", "phaseB_sensitivity.py", "phaseB_grade.py", "phaseB_rob_sans610.py",
    "phaseB_ratio_bootstrap.py", "phaseB_recall_split.py", "phaseB_subgroups.py",
    "phaseB_temporal.py", "appendix_content_sharing.py", "venue_sensitivity.py",
    # stage 5 (R)
    "phaseB_metareg.R", "phaseB_metareg_robustness.R",
    # stage 6 figures
    "phaseB_export_json.py", "phaseB_figures.py", "phaseB_concentration_table.py",
    "phaseB_figures3.py", "phaseB_figures2.py", "fig_coverage_panels.py", "fig_labels.py",
    "make_forest_plot.py",
    # stage 7 HTML
    "build_litreview_html.py", "build_companion_dashboard.py", "phaseB_dashboard.py",
    "phaseB_review_response.py",
    # stage 8 ledgers and guards
    "sync_provenance_ledger.py", "validate_frozen.py", "validate_prisma.py",
    "check_invariants.py", "check_manuscript_stats.py", "make_prisma.py",
    "make_counts_crosswalk.py",
    # reliability, named in replication_package.md
    "rob_reliability.py",
    # read by check_manuscript_stats.py (figure/caption cross-check) and by anyone rebuilding
    # the submission documents
    "make_manuscript_docx.py", "make_nhb_docx.py", "make_box1.py",
    # this builder itself
    "build_public_package.py",
    # Added 2026-09-18. run_phaseB.sh calls all seven and none of them shipped, so the runner the
    # README tells a reader to use died partway through, and several artefacts in the package had
    # no generator beside them: phaseB_perturbation.py computes the deliberate-miscoding analysis
    # reported in Note A2, make_si_characteristics.py writes Supplementary Data 1, and
    # make_si_lists.py writes the SI lists. Found by checking the runner against the tree rather
    # than trusting the allowlist.
    "phaseB_perturbation.py", "phaseB_concentration_null.py",
    "make_si_characteristics.py", "make_si_lists.py", "make_behavioural_arm_dispositions.py",
    "check_pipeline_docs.py", "sync_doc_freeze_headers.py",
]

SEARCH_SCRIPTS = [
    "scopus_search.py", "scopus_fetch_corpus.py", "openalex_keyword_search.py",
    "pubmed_search.py", "semantic_scholar_search.py", "snowball_openalex.py", "tune_search.py",
    "search_behavioural_arm.py", "search_behavioural_pubmed.py",
    "fetch_abstracts_openalex.py", "fetch_abstracts_openalex_batch.py",
    "fetch_abstracts_crossref_pubmed.py",
]

DOC_FILES = [
    # how to run it
    "docs/PIPELINE.md", "docs/ENVIRONMENT.md", "docs/CODEBOOK_estimates.md",
    "docs/FROZEN.md", "docs/replication_package.md", "docs/package_promises_2026-09-14.md",
    # the paper
    "docs/manuscript_draft.md", "docs/counts_crosswalk.md",
    # protocol and method of record
    "docs/protocol.md", "docs/prisma_checklist.md", "docs/screening_protocol.md",
    "docs/screening_criteria.txt", "docs/screening_criteria_stage2.txt",
    "docs/screening_criteria_v2_2026-09.txt",
    "docs/extraction_protocol_v2.md", "docs/value_verification_protocol.md",
    "docs/construct_and_concentration_rules.md", "docs/estimate_selection_rule.md",
    "docs/moderator_codebook.md", "docs/topic_taxonomy.md",
    "docs/rob_checklist_v3.md", "docs/grade_certainty_framework.md",
    "docs/grey_lit_protocol.md",
    # provenance, decisions, audit trail
    "docs/METHODS_PROVENANCE.md", "docs/llm_provenance.md", "docs/human_review_provenance.md",
    "docs/DECISIONS_REGISTER.md", "docs/research_log.md", "docs/dataset_provenance.md",
    "docs/learned_review_rules.md", "docs/data_quality_methods.md", "docs/cleaning_methods.md",
    "docs/blind_reextraction_results.md",
    # the corpus repair of September 2026, in its own reviewer-facing account
    "docs/corpus_repair_2026-09/REPAIR_REPORT.md",
]

QA_FILES = [
    # every extract_v2/qa file a live pipeline script reads, and nothing else. The 52 subfolders
    # of per-round extracted text stay behind: they are derived from publisher full texts.
    "data/extract_v2/qa/blind_reliability.csv",
    "data/extract_v2/qa/rob_appraisals_v145.csv",
    # The adjudication record of every validation campaign the paper cites. The campaign working
    # directories stay behind (they hold publisher full texts), so without these the reader has the
    # claim in Note C1 and none of the evidence for it. Added 2026-09-16, when the late
    # re-extraction shipped its scores nowhere.
    "data/extract_v2/qa/late_reextract_2026-09_SUMMARY.md",
    "data/extract_v2/qa/late_reextract_2026-09_per_study.csv",
    "data/extract_v2/qa/late_reextract_2026-09_omission_queue.csv",
    "data/extract_v2/qa/late_reextract_2026-09_screen_disputes.csv",
    "data/extract_v2/qa/late_reextract_2026-09_moderator_disputes.csv",
    "data/extract_v2/qa/gpt_check_2026-09_wave4_scores.md",
    "data/extract_v2/qa/gpt_check_2026-09_wave5_scores.md",
    "data/extract_v2/qa/gpt_check_2026-09_wave5_adjudication.md",
    "data/extract_v2/qa/decisions_sacha_2026-09-16.csv",
    "data/extract_v2/qa/reextraction_rulings_2026-09-16.csv",
    # The recall-window coding of record. The 2026-08-12 file covered 22 studies and carried no
    # question wording; this one covers all 71 seen-recall studies and quotes each survey item
    # verbatim, which is what §2.4 and Note B4 describe and what check_manuscript_stats.py reads.
    "data/extract_v2/qa/recall_windows_2026-09-14.csv",
    # Whether each headline abstract discloses how its content sample was selected (Note B).
    "data/extract_v2/qa/curated_abstract_disclosure_2026-09-11.csv",
    "data/extract_v2/qa/curated_abstract_disclosure_2026-09-11_notcurated.txt",
    "data/extract_v2/qa/frozen_dois.json",
    "data/extract_v2/qa/abstract_only_list.json",
    "data/extract_v2/qa/cordonnier_changelog.csv",
    "data/extract_v2/qa/curation_adjudication.csv",
    "data/extract_v2/qa/decided_drops.csv",
    "data/extract_v2/qa/dropped_studies.csv",
    "data/extract_v2/qa/drop_audit.json",
    "data/extract_v2/qa/included_not_retrieved.csv",
    "data/extract_v2/qa/oa_dups_dropped.csv",
    "data/extract_v2/qa/openalex_candidates_STAGED.csv",
    "data/extract_v2/qa/openalex_not_retrieved.csv",
    "data/extract_v2/qa/prisma_dispositions.csv",
    "data/extract_v2/qa/prisma_orphans.csv",
    "data/extract_v2/qa/review_pooled_drops.csv",
    "data/extract_v2/qa/stepb_drops_queue.csv",
    "data/extract_v2/qa/v1.2_drops_ledger.csv",
]

ALLOW = [
    # ---- documentation and protocol -----------------------------------------------------
    *[("opt", f) for f in DOC_FILES],
    ("file", "requirements.txt"),

    # ---- figures the manuscript and the supplement use ----------------------------------
    ("glob", "docs/fig*.svg"),
    ("opt", "docs/prisma_flow.svg"),
    ("opt", "docs/prisma_flow.png"),
    ("opt", "docs/box1_ccdh_meta.svg"),

    # ---- pipeline-generated HTML deliverables -------------------------------------------
    ("opt", "docs/phaseB_dashboard.html"),
    ("opt", "docs/phaseB_descriptives.html"),
    ("opt", "docs/phaseB_slices.html"),
    ("opt", "docs/phaseB_figures.html"),
    ("opt", "docs/phaseB_figure_gallery.html"),
    ("opt", "docs/companion_dashboard.html"),
    ("opt", "docs/litreview_measurement.html"),

    # ---- human coding: sheets, instructions, answer keys, scored IRR --------------------
    # The `papers/` subfolders under RA_package hold the articles handed to the coders and are
    # denied as a tree; the sheets, keys and scored results are ours and ship.
    ("tree", "docs/RA_package", ["*.csv", "*.json", "*.html", "*.txt", "*.md"]),

    # ---- independent-model verification: the adjudication trail --------------------------
    # Methods §4.11 promises "the complete adjudication trail of the independent-model
    # verification (including the rows where our coding was found wrong)". That trail is these
    # three waves: the blind and verify sheets sent out, the sheets that came back, the
    # instructions each wave ran under, and the scored disputes with the author's ruling on each.
    # All of it is our own coding of what the papers report, so all of it is redistributable.
    # Two things inside these folders are not, and are denied above by name: the wave-3 prompt
    # bodies (whole article texts) and the wave-2 disputes page (embedded paper front matter).
    ("tree", "docs/gpt_check_2026-09", ["*.csv", "*.md"]),
    ("tree", "docs/gpt_check_2026-09_wave2", ["*.csv", "*.md"]),
    ("tree", "docs/gpt_check_2026-09_wave3", ["*.json", "*.md"]),
    ("glob", "data/extract_v2/qa/gpt_check_2026-09*"),   # the scored KEY, disputes and rulings

    # ---- scripts -------------------------------------------------------------------------
    *[("file", f"scripts/{s}") for s in PIPELINE_SCRIPTS],
    *[("opt", f"scripts/{s}") for s in SEARCH_SCRIPTS],

    # ---- the dataset ---------------------------------------------------------------------
    ("frozen", None),                                   # resolved from FROZEN.md's top block
    ("opt", "data/README.md"),
    ("tree", "data/inputs", []),                        # hand-curated, nothing regenerates them
    ("opt", "data/extract_v2/estimates_reextracted.csv"),
    ("opt", "data/extract_v2/estimates_master_final.csv"),
    ("opt", "data/extract/include635_tagged.csv"),
    # the estimates the corpus repair added, as extracted, before the merge into the freeze
    ("opt", "data/extract_v2/repair_2026-09/repair_estimates_final.csv"),
    *[("opt", f) for f in QA_FILES],
    # ---- the September behavioural arm: every decision file make_behavioural_arm_dispositions.py
    # reads (identifiers, titles, decisions, reasons and short quotes; no record text) and the two
    # files it writes, which validate_prisma.py and make_prisma.py read in turn. Found missing on
    # 2026-09-18 by cloning the public repository and running its own runner: stage 8 died here.
    *[("file", f"data/extract_v2/qa/behavioural_arm/openalex_2026-09/{f}") for f in (
        "MANIFEST.json", "screen_all.csv", "screen_unique.csv", "retrieval_list.csv",
        "adjudication/ruled_all.csv", "adjudication/retrieval_final.csv",
        "fulltext/screen/screened_all.csv", "extraction/rows.csv")],
    ("file", "data/extract_v2/qa/behavioural_arm_dispositions.csv"),
    ("file", "data/extract_v2/qa/behavioural_arm_funnel.json"),
    # ---- the two blind re-extraction campaigns: their scores (Note B1 quotes them and
    # check_manuscript_stats.py asserts them), the per-study coding each fresh agent returned (the
    # guard counts which studies the blind pass reached), and the author's rulings. The batch
    # worklists and prompts stay behind.
    ("glob", "data/extract_v2/full_reextract_2026-09/scores/*"),
    ("glob", "data/extract_v2/full_reextract_2026-09/extractions/*.json"),
    ("glob", "data/extract_v2/full_reextract_2026-09/*.csv"),
    ("glob", "data/extract_v2/full_reextract_2026-09/*.md"),
    ("glob", "data/extract_v2/late_reextract_2026-09/scores/*"),
    ("glob", "data/extract_v2/late_reextract_2026-09/extractions/*.json"),
    ("opt", "docs/SI_lists_README.md"),
    # ---- the cross-family sweep on the released freeze (GPT-5.6, κ = 0.80) and its wave-5
    # completion: the answer keys and returned codes check_manuscript_stats.py counts coverage
    # from, the disagreement tables, and the instructions. Codes and identifiers only; the
    # worklists that paste article text stay behind with the wave-3 batches.
    *[("file", f"docs/codex_check/{f}") for f in (
        "FULL_ANSWER_KEY.csv", "ANSWER_KEY.csv", "codex_disagreements.csv",
        "codex_full_disagreements.csv", "CODEX_INSTRUCTIONS.md")],
    ("tree", "docs/codex_check_wave5", ["*.csv", "*.md", "*.json"]),
    ("glob", "data/extract_v2/qa/excl*.csv"),
    ("glob", "data/extract_v2/qa/fn*.csv"),
    ("glob", "data/extract_v2/qa/triage_*.csv"),
    ("tree", "data/extract_v2/qa/missed_concentration", ["*.csv"]),
    ("tree", "data/extract_v2/qa/missed_estimates", ["*.csv"]),
    ("tree", "data/extract_v2/qa/round3_keys", ["*.csv", "*.json", "*.md"]),

    # ---- risk of bias ----------------------------------------------------------------------
    ("tree", "data/rob/v3out", ["*.csv"]),
    ("glob", "data/rob/rob_v3_*.csv"),
    ("opt", "data/rob/risk_of_bias_v3_master.csv"),
    ("opt", "data/rob/risk_of_bias_master.csv"),
    ("opt", "data/rob/risk_of_bias_master_v2.csv"),

    # ---- reliability, grey literature, screening decisions ---------------------------------
    ("tree", "data/kappa", ["*.csv"]),
    ("tree", "data/grey", ["*.csv"]),
    ("tree", "data/verify", ["*.csv"]),
    ("glob", "data/screen_title_*.csv"),
    ("glob", "data/screen_abstract_*.csv"),
    ("glob", "data/screen_stage5_*.csv"),
    ("opt", "data/screening_goldset.csv"),
    ("opt", "data/seed_berriche_annexe1.csv"),

    # ---- analysis outputs --------------------------------------------------------------------
    ("tree", "data/synth/phaseB", []),
    # The public companion site. site_src/ is the source, site/ the build output; both ship so the
    # deposit is the thing GitHub Pages serves AND the thing that rebuilds it.
    ("file", "docs/preprint/Altay_Systematic_Review_Misinfo.pdf"),
    ("tree", "site_src", []),
    ("tree", "site", []),
    ("tree", "worker", []),        # the submission proxy, its tests and its setup notes

    ("opt", "data/synth/prisma_counts.json"),
    ("opt", "data/synth/venue_types.csv"),

    # ---- searches: query strings, run dates and tuning evidence. No retrieved records. -------
    ("opt", "searches/query_log.md"),
    ("opt", "searches/scopus_query_log.tsv"),
    ("glob", "searches/tune_search_*.json"),
    ("glob", "searches/recall_check_*.json"),
]


# ---------------------------------------------------------------------------------------------
# selection
# ---------------------------------------------------------------------------------------------

def frozen_dataset_path():
    """The `File:` line of the TOP block of docs/FROZEN.md — the only valid dataset pointer."""
    spec = open(os.path.join(ROOT, "docs/FROZEN.md"), encoding="utf-8").read()
    return re.search(r"File:\s*(\S+)", spec).group(1)


def frozen_md5():
    spec = open(os.path.join(ROOT, "docs/FROZEN.md"), encoding="utf-8").read()
    return re.search(r"MD5:\s*(\w+)", spec).group(1)


def walk_tree(rel_dir, keep_globs):
    for dirpath, dirnames, filenames in os.walk(os.path.join(ROOT, rel_dir)):
        dirnames[:] = [d for d in sorted(dirnames) if not d.startswith(".") and d != "Old"]
        for fn in sorted(filenames):
            if fn.startswith("."):
                continue
            if keep_globs and not any(fnmatch.fnmatch(fn, g) for g in keep_globs):
                continue
            yield os.path.relpath(os.path.join(dirpath, fn), ROOT)


def select(all_scripts=False):
    """Return (sorted list of repo-relative paths to copy, list of skip notes)."""
    chosen, notes, skipped = [], [], []
    rules = list(ALLOW)
    if all_scripts:
        rules.append(("tree", "scripts", ["*.py", "*.R", "*.sh"]))

    for rule in rules:
        kind = rule[0]
        if kind == "frozen":
            cands = [frozen_dataset_path()]
        elif kind in ("file", "opt"):
            cands = [rule[1]]
        elif kind == "glob":
            import glob as _g
            cands = sorted(os.path.relpath(p, ROOT)
                           for p in _g.glob(os.path.join(ROOT, rule[1])))
        elif kind == "tree":
            cands = list(walk_tree(rule[1], rule[2]))
        else:
            raise ValueError(kind)

        if kind in ("file", "frozen") and not os.path.exists(os.path.join(ROOT, cands[0])):
            raise SystemExit(f"required file missing: {cands[0]}")
        if kind == "opt" and not os.path.exists(os.path.join(ROOT, cands[0])):
            notes.append(f"absent, skipped: {cands[0]}")
            continue
        if kind == "glob" and not cands:
            notes.append(f"no match: {rule[1]}")

        for rel in cands:
            abs_p = os.path.join(ROOT, rel)
            if not os.path.isfile(abs_p):
                continue
            why = denied(rel, os.path.getsize(abs_p))
            if why:
                skipped.append((rel, why))
                continue
            chosen.append(rel)

    return sorted(set(chosen)), notes, skipped


# ---------------------------------------------------------------------------------------------
# generated files
# ---------------------------------------------------------------------------------------------

def write_identifier_lists(out):
    """Identifiers, not records: enough to re-retrieve every included study from source."""
    d = os.path.join(out, "data/identifiers")
    os.makedirs(d, exist_ok=True)
    freeze = os.path.join(ROOT, frozen_dataset_path())
    rows = list(csv.DictReader(open(freeze, encoding="utf-8")))
    dois = {}
    dp = os.path.join(ROOT, "data/extract_v2/qa/frozen_dois.json")
    if os.path.exists(dp):
        dois = json.load(open(dp, encoding="utf-8"))

    def id_type(i):
        if i.startswith("2-s2.0-"):
            return "scopus_eid"
        if i.startswith("OA-W") or i.startswith("W"):
            return "openalex_work"
        if i.startswith("PMID-"):
            return "pubmed_pmid"
        if i.startswith("NEW-") or i.startswith("SEED-"):
            return "hand_added"
        return "other"

    per = {}
    for r in rows:
        per.setdefault(r["id"], []).append(r)
    p = os.path.join(d, "included_studies.csv")
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["study_id", "id_type", "doi", "n_estimates"])
        for sid in sorted(per):
            w.writerow([sid, id_type(sid), dois.get(sid, ""), len(per[sid])])
    return len(per), p


def write_searches_readme(out):
    p = os.path.join(out, "searches/README.md")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write("""\
# searches/ — queries and run dates, not retrieved records

Every database query is a parameterised script in `scripts/` and every run was logged with its
date. What is here is the **query string, the run date and the result count** for each run:

- `scopus_query_log.tsv` — one row per Scopus run: UTC timestamp, name, total results, query.
- `query_log.md` — the OpenAlex and PubMed runs, with their terms and counts.
- `tune_search_*.json` — the search-tuning comparison behind the final Boolean (query variants,
  corpus size, recall caught/indexed). No records.
- `recall_check_*.json` — the seed-paper recall check: per seed, the identifier query, whether
  the seed was indexed, whether the search caught it, and the verdict.

**The retrieved records themselves are not redistributed.** Scopus results fall under Elsevier's
API terms, and the OpenAlex/PubMed dumps are full record payloads. Re-run the query strings above
against the same databases to regenerate them; counts are only reproducible as of the run date,
which is why every date is recorded. `data/identifiers/included_studies.csv` gives the identifier
and DOI of every included study so the corpus itself can be re-retrieved from source.
""")
    return p


LICENSE_TEXT = """\
LICENCE
=======

This package is released under two licences, split by what the material is.

--------------------------------------------------------------------------------------------
1. CODE  —  MIT Licence
--------------------------------------------------------------------------------------------
Applies to everything under `scripts/`.

MIT License

Copyright (c) {year} Sacha Altay

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

--------------------------------------------------------------------------------------------
2. DATA, DOCUMENTATION, FIGURES AND TEXT  —  Creative Commons Attribution 4.0 (CC BY 4.0)
--------------------------------------------------------------------------------------------
Applies to everything under `data/`, `docs/` and `searches/`, and to this package's README.

You are free to share and adapt this material for any purpose, including commercially, provided
you give appropriate credit, link to the licence, and indicate if changes were made.

Licence text: https://creativecommons.org/licenses/by/4.0/legalcode
Summary:      https://creativecommons.org/licenses/by/4.0/

Attribution: Altay, S. ({year}). {title}.
Replication package, freeze {freeze}.

--------------------------------------------------------------------------------------------
3. THIRD-PARTY MATERIAL NOT COVERED BY EITHER LICENCE
--------------------------------------------------------------------------------------------
The coded dataset quotes short verbatim sentences from the reviewed articles, one per extracted
estimate, so that every number stays checkable against its source. Those quotations are the
copyright of their publishers and are reproduced here under quotation / fair-dealing provisions.
They are not licensed onward by the CC BY grant above.

No publisher PDF, no extracted article body, and no Scopus, OpenAlex or PubMed record payload is
included in this package. See the "Redistribution boundary" section of README.md.
"""


def paper_title():
    """The paper's title, read from the master's H1 so the citation cannot drift from it."""
    with open(os.path.join(ROOT, "docs", "manuscript_draft.md"), encoding="utf-8") as f:
        for line in f:
            if line.startswith("# "):
                return line[2:].strip()
    raise SystemExit("docs/manuscript_draft.md has no H1 title")


def preprint_url():
    """The preprint link the site was built with (build_site.PREPRINT_URL), read from the built
    site's meta.json so the README and the website can never name different links."""
    p = os.path.join(ROOT, "site", "data", "meta.json")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f).get("preprint")


def write_license(out, freeze):
    p = os.path.join(out, "LICENSE")
    open(p, "w", encoding="utf-8").write(
        LICENSE_TEXT.format(year=date.today().year, freeze=os.path.basename(freeze),
                            title=paper_title()))
    return p


README_TEXT = """\
# Prevalence and concentration of misinformation exposure — replication package

Everything needed to reproduce the numbers, figures and tables of the systematic review
*{title}* (Altay, {year}){paper_ref}, from one frozen dataset. Built from the working repository
on {built}, freeze **{version}** ({rows} estimates from {studies} studies), MD5 `{md5}`.

The root holds six things: **`data/`** the dataset and everything derived from it, **`scripts/`**
the code, **`docs/`** the methods and the audit trail, **`searches/`** the queries behind the
corpus, **`companion/`** the interactive website, and this file. Nothing else is needed to
reproduce the paper, and `companion/` is not needed at all.

## What is here

| | |
|---|---|
| `data/extract_v2/{freeze_name}` | the frozen dataset. Every number in the paper comes from this one file. |
| `docs/CODEBOOK_estimates.md` | what each of its 57 columns means |
| `docs/PIPELINE.md` | the ordered run of every script, with inputs and outputs |
| `docs/ENVIRONMENT.md` | interpreter and package versions, seeds, compute cost |
| `docs/manuscript_draft.md` | the manuscript the pipeline is checked against |
| `docs/FROZEN.md` | the freeze ledger: every dataset version, its MD5 and what changed |
| `data/synth/phaseB/` | all analysis outputs, regenerated wholesale by the pipeline |
| `data/inputs/` | the hand-curated inputs nothing regenerates (read `data/inputs/README.md`) |
| `data/rob/` | the risk-of-bias appraisals and their aggregate |
| `docs/RA_package/` | the human coding sheets, instructions and answer keys |
| `data/identifiers/included_studies.csv` | identifier and DOI of every included study |
| `searches/` | the query strings and run dates behind the searches |
| `companion/` | the interactive website at https://altay-research.github.io/misinfo-prevalence-review-public/, its source and the submission worker. Nothing here is needed to reproduce anything. |

## Reproducing the results

The analysis is **stdlib-only Python plus R/metafor**. No numpy, scipy, pandas or matplotlib:
the figures are hand-rolled SVG and the statistics are written against the standard library, so
every headline number regenerates with nothing installed. `requirements.txt` covers only the
`.docx` builders.

```bash
bash scripts/run_phaseB.sh                   # stages 1-4 and 6: everything before the metareg
Rscript scripts/phaseB_metareg.R             # stage 5: needs R 4.3 + metafor + boot
bash scripts/run_phaseB.sh --post-metareg    # stages 7-8: the dashboards, then the guards
```

`docs/PIPELINE.md` is the authority on the run order, and it matters: several stages read what an
earlier stage wrote, and a skipped stage does not fail on a populated tree, it silently computes
against the previous file. The bootstrap (`phaseB_metareg_robustness.R`) is run by hand;
its published intervals are at B = 200.

A few stages read inputs this package does not redistribute. The runner skips those by name,
printing the reason, and the outputs they would write are included:

- `validate_prisma.py`, `make_prisma.py` and `make_si_lists.py` attribute each record to its
  search stream from the raw Scopus, OpenAlex and PubMed record dumps, which are not
  redistributable. Their outputs are included: `data/synth/prisma_counts.json`,
  `docs/prisma_flow.svg`, and the two Supplementary Data lists under `data/synth/phaseB/`.
- `sync_doc_freeze_headers.py` maintains freeze headers in working-repository documents that are
  not part of this package.
- `venue_sensitivity.py` runs; where it would re-derive a venue type from fetched OpenAlex
  records it keeps the shipped `data/synth/venue_types.csv` instead. Its output,
  `data/synth/phaseB/venue_sensitivity.csv`, is included.
- `check_manuscript_stats.py` runs, and every statistic it asserts is re-checked here, with one
  check skipped: it verifies that an archived abstract exists on disk for each abstract-only
  study, and those archived abstracts sit under `data/fulltext/`, which is never redistributed.
  The script says so and carries on rather than failing. The abstract-only studies themselves are
  listed with their DOIs in `data/extract_v2/qa/abstract_only_list.json`, so the same check can be
  made against the publishers' own pages.

This was verified on a fresh clone of the repository ({built}): the three commands above run to
completion, and every file under `data/synth/` regenerates byte-identical to the committed copy.

## The independent-model adjudication trail

`docs/gpt_check_2026-09*/` and `data/extract_v2/qa/gpt_check_2026-09*` are the verification a
different model family ran over the corpus, blind: the sheets sent out, the sheets returned, the
instructions each wave ran under, and the scored disputes with the author's ruling and reason on
every row, the rows where our coding was found wrong included. Two things inside those folders do
not ship, because they are article text rather than coding: the wave-3 prompt files, which paste
each paper's whole extracted body under the instructions, and the wave-2 disputes page, which
embeds the disputed papers' front matter. The rulings they record are in the disputes tables.

## Redistribution boundary

Held back from this package, and excluded by a denylist that is re-checked against the built tree:

- **Publisher PDFs and extracted article bodies** (`data/fulltext/`, `PDFs/`). Third-party
  copyright. They exist in the working repository only so every extracted number stays checkable
  against its source.
- **Scopus records** (`data/corpus_strict_v2_*.jsonl`, `searches/scopus_*.json`). Elsevier's API
  terms prohibit redistributing retrieved records.
- **Full OpenAlex and PubMed record dumps.** Identifiers and DOIs are released instead, in
  `data/identifiers/included_studies.csv`, so the corpus can be re-retrieved from source.

The coded dataset does carry one short verbatim quotation per extracted estimate. That is what
makes the coding auditable; see section 3 of `LICENSE`.

## Licence

- **Code** (`scripts/`) — MIT.
- **Data, documentation, figures and text** (`data/`, `docs/`, `searches/`) — CC BY 4.0.

Full text in `LICENSE`.

## Citation

The paper: Altay, S. ({year}). *{title}.*{paper_cite}

This package: Altay, S. ({year}). Replication package and interactive companion for *{title}*,
freeze {version}. https://github.com/altay-research/misinfo-prevalence-review-public

## Contents

`MANIFEST.txt` lists every file in this package with its size, and records what the build
excluded and why.
"""


ISSUE_TEMPLATES = {
    'feedback.yml': """\
name: A missed study, or any comment
description: A study the review missed, something coded wrongly, or anything else you want to say.
labels: ["feedback"]
body:
  - type: textarea
    id: submission
    attributes:
      label: Your message
      description: If it is a study, a DOI and what it reports is enough.
      placeholder: |
        Grinberg et al. 2019, Science, 10.1126/science.aau2706
        Fake news sources were 6.7% of the political links shared on Twitter, out of all
        political links shared by the panel (Table 2). US, 2016.
    validations:
      required: true
  - type: input
    id: contact
    attributes:
      label: Your email
      description: Optional, only so the author can ask a follow-up.
""",
    'coding-query.yml': """\
name: A coding query or correction
description: Challenge how a specific estimate was coded. Every estimate on the site has an identifier and a link that fills this in for you.
title: "Coding query: "
labels: ["coding"]
body:
  - type: input
    id: estimate
    attributes:
      label: Estimate identifier
      description: The seven-character id at the top right of the estimate record, e.g. edd2e76.
    validations:
      required: true
  - type: textarea
    id: issue
    attributes:
      label: What looks wrong
      description: The field you think is miscoded, and what the paper actually says. The verbatim quote is on the record, so point at it.
    validations:
      required: true
""",
    'config.yml': """\
blank_issues_enabled: true
contact_links:
  - name: Explore the data first
    url: https://altay-research.github.io/misinfo-prevalence-review-public/
    about: Every estimate, the sentence it came from, and what it is a share of.
""",
}


def write_issue_templates(out):
    """Guided forms for the repository's own New Issue button. The site's links pre-fill a body
    directly, but a reader who lands on the repo instead gets a blank box without these."""
    d = os.path.join(out, ".github/ISSUE_TEMPLATE")
    os.makedirs(d, exist_ok=True)
    for name, body in ISSUE_TEMPLATES.items():
        with open(os.path.join(d, name), "w") as f:
            f.write(body)
    return d


PAGES_WORKFLOW = """\
# Publishes companion/site/ to GitHub Pages on every push to main.
#
# Pages can only serve a branch root or /docs directly, and this package needs its root for the
# replication tree, so the site is deployed as an artifact instead — from companion/site, where the
# website lives so that it does not clutter the root. Generated by
# scripts/build_public_package.py; edit it there, not here.
name: Deploy site to Pages
on:
  push:
    branches: [main]
  workflow_dispatch:
permissions:
  contents: read
  pages: write
  id-token: write
concurrency:
  group: pages
  cancel-in-progress: false
jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/configure-pages@v5
      - uses: actions/upload-pages-artifact@v3
        with:
          path: companion/site
      - id: deployment
        uses: actions/deploy-pages@v4
"""


def write_pages_workflow(out):
    p = os.path.join(out, ".github/workflows/pages.yml")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        f.write(PAGES_WORKFLOW)
    return p


def write_readme(out, meta):
    p = os.path.join(out, "README.md")
    open(p, "w", encoding="utf-8").write(README_TEXT.format(**meta))
    return p


# ---------------------------------------------------------------------------------------------
# final scan
# ---------------------------------------------------------------------------------------------

GENERATED = ("LICENSE", "README.md", "MANIFEST.txt", ".github/workflows/pages.yml",
             ".github/ISSUE_TEMPLATE/*.yml")


def scan_pairs(pairs):
    """Re-derive the deny verdict, and scan the text, for a list of (rel, abs) pairs.

    Used twice: over the built tree after a real build, and over the source files a --dry-run
    would have copied, so the dry run answers the same three questions as the build.
    """
    violations, user_hits, email_hits = [], [], []
    for rel, ap in pairs:
        size = os.path.getsize(ap)
        why = denied(rel, size)
        # LICENSE/README/MANIFEST are generated here and carry none of the denied material
        if why and rel not in GENERATED:
            violations.append((rel, why))
        if os.path.splitext(rel)[1] in TEXT_SUFFIXES and size < 20 * 1024 * 1024:
            txt = open(ap, encoding="utf-8", errors="replace").read()
            for m in sorted(set(USER_PATH_RE.findall(txt))):
                user_hits.append((rel, m, txt.count(m)))
            third_party = sorted({e for e in EMAIL_RE.findall(txt)
                                  if e.lower() not in ALLOWED_EMAILS})
            if third_party:
                email_hits.append((rel, third_party))
    return violations, user_hits, email_hits


def final_scan(out):
    """Re-derive the deny verdict for every file actually written. Any hit fails the build."""
    pairs = []
    for dirpath, dirnames, filenames in os.walk(out):
        dirnames[:] = [d for d in sorted(dirnames) if d != ".git"]
        for fn in sorted(filenames):
            ap = os.path.join(dirpath, fn)
            pairs.append((os.path.relpath(ap, out), ap))
    return scan_pairs(sorted(pairs))


def report_scan(violations, user_hits, email_hits):
    if violations:
        print(f"DENYLIST VIOLATIONS ({len(violations)}):")
        for rel, why in violations:
            print(f"  ! {rel}  [{why}]")
    else:
        print("denylist: clean (no PDF, no data/fulltext, no record dump, no secret, "
              f"nothing over {MAX_BYTES/1e6:.0f} MB)")
    if user_hits:
        print(f"ABSOLUTE /Users/ PATHS IN SHIPPED TEXT ({len(user_hits)}):")
        for rel, m, c in user_hits:
            print(f"  ! {rel}: {m} (x{c})")
    else:
        print("absolute paths: clean (no /Users/<name> path in any shipped text file)")
    if email_hits:
        print(f"THIRD-PARTY EMAIL ADDRESSES IN SHIPPED TEXT ({len(email_hits)} file(s)):")
        for rel, addrs in email_hits:
            print(f"  ! {rel}: {', '.join(addrs)}")
    else:
        print("contact details: clean (no email address outside the allowlist)")


# ---------------------------------------------------------------------------------------------

# The website is three directories in the working repository — the built site, its source and the
# submission worker — and at the root of the package they sat between the data and the code, which
# is the first thing a visitor sees and not what they came for (Sacha, 2026-09-18: "it looks super
# complex and not well organized"). They are published under one companion/ folder instead. Only the
# PUBLISHED layout changes; the working repository keeps its own paths, so nothing else breaks.
COMPANION = ("site", "site_src", "worker")


def published_path(rel):
    top = rel.split(os.sep)[0]
    return os.path.join("companion", rel) if top in COMPANION else rel


def human(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} B"
        n /= 1024


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(ROOT),
                                                  "misinfo-prevalence-review-public"),
                    help="target directory (must be OUTSIDE the repo). "
                         "Default: ../misinfo-prevalence-review-public")
    ap.add_argument("--dry-run", action="store_true", help="list what would ship, copy nothing")
    ap.add_argument("--force", action="store_true",
                    help="rebuild into an existing non-empty target (its contents are replaced)")
    ap.add_argument("--all-scripts", action="store_true",
                    help="ship every script, not just the live pipeline and the search layer. "
                         "docs/replication_package.md is ambiguous about the freeze-history "
                         "one-offs; this is the switch if the author wants them released.")
    ap.add_argument("--allow-user-paths", action="store_true",
                    help="downgrade absolute /Users/<name> paths found in shipped text from a build "
                         "failure to a warning")
    args = ap.parse_args()

    out = os.path.abspath(args.out)
    if os.path.commonpath([out, ROOT]) == ROOT:
        raise SystemExit(f"refusing to build inside the repository: {out}")

    freeze = frozen_dataset_path()
    md5 = frozen_md5()
    print(f"repo   : {ROOT}")
    print(f"freeze : {freeze}  (MD5 {md5})")
    print(f"target : {out}\n")

    chosen, notes, skipped = select(all_scripts=args.all_scripts)
    total = sum(os.path.getsize(os.path.join(ROOT, r)) for r in chosen)
    print(f"selected {len(chosen)} files, {human(total)}")
    for n in notes:
        print(f"  note: {n}")
    if skipped:
        print(f"  {len(skipped)} candidate(s) refused by the denylist during selection:")
        for rel, why in skipped[:40]:
            print(f"    - {rel}  [{why}]")
        if len(skipped) > 40:
            print(f"    ... and {len(skipped) - 40} more")

    if args.dry_run:
        for r in chosen:
            print("  ", r)
        # Run the exclusion scan against the source files, so a dry run answers the same three
        # questions as a build without writing anything.
        print("\n--- exclusion scan (source files, nothing written) ---")
        violations, user_hits, email_hits = scan_pairs(
            [(r, os.path.join(ROOT, r)) for r in chosen])
        report_scan(violations, user_hits, email_hits)
        return 1 if (violations or email_hits) else 0

    if os.path.exists(out) and os.listdir(out) and not args.force:
        raise SystemExit(f"target exists and is not empty: {out}  (use --force to rebuild)")
    # NOTHING IS DELETED UP FRONT. This directory is also a git working tree, and emptying it
    # before rewriting leaves a window in which the whole package looks deleted. On 2026-09-18 a
    # commit from another session landed inside that window and published a tree of five files
    # where there had been 640. Files are overwritten in place below, and only genuinely stale ones
    # are removed at the end (see the sweep after the copy loop), so the tree is never empty.
    KEEP = {".git", ".gitignore", ".github"}
    before = set()
    if os.path.exists(out):
        for dirpath, dirnames, filenames in os.walk(out):
            dirnames[:] = [d for d in dirnames if os.path.join(
                os.path.relpath(dirpath, out), d).split(os.sep)[0] not in KEEP]
            for fn in filenames:
                rel_ = os.path.relpath(os.path.join(dirpath, fn), out)
                if rel_.split(os.sep)[0] not in KEEP:
                    before.add(rel_)
    os.makedirs(out, exist_ok=True)

    written = set()          # what this build put there, for the stale sweep at the end
    for rel in chosen:
        dst = os.path.join(out, published_path(rel))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(os.path.join(ROOT, rel), dst)
        written.add(published_path(rel))

    n_studies, idpath = write_identifier_lists(out)
    for _root, _dirs, _files in os.walk(out):
        for _f in _files:
            _r = os.path.relpath(os.path.join(_root, _f), out)
            if _r.split(os.sep)[0] in ("data", "searches") and _r not in written:
                written.add(_r)          # identifier lists and the searches README are generated
    write_searches_readme(out)
    write_pages_workflow(out)
    write_issue_templates(out)
    write_license(out, freeze)

    # Parse the CSV; do NOT count lines. Source quotes contain embedded newlines, so the line
    # count is 1063 against 1048 actual records, and that wrong number was the headline of the
    # replication package README until 2026-09-17.
    with open(os.path.join(ROOT, freeze), encoding="utf-8") as _f:
        _recs = list(csv.DictReader(_f))
    rows = len(_recs)
    assert n_studies == len({r["id"] for r in _recs}), \
        "package study count disagrees with the freeze it ships"
    version = re.search(r"estimates_(v[\d.]+)_frozen", freeze).group(1)
    pre = preprint_url()
    write_readme(out, dict(built=date.today().isoformat(), version=version, rows=rows,
                           studies=n_studies, md5=md5, freeze_name=os.path.basename(freeze),
                           year=date.today().year, title=paper_title(),
                           paper_ref=f", preprint at {pre}" if pre else "",
                           paper_cite=f" Preprint: {pre}" if pre else
                                      " Preprint to follow; this line is updated when it is posted."))

    # ---- final scan --------------------------------------------------------------------------
    print("\n--- final scan ---")
    violations, user_hits, email_hits = final_scan(out)
    report_scan(violations, user_hits, email_hits)

    # The README tells a reader to run scripts/run_phaseB.sh. On 2026-09-18 that runner named seven
    # scripts the package did not contain, so it died partway and three shipped artefacts had no
    # generator beside them. The allowlist is curated by hand and drifted from the runner without
    # anything noticing. This compares the two every build.
    runner = os.path.join(out, "scripts/run_phaseB.sh")
    if os.path.exists(runner):
        named = sorted(set(re.findall(r"[a-zA-Z_0-9]+\.(?:py|R|sh)",
                                      open(runner, encoding="utf-8").read())))
        absent = [n for n in named if not os.path.exists(os.path.join(out, "scripts", n))]
        if absent:
            print(f"runner       : INCOMPLETE — run_phaseB.sh calls {len(absent)} script(s) that are "
                  f"not in the package:")
            for a in absent:
                print(f"               - {a}")
            print("               add them to PIPELINE_SCRIPTS; the package cannot run as documented")
            sys.exit(1)
        print(f"runner       : complete ({len(named)} scripts named by run_phaseB.sh, all present)")

    # ---- stale sweep -------------------------------------------------------------------------
    # Only files the DENYLIST now refuses are removed. A broader "anything this build did not write"
    # rule was tried on 2026-09-18 and deleted LICENSE, README.md and the site tree, because those
    # are produced by helpers rather than copied and are not in `chosen`. The narrow rule solves the
    # problem that prompted it — iCloud duplicates left behind by an earlier build — without
    # needing to know how every shipped file came to exist.
    #
    # The removal happens HERE rather than before the copy, so the tree is never empty. On
    # 2026-09-18 a commit from another session landed inside the old wipe-first window and published
    # a tree of five files where there had been 640.
    # Anything that MOVED leaves its old location behind, because the sweep below only removes
    # denied files. site/, site_src/ and worker/ became companion/* on 2026-09-18; without this the
    # package would ship both copies.
    for name in COMPANION:
        old_ = os.path.join(out, name)
        if os.path.isdir(old_) and os.path.isdir(os.path.join(out, "companion", name)):
            shutil.rmtree(old_)
            print(f"relocated    : {name}/ -> companion/{name}/ (old copy removed)")

    stale = []
    for dirpath, dirnames, filenames in os.walk(out):
        dirnames[:] = [d for d in dirnames
                       if os.path.relpath(os.path.join(dirpath, d), out).split(os.sep)[0] not in KEEP]
        for fn in filenames:
            rel_ = os.path.relpath(os.path.join(dirpath, fn), out)
            if rel_.split(os.sep)[0] in KEEP:
                continue
            # match the file itself and every directory above it: iCloud duplicates whole FOLDERS
            # too ("docs 2/", "site 2/"), and a file-only test shipped 60 of them on 2026-09-18
            # The sweep tested DENY_GLOBS directly and so bypassed the ALLOWED_PDFS exception in
            # denied(): the author's own preprint was copied in and swept straight back out, while
            # the final scan reported "no PDF" about files it had just removed. Ask denied() about
            # the file, and keep the glob test only for the DIRECTORY components above it.
            parts = rel_.split(os.sep)
            rel_posix = rel_.replace(os.sep, "/")
            if denied(rel_posix) \
                    or any(any(fnmatch.fnmatch(part, g) for g in DENY_GLOBS) for part in parts[:-1]) \
                    or any(re.match(r"^.*[A-Za-z0-9] \d+$", part) for part in parts[:-1]):
                stale.append(rel_)
    for rel_ in stale:
        os.remove(os.path.join(out, rel_))
    print(f"stale sweep  : removed {len(stale)} denied file(s) left by an earlier build"
          + (f" (e.g. {stale[0]})" if stale else ""))

    # ---- manifest ----------------------------------------------------------------------------
    entries = []
    for dirpath, dirnames, filenames in os.walk(out):
        dirnames[:] = sorted(dirnames)
        for fn in sorted(filenames):
            ap_ = os.path.join(dirpath, fn)
            entries.append((os.path.relpath(ap_, out), os.path.getsize(ap_)))
    entries.sort()
    grand = sum(s for _, s in entries)
    bytop = {}
    for rel, s in entries:
        top = rel.split(os.sep)[0] if os.sep in rel else "(root)"
        c, b = bytop.get(top, (0, 0))
        bytop[top] = (c + 1, b + s)

    lines = [
        "MANIFEST — public replication package",
        f"built           : {date.today().isoformat()}",
        f"freeze          : {freeze}",
        f"freeze MD5      : {md5}",
        f"estimates/studies: {rows} / {n_studies}",
        f"files           : {len(entries)}",
        f"total size      : {human(grand)}",
        "",
        "By directory",
        "------------",
    ]
    for top in sorted(bytop):
        c, b = bytop[top]
        lines.append(f"  {top:<22} {c:>5} files  {human(b):>10}")
    lines += ["", "Excluded, and why", "-----------------",
              "  data/fulltext/, PDFs/     publisher PDFs and extracted article bodies "
              "(third-party copyright)",
              "  data/corpus_*.jsonl       Scopus records (Elsevier API terms)",
              "  searches/scopus_*.json    Scopus record exports",
              "  searches/*.jsonl          OpenAlex / PubMed record dumps",
              "  data/*_netnew.jsonl       OpenAlex / PubMed record dumps",
              "  data/abstracts/           fetched abstract records (gitignored upstream)",
              "  docs/Old/, .work/, .backups/  superseded drafts and internal working files",
              "  *.pdf, *.key, .secrets    denied outright",
              f"  any file > {MAX_BYTES/1e6:.0f} MB",
              ""]
    if skipped:
        lines.append(f"Refused at selection ({len(skipped)})")
        lines.append("-" * 40)
        for rel, why in skipped:
            lines.append(f"  {rel}  [{why}]")
        lines.append("")
    lines += ["Files", "-----"]
    for rel, s in entries:
        lines.append(f"  {s:>10}  {rel}")
    open(os.path.join(out, "MANIFEST.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")

    print(f"\npackage : {out}")
    print(f"files   : {len(entries)}")
    print(f"size    : {human(grand)}")
    for top in sorted(bytop):
        c, b = bytop[top]
        print(f"  {top:<22} {c:>5} files  {human(b):>10}")
    print(f"manifest: {os.path.join(out, 'MANIFEST.txt')}")

    # A third-party email address fails the build like a denied file does. The fix is always to
    # redact it at its source (or in the generator that produced the file), never to wave it past:
    # every one of them arrived by accident, inside a sentence quoted out of an article.
    fail = bool(violations) or bool(email_hits) or (bool(user_hits) and not args.allow_user_paths)
    if fail:
        print("\nBUILD FAILED the exclusion scan — see the hits above.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
