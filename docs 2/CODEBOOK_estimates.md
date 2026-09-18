# Codebook — the frozen estimates dataset

Every one of the **57 columns** of the frozen CSV named on the `File:` line of the top block of
[`FROZEN.md`](FROZEN.md). Counts and vocabularies below are as at **v1.7.23** (1,048 estimate rows /
443 studies); the codes are stable across freezes, the counts are not.

One row is **one estimate**: a study × country × platform/source × construct × measure combination.
There is no primary/secondary hierarchy — most studies contribute several co-equal rows, and they
all enter the analysis. `docs/estimate_selection_rule.md` governs which value is taken when a paper
offers several *within* one such cell.

This file is the column-by-column reference. The rules behind the judgement-heavy fields live in:

- [`moderator_codebook.md`](moderator_codebook.md) — the moderator scheme, the denominator decision
  tree, and the v1.6.0 taxonomy overhaul. **The live rules; read its end-of-file refinements.**
- [`construct_and_concentration_rules.md`](construct_and_concentration_rules.md) — the governing
  "denominator sets the construct" rule (partly superseded; see its banner).
- [`topic_taxonomy.md`](topic_taxonomy.md) — the 12 topic codes.
- [`DECISIONS_REGISTER.md`](DECISIONS_REGISTER.md) — every contested call and how it was settled.
- [`extraction_protocol_v2.md`](extraction_protocol_v2.md) — how a row gets extracted in the first place.

Nine of these columns are enforced mechanically by `scripts/check_invariants.py`, whose non-zero
exit blocks a freeze. Those are flagged **[inv]** below.

**Blank is meaningful, and it is not the same as `n/a`.** A blank means the field does not apply to
that row or the source does not say; the literal string `n/a` appears only in `denom_class` /
`denom_scope`, where it marks CONCENTRATION rows that have no denominator by construction.

---

## A. Identity and provenance

