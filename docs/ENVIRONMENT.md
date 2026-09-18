# Environment

The software the published numbers were produced on, and the minimum a reproducer needs.
Freeze **v1.7.23**. Recorded 2026-09-07, freeze pointer refreshed 2026-09-14.

## Interpreters

| | version used | what it runs |
|---|---|---|
| Python | **3.14.5** (Homebrew, `/opt/homebrew/bin/python3`) | every pipeline stage except the two meta-regressions |
| R | **4.3.0** (2023-04-21), platform `aarch64-apple-darwin20` | `scripts/phaseB_metareg.R`, `scripts/phaseB_metareg_robustness.R` |
| OS | macOS 15.7.4, arm64 | — |

Nothing in the pipeline uses a Python feature newer than 3.11. The scripts are stdlib-only, so
any 3.11+ interpreter should reproduce them; 3.14.5 is what the freeze was computed on.

## Python packages

The analysis is **stdlib only** — no numpy, scipy, pandas or matplotlib. Figures are hand-rolled
SVG; the bootstrap, the DerSimonian-Laird pooling and the incomplete-beta t-tail are written
against the standard library. Every headline number in the manuscript regenerates with no
third-party package installed.

Three packages are needed only for document building and PDF retrieval (`requirements.txt`):

| package | version | needed by |
|---|---|---|
| `python-docx` | 1.2.0 | `make_manuscript_docx.py`, `make_nhb_docx.py`, `make_arcom_docx.py` |
| `lxml` | 6.1.1 | `make_tracked_docx.py` (raw OOXML tracked changes) |
| `pypdf` | 6.14.2 | `recover_pdfs.py` (falls back to `PyPDF2`) |

```bash
pip install -r requirements.txt      # only for the .docx builders and PDF retrieval
```

## R packages

```r
install.packages(c("metafor", "boot"))
```

Installed versions, with the dependencies metafor pulls in:

| package | version | role |
|---|---|---|
| `metafor` | 4.2.0 | `escalc(measure="PLO")`, `rma.mv` multilevel fits, cluster-robust omnibus |
| `boot` | 1.3.28.1 | bootstrap machinery |
| `Matrix` | 1.5.4 | metafor dependency |
| `nlme` | 3.1.162 | metafor dependency |
| `numDeriv` | 2016.8.1.1 | metafor dependency |
| `mathjaxr` | 1.6.0 | metafor dependency |

Both R scripts resolve the repository root from their own file location, so they run from any
checkout. `MISINFO_ROOT` overrides that if you need to point them elsewhere.

## External command-line tools

| tool | version | needed by |
|---|---|---|
| `pdftotext` (poppler) | 26.03.0 | the full-text extraction helpers in `scripts/` (retrieval stage only, not the analysis) |
| `git` | any | the freeze ledger tags every frozen dataset |

## Network

The analysis pipeline is **fully offline**. The search and retrieval scripts are not: Scopus
(`$SCOPUS_KEY`), OpenAlex, PubMed, Semantic Scholar and Crossref are all live APIs, and their
counts are only reproducible as of the run date recorded next to each. One pipeline-adjacent
script, `venue_sensitivity.py`, reads `data/abstracts/*.jsonl`, which is gitignored and
regenerable only via a live OpenAlex fetch (`scripts/fetch_abstracts_openalex_batch.py`) — its
output `venue_sensitivity.csv` is therefore not offline-reproducible.

## Compute cost

One stage is expensive. `scripts/phaseB_metareg_robustness.R` runs a study-cluster bootstrap of
the pseudo-R² ladder: **B = 200 resamples, roughly 25 minutes** single-threaded on the machine
above. It checkpoints after every resample to
`data/synth/phaseB/.metareg_boot_checkpoint.rds` (gitignored) and resumes with `RESUME=1`:

```bash
B=200 RESUME=1 Rscript scripts/phaseB_metareg_robustness.R
```

`B` is read from the environment and defaults to 200 — the value behind the published intervals
(e.g. ground truth 21.4 [16.5–27.7] in §2.6). A smoke run with `B=5` finishes in minutes and
verifies the plumbing without reproducing the intervals.

Everything else in the pipeline finishes in seconds to a couple of minutes. `phaseB_metareg.R`
takes a few minutes; the rest of Phase B runs end to end in well under five.

## Determinism

Every stochastic step sets a seed, and re-running any stage on the same freeze reproduces its
output byte for byte. Seeds in use: `phaseB_precision.py` 20260722, `phaseB_uncertainty.py`
20260723 (B = 2000), `phaseB_ratio_bootstrap.py`, `phaseB_review_response.py` 20260824,
`appendix_content_sharing.py` 7, `phaseB_metareg_robustness.R` 20260902.
`phaseB_recall_split.py` takes its seed as a parameter.

One historical gotcha, fixed and worth not reintroducing: `phaseB_precision.py` built its frame
from a set, which made its confidence intervals depend on `PYTHONHASHSEED`. It uses an
insertion-ordered frame since 2026-08-11. Do not reintroduce set iteration into an ordered
computation.
