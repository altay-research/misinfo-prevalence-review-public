# Full blind re-extraction 2026-09 — screening and estimate extraction (one batch per agent)

You are the SECOND, INDEPENDENT extractor for a systematic review of the PREVALENCE, EXPOSURE,
SHARING and CONCENTRATION of misinformation. Each paper in your batch is in the review's corpus.
You are NOT told what the first extractor found, and you must not look for it: work from the text
file given, and nothing else (no web, no other file in the repository). Being right matters more
than agreeing with anyone. Your job, per paper, from its text ONLY: (1) decide eligibility from
scratch, (2) if eligible, extract EVERY distinct estimate as a row to the schema below, with every
moderator field filled. The moderators (ground_truth, classification_level, sampling_frame, topic,
denom_scope, breadth) matter as much as the values: code each one from the paper's own methods.

Some texts are an ABSTRACT only (text_status "abstract_only" in the manifest): extract what the
abstract supports and say so in text_status. Large texts: read in chunks (offset/limit). You need
the abstract, methods (sample, data source, how misinformation was defined and coded) and results
(the numbers with their denominators).

## 1. Eligibility (paper level)
"Misinformation" is broad: misinformation, disinformation, fake or false news, unreliable or
untrustworthy sources, junk news, inaccurate or misleading (health) content.

INCLUDE if the paper reports at least one quantitative share with a denominator for one of:
- RECALL: share of survey respondents who say they encountered / came across / were exposed to /
  received / SHARED misinformation (any wording, any window; "how often" scales count if a share of
  respondents above a threshold, or a share reporting any, is given). "Perceived amount of
  misinformation in one's environment" (a lot / some / none) counts. Belief in false claims does NOT.
- CONTENT: share of items in a sample (posts, videos, comments, articles, websites, search results,
  chatbot answers, ads) classified false, misleading, inaccurate, unreliable, or misinformation.
- EXPOSURE: share of what people saw / visited / consumed that was misinformation (logs, panels).
- REACH: share of people who encountered it at least once, from behavioural data.
- SHARING: share of shares / retweets / posts / links carrying misinformation, or share of users who
  shared it, from platform data (observed, not hypothetical).
- CONCENTRATION: a top group of users or sources accounting for a stated share of exposure/sharing.

