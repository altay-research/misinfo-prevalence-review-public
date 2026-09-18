# Data-quality assurance — methods narrative (for the manuscript)

This systematic review used large-language-model assistance for extraction and coding, under continuous human
supervision. To ensure the estimate dataset is accurate and internally consistent, we subjected it to a layered
verification campaign. Each layer targets a different failure mode; every step is versioned (immutable frozen file
+ MD5 + git tag + changelog) and logged (`docs/research_log.md`), and all human adjudications are recorded
(`docs/human_review_provenance.md`, `human_review_ledger.csv` — 206 logged author decisions). The dataset evolved from
v1.4.0 through the audit campaign, the 2026-07-23 review, the September 2026 corpus repair and the September
re-extraction merge to the frozen **v1.7.23 (1,048 estimates / 443 studies)**; see `docs/counts_crosswalk.md` for the
canonical counts and `docs/FROZEN.md` for the full version history.

Sections 1 to 7 describe the layers in the order they were run. Each is dated, because several were run on a corpus
much smaller than the released one and their sample sizes describe that corpus, not this freeze. Section 8 is the
review's blind layer as released.

## 1. Coding rules, ratified iteratively by the author
Extraction was governed by explicit rules the author ratified from repeated source spot-checks (L1–L43;
`docs/learned_review_rules.md`), plus construct rules (`docs/construct_and_concentration_rules.md`): the DENOMINATOR
defines the construct (CONTENT / EXPOSURE / REACH / SHARING / RECALL / CONCENTRATION); definitional-strictness and
denominator variants are KEPT (not collapsed) as the review's central analytic target; scope tags (population_scope,
denom_class, breadth, classification_level) separate general-public prevalence from elite/curated/topical estimates.

## 2. Deterministic audit + adjudicated review (July 2026)
An automated audit (`scripts/audit_dataset_v140.py`) checked schema, vocabulary, value ranges, rule-application
coverage, and duplicates. A 20-agent qualitative pass read each study's source against its coding (80 findings). The
author adjudicated all flagged items against the primary sources, frequently overriding the AI (documented overrides
in `human_review_provenance.md` §C) — evidence the AI output was verified, not accepted.

## 3. Full independent re-read of every study (July 2026, 324-study corpus)
All studies in the then-current freeze (324 at that time) were re-read against source by 21 agents, re-verifying each
value and construct and completing all descriptive fields (a misinformation definition for every study; topic;
political orientation for every party row). Result: **544 confirmations and a single value correction** across ~700
estimates. The author then resolved all 116 residual judgment calls against source. This pass used the same model
family as the original extraction, so it measures reproducibility, not correctness.

## 4. Highest-rigour re-audit, three pillars (July 2026)
- **Convention completeness** (`scripts/reaudit_v143.py`): verified every convention was applied dataset-wide
  (e.g. every REACH sub-typed exposure/sharing/liking; every SHARING sub-typed) — remaining gaps were backfilled.
- **Apply-integrity:** verified the deterministic apply scripts (~250 changes) matched their changelogs and corrupted
  no fields; all study exclusions/merges confirmed. Passed clean at the time. The same check, re-run adversarially on
  2026-09-14, did NOT pass: see §9.
- **Hidden-duplicate detection:** cross-study value/title matching caught duplicate studies entered under different
  identifiers (e.g. two Portuguese/English versions of one paper; a Scopus + supplementary entry of another), which
  were merged (values ported, nothing lost).

## 5. Arithmetic re-derivation (July 2026)
Every value with a reported numerator/denominator (259 estimates at that freeze) was re-derived and compared to the
coded value. No computation errors were found (all auto-flagged mismatches were regex artifacts — years, Likert
scales, concentration group-vs-share — with the coded values matching the papers verbatim).

## 6. Outlier / plausibility scan
Per-construct value distributions were inspected for implausible values. Distributions were as expected (whole-diet
EXPOSURE small; the high CONTENT values are curated single-topic content analyses, correctly tagged
topical). Every extreme value (including a 100% and two 0%s) was verbatim-confirmed against source — two of them
substantive findings (e.g. the most-shared COVID-19 articles contained no misinformation).

## 7. Exclusion re-check against evolved criteria (July 2026)
Because inclusion criteria expanded over the project (source-level exposure, elite/politician estimates, audience
concentration, definitional variants, and small-N topical samples all became includable), we re-screened all
previously-dropped studies (351 drop records) for wrongful exclusions. An agent re-adjudicated 17 borderline drops
against current criteria: **2 re-included** (one, `85138494787`, had a valid topical content-prevalence the original
drop overlooked; the other kept dropped after review), 15 confirmed correctly dropped, and one keyword false-candidate
corrected. One study reconsidered but retained-as-dropped is documented with its rationale (`qa/v145_rejections.csv`).

