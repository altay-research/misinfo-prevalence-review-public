> **ORIGINAL PROTOCOL AS DRAFTED (June 2026) — retained unedited as the protocol of record.**
> The review was executed with documented deviations: dual-independent screening was replaced by single-LLM-screener + bounding checks; Web of Science was skipped (Scopus+OpenAlex+PubMed+snowball); RoB became the Hoy-adapted v3 instrument; a multilevel meta-regression was added. The as-executed methods are
> `docs/METHODS_PROVENANCE.md` + manuscript §4; every deviation is logged with rationale in
> `docs/research_log.md` / `docs/DECISIONS_REGISTER.md`. (Banner added 2026-08-11.)

# Protocol (PRISMA-P) — DRAFT v0.1 (2026-06-20)

> Living document. Every substantive change is committed to git with a message
> explaining the rationale. Decisions and their justifications are logged in
> `research_log.md`.

## 1. Title
Prevalence and concentration of misinformation exposure: a systematic review of
audience-level estimates and the methodological choices that shape them.

## 2. Rationale (why this review, why now)
Headline estimates of "how much misinformation is out there" diverge by orders of
magnitude. Three distinct quantities are routinely conflated:
1. **Content prevalence** — share of items (posts/URLs) that are false/unreliable.
2. **Audience exposure** — share of an individual's information diet that is
   misinformation.
3. **Concentration** — how unequally exposure/consumption is distributed (share
   consumed by the top X% of users; Gini-type measures).
Existing systematic reviews are **health-domain only** (JMIR 2021; BMC 2026) or
narrative/bibliometric (Budak 2024; Tandfonline 2024). None synthesises audience
exposure **and** concentration across domains and platforms with methodological
coding. (Evidence: `research_log.md`, 2026-06-20.)

## 3. Research questions
- **RQ1 (prevalence):** What is the estimated audience exposure to / consumption of
  misinformation, across platforms (incl. TikTok), countries, and time?
- **RQ2 (concentration):** To what extent is misinformation consumption — and
  production/sharing — concentrated among a minority of users?
- **RQ3 (methods):** How do measurement choices (denominator; source/domain list;
  definition source; platform; country; time window; data type: trace vs survey vs
  content) drive variation in the estimates?
- **RQ4 (actors):** What is the prevalence of misinformation in the output of specific
  actor classes — political elites (politicians/candidates/parties), influencers,
  news outlets — and on which platforms? (Added 2026-06-20.)
- **RQ5 (grey lit vs peer-reviewed):** How do non-peer-reviewed reports (e.g. Science
  Feedback, NewsGuard, Reuters Institute) define and quantify misinformation, and how
  do their headline figures and methods compare with peer-reviewed estimates?

## 4. Eligibility criteria (v0.2, 2026-06-20)

Structured PICOS-style for a prevalence review. A record is INCLUDED only if it meets
every "Include" condition and triggers no "Exclude" condition.

### 4.1 Inclusion (all required)
- **Phenomenon/construct.** Reports ≥1 quantitative estimate of one of:
  (i) **audience exposure** to misinformation (share of a person's/population's
  information diet, reach, impressions); (ii) **consumption** (visits, time, views);
  (iii) **observed sharing/production** (real-world dissemination); (iv) **concentration**
  of any of the above (share by top X%, Gini, supersharer/superconsumer stats);
  (v) **actor-level prevalence** — misinformation as a share of a defined actor class's
  output (politicians/parties, influencers, news outlets). [RQ1–RQ4]
- **Misinformation, broadly construed**, operationalised in the study via a stated
  procedure: source/domain reliability list (e.g. NewsGuard, fact-checker lists),
  item-level veracity rating, or equivalent. The *definition used* is itself extracted
  (it is an object of analysis, not a gate).
- **A denominator is identifiable** (estimate is "X of some defined total"), so the
  figure is interpretable as prevalence/share. Pure counts with no denominator are
  recorded but flagged as non-comparable.
- **Empirical & quantitative.**
- **Channel:** online platforms AND/OR traditional media (TV/radio/press). [decided]
- **Any country; any time period of data.**

### 4.2 Exclusion
- Studies of *content* prevalence only (no audience denominator) — but record them
  separately, as the conflation is part of RQ3.
