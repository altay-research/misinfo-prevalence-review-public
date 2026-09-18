# Human-in-the-loop review provenance

**Purpose.** This document is the auditable record of the human review and adjudication work across the
project: the **author's own** (SY) in §A, and the second human coder's in §B1. In this AI-assisted systematic review, coding and verification were produced
with LLM assistance, but **every consequential coding decision was reviewed by the author against the
primary source (the full-text PDF), and the author frequently overrode or modified the AI**. This record
documents that human-in-the-loop verification for the Methods/transparency statement and for peer review.
It distinguishes, honestly, **human adjudication (author SY)** from **LLM second-reader verification**
(machine passes that assist but do not substitute for human judgment).

Every artifact cited below is in the repository and versioned in git. Counts are the *actual* rows the
author filled, not the sheet size.

---

## A. Author (human) adjudication episodes — chronological

| # | Date | What the author reviewed | Scope (author-filled) | Artifact | Output |
|---|---|---|---|---|---|
| A1 | 2026-06-20 | Title/abstract **screening** gold set — hand-labelled include/exclude to validate the screening classifier | 40 studies hand-labelled | `data/screening_goldset.csv`, `data/screen_shards/validation.csv` (human_label vs model_label + agree) | screening calibration |
| A2 | 2026-06-22 | **Value review, round 1** — read the source for the first estimates and gave keep/drop/discuss + reasoning | 9 values (`your_call`+`your_note`) | `data/extract_v2/qa/sacha_review_round1.csv` | rules **L1–L7** (`docs/learned_review_rules.md`) |
| A3 | 2026-06-25 → 26 | **Value spot-checks, rounds 2–6** — canonical-paper spot-checks reading each PDF; derived error patterns | 36 documented rulings | `docs/learned_review_rules.md` (L8–L43, each tagged "Sacha spot-check") | rules **L8–L43** |
| A4 | (v1.2 build) | **Estimate validation sheet** — AI-inferred keep/drop calls + rules presented for the author's validation; author annotated/overrode | 22 explicit annotations/overrides (of 427 AI-inferred calls reviewed) | `data/extract_v2/qa/sacha_review_round2.csv` (`final_call`, `your_note`) | v1.2 recodes |
| A5 | 2026-07-14 | **RA-contested 29 papers** — independent adjudication reading each full text (the author, not the RA) | 28/29 decisions + 18 notes | `docs/RA_package/round1_2026-07/ra29_verification_SACHA.csv` | **7 coding rules R1–R7** ratified; `docs/RA_package/round1_2026-07/adjudication_29_resolved.csv` |
| A6 | (v1.2) | **v1.2 review decisions** — keep/drop on specific contested items | 20/24 | `data/extract_v2/qa/v12_review_decisions.csv` | v1.2 freeze |
| A7 | 2026-07-15/16 | **Demographic review** — per-row keep/drop + notes on every demographic breakdown, reading sources; set 4 conventions | 85 rows adjudicated (18 drop) | returned `demo_review (2).csv` → `data/extract_v2/qa/review_v140_changelog.csv` | RULE DEMO + v1.4.0 |
| A8 | 2026-07-16 | **Geographic review** — country/region breakdown keep/drop | 9/9 | `data/extract_v2/qa/geo_review_decisions.csv` | geographic coding |
| A9 | 2026-07-17 → 2026-07-23 (closed) | **v1.4.0 data-quality audit** — adjudicating deterministic rule-conflicts + 80 qualitative findings, reading the PDF for each (Open-PDF in the sheet) | 206 items ruled (AGREE 72, DECISION 67, COMMENT 32, NOTE_ONLY 27, OVERRIDE 3, UNSURE 5) | `data/extract_v2/qa/audit_v140_decisions_round1.csv` → `human_review_ledger.csv` | v1.4.1 and the freezes that followed |
| A10 | 2026-07-27 → 29 | **Human IRR v2** — the author and the RA independently coded the same blinded sample (24 snippet items, 24 full-paper items in two batches), blind to the dataset and to each other | 48 items coded by the author | `docs/RA_package/irr_v2/` (`part1_sacha.csv`, `part2_sacha.csv`, `part2b_sacha.csv`), scored by `scripts/score_human_irr.py` | the human-ceiling row of manuscript Table 2; `irr_v2/results_report.md` |
| A11 | 2026-07-30 → 2026-08 | **IRR round-2 adjudication** — re-reading the full text on every item the two coders jointly flagged | 3 flagged items re-adjudicated; 4 coders-agree-against-dataset items re-read | `docs/RA_package/irr_v2/disagreements.csv` | 2 denominator recodes; 1 fraudulent paper removed |
| A12 | 2026-08-24 → 2026-09 | **Human validation round 3** — four blind tasks coded by the author alongside the RA: title screening (200 titles), abstract screening (60 records), full-text eligibility (50 studies), grey-literature claims (30) | 340 blind items, plus the author-only adjudication of every coder-vs-pipeline disagreement | `docs/RA_package/round3_2026-08/` (`*_sacha_FILLED.csv` + the three `*_adjudication_sacha_FILLED.csv`) | the screening-validation rows of manuscript Table 2; the abstract-stage misses that triggered the corpus repair |
| A13 | 2026-09-02 | **Abstract re-screen triage** — ruling ELIGIBLE / UNSURE / NOT ELIGIBLE on the double-flagged abstract-stage exclusions, from title + abstract + both screeners' reasons | 25 rulings (14 ELIGIBLE, 8 UNSURE, 3 not eligible) | `data/extract_v2/qa/abstract_rescreen/rescreen_triage_sacha_FILLED.csv`; page `docs/RA_package/abstract_rescreen_2026-09/triage_sacha.html` | **the finding that the screening criteria never named self-reported RECALL**, and the corrected criteria (`abstract_rescreen/adjudication/CRITERIA.md`) the whole corpus repair then ran under |
| A14 | 2026-09 | **Corpus-repair rulings** — the contested cases from the re-screen of every title- and abstract-stage exclusion | author rulings on the repair's disputed records | `docs/corpus_repair_2026-09/repair_rulings.html` → `scripts/apply_repair_rulings.py` | the repaired corpus (§4.4) |
| A15 | 2026-09 | **Independent-model cross-check disputes** — every row where the second model family disagreed with our coding, adjudicated against the paper | 23 disputes in wave 2, plus the wave-1 and wave-3 queues | `docs/gpt_check_2026-09*/` + `rulings/disputes_wave2_sacha_FILLED.csv` | v1.7.16 |
| A16 | 2026-09-08 → 09-10 | **Full blind re-extraction adjudication** — every screen dispute, omission candidate and moderator disagreement raised by the 57-batch blind pass, ruled item by item on a desktop adjudication page | **592 items ruled** (201 omission candidates, 365 moderator disputes, 26 screen disputes; OURS 181, THEIRS 172, NOT_CODEABLE 156, ADD_ROW 40, EXCLUDE_STUDY 26, THIRD 12) | `data/extract_v2/full_reextract_2026-09/rulings_sacha_2026-09-08a–c.csv`, `rulings_sacha_2026-09-10a.csv` | v1.7.18: 36 removals, 30 addition sets, 160 corrections, 29 manual items |
| A17 | 2026-09-12 → 09-14 | **Value verification against source** — the author personally re-verified a 221-estimate / 89-study sample against the papers, as one of the two coders (see §B2) | 212 of 221 answered; 202 confirmed outright, 10 disagreements raised | `data/extract_v2/qa/value_verification_keys/sacha_scored.csv`, `sacha_notes.csv` (58 study-level remarks) | three row removals and eight documentation groups in v1.7.18 |
| A18 | 2026-09-14 | **Pre-merge rulings and the ledger close-out** — sections A to L of the pre-merge brief, then the 11 outstanding value-verification ledger proposals | 73 pre-merge rulings + 11 ledger rulings | `full_reextract_2026-09/premerge_rulings_sacha_2026-09-14a/b.csv`; `value_verification_keys/ledger_rulings_sacha_2026-09-14.csv`; brief at `docs/PREMERGE_BRIEF_2026-09-09.md` | v1.7.18 → v1.7.20 |

