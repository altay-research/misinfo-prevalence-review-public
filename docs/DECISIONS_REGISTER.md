# Decisions register — for Sacha's review & validation

Every consequential decision made in building this review, with the rationale and the
alternative considered. **Review column is blank for you** — mark each: `✅ keep` /
`✏️ change (note)` / `❓ discuss`. Grouped by phase. Cross-refs to `research_log.md` (§).
Last built 2026-06-22. Nothing here is locked; all are reversible.

---

## A. Scope & eligibility

| # | Decision | Why | Alternative | Your call |
|---|---|---|---|---|
| A1 | **Broad construct**: misinformation, disinformation, fake/false news, unreliable/untrustworthy sources, junk news | The conflation across these terms is part of the phenomenon we study | Restrict to "fake news" or to fact-checked falsity only | |
| A2 | **Online + traditional media** (TV/radio/press) | Exposure happens across the whole diet, not just online | Online-only (most of the literature) | |
| A3 | **Any country, any date, no quality threshold** | Maximise coverage; describe heterogeneity rather than pre-filter | Date bound (e.g. 2016+), or quality cut | |
| A4 | **English-language only** | Resource constraint; documented limitation | Multilingual screening | |
| A5 | **Preprints included** (flagged) | Field is preprint-heavy (arXiv/SSRN/OSF); excluding biases toward older work | Peer-reviewed only | |
| A6 | **BELIEF / susceptibility EXCLUDED** | Different construct; our search wasn't built for it → would be a biased sliver | Include belief as a 5th quantity | |
| A7 | **Experimental ("asked-to-share") sharing EXCLUDED; observed real-world sharing INCLUDED** | Survey/lab sharing ≠ what people actually share | Include experimental sharing | |
| A8 | **Correction/intervention experiments, detection algorithms, pure theory EXCLUDED** | Not prevalence measurements | — | |
| A9 | **Grey literature = separate non-pooled CONTRAST track** | Advocacy/regulator numbers are the denominator problem in extreme form; pooling would corrupt the synthesis | Pool grey lit with peer-reviewed; or exclude entirely | |
| A10 | **Solo review; LLM as documented second screener/extractor** | No co-screener available; mitigated by κ + verification | Recruit a human second coder | |

## B. Search & sources

| # | Decision | Why | Alternative | Your call |
|---|---|---|---|---|
| B1 | **Scopus** as primary database | Available API; broad coverage | WoS / PubMed / Google Scholar | |
| B2 | **Recall-favouring Boolean** (`strict_v2`), reduction at screening not in query | SR norm: maximise recall, filter later | Tighter, higher-precision query | |
| B3 | **Recall validated on Berriche seed-16 → 14/16** | Empirical recall check before committing | No formal recall test | |
| B4 | **Year-sliced retrieval** (Scopus entitlement workaround) | API capped cursor/count; slicing recovers full set | — (forced) | |
| B5 | **OpenAlex citation snowball** (backward+forward) from 224 audience-side core studies | Recovers non-Scopus venues (JQD, HKS Misinfo Review, ICWSM, preprints) | Full OpenAlex re-search (30k+ to screen); or no snowball | |
| B6 | **No Web of Science** | No institutional access at build time | Add WoS (would raise recall) — **OPEN, see I1** | |
| B7 | **Frozen, dated snapshots** (Scopus 2026-06-20; OpenAlex 2026-06-22) | Reproducibility against live DBs | Re-query at write-up | |

## C. Screening

| # | Decision | Why | Alternative | Your call |
|---|---|---|---|---|
| C1 | **LLM-assisted dual screening**, recall-protective (uncertain → MAYBE) | Volume (22k) infeasible solo by hand; protect recall | Hand-screen a sample only | |
| C2 | **Validated on 40-case gold set + 300-record exclusion audit (0 leaks); κ = 0.89** | Bound the screening error | Trust single pass | |
| C3 | **Snowball stream screened with same criteria** (1,818 → 331 advancing) | Consistency across streams | Separate criteria | |
| C4 | **Full-text via OA + library + Sci-Hub** (author-authorised); ~73% obtained | Maximise retrieval; rest = documented limitation | OA-only | |
| C5 | **Dual-reader verification tightened includes 635 → 535** (−16% over-inclusion) | Single-screener over-includes; adjudication corrects | Keep single-screen includes | |

## D. Extraction & coding