- Belief/susceptibility-only and intervention-only studies (no exposure estimate).
- **Hypothetical / stated / intended behaviour.** For the sharing/production construct,
  EXCLUDE studies measuring *sharing intentions* — "would you share?", willingness-to-
  share, intention-to-share, vignette/lab experiments on hypothetical sharing (e.g.
  much of the accuracy-nudge literature). INCLUDE only **observed real-world sharing**
  (digital-trace / platform / behavioural data). NB: the criterion is *hypothetical vs
  actual behaviour*, NOT survey-vs-trace — survey-measured *exposure* ("did you see
  X?") estimates real exposure and stays IN; only hypothetical *intentions* are out.
  This is a SCREENING-stage criterion: keyword counts show the explicitly-flagged
  intention bucket is small (223 records, 2026-06-20) but most experimental sharing
  studies are not keyword-separable from field studies, so they must be caught by
  human screening on the measurement type. Coded via the `data type` / `behaviour
  type` extraction field.
- Computer-science detection/classification methods papers (no human exposure estimate).
- Non-empirical (commentary, theory, pure review, editorial).
- *Content* prevalence with **no audience denominator** → recorded in a separate table
  (feeds RQ3 on the content-vs-audience conflation), not in the main synthesis.
- Belief/susceptibility-only and intervention/correction-only studies (no exposure est.).
- **Hypothetical/stated/intended behaviour** (sharing-intention experiments, willingness-
  to-share, vignette/lab hypothetical sharing). Screening-stage criterion; see §4.4.

### 4.3 Confirmed parameters (Sacha, 2026-06-20)
- **Date range:** NO lower bound; include all years and report the year distribution.
- **Language:** **English only** at full-text screening. Known relevant non-English
  studies (e.g. Berriche 2024 [Fr]; possibly Cordonnier & Brest [Fr]) are noted as a
  documented limitation; English-language reports of the same data are used where they
  exist (e.g. Lasser et al. 2022 is English). This trades some coverage for solo-review
  feasibility — flagged as a limitation in the write-up.
- **Publication type:** peer-reviewed articles + conference papers + **preprints
  (flagged as non-peer-reviewed)**; a sensitivity analysis excludes preprints. Grey
  lit/reports handled in the separate RQ5 track.
- **Minimum sample/quality:** NO hard threshold at inclusion; quality captured in the
  risk-of-bias appraisal (§9) and used in sensitivity analysis.

### 4.4 Construct-specific note (sharing)
For the sharing/production construct the criterion is *hypothetical vs actual
behaviour*, NOT survey-vs-trace: survey-measured **exposure** ("did you see X?") stays
IN; only hypothetical **intentions** ("would you share X?") are excluded. Most lab
sharing-intention studies are not keyword-separable from field studies (explicit
intention bucket = 223 records, 2026-06-20), so this is enforced by human screening on
the measurement type and coded in the `behaviour type` extraction field.

## 5. Information sources
**Peer-reviewed:** Scopus (primary, confirmed), Web of Science (planned). Supplementary:
local PDF library (recall check), Semantic Scholar (citation chaining).
**Grey literature (separate track, RQ5):** targeted search of known producers of
prevalence figures — Science Feedback, NewsGuard, Reuters Institute (Digital News
Report), EU DisinfoLab, ISD, Oxford ComProp, Avaaz, EUvsDisinfo, AlgorithmWatch,
Mozilla. Searched and logged separately; **never pooled** with peer-reviewed estimates.
**Seed/recall set:** the 19-study table digitised from Berriche (2024) —
`data/seed_berriche_annexe1.csv`. Any final search string MUST recover the indexed
seed studies (recall validation, §research_log 2026-06-20).

## 6. Search strategy
Building blocks and exact strings are in `scripts/scopus_search.py` and logged with
dated hit counts in `searches/scopus_query_log.tsv`. **Working string = preset
`strict_v2`** (adopted 2026-06-20 after recall validation: 14/16 seed studies vs 8/16
for v1). It requires a topic term AND a measurement-family term (exposure/consumption/
sharing/spread/diffusion/scale/quantification/supersharer/…) and excludes CS-detection
terms in the TITLE only. **Corpus = 20,409 Scopus records (2026-06-20).**
**Precision task (RESOLVED 2026-06-20):** tuning (`scripts/tune_search.py`) showed no
query-tightening variant preserves recall (prox_W5 → 11/16; empirical → 12/16; combo →
9/16; consumption-only → 10/16), whereas v2_baseline keeps 14/16. Decision: **do not
tighten the query; keep `strict_v2` (recall-max) and reduce the ~20k at the screening
stage** via LLM-assisted title/abstract pre-screen with human verification of all
borderline/excluded records (auditable; no silent capping). `prox_W5` (6,603 records)
reported as a **sensitivity analysis**. *Sharing* terms are retained: dropping them
loses the supersharer/production-side seed studies central to RQ2.

## 7. Selection process
Two-stage screening (title/abstract → full text), dual independent screening with a
documented reconciliation rule (to set once team is decided). Record every exclusion
reason. PRISMA flow diagram produced at the end.

## 8. Data extraction & coding scheme (DRAFT)
Per estimate (one row = one estimate, studies may yield several — cf. Berriche table):
study, year, country, platform/data source, period, sample/N, data type
(trace/survey/content), misinformation **definition source** (which fact-checker /
domain list), corpus size (# fake-news sources; # mainstream sources), **construct**
(content prevalence / audience exposure / concentration), **denominator** (of what
total?), point estimate, units, concentration statistic (share by top X%; Gini).
The seed CSV already instantiates most of these columns.

## 9. Risk-of-bias / quality appraisal
To select (e.g. a bespoke checklist for trace-data validity: domain-list provenance,
denominator transparency, platform coverage). Not yet defined.

## 10. Synthesis
Structured/narrative quantitative synthesis with tabulation by construct and by
method; **no pooled meta-analytic effect size** (heterogeneous constructs). Possible
targeted pooling only within tightly comparable clusters (e.g. untrustworthy-domain
share of web news diet). Visual: estimates arrayed by construct + method moderators.

## 11. Open items
See the running checklist at the end of `research_log.md`.