EXCLUDE (give the ground): detection / classifier / modelling work; intervention, correction,
inoculation or fact-checking-EFFECT experiments; belief, susceptibility or discernment only;
hypothetical or experimental sharing INTENTIONS; reviews, commentary, theory; qualitative-only;
QUALITY-ONLY studies (see §3); all-false corpora with no denominator (fact-check sets, "419 fake
items"); scale MEANS only, with no share of respondents/items (e.g. "mean exposure 2.4 on 1–5"),
unless a share is derivable per R8 below; the text is not the paper named (say so: text_status).

A study whose AIM is something else (motivations, literacy, hesitancy) is still INCLUDED if a
descriptive share is reported anywhere (results table, sample description). Look for it.

## 2. Unit of analysis = the estimate. One row per distinct estimate.
One row per unique (country × platform/source × measure × definition variant). Split when the paper
reports separate numbers by country, platform or measure; NEVER invent sub-rows from a pooled number.
Collapse time series to one representative point (say which); keep the main figure rather than
demographic subgroups (record subgroup rows only when they are the paper's headline, e.g. by party).
R4: quality over quantity — one estimate you are certain of beats ten uncertain ones.
R8 (value keep rule): a value is kept if it is stated VERBATIM, or is an exact part/whole share from
verbatim counts with the same denominator (44/150 = 29.3%). NEVER keep a cross-category sum or a
complement you computed (100 − 56.5), a rounding, or a figure the paper cites from elsewhere.
R1: CONCENTRATION rows must carry BOTH conc_group_pct (the group as % of users/sources) AND
conc_share_pct (their share of exposure/sharing); a bare count of accounts is unusable.
R3: content falsity computed INSIDE a misinformation-only sample → within_misinfo_content=true
(kept, appendix only).

## 3. THE DENOMINATOR SETS THE CONSTRUCT (governing rule). Ask: a share of WHAT?
- all items that EXIST (an outlet's/person's/platform's posts, videos, websites, search results,
  chatbot answers) → CONTENT
- consumed (views, visits, clicks, diet share) → EXPOSURE (exposure_type proportion; a mean count
  of sites/stories is exposure_type intensity, value_kind per_capita_intensity)
- people reached ≥ 1, behavioural → REACH (reach_subtype exposure | sharing | liking)
- shared / engaged (reshares, retweets, likes, engagement) → SHARING (sharing_subtype content_share
  = % of shared items that are misinfo; actor_share = % of users who shared any)
- self-report → RECALL (recall_subtype exposure | sharing)
- top X% → Y% of activity → CONCENTRATION (conc_unit user | source; conc_dimension exposure | sharing)
"% of shared links unreliable" is SHARING, not CONTENT. One named actor's own output is CONTENT; a
CLASS of actors measured by what they share follows the study's framing (usually SHARING).
QUALITY vs CONTENT: CONTENT only if items are judged for truth/falsity against an external ground
truth (fact-checks, expert verification, guideline concordance stated as accurate/inaccurate,
explicit false/misleading coding, a source-reliability list). DISCERN / GQS / JAMA / usefulness /
completeness / "quality" scores → construct QUALITY (row kept, excluded from prevalence). A Likert
accuracy scale reported only as a mean → not a share, no row (say so in notes). If a wholly true
item could receive the label ("misleading" = covers < 4 screener items), it is QUALITY.
When genuinely ambiguous → QUALITY and borderline=true.

## 4. Row schema (JSON). Strings unless noted; use "" when not applicable, never null.
id (given) · country (as stated) · country_norm (canonical English name; "Multi-country" for
enumerated nations; "Global" if worldwide/unspecified) · country_scope single|multi|global ·
platform (as stated) · platform_norm one of Twitter/X, Facebook, YouTube, TikTok, Instagram,
WhatsApp, Telegram, Reddit, Google Search, web_cross_platform, survey, multi_platform, other ·
date (data-collection period as stated) · year (4-digit year of data collection; publication year
if unknown, say so in notes) · measure_type (one line: what the % is, e.g. "% of respondents who
shared fake news in the past month") · value_pct (number as string, e.g. "9.9"; "" only for
value_kind range_not_point) · value_raw (verbatim number(s) with counts, e.g. "64/289 (22.1%)") ·
value_kind proportion|scale_score|per_capita_intensity|range_not_point · construct
CONTENT|EXPOSURE|REACH|SHARING|RECALL|CONCENTRATION|QUALITY|OTHER · recall_subtype exposure|sharing
· sharing_subtype content_share|actor_share · exposure_type proportion|intensity|diet_share ·
reach_subtype exposure|sharing|liking · conc_group_pct · conc_share_pct · conc_unit user|source ·
conc_dimension exposure|sharing · conc_group_label · denominator (what the % is a share of, with
the number: "2,005 UK social media users (Opinium panel)") · definition (how an item/respondent
qualified for the numerator) · misinfo_def (the paper's definition of misinformation, short quote)
· n (denominator size with unit: "289 articles") · source_quote (VERBATIM sentence(s) or table cell
containing the value — mandatory, copy exactly) · page_loc (page/section/table) · population_scope
general_public|elite_politician|professional|other · breadth fabricated|false|misleading (veracity
strictness of the numerator; "" for source-level lists and QUALITY) · classification_level
claim_level|source_level|mixed · ground_truth fact_checker|domain_list|researcher_coding|crowd|
classifier|self_report · ground_truth_detail (who coded, against what, reliability) · unit
item|claim|url|account|person|exposure · denom_scope topical|political_news|news_diet|all_media|
population|n/a · denom_selection ""|curated|single_source · sampling_frame keyword_topical|
random_platform|panel_trace|survey_sample|curated_seed|full_census|convenience|purposive · topic
health_other|covid19|vaccines|politics_elections|general_news|war_geopolitics|science_other|
crime_society|economy_finance|other · definition_variant (bool: true when this row is a
stricter/broader definition of another row in the same country×platform cell) ·
within_misinfo_content (bool) · borderline (bool) · moderator_quote (verbatim snippet justifying
denominator/ground-truth coding) · confidence high|medium|low · notes.

denom_scope rules: surveys and REACH → population ALWAYS (the denominator is who was asked, not the
topic). A single-issue keyword corpus → topical. Top-N / most-viewed / first-page / rank-truncated
sets → the scope of the topic PLUS denom_selection=curated. One account/channel/outlet →
denom_selection=single_source. Multi-issue keyword corpora → curated. CONCENTRATION and OTHER → n/a.
Prefer the narrower category when two readings are defensible.

## 5. Output: ONE JSON file per paper, at the path given in the batch manifest:
{"id": ..., "title": ..., "text_status": "ok|truncated|garbled|wrong_paper|abstract_only",
 "screen": "INCLUDE|EXCLUDE", "screen_reason": "...", "constructs_found": [...],
 "estimates": [ {row}, ... ],   (empty list if EXCLUDE)
 "missed_or_uncertain": "anything you saw but did not extract, and why",
 "rob": {"design": "one line: sampling frame, response rate, coding procedure, reliability stats
          as reported", "item6_quote": "verbatim case-definition sentence", "item10_quote":
          "verbatim numerator/denominator sentence"} }
Write valid JSON (ensure_ascii not required). Do the papers in the order given. Then run the
validator named in the manifest and fix anything it reports before finishing. Report per paper:
screen, number of rows, constructs.