**These are the AUTHOR's decisions.** In several the author actively **disagreed with the AI** (see §C) —
evidence this was genuine verification, not rubber-stamping.

Episodes A1–A9 ran on a corpus of roughly 320 studies; A10–A18 ran during and after the September
corpus repair, on the corpus the review releases. The later tranche is the larger one: A16 alone is
592 individually reasoned rulings, against 206 in A9.

---

## B1. The second human coder (research assistant)

The author is not the only human in the loop, and the RA's work is recorded here because it is human
oversight of the same kind, coded blind to the pipeline and to the author.

| # | Date | What the RA coded | Scope | Artifact | Output |
|---|---|---|---|---|---|
| R1 | 2026-07 | **Inclusion decisions, round 1** — keep/drop on a blinded sample, then the 29 contested cases the author re-adjudicated in A5 | κ = 0.33 on inclusion; construct agreement 42 of 51 | `docs/RA_package/round1_2026-07/` | rules R1–R7 |
| R2 | 2026-07-29 | **Human IRR v2** — the same 48 blinded items the author coded in A10, independently and blind to him | 48 items | `docs/RA_package/irr_v2/part1_laura.csv`, `part2_laura.csv`, `part2b_laura.csv` | the coder-versus-coder ceiling: denominator κ = 0.84, construct κ = 0.60 from full papers, κ = 0.48 from sentences |
| R3 | 2026-08-24 → 09 | **Human validation round 3** — the same four blind tasks as A12 (200 titles, 60 abstracts, 50 full texts, 30 grey claims) | 340 blind items | `docs/RA_package/round3_2026-08/*_laura_FILLED.csv` | the two abstract-stage misses both coders agreed on, which triggered the corpus repair |
| R4 | 2026-09 | **Value verification against source** — the same 221-estimate / 89-study sample as A17, independently | **208 of 221 confirmed outright (94.1%)**, 13 disagreements, 51 study-level notes | `data/extract_v2/qa/value_verification_keys/laura_scored.csv`, `laura_notes.csv`, `laura_SUMMARY.md` | adjudicated against source with the author's own verdicts; feeds v1.7.18 |

