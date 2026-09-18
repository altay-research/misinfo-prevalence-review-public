# Target-estimate selection rule — for Sacha's validation

**Problem.** Most included papers report MANY numbers, several potentially relevant. We must
pick the value that best represents each construct, apply the rule consistently, and document
per value WHICH alternatives existed and WHY we chose the one we did. This file defines the
rule; the per-value documentation (chosen vs alternatives + reason) is produced by the
verification run and stored alongside each value. **Status: RATIFIED by Sacha 2026-06-22** (see the resolved-decisions block at the end).

## What is NOT a selection choice (these are separate estimates, not alternatives)
We extract at the level of **study × country × platform/source × construct × measure_type**.
Different countries, platforms, constructs, or measures are **distinct estimates**, each kept
(e.g. your JQD = FR/US/UK/DE × {Facebook, Web} = 8 estimates). The selection rule applies
only to choosing ONE value *within* a single such cell when the paper offers several.

## Selection hierarchy (apply in order, within a cell)
1. **Denominator representativeness (primary).** Choose the value whose denominator is the
   broadest and least curated — the one closest to "of everything in scope," not "of a
   hand-picked / flagged / worst-case subset."
   *e.g. "% of all sampled posts" ✓ over "% of posts already flagged as suspect" ✗.*
2. **Authors' headline figure.** Among denominator-valid candidates, prefer the figure the
   authors present as the main result for that construct (abstract/results headline) over
   secondary, robustness, or appendix numbers.
3. **Measurement quality.** Behavioural/observed over self-report (for exposure); a
   validated misinformation definition (fact-check verdict, established unreliable-source
   list) over ad hoc author coding.
4. **Completeness / time.** Full study period or all waves pooled over a single peak, event
   window, or single wave — *unless the paper's unit of analysis IS that event*. Prefer the
   largest complete N.
5. **Aggregation level.** Overall/pooled within the cell over a single sub-bucket. If only
   sub-buckets are reported, compute/record the overall if derivable; otherwise take the
   central (median) sub-bucket and document it.
6. **Conservatism tie-break.** If two candidates remain equally valid, prefer the central /
   overall value, NOT the maximum or the cherry-picked extreme.

## Never select
- A number that is a **secondary citation** of another study (e.g. a paper quoting Allen's
  0.15%) — that belongs to the cited study, not this one.
- A **cherry-picked peak** or **worst-case subgroup** presented for emphasis.
- A **quality/usefulness score** in place of a falsity measure (per the CONTENT/QUALITY rule).
- Any value **not anchored to a verbatim source quote** (per the 100%-confidence protocol).

## What gets documented per selected value (for your audit)
The June draft of this file proposed three dedicated columns (`chosen_value`, `alternatives_seen`,
`selection_reason`). The schema that shipped carries the same information in the columns the
codebook documents, and those three names are **not** in the frozen CSV:

- the value and its evidence: `value_pct`, `value_raw`, `source_quote` (verbatim, mandatory on
  every row) and `denominator` (what it is a share of);
- the alternatives that were not taken: kept as their own rows wherever they are co-equal
  estimates, and marked `definition_variant` when they are a stricter or broader definition of
  the same quantity. A paper's several figures for one cell are usually all held, not discarded;
- the reason for the pick: `flag` and `moderator_quote`, plus the freeze changelog entry for any
  value that was later re-ruled.

Every pick stays reviewable: the quote shows what was taken, the sibling rows show what was
considered, and the changelogs show what moved and on whose ruling.

## Resolved decisions (Sacha, 2026-06-22)
- **Q1 → KEEP BOTH.** Behavioural and self-report for the same exposure cell are kept as
  separate `measure_type` rows (don't lose data). ✅
- **Q2 → (c), RATIFIED and enforced as R8.** When only sub-buckets exist and no overall is
  reported: keep each sub-bucket as its own quote-anchored row (tagged by sub-topic).
  **Never compute our own overall** — a calculated number has no verbatim source quote and would
  violate the 100%-confidence rule. R8 has since removed rows from the freeze on exactly this
  ground, most recently Allcott & Gentzkow's EXPOSURE 5 at v1.7.18, whose denominator had been
  built by summing two site lists. ✅
- **Q3 → POOL.** Multi-wave panels: use the pooled-across-waves figure; if not reported
  pooled, the most recent complete wave. ✅
- **Q4 → UP TO ~10 RELEVANT.** `alternatives_seen` is not capped at 3 — record all
  alternatives that appear *somewhat relevant* (up to ~5–10), but omit trivia/irrelevant
  numbers. Judgment on relevance, not exhaustiveness. ✅
