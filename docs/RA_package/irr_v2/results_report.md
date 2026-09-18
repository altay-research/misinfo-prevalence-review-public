# Human IRR results (v3 design) — scored 2026-07-29

Coders: Sacha (author) + Laura (RA, naive: her round-1 studies excluded from the draw).
Blind to the dataset and each other. Scored by `scripts/score_human_irr.py` on FROZEN v1.5.7 key.
Pre-registered exclusions applied (research_log 2026-07-27/28): C21 out of Sacha-vs-dataset
(flag leak), D11 void (Sacha blank-by-refusal + prior value disclosure), breadth reported
with/without the 4 blank-definition items, topical/curated breakout.

## The load-bearing numbers — coder vs coder (human ceiling)

| dimension | evidence | n | raw | kappa |
|---|---|---:|---:|---:|
| construct (Part 1) | snippet | 24 | .583 | **.477** |
| breadth (Part 1) | snippet | 24 | .667 | .558 |
| breadth excl 4 blank-def | snippet | 20 | .750 | .655 |
| construct (Part 2) | full paper | 11 | .818 | **.738** |
| denominator class (Part 2) | full paper | 11 | **1.000** | **1.000** |
| value extraction (Part 2) | full paper | 11 | .909 | — |

**The evidence gradient is the finding.** From snippets, two trained humans agree only
moderately (construct κ .48); given the full paper, they converge (construct κ .74, denominator
κ 1.00, value 91%). The denominator — the field's modal defect and our pipeline's dominant error
pattern — is essentially PERFECTLY codeable by humans when they read the paper. The feared
topical↔curated confusion (pre-registered 2026-07-28) did not occur even once.

## Coder vs dataset

| dimension | sacha | laura |
|---|---|---|
| construct (Part 1) | κ .646 (excl C21: .629, n=23) | κ .602 |
| breadth | κ .556 (excl blank-def: .647) | κ .718 (excl blank-def: .728) |
| denominator (Part 2) | 1.000 (11/11) | .857 (11/12; one news_diet↔all_media) |
| construct (Part 2) | κ .750 | κ .786 |
| value exact | 9/11 (+1 valid sibling) | 9/12 (+1 sibling) |

Value misses, all explained: **D12 both coders 18.1 vs key 31.7 — an instrument artifact, not an
error on either side** (the pointer demanded "the single overall figure"; the paper's overall is
18.1% while the dataset row is the TikTok-specific 31.7% by design — unit = study×platform;
verified against the fulltext 2026-07-29). Laura's D06 = NOT FOUND after the 5-minute rule (a
retrievability datum; Sacha found it). Excluding the D12 artifact, extraction agreement is
Sacha 10/10, Laura 10/11.

## Anatomy of the ceiling disagreements (Part 1 construct, 10 items)

They cluster exactly where the taxonomy says the hard boundaries are: QUALITY↔CONTENT (the
falsity/quality rule: C01, C03, C10) and within the exposure family REACH↔EXPOSURE↔RECALL
(C14, C17, C19, C20). In 9 of 10 disagreements the dataset's code coincides with ONE of the two
coders (the sole exception is C10) — the dataset sits inside the human disagreement space, not
outside it.

## Reading against the machine tiers (for §4.8)

The three-tier ladder now closes: same-model consistency κ .78–.89 (reproducibility only);
independent model vs dataset, whole corpus, construct κ .75; and now the human ceiling —
**κ .48 on snippet evidence, κ .74–1.00 on full-paper evidence**. Two implications. (1) The
machine figures clear the bar the human ceiling sets: an independent model family agrees with
the dataset (κ .75) at least as well as two trained humans agree with each other on comparable
evidence. (2) The construct classification is genuinely ambiguous from isolated sentences —
which is the paper's argument about the literature's reporting practices, arriving this time
through the reliability study.

## Adjudication of the four both-against-dataset items (2026-07-29, final)

Sacha re-coded all four from the full text via `qa/irr_adjudication.html`, with the decisive
evidence displayed. His final codes — C05: false · C07: SHARING · C10: QUALITY · D09: QUALITY —
match the dataset on ALL FOUR. No dataset change (no v1.5.8). Every both-against-key signal
traced to evidence the snippet or abstract had hidden: a second instrument in the same paper
(C05), the word "concentration" used loosely (C07), and two quality rubrics that sound like
falsity verdicts until the methods define them (C10: unknown-effectiveness ≠ false; D09:
"misleading" = covers <4/6 ASRS questions, a coverage criterion).

## D11 postscript (2026-07-29)

Sacha refused D11's premise (pre-registered: no single overall figure exists); Laura, coding
independently, picked the OTHER equally-overall sibling (9.9 algorithmic vs key 6.9
chronological) — confirming the critique; scored ALT, no penalty. Her denominator (news_diet vs
all_media) is a single-coder disagreement, below the adjudication bar. Her note ("exposure was
mimicked through bots so not actual people") blindly reproduces the RoB appraisal's core finding
for that study (agent-based audit, items 1–3+5 HIGH) — an independent validation of the
appraisal layer.

## BATCH 2 scored (2026-07-30) — pooled Part 2 n=23–24

Both coders found batch 2 markedly harder, and said so before seeing any scores (Laura: "much
harder than round 1... some papers did not fit any construct, or the methodology was described in
such an intransparent way that it was not possible to get all the info"; Sacha concurred).
The confidence data agree: Laura 4.11→2.92, Sacha ~3.9→3.67; NOT FOUND 1→3.

**Pooled Part 2 (batches 1+2):** ceiling construct κ .596 (raw .739) · ceiling denominator κ .841
(raw .913) · ceiling value agreement .652. Batch-2-only ceiling: construct κ .43, denominator
κ .71. Vs dataset: Sacha denominator κ .768 / construct κ .784 / value 20 exact + 1 alt + 2 miss;
Laura .639 / .697 / 14 exact + 2 alt + 8 miss.

**Reading:** batch 1 (transparent designs) produced near-perfect full-paper agreement; batch 2 was
DRAWN to stress content analyses, and there the ceiling is capped not by coder skill but by the
papers' own reporting (both coders' notes independently attribute the difficulty to opaque
methods and absent overall figures). The evidence gradient becomes two-stage: snippets κ .48 →
transparent papers ≈ perfect → opaque papers κ .43–.71. The human ceiling inherits the
literature's reporting quality — which is the review's thesis, measured a third way.

**Topical/curated finally bit (E01):** Sacha curated_sample (= dataset), Laura topical — the
first confusion on that boundary across 23 denominator items, and the dataset's side of it held.

**Adjudication queue (round 2):** E02 (both coders curated_sample vs key population — talk-shows
panel), E03 (both topical vs key curated_sample — the batch's mirror-image boundary case), and
E12 (Sacha: "I read everything and did not find a single usable estimate" vs key 54 RECALL — a
dataset-row soundness question, the first of the whole IRR). Everything else is single-coder
noise or documented multi-figure artifacts (E06 Laura computed 8.3 from a different table
denominator; E09 36.1 vs 37.2 near-miss).
