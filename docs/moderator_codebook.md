# Moderator Codebook — methodological/definitional coding

Purpose: turn the paper's thesis ("methodological choices drive divergent prevalence
estimates") from an assertion into a **coded, testable** set of moderators for the
meta-regression. Six dimensions, each an explicit categorical column added to the
frozen dataset. All are **derivable from existing fields** (`misinfo_def`,
`definition`, `measure_type`, `denominator`, `source_quote`, `platform`, `country`) —
this is a coding pass, not a re-read.

**Process:** LLM codes each row from the existing text → **quote-anchored second-reader
verification** (same standard as extraction) → κ/AC1 on a blind subsample. Apply on the
**v1.2** rows (post-re-freeze). Every code must be justifiable from `source_quote` /
`misinfo_def`; when a row genuinely fits two, record `primary` + `secondary`.

---

## (a) `breadth` — how wide the "misinformation" net is
Ordered from narrowest to widest (this ordering IS a moderator — wider nets → higher %):

> ⚠️ **PARTLY SUPERSEDED by the v1.6.0 taxonomy overhaul (see the section at the end of this file).**
> `breadth` is now a **PURE veracity scale with THREE live values** — `fabricated` / `false` /
> `misleading` — and is **BLANK** whenever the definition sets no per-item veracity standard
> (source-reliability lists, quality ratings). The last two rows below are **RETIRED**: they were
> blanked in v1.6.0 (originals preserved in `breadth_legacy`) and do NOT appear in the frozen data.
> The source-vs-claim axis is `classification_level`/`ground_truth`; quality is the QUALITY construct.
> Do not hand these two codes to any coder or cross-check. (Note added 2026-08-04 after this stale
> table was copied into a blind cross-check's instructions and produced unmatchable codes.)

| code | means | tell |
|---|---|---|
| `fabricated` | invented/hoax content only | "fabricated", "hoax", "made-up" |
| `false` | verifiably false claims (checked against ground truth) | fact-check "false" verdicts, expert-judged incorrect |
| `misleading` | misleading / manipulated / missing-context, not outright false | "misleading", "manipulated", "lacks context" |
| ~~`unreliable_source`~~ | **RETIRED v1.6.0** — was: coded by SOURCE (not per-item falsity) | now → leave `breadth` blank; see `classification_level=source_level` |
| ~~`low_quality`~~ | **RETIRED v1.6.0** — was: quality/reliability rating, not falsity | now → leave `breadth` blank; see construct=QUALITY |

> **Grounding:** this scheme operationalises the (Mis)information Funnel (Nickl et al.
> 2025) and matches Part III of the cross-project definitional lit review, which supplies the
> citations (Wardle & Derakhshan; Rogers 2020; Nenno 2025; Budak 2024; Allen 2020/2024). That
> review lives outside this repository, in the shared hub at
> `Claude/knowledge/litreviews/litreview_misinfo_definitions.md` (iCloud); the repo's own
> definitional canon as it reached the manuscript is §1 of `docs/manuscript_draft.md`.
> The lit review IS the intro/justification for this coding; keep the two in sync.

## (a0-ter) QUALITY vs CONTENT — code the OPERATIONALISATION, not the label (2026-08-10)

A paper's word for its own category is not evidence of what it measured. Worked example, settled
after three flips (see DECISIONS_REGISTER, study 85207525286): the paper reports 92% of #adhdtest
TikToks as **"misleading"**, but defines *useful* as containing "at least 4 out of the 6 questions on
the ASRS-v1.1 screener" — so "misleading" means *covered fewer than 4 screener items*, and a wholly
TRUE video can be labelled misleading. Coverage/completeness → **QUALITY**, `breadth` blank, excluded
from prevalence.
Rule: read how the category was ASSIGNED. If a wholly true item could receive the label, it is not a
veracity judgement, whatever the label says.

## (a0-bis) CONTENT vs SHARING — ratified 2026-08-10 (Sacha)

Decide on the DENOMINATOR, never on the numerator's verb.
- the corpus is a stream of **sharing ACTS** (shares, retweets, link-bearing posts, engagement) -> **SHARING**
- the corpus is a set of **items that EXIST** (an outlet's or a person's own posts, articles, videos,
  search results) -> **CONTENT**, including when those items contain links.
- **One named actor's own output is CONTENT; a CLASS of actors measured by what they share is
  SHARING.** Sacha, first pass: "it's one person, what matters here is that people see it or not, not
  [the actor]" (Bolsonaro's own 100 tweets -> CONTENT). Refined 2026-08-10 after the rule was applied
  literally and swallowed studies of 945 politicians / 4,787 state legislators / parliamentary
  parties: "ok ok i guess it's sharing then, if the study describes it as such". Those are behavioural
  sharing RATES over a population of actors, not one person's output. Follow the study's own framing
  when the unit is a class of actors.
Applied in v1.7.4 to the 8 rows (of 100 source-level/domain-list rows) that disagreed with the rule;
the other 92 already complied.

## (a0) CONSTRUCT is set by the DENOMINATOR (governing rule — see `docs/construct_and_concentration_rules.md`)
The construct (CONTENT / EXPOSURE / REACH / SHARING / RECALL) is defined by the **universe the % is a
share OF**, not the numerator or topic. All content that exists → CONTENT; consumed (views/visits/
**clicks**/diet) → EXPOSURE; population reached ≥1 → REACH; **shared/engaged (reshares, likes, FB
engagement)** → SHARING; self-report → RECALL. FB/Twitter engagement = SHARING (content_share), NOT
OTHER. "% of shared links unreliable" = SHARING, not CONTENT. This IS the review's thesis. Ratified
2026-07-15. CONCENTRATION additionally carries `conc_unit` {user|source} (renamed from the draft individuals/news_source vocabulary; `bots` was dropped — bot concentration rows are typed by the account unit they measure) ×
`conc_dimension` {exposure|sharing}: keep individuals + news_source (labelled separately), DROP bots.
New fields: `conc_unit`, `conc_dimension`, `demographic_group` (age/party breakdowns — systematic pass).

## (a2) `classification_level` — source-level vs claim-level (ADD; Nenno 2025 ~10×)
Distinct from `ground_truth`. Nenno et al. (2025) find claim-level detection yields
~tenfold higher prevalence than source-level — so this is a first-order predictor and
must be its own column, not folded into breadth/ground_truth.
| code | means |
|---|---|
| `source_level` | domain/account reliability (NewsGuard, Grinberg lists) — a lower bound |
| `claim_level` | per-item text/claim classification (fact-check or classifier on content) |
| `mixed` | both used |

## (a3) `question_type` — existence / exposure / engagement (Budak 2024; González-Bailón 2024)
The three routinely-conflated prevalence questions; do NOT pool across them.
| code | means | maps to our `construct` |
|---|---|---|
| `existence` | misinfo present in the system (% of items) | CONTENT |
| `exposure` | misinfo people were exposed to / saw | EXPOSURE, REACH, RECALL |
| `engagement` | misinfo people interacted with (shared/liked/clicked) | SHARING |

## (b) `ground_truth` — how "misinfo" was adjudicated
| code | means | tell |
|---|---|---|
| `fact_checker` | fact-check verdicts / expert panel, claim-level | Snopes, PolitiFact, Décodex (claim), expert coders |
| `domain_list` | source/domain reliability list | NewsGuard, MBFC, Grinberg black/red/orange, Décodex (source) |
| `researcher_coding` | authors/trained coders per codebook | "trained coders", "we classified" |
| `crowd` | lay/crowd ratings | MTurk raters, community notes |
| `classifier` | automated ML / suspicion score | "classifier", "model-labelled", "suspicion score" |
| `self_report` | respondent reports seeing/recalling (RECALL) | survey "have you seen…" |

## (c) `unit` — what is counted (numerator/denominator object)
| code | means |
|---|---|
| `claim` | individual claims/statements |
| `item` | content items (posts, videos, articles, tweets) |
| `url` | links/URLs to sources |
| `account` | users/accounts (producer side; concentration) |
| `person` | survey respondents / panel individuals (exposure, recall, reach) |
| `exposure` | impressions / views / exposure-events |

## (d) `denom_class` — the denominator the % is a share OF

> **This is the most consequential field in the codebook.** The review's entire thesis is that the
> denominator, not the phenomenon, drives the number. Code it wrong and the central analysis is wrong.
> Revised 2026-07-23 (v1.5.1) after a cross-model check found news-wide denominators split across two
> categories; `news_diet` was added to fix it.

### The one question
**If this percentage were 100%, what would that mean?** The answer names the denominator. Code what the
percentage is a share OF — never the topic, never what is being counted in the numerator.

### The seven categories

| code | the denominator is… | canonical examples |
|---|---|---|
| `population` | **PEOPLE** — a defined group of persons | "% of respondents who saw…", "% of panellists who visited ≥1" |
| `all_media` | **ALL MEDIA** one person consumed, news *and* non-news | "% of total daily media consumption (TV+desktop+mobile)", "total connected time", "all Facebook pages liked" |
| `news_diet` | **ALL NEWS** consumed, not restricted by topic | "% of all news web traffic", "all news website visits", "news diet of the median participant" |
| `political_news` | **POLITICAL/ELECTION news** only | "URLs shared under 2016 election hashtags", "posts by politicians", "hard political news" |
| `topical` | content on **ONE ISSUE** (a keyword/hashtag corpus) | "COVID-keyword tweets", "#vaccine videos", "search results for 'chemtrails'" |
| `curated_sample` | a **HAND-PICKED** set with no natural total | "the 500 most-shared posts", fact-check-seeded item sets |
| `single_source` | **ONE** account, channel, outlet or platform feature | "posts by @account", "one subreddit", "one broadcaster's transcripts" |

### Decision tree — apply in this order, stop at the first match

1. **Is the % a share of PEOPLE?** → `population`. (This beats every rule below. If it were 100%, every
   person would qualify.)
2. **Is the denominator someone's own consumption stream?** If yes, ask how wide:
   - includes non-news media → `all_media`
   - all news, any topic → `news_diet`
   - only political/election news → `political_news`
3. **Was the set assembled by searching one topic?** → `topical`
4. **Was the set hand-picked, or seeded from already-known misinformation?** → `curated_sample`
5. **Is it one account / channel / outlet?** → `single_source`

### The distinction that matters most: `all_media` vs `news_diet` vs `political_news`

These three differ **by roughly twenty-fold on the same phenomenon**, and that gap is one of the
review's clearest results. Do not blur them.

| | denominator | typical value |
|---|---|---|
| `all_media` | everything a person consumed, incl. entertainment and non-news | ~0.15% |
| `news_diet` | all the news a person consumed | ~3.4% |
| `political_news` | the political news specifically | higher still |

The misinformation is the same. Only the denominator changed. **A study is `all_media` only if non-news
media are genuinely inside the denominator.** "All news traffic" is `news_diet`, however comprehensive it
sounds — "all" refers to all *news*, not all *media*.

### Rules for the recurring hard cases

**Surveys and self-report → `population`, always.** The denominator is *who was asked*, not what they
were asked about. "38% of respondents said they had seen false claims about COVID" is `population`. It
is **not** `topical` because the question named COVID — topic is already captured by the `topic`
moderator, and coding it here double-counts it. Same for REACH ("% who visited ≥1 unreliable site"): the
denominator is the people observed, however narrow the thing being counted.

**"Most-shared" as a sampling method → `curated_sample`, not `news_diet`.** Selecting the top-N by
engagement produces a hand-assembled set with no natural total.

**A platform-wide census is not `all_media`.** "All tweets mentioning X" is `topical`; "all posts on one
platform" is `single_source` unless that platform genuinely represents the person's whole diet.

**A misinformation-weighted retrieval instrument makes the denominator `curated_sample`, however
large the corpus.** If the keyword/query list used to build the corpus deliberately includes
misinformation-associated terms, the denominator is tilted toward misinformation by construction, and
no amount of size or probability-sampling downstream repairs it. `topical` requires a
*topic-neutral* query set on a *single* issue. (Added 2026-07-23 after the second-opinion re-check of
2603.11058, whose keyword list was ~half "ambiguous and misinformation-related terms".)

**Numerator-building vs denominator-defining (the distinction the v1.5.4 adjudication converged on).**
A misinformation-weighted or rank-truncated instrument that builds the *numerator* over a clean
single-issue denominator stays `topical`; it becomes `curated_sample` only when the truncation, seeding
or multi-topic scope defines the *sampled set itself*. Example: a topic-neutral Boolean search for all
1.3M COVID-vaccine articles, with a misinfo classifier applied only to find the false ones, is
`topical` (the denominator is all vaccine articles). But "the 5,000 most-retweeted Zika tweets" or "the
top-100 links by engagement" is `curated_sample` (rank truncation defines the set). Ask: is the
selection building the numerator, or defining the denominator?

**A keyword corpus spanning several unrelated issues is not `topical`.** That category is defined as
content on ONE issue. Absent a person's consumption stream, a multi-domain keyword corpus falls to
`curated_sample`.

**When two readings are defensible, prefer the NARROWER category** and record the reasoning in
`moderator_quote`. Over-claiming a whole-diet denominator inflates the review's most important cell.

### Relationship to the whole-diet backbone
The backbone (the review's cleanest audience-diet designs) is
`denom_class ∈ {all_media, news_diet, political_news, population}` combined with a behavioural
construct. Adding `news_diet` **does not change backbone membership** — it subdivides it — so headline
values are unaffected. What changes is that the moderator analysis can now separate the three widths
instead of confounding them.

### Superseded field
`denom_type` (5 values, v1.2-era) is retained but **not canonical**; it disagrees with `denom_class` on
80 rows (`qa/v150_denom_conflicts.csv`). Use `denom_class` for all analysis.

## (e1) `platform_norm` — canonical platform (collapse the 140 raw values)
`Twitter/X, Facebook, YouTube, TikTok, Instagram, WhatsApp, Telegram, Reddit,
Google Search, web_cross_platform (tracking/browsing), survey, multi_platform, other`.

## (e2) `sampling_frame` — how the data were drawn
| code | means |
|---|---|
| `keyword_topical` | keyword/hashtag search |
| `random_platform` | random / representative platform sample |
| `panel_trace` | behavioural panel / web-tracking / voter-file panel |
| `survey_sample` | survey respondents |
| `curated_seed` | fact-check-seeded / known-misinfo list |
| `full_census` | full firehose/decahose/platform census |
| `convenience` | MTurk / convenience / non-representative |

## (f) `country_norm` + `country_scope`
- `country_norm`: canonical name; collapse "USA"↔"United States"; use "Multi-country"
  for enumerated multi-nation, "Global" for worldwide/unspecified.
- `country_scope`: `single` / `multi` / `global`.

---

## Dimensions added from the RA verification (Sacha, 2026-07-14) — see `RA_package/round1_2026-07/verification_implications_and_rules.md`

## (g) `population_scope` — WHOSE misinformation this is (R2)
Specific-population estimates are KEPT, not dropped — but tagged and reported separately from
general public. (~14 studies.)
| code | means | tell |
|---|---|---|
| `general_public` | general population / representative panel / open platform audience | default |
| `elite_politician` | politicians, candidates, MPs, party accounts | "members of Congress", "politicians' posts" |
| `professional` | defined professional group | pharmacists, physicians, journalists |
| `other` | any other bounded population | students, one country's diaspora, etc. |

## (h) Multiple estimates per study — NO primary/secondary hierarchy; just flag definition-variants (R4/R4a)
No one-estimate-per-paper rule, and no "primary vs secondary" ranking. Most studies contribute several
**co-equal** estimates that all matter equally and all enter the analysis — e.g. Altay/Nielsen/Fletcher
2022 = 4 countries × 2 constructs (EXPOSURE, SHARING) = **8 co-equal estimates**. Keep every
clearly-reported, high-confidence DISTINCT estimate; collapse only redundant demographic subgroups and
time-series (pick one representative point). One estimate we're 100% sure of beats ten unsure ones.
- The pooled median de-duplicates to **one estimate per (study × construct × country × platform) cell.**
  Co-equal estimates live in different cells, so they all enter — nothing to flag.
- **The ONLY flag needed: `definition_variant` (bool).** TRUE when an estimate is a stricter/broader
  *definition* of another estimate in the SAME cell (e.g. #4 "entirely false" 27% vs "contains any"
  79%; source-level vs content-level of the same quantity). Definition-variants are all KEPT and are
  central to the breadth analysis (R4b), but for the single pooled median only ONE per cell is used
  (at a fixed reference breadth) so a study isn't double-counted. Each variant keeps its own `breadth` /
  `classification_level` code.

## (i) `exposure_type` — proportion vs intensity (R5)
Only for EXPOSURE. Intensity measures are NOT prevalence proportions and stay out of the %-headline.
| code | means |
|---|---|
| `proportion` | % of diet / % of people (a share) — the headline-eligible form |
| `intensity` | mean/median count (mean sites visited, mean stories read) — side-bucket only |

## (j) `sharing_subtype` — actor-share vs content-share (R6)
Only for SHARING. (Largely derivable from `unit`: account→actor_share, item/url→content_share — but
make it explicit + audit all 56 SHARING rows.)
| code | means |
|---|---|
| `actor_share` | % of users/accounts who shared any misinfo |
| `content_share` | % of shared content (posts/links/engagement) that is misinfo |

## (k) `within_misinfo_content` (bool) — the appendix bucket (R3)
`TRUE` when a study reports content-level falsity WITHIN a sample defined by misinfo source
(low-quality/misinfo sites). Excluded from the main prevalence; retained for a brief appendix analysis
(`data/extract_v2/within_misinfo_content/`). NOT a headline estimate.

## CONCENTRATION extraction rule (R1)
CONCENTRATION is EXEMPT from the "within-misinfo → drop" rule (that rule is only for CONTENT
prevalence). Audience/user/sharer concentration is valid even inside a misinfo-only sample. Every
concentration estimate MUST carry BOTH: `conc_group_pct` (group size as % of the population/users,
e.g. "1% of users") AND `conc_share_pct` (the % of content/exposure they account for, e.g. "70%"). A
bare count without the population denominator ("top 35 accounts = 28.6%") is UNUSABLE → re-extract the
denominator or drop.

## Breadth is a HEADLINE, not just a covariate (R4b)
Because this is a prevalence review, **the spread of estimates across definition strictness is a
headline finding.** Keep same-quantity estimates reported under multiple definitions (fabricated/false/
misleading; source vs claim level; entirely vs contains-any), each tagged with its `breadth` +
`classification_level` code — do NOT collapse. Report prevalence **stratified by breadth** as a primary
result, alongside the single pooled median (which fixes one reference breadth per study).

---

## New columns to add
`breadth, breadth_secondary, ground_truth, unit, denom_class, platform_norm,
sampling_frame, country_norm, country_scope, moderator_coder, moderator_quote,
population_scope, exposure_type, sharing_subtype, within_misinfo_content,
definition_variant, conc_group_pct, conc_share_pct`
(`moderator_quote` = the verbatim snippet justifying `breadth`+`ground_truth`, for audit.)

## Why this is the analytic backbone
The headline meta-regression regresses `value_pct` on these moderators (esp.
`breadth`, `ground_truth`, `denom_class`, `unit`) within/across construct — that is
the quantitative demonstration of "definitions drive the numbers." Without these
coded, the thesis is only illustrated by anecdote (the CONTENT-vs-EXPOSURE contrast),
not modelled.

---

## Denominator-class rules added 2026-07-23 (from the cross-model check)

The Perplexity/GPT-5.6 cross-model pass disagreed with our `denom_class` on the same study three
times in the same direction. Investigating proved it right: **we were labelling the same kind of
denominator two different ways.**

### (i) RESOLVED (v1.5.1) — news-wide denominators are split across two labels [`news_diet` was added as recommended below; kept for the reasoning]

`all_media` currently contains *"all news website visits 2017"* while `political_news` contains
*"% of all news web traffic (visits to news websites)"*. Same quantity, different bin.
**11 rows / 5 studies affected** — worklist: `data/extract_v2/qa/v150_newsdiet_worklist.csv`
(W4293124965 x4, W7146985142 x2, 85209547248, +3).

This matters more than the row count suggests, because the denominator IS the paper's argument.
`all_media` also holds genuinely whole-media denominators (*"total daily media consumption
(~460 min/person/day across TV, desktop, mobile)"* — the Allen 2020 design giving ~0.15%), whereas an
all-**news** denominator gives ~3.4% on the same phenomenon. That is roughly a **20x difference driven
purely by the denominator** — exactly the effect the review exists to document. Merging the two would
destroy the paper's single cleanest illustration of its own thesis.

**RECOMMENDATION (needs Sacha's call): add a third category `news_diet`.**
- `all_media` = the person's ENTIRE information/media consumption, news and non-news (TV + web +
  mobile; total connected time; all Facebook pages liked).
- `news_diet` = ALL news consumption, not restricted by topic (all news website visits; all news
  web traffic; "news diet of the median participant").
- `political_news` = news restricted to POLITICS/elections (election-hashtag URL sets, politician
  posts, hard political news).

All three remain inside the whole-diet backbone set, so **the backbone median (7.5% at the time of writing; resolve the current value from the pipeline) and every headline
number are unaffected** — this is a moderator-resolution fix, not a value fix. The recode is 11 rows,
deterministic, and lands as v1.5.1. ALTERNATIVE if Sacha prefers no new category: fold the 9 news-wide
`political_news` rows into `all_media` and rename the concept in the paper — cheaper, but it puts the
0.15% all-media and 3.4% all-news designs in the same bin and blurs the 20x contrast.

### (ii) RULE (settled) — survey/self-report denominators are the POPULATION, not the topic

For RECALL and any self-report estimate, `denom_class` describes **who was asked**, not what they were
asked about. "% of respondents who report seeing COVID misinformation" is `population` — the percentage
is a share of respondents. It is NOT `topical` merely because the question named a topic.

The cross-model pass coded three such rows `topical` where we have `population` (A18, A27, A28). Our
convention is correct, but it was **written down nowhere a coder could find it**, so the disagreement was
our documentation failing rather than the other rater. Topic is already captured by the `topic`
moderator; `denom_class` must not duplicate it.

Corollary: the same applies to REACH ("% of people who visited >=1") — the denominator is the population
observed, regardless of how narrow the content being counted is.

## Hard boundary (documented): topical vs curated_sample

`denom_class` forces two axes into one field: SCOPE (topical → political_news → news_diet →
all_media → population) and SELECTION BIAS (curated_sample, single_source). A curated sample of
single-issue content is genuinely BOTH; the field records one. Precedence rule: when the sample was
selection-shaped (top-N, most-viewed, first-page, rank-with-threshold), code `curated_sample` —
the selection bias is the more decision-relevant fact for reading the number; the topic is kept in
`topic`. `topical` requires an exhaustive, topic-neutral query on a single issue.
NB (2026-07-30): this boundary was the dataset author's most frequently-questioned rule across the
human IRR (raised on three separate items), and it produced the field's and our pipeline's dominant
coding error. It is intrinsically hard, not a labelling accident — worth a sentence in the paper's
limitations. Borderline calls (e.g. a low view-count threshold as inclusion filter vs set-defining
truncation) are legitimately author-adjudicated; see v1.5.8 E03.

## v1.6.0 taxonomy overhaul (2026-07-30)

**DEPRECATED (retained in CSV for provenance, dropped from analysis):**
- `question_type` — redundant with `construct` (existence≈CONTENT, exposure≈EXPOSURE/REACH/RECALL,
  engagement≈SHARING) plus a drift tail. Do not use.
- `diet_type` — never a controlled vocabulary (60+ free-text values). The whole_diet/topical signal
  it aimed at lives in `denom_scope`. Do not use.

**BREADTH is now a PURE veracity scale:** {fabricated, false, misleading}. `unreliable_source`
(a judgment-unit, duplicated `classification_level=source_level`) and `low_quality` (QUALITY
construct) were blanked; originals in `breadth_legacy`. The breadth moderator now measures veracity
strictness only; the source-vs-claim axis is `classification_level`/`ground_truth`; quality is the
QUALITY construct.

**DENOMINATOR is now two clean axes** (the old `denom_class` retained for back-compat):
- `denom_scope` = scope only {topical, political_news, news_diet, all_media, population, n/a}.
- `denom_selection` = selection-bias axis {'', curated, single_source}.
A curated top-N single-issue study is `denom_scope=topical` AND `denom_selection=curated` — both
recorded. NB: when the two axes were split, `denom_scope` on the rows carrying a `denom_selection`
was RULE-INFERRED from `topic` (general_news→news_diet, politics→political_news, else→topical).
That inference was provisional when written; it was checked at v1.6.1, re-checked by the v1.7.9 QA
pass, and the human value-verification round read the denominator of 221 estimates against the source
papers, so it is analysis-grade. 243 rows now carry a `denom_selection` (curated 214,
single_source 29).

**Six included constructs** (framing corrected): CONTENT, EXPOSURE, REACH, SHARING, RECALL,
CONCENTRATION (+ excluded QUALITY, OTHER). SHARING = CONTENT computed over a sharing stream
(% of *shared* items false) vs CONTENT (% of *all* items false) — kept distinct because the
sharing universe is a behaviourally reported quantity. REACH and RECALL share the *people*
denominator and differ by measurement (behavioural vs self-report) — that difference is the
exposure–perception gap itself.

## Concentration: volume-percentile vs qualitative-group (v1.6.5)

The top-X%→Y% CONCENTRATION headline (top-1% band; resolve the current median/k from concentration_by_threshold.csv, which reads 70.0% over 5 studies for the exact top-1% band at v1.7.20) pools ONLY genuine volume-percentile
studies (a % of users defined by activity rank → a % of activity). Some CONCENTRATION rows report a
QUALITATIVELY-defined group's share (verified accounts, top-N accounts/sources, a deplatformed set,
a single named actor) — these have `conc_group_pct` BLANK on purpose and carry a descriptive
`conc_group_label`; they must NOT be forced into a percentile band. Single named actors (e.g.
@RobertKennedyJr) are OTHER, not CONCENTRATION (v1.6.4).