That check was bounded by the criteria as written, and the criteria themselves were the defect. The September 2026
corpus repair re-screened *every* title- and abstract-stage exclusion under corrected criteria, retrieved 335 full
texts and found 208 of them eligible, of which 131 are held in the released freeze
(`docs/corpus_repair_2026-09/REPAIR_REPORT.md`); §7 above therefore describes a pass that could not have
found what the repair found.

## 8. Blind independent re-extraction — the released blind layer (September 2026)
Two earlier blind passes are superseded and are kept only as provenance: a 54-study high-leverage sample re-extracted
by three agents in July 2026 (79% exact agreement; the residual was multiple valid estimates per study, not coding
error; `qa/blind_reliability.csv`), and a seeded random 10% of the June corpus, 33 of 283 full-text studies, re-extracted
at v1.6.x (`docs/blind_reextraction_results.md`). Both describe corpora far smaller than the released one, and the
second is the row manuscript §4.8 cites for the pre-repair corpus.

The review's blind layer as released is the **full 57-batch re-extraction of the whole corpus**, run 2026-09-07 to
2026-09-09 and scored on **456 of 456 studies** as the corpus then stood
(`data/extract_v2/full_reextract_2026-09/`). One fresh agent per batch of eight studies re-extracted every study
from its archived text with no sight of our coding, our values or our moderators, returning its own screen decision,
rows and moderator codes. It ran on the same model family as the original extractor, so the paper reports it as a
curation check, not as an independent-model reliability tier.

What it found (`full_reextract_2026-09/scores/SUMMARY.md`):

| result | value |
|---|---|
| Eligibility | 430 studies re-confirmed INCLUDE, 26 disputed |
| Value reproduction | 712 of 837 then-frozen main-pool rows matched (85.1%) |
| Omissions the pipeline had missed | 202 candidate rows across 123 studies |
| Moderator disputes on matched pairs | 367 |
| Field agreement (κ on 712 pairs) | classification_level .958 · ground_truth .919 · denom_scope .891 · construct .885 · platform_norm .853 · sampling_frame .819 · topic .792 · breadth .755 · population_scope .588 |

Every dispute, omission candidate and moderator disagreement went to the author on an adjudication page, and the
rulings were merged as freeze operations rather than applied by the model: **36 removals, 30 addition sets, 160
corrections and 29 manual items** (v1.7.18, `merge_plan.py`). Thirty-four rows in the released freeze carry
`source = blind_reextraction_2026-09`, each one an estimate the original pass had missed and the author ruled ADD.

## 9. Human value verification and the 2026-09-14 audit
Two human coders independently verified the same 221 estimates from 89 studies against the source papers (Laura
208/221 confirmed outright, Sacha 202/221; `data/extract_v2/qa/value_verification_keys/`). Their disagreements, 13 from one coder and 10 from the other,
went to source adjudication and produced three row removals and eight documentation groups in v1.7.18.

Four adversarial audit passes then ran before the manuscript re-sync, and three of them found defects this project's
own merge had introduced (v1.7.20, `docs/FROZEN.md` top block): a duplicate study held under two ids by two search
arms; four ruled operations that apply_v1718 imported but never applied, because it read only the additions of the
script it imported; and three rows clobbered by a matcher keyed on a non-unique tuple, one of which destroyed a value
the author had ruled. Each was repaired, and the matcher now refuses a non-unique match on any value-bearing field.

## Summary
The prevalence dataset underlying this review was verified from nine independent angles — rule-based deterministic
audit, adjudicated qualitative review, full source re-read, three-pillar re-audit, arithmetic re-derivation, outlier
scan, exclusion re-check, full-corpus blind re-extraction, and two-coder human value verification. The coding is
convention-complete and fully source-anchored, with a complete human-in-the-loop decision trail.

We do not claim the dataset is error-free. Each layer found errors the layer before it had passed, including in
September, and the most recent audit found three defects in the merge machinery itself. What we can report is the size
and the shape of what the checks found, which is what §8 and §9 do, and that every correction is attributable to the
ruling that authorised it. Declared open items are listed in `docs/FROZEN.md`: 56 empty `denominator` fields, and 19
ledger proposals closed without a ruling because their study left the corpus.
