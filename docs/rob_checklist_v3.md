# Risk-of-bias instrument v3 — Hoy-mapped, full-text appraisal

**Status:** supersedes `docs/Old/rob_checklist.txt` (v2, 5 bespoke dimensions scored from
"title + context"). Introduced 2026-07-23 following the multi-dimension project review.

**Coverage, as at 2026-09-16.** Risk of bias is appraised for all 443 studies in the freeze, 418 of
them from full text and 25 from the abstract alone. On the ruling-corrected variant the summary
ratings are LOW 53, MODERATE 210, HIGH 181; the full-text-only sensitivity is LOW 52, MODERATE 208,
HIGH 159. `scripts/aggregate_rob_v3.py` asserts coverage against the freeze on every run and writes
the distributions to `data/rob/rob_v3_summary.csv`; the §"Why v3 exists" section below describes the
July 2026 corpus and is kept as the rationale of record, not as a current count.

## Why v3 exists

Three defects in v2, all of which a peer reviewer would raise:

1. **Not a recognised instrument.** v2 was a home-grown 5-dimension scheme. Reviewers of a
   prevalence review expect an established prevalence-appraisal tool, or an explicit,
   documented adaptation of one.
2. **Scored from title + context, not full text.** `Old/rob_checklist.txt:2` says "Judge from
   title + context (ctx)". Judging sampling, case definition and measurement validity from a
   title is not defensible. 90% of the frozen corpus (286/317) has cached full text.
3. **Barely discriminated.** v2 rated 73% of studies HIGH overall, 77% NARROW denominator,
   81% CURATED sampling. An instrument on which almost everything scores badly carries little
   information — and the review's headline claim ("risk of bias tracks the number inversely")
   depends on this instrument separating studies.

Plus a coverage failure: **88 of 317 frozen studies had no RoB record at all**, while the
v2 master carried **261 records for studies no longer in the corpus** — it was never
reconciled to the final frozen study list.

## Base instrument

**Hoy D, Brooks P, Woolf A, et al. (2012)**, "Assessing risk of bias in prevalence studies:
modification of an existing tool and evidence of interrater agreement", *Journal of Clinical
Epidemiology* 65(9):934-939. Ten items; 1-4 external validity (selection/non-response),
5-10 internal validity (measurement/analysis). Each item is rated **LOW** or **HIGH** risk.

Hoy is chosen over the JBI prevalence checklist because two of its items map directly onto
the constructs this review is built around:

