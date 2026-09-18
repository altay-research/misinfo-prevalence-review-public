# Public Replication Package — manifest & legal boundary

The working repo is ~5.1 GB and contains material that **cannot be redistributed**:
- **PDFs** (`PDFs/`, `data/fulltext/`) — third-party copyright.
- **Scopus records** (`data/corpus_strict_v2_*.jsonl`, `searches/scopus_*`) — Elsevier
  API terms prohibit redistribution of retrieved records.
- **Full OpenAlex/PubMed record dumps** — redistribute IDs/DOIs, not full records.

## What the PUBLIC package (OSF) SHOULD contain
Include (all author-generated or non-copyright):
- `scripts/` — all search, screening, extraction, validation scripts (incl.
  `validate_frozen.py`, `validate_prisma.py`, `rob_reliability.py`).
- `docs/` — protocol, PRISMA-P, methods provenance, `llm_provenance.md`, decisions
  register, research log, criteria/prompt files (`screening_criteria*.txt`,
  `construct_tagging.txt`, `rob_checklist_v3.md (the Hoy-adapted instrument of record; the superseded v2 rob_checklist.txt ships as history)`, extraction/value protocols).
- **Coding sheets & answer key** — `RA_package/` (blind sheet + instructions;
  answer key released post-review). The `papers/` folder of each coding round is the set of
  articles handed to the coders, and never ships.
- **The independent-model adjudication trail** — `docs/gpt_check_2026-09*/` (sheets out, sheets
  back, instructions per wave) and `data/extract_v2/qa/gpt_check_2026-09*` (the scored KEY,
  disputes and rulings). Methods §4.11 names this trail specifically, "including the rows where
  our coding was found wrong", so it is a promise, not an optional extra. Two files inside those
  folders are article text rather than coding and are denied by name: the wave-3 prompt bodies
  and the wave-2 disputes page.
- **Our extracted data** — the frozen estimates CSV named on the `File:` line of the top block of
  `docs/FROZEN.md` (the builder resolves the pointer; it does not hardcode a filename), plus the
  legacy `data/extract_v2/estimates_reextracted.csv` if present, the RoB appraisals and the kappa
  result tables. Our own coding, and redistributable.
- **Hand-curated inputs** — `data/inputs/` (+ its README). The pipeline reads these and
  nothing regenerates them, so a package without them does not run.
- **Analysis outputs** — `data/synth/phaseB/`, all author-generated and all regenerable
  from the freeze by `docs/PIPELINE.md`.
- **How to run it** — `docs/PIPELINE.md`, `docs/ENVIRONMENT.md`, `docs/CODEBOOK_estimates.md`,
  `data/README.md`, `requirements.txt`, `scripts/run_phaseB.sh`.
- **Identifier lists, not records** — DOIs / EIDs / OpenAlex IDs / PMIDs per stream
  and per terminal state, so anyone can re-retrieve from source. Derive from
  `data/extract_v2/qa/frozen_dois.json` + the PRISMA reconciliation output.
- **PRISMA flow** (`docs/prisma_flow.svg`) + reconciliation report.

## What to EXCLUDE (never upload)
- Any PDF or extracted full-text (`PDFs/`, `data/fulltext/`), wherever it sits. Extracted article
  bodies have twice turned up outside `data/fulltext/`: as an HTML text extraction in a coder
  `papers/` folder, and pasted into the wave-3 extraction prompts under `docs/`. Both carried the
  papers' corresponding-author contact details. The denylist covers the trees, not the extensions.
- `data/fulltext/abstract/` — archived abstracts for the abstract-only studies. Held back with the
  rest of the tree; the reasoning and the manuscript correction it forces are in
  `docs/package_promises_2026-09-14.md`.
- Any third-party contact detail in shipped text. A quoted sentence can run through an article's
  CONTACT line; the build scans for it and fails on a hit.
- Raw Scopus/OpenAlex/PubMed record dumps (`data/corpus_*`, `data/*_netnew.jsonl`,
  `searches/*`). Replace with ID + query-string + run-date so the search is
  reproducible without redistributing records.
- `.secrets`, `*.key`, anything with an API key (already gitignored).
- `.work/`, `.backups/` (Claude-internal).

## Build step
`scripts/build_public_package.py` copies the allowed set into `dist/public/`, emits per-stream ID
lists (no records), runs three exclusion scans over what it would ship (denylist hits, absolute
`/Users/` paths, and contact details that are not the author's own published addresses), and writes
a README with the search strings and run dates. A denylist or contact-detail hit fails the build,
and `--dry-run` runs the same scans against the source files it would copy.

## Status
Manifest defined 2026-07-02; builder written and audited against the manuscript's own promises on
2026-09-14 (`docs/package_promises_2026-09-14.md`, six findings, five fixed in the builder). Rebuild
from the final freeze before deposit, so the deposited IDs match the corpus that ships. The search
currency top-up is not a blocker for a 2026 submission: the June 2026 searches are inside PRISMA's
12-month currency window, and the September behavioural and Scholar top-ups are more recent still.

Audited against the manuscript's own promises on 2026-09-14: every sentence that tells a reader
something is public was checked against what the builder selects. Five gaps closed in the builder,
one closed by correcting the manuscript. Findings, reasoning and the sentence that has to change
are in `docs/package_promises_2026-09-14.md`. A `LICENSE` now sits at the repo root carrying the
same MIT + CC BY 4.0 split the builder writes into the package.
