# PRISMA 2020 Checklist — "Rare on screens but on everyone's mind"

Manuscript: `docs/manuscript_draft.md` (frozen dataset v1.7.23). Drafted 2026-08-12; section and
figure numbers re-verified against the Nature Human Behaviour build (`scripts/make_nhb_docx.py`)
on 2026-09-07. Supplementary material is numbered as Supplementary Notes A-E and Supplementary
Figs. 1-3, which is the numbering the submitted files use.

| # | Item (abbreviated) | Where reported |
|---|---|---|
| 1 | Title identifies a systematic review | Title |
| 2 | Abstract (PRISMA-for-Abstracts) | Abstract. Registration status and funding are stated in §4.1 and §4.10 but not in the abstract itself; add one closing line at submission if the journal applies the abstract checklist strictly |
| 3 | Rationale | §1 (divergent estimates; gap vs prior reviews) |
| 4 | Objectives | §1 (collect, describe, quantify what explains disagreement) |
| 5 | Eligibility criteria | §4.2; construct grouping §4.6 + Table 1 |
| 6 | Information sources + last-searched dates | §4.3 (Scopus 2026-06-20; OpenAlex/PubMed 2026-06-24; snowballing; supplementary search) |
| 7 | Full search strategies | Supplementary Note D (verbatim Scopus string; other streams described; scripts in repository) |
| 8 | Selection process | §4.4 (single LLM screener + bounding checks; second-reader verification) |
| 9 | Data collection process | §4.5 (double extraction, reconciliation); reliability §4.8 + Supplementary Note C1 |
| 10a | Data items — outcomes | §4.5–4.6 (value, value_kind, construct taxonomy, falsity–quality rule) |
| 10b | Data items — other variables | §4.5, Supplementary Note C2 (moderators; explicit "unspecified" levels) |
| 11 | Risk of bias tool/process | §4.7 (Hoy adaptation, quote requirement, summary rule); PABAK §4.8 |
| 12 | Effect measures | §4.9 (proportions; study-level medians + bootstrap CIs; ratios) |
| 13a | Synthesis eligibility | §4.9 (main-analysis set; QUALITY/OTHER never pooled) |
| 13b | Data preparation | §4.9 + Supplementary Note C2 (logit PLO; concentration standardisation) |
| 13c | Display methods | §4.9; Figures 1–5; Supplementary Table 1 (B3) |
| 13d | Synthesis methods + rationale | §4.9 (no pooled figure, rationale; DL models; prediction intervals) |
| 13e | Heterogeneity exploration | §4.9 + Supplementary Note C2 (slicing, meta-regression); Supplementary Note A |
| 13f | Sensitivity analyses | §4.9 + Supplementary Note C2; results §2.7 + Supplementary Note B2 |
| 14 | Reporting bias assessment | Supplementary Note C2 (Spearman rationale vs Egger); results §2.4 |
| 15 | Certainty assessment | §4.7 (the risk-of-bias input); method and ratings in Supplementary Note B3; summary in §2.7 |
| 16a | Selection results + flow | Supplementary Fig. 1 (PRISMA flow); counts in Abstract, §4.3–4.4 |
| 16b | Excluded-at-full-text list with reasons | `data/synth/phaseB/si_fulltext_exclusions.csv` — one row per excluded report with its reason category and the ledger's own free text (`docs/SI_lists_README.md`); ships as supplementary data, no in-text table |
| 17 | Study characteristics | Aggregate in §2.1–2.2; per-study in `data/synth/phaseB/si_included_studies.csv` (author, year, title, venue, DOI, constructs, n estimates, text basis) and in the frozen dataset (§4.11) |
| 18 | Risk of bias per study | Distributions in Supplementary Note B1; per-study appraisals with quotes in the repository (§4.11) |
| 19 | Individual study results | No per-study in-text figure; construct-level distributions in Figure 3, and all 1,048 estimates ship study by study in the supplementary data (§4.11) |
| 20a–d | Synthesis results | §2.3–2.10; Supplementary Notes A–B |
| 21 | Reporting bias results | §2.4 |
| 22 | Certainty results | §2.7 + Supplementary Note B3 (Supplementary Table 1) |
| 23a–d | Discussion: interpretation, evidence limits, process limits, implications | §3 (incl. the seven-limitation paragraph); Supplementary Note C3 |
| 24a | Registration | §4.1 — explicitly NOT registered (statement satisfies the item) |
| 24b | Protocol access | §4.1 — no prospective protocol; append-only research log named as the timestamped record |
| 24c | Amendments | §4.1 — deviations documented in the log; formal amendments n/a |
| 25 | Support | §4.10 Statements — University of Zurich, UZH Postdoc Grant no. FK-25-078 |
| 26 | Competing interests | §4.10 Statements — none declared |
| 27 | Availability of data/code/materials | §4.11 |

## Remaining gaps (author's call at submission)

1. Abstract does not itself carry registration/funding lines (item 2 sub-checklist) — one sentence
   if the target journal enforces it.
2. Item 16b is satisfied by a supplementary table rather than an in-text one. The table exists
   (`si_fulltext_exclusions.csv`, 441 records); 102 of its rows carry the reason category but no
   per-record free text, 75 of them because the v1-to-v2 re-freeze logged none. Disclosed in
   `docs/SI_lists_README.md`.
3. Items 17–19 rely on the released dataset as the per-study table — standard for estimate-level
   syntheses of this size, but be ready to render per-study tables on request.
