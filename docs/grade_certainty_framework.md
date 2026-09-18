# Certainty-of-Evidence Framework (GRADE, adapted for prevalence)

> **APPLIED, and re-derived on every re-freeze** via `scripts/phaseB_grade.py` →
> `data/synth/phaseB/grade_sof.csv`. Current result (v1.7.23): EXPOSURE HIGH · REACH MODERATE ·
> RECALL MODERATE · SHARING MODERATE · CONCENTRATION MODERATE · CONTENT VERY LOW.
> NB this framework doc is NOT the source of truth — grade_sof.csv is, and the ratings move between
> freezes. EXPOSURE was HIGH on v1.4.6, MODERATE from the CI-width criterion, and HIGH again on
> v1.7.20 where the recomposed set triggers no downgrade. SHARING has moved three times: MODERATE →
> LOW at v1.7.8 (indirectness + precision-fragility), back to MODERATE at v1.7.9, LOW at v1.7.16 when
> the corpus repair added topical and curated sharing studies, and MODERATE again at v1.7.20. The
> manuscript checker anchors all six full GRADE rows. Read the CSV.

Standard GRADE rates certainty in an *effect* estimate. This review reports
*prevalence / exposure / concentration* proportions, so we use the **prevalence
adaptation** of GRADE (Murad 2023; Migliavaca et al. 2020 on prevalence
meta-analysis; Borges Migliavaca "certainty of prevalence evidence"). Certainty is
rated **per construct** (CONTENT, EXPOSURE, CONCENTRATION, SHARING, REACH, RECALL),
not per study, and reported in the Results/GRADE Summary-of-Findings table.

This rubric is the instrument; it is encoded in `scripts/phaseB_grade.py` and applied on every
re-freeze, so the ratings always attach to the current pooled medians and IQRs.

## Starting point
Observational prevalence evidence starts at **HIGH** certainty (unlike intervention
GRADE, prevalence estimates are not automatically downgraded for being
observational). Then rate DOWN on five domains and UP is not used.

## Downgrade domains (−1 serious / −2 very serious each)

1. **Risk of bias** — use the per-construct RoB distribution we already computed
   (`data/rob/`, `scripts/rob_reliability.py`). Rule of thumb: >50% of a construct's
   studies HIGH RoB → −1; overwhelmingly HIGH → consider −2.
   (This is the domain that separates the constructs: on the current freeze CONTENT is 55% HIGH-RoB
   and takes the downgrade, while EXPOSURE is 0% and takes none.)

2. **Inconsistency** — heterogeneity of estimates within the construct. Prevalence
   proportions are expected to vary, so judge by spread relative to the claim: wide
   IQR spanning an order of magnitude with no explanatory moderator → −1. Use the
   median/IQR per construct×denom_type; note that our whole-diet vs topical/curated
   split (the definitional driver) is a *predictor*, not unexplained inconsistency —
   don't double-penalize what the moderator analysis explains.

3. **Indirectness** — does the measure answer "audience-level exposure/consumption of
   misinformation"? Downgrade constructs that only proxy it: content-share with a
   topical/curated denominator (not whole-diet), engagement/sharing used as an
   exposure proxy, single-platform samples generalized to "the public". Tie to the
   existing flags (`topical_denominator`, `engagement_not_exposure`, `small_content_n`).

4. **Imprecision** — small denominators / few studies. Prevalence: tiny N or very few
   estimates in a cell, or CIs (where reported) spanning a decision-relevant range → −1.
   Our sample-size-weighted sensitivity (I4) informs this: constructs whose weighted
   mean diverges wildly from the unweighted median (CONTENT, REACH) are precision-
   fragile.

5. **Publication / selection bias** — curated corpora that sample only already-false
   items (no total denominator) inflate content prevalence; grey-track producer
   incentives (CCDH vs Meta denominator contrast). Downgrade constructs dominated by
   such designs.

## Output (Summary of Findings, per construct)
`data/synth/phaseB/grade_sof.csv` carries one row per construct with k studies, median and IQR,
%HIGH RoB, %topical, the weighted-median shift, the downgrade count, the certainty rating and the
reason for each downgrade. It is regenerated with the rest of Phase B, never hand-assigned, and the
manuscript checker asserts all six rows against it.

The pattern the rubric was expected to produce did hold: CONTENT lands at VERY LOW on four
downgrades (55% HIGH RoB, content-share indirectness, a 22-point weighting shift, 94% topical or
curated corpora), and the behavioural constructs land higher. EXPOSURE takes no downgrade at all on
the current freeze, which is a stronger result than the rubric anticipated and rests on 18 studies.

## Reproducibility
The ratings are computed by `scripts/phaseB_grade.py` over the current freeze and `data/rob/`, so
the SoF table regenerates deterministically like the other gates. Do NOT hand-assign in prose.
