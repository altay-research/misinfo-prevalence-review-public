#!/usr/bin/env bash
# run_phaseB.sh — regenerate the whole Phase B analysis from the current freeze.
#
# The run order lives here and in docs/PIPELINE.md, and the two must agree. Ordering is not
# cosmetic: several stages read what an earlier stage wrote, and on an already-populated repo a
# skipped stage does not fail — it silently computes against the PREVIOUS freeze's file.
#
# The two R stages are not run here. phaseB_metareg.R needs R + metafor and takes minutes;
# phaseB_metareg_robustness.R takes about 25 minutes. The script stops where the first is needed,
# prints the command, and resumes with --post-metareg.
#
#   bash scripts/run_phaseB.sh                 stages 1-4 and 6 (everything before the metareg)
#   Rscript scripts/phaseB_metareg.R           by hand
#   bash scripts/run_phaseB.sh --post-metareg  stage 7 and the guards
#   bash scripts/run_phaseB.sh --all           both halves, assuming the metareg CSVs are current
#
# Env: PY overrides the interpreter (default python3). Exits non-zero on the first failure.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PY="${PY:-python3}"

MODE="${1:-pre}"
case "$MODE" in
  ""|pre)          MODE=pre ;;
  --post-metareg)  MODE=post ;;
  --all)           MODE=all ;;
  -h|--help)       sed -n '2,/^[^#]/p' "${BASH_SOURCE[0]}" | grep '^#' | sed 's/^# \{0,1\}//'; exit 0 ;;
  *) echo "unknown argument: $MODE  (use --post-metareg, --all or nothing)" >&2; exit 2 ;;
esac

# Some stages read inputs the PUBLIC PACKAGE does not redistribute (the raw record dumps, the
# working-repository docs). In the package they are skipped BY NAME, with the reason printed, and
# their outputs ship with the package. Tested by cloning the public repository and running the
# three commands in its README end to end (2026-09-18): a stage that fails on a missing input took
# the whole runner down at stage 8 and nothing after it ran.
needs() {
  case "$1" in
    validate_prisma.py|make_prisma.py|make_si_lists.py) echo data/openalex_adjudicate.jsonl ;;
    sync_doc_freeze_headers.py)                         echo docs/reporting_summary_draft.md ;;
    *) echo "" ;;
  esac
}
step() {
  printf '\n\033[1m>>> %s\033[0m\n' "$*"
  local req; req="$(needs "$1")"
  if [ -n "$req" ] && [ ! -e "$req" ]; then
    printf '    SKIPPED: needs %s, which the public package does not redistribute; the outputs of this stage ship with the package.\n' "$req"
    return 0
  fi
  "$PY" "scripts/$1"
}

freeze="$(sed -n 's/^- File:[[:space:]]*//p' docs/FROZEN.md | head -1)"
printf '\033[1mfreeze:\033[0m %s\n' "$freeze"
[ -f "$freeze" ] || { echo "freeze file missing: $freeze" >&2; exit 1; }

