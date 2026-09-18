# LLM Provenance & Reproducibility Disclosure

Per RAISE (Responsible use of AI in evidence SynthEsis, 2025) and the Cochrane/
Campbell/JBI/CEE joint position statement (2025): any AI step that *makes or
suggests a judgement* must be reported transparently — model, version, settings,
prompt, and date. This file is that record. Reconstructed from `research_log.md`
(append-only, dated per entry), `Old/qa_plan.md (historical roadmap, executed)`, and the pinned scripts.

**Honesty note on precision.** The judgement stages were run as **in-session
Claude subagents** (the Agent tool), not standalone API scripts, because the
author had no standalone API key (research_log entry 17, 2026-06-20). Consequently
the *model family and settings* are documented below, but **exact build strings and
per-call temperatures were not captured at run time** for the subagent stages —
this is a stated reproducibility limitation, not a claim of determinism. The
deterministic parts of the pipeline (search, figures, validation) are fully
reproducible from the scripts.

---

## Model allocation (what actually ran)

Policy (Old/qa_plan.md (historical roadmap, executed) "Models / cost", RESUME_HERE.md): **Sonnet for screening bulk;
Opus for extraction + Step-B verification + adjudication.** Haiku was **rejected**
by the author and **never used** for any judgement (see "Superseded artifact").

| Stage | Task | Model (family) | Temp | Prompt / criteria artifact | Dates |
|---|---|---|---|---|---|
| 1. Title screening — validation + Batch 1 | INCLUDE/MAYBE/EXCLUDE, recall-protective | **Opus-class** (in-session subagents) | default (not pinned) | `docs/screening_criteria.txt` | 2026-06-20 |
| 1. Title screening — bulk Batches 2–N | same | **Sonnet-class** (in-session subagents) | default | `docs/screening_criteria.txt` | 2026-06-20 → 06-21 |
| 2. Abstract screening | INCLUDE/EXCLUDE on fetched abstracts | Sonnet-class → Opus adjudication | default | `docs/screening_criteria_stage2.txt` | 2026-06-21 |
| 2b. Net-new screening (OpenAlex / PubMed) | dual-screen + adjudicate | Sonnet dual-screen → **Opus** adjudication | default | `docs/screening_criteria*.txt` | 2026-06-24 |
| 3. Construct tagging | CONTENT/EXPOSURE/… classification | **Opus-class** | default | `docs/Old/construct_tagging.txt` | 2026-06-21 |
| 4. Estimate extraction (v1) | value/denominator/platform/country/N/def | **Opus-class** | default | `docs/extraction_protocol_v2.md` | 2026-06-21 |
| 4b. Independent re-extraction (v2, "second coder") | full re-extraction of all candidates | **Opus-class**, separate pass | default | `docs/extraction_protocol_v2.md` | 2026-06-22 → 06-23 |
| 5. Step-B value verification | verbatim-quote-or-drop anchoring | **Opus-class** | default | `docs/value_verification_protocol.md` | 2026-06-22+ |
| 6. Dual-reader verification + κ | reader A vs reader B + adjudication | Opus/Sonnet-class passes | default | `docs/screening_criteria.txt` | 2026-06-21 |
| 7. Risk-of-bias appraisal | 5-dimension low/mod/high | **Opus-class** | default | `docs/Old/rob_checklist.txt` | 2026-06-21 |
| 8. Blind 10% re-extraction (error rate) | fresh agents, no access to frozen coding | **Opus-class** | default | `docs/extraction_protocol_v2.md` | 2026-06-2x |

**"In-session subagents" = the Agent tool inside a Claude Code session** running on
the then-current session model (Claude Opus / Sonnet family, June 2026). Where a row
says "Opus-class," the substantive extraction/adjudication/verification work was done
by the highest-tier model available in-session at that date.

**Model asymmetry across streams (disclose in the manuscript).** Screening tiers
were not uniform across identification streams: Scopus titles were screened by
Opus-class agents on the early validation batch then Sonnet-class on the bulk
batches; the PubMed and OpenAlex net-new streams were Sonnet-class dual-screen with
Opus-class adjudication. All streams used the *same* committed criteria files
(`screening_criteria*.txt`), so the decision rule was constant; only the model tier
differed. This asymmetry is a minor reproducibility caveat, not a criteria difference.

