# data/ — what is where

About 3.3 GB across 19 directories. Most of it is retrieved source material; the analysis itself
turns on a handful of files. If you are here to reproduce the results, you need exactly four
things:

| you need | where |
|---|---|
| the frozen estimates dataset | `extract_v2/estimates_v<version>_frozen.csv` — the version named on the `File:` line of the **top block** of `../docs/FROZEN.md`, and nowhere else |
| what its 57 columns mean | [`../docs/CODEBOOK_estimates.md`](../docs/CODEBOOK_estimates.md) |
| the risk-of-bias appraisals | `rob/v3out/shard_*.csv` → `rob/risk_of_bias_v3_master.csv` |
| the two hand-curated inputs | `inputs/` |

Then run [`../docs/PIPELINE.md`](../docs/PIPELINE.md).

## Redistribution

**`fulltext/` and `PDFs/` are never redistributed.** They hold publisher PDFs and complete extracted
article bodies, which are the copyright of their publishers and are here only so every extracted
number stays checkable against its source. The same applies to `corpus_strict_v2_2026-06-20.jsonl`
and the Scopus dumps in `../searches/`: Elsevier's API terms prohibit redistributing the records.
`../docs/replication_package.md` is the authority on what a public package may contain.

## The directories

| directory | files | what it holds |
|---|---:|---|
| `extract_v2/` | 3,673 | **The estimate dataset and its whole history.** Every freeze `estimates_v1.x.y_frozen.csv` sits at the top level, immutable and MD5-stamped in `FROZEN.md`; the working files from the v1.2 rebuild sit beside them. Six subdirectories: `qa/` (below), `repair_2026-09/` (474, the corpus-repair extraction round), `full_reextract_2026-09/` (80), `wave3_2026-09/` (19), `reviews/`, `sensitivity_notrunc/`. |
| `extract_v2/qa/` | 2,897 | The audit trail: per-freeze changelogs, adjudication queues, decision pages, cross-check response files, and 52 subdirectories of extracted text per verification round. Named by campaign — `round3_keys/` (the round-3 human validation keys), `value_verification_keys/`, `irr_adjudication_papers/`, `blind/`, `missed_estimates/`, `missed_concentration/`, `title_rescreen/`, `abstract_rescreen/`, `rulings/`, `fable_qa_2026-08-11/`, `hand_found/` (the one with its own README). Sharded worklists (`aa_*.csv`, `a2_*.csv`) are batch slices from an agent coding round. |
| `fulltext/` | 3,522 | **Source material. Never redistributed.** `pdf/` (442) and `fetched/` (1,645) are publisher PDFs; `v2txt/` (1,102) the extracted article bodies the extraction rounds read; `txt/`, `v2txt_raw/`, `v2txt_reading/`, `abstract/` (29 archived abstracts for abstract-only studies) the rest. `shards*/`, `work/`, `extract/` are retrieval scratch. |
| `stage5/` | 521 | Stage-5 retrieval: the batch of records that advanced from abstract screening to full-text assessment, with their fetch logs. |
| `rob/` | 137 | Risk of bias. `v3out/shard_*.csv` are the per-shard appraisals; `risk_of_bias_v3_master.csv` is the aggregate `scripts/aggregate_rob_v3.py` builds from them, plus `rob_v3_summary.csv`, `rob_v3_by_construct.csv`, `rob_v3_item_distribution.csv`. `risk_of_bias_master{,_v2}.csv` are the superseded v1 and v2 instruments, kept for the reliability comparison. `repair_2026-09/` holds the corpus-repair shards. |
| `synth/` | 92 | Synthesis. `phaseB/` (61) is **every analysis output**, regenerated wholesale on each freeze — never hand-edit anything in it, and never put a hand-made file there. The top level holds the normalisation chain (`normalised_*.csv`, `to_normalise*.jsonl`) and `prisma_counts.json`, written by `validate_prisma.py`. |
| `screen_shards/` | 92 | Title-stage screening shards. `screen_shards_s2/` (21) is the abstract stage, `screen_shards_tag/` (7) the tagging pass. |
| `snowball/` | 49 | Backward and forward citation snowballing via OpenAlex, and what advanced from it. |
| `verify/` | 23 | Second-reader verification outputs from the Phase A verification round. |
| `extract/` | 17 | The v1 extraction, superseded by `extract_v2/`. Kept because `validate_prisma.py` reconciles against it. |
| `kappa/` | 15 | Inter-rater reliability worksheets and scored outputs. |
| `clean/` | 11 | Cleaned intermediate corpora from the screening stage. |
| `grey/` | 11 | Grey literature: the master list, the curation decisions, and `grey_verification.csv` with a per-row verdict. Protocol in `../docs/grey_lit_protocol.md`. |
| `exverify/` | 10 | Exclusion verification — a re-check of what the screen threw out. |
| `audit/` | 4 | Standalone audit outputs. |
| `inputs/` | 4 | **Hand-curated inputs with no generator.** See [`inputs/README.md`](inputs/README.md). |
| `abstracts/` | 2 | Fetched abstracts (`abstracts.jsonl`, `advancing_with_abstracts.jsonl`). **Gitignored** — regenerable only through a live OpenAlex fetch (`scripts/fetch_abstracts_openalex_batch.py`), which is why `venue_sensitivity.py` is the one pipeline stage an offline reproducer cannot re-run. |
| `new_papers/` | 2 | The screening inbox for PDFs dropped in by hand. |

## Top-level files (45)

- `corpus_strict_v2_2026-06-20.jsonl` — the full Scopus result set for the `strict_v2` Boolean, 2026-06-20. **Not redistributable** (Elsevier API terms).
- `openalex_netnew.jsonl`, `pubmed_netnew.jsonl` — records each database contributed beyond Scopus; `*_adjudicate.jsonl` are the screening dispositions for them.
- `screen_title_2026-06-20.csv`, `screen_abstract_2026-06-21.csv`, `screen_stage5_2026-06-21.csv` — the three screening stages, dated. These are what the PRISMA flow reconciles against.
- `oa_screen_*.csv` (32 slices) and `pm_screen_*.csv` (4) — the OpenAlex and PubMed screening shards behind those files.
- `seed_berriche_annexe1.csv` — the seed corpus digitised from Berriche (2024), used for the recall check.
- `screening_goldset.csv` — the hand-labelled gold set the screener was validated against.

## Conventions

- **The freeze is immutable.** Never edit a `*_frozen.csv`. A change is a new freeze, built by a
  script, MD5-stamped and git-tagged in `../docs/FROZEN.md`.
- **Coder files are never edited after delivery.** A fix to a generated file goes in its generator,
  not the file.
- **Deduplication is on content** (PDF MD5), not on identifiers — the same paper arrives under a
  Scopus EID, an OpenAlex id and a DOI.
- **Every output directory is disposable; every input directory is not.** `synth/phaseB/` can be
  deleted and rebuilt. `inputs/`, `rob/v3out/` and the freezes cannot.
