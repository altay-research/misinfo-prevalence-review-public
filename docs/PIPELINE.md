# PIPELINE — from the frozen dataset to the manuscript

Everything the review reports is computed from one file: the frozen estimates CSV named on the
`File:` line of the **top block** of [`FROZEN.md`](FROZEN.md). No script hardcodes that path; each
one re-reads the ledger, so the whole pipeline tracks the freeze automatically.

This document is the run order. It is derived from what each script actually reads and writes, not
from anyone's memory of it, and it corrects two ordering errors that lived in the informal order for
several freezes (§ *Ordering traps*). `scripts/run_phaseB.sh` executes the Python stages in exactly
this sequence and tells you where the two R stages go.

**Rule: after any re-freeze, run the whole thing.** Partial re-runs are how stale numbers get into a
manuscript. Several outputs read other outputs, so a skipped stage does not fail — it silently
computes against the *previous* freeze's file. That has happened here (`ratio_bootstrap.csv` at
v1.6.9) and is the reason this file exists.

---

## Quick start

```bash
cd <repo root>

bash scripts/run_phaseB.sh              # stages 1-4 and 6: everything before the meta-regression
Rscript scripts/phaseB_metareg.R        # stage 5. a few minutes; needs R 4.3 + metafor
bash scripts/run_phaseB.sh --post-metareg   # stages 7-8: the stages that read the metareg
                                            #             output, then the guards
```

The bootstrap (`phaseB_metareg_robustness.R`) is deliberately not in the script. Start it
by hand when the ladder has actually changed:

```bash
B=200 Rscript scripts/phaseB_metareg_robustness.R          # ~28 h
B=200 RESUME=1 Rscript scripts/phaseB_metareg_robustness.R # resume after an interruption
```

No third-party Python package is needed for any number in the paper. See
[`ENVIRONMENT.md`](ENVIRONMENT.md).

---

## Stage 0 — inputs

Nothing to run. These are what the pipeline consumes.

| input | what it is |
|---|---|
| `docs/FROZEN.md` | the freeze ledger. Top block's `File:` line is the **only** valid dataset pointer |
| `data/extract_v2/estimates_v*_frozen.csv` | the freeze itself, immutable and MD5-stamped |
| `data/rob/v3out/shard_*.csv` | the risk-of-bias appraisal shards (137 tracked files) |
| `data/extract_v2/qa/rob_appraisals_v145.csv` | the legacy per-study RoB table several scripts still join on |
| `data/extract_v2/qa/blind_reliability.csv` | the blind re-extraction subset, for sensitivity 3 |
| `data/inputs/*` | hand-curated inputs with no generator — see [`../data/inputs/README.md`](../data/inputs/README.md) |
| `data/synth/prisma_counts.json` | written by `validate_prisma.py`; feeds the PRISMA diagram and the crosswalk |

Everything written by the stages below lands in `data/synth/phaseB/` (tables), `data/rob/` (the RoB
master) or `docs/` (figures and HTML). **`data/synth/phaseB/` is regenerated wholesale. Never
hand-edit anything in it, and never put a hand-made file there** — that is what `data/inputs/` is
for.

## Stage 1 — risk of bias

```bash
python3 scripts/aggregate_rob_v3.py
```

Reads the shards + the freeze; writes `data/rob/risk_of_bias_v3_master.csv`, `rob_v3_summary.csv`,
`rob_v3_by_construct.csv`, `rob_v3_item_distribution.csv`.

**Run this whenever the study set changes** (any add or drop). Skip it and RoB coverage no longer
matches the freeze, and stage 4's GRADE table reads a stale master.

## Stage 2 — the analysis dataset

```bash
python3 scripts/phaseB_prep_regression.py
```

Reads the freeze + `rob_appraisals_v145.csv`; writes `data/synth/phaseB/regression_data.csv` —
the estimate-level modelling frame, including `denom_fine` (the 8-level denominator).

Two things about the `n` parser, learned the hard way: it enforces a strict K/M suffix regex, and it
carries an 11-row hand-audited `N_OVERRIDES` table for n-strings whose first number is not the
denominator. When a new row parses wrong, **extend the table; never loosen the regex.**