The value-verification round (R4 with A17) is the largest single tranche of human checking in the
project: **two coders, 221 estimates each, read against the source papers**, with a side-by-side
comparison at `value_verification_keys/laura_vs_sacha_2026-09-13.md` and the adjudication at
`ledger_adjudication_report.md`. Their agreement pattern is itself a result — both confirm about
95% of rows outright, and their disagreements concentrate in REACH, the construct whose boundary
with SHARING the instrument under-specifies.

---

## B2. LLM second-reader verification (machine — assists, does NOT replace human review)
Recorded separately for honesty; these are **not** human adjudications:
- `data/verify/*.csv` (17 shards, `eid,verdict,reason`) — LLM keep/drop second-reader over the corpus.
- `data/exverify/*.csv` (9 shards, `eid,verdict,corrected_estimate,reason`) — LLM value-verification.
- `data/extract_v2/qa/sel_*.csv`, `fn_*.csv`, `triage_*.csv` — LLM extraction/selection/triage passes.
- The 20-agent qualitative audit (`qa/qual_raw/`) — LLM source-vs-coding pass that **surfaced** the 80
  findings the author then adjudicates in A9.
Design principle: the LLM proposes and flags; **the author disposes**, against the source.

---

## C. Evidence this is genuine verification, not rubber-stamping
The author overrode or materially modified the AI on numerous occasions, e.g.:
- **RA adjudication (A5):** of the 29 contested papers, independent full-text reading found the LLM's keep
  correct on 18 but confirmed **11 real over-includes** — the author corrected the dataset, and *also*
  reversed several of the RA's over-exclusions. Net: human judgment moved in both directions.
