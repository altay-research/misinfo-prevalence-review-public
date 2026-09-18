# What the paper promises the replication package, and what the package ships

Audit of 2026-09-14, closed the same day. The question behind it is narrow: for every sentence in
the manuscript that tells a reader something is public, does the package built by
`scripts/build_public_package.py` actually contain it?

Five of the six findings were fixed in the builder. One could not be, and the manuscript sentence
has to change instead. That one is section 2.

---

## 1. The independent-model adjudication trail — FIXED, now ships

Methods §4.11: "the complete adjudication trail of the independent-model verification (**including
the rows where our coding was found wrong**)". Supplementary Note C3: "The audit trail is public in
the repository."

Before the fix, nothing matching `gpt_check_2026-09*` matched any ALLOW rule, in `docs/` or in
`data/extract_v2/qa/`. The package shipped none of it.

Now shipping: the three waves' blind and verify sheets, the sheets that came back, the instructions
and manifest each wave ran under, and the scored outcome tables
(`gpt_check_2026-09_KEY.csv`, `_disputes.csv`, `_scores.md`, and the wave-2 equivalents). The
disputes tables carry `RULING` and `RULING_reason` per row, which is the part §4.11 singles out.

Two files inside those folders are denied by name, because they are article text rather than our
coding:

- `docs/gpt_check_2026-09_wave3/batches/*` — the prompt sent for each wave-3 paper pastes that
  paper's **whole extracted body** (30–95 kB) below the instructions. This is `data/fulltext/`
  material sitting in `docs/`, and it carries the papers' corresponding-author contact lines. The
  wave's evidence is its `returns/`, which ship.
- `docs/gpt_check_2026-09_wave2/disputes_wave2.html` — the internal adjudication page embeds each
  disputed paper's front matter in expandable cards: authors, postal addresses, phone numbers,
  emails. Its rulings ship as `gpt_check_2026-09_wave2_disputes.csv`.

## 2. The abstract-only abstracts — NOT SHIPPED. The manuscript sentence must change.

Supplementary Note C3, limitation "Re-checkability", currently reads:

> Re-checkability: 32 studies were coded from the abstract alone because no full text could be
> obtained; **their abstracts are archived with the data, so the coding can be re-checked against
> the text it rests on**, and construct medians excluding all abstract-only appraisals are reported
> in Note B2.

The archive is `data/fulltext/abstract/` (29 files). It does not ship, and after review it should
not:

- These are **complete verbatim abstracts**, not the one-sentence quotations that section 3 of
  `LICENSE` covers under quotation provisions. Reproducing a whole abstract is a different act from
  quoting the sentence a number came from.
- 18 of the 29 were lifted from `data/abstracts/abstracts.jsonl`, a fetched-record store the
  denylist already excludes twice, by directory and by the `*_abstracts.jsonl` pattern. Shipping
  the files would release the records the pattern exists to hold back.