run_pre() {
  # --- stage 1: risk of bias (rerun whenever the study set changes) ---
  step aggregate_rob_v3.py

  # --- stage 2: the analysis dataset every model reads ---
  step phaseB_prep_regression.py

  # --- stage 3: descriptive backbone ---
  step phaseB_descriptives.py
  step phaseB_slices.py
  step phaseB_platform_construct.py     # owns labels_for(), imported by stage 6 and the guards

  # --- stage 4: the statistics ---
  step phaseB_precision.py
  step phaseB_uncertainty.py
  step phaseB_sensitivity.py
  step phaseB_grade.py                  # after uncertainty + precision
  step phaseB_rob_sans610.py
  step phaseB_ratio_bootstrap.py
  step phaseB_recall_split.py
  step phaseB_subgroups.py
  step phaseB_temporal.py
  step appendix_content_sharing.py
  step phaseB_perturbation.py            # how much construct miscoding the gap absorbs
  step phaseB_concentration_null.py      # is misinformation more concentrated, or just rarer?
  # venue_sensitivity.py needs data/abstracts/*.jsonl, which is gitignored and only regenerable
  # from a live OpenAlex fetch. Run it only when those files are present.
  if [ -f data/abstracts/abstracts.jsonl ]; then
    step venue_sensitivity.py
  else
    printf '\n\033[33mskip venue_sensitivity.py — data/abstracts/*.jsonl absent (live OpenAlex fetch)\033[0m\n'
  fi

  # --- stage 6: figures. Order matters; see docs/PIPELINE.md "Ordering traps". ---
  step phaseB_export_json.py            # estimates_full.json, read by figures2 + the companion
  step phaseB_figures.py                # writes concentration_standardized.csv
  step phaseB_concentration_table.py    # reads it
  step phaseB_figures3.py               # reads concentration_by_threshold.csv
  step phaseB_figures2.py               # embeds fig1/2/4 and figI-figL: runs last
  step fig_coverage_panels.py
  step make_forest_plot.py
}

run_post() {
  # --- stage 7: HTML deliverables (all read the metareg output) ---
  step build_litreview_html.py
  step build_companion_dashboard.py
  step phaseB_dashboard.py
  step phaseB_review_response.py
  step build_site.py                    # site/ — the public companion, from the freeze

  # --- stage 8: ledgers and guards. check_invariants gates the freeze. ---
  step make_behavioural_arm_dispositions.py   # terminal states for the arm's advanced records.
                                    # A study LEAVING the freeze changes its state from
                                    # ARM_INCLUDED_FROZEN to ARM_EXCLUDED_AT_RULING, and
                                    # validate_prisma then has an unmapped state. It was in
                                    # neither run order until v1.7.23 hit exactly that.
  step sync_provenance_ledger.py
  step sync_doc_freeze_headers.py   # the "as at freeze vX (N/M)" lines in the current docs.
                                    # They name a version, which exempts them from the drift
                                    # check, so they went two freezes stale unnoticed.
  step validate_frozen.py
  step validate_prisma.py
  step check_invariants.py
  step check_manuscript_stats.py
  step make_prisma.py
  step make_si_lists.py            # PRISMA 16b/17: the two SI study lists.
                                   # It asserts its per-reason counts against
                                   # prisma_counts.json, so it must follow
                                   # validate_prisma.py. It was missing from this
                                   # script, so after a re-freeze the two lists
                                   # silently described the previous corpus.
  step make_si_characteristics.py   # Supplementary Data 1: PRISMA 17-19, per included study
  step make_counts_crosswalk.py
  step check_site.py                    # site numbers + JS/Python aggregation parity
  step check_pipeline_docs.py       # the two run orders must name the same scripts
}

case "$MODE" in
  pre)  run_pre ;;
  post) run_post ;;
  all)  run_pre; run_post ;;
esac

if [ "$MODE" = "pre" ]; then
  cat <<'MSG'

============================================================
Python stages before the meta-regression are done.

Now run the R stages by hand (R 4.3 + metafor + boot):

  Rscript scripts/phaseB_metareg.R
      -> metareg_univariable.csv, metareg_multivariable.csv, metareg_measurement_pred.csv
      a few minutes.

  B=200 Rscript scripts/phaseB_metareg_robustness.R
      -> metareg_r2_bootstrap.csv, metareg_r2_within_content.csv
      ABOUT 25 MINUTES at B=200, the value behind the published intervals.
      Checkpoints to data/synth/phaseB/.metareg_boot_checkpoint.rds after every resample;
      resume with  B=200 RESUME=1 Rscript scripts/phaseB_metareg_robustness.R
      Only needed when the variance-explained ladder has actually moved.

Then finish the pipeline:

  bash scripts/run_phaseB.sh --post-metareg
============================================================
MSG
else
  printf '\n\033[1mPhase B complete.\033[0m All guards passed.\n'
fi
