#!/usr/bin/env python3
"""Refresh the "as at freeze vX (N estimates / M studies)" lines in the current docs.

WHY THIS EXISTS. `make_counts_crosswalk.py` exempts any line naming a version, on the sound theory
that "v1.5.2 (679 estimates / 317 studies)" is provenance rather than drift. But a handful of docs
use that same shape to describe the CURRENT corpus — "Counts below are as at v1.7.20 (1,048 estimate
rows / 443 studies)" — so naming the freeze bought them a permanent exemption from the check while
they went two freezes stale (found 2026-09-16). Those lines are now GENERATED, like the provenance
ledger, so they cannot drift again.

It is a CURATED list, not a search-and-replace: most `v1.7.x` mentions in these files are real
history ("SHARING moved to MODERATE at v1.7.20") and must not be touched. Every entry names one file
and one regex that matches exactly one line; a pattern that stops matching is an ERROR, because it
means the sentence was reworded and nobody refreshed it.

Run: python3 scripts/sync_doc_freeze_headers.py [--check]
  --check reports what is stale and exits non-zero without writing (use it in the guard sequence).
"""
import argparse
import csv
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def freeze_facts():
    """Version, file, MD5, tag and date from the TOP block of FROZEN.md, plus the live counts."""
    txt = open(os.path.join(ROOT, "docs/FROZEN.md"), encoding="utf-8").read()
    head = txt[:txt.index("\n## ")]
    f = {
        "version": re.search(r"# FROZEN DATASET (v[\d.]+)", head).group(1),
        "date": re.search(r"# FROZEN DATASET v[\d.]+ \(([\d-]+)\)", head).group(1),
        "file": re.search(r"- File: (\S+)", head).group(1),
        "md5": re.search(r"- MD5: (\S+)", head).group(1),
        "tag": re.search(r"- Git tag: (\S+)", head).group(1),
    }
    rows = list(csv.DictReader(open(os.path.join(ROOT, f["file"]), encoding="utf-8")))
    f["estimates"] = len(rows)
    f["studies"] = len({r["id"] for r in rows})
    # the main-set size is canonical in counts_crosswalk.md; read it rather than re-deriving the
    # predicate here, so this script cannot disagree with the drift check about what "main set" means
    cw = open(os.path.join(ROOT, "docs/counts_crosswalk.md"), encoding="utf-8").read()
    f["main_set"] = int(re.search(r"\| Estimates in the main analysis set \| (\d+) \|", cw).group(1))
    f["est_c"] = f"{f['estimates']:,}"
    f["studies_c"] = f"{f['studies']:,}"
    f["main_c"] = f"{f['main_set']:,}"
    return f


# (file, regex matching the whole stale line, replacement template)
# The regex must match EXACTLY ONE line. Keep each one anchored on wording that is unlikely to
# change, and on the numbers that go stale.
EDITS = [
    # README.md is the first file any reproducer reads, and it escaped the drift check for exactly
    # the same reason the others did: its status line names a version.
    ("README.md",
     r"analysis complete on frozen dataset \*\*v[\d.]+\*\* \([\d,]+ estimates / [\d,]+ studies\)",
     "analysis complete on frozen dataset **{version}** ({est_c} estimates / {studies_c} studies)"),
    ("docs/CODEBOOK_estimates.md",
     r"Counts and vocabularies below are as at \*\*v[\d.]+\*\* \([\d,]+ estimate rows /\n[\d,]+ studies\)",
     "Counts and vocabularies below are as at **{version}** ({est_c} estimate rows /\n{studies_c} studies)"),
    ("docs/CODEBOOK_estimates.md",
     r"All nine hold on v[\d.]+\.",
     "All nine hold on {version}."),
    ("docs/ENVIRONMENT.md",
     r"Freeze \*\*v[\d.]+\*\*\.",
     "Freeze **{version}**."),
    ("docs/prisma_checklist.md",
     r"\(frozen dataset v[\d.]+\)",
     "(frozen dataset {version})"),
    ("docs/grade_certainty_framework.md",
     r"Current result \(v[\d.]+\):",
     "Current result ({version}):"),
    ("docs/SI_lists_README.md",
     r"from freeze v[\d.]+ and the PRISMA",
     "from freeze {version} and the PRISMA"),
    ("docs/METHODS_PROVENANCE.md",
     r"As at freeze \*\*v[\d.]+\*\* \([\d-]+\): [\d,]+ estimate rows / [\d,]+ studies, [\d,]+ of them in the main",
     "As at freeze **{version}** ({date}): {est_c} estimate rows / {studies_c} studies, {main_c} of them in the main"),
    ("docs/data_quality_methods.md",
     r"the frozen \*\*v[\d.]+ \([\d,]+ estimates / [\d,]+ studies\)\*\*",
     "the frozen **{version} ({est_c} estimates / {studies_c} studies)**"),
    ("docs/reporting_summary_draft.md",
     r"Freeze \*\*v[\d.]+\*\* \(`data/extract_v2/estimates_v[\d.]+_frozen\.csv`,\n"
     r"MD5 `[0-9a-f]{32}`, git tag `dataset-frozen-v[\d.]+`, frozen [\d-]+\)",
     "Freeze **{version}** (`{file_base}`,\nMD5 `{md5}`, git tag `{tag}`, frozen {date})"),
    ("docs/reporting_summary_draft.md",
     r"Every count in this file is synced to freeze v[\d.]+\. Set this date",
     "Every count in this file is synced to freeze {version}. Set this date"),
    ("docs/reporting_summary_draft.md",
     r"Every count in this file is synced to freeze v[\d.]+\. One command",
     "Every count in this file is synced to freeze {version}. One command"),
    ("docs/reporting_summary_draft.md",
     r"the freeze underlying this paper is `estimates_v[\d.]+_frozen\.csv` \([\d,]+ estimates",
     "the freeze underlying this paper is `{file_name}` ({est_c} estimates"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()

    f = freeze_facts()
    f["file_base"] = f["file"]
    f["file_name"] = os.path.basename(f["file"])
    print(f"freeze {f['version']} ({f['date']}): {f['est_c']} estimates / {f['studies_c']} studies, "
          f"{f['main_c']} in the main set")

    stale, missed = [], []
    by_file = {}
    for path, rx, tmpl in EDITS:
        full = os.path.join(ROOT, path)
        txt = by_file.get(path) or open(full, encoding="utf-8").read()
        hits = list(re.finditer(rx, txt))
        if len(hits) != 1:
            missed.append(f"{path}: pattern matched {len(hits)} lines, expected 1 -> {rx[:60]}")
            continue
        new = tmpl.format(**f)
        if hits[0].group(0) != new:
            stale.append(f"{path}: {hits[0].group(0)[:78]!r}")
            txt = txt[:hits[0].start()] + new + txt[hits[0].end():]
        by_file[path] = txt

    for m in missed:
        print(f"  UNMATCHED  {m}")
    for s in stale:
        print(f"  stale      {s}")

    if a.check:
        if missed or stale:
            print(f"\nFAIL — {len(stale)} stale, {len(missed)} unmatched. "
                  "Run without --check to refresh.")
            return 1
        print("\nPASS — every generated freeze header is current.")
        return 0

    if missed:
        print("\nREFUSING TO WRITE while a pattern is unmatched: fix the pattern first, or the "
              "sentence it used to guard is now unguarded.")
        return 1
    for path, txt in by_file.items():
        open(os.path.join(ROOT, path), "w", encoding="utf-8").write(txt)
    print(f"\nrewrote {len(by_file)} file(s); {len(stale)} line(s) refreshed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
