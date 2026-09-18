# Extraction protocol v2 — estimate-level + sharp construct rules (2026-06-22)

Supersedes the v1 one-estimate-per-paper extraction. Two changes, both prompted by review
(research_log §40): (a) the unit of analysis is the **estimate**, not the paper;
(b) a **sharp operational rule** for the QUALITY↔CONTENT boundary.

## A. Unit of analysis = the estimate (nested in study)
Extract **every** distinct estimate a paper reports, as its own row, keyed by the
dimensions on which it varies. One row per unique combination of:
`study(eid) × country × platform/source × measure_type × subgroup(if reported)`.

Example (Altay et al., JQD, 4 countries × {Facebook, Web}): **8 rows**
— FR-Facebook, FR-Web, US-Facebook, US-Web, GB-Facebook, GB-Web, DE-Facebook, DE-Web,
each with its own value, denominator, and n.

Rules:
- Split when the paper reports separate numbers by country, platform/source, or measure.
- Do NOT split a single pooled number into invented sub-rows — only extract numbers the
  paper actually reports.
- Granularity ceiling (this project, per decision 2026-06-22): country × platform × measure.
  Demographic/partisan subgroups and time waves are recorded in a `subgroup` field when
  trivially available but are NOT separately required.
- Each row carries: eid, country, platform, measure_type, subgroup, value_pct, value_raw,
  denominator_text, denom_class, n, page/loc. `estimate_id = eid + "#" + running index`.
- Requires full text (abstracts rarely give all sub-estimates) → gated on retrieval.

## B. Sharp QUALITY↔CONTENT rule
The problem: "content" studies mix *falsity* judgments with *quality/usefulness* ratings;
the borderline ("partially accurate", "non-guideline") is where inter-coder κ fell to ~0.5.

**Operational rule — classify an estimate as:**
- **CONTENT (false-content prevalence)** ONLY IF the study judges **verifiable truth/falsity
  against an external ground truth** — fact-check verdicts, expert-verified false claims, a
  curated false/unreliable-source list (NewsGuard, domain lists), or explicit
  "false/misleading vs true" coding. The reported figure must be the share of items in the
  **false/misleading** category.
- **QUALITY (excluded from prevalence)** IF the figure is a rating of usefulness,
  completeness, reliability, overall "quality", guideline-adherence/concordance, or a
  graded "accuracy score" that is NOT a binary/clear truth-falsity verdict (e.g. DISCERN,
  GQS, JAMA benchmarks, "moderate quality", "partially accurate", "non-guideline").
- **Tie-breakers:** "inaccurate/incorrect *information*" checked against medical/scientific
  fact → CONTENT. "Poor/low quality", "not useful", "incomplete", "suboptimal" → QUALITY.
  A Likert quality scale dichotomised by the authors into "misinformation" → QUALITY unless
  the cut is explicitly a truth/falsity verdict.
- When genuinely ambiguous after this rule → QUALITY (conservative: keep only clean falsity
  in the CONTENT headline) and flag `borderline=Y`.

Applied during v2 extraction; borderline flags enable a sensitivity analysis (headline with
vs without borderline cases).