- **Hoy item 10** ("Were the numerator(s) and denominator(s) for the parameter of interest
  appropriate?") *is* this review's denominator thesis, stated as a validated appraisal item.
- **Hoy item 6** ("Was an acceptable case definition used?") *is* the falsity-vs-quality
  boundary — the "what counts as misinformation" problem.

Being able to say "our central methodological claims correspond to items 6 and 10 of a
validated prevalence risk-of-bias tool" is a substantially stronger position than defending
a bespoke scheme.

## The ten items, adapted to misinformation-prevalence designs

Rate each **LOW** or **HIGH** risk of bias. Where an item cannot be judged from the
available text, rate **UNCLEAR** and treat as HIGH in the overall (recorded separately).

| # | Hoy item | Adapted decision rule for this review |
|---|---|---|
| 1 | Target population representative of the national population? | Does the study's target population represent a real audience/public, or is it an artificial universe (e.g. only accounts that already posted misinformation, only a curated topic corpus)? **HIGH** if the population is defined by the phenomenon being measured (selection on the outcome). |
| 2 | Sampling frame a true representation of the target population? | Is the frame (panel, platform sample, search results, URL corpus) a fair route to that population? **HIGH** for keyword-seeded or topic-curated frames used to support a general claim. |
| 3 | Some form of random selection used? | Random/probability sampling, a full census of the frame, or a complete behavioural trace = **LOW**. Purposive, convenience, top-N-by-engagement, or "most-shared" selection = **HIGH**. |
| 4 | Likelihood of non-response bias minimal? | Survey/panel: response and attrition rates reported and acceptable. Trace/panel data: consent/opt-in bias addressed. Content analyses: **n/a** — record `NA`, do not penalise. |
| 5 | Data collected directly from the subjects? | Behavioural trace or direct survey of the person = **LOW**. Proxy/aggregate/inferred audience (e.g. inferring exposure from publisher-side counts) = **HIGH**. Content-only designs: **NA**. |
| 6 | Acceptable case definition used? | **Load-bearing.** Was misinformation defined against an external ground truth (fact-check verdicts, validated domain/credibility list, expert-verified false claims)? Author-devised subjective coding, or quality/usefulness/guideline-adherence standing in for falsity = **HIGH**. Mirrors the project's CONTENT-vs-QUALITY rule. **See the source-level-list ruling below — it governs a large minority of studies.** |

### RULING: source-level credibility lists satisfy item 6 (Sacha, 2026-07-23)

**A published source-level credibility, reliability or "junk news" list counts as an acceptable
external case definition. Item 6 = LOW.** This covers NewsGuard, Media Bias/Fact Check, the
Grinberg/Lazer black-red-orange lists, the Oxford Computational Propaganda "junk news" typology,
Décodex, and comparable third-party blacklists — including ad-hoc unions of several such lists.

*Why this is the right call rather than a lenient one.* The worry is that these lists encode partisan
lean, sourcing standards or professionalism rather than verified falsity, so treating them as ground
truth lets quality masquerade as prevalence. But this review **already measures that**, on dedicated
moderators: `breadth` (the veracity scale — fabricated → false → misleading, blank when the
definition states no per-item veracity standard; the retired wider codes now live in
`classification_level` = source_level vs claim_level) — and the meta-regression estimates how much
the estimate moves as the identification level and definition widen. Penalising source-level
identification a second time inside the risk-of-bias instrument would **double-count the very thing the
moderator analysis exists to quantify**, and would push the bias rating and the breadth moderator into
collinearity — making it impossible to tell whether "high-RoB studies report higher numbers" is a
statement about study quality or merely a restatement of the breadth coding.

This is the same principle GRADE applies under Inconsistency: do not penalise as bias what a moderator
already explains. It also keeps item 6 doing one job — *is there an external standard at all?* — rather
than smuggling in a judgement about which external standard is best.

**What still fails item 6:** author-devised coding with no external anchor; quality instruments
(DISCERN, GQS, JAMA, VIQI) or guideline-adherence standing in for falsity; circular definitions; and
lists assembled by the authors themselves for the study at hand from no stated criteria. The line is
*external and pre-existing* versus *internal and ad hoc* — not *claim-level* versus *source-level*.

**Consequence for `classification_level`:** source-level identification remains recorded there
(`source_level` vs `claim_level`) and, per Nenno et al. 2025 (~10x difference), stays a first-order
moderator. The information is preserved; it is just not counted twice.

**Rows requiring re-rating under this ruling (EXECUTED — the re-ratings were applied in the v3 master; historical record)** (8 appraised rows rated item 6 HIGH/UNCLEAR on a
source-level list; 6 of them have item 10 HIGH too, so they move HIGH → MODERATE):
`85038621544` · `85066887935` · `85074511992` · `85074596916` · `85078014559` · `85092033301` ·
`85131073869` · `85164694763`. Shards 20-31 must apply the ruling from the outset.
| 7 | Instrument shown to have validity and reliability? | Is the classifier/coding scheme validated, and is coder reliability reported (kappa/alpha, or a validated list)? No reliability statistic and no validated instrument = **HIGH**. |
| 8 | Same mode of data collection for all subjects? | Consistent instrument/platform/period across the sample = **LOW**. Mixed modes without adjustment = **HIGH**. |
| 9 | Length of the shortest prevalence period appropriate? | Is the observation window stated and adequate for the claim? Undated or single-day windows generalised to "prevalence" = **HIGH**. |
| 10 | Numerator(s) and denominator(s) appropriate? | **Load-bearing.** Is the denominator the quantity the claim implies — a real audience's whole diet or a defined total — rather than a curated subset? Selected-on-misinformation denominators, or "% of the false items" presented as prevalence = **HIGH**. |

### Summary judgement

Following Hoy, the overall rating is a **judgement**, not a count, but anchored:

- **LOW** — 0–2 HIGH items, and items 6 and 10 both LOW.
- **MODERATE** — 3–5 HIGH items, or one of items 6/10 HIGH.
- **HIGH** — ≥6 HIGH items, or both items 6 and 10 HIGH.

Items 6 and 10 are weighted because they are the dimensions the review's argument turns on;
this weighting is pre-specified here rather than applied post hoc.

## Required output per study

```
study_id, item1..item10 (LOW|HIGH|UNCLEAR|NA), n_high, overall (LOW|MODERATE|HIGH),
source_read (full_text|abstract_only), quote_item6, quote_item10, notes
```

`quote_item6` and `quote_item10` are **verbatim** sentences from the source supporting those
two judgements. A rating on items 6 or 10 without a supporting quote is not accepted — this
is the same quote-anchoring discipline used for value extraction.

## Crosswalk to v2

Retained so the v2 ratings remain interpretable and the change is auditable:

| v2 dimension | v3 items |
|---|---|
| denominator (CLEAR/NARROW/UNCLEAR) | 10 (primary), 1 |
| sampling (REPRESENTATIVE/CURATED/CONVENIENCE) | 2, 3 |
| definition (VALIDATED/PARTIAL/ADHOC) | 6 (primary), 7 |
| measurement (BEHAVIOURAL/SELF_REPORT/CONTENT_CODING) | 5, 8 |
| sample_size (ADEQUATE/SMALL/UNCLEAR) | — (Hoy has no size item; retained as a separate descriptor, not a bias item) |
| — | 4, 9 are new in v3 |

Sample size is deliberately **not** a Hoy risk item. It was carried in v2 and conflated
precision with bias; v3 keeps it as a descriptive field only. This matters because the
review reports a separate precision-weighting analysis, and double-counting sample size as
both bias and precision would penalise small studies twice.

## Scoring procedure

1. Read the cached full text (`data/fulltext/v2txt/`). If unavailable, read the abstract and
   record `source_read=abstract_only`; these are reported separately and are candidates for
   a sensitivity analysis.
2. Rate all ten items with the rules above.
3. Extract the two verbatim quotes.
4. Reliability: a blind second pass on a random subsample, reported with raw agreement,
   Cohen's kappa, **and** prevalence-adjusted coefficients (PABAK/Gwet AC1) — the v2
   reliability script already does this correctly and is retained. Because both passes are
   LLM passes, this is reported as **model self-consistency**, not inter-rater reliability;
   see the human-verification study for the independent figure.
