# RA_package — human coding rounds

## Layout
- `irr_v2/` — the COMPLETED human IRR (v3 design, built on FROZEN v1.5.6+): coder worksheets +
  HTML coding pages (`code_<coder>.html`), blind-named PDFs in `papers/`, ANSWER_KEY.csv,
  sample_manifest.csv. BOTH coders' sheets are committed (Sacha + Laura, two batches, 35
  full-paper items); scored and reported in manuscript §4.8 (denominator κ .84, construct .60). Score with `scripts/score_human_irr.py`; build with
  `scripts/build_human_irr_worksheet.py` + `scripts/build_irr_coding_html.py`.
  (The `perplexity_*` files are the cross-model sweep artifacts — kept here because the
  ingest/score scripts reference these paths.)
- `round1_2026-07/` — ARCHIVE of the first RA round (Laura, July 2026: inclusion decisions,
  κ = 0.33, adjudication of 29 contested cases, construct agreement 42/51). Cited in
  manuscript §4.8; nothing here is live.
- Root files (`RA_coding_sheet.csv`, `_ANSWER_KEY.csv`, `laura_vs_key_disagreements.csv`,
  `ra_kappa_dual.json`, `ra_scoring_result.json`) stay at root because scripts reference
  these paths (`build_human_irr_worksheet.py` uses `RA_coding_sheet.csv` to exclude Laura's
  round-1 studies from her IRR sample).

## Scoring rules pre-registered for the IRR (see research_log 2026-07-27/28)
Exclude C21 + D11 from Sacha's vs-dataset comparisons; report Part-1 breadth with/without the
4 blank-definition items; break out topical<->curated_sample denominator disagreements
(instrument under-specifies the precedence rule, symmetrically for both coders).
