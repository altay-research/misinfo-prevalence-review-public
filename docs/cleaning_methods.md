> **HISTORICAL (pre-extract_v2 pipeline, June 2026).** Documents the first-generation cleaning;
> its dataset, file paths and medians are all superseded (current: docs/FROZEN.md pointer +
> data_quality_methods.md). Kept because the QUALITY/BELIEF exclusion rationale it records is
> still the conceptual basis of the falsity-vs-quality rule. (Banner added 2026-08-11.)

# Estimate cleaning & re-classification — methods (2026-06-21)

**Why this exists.** During synthesis review, Sacha flagged that the CONTENT median (37%)
and RECALL median (57%) "looked too high" and questioned whether those estimates were
really measuring *prevalence of misinformation*. Inspection confirmed two contamination
problems, so we ran a transparent, reproducible re-classification of every numeric
estimate. This document records the rationale, taxonomy, process, decisions, and results
so the cleaning is fully auditable.

## The two problems found (by sampling, before deciding)
Evidence: `python3` sampling of the CONTENT and RECALL buckets (see research_log §34):
1. **Content QUALITY ≠ falsity.** Many "content prevalence" estimates were actually
   accuracy/usefulness/guideline-adherence ratings — e.g. "77% classified as *neither
   useful*", "80% *non-guideline*", "44% *partially accurate*". These are information-
   quality scores, **not** the share of items that are false. They inflate "content
   prevalence".
2. **RECALL conflated SEEING with BELIEVING.** The RECALL bucket mixed legitimate
   self-reported exposure ("90% *encountered* misinfo") with **belief** ("69% *believe*",
   "61% *believe* insect transmission", "rumours *believable* 30%"). Belief is a
   different construct.

Secondary: a few **behavioural exposure** estimates (e.g. "26% *visited* an untrustworthy
site") were mis-tagged as RECALL; they are trace/behavioural exposure.

## Decisions (and their justification)
- **BELIEF → EXCLUDED.** Belief-in-misinformation is out of scope (our criteria exclude
  belief/susceptibility), AND our search string was never designed to capture it (no
  belief/susceptibility terms), so the belief studies we happen to have are a **biased,
  non-representative sliver** of a large separate literature. Reporting a "belief
  prevalence" from them would mislead. (Sacha's call, 2026-06-21.)
- **QUALITY → EXCLUDED from prevalence.** A quality/usefulness rating is not the prevalence
  of misinformation. Kept as a clearly-labelled separate category (shown greyed in the
  figure), never pooled with prevalence.
- **TRACE_EXPOSURE → merged into EXPOSURE.** Behavioural exposure (visits / % of diet /
  time) is the construct we care about; mis-tagged ones were reassigned here.
- **FALSE_CONTENT** kept as CONTENT, but flagged: these overwhelmingly use **keyword-
  curated, topic-specific samples** (e.g. "TikToks about prostate cancer"), so the figure
  is "% of items false *in a curated topic sample*", NOT "% of what people see". This
  denominator caveat is itself a paper finding.

## Taxonomy (the strict re-classification scheme)
Every numeric estimate in the included set was re-classified by an LLM agent, given the
estimate text + title + abstract/full-text context, into EXACTLY one of:
| code | meaning | keep? |
|---|---|---|
| FALSE_CONTENT | share of ITEMS that are false/misleading | ✅ → CONTENT |
| QUALITY | accuracy/usefulness/quality/guideline rating, not falsity | ❌ excluded |
| SAW | % of PEOPLE who report seeing/encountering misinfo (recall) | ✅ → RECALL |
| BELIEF | % who believe / find believable | ❌ excluded (out of scope) |
| TRACE_EXPOSURE | behavioural/trace exposure (visits, % of diet, time) | ✅ → EXPOSURE |
| SHARING | observed sharing/spread, or % of an actor's output | ✅ → SHARING |
| CONCENTRATION | share by the top X% of users/accounts | ✅ → CONCENTRATION |
| OTHER | unclear / something else | held out |

## Process (reproducible)
1. Sample + inspect (research_log §34).
2. Build context-rich input: `data/clean/to_clean.jsonl` (the 282 CONTENT+RECALL value-
   bearing estimates) + `to_clean2.jsonl` (the remaining 78), each with value_raw, title,
   and abstract/full-text excerpt.
3. Re-classify via agents → `data/clean/c_*.csv`, `c2_*.csv` (eid, new_class, value_pct,
   reason). 359 estimates classified.
4. Merge + map to final categories → `data/synth/normalised_clean.csv`.
5. Recompute medians; regenerate figure (`scripts/make_contrast_figure.py` now reads the
   clean file) → `docs/figure_contrast.*`.

## Result (cleaned medians, included set)
| category | n | median | note |
|---|---|---|---|
| CONTENT (items false, curated samples) | 177 | **36%** | inflated denominator (topic-curated) |
| RECALL (self-report "I saw it") | 20 | 68% | soft, over-reported |
| SHARING | 23 | 31% | |
| CONCENTRATION (top users) | 13 | 70% | rarely measured (n=13) |
| **EXPOSURE (% of actual diet, behavioural)** | 16 | **11%** | the number that matters; lower still for whole-diet studies |
| ~~QUALITY~~ (excluded) | 59 | 44% | not misinformation prevalence |
| ~~BELIEF~~ (excluded) | 6 | 54% | out of scope; search-biased |

**Net:** 65 estimates (59 QUALITY + 6 BELIEF) removed from "prevalence". The headline
holds and is cleaner: perceived/curated-content numbers are high; **behavioural exposure
is ~an order of magnitude lower**; concentration high but barely measured.

## Refinements DONE (2026-06-22, research_log §38)
- **EXPOSURE split**: whole-diet n≈15 median **6.0%** vs topical n=7 median 8.5% — the
  true consumption headline is ~6%. (data/synth/exposure_split.csv)
- **Dual-pass κ** (blind second coder, n=90): cleaning κ=0.60 overall, **0.75 among the 5
  prevalence buckets**; disagreements concentrate on the QUALITY↔CONTENT boundary (the
  fuzzy "is an accuracy rating falsity?" call). EXPOSURE cleanly separated → headline
  robust. RoB reliability (overall, n=89): raw 85%, within-1-level 100%; Cohen κ=0.48
  deflated by HIGH-heavy skew (73/13/3), paradox-robust **PABAK=0.78, Gwet AC1=0.83**
  ("almost perfect"). Weakest dimension = definition rigour (AC1=0.60). Recompute:
  `scripts/rob_reliability.py`.