## Stage 3 — descriptive backbone

```bash
python3 scripts/phaseB_descriptives.py        # construct_distributions, concentration, whole_diet,
                                              # diagnostics, corpus_counts + docs/phaseB_descriptives.html
python3 scripts/phaseB_slices.py              # slices_*.csv (12 tables) + docs/phaseB_slices.html
python3 scripts/phaseB_platform_construct.py  # platform_by_construct.{csv,md}
```

`phaseB_platform_construct.py` owns `labels_for()`, the classifier that turns raw platform strings
into canonical labels (keyword rules + a 12-entry overrides table). `fig_coverage_panels.py` and
`check_manuscript_stats.py` **import** that function rather than reimplementing it, so section 2.1
and Figure 1 cannot drift apart. Run it before either.

## Stage 4 — the statistics

Order within this stage matters only where noted.

```bash
python3 scripts/phaseB_precision.py       # precision_weighting.csv  (needs regression_data.csv)
python3 scripts/phaseB_uncertainty.py     # uncertainty_medians, heterogeneity,
                                          # small_study_effects, leave_one_out_wholediet
python3 scripts/phaseB_sensitivity.py     # sensitivity.csv          (needs the RoB master)
python3 scripts/phaseB_grade.py           # grade_sof.csv            (needs uncertainty_medians +
                                          #                           precision_weighting + RoB master)
python3 scripts/phaseB_rob_sans610.py     # rob_sans610.csv          (needs the RoB master)
python3 scripts/phaseB_ratio_bootstrap.py # ratio_bootstrap.csv
python3 scripts/phaseB_recall_split.py    # recall_split.csv
python3 scripts/phaseB_subgroups.py       # subgroups.csv, subgroups_summary.json
python3 scripts/phaseB_temporal.py        # temporal.csv
python3 scripts/appendix_content_sharing.py   # appendix_content_sharing.csv
python3 scripts/phaseB_perturbation.py        # perturbation.csv — how much construct miscoding the
                                              #   exposure-recall gap absorbs before it closes
python3 scripts/phaseB_concentration_null.py  # concentration_null.csv — is misinformation actually
                                              #   more concentrated, or only rarer?
python3 scripts/venue_sensitivity.py      # venue_sensitivity.csv    (NOT offline-reproducible)
```

`phaseB_grade.py` must follow `phaseB_uncertainty.py` and `phaseB_precision.py`; both feed its
imprecision and inconsistency judgements. Everything else in this stage reads only the freeze and
the RoB master.

Two standing conventions that have broken before:

- In `phaseB_uncertainty.py`, the **medians use the full main set**; only I², τ² and the Spearman
  small-study test use the n-restricted subset, because those require n. Do not let the two
  populations converge.
- `appendix_content_sharing.py` must be re-run after **any** recode touching `construct` or
  `ground_truth` — its strata moved at both v1.7.8 and v1.7.9. Its point estimate is the observed
  difference; the bootstrap supplies only the interval.

`venue_sensitivity.py` reads `data/abstracts/*.jsonl`, which is gitignored and only regenerable
through a live OpenAlex fetch. It is part of the pipeline but is the one stage an offline reproducer
cannot re-run; the committed `venue_sensitivity.csv` stands as the record.

## Stage 5 — meta-regression (R)

```bash
Rscript scripts/phaseB_metareg.R
```

Reads `regression_data.csv`; writes `metareg_univariable.csv`, `metareg_multivariable.csv`,
`metareg_measurement_pred.csv`. metafor logit-PLO, random effects `~1|study_id/estimate_id`,
cluster-robust omnibus on every fit (the CSV carries both the robust `QMp` and `QMp_model`). Sparse
levels are collapsed uniformly across all ten moderators at `MIN_LEVEL_N = 10`; relevelling happens
**after** the collapse (the `set_ref` guard exists because doing it the other way round silently
left `breadth` at the alphabetical default). Uncoded cells enter as an explicit `"unspecified"`
level rather than being row-dropped — `breadth` has 141 of them. The reported R² is the df-adjusted
one.

