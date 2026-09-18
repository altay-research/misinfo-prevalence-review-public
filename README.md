# Prevalence and concentration of misinformation exposure — replication package

Everything needed to reproduce the numbers, figures and tables of the systematic review, from one
frozen dataset. Built from the working repository on 2026-09-18, freeze **v1.7.23**
(1048 estimates from 443 studies), MD5 `08f050baf45086f45b5b3bec2390a115`.

The root holds six things: **`data/`** the dataset and everything derived from it, **`scripts/`**
the code, **`docs/`** the methods and the audit trail, **`searches/`** the queries behind the
corpus, **`companion/`** the interactive website, and this file. Nothing else is needed to
reproduce the paper, and `companion/` is not needed at all.

## What is here

| | |
|---|---|
| `data/extract_v2/estimates_v1.7.23_frozen.csv` | the frozen dataset. Every number in the paper comes from this one file. |
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
| `companion/` | the interactive website at altay-research.github.io, its source and the submission worker. Nothing here is needed to reproduce anything. |

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

Three stages cannot run offline from this package alone, by design rather than by omission:

- `validate_prisma.py` reconciles the PRISMA flow against the raw Scopus, OpenAlex and PubMed
  record dumps, which are not redistributable. Its output, `data/synth/prisma_counts.json`, is
  included, so `make_prisma.py` and `make_counts_crosswalk.py` still run.
- `venue_sensitivity.py` reads fetched OpenAlex abstracts. Its output,
  `data/synth/phaseB/venue_sensitivity.csv`, is included.
- `check_manuscript_stats.py` runs, and every statistic it asserts is re-checked here, with one
  check skipped: it verifies that an archived abstract exists on disk for each abstract-only
  study, and those archived abstracts sit under `data/fulltext/`, which is never redistributed.
  The script says so and carries on rather than failing. The abstract-only studies themselves are
  listed with their DOIs in `data/extract_v2/qa/abstract_only_list.json`, so the same check can be
  made against the publishers' own pages.

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

Altay, S. (2026). *Prevalence and concentration of misinformation exposure: a systematic
review.* Replication package, freeze v1.7.23.

## Contents

`MANIFEST.txt` lists every file in this package with its size, and records what the build
excluded and why.
