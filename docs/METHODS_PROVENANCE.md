# Methods & Provenance — Misinformation Prevalence & Concentration Review
*Living document, hand-maintained. Git history is the authoritative step-by-step audit trail (`git log`);
`docs/FROZEN.md` and `docs/counts_crosswalk.md` are the authoritative pointers for every count.*

## 1. Objective & thesis
Systematic review of the PREVALENCE and CONCENTRATION of audience-level misinformation exposure. Core thesis: the field conflates distinct quantities under "prevalence" — CONTENT (% of items false), EXPOSURE (% of a person's diet), REACH (% of people who encounter ≥1), SHARING, CONCENTRATION (share by top users), RECALL (self-report) — and the alarming numbers measure content composition, not population exposure; the denominator drives everything.

## 2. Search & corpus (PRISMA identification)
Databases: Scopus (primary, strict_v2 query, frozen snapshot 2026-06-20, 20,344 records) + PubMed (E-utilities) + OpenAlex (keyword + snowball + abstracts) + author's library (~3,800 PDFs) + grey-literature track (separate). WoS not searched (documented boundary; ~80-90% Scopus overlap).
Two September 2026 top-ups follow the June searches and are NOT inside the 25,907 records the PRISMA
flow identifies: an OpenAlex behavioural/preprint-venue query (2026-09-07, 5,382 net-new records
screened in 45 batches, 20 studies held) and a hand-run Google Scholar recall check (2026-09-04,
5 studies held). Both are drawn on the flow figure as their own identification boxes; how they should
be folded into the identified totals is an open author decision, stated in `docs/doc_audit_2026-09-14.md`.

## 3. Screening
SINGLE-screener LLM title screening under a recall-protective rule (not dual independent screening — a resource decision, recorded explicitly), bounded by: a 40-title gold set (97.5% agreement, all 9 known positives recovered), a blind re-screen of 300 exclusions (0 missed includes), and a 90-record dual-pass subsample (kappa 0.89). That kappa compares two passes of the SAME model family and measures model self-consistency, not inter-rater reliability. Abstract stage used dual reading with adjudication. Recall validated by dual-pass false-negative audits: abstract-stage ~99.7%, title-stage ~99.5%.
Those audits were same-family, and in September 2026 a human round-3 validation found what they had
missed: the June criteria never named self-reported RECALL and under-specified CONTENT prevalence, so
both were excluded by instruction. Every title- and abstract-stage exclusion was then re-screened by
two independent model families under corrected criteria, retrieved, screened at full text and
extracted. Full account: `docs/corpus_repair_2026-09/REPAIR_REPORT.md`; the corrected criteria are at
`data/extract_v2/qa/flagged_abstracts/adjudication/CRITERIA.md`.

## 4. Extraction (estimate-level)
Unit = study × country × platform × measure (multiple rows per study). Every value carries a VERBATIM source_quote (verbatim-or-drop), a denominator, a definition, n, and measurement date. 100%-confidence quote-anchoring (Step A: 567/568 values verbatim-present in full text).

## 5. Construct & denominator taxonomy
Constructs: CONTENT / EXPOSURE / REACH / SHARING / RECALL (sub-typed exposure vs sharing) / CONCENTRATION (audience-level; source/creator concentration excluded) / QUALITY (excluded from prevalence) / OTHER; BELIEF excluded.
denom_type: population (whole-diet) / topical (keyword/topic) / single_source / curated (misinfo-pre-selected → dropped as circular).

## 6. Verification pipeline (QA)
- **Manual expert spot-check** (6 rounds) → 43 learned coding rules (docs/learned_review_rules.md, L1–L43) encoding error classes: news≠fake-news, regression-slope≠prevalence, audience-lean≠prevalence, echo-chamber/bot≠prevalence, source-level≠content, conspiracy/stance/sentiment≠falsity, fact-check/corpus composition (circular), creator-concentration, nested-subgroup, relative-virality, mean-count≠share, reach≠diet-share, single-source documentation.
- **Phase 2** cross-source dedup + data_provenance (non-independence) flagging + retraction/preprint check + unit-of-analysis.
- **Step B**: independent full-text second-reader pass over all full-text studies applying L1–L43 (verify value↔quote↔text, construct audit, sampling-frame neutrality/circularity test, denominator-type tag, fill date/n/definition).
- **Reviewer adjudication**: every proposed drop reviewed (flag-don't-delete → human sign-off).
- **Strict re-examination** of low-confidence keeps.

## 7. Adversarial certification (2026-06-29)
- Argue-to-keep: 40-study random sample of the 187 dropped studies → **0 rescued / 40 upheld** (false-drop rate ~0%, 95% CI ~0–9%). Curation certified — no over-pruning.
- Refute headline: 24 population-denominator EXPOSURE estimates → 21 hold, 3 denominator-mislabels corrected. Canonical anchors confirmed verbatim (Allen 0.15%, Guess 5.9%, Oswald 0.75%).

## 8. Current dataset
> **Do not read this section for a count.** The current freeze is the TOP block of `docs/FROZEN.md`,
> and `docs/counts_crosswalk.md` — regenerated by `scripts/make_counts_crosswalk.py` on every
> re-freeze — says what each count means. This section is hand-maintained, was left at v1.5.2
> (679/317) for fifteen freezes, and went stale again at v1.7.14 and v1.7.16. Those two files are
> authoritative whenever they disagree with what follows.

As at freeze **v1.7.23** (2026-09-16): 1,048 estimate rows / 443 studies, 934 of them in the main
analysis set. Constructs: {'CONTENT': 429, 'RECALL': 255, 'SHARING': 128, 'REACH': 106,
'EXPOSURE': 46, 'CONCENTRATION': 36, 'OTHER': 27, 'QUALITY': 21}
(`data/synth/phaseB/corpus_counts.csv`).

## 9. The June plan of record — every step DONE
Kept verbatim as the plan, with each step's completion recorded. kappa=0.78 + adjudication → FREEZE
(dataset-frozen-v1) → blind 10% re-extraction (error rate + CI) → RA human gold-standard → Phase 4
(moderator/RoB coding, medians by construct×denom_type×RoB, sensitivity analyses, definition
meta-regression, PRISMA flow + GRADE) → rebuild figure/dashboard/manuscript. All complete by
2026-08, and each was re-run on the repaired corpus in September: risk of bias now covers 443 of 443
studies, the blind re-extraction covers the whole corpus rather than a 10% sample (§8 of
`docs/data_quality_methods.md`), and GRADE is re-derived on every re-freeze into
`data/synth/phaseB/grade_sof.csv`.