Then, only when the ladder has moved:

```bash
B=200 Rscript scripts/phaseB_metareg_robustness.R
```

Writes `metareg_r2_bootstrap.csv` and `metareg_r2_within_content.csv` — the §2.6 bootstrap
intervals and the within-CONTENT ladder. **This takes about 25 minutes at B = 200**, which is the
value behind the published intervals. It checkpoints after every resample to
`data/synth/phaseB/.metareg_boot_checkpoint.rds` (gitignored) and resumes with `RESUME=1`; the
checkpoint is only reused when `MODS` and `B` match, so changing either starts fresh. `B=5`
smoke-tests the plumbing in minutes without reproducing the intervals.

## Stage 6 — figures

**This is where the order actually bites.** Each script embeds or reads what the one above it wrote.

```bash
python3 scripts/phaseB_export_json.py         # estimates_full.json  (+ titles.json if present)
python3 scripts/phaseB_figures.py             # fig1-fig4 + concentration_source.csv
                                              #            + concentration_standardized.csv
python3 scripts/phaseB_concentration_table.py # concentration_by_threshold.csv  <- needs the line above
python3 scripts/phaseB_review_response.py     # review_*.csv (6 tables answering the 2026-08-24 review)
                                              #   moved ahead of the figures: figQ plots its
                                              #   review_matched_concentration.csv
python3 scripts/phaseB_figures3.py            # figI, figJ, figK, figQ, figL    <- needs the two above
python3 scripts/phaseB_figures2.py            # figF, figG + docs/phaseB_figure_gallery.html
                                              #   embeds fig1/2/4 and figI-figL, so it runs LAST
python3 scripts/fig_coverage_panels.py        # figN (manuscript Fig 1), figP_*, coverage_*.csv
python3 scripts/make_forest_plot.py           # fig5  (needs uncertainty_medians + recall_split)
```

`fig_coverage_panels.py` uses **one** drawing routine for every moderator panel. Never fork it. The
regression check when you touch it: the platform SVG must come out byte-identical.

`phaseB_review_response.py` reads `regression_data.csv`, the RoB master,
`data/inputs/nonmisinfo_concentration.csv` and the RA package's answer keys, all of which are in
place by stage 5, so it runs here rather than in stage 7.

Figure labels come from `scripts/fig_labels.py`, the single map from codebook levels to prose.
A level with no entry there prints as its raw snake_case code, so the generators warn when they
draw one: add the label to `PRETTY` rather than patching the SVG.

## Stage 7 — HTML deliverables

All of these read stage 5 and stage 6 output, so they come after both.

```bash
python3 scripts/build_litreview_html.py       # docs/litreview_measurement.html + docs/fig_funnel.svg
                                              #   reads metareg_univariable + metareg_measurement_pred
python3 scripts/build_companion_dashboard.py  # docs/companion_dashboard.html (reads estimates_full.json)
python3 scripts/phaseB_dashboard.py           # docs/phaseB_dashboard.html — embeds every SVG,
                                              #   reads the metareg CSVs, grade_sof, slices, precision
python3 scripts/build_site.py                 # site/ — the PUBLIC companion site, generated from
                                              #   site_src/ + the freeze + the phaseB outputs.
                                              #   Served by GitHub Pages from the public repo.
```

The public site is generated, never hand-edited: `site_src/` holds the pages and assets,
`site/` is build output. Its aggregation is a second implementation of a published statistic
(`site/assets/agg.js` ports `scripts/lib_slices.py`), so `check_site.py` reproduces every published
slice row in both languages and fails the build on a mismatch.

## Stage 8 — ledgers and guards

Run these last, in this order. The last three gate the freeze.