## Reliability figures and what they compare (critical for honest reporting)

All κ below are **inter-LLM** (one model pass vs another), NOT human-vs-human or
human-vs-LLM, unless stated. The single human validation (independent RA vs the
frozen LLM coding) is **COMPLETE** (2026-08 addendum below) — see `FROZEN.md` / RA_package.

| Metric | Value | Compares |
|---|---|---|
| Title-screen κ | 0.89 (0.89–0.91) | LLM pass A vs LLM pass B |
| Construct κ | 0.78 (raw 84%) | LLM vs strict-LLM re-pass |
| Re-extraction κ | 0.82 | LLM vs LLM second extraction |
| RoB reliability (overall) | raw 85%, within-1-level 100%, Cohen κ 0.48, **PABAK 0.78, Gwet AC1 0.83** | LLM vs LLM, 89-study blind subsample; Cohen κ deflated by HIGH-heavy skew (73/13/3) — AC1/PABAK are the honest figures. `scripts/rob_reliability.py` |
| Blind 10% reproduction | 90% finding / 94% construct | fresh LLM vs frozen LLM coding |
| Author spot-check | 6 rounds → 49 rules | **human (author), ad hoc, not blinded** |
| RA gold standard | **done** (2026-08 addendum) | **human (independent) vs LLM — since run (2026-08 addendum below)** |

## Settings & keys
- Only the (unused) title-screen script pins settings: `claude-haiku-4-5-20251001`,
  `temperature=0`, `max_tokens=100` (`scripts/screen_titles.py`). This script was
  **never run** (see below).
- In-session subagent stages used harness-default sampling. No API keys are stored
  in the repo; `SCOPUS_KEY` / `ANTHROPIC_API_KEY` are read from env only.

## Superseded artifact
`scripts/screen_titles.py` pins Haiku and temperature 0 for a standalone-API title
screen. It was written but **never executed**: the author rejected Haiku and had no
standalone key, so screening pivoted to in-session Sonnet/Opus subagents
(research_log entry 17, 2026-06-20). The script is retained only as a documented,
reproducible *alternative*; it is **not** the method used. Do not cite Haiku as a
screening model.

## Known limitations (report these)
1. Subagent model **build strings and per-call temperatures not captured** — the
   judgement stages are reproducible in *method* (criteria files committed) but not
   bit-for-bit in *output*.
2. All headline κ are **inter-LLM**; human validation (RA) is COMPLETE (see the 2026-08 addendum below).
3. Full text truncated to ~12k chars for extraction (decision I2) — a known accuracy
   ceiling. The no-truncation sensitivity check was run on 2026-07-02 over 21 EXPOSURE and
   CONCENTRATION studies (`data/extract_v2/sensitivity_notrunc/`): truncation caused omission,
   not corruption, no frozen value moved, and the 15 rows it had missed were added at v1.2.
   The September 2026 blind re-extraction then re-read every study from its full archived text.


## Addendum 2026-08-11 — reliability tiers completed since the June rows above

The June table above records the SAME-MODEL tier only. Since then, both stronger tiers completed
(full detail: manuscript §4.8; docs/codex_check/MODEL_AND_PROVENANCE.md; RA_package/README.md):

- **Independent model family (GPT-5.6 Terra):** historical whole-corpus sweep (construct κ .75) that
  drove the denominator recoding campaign; then a nine-batch fresh-session sweep of all 647 codeable
  estimates on the current freeze — construct κ .802 (raw .858), denominator scope κ .72,
  breadth .48 (interpreted in §4.8 as a property of the literature's definitions).
- **Human IRR (Sacha + Laura):** two batches, 35 full-paper items — denominator κ .84 (91% raw),
  construct .60, sentence-level ceiling .48; the exercise exposed one fabricated study and triggered
  the corpus integrity re-screen.
- **Same-family QA (2026-08-11, Fable):** all 170 rows of the 40 load-bearing studies re-read
  against source — zero value errors, 92 metadata fixes (v1.7.9). Curation evidence only; same-family
  passes are NEVER reported as a reliability tier.