- Several are scraped publisher pages rather than deposited abstracts, navigation chrome included
  (`OA-W4360608277` opens "You have accessJournal of UrologyCME1 Apr 2023 … More articles by this
  author").
- Mechanically, shipping them means carving an exception into `data/fulltext/`, the strongest rule
  in the denylist, and then into the post-build re-scan, whose stated purpose is that a widened
  ALLOW cannot open exactly that kind of hole. The cost is not the 132 kB; it is the precedent in
  a rule that has to hold under a reviewer's reading.

Nothing about the coding becomes unauditable. Every abstract-only study is named with its DOI in
`data/extract_v2/qa/abstract_only_list.json`, and the coded value with its source quotation is in
the freeze. A reader re-checks against the publisher's own abstract page, one click from the DOI.

**The one-sentence correction the manuscript needs.** Replace, in Supplementary Note C3:

> their abstracts are archived with the data, so the coding can be re-checked against the text it
> rests on

with:

> each is listed with its DOI in the released data, so the coding can be re-checked against the
> abstract at its source

(Owner: the manuscript worker. Not applied here; `docs/manuscript_draft.md` was out of scope for
this pass.)

## 3. The recall-window file — FIXED, re-pointed

The package shipped `recall_windows_2026-08-12.csv`: 22 studies, three columns, no question
wording. The file of record is `recall_windows_2026-09-14.csv`: 71 studies, with
`question_verbatim`, `evidence_note` and `text_kind`. It is what §2.4 and Note B4 describe and what
`check_manuscript_stats.py` reads. The ALLOW list now names the current file.

## 4. `check_manuscript_stats.py` inside the package — FIXED

Five inputs were absent from the package, so the checker could not run at all. Four are ours and
now ship:

| Input | Status |
|---|---|
| `data/extract_v2/qa/recall_windows_2026-09-14.csv` | ships (finding 3) |
| `data/extract_v2/qa/curated_abstract_disclosure_2026-09-11.csv` | ships |
| `data/extract_v2/qa/curated_abstract_disclosure_2026-09-11_notcurated.txt` | ships |
| `data/extract_v2/repair_2026-09/repair_estimates_final.csv` | ships |
| `docs/corpus_repair_2026-09/REPAIR_REPORT.md` | ships |

The sixth input is the abstract archive of section 2, which cannot ship. That check now reports
itself skipped, by name and with the reason, instead of raising an `AssertionError` on a tree that
was withheld on purpose.

**The one check a third party cannot re-run:** that an archived abstract exists on disk for every
study with no full text. Nothing else. Every statistical assertion in the file runs on the package
as shipped.

## 5. Extracted full text with a corresponding author's email — FIXED

`docs/RA_package/value_verification_2026-09/papers/V070.html` is the extracted full text of
van Antwerpen et al., handed to the coders because no PDF existed for that paper. It carries the
corresponding author's email in the clear, and it would have shipped: the RA_package ALLOW rule
keeps `*.html`, and the `*.pdf` rule that hides every other paper in those folders does not touch
it.

The denylist now excludes `docs/RA_package/*/papers/*` as a tree, not by extension, so the next
non-PDF dropped in a coder folder cannot ship either. The original `V070.html` stays where it is;
the RA package uses it. Its two byte-identical Finder duplicates ("V070 2.html", "V070 3.html",
same MD5 `ba1280f8…`) went to the Trash.

The other two coder trees, `round3_2026-08/papers` (50 files) and `irr_v2/papers` (12 files), are
PDFs throughout. No other non-PDF exists under any `papers/` folder.

## 6. LICENSE — FIXED

The repository had none; the builder generated MIT + CC BY 4.0 at build time only. `LICENSE` now
sits at the repo root with the same two grants, the same third-party-material section, and
`Copyright (c) 2026 Sacha Altay`. The repo-root copy is freeze-agnostic (it points at
`docs/FROZEN.md`) where the built package's copy pins the freeze it was built from.

---

## Found in this pass, not in the audit

- **A second contact-detail leak, in a file that was already shipping.**
  `data/extract_v2/qa/missed_estimates/candidates.csv` quotes raw sentences out of the article
  texts, and one of them ran through the front matter of Tham-Agyekum et al. and swallowed its
  CONTACT line, two author email addresses included. Fixed in the generator
  (`scripts/scan_missed_estimates.py` now scrubs email addresses out of every candidate sentence)
  and the same substitution was applied to the existing queue, one row of 522. Nothing else in the
  row changed; the pre-scrub copy is in `.backups/`.
- **The builder had no way to catch that class.** The post-build scan looked for absolute
  `/Users/` paths but not for contact details. It now reports every email address in shipped text
  that is not one of the author's two published addresses, and a hit fails the build. The fix for
  a hit is always to redact at source, never to add an exception.
- **`--dry-run` did not run the exclusion scan**, so "the dry run is clean" meant only that
  selection had refused the obvious things. The dry run now runs the same three scans against the
  source files it would copy, and exits non-zero on a denylist hit.