- **v1.4.0 audit (A9):** the author **overrode the AI's "drop"** on González-Bailón (kept the 76%) and on
  the 4-country legislator party-shares (kept as concentration) — against the reading agent's recommendation.
- **v1.4.0 audit (A9):** the author independently caught that a value the AI reported (17.55%, Guo/2006.04278)
  **was not in the paper**, before the re-read agent confirmed it — i.e. the human found an AI error.
- **v1.4.0 audit (A9):** the author refined the AI's binary "SHARING vs REACH" into a new, more accurate
  **"REACH, subtype = sharing"** category the AI had not proposed.
- **Value spot-checks (A2–A3):** 43 documented error patterns (L1–L43) were derived *from* the author
  reading sources and correcting the AI (complements, cited numbers, coefficients, circular denominators).

---

## D. Running quantitative summary

`data/extract_v2/qa/human_review_summary.md` + `human_review_ledger.csv` hold the v1.4.0 audit (A9)
per item: AI recommendation vs the author's decision, adjudication (AGREE / OVERRIDE / MODIFY), and the
author's verbatim reasoning, with source_consulted = "PDF (reviewed in-sheet)". That ledger closed at
206 items; `scripts/ingest_human_decisions.py --round N --date YYYY-MM-DD <decisions.csv>` is the
script that filled it.

The later rounds do not use that ledger. Each one keeps its own ruling file, because each is keyed to
a different artifact (a screening record, a re-extraction dispute, an estimate row), and the freeze
script that applies it names the ruling key for every operation it performs. The complete set:

| round | ruling file | items |
|---|---|---:|
| IRR v2 + round-2 adjudication (A10–A11) | `docs/RA_package/irr_v2/part*_sacha.csv`, `disagreements.csv` | 48 + 7 |
| Validation round 3 (A12) | `docs/RA_package/round3_2026-08/*_sacha_FILLED.csv` | 340 + adjudications |
| Abstract re-screen triage (A13) | `qa/abstract_rescreen/rescreen_triage_sacha_FILLED.csv` | 25 |
| Cross-check disputes (A15) | `docs/gpt_check_2026-09_wave2/rulings/disputes_wave2_sacha_FILLED.csv` | 23 |
| Blind re-extraction (A16) | `full_reextract_2026-09/rulings_sacha_2026-09-10a.csv` (latest wins) | 592 |
| Value verification (A17, R4) | `value_verification_keys/{sacha,laura}_scored.csv` | 221 each |
| Pre-merge + ledger close-out (A18) | `premerge_rulings_sacha_2026-09-14a/b.csv`, `ledger_rulings_sacha_2026-09-14.csv` | 73 + 11 |

## E. Draft transparency statement (for the manuscript Methods)
> Coding and verification were performed with large-language-model assistance under human supervision.
> All included estimates and every flagged coding decision were reviewed by the author (SY) against the
> full-text primary source. Across the review the author conducted [A1–A18] structured adjudication passes
> (screening calibration, value spot-checks yielding 43 documented coding rules, independent re-adjudication
> of RA-contested papers, demographic/geographic reviews, a full data-quality audit, four blind human
> validation tasks coded alongside a research assistant, the adjudication of 592 disputes raised by a
> blind re-extraction of the whole corpus, and a two-coder verification of 221 estimates against their
> source papers). The author
> frequently overrode or corrected AI-proposed codings — including reversing AI drop recommendations,
> identifying an AI-fabricated value absent from the source, and introducing coding categories the AI had
> not proposed — demonstrating that AI outputs were verified rather than accepted. LLM second-reader passes
> (`data/verify`, `data/exverify`, the qualitative audit agents) were used to *surface* candidate errors for
> human adjudication and did not by themselves determine any coding decision. All decisions, reasoning, and
> the AI-vs-human adjudication are logged (`docs/human_review_provenance.md`, `human_review_ledger.csv`).

- **Grey-literature track (2026-06-20, noted 2026-08-26):** the author participated directly in coding the Science Feedback (SIMODS) claims during the grey-lit sessions; a formal blind re-code of a 30-claim stratified sample (round 3, Task D) was added 2026-08-26.