| # | Decision | Why | Alternative | Your call |
|---|---|---|---|---|
| D1 | **Estimate-level unit** (study × country × platform × measure) | Preserves within-study variation = the thesis; your JQD = 8 rows not 1 | One headline estimate per study (the v1 error we fixed) | |
| D2 | **Granularity ceiling = country × platform × measure** (subgroup/time only if trivial) | Tractable; deeper splits need full text throughout | Also split by demographic subgroup & time wave | |
| D3 | **Full-text truncated to ~12k chars** for extraction | Token cost | **Un-truncated / grep-whole-text — OPEN, see I2 (biggest accuracy gap)** | |
| D4 | **Full double-extraction** (all 793 re-extracted independently); 80% value-accurate; κ=0.82 | Gold-standard reliability | Sample-verify only (26%, what we had before) | |
| D5 | **Disagreements reconciled "second-reader-wins"** | Pragmatic | **Third-pass adjudication — OPEN, see I3** | |
| D6 | **Drop values that are secondary citations** (e.g. a paper quoting Allen's 0.15%) | Avoid double-counting famous numbers | Keep all reported numbers | |

## E. Construct taxonomy & falsity–quality rule

| # | Decision | Why | Alternative | Your call |
|---|---|---|---|---|
| E1 | **6 constructs** (CONTENT, RECALL, EXPOSURE, SHARING, CONCENTRATION) **+ 2 excluded** (QUALITY, BELIEF) | The conflation is the paper; the taxonomy operationalises it | Fewer/coarser categories | |
| E2 | **CONTENT only if verifiable falsity vs external ground truth**; usefulness/quality/guideline ratings → QUALITY (excluded) | A low-quality item isn't necessarily false | Count quality scores as content prevalence (inflates ~+5–10pp) | |
| E3 | **EXPOSURE split: whole-diet vs topical** | Denominators differ by orders of magnitude | Single EXPOSURE category | |
| E4 | **Borderline falsity/quality flagged** → sensitivity analysis | Transparency on the fuzzy boundary | Force a binary call | |
| E5 | **QUALITY + BELIEF excluded from prevalence** medians | Not prevalence of falsity | Include them | |

## F. Risk of bias

| # | Decision | Why | Alternative | Your call |
|---|---|---|---|---|
| F1 | **5-dimension appraisal** (denominator, sampling, definition, measurement, sample size) → overall low/mod/high | No standard RoB tool for prevalence-of-misinfo; built one fit to the constructs | Adapt an existing prevalence-RoB tool (e.g. JBI) | |
| F2 | **Per-study appraisal, mapped to estimates** for the cross-tab | RoB is a study property | Per-estimate appraisal | |
| F3 | **Reliability-checked on a blind subsample** | Bound RoB subjectivity | Single pass | |

## G. Synthesis & analysis

| # | Decision | Why | Alternative | Your call |
|---|---|---|---|---|
| G1 | **NO pooled meta-analytic prevalence**; medians/IQR *within* construct | Pooling heterogeneous constructs reproduces the conflation we critique | Random-effects pooled estimate | |
| G2 | **Unweighted medians** | Simple, robust to outliers; sample sizes span orders of magnitude | Sample-size or precision weighting — **OPEN, see I4** | |
| G3 | **Heterogeneity (platform/country/definition) described, not averaged away** | It's a finding | Treat as nuisance variance | |
| G4 | **Sensitivity analyses**: borderline-excluded; single- vs double-extraction | Show robustness | Report point estimates only | |

## H. Process & reproducibility

| # | Decision | Why | Your call |
|---|---|---|---|
| H1 | Every query a parameterised script; append-only log; git; keys in env vars only | Auditable for peer review | |
| H2 | Frozen snapshots + dated counts | Live-DB reproducibility | |

---

## I. Improvement options proposed 2026-06-22 — status as at 2026-09-14

The table below is the June list, kept verbatim. Six of the eight were run; the two that were not
are decisions in their own right. Status per option:

| # | status |
|---|---|
| I1 Web of Science | **NOT RUN**, by decision — no institutional access (documented limitation, §H). Two September top-up searches were run instead: an OpenAlex behavioural/preprint-venue query (5,382 net-new records, 20 studies) and a hand-run Google Scholar recall check (5 studies). |
| I2 Un-truncated re-extraction | **DONE, twice.** A 21-study truncation sensitivity on 2026-07-02 (omission, not corruption; 15 missed rows added at v1.2), then the 57-batch blind re-extraction of 2026-09, which read the whole archived text of every study in the corpus. |
| I3 Third-pass adjudication of double-extraction disagreements | **DONE in a stronger form.** Every disagreement raised by the independent-model cross-check and by the blind re-extraction went to the author for adjudication against the source paper: 592 rulings on 2026-09-08/10, plus the wave-2 disputes. |
| I4 Precision-weighted sensitivity | **DONE.** `data/synth/phaseB/precision_weighting.csv`, reported in Results and in the GRADE imprecision domain. |
| I5 Numeric / units audit | **DONE.** Every value with a reported numerator and denominator was re-derived; invariant 8 now blocks a mean-scale value entering the proportion pool. |
| I6 Deepen grey lit | **DONE as a parallel track, deliberately not co-equal.** Pre-specified producer list, 117 claims, each verified against the producer's own publication; never pooled with the corpus. |
| I7 Belief studies as an appendix | **NOT RUN**, by decision — the search string was never designed for belief, so the belief studies in hand are a biased sliver (§A). |
| I8 Country/platform metadata completion | **DONE.** `country_norm` is filled on 1,035 of 1,048 rows and `platform_norm` on 1,044; coverage panels by country and platform are generated per freeze. |

The June text follows unchanged.

| # | Option | What it would add | Effort | My rec |
|---|---|---|---|---|
| **I1** | **Add Web of Science** (+ optionally full OpenAlex search) | Higher recall; closes "single primary DB" critique | Medium–large (new screening campaign) | Optional; snowball already caught the big non-Scopus gaps |
| **I2** | **Un-truncated full-text re-extraction** (grep whole text, not first 12k chars) | Recovers estimates in results sections we couldn't see; fixes truncation-caused drops. **Biggest accuracy gain.** | Medium (~40 agents, but targeted to long/dropped papers) | **Recommend** — this is the real gap |
| **I3** | **Third-pass adjudication** of the ~150 double-extraction disagreements | Turns "second-reader-wins" into true gold-standard adjudication | Small–medium (~10 agents) | Recommend if targeting a methods-strict venue |
| **I4** | **Sample-size / precision-weighted** sensitivity on the medians | Shows headline isn't driven by many tiny studies | Small (deterministic) | Recommend (cheap, strengthens) |
| **I5** | **Numeric/units audit** of the 31 sub-1% values + range handling | Catches proportion-vs-percent slips | Small | Recommend (cheap) |
| **I6** | **Deepen grey lit** to a co-equal track (defined exhaustive producer list) | Lets us make stronger grey-lit claims | Medium | Only if grey lit becomes central |
| **I7** | **Belief studies as a documented appendix** (not in main synthesis) | Pre-empts "why exclude belief?" | Medium | Optional |
| **I8** | **Country/platform metadata completion** (many rows = 'overall') | Enables subgroup/heterogeneity analyses | Medium | Optional, for a richer results section |

---

## Sign-off
The June sign-off asked which of I1–I8 to run; the status table above records what was run. Six were
executed and the other two were decided against with a stated reason.

---

## SETTLED — 2026-08-10: study 85207525286 ("A1", the #adhdtest / ASRS study) is **QUALITY**

**Status: closed. Do not re-open without new evidence about the paper's own operationalisation.**

This row (value 92) has now been decided four times and flipped three, which is why it is being
written down rather than left to the next coder's reading of the word "misleading":

| when | call | on what basis |
|---|---|---|
| v1.6.4 | QUALITY → CONTENT | audit judgement |
| v1.6.8 | reverted to QUALITY | the Codex cross-check independently chose QUALITY |
| 2026-08-05 round | coder said CONTENT again | read the label "misleading" at face value |
| **2026-08-10** | **QUALITY, final (Sacha)** | the paper's operationalisation, quoted below |

**The deciding fact.** The study categorises a video as *"useful"* if its content contains
**"at least 4 out of the 6 questions on the ASRS-v1.1 screener"**; *"misleading"* is simply the
complement. A video can be **entirely true** and still be labelled "misleading" for covering only
three screener items. That is a coverage/completeness criterion, not a veracity one — so the row is
a QUALITY rating and is excluded from prevalence, and its `breadth` stays blank.

**The trap to avoid next time:** the paper's *label* ("misleading") looks like a veracity term and
matches a live `breadth` value, which is what pulled three separate readers toward CONTENT. Code the
**operationalisation**, never the label. Any future cross-check that flags this row should be
answered with this entry, not re-adjudicated.

---

## 2026-08-11 — QA-pass ruling: 85059494932 KEEPS political_news (CLOSED)

The Fable QA pass challenged the 10% row's `political_news` denom_class: the corpus was collected by
keyword search on the two 2016 candidates' names, which codebook rule 3 reads as `topical`.
**Sacha's ruling: keep political_news.** Rationale: during a presidential election, a
candidate-name-defined tweet universe IS the political-news stream; the authors built the corpus to
represent the full election conversation, not a topical slice of it. This was the only QA finding
that could have moved the whole-diet backbone (k 33→32). Any future cross-check that flags this row
should be answered with this entry, not re-adjudicated.

## 2026-08-11 — QA-pass ruling: Faker Island 0.05% is SHARING, scope news_diet + selection curated (CLOSED)

The 184M-tweet denominator (every tweet linking to 420 fact-checker-listed French outlets, posted by
3.7M accounts) is a stream of link-bearing posts by a class of actors → SHARING under rule a0-bis as
refined at v1.7.8. Denominator recorded on the two-axis taxonomy: scope stays news_diet (the outlet
universe is fact-checker-derived news media, not hand-picked — Sacha's note), selection = curated,
so denom_class = curated_sample. NB this settles THIS study only; the general link-bearing-posts
rule for the remaining 36 rows is still a declared open item.

## 2026-09-16 — wave-5 cross-check ruling: `W7117302408` breadth is `misleading` (CLOSED, applied at v1.7.22)

The wave-5 independent coder flagged our `false` on this survey's 69% exposure item. The paper's own
sentence is "About 69% of respondents indicated that **misleading or false** information circulating
on social media platforms created confusion", under a table row labelled "Exposure to misinformation
and fake news". A band that admits misleading content is `misleading`. **Their reading adopted**,
applied by `apply_v1722.py` as a one-cell edit. Effect: breadth's adjusted R² 12.2% → 12.3%, breadth
counts 186/155 → 185/156, no median moves.

## 2026-09-16 — wave-5 cross-check: `W7162938155` denominator class (CLOSED — keep `curated_sample`)

| | |
|---|---|
| **The row** | CONTENT, ~23% of 5,385 TikTok and Facebook user comments labelled hoax |
| **The denominator** | comments crawled via Apify, "restricted to discussions about the Prabowo-era government in Indonesia" |
| **Ours** | `curated_sample` |
| **Theirs** | `topical` |

There is no rank truncation and no seeding from known misinformation, so codebook rule 4 does not
fire, and the reading turns entirely on whether a national government is ONE issue (`topical`) or a
domain spanning several unrelated ones (`curated_sample`). The instructions' own "prefer the
narrower category" tie-break gives ours. **Nothing in the paper decides it**, which is why it came
here rather than being settled at the desk.

**Sacha's ruling, 2026-09-16: keep `curated_sample`.** No data change. The dissent stays on the
record in `data/extract_v2/qa/gpt_check_2026-09_wave5_adjudication.md`, so a future cross-check that
flags this row should be answered with this entry rather than re-adjudicated. One row, on the
moderator at the bottom of the variance ladder; changing it would have moved nothing the manuscript
reports.

## 2026-09-16 — wave-5 cross-check: does `W7171843315` belong in the CONTENT pool? (CLOSED — keep, and disclose)

| | |
|---|---|
| **The row** | CONTENT, 41.3% of 480 observed interactions carried a health-misinformation claim |
| **The denominator** | face-to-face community-health-worker home visits, 36 CHWs, eight health centres, six months |
| **Ours** | CONTENT |
| **Theirs** | OTHER |

Under denominator-sets-construct this is a share of communication events each individually judged,
which is what CONTENT means, and the row is coded `unit = item`, `classification_level = claim_level`,
`ground_truth = researcher_coding` consistently with that. But it is the only CONTENT study in the
corpus counting something that was never online: every other one counts posts, videos or articles.
The question is not the coding but the scope — whether an offline observational study belongs in a
corpus built from platform content. It is 1 of 275 CONTENT studies and moves no median either way.

**Sacha's ruling, 2026-09-16: keep it, and disclose it in the supplement.** The coding follows the
review's own rules, and dropping a study because its answer is awkward is worse than keeping one a
referee might query — but it should not be silent. Supplementary Note C now names it as the corpus's
only study of offline interpersonal transmission, and `check_manuscript_stats.py` asserts that
sentence, so it cannot be softened away in a later edit. No data change.
