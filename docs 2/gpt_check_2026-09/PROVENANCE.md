# Independent cross-check — provenance

- **Coder:** OpenAI gpt-5.6-luna (medium), run by Sacha in Codex, 2026-09-03. A different model
  family from the Anthropic Opus-class agents that produced the extractions, which is what makes
  the blind construct kappa a reliability figure rather than a self-consistency figure.
- **Discipline:** one FILE per fresh session (16 sessions). Within a batch the blind file was always
  coded before the verify file, because the verify file shows our own construct codes.
- **Shipped:** `blind_NN.csv` / `verify_NN.csv` at this folder's top level, built by
  `scripts/build_gpt_crosscheck.py` (313 rows / 106 studies, order shuffled, seed 20260903).
  Our own codes were NOT in the shipped folder; they live in
  `data/extract_v2/qa/gpt_check_2026-09_KEY.csv`.
- **Returned, as delivered:** `returned/` — byte-identical copies of the 16 files Sacha sent back,
  archived before scoring so the inputs to the score can be re-checked.
- **Re-runs:** `blind_05.csv` and `verify_01.csv` came back with every row unfilled on the first
  attempt and were re-run in fresh sessions. No other file was re-run, and no returned file was
  edited by us.
- **Scored by:** `scripts/score_gpt_crosscheck.py` -> `data/extract_v2/qa/gpt_check_2026-09_scores.md`
  and `_disputes.csv`. row_key is positional within the package build and must never be re-derived
  from the current `repair_estimates.csv`, which grows as batches land.
- **Result:** fact-check pass 250/313 confirmed (79.9%); blind pass 81.8% agreement, kappa 0.732.
  104 rows queued for adjudication against the papers. No verdict applied automatically.