| column | filled | definition |
|---|---:|---|
| `id` | 1048/1048 | Study identifier, and the unit of clustering in every model. Format follows the stream that supplied the record: `2-s2.0-<EID>` (Scopus, 836 rows), `W<id>` / `OA-W<id>` (OpenAlex, 142), `PMID-<id>` (PubMed, 8), a bare arXiv id (10), `scholar_<nn>` (the September Google Scholar recall check, 24), `SEED-<author><year>` (Berriche seed corpus, 9) or `NEW-<author><venue>` (hand-added grey and late acquisitions, 19). Rows sharing an `id` are the same study and are **not** independent. |
| `source` | 1048/1048 | Which retrieval and extraction pass produced the row, so an estimate's evidentiary basis is visible without reading the log. 26 values, the largest being `full_text_stepb` (351), `full_text_repair_2026-09` (284), `full_text_upgraded` (77), `wave3_value_verification_2026-09-07` (49), `behavioural_arm_2026-09` (35), `blind_reextraction_2026-09` (34), `full_text` (33), `full_text_rev2` (30), **`abstract` (29 rows from 25 studies — the appraisal was made from the abstract only; §4 reports these separately)**, `scholar_arm_2026-09` (24), plus per-study re-extraction tags (`reextract_lyons_verified`, `reextract_figeac_parties`, …). |
| `data_provenance` | 559/1048 | The campaign that added or last substantively touched the row: `corpus_repair_2026-09:stage2_title:ELIGIBLE` (220), `demographic_pass_2026-07-15` (42), `corpus_repair_2026-09:stage1_abstract:UNSURE` (37), `full_text_reextract_2026-07-15` (31), `corpus_repair_2026-09:stage1_abstract:ELIGIBLE` (27), … Blank on rows that entered at the original v1.1/v1.2 extraction and were never re-touched. A minority of rows use it to name the data source rather than the campaign (`NewsGuard`, `YouGov-Pulse`); read it as provenance, never as a quality rating. |
| `moderator_coder` | 1046/1048 | Who assigned the moderator codes, and when: `llm_batch_2ndreader_2026-07` (515), `opus_repair_2026-09` (284), `claude_wave3_2026-09` (72), `llm_reextract_2026-07-15` (39), `claude_behavioural_arm_2026-09` (35), `claude_blind_2026-09` (34), `gpt_blind_2026-09_promoted` (12), `author_extraction_2026-07-30` / `_2026-09-02` (7, Sacha's own). Names the *instrument*, which is what a same-family-vs-independent-family reliability argument turns on. |
| `confidence` | 979/1048 | The extractor's confidence that this row's value and typing are right: `high` (633), `medium` (321), `low` (25). Used in sensitivity analyses, never to weight the headline. |
| `flag` | 885/1048 | Free-text audit note attached to the row: page/table location, caveats ("reach, not diet-share"), recode history ("OTHER->CONCENTRATION_v1411"), the arm that found it ("behavioural arm (OpenAlex method-term search)"), non-independence warnings. Not a controlled vocabulary and **never** used for filtering by any analysis script — anything an analysis needs to know has its own column. The literal token `abstract_only` appears here on 29 rows and duplicates `source == "abstract"`. |

## B. Study descriptors

| column | filled | definition |
|---|---:|---|
| `country` | 1029/1048 | Country as the paper writes it. Free text, 219 distinct values including near-duplicates (`United States` 204, `USA` 68 and `US` 38 all appear). **Do not group on this column.** |
| `country_norm` | 1035/1048 | Canonical country. 69 values. `USA`↔`United States` collapsed; `Multi-country` for an enumerated set of nations (67), `Global` for worldwide or unspecified (147). This is the analysis column. |
| `country_scope` | 1004/1048 | `single` (789) / `global` (141) / `multi` (74). |
| `platform` | 1041/1048 | Platform as the paper writes it. Free text, 274 distinct values. **Do not group on this column.** |
| `platform_norm` | 1044/1048 | Canonical platform, 17 values: `Twitter/X` (249), `survey` (139), `web_cross_platform` (114, tracking/browsing panels), `Facebook` (105), `YouTube` (95), `multi_platform` (93), `other` (87), `TikTok` (66), `Instagram`, `Google Search`, `Reddit`, `WhatsApp`, `Bing`, `Telegram`, `4chan`, `Instagram Reels`, `YouTube Shorts`. `scripts/phaseB_platform_construct.py` owns the raw-string classifier (`labels_for()`); figures and the manuscript checker import it rather than reimplementing it. For self-reported RECALL the platform is the survey question's frame, not a measured source. |
| `date` | 1005/1048 | The **data-collection** period, verbatim as reported: `2020-2021`, `February 2021`, `December 2019 - January 2020`, `2017`. Free text on purpose — collapsing it would destroy the ranges. Not the publication year. |
| `year` | 990/1048 | The data-collection **end year**, parsed from `date`. Added at v1.6.6 as a derived, analysis-neutral column. Range 1996–2026; mode 2020 (271) and 2021 (206). |
| `era` | 921/1048 | `year` banded for the temporal moderator: `<=2016` (78) / `2017-2019` (153) / `2020-2021` (446) / `>=2022` (244). Bands chosen around the 2016 election and the COVID period. Added at v1.6.6 with `year`. |
| `topic` | 1048/1048 | Subject-matter domain of the misinformation studied, one primary code per study, from the 12 in `topic_taxonomy.md`: `health_other` (275), `general_news` (257), `covid19` (231), `politics_elections` (189), `vaccines` (39), `other` (18), `war_geopolitics` (15), `science_other` (15), `crime_society` (7), `economy_finance` (2), and the unused `climate_environment` / `immigration`. COVID vaccines are `covid19`, not `vaccines`. A whole-diet or untrustworthy-domain-list study is `general_news`; do not force a subject onto it. |
| `population_scope` | 1048/1048 | Whose misinformation this is. `general_public` (932, the default), `elite_politician` (53), `other` (44), `professional` (15), plus two narrow legacy labels (`business_source_not_general_public` 3, `at_risk_nonrepresentative` 1). Specific-population rows are kept, not dropped, and reported separately. |
| `sampling_frame` | 1034/1048 | How the data were drawn: `keyword_topical` (446), `survey_sample` (157), `panel_trace` (151, behavioural/web-tracking/voter-file panels), `convenience` (119), `full_census` (92, firehose/decahose/platform census), `curated_seed` (35), `purposive` (28), `random_platform` (5), + one rare compound (`convenience_snowball`). One of the top variance-explaining moderators. |

## C. The estimate itself

| column | filled | definition |
|---|---:|---|
| `value_pct` | 1040/1048 | **The number the review is about**, on a 0–100 percentage scale. Blank where the paper reports only a non-proportion quantity. Never rescaled or transformed at extraction; the logit transform happens in the model. |
| `value_raw` | 935/1048 | The value as printed in the source, including fractions (`13/97`), ranges, counts (`top 15 accounts`) and prose. Kept so `value_pct` can be re-derived and checked. |
| `value_kind` | 1048/1048 | **[inv]** What kind of quantity `value_pct` is: `proportion` (1,038 — the only kind that enters a pooled statistic), `per_capita_intensity` (6, mean sites visited), `range_not_point` (4). The `scale_score` code is defined but now unused: the mean quality-scale rows it marked were removed from the corpus, and every QUALITY row still held is a proportion. Every pooled analysis filters `value_kind == "proportion"` explicitly. This column exists because two mean quality scores (4.818, 2.003) once sat in the percentage pool; an invariant now blocks that. |
| `measure_type` | 1048/1048 | Free-text statement of exactly what was measured, in the paper's own terms: *"share of shared COVID-19 URLs from fake-news domains, black+red (content-N = 7,062,989 tweets-with-URL)"*. 900 distinct values on 1,048 rows — it is a description, not a category. The categorical version of this information is spread across `construct`, `unit`, `classification_level` and `ground_truth`. Also the field `check_invariants.py` scans for stray mean-score language. |
| `n` | 999/1048 | The denominator's size, verbatim from the source, which is why it is a string and not a number: `1059`, `100 videos`, `1,500 respondents`, `7062989`. `phaseB_prep_regression.py` parses it with a strict K/M-suffix regex plus an 11-row hand-audited `N_OVERRIDES` table for strings whose first number is not the denominator. **When a row parses wrong, extend the override table; never loosen the regex.** Only rows with a parseable n enter I², the Spearman small-study test and the precision-weighted sensitivity. |
| `denominator` | 992/1048 | Prose description of the universe the percentage is a share of: *"7,062,989 COVID-19 tweets containing at least one URL (panel of 1.6M registered voters)"*. The evidence behind `denom_scope` / `denom_selection`. 803 distinct values. |
| `source_quote` | 1048/1048 | **The verbatim sentence from the paper that contains the number.** Mandatory on every row, and a single contiguous span (repaired corpus-wide by `scripts/repair_quote_integrity.py`). This is what makes every estimate re-checkable against its source, and it is the artefact every cross-check and IRR round was scored against. |

## D. Construct typing

| column | filled | definition |
|---|---:|---|
| `construct` | 1048/1048 | **[inv]** The review's central variable. **The construct is set by the DENOMINATOR** — the universe the percentage is a share of — never by the numerator or the topic. Six included: `CONTENT` (429, all content that exists), `RECALL` (255, self-report), `SHARING` (128, content shared or engaged with), `REACH` (106, people who encountered ≥1), `EXPOSURE` (46, content consumed — views, visits, clicks, diet share), `CONCENTRATION` (36). Two excluded from prevalence: `OTHER` (27) and `QUALITY` (21, source or content quality ratings that are not veracity judgements). Shortcut when unsure: *a share of what?* Constructs are reported separately and **never pooled** — I² is 99–100%. |
| `question_type` | 925/1048 | **DEPRECATED at v1.6.0; retained for provenance only. Do not use.** Was `existence` / `exposure` / `engagement`, which is redundant with `construct` (existence≈CONTENT, exposure≈EXPOSURE/REACH/RECALL, engagement≈SHARING) and has since drifted (`sharing` 11, `content` 8, `recall` 6, `concentration` 5, `reach` 1 appear in it). |
| `diet_type` | 262/1048 | **DEPRECATED at v1.6.0; retained for provenance only. Do not use.** Never had a controlled vocabulary — 55 distinct values on 262 filled rows, mixing `TOPICAL`/`WHOLE_DIET` with free text. The whole-diet-vs-topical signal it aimed at is now `denom_scope`. |
| `unit` | 1019/1048 | What is actually counted: `item` (430, posts/videos/articles/tweets), `person` (348, survey respondents or panel individuals), `url` (127), `account` (47), `exposure` (46, impressions/views), `claim` (12), plus 3 rare labels (`source`, `post`, `reach`). Distinct from `construct`: the unit is the object, the construct is the universe. |

## E. What counted as misinformation

| column | filled | definition |
|---|---:|---|
| `definition` | 1035/1048 | Short operational statement of the misinformation category **as this estimate used it**: *"black/red fake-news domain URLs per Grinberg classification"*. 782 distinct values. |
| `misinfo_def` | 1016/1048 | The paper's fuller definition, usually quoted: *"NewsGuard domain trust score < 60 (source/domain-level)"*. `definition` is the operational shorthand, `misinfo_def` the paper's own words. **Capped at 200 characters on 441 rows**, 430 of which end mid-word: the extraction stored only the first 200 characters, and the untruncated text is not recoverable without re-reading the sources. Use it as an indication of how a study defined misinformation, not as a complete quotation; `breadth` and `ground_truth` are the coded fields and are complete. |
| `breadth` | 667/1048 | **[inv]** How wide the veracity net is. Since v1.6.0 a **pure veracity scale with exactly three live values**: `fabricated` (42, invented/hoax only) / `false` (357, verifiably false against a ground truth) / `misleading` (268, manipulated or missing-context but not outright false). **Blank whenever the definition sets no per-item veracity standard** — source-reliability lists and quality ratings leave it blank; the source-vs-claim axis is `classification_level`, and quality is the QUALITY construct. Two invariants police this: only these three values or blank, and no QUALITY row may carry a breadth. Breadth is a *headline*, not just a covariate: same-quantity estimates under several definitions are all kept and reported stratified. |
| `breadth_legacy` | 955/1048 | The pre-v1.6.0 five-value breadth, preserved verbatim when the scale was narrowed: `false` (372), `unreliable_source` (292, retired), `misleading` (226), `fabricated` (42), `low_quality` (19, retired), plus two labels coined by later extraction passes (`ai_generated` 2, `harmful_channel` 2). Provenance only. **Never hand this vocabulary to a coder or a cross-check** — doing so once produced a batch of unmatchable codes. |
| `classification_level` | 1043/1048 | Whether misinformation was judged per source or per item. `claim_level` (696, per-item text or claim classification), `source_level` (339, domain or account reliability — a lower bound), `mixed` (3), plus 5 rows on rarer labels (`post_level`, `topic_level`, `self_perceived`). Its own column, not folded into breadth, because Nenno et al. (2025) find claim-level detection yields roughly tenfold higher prevalence than source-level. One of the top variance-explaining moderators. |
| `source_level` | 64/1048 | **Legacy v1.2-era boolean** (`TRUE` only) marking source-level classification, superseded by `classification_level == "source_level"`. Retained for provenance. Do not use for analysis. |
| `ground_truth` | 1048/1048 | How "misinformation" was adjudicated, on a 5-code controlled vocabulary: `researcher_coding` (397, authors or trained coders per a codebook), `domain_list` (312, NewsGuard, MBFC, Grinberg lists, Décodex-source), `self_report` (238, the respondent says they saw it), `fact_checker` (63, claim-level fact-check verdicts or an expert panel), `classifier` (38, automated ML or suspicion score). Normalised to these five at v1.5.0, when 14 rows held whole prose sentences as the category value and silently fragmented every groupby. **The single largest variance-explaining moderator**; the current R² and its bootstrap interval are in `data/synth/phaseB/metareg_r2_bootstrap.csv`, not here. |
| `ground_truth_detail` | 414/1048 | The free-text detail the normalisation would otherwise have destroyed: which list, which raters, what reliability. *"Hand-coded low-credibility health domains (2 coders, Krippendorff's alpha = 1.00)"*, `newsguard`, `domain_list (Decodex)`. Where a reader goes to see whether "researcher_coding" meant two trained coders or one author. |
| `moderator_quote` | 987/1048 | The verbatim snippet justifying the moderator codes — chiefly `breadth`, `ground_truth` and `sampling_frame`. The audit trail for the coding pass, in the same way `source_quote` is the audit trail for the value. |

## F. The denominator (two clean axes, plus two legacy fields)

The review's thesis is that the denominator, not the phenomenon, drives the number. Getting these
right is the whole argument. The decision tree, the hard cases and the twenty-fold
`all_media` / `news_diet` / `political_news` contrast are in `moderator_codebook.md` §(d).

| column | filled | definition |
|---|---:|---|
| `denom_scope` | 1048/1048 | **[inv]** SCOPE only, since v1.6.0: `topical` (458, content on one issue), `population` (371, a defined group of people), `political_news` (82), `news_diet` (59, all news regardless of topic), `all_media` (19, everything a person consumed including non-news), `n/a` (59, CONCENTRATION rows and the OTHER composition rows, which have no denominator by construction). Two invariants: every REACH row and every RECALL row must be `population` or `n/a` — for self-report the denominator is *who was asked*, never what they were asked about. |
| `denom_selection` | 243/1048 | **[inv]** SELECTION-BIAS axis, orthogonal to scope: `curated` (214, hand-picked, rank-truncated or misinfo-seeded), `single_source` (29, one account, channel, outlet or platform feature), blank otherwise. A curated top-N single-issue study is `denom_scope=topical` **and** `denom_selection=curated` — both are recorded, which the old fused field could not do. |
| `denom_class` | 1009/1048 | **[inv]** The **legacy fused** field, kept for back-compatibility and still the one several older scripts group on: `population` (344), `topical` (234), `curated_sample` (214), `political_news` (62), `n/a` (59), `news_diet` (51), `single_source` (29), `all_media` (16). Forces the two axes above into one column; an invariant asserts it stays consistent with them (`curated_sample`⇔`denom_selection=curated`, `single_source`⇔`single_source`, otherwise `denom_class == denom_scope` with no selection). It is **blank on 39 rows** added by the September passes, where `denom_scope` carries the coding and the fused field was never backfilled; group on `denom_scope` × `denom_selection` for new work and the blanks do not arise. |
| `denom_type` | 901/1048 | **SUPERSEDED v1.2-era field. Not canonical; do not use for analysis.** `population` (405), `topical` (329), `curated` (129), `single_source` (27), + 11 stragglers on four rarer labels. It genuinely **disagrees with `denom_class` on dozens of rows**, which is why it was kept rather than collapsed: the disagreement is evidence about how hard the boundary is (`data/extract_v2/qa/v150_denom_conflicts.csv`). |

## G. Construct subtypes

Each applies to one construct only, and is blank everywhere else.

| column | filled | definition |
|---|---:|---|
| `exposure_type` | 46/1048 | EXPOSURE only. `proportion` (40, a share — the headline-eligible form) / `intensity` (3, a mean or median count such as "mean sites visited") / `diet_share` (3, legacy label for a diet-share proportion). Intensity measures are not prevalence proportions and stay out of the percentage headline. |
| `sharing_subtype` | 126/1048 | SHARING only. `content_share` (115, % of shared content that is misinformation) / `actor_share` (11, % of users who shared any). Largely derivable from `unit` but made explicit, because the two answer different questions. |
| `reach_subtype` | 106/1048 | REACH only. What the person did at least once: `exposure` (61, saw or visited ≥1), `sharing` (40, shared ≥1), `liking` (5). Added at v1.4.1 so "% who did X at least once" rows are not pooled across different X. |
| `recall_subtype` | 255/1048 | RECALL only. What the respondent was asked to recall: `exposure` (166, "have you seen…") vs `sharing` (89, "have you shared…"). Added at v1.4.1/v1.6.6 after the outlier check found no misclassifications but did find this substructure — the medians differ substantially. Drives the seen-vs-shared split reported in §2.3 (`scripts/phaseB_recall_split.py`). |
| `other_subtype` | 28/1048 | OTHER only. What the excluded row actually measures, so the exclusions are legible rather than a black box: `spreader_makeup` (8), `source_domain` (5), `producer_party` (4), `audience_overlap` (2), `account_type` (2), `ai_provenance` (2), `harm_category` (2), `query_demand`, `community`, `country_composition` (1 each). Composition rows — "what share of misinformation spreaders were conservative" — are kept and reported separately, never mixed into prevalence. |
| `definition_variant` | 174/1048 | Marks an estimate that is a stricter or broader **definition** of another estimate in the same (study × construct × country × platform) cell — "entirely false" 27% beside "contains any" 79%, or the source-level and claim-level versions of one quantity. `TRUE` on 123 rows. A literal `False` appears on 51 rows, all from the two September passes (`behavioural_arm_2026-09` 26, `blind_reextraction_2026-09` 25), which filled the field rather than leaving it blank; **`False` and blank mean the same thing**, so test for the truthy value, never for non-emptiness. All variants are kept and are central to the breadth analysis; the single pooled median uses only one per cell, at a fixed reference breadth, so a study is not double-counted. |

## H. Concentration

`CONCENTRATION` rows answer a different question from prevalence — *does a small minority account
for most of it?* — and are typed on their own axes. An invariant requires every CONCENTRATION row to
carry `denom_class == "n/a"` **and** a non-blank `conc_unit` **and** a non-blank `conc_dimension`.

| column | filled | definition |
|---|---:|---|
| `conc_group_pct` | 32/1048 | The group's size as a percentage of the population or of all sources — the **X** in "the top X%". Values run from 0.0013 to 31.3; `1` is the headline band. **Deliberately blank** on the 7 CONCENTRATION rows whose group is defined qualitatively rather than by an activity percentile (see `conc_group_label`); those must never be forced into a percentile band. |
| `conc_share_pct` | 42/1048 | The percentage of activity, exposure or content that group accounts for — the **Y** in "→ Y% of activity". Both this and `conc_group_pct` are mandatory for a percentile-band row; a bare count with no population denominator ("top 35 accounts = 28.6%") is unusable and is either re-extracted or dropped. |
| `conc_unit` | 39/1048 | **[inv]** What is concentrated: `user` (31, people or accounts — the primary interest, and the only unit in the headline top-1% figure) or `source` (8, top domains or outlets). Filled on all 36 CONCENTRATION rows and on 3 OTHER composition rows. **Reported separately and never pooled**: "top 1% of users → 80% of exposure" is not comparable to "top 10 sources → 95% of tweets". Renamed from the draft `individuals`/`news_source` vocabulary; the `bots` category was dropped, and bot rows are now typed by the account unit they measure. |
| `conc_dimension` | 49/1048 | **[inv]** What the share is of. On the 36 CONCENTRATION rows: `sharing` or `exposure`. The other 13 filled rows are `OTHER` composition rows, which reuse the field to say what they are compositions of: `sharing` (6), `political_party` (4), `exposure` (2), `country` (1). Reading the whole column as concentration would silently mix composition into it — filter on `construct == "CONCENTRATION"` first. |
| `conc_group_label` | 20/1048 | Plain-language description of a **qualitatively defined** group, used exactly where `conc_group_pct` is blank: *"top-15 Twitter accounts (rank-truncated; mostly verified)"*, *"deplatformed users (0.23% of panel; selection-defined by moderation, not a volume percentile)"*, *"top 3 domains"*. Added at v1.6.5 so these rows stay in the dataset, and out of the percentile pooling. |

## I. Demographic breakdowns

Added by a systematic corpus-wide pass at v1.3 and extended in later freezes. A demographic row is a
co-equal row, not a replacement for the overall. `check_invariants.py`'s "main set" excludes any row with a
non-blank `demographic_group`, so these never inflate a headline median.

| column | filled | definition |
|---|---:|---|
| `demographic_group` | 104/1048 | The subgroup, as `dimension=label`: `party=Front National (FN, far right)`, `age=65+`, `political=Republicans`. Free text by design — the labels are the papers'. Non-blank marks the row as a breakdown. |
| `demographic_dimension` | 104/1048 | Which dimension the breakdown is on: `political` (71), `age` (19), `gender` (8), `education` (3), `office_level` (2), `community` (1). The groupable version of the prefix in `demographic_group`. Region and country breakdowns were deliberately set aside as geographic, not demographic. |
| `demographic_subtype` | 90/1048 | **The distinction that makes these rows readable**, and it is easy to get wrong. `per_subgroup_rate` (77) — the rate *within* that subgroup ("3.7% of over-65s' shared URLs were from fake domains"). `spreader_composition` (8) / `subgroup_composition` (1) — that subgroup's share *of* the misinformation ("over-65s were 60% of all fake-news sharers"). `overall` (2) — the all-groups figure kept alongside its breakdown. Two rows of one study (`scholar_04`) carry `older` / `younger`, which are age labels rather than subtypes and are a coding slip of the September passes; both are `age` breakdowns and read as `per_subgroup_rate`. A rate and a composition are not the same quantity and must not be plotted on one axis. |
| `political_orientation` | 80/1048 | Normalised political label for political breakdowns, so cross-country party names are groupable: `right` (31), `left` (19), `far_right` (11), `mixed` (9), `center` (7), `far_left` (3). Blank on non-political rows. |
| `intersection_duplicate` | 2/1048 | Marks a cell a paper reports **twice**, once in each of two crossed series. W4205602257 reports the same 3.7% as "political=Independent (age 65+)" in its political series and as "age=65+ (political independents)" in its age series. Both rows are kept — deleting either breaks a reported series — and the field carries `twin_of:<the other row's group>` so a demographic analysis can de-duplicate. The project's standard keep-and-flag convention. |

---

## Invariants (`scripts/check_invariants.py`)

Nine properties the taxonomy guarantees, so a violation is a coding error rather than a judgement
call. Each was added because it caught something real. Non-zero exit blocks a freeze.

1. `FROZEN.md`'s declared MD5 matches the file on disk.
2. `breadth` is one of the three live values, or blank.
3. No `QUALITY` row carries a veracity `breadth`.
4. Every `CONCENTRATION` row has `denom_class == "n/a"` and a typed `conc_unit` and `conc_dimension`.
5. `denom_class` agrees with `denom_scope` × `denom_selection`.
6. Every `REACH` row's `denom_scope` is `population` or `n/a`.
7. Every `RECALL` row's `denom_scope` is `population` or `n/a`.
8. No mean-scale value sits in the proportion pool.
9. No two rows are fully identical.

All nine hold on v1.7.23.

## Reading a row

To decide what a number means, read four fields in this order: **`denominator`** (what the
percentage is a share of), **`construct`** (which of the six questions that makes it),
**`misinfo_def`** (what counted as misinformation) and **`source_quote`** (the sentence it came
from). Everything else is a coded, groupable summary of those four.