```bash
python3 scripts/make_behavioural_arm_dispositions.py  # terminal states for the behavioural arm;
                                            #   re-run whenever the study set changes
python3 scripts/sync_provenance_ledger.py   # regenerates the freeze table in dataset_provenance.md
python3 scripts/sync_doc_freeze_headers.py  # regenerates the "as at freeze vX (N/M)" lines in the docs
python3 scripts/validate_frozen.py          # integrity gate on the frozen CSV
python3 scripts/validate_prisma.py          # PRISMA reconciliation -> data/synth/prisma_counts.json
python3 scripts/check_invariants.py         # 9 codebook invariants + the FROZEN.md MD5 check
python3 scripts/check_manuscript_stats.py   # every derived stat in the manuscript, against the pipeline
python3 scripts/make_prisma.py              # docs/prisma_flow.svg, asserted against the reconciliation
python3 scripts/make_si_lists.py            # si_included_studies.csv, si_fulltext_exclusions.csv,
                                            #   docs/SI_lists_README.md — PRISMA items 16b and 17
python3 scripts/make_si_characteristics.py  # Supplementary Data 1 — PRISMA 17-19, per included study
python3 scripts/make_counts_crosswalk.py    # the canonical counts table + the repo-wide drift check
python3 scripts/check_site.py               # every number rendered into site/, plus the JS<->Python
                                            #   aggregation parity test (needs node on PATH)
python3 scripts/check_pipeline_docs.py      # this block and run_phaseB.sh must name the same scripts
```

`make_si_lists.py` must follow `validate_prisma.py`: it imports the flow figure's reason labels and
asserts its per-reason row counts against `prisma_counts.json`, so a stale reconciliation makes it
fail rather than ship a study list that contradicts the figure. Its offline run is deterministic;
`--fetch` adds a DOI-registry lookup for bibliography gaps and caches the result to
`data/synth/si_biblio_cache.json`, which is what makes every later run offline.

Non-zero exit from `check_invariants.py` **blocks the freeze**. `make_counts_crosswalk.py` exits
non-zero when any current document contradicts the canonical counts; it checks counts only, not
derived statistics, so §2 and §3 of the manuscript still need a manual sweep after a re-freeze.

`sync_provenance_ledger.py` regenerates the freeze table inside `dataset_provenance.md` from
`FROZEN.md`. The two had silently diverged by 21 freezes before this was automated. The table is
generated; do not hand-edit it.

`sync_doc_freeze_headers.py` does the same job for the one-line freeze headers that several current
documents carry ("Counts below are as at **v1.7.20** (1,048 estimate rows / 443 studies)"). Naming a
version is what the drift check treats as provenance rather than staleness, so those lines had a
standing exemption from it and sat two freezes behind. They are generated now. It is a CURATED list
of file-and-pattern pairs, because most `v1.7.x` mentions in the same files are real history; a
pattern that stops matching is an error, not a silent skip. `--check` reports without writing.

The run order in this block and in `scripts/run_phaseB.sh` must agree, and
`scripts/check_pipeline_docs.py` asserts that they do.

---

## Ordering traps

Three real dependencies that the informal run order got wrong. All three fail *silently* on an
already-populated repository — the script finds last freeze's file and computes against it — which
is exactly why they survived so long.

1. **`phaseB_concentration_table.py` must run AFTER `phaseB_figures.py`.** It reads
   `concentration_standardized.csv`, which `phaseB_figures.py:212` writes. The old order put the
   table right after GRADE, well before the figures. In a clean room it fails outright with
   `FileNotFoundError`; in this repo it quietly used the previous freeze's concentration standardisation.
2. **`phaseB_dashboard.py` and `build_litreview_html.py` must run AFTER `Rscript
   phaseB_metareg.R`.** Both read `metareg_univariable.csv`, `metareg_multivariable.csv` and
   `metareg_measurement_pred.csv`. The old order put the dashboards before the meta-regression.
3. **`phaseB_figures2.py` runs LAST among the figure scripts, and `phaseB_export_json.py` first.**
   figures2 reads `estimates_full.json` and inlines fig1/fig2/fig4 (from `phaseB_figures.py`) and
   figI–figL (from `phaseB_figures3.py`) into the gallery. The shorthand `phaseB_figures{,2,3}.py`
   gets this backwards.

Five pipeline scripts were missing from the informal order entirely, and four of them produce
numbers the manuscript or its checker quotes:

