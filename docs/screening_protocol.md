> **ORIGINAL PROTOCOL AS DRAFTED (June 2026) — retained unedited as the protocol of record.**
> The review was executed with documented deviations: the executed gold set was 40 titles (not 31); the budget-confirmation script was never run — screening ran via in-session subagents (see llm_provenance.md). The as-executed methods are
> `docs/METHODS_PROVENANCE.md` + manuscript §4; every deviation is logged with rationale in
> `docs/research_log.md` / `docs/DECISIONS_REGISTER.md`. (Banner added 2026-08-11.)

# Screening protocol — DRAFT v0.1 (2026-06-20)

Reduces the 20,344-record `strict_v2` corpus to the included set, transparently and
reproducibly, WITHOUT silent capping. Two stages (title → full text); LLM-assisted
classification with human verification. Every record keeps a label + reason + stage.

## Why LLM-assisted (and how recall is protected)
A solo reviewer cannot hand-screen 20k titles, and tightening the query sacrifices
recall (see research_log §11). So: an LLM applies the §4 eligibility criteria to each
title, returning INCLUDE / MAYBE / EXCLUDE + reason. **Recall protections:**
- The prompt is tuned to be **inclusive** — when in doubt → MAYBE, never EXCLUDE.
- **All INCLUDE + all MAYBE** go to the next stage (human-read at full text).
- A **human audits a random sample of EXCLUDEs** (target ≥300, ~1.5%) every run; if any
  true-eligible is found in the EXCLUDE pile, the prompt is revised and the stage re-run.
- The screener is validated against a **hand-labelled gold set**
  (`data/screening_goldset.csv`, 31 titles) before any production run; report
  agreement (esp. that no gold INCLUDE/MAYBE is sent to EXCLUDE).

## Stage 1 — title screen (this corpus has titles only)
Input: `data/corpus_strict_v2_2026-06-20.jsonl`. Output: `data/screen_title_<date>.csv`
(eid, title, label, reason). Decision rules given to the model (from protocol §4):
- INCLUDE/MAYBE if the title plausibly reports a **quantitative estimate** of audience
  exposure / consumption / observed sharing / concentration / actor-level prevalence of
  misinformation (broad), incl. **content-prevalence** studies (kept in a separate
  bucket).
- EXCLUDE only if clearly: CS detection/classification; intervention/correction-only;
  belief/susceptibility-only; hypothetical/stated **sharing intentions**; non-empirical
  (commentary/theory/book/editorial/proceedings volume/dataset-resource); or off-topic.
- Default to MAYBE under uncertainty.

## Stage 2 — full-text screen
Fetch abstracts/PDFs for Stage-1 survivors (Scopus Abstract Retrieval / open access /
library), then human + LLM full-text screen against §4, with dual-pass on a sample.
Record final include/exclude + reason → PRISMA flow counts.

## Outputs & audit trail
- `data/screen_title_<date>.csv` — every record labelled (no record dropped silently).
- `searches/screen_title_audit_<date>.md` — gold-set agreement + the EXCLUDE-sample audit.
- PRISMA numbers (identified / screened / excluded-with-reasons / included) assembled
  at the end.

## Cost / key note
`scripts/screen_titles.py` calls the Claude API (model pinned, temperature 0 for
reproducibility) and reads `ANTHROPIC_API_KEY` from the environment (never stored).
~20k short title classifications on a small/fast model is cheap; confirm model + budget
with Sacha before the full run.