| script | output | cited by |
|---|---|---|
| `phaseB_metareg_robustness.R` | `metareg_r2_bootstrap.csv`, `metareg_r2_within_content.csv` | §2.6 intervals; asserted in `check_manuscript_stats.py` |
| `phaseB_subgroups.py` | `subgroups.csv`, `subgroups_summary.json` | §2.9 demographic subgroups |
| `phaseB_review_response.py` | 6 × `review_*.csv` | matched concentration ratio (§2.10 and figQ), Cramér's V, weight shares |
| `phaseB_temporal.py` | `temporal.csv` | the temporal moderator (no manuscript assertion) |
| `venue_sensitivity.py` | `venue_sensitivity.csv` | corpus composition by publication type |

---

## What is *not* in this pipeline

`scripts/` holds about 240 files. Only the ~30 above are the live pipeline. The rest fall into four
groups, and a reproducer should not try to run them:

- **Freeze-history one-offs (~73)** — `apply_v1XX.py`, `build_v1.X.py`, `reaudit_*.py`. Each builds
  one freeze from the one before it and names its specific input freeze on purpose. They are the
  audit trail of how the dataset reached the current freeze, not code to re-run. `FROZEN.md` names the builder
  of every freeze.
- **QA / coding-round one-offs (~89)** — `build_*`, `score_*`, `merge_*`, `aggregate_*`,
  `adjudicate_*`. Each belongs to one verification round (a cross-model pass, a human IRR round, an
  adjudication queue) and expects that round's artefacts.
- **Search and retrieval (~30)** — `scopus_search.py`, `openalex_keyword_search.py`,
  `pubmed_search.py`, the abstract fetchers, the PDF recovery tools. Live APIs, dated results, a
  `$SCOPUS_KEY` for Scopus. Counts are reproducible only as of their run date.
- **Deliverable builders (~9)** — `make_manuscript_docx.py`, `make_nhb_docx.py`,
  `make_tracked_docx.py`, `make_arcom_docx.py`, `make_box1.py`. These need `python-docx`/`lxml`.

**Ten of the historical scripts cannot be replayed at all**: `aggregate_cadj.py`,
`aggregate_qual_audit.py`, `aggregate_reread.py`, `aggregate_rob.py`, `aggregate_topics.py`,
`apply_found.py`, `apply_hv.py`, `apply_phaseA.py`, `build_v1.3.py`, `make_review_sheets.py`. They
read agent scratch directories under `$CLAUDE_JOB_DIR` that no longer exist. Their *outputs* are all
committed (the freezes, `data/extract_v2/qa/`), so nothing is lost; the freeze chain simply cannot be
re-executed from the top. It can be verified — every freeze's MD5 and git tag are in `FROZEN.md`.

---

## Determinism

Every stage is deterministic and reproduces byte-identical output on a re-run against the same
freeze. Verified in a clean room on 2026-09-07 for `phaseB_prep_regression.py`,
`phaseB_recall_split.py` and `check_invariants.py`, and again here for `phaseB_figures3.py` and
`phaseB_review_response.py` after their input paths moved.

Seeds and compute cost are listed in [`ENVIRONMENT.md`](ENVIRONMENT.md).

## Blind re-extraction campaign (2026-09) — COMPLETE, merged at v1.7.18

Never part of the regenerate-everything run: it produced rulings that a freeze script consumed. All
57 batches ran, all 456 studies then in the corpus were scored, the author ruled 592 items on
2026-09-08 and 09-10, and `apply_v1718.py` applied them (36 removals, 30 addition sets, 160
corrections, 29 manual items). The order below is kept so the campaign can be re-run or audited.
Order: `build_full_reextraction.py` -> extraction agents -> `validate_repair_extractions.py
--dir data/extract_v2/full_reextract_2026-09 --batch N` -> `score_full_reextract.py` ->
`build_reextract_adjudication.py` (Sacha's page) -> archive rulings -> `plan_reextract_merge.py`
(-> `merge_plan.py`, imported by the freeze script). See
`data/extract_v2/full_reextract_2026-09/README.md`. The behavioural-arm screening
(`build_behavioural_screen.py`, screening agents, then aggregation) was a search top-up on the same
path; it is also complete, and its 20 studies are in the released freeze.
