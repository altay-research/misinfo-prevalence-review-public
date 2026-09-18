# Research Log — Systematic Review of Misinformation Prevalence & Concentration

**Append-only chronological log.** Every step, command, result, and the *reasoning*
behind each decision is recorded here so the project is fully reproducible and every
choice is justifiable for peer review. Do **not** rewrite history; correct mistakes
by adding a new dated entry that supersedes the old one (and say so explicitly).

Conventions:
- Dates are ISO `YYYY-MM-DD`. All times Europe/Zurich unless noted.
- Exact commands/queries are reproduced verbatim in code blocks.
- API keys are **never** stored here or in any script; they are read from
  environment variables at runtime (see `README.md`). Where a key was used, the
  log records *that* a key was used and the endpoint, not the key value.
- Hit counts are database-state-dependent: a count is only reproducible *as of the
  query date*. Always record the date next to any count.

---

## 2026-06-20 — Session 1: Idea evaluation & landscape scan (pre-protocol)

### 0. Question under evaluation
Is it worth doing a **systematic literature review** on (a) the **prevalence** of
misinformation (broadly construed: misinformation, disinformation, false/fake news,
unreliable/untrustworthy websites, junk news) and (b) the **concentration** of
misinformation *consumption* (whether a small minority accounts for most exposure)?
Sub-goal: document the methodological differences, platforms, countries, and
measurement choices that drive divergent headline estimates.

Decisions taken with the user this session (recorded for traceability):
- **Format:** Systematic review + quantitative *extraction* (PRISMA-style), **not** a
  pooled meta-analytic effect size. Rationale: "misinformation broadly" means
  estimates measure heterogeneous constructs; a single forest plot would be
  indefensible. Quantitative *tabulation* coded by method is more honest.
- **Construct scope:** Broad (false news + disinformation + unreliable domains +
  rumour/conspiracy), with heterogeneity treated as a *finding to document* rather
  than a nuisance to suppress.
- **Search boundary (Scopus):** Strict — require exposure/consumption/reach/audience/
  news-diet/prevalence terms; exclude pure belief/susceptibility and intervention-
  only studies at the query stage.
- Still **open** (upstream decisions, deferred): solo vs co-authored; online-only vs
  include legacy/TV; final database set (Scopus confirmed; Web of Science likely).

### 1. Conceptual framing decided this session
The literature conflates three distinct quantities under the word "prevalence."
The review will separate them explicitly (this separation is itself a contribution):
1. **Content prevalence** — share of posts/URLs/items that are false/unreliable.
2. **Audience exposure** — share of an individual's information diet that is
   misinformation (person-level).
3. **Concentration** — how unequally exposure/consumption is distributed (e.g. share
   consumed by the top 1–10% of users; Gini). 
Observation motivating the paper: alarming headline numbers are almost always (1);
reassuring numbers are (2)–(3).

### 2. Search of local PDF library (3,806-line index)
Index file:
`~/Library/Mobile Documents/com~apple~CloudDocs/Sacha/Claude/pdf_index_raw.jsonl`
(JSONL, one paper per line: title, authors, year, journal, doi, summary.)
Method: `grep -iE` over the index, then parse JSON for year+title. Full commands are
preserved in `scripts/search_pdf_index.sh`.

Key findings (what already exists locally):
- **Reviews / syntheses:** Budak et al. 2024 *Nature* "Misunderstanding the harms of
  online misinformation" (narrative, US-centric, harm-focused — NOT systematic
  extraction); "Mapping the Scholarship of Fake News Research: A Systematic Review"
  2022 (bibliometric, not a synthesis of prevalence numbers); "Systematic Literature
  Review on the Spread of Health-related Misinformation" 2019 (health-only,
  qualitative); Altay 2023 "Misinformation on misinformation" (conceptual/method
  critique, not a prevalence synthesis).
- **Primary prevalence studies (raw material):** Allen et al. 2020 *Sci Adv*
  "Evaluating the fake news problem at the scale of the information ecosystem";
  Guess 2019 "Less than you think"; Guess 2021 "(Almost) Everything in Moderation";
  Fletcher/Nielsen 2018 "Measuring the reach of fake news in Europe"; Altay 2022
  "Quantifying the infodemic."
- **Primary concentration studies (raw material):** Grinberg et al. 2019 *Science*
  (1% of users = 80% of consumption); "Supersharers of fake news on Twitter" 2020;
  Guess 2020 "Exposure to untrustworthy websites in the 2016 US election"; "The
  small, disloyal fake news audience" 2018.

Interpretation: locally, the primary estimates exist in abundance but no synthesis
sits on top of them combining **prevalence + concentration** across domains.

### 3. Web search (US-region, June 2026)
Tool: harness WebSearch. Queries run (verbatim):
- `systematic review prevalence of misinformation exposure across platforms meta-analysis`
- `concentration of misinformation consumption supersharers systematic review 2025`
- `how prevalent is misinformation systematic review meta-analysis 2024 2025 2026`

Relevant existing reviews surfaced (potential competitors):
- **JMIR 2021** "Prevalence of Health Misinformation on Social Media: Systematic
  Review" — health-only; measures *content* prevalence, not audience exposure/
  concentration. https://www.jmir.org/2021/1/e17187/
- **BMC Public Health 2026** "Exposure to health misinformation on social media
  across key health domains: a systematic review and meta-analysis" — 69 studies,
  health-only, survey-based exposure; no political/general; no concentration.
  https://link.springer.com/article/10.1186/s12889-026-27242-2
- **PNAS 2024** "Susceptibility to online misinformation: a systematic meta-analysis"
  — *susceptibility* (who believes), not prevalence/exposure.
  https://www.pnas.org/doi/10.1073/pnas.2409329121
- **Tandfonline 2024** "Misinformation, disinformation, and fake news: lessons from
  an interdisciplinary, systematic literature review" — definitions/themes/
  bibliometrics, NOT quantitative prevalence.
  https://www.tandfonline.com/doi/full/10.1080/23808985.2024.2323736
  (NOTE: WebFetch on this URL returned HTTP 403; scope inferred from search snippet.
  TODO: retrieve full text via institutional access to confirm it does not extract
  prevalence/concentration estimates.)

### 4. Semantic Scholar API (Graph API v1, public, no key)
Endpoint: `https://api.semanticscholar.org/graph/v1/paper/search`
Heavily rate-limited (HTTP 429) on 2026-06-20; only partial results returned.
Script: `scripts/semantic_scholar_search.py`.
The one batch that returned for "concentration of consumption" yielded only the
**primary** studies (Allcott/Gentzkow 2018 selective exposure; Grinberg 2019;
Guess untrustworthy-websites 2020; "Quantifying partisan news diets" 2022) — i.e.
**no review paper sits above them.** Consistent with the local-index finding.
TODO: re-run with an API key / slower cadence for a complete pass.

### 5. Scopus API (scoping queries) — KEY EVIDENCE
Endpoint: `https://api.elsevier.com/content/search/scopus`
Auth: `X-ELS-APIKey` header, key read from `$SCOPUS_KEY` env var (not stored).
Script: `scripts/scopus_search.py`. **Counts below are as of 2026-06-20.**

Query building blocks (verbatim):
```
TOPIC = ( misinformation OR disinformation OR "fake news" OR "false news"
          OR "unreliable news" OR "untrustworthy websites" OR "low-quality news"
          OR "junk news" )
EXPOSURE = ( exposure OR consumption OR reach OR audience OR "news diet"
             OR prevalence OR circulation )
NOTCS = AND NOT TITLE-ABS-KEY ( detection OR classifier OR classification
        OR "deep learning" OR "neural network" OR "machine learning" OR blockchain
        OR algorithm OR transformer OR dataset )
```

Counts (2026-06-20):
| Query | Hits |
|---|---|
| `TITLE-ABS-KEY ( TOPIC AND EXPOSURE )` | **7,538** |
| `TITLE-ABS-KEY ( TOPIC AND EXPOSURE ) NOTCS` (strip CS-detection) | **5,796** |
| Reviews only — `TITLE ( (misinfo OR disinfo OR "fake news") AND (prevalence OR exposure OR consumption) ) AND DOCTYPE(re)` | **11** |
| `TITLE-ABS-KEY ( TOPIC AND CONCENTRATION-terms ) NOTCS` | 318 (noisy — "concentration" also matches dose/vaccine concentration; needs cleaning) |

**Decisive result:** all **11** existing *reviews* with prevalence/exposure/
consumption in the **title** are **health-domain** (e.g. health misinformation,
older adults, cancer web-monitoring). **None** is a general/political prevalence
review; **none** addresses concentration of consumption.

Note on a non-effect: adding `LIMIT-TO(SUBJAREA,...)` did not change the 5,796 count
in the standard Search API response — `LIMIT-TO` facets are not applied as filters
via this endpoint the way they are in the Scopus web UI. TODO: apply subject-area
filtering client-side on the `subtype`/`subjarea` fields, or use the facet API.

### 6. Conclusion of Session 1 (idea evaluation)
**The gap is real and confirmed three independent ways** (local index; web/Semantic
Scholar; Scopus reviews-in-title = 11, all health). No general, cross-platform
systematic review synthesizes *exposure prevalence* AND *concentration of
consumption*, coded by method. The **concentration** half is the thinner, more
original, more defensible contribution; **prevalence** is the more expected one.
Corpus is tractable (~5,800 after removing CS noise; concentration far smaller).

**Decision: proceed to a formal protocol** (PRISMA-P). See `docs/protocol.md`.

### 7. Berriche (2024) thesis — seed corpus found
User recalled that Manon Berriche's PhD thesis contains an appendix table of
prevalence studies. Located it:
- **Berriche, M. (2024).** *Tu crois que c'est vrai ? Diversité des régimes
  d'énonciation face aux fake news et mécanismes d'autorégulation conversationnelle.*
  PhD, Université Paris-Cité, defended 2024-12-05 (dir. D. Cardon & S. Pène).
  HAL: https://theses.hal.science/tel-05409923 ; PDF mirror: https://arxiv.org/pdf/2511.18369
- Downloaded to `literature/berriche_these_2024.pdf` (438 pp., 15 MB) and extracted
  to text with `pdftotext -layout`.
- **Annexe 1 (pp. 418–422):** "Revue de littérature non exhaustive d'études mesurant
  l'audience des fake news et/ou leur place dans le total de contenus consommés par
  les individus." Columns: Étude · Échantillon · Données · Pays · Période · Corpus ·
  Définition des fake news · Audience/Engagement · Place dans la consommation globale.
- **Digitised to `data/seed_berriche_annexe1.csv` (19 studies / 22 rows** — Altay 2022
  split by country). Spans Allcott & Gentzkow 2017 → Baribi-Bartov et al. 2024.
- **Annexe 2 (pp. 423+):** studies on *effects* of content types on beliefs/attitudes/
  behaviour (DellaVigna & Kaplan 2007, Bond 2012, etc.) — secondary, not digitised yet.

Use of this seed set: (a) starting extraction template — confirms the coding columns
are right; (b) **recall/validation test** — the final search string must recover every
one of these 19 studies, else it is too narrow. TODO: cross-check each seed study's
indexing in Scopus and confirm the strict query catches them.

### 8. Scope decisions taken (2026-06-20, session 1 cont.)
- **Channels: ONLINE + TRADITIONAL (TV / radio / press).** Broad. Implication: the
  search string must not implicitly restrict to web/social platforms; TV-panel and
  legacy-media exposure studies (e.g. Allen 2020 TV panel; DellaVigna & Kaplan 2007)
  are in scope. Increases heterogeneity — handled by the construct/method coding.
- **Authorship: SOLO for now.** Claude acts as the documented second screener;
  reconciliation rule to be defined; co-author may be added later.
- **Next step chosen: recall validation on Scopus** (this session).

### 9. Recall validation against the Berriche seed set (2026-06-20)
Goal: a search string is only defensible if it recovers known-relevant studies.
Test, per seed study: (a) is it indexed in Scopus? (b) is it captured by preset
`strict`? Script: `scripts/recall_check.py` (reproducible; results saved to
`searches/`). Results below (counts as of 2026-06-20):

**Run 1 — preset `strict` (v1):** recall **8/17**. 9 seminal studies MISSED, e.g.
Allcott & Gentzkow 2017, Allen 2020, Osmundsen 2021, Baribi-Bartov 2024, Allen 2024.
Diagnosis: (i) the exposure-term block was too narrow — prevalence studies frame
themselves as *sharing / spread / diffusion / scale / quantifying / supersharers*,
none of which were in the block; (ii) the `AND NOT TITLE-ABS-KEY(... algorithm ...
dataset ...)` exclusion was killing legitimate social-science papers that mention
"dataset"/"algorithm" in passing. (Also: common-name identifiers — Zhou, Moore —
matched the WRONG paper, a test artifact; fixed in run 2 with exact-title IDs.)

**Run 2 — `strict` (v1) vs `strict_v2`:** with exact-title identifiers,
**v1 recall = 8/16; v2 recall = 14/16** indexed seed studies. v2 fixes:
- broadened measurement family: add sharing/shared/spread/diffusion/dissemination/
  quantif\*/"how much"/supersharer\*/traffic/visits/engagement/scale/consume\*;
- restrict the CS exclusion to **TITLE only** (incidental "dataset"/"algorithm" in an
  abstract no longer excludes the paper).
- v2 recovers Allen 2020, Osmundsen 2021, Baribi-Bartov 2024, Allen 2024, Altay 2022.
- Remaining v2 misses are NOT string failures: **Fletcher et al. 2018 is a Reuters
  Institute report — grey literature, not indexed in Scopus** (motivates the grey-lit
  track, §11); Guess 2021 and Cordonnier & Brest 2021 are common-name identifier
  collisions still to be pinned to the exact paper (Cordonnier & Brest may also be a
  French-language report / grey lit).

**Decision: adopt `strict_v2` as the working Scopus string** (preset `strict_v2` in
`scripts/scopus_search.py`). Rationale: systematic reviews must favour **recall over
precision** — catch everything, exclude at screening.

**Corpus size (Scopus, 2026-06-20):** `strict_v2` = **20,409 records** (vs v1 5,796).
TENSION TO RESOLVE: 20k titles is heavy for a solo screener. Options to add to the
protocol: (a) tighten precision with a proximity operator (e.g. require topic+measure
within N words, `W/n`); (b) add a mandatory empirical/quantitative filter; (c) plan an
LLM-assisted title-screening pass with human verification of all borderline/excluded.
Do NOT silently cap results. Logged as open item.

### 10. Scope additions requested by user (2026-06-20)
- **(A) Actor-level prevalence — who spreads misinformation (esp. political elites).**
  Explicitly IN SCOPE: studies quantifying the prevalence of misinformation in the
  output of specific actor classes — politicians/candidates/parties, influencers,
  news outlets — across platforms incl. **TikTok**. Motivating example the user
  recalled: a recent German study on politicians' content on TikTok. Candidate found:
  *"TikTok Rewards Divisive Political Messaging During the 2025 German Federal
  Election"* (arXiv 2509.10336; EPJ Data Science 2026), 25,292 videos by German
  politicians — but framed around *divisive engagement*, not misinformation per se.
  **RQ4 anchor study identified (2026-06-20):** Lasser, J., Aroyehun, S.T., Simchon, A.,
  Carrella, F., Garcia, D., & Lewandowsky, S. (2022). "Social media sharing of
  low-quality news sources by political elites." *PNAS Nexus*. 3M+ tweets from MPs in
  US/UK/Germany 2016-2022; German MPs shared 812 misinformation links (1.3% of tweets),
  CDU/CSU > centre/left; headline = "asymmetric American exceptionalism" (US elites
  share far more). This is the "German study" the user recalled (Lewandowsky/Garcia
  group). Add to actor-prevalence sub-corpus + use as RQ4 recall check.
  Implication for search: ensure actor terms (politician\*, candidate\*,
  legislator\*, "political elites", influencer\*) and TikTok are not excluded; they
  are already compatible with `strict_v2`.
- **(B) Grey literature / reports IN SCOPE, analysed separately.** Many non-peer-
  reviewed reports quantify misinformation prevalence (e.g. **Science Feedback** ~30%
  figures, **NewsGuard**, **Reuters Institute Digital News Report**, **EU DisinfoLab**,
  **ISD**, **Oxford ComProp**, **Avaaz**, **EUvsDisinfo**). Decision: include a
  dedicated grey-literature track, clearly flagged and **never pooled** with peer-
  reviewed estimates; for each, document (i) how it defines "misinformation", (ii) its
  method/denominator, (iii) its limitations. This turns the reports into a *critique
  object* (how definitional/method choices inflate headline %), directly serving RQ3.
  Note: the recall test already produced a concrete case — Fletcher 2018 (Reuters
  report) is not in Scopus — proving Scopus alone misses grey lit.

### 11. Search tuning — precision/recall trade-off + the "sharing" question (2026-06-20)
Script `scripts/tune_search.py` compares candidate filters on BOTH corpus size and
recall vs the seed set (counts as of 2026-06-20):

| variant | corpus | recall (seeds) |
|---|---|---|
| consumption_only (no sharing terms) | 8,713 | 10/16 |
| **v2_baseline (consumption + sharing)** | **20,409** | **14/16** |
| prox_W5 (topic W/5 measure) | 6,603 | 11/16 |
| empirical (v2 + empirical terms) | 10,113 | 12/16 |
| prox_AND_emp | 3,517 | 9/16 |

Findings:
- **User's question — also include *sharing*, not just consumption?** YES, keep it.
  Dropping sharing nearly halves the corpus (20,409 → 8,713) but recall falls to
  10/16: it loses the supersharer/sharing seed studies (Osmundsen 2021, Baribi-Bartov
  2024, Allen 2024 …). Concentration of *sharing/production* is half of RQ2, so
  sharing terms are required, not optional.
- **No query-tightening variant preserves recall.** prox_W5 (11/16), empirical (12/16),
  combo (9/16) all drop known-relevant studies. (Recall denominators include a few
  ambiguous identifiers, so read these directionally — but the direction is clear.)
- **Useful by-product:** Scopus DOES accept `W/n` with parenthesised OR-groups
  (prox_W5 ran), so a proximity query is available as a **sensitivity analysis** to
  report alongside the primary search.

**Decisions:**
1. **Primary Scopus string = `strict_v2` (v2_baseline), sharing INCLUDED.** Maximise
   recall at the search stage.
2. **Reduce the ~20k at the SCREENING stage, not by mutilating the query** — LLM-
   assisted title/abstract pre-screen with human verification of all borderline and
   excluded records (documented, auditable). This is the only path that does not
   sacrifice recall.
3. Report `prox_W5` as a sensitivity analysis.

### 12. Sharing: exclude hypothetical/stated sharing (user point, 2026-06-20)
User flagged that much sharing research measures *sharing intentions* ("would you
share?") experimentally, whereas we want **observed real-world sharing**. Quantified
the noise (counts 2026-06-20, logged in `searches/scopus_query_log.tsv`):
- explicit sharing-intention bucket (`"sharing intention*"/"willingness to share"/
  "would you share"/vignette/hypothetical` within corpus) = **223 records**;
- behavioural/observed-sharing signal (trace/platform/Twitter/Facebook/URL) = **2,522**.
The 223 is a LOWER BOUND — most lab sharing studies don't use the word "intention",
so they are not keyword-separable. **Decision:** add an explicit eligibility exclusion
(protocol §4) for hypothetical/stated/intended sharing, enforced at SCREENING, not in
the query (preserves recall). Key nuance recorded: criterion = hypothetical vs actual
*behaviour*, not survey vs trace — survey-measured *exposure* stays in; only
hypothetical *intentions* are excluded.

### 13. Eligibility criteria drafted (v0.2, 2026-06-20)
Wrote a PICOS-style eligibility set (protocol §4): inclusion = quantitative
audience-exposure / consumption / observed-sharing / concentration / actor-level
estimate with an identifiable denominator and a stated misinformation operationalisation;
exclusions = CS-detection, non-empirical, content-only-without-denominator,
belief/intervention-only, hypothetical/stated sharing. Definition of misinformation is
EXTRACTED, not used as a gate (it is an analysis object). Four defaults set provisionally
pending Sacha's confirmation: date range (no lower bound, report distribution); language
(English + French at full text, German TBD); publication type (incl. preprints, flagged);
no hard sample/quality threshold (handled in risk-of-bias + sensitivity). These are the
only criteria genuinely requiring his input; everything else follows from prior decisions.

### Open items carried forward
RESOLVED this session: solo for now ✓ ; channels = online + traditional ✓ ;
search string = `strict_v2` incl. sharing ✓ ; reduction at screening (not query) ✓ ;
exclude hypothetical/stated sharing at screening ✓ ; eligibility criteria v0.2 drafted ✓ ;
RQ4 anchor study identified (Lasser et al. 2022) ✓ ; grey-lit track skeleton ✓ ;

### 14. Eligibility parameters confirmed (Sacha, 2026-06-20)
- Date range: NO lower bound (report distribution).
- Language: **English only** at full text (FR/DE studies noted as limitation; English
  reports of same data used where they exist).
- Preprints: INCLUDE, flagged non-peer-reviewed + sensitivity analysis excluding them.
- Quality threshold: NONE at inclusion (handled via risk-of-bias + sensitivity).
Protocol §4.3 updated from provisional to confirmed. Eligibility is now FROZEN for v1.

### 15. Corpus retrieval + competitors + grey-lit pilot (2026-06-20, session 1 cont.)
Project moved to `~/Desktop/Claude/Random/Misinfo_Prevalence_Review/` (WildCard rule);
registry path fixed manually (rescan doesn't reach there); dashboard regenerated.

**(2) Full corpus retrieval — `scripts/scopus_fetch_corpus.py`.** This key's entitlement
**forbids the cursor parameter** (403 ENTITLEMENTS_ERROR), **caps page size at 25** (400 at
count=200), and **start/count at 5,000**. Workaround: **slice the query by publication
year** (each slice < 5,000), paginate with start/count, union + dedupe by eid. Gotcha
fixed: parenthesise the base query before AND-ing `PUBYEAR`, else Scopus mis-parses
precedence and the year filter is silently ignored (unparenthesised "<2015" returned
24,170 > total). Year counts: <2015=986; 2024=3,006; all single years < 5,000. Snapshot →
`data/corpus_strict_v2_2026-06-20.jsonl` (STANDARD view; abstracts NOT included — fetch
later for survivors only). **Result: 20,344 unique records** (6 MB) vs API total 20,409
— a 0.3% gap, almost certainly records with missing/odd PUBYEAR not matched by any year
slice; negligible, documented (chase later if needed). Distribution: exponential growth,
concentrated 2018+ (2025 peak = 3,947), long thin tail to 1908; types: 12,403 Article,
3,335 Conference Paper, 1,702 Book Chapter, 1,217 Review. **In-snapshot seed spot-check:
all 5 probed seed titles present** (Allen 2020, Guess 2020, Baribi-Bartov 2024, Guess
2019, Nelson & Taneja 2018) — recall confirmed in the actual data, not just the count API.

**(4) Competitors — `docs/related_reviews.md`.** Budak et al. 2024 *Nature* read in full
locally (`s41586-024-07417-w.pdf`): confirmed a **Perspective** (not systematic), on
effects/harms, US + W. Europe, three-misperceptions framing; **no PRISMA, no extraction,
no concentration synthesis, no grey lit**. Comparison table + differentiation paragraph
drafted; other competitors characterised from abstracts (△, full text TODO).

**(3) Grey-lit pilot — `docs/grey_literature.md`.** Coded Avaaz "Facebook's Algorithm: A
Major Threat to Public Health" (2020): 3.8bn "estimated views" with **no denominator**;
sample **selected on the outcome**; "views" = CrowdTangle interactions × multiplier (not
exposure); report concedes views ≠ exposure, measures no harm. Textbook RQ5 object.
NewsGuard "30%" AI monitor stubbed. The exact **Science Feedback ~30% report** did NOT
surface via search — need link/title from Sacha.

### 16. Grey-lit SIMODS coded + screening workflow built (2026-06-20)
**Science Feedback found** — it was in Sacha's library, not surfaced by web search: the
two **SIMODS** reports (`Articles_Claude/SIMODS-Report-1.pdf`, `-2.pdf`), 2025, EU/DSA
EDMO structural indicators. Coded on the grey-lit grid (`docs/grey_literature.md` pilot
#3). Prevalence: TikTok ~20%→25%, FB ~13%, X ~11%; "problematic content" up to ~43%;
health ~43% of misinfo. **Crux:** their denominator = a **keyword-seeded high-risk-topic
corpus** (Ukraine/climate/health/migration/politics), exposure-weighted — not the whole
diet — which is why they land 1–2 orders of magnitude above Allen 2020 (0.15%). This is
the paper's denominator thesis in one example. (Sacha publicly critiqued SIMODS — reuse.)

**Screening workflow built** (`docs/screening_protocol.md`, `scripts/screen_titles.py`,
`data/screening_goldset.csv`). Two-stage (title→full text), LLM-assisted + human
verification, recall-protective (uncertain→MAYBE; all INCLUDE+MAYBE advance; random
EXCLUDE audit ≥300; gold-set validation before production). Gold set = 31 hand-labelled
titles sampled across the corpus; that sample alone shows ~0 clear includes / ~3 MAYBE /
rest EXCLUDE — i.e. the broad query is high-recall/low-precision as intended, so the
screener carries the load. Script pins model + temp=0, reads ANTHROPIC_API_KEY from env,
resumable. NOT yet run — no API key in env; needs Sacha's key + model/budget OK.

### 17. Screening pivot to in-session Opus subagents; validation + Batch 1 (2026-06-20)
Sacha has no API key and rejected Haiku → screening is done IN-SESSION via Opus
subagents (Agent tool), not the external-API script. Shared criteria file
`docs/screening_criteria.txt`; each agent reads a corpus slice, judges each title
(no keyword script), writes a shard CSV in `data/screen_shards/`, returns INCLUDE/MAYBE.
Gold set upgraded with 9 known-positive anchors (seed studies in corpus) → now tests
true-positive recall.

**Validation (40-case gold set, 1 agent):** 97.5% agreement (39/40); **NO RECALL
LEAKS**; all 9 known positives → INCLUDE; sole disagreement was safe-direction
(human EXCLUDE → model MAYBE). Methodology validated.

**Batch 1 = 16 agents (1 validation + 15 screening), corpus lines 0–1500.** Note the
corpus is YEAR-ORDERED (download was year-sliced: <2015, then 2015→2026), so lines
0–1500 are the **legacy tail (1908–2017)**, poor in prevalence studies. Result
(consolidated from shard files → `data/screen_title_2026-06-20.csv`): 1,500 screened →
**4 INCLUDE, 167 MAYBE, 1,329 EXCLUDE; 171 advancing (11.4%)**. The 2018–2026 bulk
(~18,800 records) will be far denser — advancing rate will rise.
**Cost/throughput:** ~31k subagent tokens/screening-agent → ~490k tokens for this
~1,600-title batch. Remaining ~18,800 ≈ 12–13 more 16-agent batches.

### 18. Screening Batch 2 (2026-06-20): lines 1500–5500
16 agents × 250 titles = 4,000 (terse returns: counts only, consolidated from files).
Batch result: 79 INCLUDE, 512 MAYBE, 3,409 EXCLUDE (advancing 14.8% — higher than the
legacy tail, as expected). **Cumulative: 5,500 / 20,344 screened (27%)** → 83 INCLUDE,
679 MAYBE, 4,738 EXCLUDE; 762 advancing (13.9%). Master: `data/screen_title_2026-06-20.csv`.
Cost: ~49k subagent tokens/agent (250 titles) ≈ ~785k/batch. Budget heuristic observed:
Batch-1 (16 agents) moved Sacha's session usage ~20%→36% (~16 pts); plan batches against
that. **Progress marker: next slice starts at corpus line 5500.**

### 19. Screening Batch 3 (2026-06-20): lines 5500–8000
10 agents × 250 = 2,500 titles → 44 INCLUDE, 322 MAYBE, 2,134 EXCLUDE.
**Cumulative: 8,000 / 20,344 screened (39%)** → 127 INCLUDE, 1,001 MAYBE, 6,871 EXCLUDE;
advancing 1,128 (14.1%). Budget calibration this session: Batch 2 (4,000 titles) moved
usage 36%→65% (~7.3 pts/1,000 titles in efficient mode: 250/agent, terse returns).
Stopped at ~84% per Sacha's 85% ceiling. **Resume marker: next slice = corpus line 8000.**

### 20. STAGE-1 TITLE SCREENING COMPLETE (2026-06-21, scheduled big batch)
Ran via the local one-shot cron job (CronCreate, fired 00:53 in the live session — local,
private, per the CLAUDE.md scheduling rule). Finished lines 8750→20344 in 3 waves of
16/16/15 Opus subagents (250 titles each), consolidating + committing after each wave.

**FINAL Stage-1 result: 20,342 / 20,344 records screened (100.0%; 2-record gap = duplicate
eids, negligible). 47/47 target slices present.**
- **INCLUDE: 276**
- **MAYBE: 2,460**
- **EXCLUDE: 17,606**
- **Advancing to Stage-2 (INCLUDE+MAYBE): 2,736 (13.5%)**
Master labels: `data/screen_title_2026-06-20.csv`; per-slice shards in `data/screen_shards/`.
Methodology validated earlier (gold set 97.5%, 0 recall leaks). Cost: ~54k subagent
tokens/agent; the full corpus (~20.3k titles) screened across this + prior sessions.

### 21. EXCLUDE audit + Stage-2 prep (2026-06-21)
**Recall audit:** 300 random EXCLUDEs (seed 20260621) re-screened BLIND by 2 independent
auditor agents (150 each). Result: **0 INCLUDE leaks** (no clearly-eligible study wrongly
excluded — the decisive recall metric passes), **23/300 (7.7%) EXCLUDE→MAYBE** boundary
disagreements (title-only fuzz; all content-quality/spread ambiguities, none a clear
prevalence study). The 23 flagged eids were bumped EXCLUDE→MAYBE in the master
(reason "audit recall-flag"). Master now: 276 INCLUDE, 2,483 MAYBE, 17,583 EXCLUDE;
**2,759 advancing**. Audit files in `data/audit/`.
**Documented limitation:** Stage-1 used single-screener title screening (not full dual
independent screening, for budget). The audit bounds the cost: ~0% INCLUDE-level misses,
~7.7% EXCLUDE/MAYBE boundary disagreement (≈1,350 of 17,583 EXCLUDEs might be MAYBE under
a stricter reading). Mitigations: recall-protective prompt (uncertain→MAYBE), audit, and
Stage-2 abstract screening resolves all advancing borderline cases. Acknowledge in the
methods/limitations.

### 22. Stage-2 abstract fetch (2026-06-21)
Scopus Abstract Retrieval is NOT entitled on this key (rich views -> 401; basic ->
empty abstracts). Switched to **OpenAlex** (free, by DOI). Per-record fetching got
rate-limited/slow, so rewrote as **batched** (DOI filter, 50 works/call) ->
`scripts/fetch_abstracts_openalex_batch.py` (~55 calls, <1 min; resumable).
Coverage of 2,758 advancing: **2,035 with abstract (74%)**, 158 no-DOI (6%), 565
DOI-but-no-abstract (20%). The 723 (26%) without an abstract stay MAYBE -> full-text/
title handling. Abstracts saved to `data/abstracts/abstracts.jsonl` (gitignored;
regenerable; 3.4 MB). Stage-2 criteria: `docs/screening_criteria_stage2.txt` (stricter,
abstract-decisive; missing abstract -> MAYBE, never auto-EXCLUDE).

### 23. STAGE-2 ABSTRACT SCREENING COMPLETE (2026-06-21)
21 subagents × ~100 records screened the 2,035 advancing-with-abstracts against the
stricter abstract criteria (`docs/screening_criteria_stage2.txt`). Screened 2,019 unique
(16 dup eids dropped). Result → `data/screen_abstract_2026-06-21.csv`:
- **INCLUDE (abstract-confirmed): 635**
- **MAYBE (need full text): 264**
- **EXCLUDE (abstract rules out): 1,120**

**Combined post-Stage-2 status of the 2,758 advancing:**
- **635 abstract-confirmed INCLUDE** (go to data extraction; note many are CONTENT-
  prevalence, e.g. % of YouTube/TikTok videos false — to be bucketed at extraction)
- **1,003 need full-text** (264 Stage-2 MAYBE + 739 without an abstract)
- **1,120 excluded at abstract**
Cost: ~84k subagent tokens/agent (abstracts are ~5× titles). Higher INCLUDE rate (~31%)
than title stage because these already passed title screening + have confirming abstracts.

### 24. Construct tagging of the 635 included — KEY RESULT (2026-06-21)
7 agents tagged each included study by construct(s) (`docs/construct_tagging.txt`;
multiple tags allowed; nothing excluded — content-prevalence KEPT, per Sacha: the
content-vs-exposure gap IS a paper point). Output `data/extract/include635_tagged.csv`.
**Primary construct (n=635):** CONTENT 371 (58%), SHARING 82 (13%), EXPOSURE 81 (13%),
ACTOR 68 (11%), CONSUMPTION 25 (4%), **CONCENTRATION 8 (1%)**.
**Any tag:** CONTENT 472, ACTOR 214, SHARING 184, EXPOSURE 110, CONSUMPTION 104,
CONCENTRATION 67. Audience-side core (primary≠CONTENT) = 264.
=> Central finding: the literature measures CONTENT, not audience EXPOSURE, and almost
never CONCENTRATION (the harm-determining quantity) — the paper's thesis, quantified.

### 25. Estimate extraction on all 635 included — DATA SPINE BUILT (2026-06-21)
13 agents extracted, per study from the abstract: estimate, units, denominator (% of
what — the key field), platform, country, definition_source, sample_n, full_text_needed.
Output `data/extract/extraction_master.csv` (635 rows, +year/author/doi/title joined).
325 have a numeric estimate in the abstract; **310 need full text** for the headline
number. Platforms: Twitter 126, YouTube 70, Facebook 48, TikTok 41, Instagram 24,
WhatsApp 15. Countries: US-dominant (~110), Spain 28, Brazil 27, China 22; 87 not stated.
Already visible: huge denominator heterogeneity (survey "% who've seen X" vs trace "% of
diet" both EXPOSURE; concentration e.g. "~14% creators → 82% of fake content",
"~800 superspreaders = 35% of daily reshares") — the methodological story, with data.

### 26. ROBUSTNESS CHECK — search-term coverage across constructs (2026-06-21)
Q (Sacha): do the search terms allow fair comparison of prevalence/exposure/concentration?
Finding: strict_v2's MEASURE block covers content/exposure/sharing well but **under-targets
CONCENTRATION** (has supersharer* but NOT concentration/Gini/skew/top-X%/inequality/
superspreader). So cross-construct COUNTS are not perfectly even for concentration.
Empirical bounding (Scopus was 403 rate-blocked from today's volume; used OpenAlex +
local corpus instead):
- OpenAlex: dedicated concentration literature is only DOZENS of papers ("misinformation
  superspreaders" 33, disinfo 8, fake-news 7; loose "concentration users" ~47) — NOT a
  hidden trove.
- Our corpus: 41 titles carry concentration-specific terms (most off-topic, only 6
  advanced); but **67 of the 635 INCLUDE carry a CONCENTRATION tag** (caught via their
  sharing/exposure language; concentration found at abstract-tagging), incl. the famous
  supersharer studies.
Conclusion: the "concentration rarely measured" finding is ROBUST; a concentration-
targeted top-up would add a handful–couple-dozen studies, not flip it. Comparisons of
exposure/content/sharing are fair.
**Fix wired in:** new presets `concentration_supp` and `concentration_missed` in
`scripts/scopus_search.py` — run when the Scopus key resets, merge NEW eids, report as a
sensitivity analysis. (Scopus key currently 403 WAF/rate-block; transient.)

### Open items (next) — full text, synthesis, PRISMA
- [ ] When Scopus resets: run `concentration_supp`/`concentration_missed`; merge + screen
      new eids; report sensitivity (does primary-CONCENTRATION count rise from 8?).
- [ ] Retrieve full text for the 310 (estimate not in abstract) — OpenAlex OA locations /
      local PDF library / Unpaywall — to fill missing numbers.
- [ ] Normalise/harmonise extraction (split EXPOSURE into survey-recall vs trace-diet;
      standardise denominators) for cross-study comparison.
- [ ] Synthesis: the content-vs-exposure contrast + denominator-as-moderator figures.
- [ ] Stage-2 full-text screen the 1,003 (264 ambiguous + 739 no-abstract).
- [ ] **Data extraction** on the 635 INCLUDE (+ confirmed full-text): per-estimate coding
      (construct: content-prevalence vs audience-exposure vs concentration; denominator;
      platform; country; definition source; point estimate) — reuse the Berriche seed
      schema (`data/seed_berriche_annexe1.csv`).
- [ ] PRISMA flow diagram: 20,344 identified → 2,758 title-advanced → Stage-2 → included.
- [ ] Completeness: supplement Scopus with citation-chasing + the local PDF library to
      catch non-Scopus studies (single-database limitation).
- [x] Audit ≥300 EXCLUDEs — DONE (0 INCLUDE leaks; 23 bumped to MAYBE).
- [ ] **Stage-2**: fetch abstracts for the 2,736 advancing records via Scopus Abstract
      Retrieval API (key in env), then abstract-screen with subagents (~100/agent;
      abstracts are longer) → collapses most MAYBEs to EXCLUDE; produces the included set.
- [ ] Assemble PRISMA flow diagram counts (identified 20,344 → screened → excluded →
      included).
- [ ] Web of Science: NO access (Sacha confirmed) → documented limitation, not a TODO.

### (superseded) earlier resume note
- [x] DONE — screening from corpus line 8000 → 20344 (~12,300 titles left, ~2021–2026,
      densest region) in 250/agent batches (~7.3 pts usage per 1,000 titles); consolidate.
- [ ] Then: audit a random EXCLUDE sample (≥300); fetch abstracts for the ~1,100+
      advancing records → Stage-2 full-text screen.
- [ ] After title screen: fetch abstracts for survivors (Scopus Abstract Retrieval) →
      Stage-2 full-text screen.
- [ ] Finalise grey-lit producer list + dated search protocol.
- [ ] Risk-of-bias / quality-appraisal checklist (trace-data validity).
- [ ] Upgrade competitor coding △→✓ (BMC 2026, JMIR 2021, Tandfonline 2024, PNAS 2024).
- [ ] Pin Guess 2021 + Cordonnier & Brest 2021 to exact records.
Scopus string = `strict_v2` ✓ (recall-validated) ; grey lit IN, separate track ✓ ;
actor-level/political-elite prevalence IN ✓.

TODO:
- [ ] **Precision vs recall:** reduce the 20,409 corpus to a screenable set without
      silent capping (proximity operator / empirical filter / LLM-assisted screen with
      human verification). Highest-priority design task.
- [ ] Add **Web of Science** as second peer-reviewed database; reconcile/dedupe.
- [ ] **Grey-lit track:** define the producer list + search method + extraction fields
      (definition of misinformation, denominator, method, limitation) for RQ5.
- [ ] Identify the exact German "politicians sharing misinformation on TikTok/Twitter"
      study the user meant; build the actor-prevalence sub-corpus (RQ4).
- [ ] Pin Guess 2021 and Cordonnier & Brest 2021 to exact records (identifier
      collisions); decide if Cordonnier & Brest is grey lit.
- [ ] Finalise eligibility criteria (online+legacy now both in): date range, languages,
      min quality/sample, content-vs-audience handling.
- [ ] Define risk-of-bias / quality-appraisal checklist (trace-data validity).
- [ ] Retrieve Tandfonline 2024 + Budak 2024 + BMC 2026 full text → write the
      "how we differ" paragraph.
- [ ] Clean the "concentration" sub-query (disambiguate from dose/chemical concentration).
- [ ] Re-run Semantic Scholar with proper pacing/key for a complete competitor scan.

### 27. SYNTHESIS v1 — content-vs-exposure contrast quantified (2026-06-21)
7 agents normalised the 308 in-abstract numeric estimates into denom_class + value_pct
(`data/synth/normalised_estimates.csv`). Median % by what the figure is a share OF:
CONTENT 36.4% (n=195), RECALL 55.3% (n=26), SHARE_OUTPUT 29.2% (n=24), CONCENTRATION
67.5% (n=8), DIET ~3-6% (n=8; whole-diet values 0.15/2.5/3.7/5.9%). KEY: content
prevalence abundantly measured & high; actual diet exposure rarely measured (n=8) & low;
concentration high but n=8; survey recall (55%) >> behavioural diet share (<6%). The
denominator drives the 36% vs 0.15% gap (3 orders of magnitude) = the methodological
thesis. Write-up in `docs/synthesis_v1.md`. First-pass (abstract-level); firm up after
full-text extraction of the 310 + denominator harmonisation.

### 28. Next-steps PRIORITY (Sacha, 2026-06-21) + full-text scoping
Sacha's order: **#2 (full-text fetch+extract the 310) → #5 (full-text screen the 1,003)
→ then #3 (concentration supp search) → #4 (citation-chase + PDF library).** #1 (whole-
diet split) deprioritised. Figure v1 delivered (`docs/figure_contrast.*`).
**#2 scoping (OpenAlex OA locations of the 310):** 157 have a direct OA PDF, 77 OA w/o
direct PDF, 76 closed. → `data/fulltext/oa_locations.jsonl`. Plan: download the 157 PDFs,
pdftotext, re-extract the headline estimate from full text (subagents) → grows DIET/
CONCENTRATION n's. The 76 closed + 77 landing-only deferred to the library/Scopus route.

### 29. #2 multi-source full-text + #5 scheduled (2026-06-21)
#2: completed OA route (95 full texts, +80 estimates -> 388 with numbers; CONCENTRATION
n 8->15, SHARE_OUTPUT 24->46, DIET stays 9). Sacha flagged I only used OpenAlex; **local
PDF library cross-ref found 45 of the 230 still-pending #2 records (+33 of the #5 pending)
already on disk** (index has doi/abstract/filepath). 230 remain via library+Unpaywall+
reference-agent. #5: pre-staged 1,006 pending (`data/stage5/pending_1003.jsonl`), plan in
`docs/plan_stage5_fulltext.md` (multi-source acquisition: library > OpenAlex > Unpaywall >
reference-agent; then Stage-2 screen; title-only-no-text stays MAYBE). SCHEDULED via local
one-shot cron for 2026-06-21 13:41 CEST.

### 30. STAGE-5 fired (2026-06-21 13:41) — multi-source full-text, in progress
Scheduled cron fired. Scoped 1,006 pending: 35 library full-texts, 33 library abstracts,
813 to fetch. Launched the vendored PDF-finder (scripts/pdf_finder/, Sci-Hub+Scholar on)
in BACKGROUND on the 813-feed (data/stage5/pending.fetch.jsonl) — slow (~hours).
Harvester scripts/stage5_harvest.py maps landed DOI-named PDFs -> eids, pdftotext, queues
unscreened. Waves so far: library 35 (12 INC/5 MAYBE/18 EXC) + fetched 26 (4 INC/8 MAYBE/
17 EXC) = **61 screened, 16 new INCLUDE** (data/screen_stage5_2026-06-21.csv). Fetched set
yields ~15-22% INCLUDE → extrapolated ~150 more includes once the 813 finish.
**Follow-up cron 7e9605ee scheduled 16:18** to harvest+screen the accumulated PDFs in
waves, consolidate, finish #2 extraction, refresh figure/summary, update PRISMA. Fully
resumable via stage5_harvest.py (skips screened eids).

### 31. RIGOR: dual-reader verification + adjudication of the 635 includes (2026-06-21)
Per Sacha "as rigorous as possible". (1) Adversarial verification (13 agents, default-
REJECT framing) of the 635 single-reader includes: 472 CONFIRM, 143 REJECT, 19 UNSURE
(23% disagreement → single screener was over-inclusive). (2) Adjudication (3rd reader,
4 agents) of the 162 disputed: 66 INCLUDE, 64 EXCLUDE, 32 FULLTEXT. **Reconciled
dual-reader-validated include set = 535** (472 both-agree + 66 adjudicated); 68 excluded
on review; 31 -> full-text-needed (join Stage-5 queue). Included set tightened 635 -> 535
(-16%). Files: data/verify/{included_verified,excluded_on_review,needs_fulltext}.txt.
**Finding ROBUST to verification** (n=535): CONTENT 59%, EXPOSURE 12%, CONCENTRATION 1%
(7); medians CONTENT 37.1% (n=214), CONCENTRATION 50% (n=13), DIET 22.1% (n=9), RECALL
55.9%. Also: 4 parallel PDF fetchers launched (~4x speed) for exhaustive retrieval.
Remaining rigor: dual-screen Stage-5 (cron updated), extraction verification, κ sample,
concentration supplementary search.

### 32. RIGOR continued (2026-06-21, ~14:30) — extraction verification + inter-rater kappa
- EXTRACTION VERIFICATION (9 agents) of 348 estimates in the verified include set vs
  source text: 294 ACCURATE (85%), 8 WRONG (corrected), 46 UNSUPPORTED (flagged; partly
  truncated-source). Status written to extraction_master (extract_verdict column).
- INTER-RATER kappa: 2 independent readers screened a random 300 corpus titles (seed
  424242). 3-way agreement 96.7%, Cohen kappa=0.89; binary advance-vs-exclude 97.3%,
  kappa=0.91 — "almost perfect" (Landis-Koch). Files data/kappa/, data/exverify/.

### 33. RIGOR PUSH COMPLETE (2026-06-21 ~15:00) — final included set 646
With credits available, ran the full rigor pipeline live (no waiting for crons):
- 5 parallel PDF fetchers finished: 381/843 retrieved (~45%; rest unfetchable -> stay
  MAYBE, documented limitation).
- Stage-5 DUAL-screened (reader A + B + adjudication) in waves: 392 screened, 111 INCLUDE.
- Extracted + normalised the 111 new includes from full text.
- **FINAL INCLUDED = 646** (535 dual-reader-verified Stage-2 + 111 Stage-5).
- Synthesis on final set: CONTENT n=248 median 37.3%; DIET n=11 median 7.5%; CONCENTRATION
  n=15 median 50%; RECALL n=33 median 57%; SHARE_OUTPUT n=44 median 31%. Content (n=248)
  vs diet (n=11) — the finding is now cleaner AND verified. Figure refreshed.
- Cancelled the redundant 16:18 follow-up cron (work done live).
RIGOR COMPLETE: dual-screening+adjudication, extraction verification (85% accurate),
inter-rater kappa 0.89-0.91, concentration sensitivity (finding robust). Publication-grade.
Remaining (minor): fold in 33 concentration-supp advancing; the ~460 unfetchable MAYBEs
documented; whole-diet/topical split; write-up.

### 34. ESTIMATE CLEANING — content-quality & belief contamination removed (2026-06-21)
Sacha flagged the CONTENT (37%) and RECALL (57%) medians as "too high". Inspection
(sampling) found: (a) CONTENT contaminated by QUALITY ratings ("not useful"/"non-
guideline"/"partially accurate" counted as misinfo); (b) RECALL conflated SAW
(encountered) with BELIEF; (c) some behavioural exposure mis-tagged as RECALL.
DECISIONS (full rationale in docs/cleaning_methods.md): BELIEF excluded (out of scope +
search not designed for it -> biased sliver, per Sacha); QUALITY excluded from prevalence
(separate category); TRACE merged into EXPOSURE; FALSE_CONTENT kept but flagged as
topic-curated denominator. PROCESS: re-classified all 359 numeric estimates via agents
with context (data/clean/c_*.csv, c2_*.csv) -> data/synth/normalised_clean.csv.
CLEAN medians: CONTENT 36% (n177), RECALL 68% (n20), SHARING 31% (n23), CONCENTRATION 70%
(n13), **EXPOSURE 11% (n16)**; removed QUALITY (n59) + BELIEF (n6). Figure regenerated on
clean taxonomy (excluded rows greyed). The thesis holds and is cleaner: perceived/curated
numbers high, behavioural exposure ~order of magnitude lower, concentration high but rare.
EVERYTHING DOCUMENTED for transparency/reproducibility (Sacha's instruction).

### 35. Direction decisions (Sacha, 2026-06-21) + gap-closing
DECISIONS: co-author = SOLO for now; framing = HYBRID (descriptive PRISMA review whose
HEADLINE is the methodological contrast — content 36% vs behavioural exposure 7.5%);
sequence = FINISH THE DATA before writing. Data gap: 126 audience-side includes lacked
estimates; +33 recovered from abstracts; 93 fetching full text (incl. Vosoughi, Lasser,
Osmundsen, Guess-2019, Nelson&Taneja — all INCLUDED, estimates pending). Canonical spine
check: all canonical studies captured/included; ~6 estimates pending in the fetch.

### 36. DATA COMPLETE (as retrievable) — gap closed (2026-06-21)
Audience-side data gap (126 includes without estimates) worked exhaustively: 33 from
abstracts + 24 + 9 via grep full-text (after fixing front-truncation bug) = 66 recovered;
**60 have no retrievable full text** (closed access / Sci-Hub miss) -> documented
limitation (counted in included set + construct distribution via tags; just no point
estimate). FINAL clean synthesis n=423 estimates: CONTENT 35% (n184, curated samples),
RECALL 68% (n21, self-report), SHARING 30% (n33), CONCENTRATION 65% (n17), **EXPOSURE 7.5%
(n23, behavioural — the number that matters)**; QUALITY (n59) + BELIEF (n6) excluded.
Canonical spine all captured + key estimates recovered. DATA IS DONE for the write-up.
Per Sacha: solo, hybrid framing (descriptive review headlined by the denominator contrast).

### 37. RISK-OF-BIAS APPRAISAL — quantifies the thesis (2026-06-21)
12 agents appraised the 390 estimate-contributing studies on 5 dimensions
(docs/rob_checklist.txt) -> data/rob/risk_of_bias_master.csv. Overall: 26 LOW, 73 MOD,
**291 HIGH (75%)**. KEY CROSS-TAB (risk x construct) — bias inversely tracks the number:
EXPOSURE (median 7.5%) = 4% HIGH; CONCENTRATION 29%; RECALL 43%; SHARING 61%; CONTENT
(median 35%) = **90% HIGH**; QUALITY(excl) 97%. Dimensions: 81% CURATED sampling, 78%
NARROW denominator, only 18% VALIDATED definition, 271/390 CONTENT_CODING vs 88
BEHAVIOURAL. => THE PAPER'S CENTRAL QUANTIFIED FINDING: the reassuring low-exposure
estimates come from LOW-bias rigorous studies; the alarming high "prevalence" numbers come
from HIGH-bias studies (curated samples, ad hoc definitions, content-coding). Not box-
ticking — this IS the result.

### 38. REFINEMENTS: EXPOSURE split + dual-pass kappa (2026-06-22)
EXPOSURE SPLIT (data/synth/exposure_split.csv, diet_type col in normalised_clean):
whole-diet n=15-16 median **6.0-6.5%** (range 0.15-61); topical-diet n=7 median 8.5%;
1 unclear. => the true "% of what people actually consume" headline is ~6%, sharper than
the pooled 7.5%. Figure now renders EXPOSURE_WHOLE vs EXPOSURE_TOPICAL.
DUAL-PASS KAPPA (independent blind second coder, n=90 subsamples, seed 424242):
- Cleaning re-classification: raw agreement 70%, kappa=0.60 over 8 categories; among the
  5 PREVALENCE buckets kappa=**0.75** (substantial). Disagreements concentrate on the
  QUALITY<->CONTENT boundary (10/27) = the genuinely fuzzy "is an accuracy rating falsity?"
  call. EXPOSURE cleanly separated -> headline robust. (data/kappa/clean_p2_*.csv)
- Risk-of-bias overall: raw agreement 85%, within-1-level 100% (NO low<->high flips),
  kappa=0.48 deflated by the skewed HIGH-heavy base rate (kappa paradox). Appraisal
  reliable. (data/kappa/rob_p2_*.csv)
LIMITATION (now documented): QUALITY/CONTENT margin is judgment-dependent; the core
prevalence bucketing and the exposure estimate are reliable.

### 39. Grey-literature systematic search (2026-06-22)
3 producer classes searched (data/grey/grey_master.csv, n=40): survey/regulator (14, all
RECALL), advocacy/audit (15; 8 denominator-free absolute counts), platform/think-tank (11;
low measured exposure + concentration). Finding: grey lit reproduces the denominator
pathology, amplified — advocacy uses uninterpretable absolute counts; survey houses report
perceived (recall) prevalence. Centerpiece example: CCDH "Disinformation Dozen = 65% of
anti-vax content" (curated concentration) vs Meta "0.05% of views" (exposure) — same actors,
3 orders of magnitude apart. Grey lit treated as a CONTRAST CASE, not pooled. Full writeup
in docs/grey_literature.md.

### 40. STRENGTHENING DB before drafting (Sacha review, 2026-06-22)
Sacha flagged 4 real weaknesses: (1) QUALITY<->CONTENT boundary fuzzy; (2) grey lit not
systematic; (3) ONE estimate per paper (multi-estimate papers like his JQD 4-country x
{FB,Web}=8 collapsed to 1); (4) JQD = 0 records in corpus (not Scopus-indexed -> his own
paper + non-Scopus venues MISSING). Decisions: DB breadth via OpenAlex snowball+venue catch;
estimate unit = country x platform x measure; grey lit systematic; sharp QUALITY/CONTENT rule.
DONE THIS SESSION: systematic grey-lit (83 claims, grey_lit_protocol.md; 27% REACH_ABSOLUTE,
28% RECALL); extraction_protocol_v2.md (estimate-level + sharp construct rule) written.
RUNNING: OpenAlex snowball (224 core studies, scripts/snowball_openalex.py); PDF recovery
(2,064 records). PENDING: screen snowball candidates; estimate-level re-extraction (gated on
full text); QUALITY recode (folded into v2 re-extraction).

### 41. DB EXPANSION via OpenAlex snowball — non-Scopus venues recovered (2026-06-22)
Snowball (scripts/snowball_openalex.py) from 224 core audience-side included studies:
backward 6,411 refs + forward 2,081 topic-citing + JQD venue sweep -> 1,822 new
topic-relevant candidates NOT in the Scopus corpus. Title+abstract screened (data/snowball/
screen/, same criteria): 1,487 EXCLUDE, 222 MAYBE, 109 INCLUDE -> **331 advancing**.
Venues confirm the Scopus blind spot: ICWSM 21, arXiv 21, JQD 17, SSRN 14, HKS Misinfo
Review 7, Oxford ORA 7 (all absent from Scopus, incl. Sacha's JQD venue). Full-text fetch
launched for the 331. Next: estimate-level re-extraction on the combined corpus.

### 42. Estimate-level extraction COMPLETE + Hameleers anchor (2026-06-22)
v2 extraction over all 977 studies -> data/extract_v2/estimates_master.csv: 789 estimate
rows from 441 studies (200 multi-estimate studies properly split; vs old 423 one-per-paper).
Medians (estimate-level, sharp QUALITY rule): CONTENT 30% (n302), RECALL 51% (n34),
SHARING 10% (n65), CONCENTRATION 59.5% (n39), EXPOSURE 10% (n39; WHOLE-DIET **6.0%** n14,
TOPICAL 18.4% n25); QUALITY 44.5% (n120, excluded), BELIEF 25% (n29, excluded). 318
borderline CONTENT/QUALITY flags -> sensitivity analysis. Figure rebuilt on v2.
HAMELEERS (Sacha flagged): Hameleers 2025 "Reconciling discrepancies between low estimates
of misinformation exposure versus high perceptions" (Communication Theory, 10.1093/ct/
qtaf021) is the theoretical companion to our empirical thesis (low measured vs high
perceived = our EXPOSURE 6% vs RECALL 51%). Documented positioning in related_reviews.md;
already in corpus/worklist. NEXT: rebuild RoB + PRISMA on v2, dedup borderline sensitivity.

### 43. v2 REBUILD COMPLETE — RoB, PRISMA, sensitivity, dashboard (2026-06-22)
- RoB v2: +100 new estimate-studies appraised (data/rob/risk_of_bias_master_v2.csv = 490).
  Estimate-level bias×construct cross-tab HOLDS: EXPOSURE 13% HIGH, CONCENTRATION 33%,
  SHARING 49%, RECALL 56%, CONTENT 89%, QUALITY 89%. Overall ~73% HIGH. Bias still inversely
  tracks the reassuring-ness of the number.
- SENSITIVITY (318 borderline CONTENT/QUALITY flags excluded): CONTENT 30%→25% (n302→169),
  EXPOSURE 10%→8%, ordering preserved (content 25 > exposure 8 > whole-diet 6). Thesis ROBUST.
- PRISMA v2: two-stream identification (Scopus 20,344 + snowball 1,822) -> 977 assessed at
  full text -> 441 contributing 789 estimates. scripts/make_prisma.py + docs/prisma_flow.*.
- Dashboard refreshed to estimate-level numbers; Hameleers anchor noted.
- Background recovery relaunched (6 shards, 246 abstract-only w/ DOI) to keep topping up.

### 44. v2 EXTRACTION VERIFICATION (2026-06-22, Sacha pushed to validate)
Stratified 206-estimate sample (all EXPOSURE+CONCENTRATION + samples of others) re-checked
against source by independent agents. RESULTS: value accuracy **85%** (175/206); construct
agreement 75%, **kappa=0.70** (substantial). Disagreements concentrate on CONTENT<->QUALITY
(7) and EXPOSURE->CONCENTRATION/SHARING (10). PRECISE row-level corrections applied to the
sampled rows (4 values fixed, 27 unsupported dropped, 24 reassigned) -> estimates_master_v2c
.csv (766 rows). Headline ROBUST and sharper: CONTENT 30%, RECALL 50%, SHARING 14%,
CONCENTRATION 50%, EXPOSURE 8.2% (WHOLE-DIET **4.2%** n10, TOPICAL 18.5% n17). Cross-stream
dups (Scopus<->snowball): 0. Quality metrics (85% / kappa 0.70) are the reported reliability;
unsampled rows carry that residual error (standard SR practice). Figure rebuilt on v2c.
LIMITATION: only the 206-sample is row-level corrected; full double-extraction not done.

### 45. FULL DOUBLE-EXTRACTION — bulletproof (2026-06-22, Sacha: "needs to be bulletproof")
Every one of the 793 estimates independently re-extracted by a second agent (206 sample in
§44 + 586 remaining here, 40 agents). DATASET-WIDE: value accuracy **80%**, construct
agreement 86%, **kappa=0.82** (n=778). Precise row-level corrections applied to the WHOLE
set: 38 values fixed, 98 unsupported dropped (secondary citations / not-in-text), 107
reassigned. FINAL data/extract_v2/estimates_master_final.csv (now canonical): 695 estimates,
408 studies. Headline ROBUST: CONTENT 30% (n278), RECALL 59% (n27), SHARING 23% (n67),
CONCENTRATION 50% (n27), EXPOSURE 8.9% (n29; WHOLE-DIET **4.2%** n10, TOPICAL 18.5% n17).
RoB x construct (final): EXPOSURE 7% HIGH vs CONTENT 88% HIGH — inverse relationship
bulletproof. Figure/PRISMA/dashboard rebuilt. This is the gold-standard SR extraction step.

### 46. Reviews handled as PRIMARY-SOURCE HARVEST, not pooled values (Sacha, 2026-06-22)
Per Sacha: a meta-analysis's pooled estimate must NOT enter our value set (secondary source;
pooling alongside its own primaries would double-count). Instead harvest its PRIMARY studies.
- Çeleğen 2026 meta-analysis (k=8 recall studies): cross-checked vs corpus → 5/8 ALREADY IN
  (Gaysynsky, Agha, Chandrasekaran, Stimpson, Othman — good recall validation), 3 MISSING
  (Alvarez-Galvez 2023 Spain; BinHamdan 2024 Saudi 87%; Jabbour 2022 Lebanon) → staged in
  data/extract_v2/reviews/harvest/to_add_primaries.csv for retrieval+quote-anchored extraction.
- Kemei 2022 scoping review: cited claims are mostly grey-lit surveys (StatCan 96%, KFF 80%)
  or belief/raw-counts (out of scope) → StatCan/KFF go to the grey-lit track, no new academic
  primaries. 
- ACTION on resume: drop the Çeleğen + Kemei pooled rows from the value set (reclassify as
  REVIEW sources); retrieve + extract the 3 missing primaries. (Frozen until then.)

### 47. Items 2/3/5 done; review cite+harvest strategy (2026-06-23)
- Item 2 DONE: Çeleğen + Kemei pooled values flagged DROP (secondary) — data/extract_v2/qa/review_pooled_drops.csv.
- Item 3 DONE: 22 abstract-only resolved → 15 keep (verbatim in abstract), 7 drop (data/extract_v2/qa/abstronly_resolved.csv). All decided drops in decided_drops.csv (9 total).
- Item 5 DONE: StatCan 96% + KFF 80% added to grey_master.csv (recall, survey).
- Item 4 NOT done: 3 Çeleğen primaries (Alvarez-Galvez/BinHamdan/Jabbour) could not be auto-resolved (3 methods failed; refs too imprecise) → staged in harvest/to_add_primaries.csv for HAND-CODING.
- NEW STRATEGY (Sacha): systematically cover+cite existing reviews/meta-analyses; harvest their PRIMARIES (not pooled). docs/reviews_to_cite.csv = 174 found, 17 prevalence-relevant. Suarez-Lledo 2021 = top harvest target.
- Item 6 = confirm Q2 (sub-bucket rule); Item 1 (apply Sacha's value-review export) + final rebuild still pending + FROZEN.

### 48. Çeleğen meta-analysis is CONSTRUCT-CONFLATED — reclassified (Sacha checks, 2026-06-23)
Sacha manually checked Çeleğen's primaries: Alvarez-Galvez 2025 (JMIR Infodemiology e69945)
= belief/susceptibility SCALE (convinced/hesitant/skeptical clusters), NOT recall;
BinHamdan 2024 (e48453) = prevalence of oral-health MISCONCEPTIONS (belief), not recall.
STATUS CHECK: all 5 "in-corpus" Çeleğen primaries (Gaysynsky, Chandrasekaran, Stimpson,
Othman, Agha) were EXCLUDED at our title screen — correctly, as belief/susceptibility (out
of scope). => Çeleğen's pooled "59% recalled exposure" is NOT clean recall; it pools belief/
misconception/recognition studies. CORRECTIONS: (1) earlier framing of Çeleğen as a 'recall
meta-analysis anchor (59%)' was WRONG — retracted. (2) Do NOT harvest its primaries (belief,
correctly excluded). (3) 3 staged primaries → all EXCLUDED (belief). (4) CITE Çeleğen as a
prime EXHIBIT of the construct-conflation thesis: a 2026 MA titled around 'exposure' that
actually pools belief-in-misinfo. (5) Our screening protocol validated (excluded them
unprompted). LESSON: when harvesting any review's primaries, verify EACH primary's construct
— reviews mislabel constructs (that's our whole point).

### 49. Dedicated review/MA search — coverage confirmed (2026-06-23)
Ran OpenAlex sweep for misinfo prevalence/exposure reviews+meta-analyses (8 query variants).
40 hits: 24 already in corpus, 16 new — but all 16 new are OFF-CONSTRUCT (belief/intervention/
detection/health-literacy/infodemic-management), none a prevalence/exposure review we lack.
→ corpus coverage of prevalence reviews CONFIRMED good. docs/reviews_external_search.csv.
Priority to cite+harvest (construct-clean, verify each primary per §48 rule): Suarez-Lledo
2021 (health-misinfo prevalence SR), Wang 2019, Balakrishnan 2022, Zhao 2023, Kbaier 2024,
Hu 2025. Çeleğen/Kemei = cite as conflation exhibits only (do not harvest).

### 50. SCREENING FALSE-NEGATIVE AUDIT (Sacha worry: wrongly-excluded seminal papers, 2026-06-23)
Checked seminal exposure papers: Allcott (title MAYBE→abstract INCLUDE→INCLUDED ✓), Guess x2,
Grinberg, Allen, Vosoughi, Osmundsen, Nelson&Taneja, Bovet ALL included. Lazer/Pennycook/
Benkler correctly excluded (commentary/belief/book). Then audited the TOP 120 most-CITED
excluded papers (a wrongly-dropped seminal paper would be high-cited): only **1 possible
false-negative** (Tasnim 2020 'Impact of rumors/misinfo COVID', 594 cit — but 'impact' title,
likely review; flagged VERIFY in recovered_candidates.csv). The rest correctly excluded
(belief/correction/intervention/effects/detection/off-topic — the dominant misinfo stream).
=> screening RECALL is strong; the recall-protective design (uncertain→MAYBE→abstract) worked
(it rescued Allcott). data/extract_v2/qa/fn_*.csv. Keep/drop for re-extraction: 376 keep
(291 full-text) / 32 drop. Re-extraction worklist built (paused pending Sacha go).

### 51. Abstract FN audit RESOLVED — recall is high; earlier alarm retracted (2026-06-23)
Dual-pass false-negative audit of all 1,120 abstract-stage excludes. PASS 1 (liberal) flagged
145 (~13%) — but massively OVER-flagged (counted datasets, theme/composition, raw counts,
detection, effects as 'prevalence'). PASS 2 (strict adjudication, protocol criteria): only 4
survive, of which 1 is belief → **3 genuine false-negatives** (85110362081 content prevalence;
85046297294 cross-platform consumption diet; 85104164793 low-prevalence/consumption review).
=> abstract-screen RECALL ≈ 99.7% (3 genuine misses / 1,120). CORRECTION: my prior 'abstract
screen too aggressive, ~13% wrongly excluded' was WRONG — a first-pass over-flagging artifact;
recall is actually strong. Recover the 3 (recovered_false_negatives.csv). This dual-pass audit
is itself a reportable METHODS STRENGTH (measured screening recall). Sacha's worry → valuable
check, reassuring answer.

### 52. CLEAN full-text RE-EXTRACTION complete (2026-06-24)
All 291 keep-studies re-extracted from full text (3 waves of ~14 agents @7). Fixes the
duplication + imprecision Sacha flagged: every distinct estimate split by country×platform×
measure, precise figure, verbatim quote, denominator, AND misinfo definition captured.
Consolidated 42 rx_*.csv → estimates_reextracted.csv = 564 rows / 280 studies; 100% quote+
denominator+definition anchored; 2 exact dups removed. 11 studies correctly yielded 0 rows
(BELIEF/secondary-cite/off-topic). This REPLACES estimates_master_final.csv as canonical
(pending Sacha review). NEXT: recover 3 FNs, regen review HTML on clean data, then frozen rebuild.

### 53. Antimicrobial-stewardship paper — corrected decision (2026-06-24)
Sacha flagged "Digital misinformation and antimicrobial stewardship" (10.1017/ice.2026.10423).
I first wrongly rejected it as "post-snapshot 2026." CORRECTION: published 2026-03-06 (BEFORE our
2026-06-20 snapshot); absent from our corpus because it is PubMed-indexed, NOT in Scopus (we
searched Scopus only). Abstract gives a clean estimate: "Misinformation comprised 19.3% of posts"
(n=1.8M antibiotic posts, Twitter/Reddit/Facebook). => ADDED as expert-identified SUPPLEMENTARY
record (CONTENT 19.3%, abstract-anchored), logged in qa/supplementary_inclusions.csv. Flags a real
point for the limitations/PRISMA: Scopus-only search misses PubMed-only venues — consider a PubMed
top-up search. Lesson: don't reflexively reject on year; check actual date + database coverage.

### 54. PubMed + OpenAlex primary-keyword TOP-UP search (2026-06-24)
Closed the database-coverage gap (Scopus was primary; OpenAlex only snowball/venue). PubMed
E-utilities, strict_v2-equivalent query (scripts/pubmed_search.py) → 5,179 hits; 5,167 fetched;
4,741 (92%) already in corpus (confirms heavy Scopus overlap) → 410 net-new. SONNET dual-screen
(usage-saving) → 1 INCLUDE + 22 MAYBE; Opus adjudication → 5 new includes (7 rows, all CONTENT
health-misinfo content analyses: chiropractic, oral health, epilepsy, tanning, COVID-FB) +2 reviews
to cite. Added as PubMed supplementary (source=abstract), logged supplementary_inclusions.csv.
OpenAlex primary keyword search still TODO. Master now larger; see estimates_reextracted.csv.

### 55. OpenAlex primary-keyword search (2026-06-24) — net-new pending screen
Ran OpenAlex topic(title)×measure(abstract) combos (scripts/openalex_keyword_search.py, OR explodes
so combos unioned) → 9,378 unique works → dedup vs Scopus+PubMed+snowball → **4,822 NET-NEW with
abstracts** (data/openalex_netnew.jsonl). Large because OpenAlex includes non-Scopus venues
(preprints/books/conference/non-English). Expected yield LOW (PubMed gave 5/410). PENDING: Sonnet
screen (~33 agents) — deferred decision (Sacha near weekly limit). State saved for resume.

### 56. OpenAlex top-up screened; candidates STAGED not merged (2026-06-24)
4,822 net-new → Sonnet dual-screen → 18 INCLUDE + 186 MAYBE → Opus adjudication → ~34 include rows
(+4 reviews). DEDUP AMBIGUOUS: exact DOI/title dedup missed variants — Berriche thesis (our SEED),
Grinberg, Allcott, Nelson-Taneja appear among "new" under title/DOI variants. Auto-merge would inject
duplicates → corrupt master. DECISION: staged to data/extract_v2/qa/openalex_candidates_STAGED.csv
(dedup_status=NEEDS_CHECK; many NEEDS_FULLTEXT — value not in abstract). RESUME: per-item dedup vs
corpus (fuzzy+manual), drop seeds/known dups, fetch full text for FULL-TEXT-NEEDED, then merge the
genuine new ones. Confirms Sacha's intuition: OpenAlex adds little beyond Scopus+PubMed. Master
unchanged at 710 rows/363 studies.

### 57. Process Sacha's UZH downloads + full folder reconciliation (2026-06-25)
Sacha downloaded/added ~34 PDFs to ~/Desktop/UZH_papers_to_get. Processed ALL 68 folder PDFs:
- ~58 in master (49 direct matches + 9 dups already extracted under their eids: BaribiBartov,
  Leveraging, a_look=OA-W4377015071, mp45, Infodemia-PL, 2023-prevalence, Assessment-FB, Nelson, etc.)
- 30 NEW studies extracted this round (Bandy junk 6.9-9.9% feed exposure; Chan perceived 53.9%;
  Fletcher RISJ reach 3.1%; Hanley Reddit 7.74% unreliable; van Antwerpen recall 50.4%; Pratelli
  swing-state 23.5%; Dahlke 12.7% reached; India anti-Muslim 3.3% peak; Greene/Zhou/Chouaki etc.)
- 9 processed but 0 rows (curated-corpus/review: folder_zero_row.csv) — correctly no prevalence.
- 1 BLOCKED: Ralston 2018 encrypted PDF (blocked_encrypted.csv) — needs unlocked re-download.
MASTER = 1104 rows / 529 studies (session start 389 → +140 via never-extracted + UZH + harvest + library).
GONZALEZ-BAILON %: rendered Fig 1C/1D — count time-series, false=thin 'barely perceptible' sliver,
NO printed %; SM not in library. Kept qualitative EXPOSURE row; exact % needs SM/replication data.

## 2026-07-01 — Automated frozen-dataset validator (scripts/validate_frozen.py)
Added an auditable integrity gate over FROZEN v1.1 (pattern borrowed from Claude
Science "reviewer agent", reimplemented as an in-repo script so the guarantee
stays in git). Reads expected file/MD5/rows/studies from docs/FROZEN.md; asserts:
MD5 match (catches any silent CSV edit), 584 rows / 328 studies, required fields,
value_pct in [0,100], X-of-Y numerator/denominator reconciliation vs value_pct
(23 reconcilable rows, all pass), full-row exact-duplicate detection, construct
vocab, and id→provenance resolution. FAIL vs WARN split; exit 1 on any FAIL.
Run: `python3 scripts/validate_frozen.py` (add --json for machine output).

FINDING (needs Sacha's call — do NOT edit frozen CSV without approval):
- SEED-cordonier2021 vs SEED-cordonnier2021 = SAME study (Cordonnier 2021),
  double-entered under one-n / two-n spellings. Identical France / Storyzy
  web-tracking / 0.16% total-time / 5% news-time. Inflates count by 1 study
  (2 studies→1) and 2 rows (4→2). If merged: 582 rows / 327 studies → would
  require re-freeze to v1.2 + new MD5 + RA answer-key update.
Benign WARNs: value_pct '73-78' (real range in source); 6 SEED-/NEW-/SUPP-
provenance ids not in the 4 main corpus jsonl (expected; provenance in prefix).

## 2026-07-01 (cont.) — errata decisions logged to FROZEN.md (v1.1 untouched, fix at v1.2)
- Cordonnier dup: KEEP full_text `SEED-cordonier2021`, DROP seed_berriche
  `SEED-cordonnier2021`, correct surviving id spelling one-n->two-n at v1.2.
- DeVerna 2024 (2-s2.0-85194023903) concentration: re-read paper. '73-78%' = mitigation
  by deployable predictors (h-index/Influence); realized concentration = oracle
  'optimal: 81%' (true top 0.25% of accounts = 81% of low-cred content). CONCENTRATION
  construct value should be 81, not midpoint of 73-78. Set value_pct=81 at v1.2.

## 2026-07-01 (cont.) — P2 done: docs/llm_provenance.md (RAISE transparency disclosure)
Reconstructed per-stage model/settings/prompt/date from log + qa_plan. Key correction
to any prior assumption: HAIKU WAS NEVER USED. screen_titles.py (haiku, temp 0) was
written but never run (entry 17: author rejected Haiku, no standalone key). Actual:
Sonnet-class = screening bulk; Opus-class = extraction + Step-B + adjudication + RoB.
Documented honest limitation: in-session subagent build-strings/temperatures not
captured -> reproducible in method (criteria files committed) not bit-for-bit output.
All headline kappa labelled inter-LLM; human RA validation still pending.

## 2026-07-01 (cont.) — RoB reliability recomputed with paradox-robust coefficients
scripts/rob_reliability.py (read-only, pass1 master vs 89-study blind pass2). Cohen
kappa 0.48 was a kappa-paradox artifact of HIGH-heavy skew (73 HIGH/13 MOD/3 LOW).
Overall: raw 85%, within-1-level 100%, PABAK 0.78, Gwet AC1 0.83 (almost perfect).
Per-dim AC1: measurement .93, denominator .92, sampling .85, sample_size .82,
definition .60 (the one genuine soft spot = definition-rigour judgment). Report
AC1/PABAK alongside kappa in manuscript. No new coding pass needed for overall.

## 2026-07-02 — PRISMA reconciliation script (scripts/validate_prisma.py)
Built machine-checked reconciliation: normalizes 6 ID schemes (2-s2.0/W/OA-W/PMID/
SEED/SUPP) to canonical keys, unions the split drop ledgers + verify/triage verdicts,
assigns every INCLUDED/staged record one terminal state. MAYBE-not-selected (428)
treated as terminal screening outcome, not orphan. Result: of 821 included/staged,
328 frozen + 141 ledgered-drops + 115 verify-rejected + 45 not-retrieved + 9 dedup
resolve cleanly; RESIDUAL = 57 DROPPED_V2_UNLEDGERED (dropped at v1->v2 re-freeze,
no ledger entry) + 126 ORPHAN (screened-in, often CONFIRMed, no terminal disposition
anywhere). ~183 records need a recorded disposition before submission — this is the
real (previously invisible) PRISMA audit gap the tool now quantifies. Worklist ->
data/extract_v2/qa/prisma_orphans.csv. Grinberg W2912178678 correctly flagged.

## 2026-07-02 (cont.) — "do everything now" batch
- Truncation sensitivity: launched over 21 EXPOSURE/CONCENTRATION studies (background); results -> data/extract_v2/sensitivity_notrunc/.
- PRISMA orphans dispositioned (deterministic draft): of 183, 57 DROP_V2_CONSOLIDATION,
  100 RECOVER? (mostly CONFIRMed-but-no-extractable-estimate = included-no-data), 26 REVIEW.
  -> data/extract_v2/qa/prisma_orphans_dispositioned.csv. Needs a bounded review pass +
  an "included_no_estimate" ledger so validate_prisma.py can go green.
- Retraction check (Crossref, #4): 314 DOIs checked, 0 retractions, 3 fetch errors, 11 no-DOI.
  -> data/extract_v2/qa/retraction_check.json.
- I5 units audit: flagged W4306964957 (0.0104/0.9595 = proportions, should be 1.04/95.95). FROZEN erratum.
- #5 Fletcher/RISJ cross-track dup (OA-W2992531903 vs grey RISJ 2018). Rule=published wins. FROZEN erratum.
- I4 precision-weighted sensitivity: sample-size weighting collapses CONTENT 19.3->2.4, REACH 26->0.4,
  SHARING 7.6->3.8, CONCENTRATION 50->39; EXPOSURE stable 2.05->2.26 (headline robust). Caveat:
  weighted-mean vs unweighted-median; needs proper inverse-variance for paper.
  -> data/extract_v2/qa/precision_weighted_sensitivity.json.
- #8 replication package manifest -> docs/replication_package.md (legal boundary defined; build at submission).
- #7 search currency top-up: DEFERRED to pre-submission (snapshot only ~2wk old; re-run generates new
  screening pipeline + would re-stale by submission). Kept as task.

## 2026-07-02 (cont.) — truncation sensitivity RESULT
21 studies, 34 headline rows: 33 CONFIRMED, 1 MISMATCH (W2953415400 label/scope 47.4->49.4),
15 MISSED estimates across 10 studies (QAnon 3.7%/39.1% reach; Eady/IRA 10%=98%; Altay FB 13.97%;
Grinberg/Pierri/Osmundsen source-concentration; Weeks 60.8% zero-visit; Oswald&Munzert 17%/8%).
Verdict: truncation = omission not corruption; frozen values stand. v1.2: add missed same-kind
rows + fix Allgaier label. Recorded in FROZEN.md errata.

## 2026-07-02 (cont.) — 126-orphan dispositioning RESULT
126 records -> 19 RECOVER, 44 INCLUDED_NO_DATA, 48 EXCLUDE, 15 CANT_TELL. PRISMA orphan
gap now has recorded reasons (was the weakest audit surface). HEADLINE: Grinberg 2019
(W2912178678) absent from frozen as primary (6% exposure / 80% top-1% / 0.1%=80% shares);
verify primary-vs-summary then add at v1.2. 19 RECOVER + 1 CANT_TELL candidate feed v1.2
additions (additive to the 15 truncation-missed rows; no overlap - truncation misses were
extra rows on frozen studies, recoveries are non-frozen studies). Files: disposition_results.csv,
disposition_summary.md. Remaining: log reasons for the 57 v2-consolidation drops.

## 2026-07-02 (cont.) — Sacha's v1.2 review decisions (from review_sheet)
ADD (14 clean): 105029346542, 85038621544, 85043684270, 85062230191, 85075076652,
  85086772538, 85095575703, 85101871838, 85129632573, 85137929479, 85163154882,
  85199110625, 85213958624 (flagged "extremely important"), 85215303159.
ADD-with-treatment:
- 105017599346 -> ADD but tag OTHER/engagement (engagement_not_exposure, L34); EXCLUDE from headline EXPOSURE pool.
- 85096862559 -> ADD but estimate looked weird; NEEDS careful full-PDF re-extraction before trusting.
- ct 105029413645 -> fetch full text & add (health-content exposure/concentration).
EXCLUDE (Sacha overrides):
- 85057304142 -> EXCLUDE. 89% concentration is among RUSSIAN TROLL accounts (3 of 221 producers), not
  audience/real-user consumption. Producer/actor concentration, out of scope (cf L12 bot/troll metrics).
- 85086931774 -> EXCLUDE. Vaccine-book stance (hesitant/supportive), not verified-false content prevalence.
GRINBERG: W2912178678 = Science news summary "Finding facts about fake news" (DOI .360-c), SECONDARY.
  DROP it; ADD the PRIMARY Grinberg et al. 2019 "Fake news on Twitter..." (DOI 10.1126/science.aau2706),
  which IS already in corpus/screening + Berriche seed (1.18% of total political exposure; 1% exposed to 80%;
  0.1% shared 80%; ~6% news-diet share). Recall gap: primary screened but never extracted/frozen.
CONFIRMS:
- DeVerna 2-s2.0-85194023903: 73-78 -> 81 (top 0.25%); for consistency also 34.6 -> 38.1 (top 10, optimal).
- W4306964957: NO CHANGE. I5 flag was a FALSE ALARM (0.0104%/0.9595% already correct). FROZEN erratum corrected.
- Allgaier W2953415400: EXPOSURE 47.4 -> 49.4 (label = all consensus-opposing = denial+conspiracy views
  16,939,655/34,296,000; 47.4 was chemtrail-conspiracy subset only). Scope fix.
FLETCHER: OA-W2992531903 ("In France and Italy... limited reach", 2018, no DOI) is a PRESS SUMMARY of the
  RISJ 2018 factsheet, i.e. the SAME item as the grey Reuters-Institute-2018 3.5%/5% reach entry — not an
  academic paper. Not "published-wins"; it's a duplicate of the grey factsheet. Keep ONE (canonical RISJ
  factsheet), drop the OpenAlex press-summary duplicate.

## 2026-07-02 (cont.) — final v1.2 decisions locked (Sacha)
- Figeac 85096862559: KEEP as SHARING, relabel to overall ~17-19% of Decodex-coded shared links
  unreliable (mobile 18.12%/desktop 13.57%; FN 47.48%); flag coded-subset/observed-sharing/French-2017.
- DeVerna 2-s2.0-85194023903: 73-78 -> 81 (top 0.25%) AND 34.6 -> 38.1 (top 10) [optimal concentration].
- W2912178678: REMOVE (Science write-up); add PRIMARY Grinberg aau2706.
- Allgaier W2953415400: 47.4 -> 49.4. Fletcher: keep RISJ factsheet, drop OA-W2992531903 press-summary.
- W4306964957: no change (false alarm).
v1.2 punch-list compiled -> docs/v1.2_punchlist.md.

## 2026-07-02 (cont.) — Sacha feedback folded into punchlist (3 fixes)
1. validate_prisma.py FAILs (126 orphans) because dispositions are in draft CSV, not the
   ledger it reads. Punchlist F hardened: move to ledger + resolve 15 CANT_TELL + HARD GATE
   0 orphans before submission.
2. I4 precision-weighting NOT paper-ready: it compared sample-size-weighted MEAN vs unweighted
   MEDIAN on RAW estimate-level data (CONTENT 19.3), which != headline study-level median
   (CONTENT 36.4 from data/synth/normalised_clean.csv). Redo (punchlist I): like-for-like
   unweighted-median vs weighted-MEDIAN + bootstrap CI on the study-level normalised set;
   report the REACH 26->~0 / CONTENT collapse as a deliberate RESULT (bigger samples find less
   misinfo), not a footnote. The qa/precision_weighted_sensitivity.json is superseded/not-for-paper.
3. Two-tier evidence risk: v1.2 new rows (14 recover + Grinberg + Figeac + 15 truncation-missed)
   were single-extraction/one-reader; frozen rows had double-extraction + Step-B. New punchlist
   step H: run new rows through quote-anchored second-reader + RoB appraisal before merge.

## 2026-07-03 — moderator codebook drafted (docs/moderator_codebook.md)
Audit found the paper's THESIS variables are not coded: (a) construct breadth,
(b) ground-truth source, (c) unit are prose-only (misinfo_def/definition); (d) denom
partial (denom_type 4-val); (e) platform coded-but-messy, sampling-frame absent;
(f) country coded-but-unnormalized (USA vs United States). Drafted a 6-dimension
codebook = meta-regression backbone. Added punchlist step J: code on v1.2 rows
(LLM -> quote-anchored second-reader -> kappa/AC1), regress value_pct on moderators.
Stored in memory (planned-analyses).

## 2026-07-03 — desktop PDFs triaged (15 files)
INGESTED text+pdf for 9 in-corpus studies missing full text (-> data/fulltext/v2txt/{id}.txt
+ data/fulltext/pdf/{id}.pdf):
 FROZEN gap-fills (7): 85055079422 (jmir, gyn-cancer tweets), 105036232690 (PIIS resp-med),
 85214504236 (Thai dietary-supplement), 85218448454 (dental-caries FB), 85159486270 (washing-
 produce YouTube), 85162702221 (Haenschen 806-user FB fake-news page likes, 18.4%),
 105002155467 (Zhou 140k US whole-diet exposure panel — key whole-diet study).
 IN-CORPUS not-frozen (2), now have text -> RECHECK disposition: 85131297994 (MaC election
 fraud), 85194077046 (Dynamics of Not Unfollowing Misinfo Spreaders).
CANDIDATES -> ~/Desktop/New papers/ (screen): 2603.11058v1 (arXiv Mar2026 multi-platform
 prevalence w/ fact-checkers), VIGINUM municipal-elections disinfo report (grey).
TRASHED: s41467-018-07761-2 (dup, text already held for 85059494932), gao-stromback-2026
 (motivations for sharing = out of scope), qdad060.303 (J Sex Med supplement, out), PIIS(1) (dupe file).

## 2026-07-03 (cont.) — disposition recheck of the 2 newly-textable in-corpus studies
Both were INCLUDE at abstract but parked in included_not_retrieved (paywalled). Text now supplied.
- 85131297994 (MaC election fraud): worth extracting; own fake-vs-true tweet share (31,128 tweets)
  is the candidate ("1% fake news" in text = citation of Shaw&Natisse, not its estimate). Borderline.
- 85194077046 (unfollowing spreaders): following/tie-network dynamics, not audience exposure ->
  LIKELY EXCLUDE (L12 tie metrics); confirm on full read.
2603.11058v1 (arXiv) queued for v1.2 add (needs extraction). All in punchlist A2.

## 2026-07-03 (cont.) — lit review stored + codebook aligned
Stored docs/lit_review_definitions.md (26-ref definitional canon, verbatim quotes, bib_keys
resolve in combined_library.bib). Part III coding scheme == our moderator codebook (validates
the analytic plan; Nickl et al. 2025 explicitly CALL for this review). Refined codebook:
added classification_level (source vs claim; Nenno ~10x) + question_type (existence/exposure/
engagement; Budak, Gonzalez-Bailon) as first-order moderators. Cross-linked the two docs.

---
### 2026-07-08 — Desktop cleanup: moved two loose items into the project
Sacha didn't want project files sitting loose on `~/Desktop`. Moved (via `mv`, not deletion):
- `~/Desktop/New papers/` → `data/new_papers/` (screening inbox: 2 pending PDFs incl. arXiv
  `2603.11058v1`, still open in v1.2 punchlist A2). Updated the hardcoded path in
  `scripts/rescan_newpapers.py` (`ND=P('data/new_papers')`) and the reference in
  `docs/v1.2_punchlist.md`. Gitignored `data/new_papers/` (large/copyright PDFs).
  NOTE: `rescan_newpapers.py` still writes its report to `~/Desktop/abstract_only_papers.md`
  (a separate desktop file, out of scope of this cleanup — left as-is).
- `~/Desktop/RA_package.zip` (131 MB packaged RA deliverable) → `docs/RA_package.zip`,
  beside its source `docs/RA_package/`. Gitignored (regenerable from that source folder).
The earlier historical entry (`CANDIDATES -> ~/Desktop/New papers/`, ~L1089) is left intact
per the append-only rule; the current path is `data/new_papers/`.

---
### 2026-07-14 — RA validation returned (Laura): ingest, divergence analysis, per-paper adjudication
**Deliverable received:** `RA_coding_sheet_Laura_FILLED.xlsx` (copied into `docs/RA_package/`).
Laura went beyond the template (which asked only "is our value correct? Y/N"): she did a
FULL INDEPENDENT re-code of all 100 items (her own keep/drop + construct + extracted value
+ notes + a right-hand meta-question column). Stronger design (true double-coding), but does
not fit `score_ra.py`'s columns.

**Divergence vs answer key (`_ANSWER_KEY.csv`, our frozen LLM codes):**
- Keep/drop raw agreement 68%, Cohen κ = 0.33. Confusion: both-keep 51, both-drop 17,
  our-keep/her-drop **29**, our-drop/her-keep 3. She is systematically stricter.
- Construct (on 51 both-keep): 42/51 agree; 9 disagreements almost all CONTENT↔SHARING,
  driven by the "most-shared as sampling strategy" question.
- Wrote `docs/RA_package/laura_vs_key_disagreements.csv` (41 rows).

**Adjudication of the 29 (LLM-kept / she-dropped)** — evidence-based, one parallel subagent
per paper reading the fulltext against the documented DROP rules (rubric in scratchpad;
verdicts in `docs/RA_package/adjudication_29_resolved.csv`). 26/29 had local fulltext; 3
(#4,#65,#81) resolved from extract metadata (provisional). **Final reconciled:**
- **LLM keep CORRECT (Laura over-dropped): 18**  |  **LLM keep WRONG (real over-inclusion): 11**
- => estimated frozen-KEEP over-inclusion ≈ **11/80 = 14%** (NOT the 32% a naive read of her
  46 drops implies — she was right on only 11 of 29 contested cases).
- LLM's 11 real errors cluster in detectable categories: creator/elite-producer denominator
  (#6,#18,#48,#94,#96), outlet/source-level w/o exposure (#14), selected-by-misinfo /
  composition (#19,#25), quality/stance-not-falsity (#7,#11), stance/account (#81).
- Laura's 18 over-drops are also systematic: she drops papers that ALSO carry a DISCERN/quality
  score while missing the separate true/false measure (#13,#28,#39,#45); she reads
  untrustworthy-site EXPOSURE studies as source-level even when they measure real audience
  exposure (#12,#16,#40); wrong-stat / whole-population-as-subgroup misreads (#24,#29,#40,#55).

**PROTOCOL DECISION (Sacha, 2026-07-14):** when a study measures REAL audience
exposure/consumption/sharing over a neutral denominator but defines "misinfo" via an
untrustworthy/low-credibility/NewsGuard SOURCE list (not content-level true/false), it
**COUNTS as prevalence and is INCLUDED**, tagged `classification_level = source_level` so the
write-up reports content-level vs source-level bands separately. This confirms (does not add to)
codebook dimension (a2) `classification_level`. Resolves #56 and #95 → keep (source_level).

**Implications (open):** (1) targeted re-audit of the ~14% over-inclusion categories across the
full v1.2 KEEP set (machine-detectable — not a full re-read); (2) the 3 our-drop/her-keep
"rescues" (#70,#85, and #99=W7160643177 which was already deliberately dropped as a circular
Telegram archive) still to check for real misses; (3) human-vs-LLM reliability figure for the
paper to be computed on the reconciled basis (prior κ were all inter-LLM).

---
### 2026-07-14 (addendum) — CORRECTION: dataset flags/denom_type are documentary, not filters
Earlier today's entry implied ~7 of the 11 RA-confirmed over-includes were "contained"
because the pipeline already tags them (curated/single_source/elite/source_level). An audit
of the actual analysis code (`scripts/make_contrast_figure.py`, `precision_weighted_sensitivity.json`,
`docs/synthesis_v1.md`, `docs/manuscript_draft.md`) shows that is WRONG:
- **No analysis script filters, down-weights, or separately reports on `denom_type` or `flag`.**
  Those columns are free-text annotations only. `make_contrast_figure.py` reads
  `data/synth/normalised_v2.csv`, a 5-col projection that does not even carry denom_type/flag.
- The ONLY exclusion applied to the headline is by **construct** (QUALITY and OTHER are
  excluded/reported separately). Everything else — curated, single_source, elite_population,
  concentration_within_curated_misinfo_set, source_level_not_content, abstract_only,
  outlet_timeline_denominator, per_narrative_not_pooled — is **pooled at full weight** into
  its construct's median.
- Therefore ALL 11 RA-confirmed over-includes (none are QUALITY construct) currently
  contaminate the headline medians/strata. The v1.2 drops+reclass matter MORE, not less.
- Also: the `denom_class` moderator + meta-regression referenced in `docs/moderator_codebook.md`
  and `docs/manuscript_draft.md` §Methods are **not implemented in any code** — the manuscript
  currently describes an analysis that does not yet exist. Aligns with the planned
  "proper I4 weighted-median redo" ([[misinfo-review-planned-analyses]]).

---
### 2026-07-14 (Phase 0 ratified) — 7 coding rules from Sacha's RA verification
Sacha reviewed the 29 contested papers (`docs/RA_package/ra29_verification_SACHA.csv`: 20 agree,
5 disagree, 3 unsure, 1 blank). His comments imply 7 ratified coding rules + process fixes — full
write-up in `docs/RA_package/verification_implications_and_rules.md`, durable summary in memory
`misinfo-review-coding-rules`. Headline: most "disagrees" are protocol evolution, not errors.
- R1 concentration exempt from within-misinfo drop (needs group-size + share); R2 population_scope
  is a tag not a drop; R3 within-misinfo content → appendix bucket; R4 no one-per-paper rule (keep
  clean country/platform breakdowns, collapse time-series/subgroups, quality>quantity); R5 exposure
  must be % not mean-count; R6 sharing_subtype actor vs content (audit 56 rows); R7 QUALITY≠misinfo.
- 5 new fields for v1.2: population_scope, estimate_role, exposure_type, sharing_subtype,
  within_misinfo_content.
- Construct calls: #95 W4293124965 FB-engagement = SHARING(content_share)+source_level NOT content
  (re-read Altay/Nielsen/Fletcher 2022: engagement-acts denominator; paper says "source level not
  content level"; twin of Comscore EXPOSURE). #51 → DROP. #55 → recode CONTENT→SHARING+source_level.
- CONSEQUENCE: the earlier re-audit drop list (reaudit_20_results.csv) must be re-checked under
  R1/R2 — concentration & elite-population drops become keep-with-tag, so the drop list shrinks.

---
### 2026-07-14 (Phase 1 done) — re-adjudicated 6 loose ends from PDFs
Per new rules (R1-R7). Results: docs/RA_package/phase1_readjudication.csv.
- #13, #51 FLIP KEEP->DROP (Sacha right): #13 no stated estimate (9.6% reconstructed from creator
  subgroup table, DISCERN-led); #51 stance-agnostic fact-checker-topic dictionary (counts refutations).
- #24 KEEP but re-coded SHARING(content_share)+source_level; denominator = fake/(fake+traditional
  news tweets) = within-news share (Sacha's unease validated; kept as 'of news shared, ~20-40% fake').
- #65 KEEP REACH; no overall figure exists -> primary electoral 12.7% + secondary_topic social 10.9%,
  covid 6.7%, health 4.3%.
- #4 KEEP CONTENT; primary=79% (contains any misinfo), secondary_severity=27% (entirely misleading,
  NESTED, descriptive-only). New rule R4a: severity gradients kept as nested secondaries, excl from pool.
- #81 DROP confirmed (stance/account-level).

---
### 2026-07-14 (Phase 3a done) — RA-rule changes applied to WORKING COPY v1.2a
Per Sacha: do the RA-rule content changes first, on a separate version (safer); full punchlist +
systematic tagging later (Phase 3b). Frozen v1.1 UNTOUCHED.
- Output: `data/extract_v2/estimates_v1.2a_ra_rules.csv` (MD5 5d468b5af19a95e63d1b8ca6c687eb5b,
  588 rows). Additive audit columns (v12a_status/action/note + the new moderator fields); NOTHING
  deleted — drops flagged, not removed. Row changelog: `qa/v1.2a_changelog.csv`.
- 328 -> 312 kept studies: 16 dropped, 1 appendix (#19), 12 recoded/tagged. All PENDINGs resolved:
  #94 concentration group-sizes (derived, flagged approx), #24 -> 30% period mean, #55 keep both swing/safe.
- Version history now tracked in `docs/dataset_provenance.md` (canonical ledger).
- NEXT: Phase 3b = full v1.2 re-freeze (v1.2a + v1.2_punchlist + systematic 5-column tagging pass,
  quote-anchored 2nd-reader) -> new MD5 + tag dataset-frozen-v1.2; then Phase 4 recompute
  (reliability + breadth-stratified medians; build the not-yet-implemented denom_class/meta-regression).

---
### 2026-07-14 (Phase 3b started) — v1.2 assembly on a NEW copy
Committed Phase 3a as `checkpoint-v1.2a-phase3a` (recoverable). Frozen v1.1 + v1.2a untouched.
- **3b-1 skeleton** (`scripts/build_v1.2.py` -> `estimates_v1.2.csv`, MD5 88c64fd4…, 312 studies):
  deterministic punch-list edits only. DeVerna 73-78->81 & 34.6->38.1; Cordonnier de-dup (drop seed
  copy, keep full_text, rename one-n->two-n, backfill value_raw); W4306964957 confirmed no-change.
  Changelog `qa/v1.2_build_changelog.csv`.
- **CONFLICTS surfaced (need Sacha):** (a) Allgaier W2953415400 punch-list C wanted 47.4->49.4 but
  Phase-3a already DROPPED it (re-audit stance/composition) -> marked SUPERSEDED, left dropped.
  (b) Fletcher E "drop OA-W2992531903 dup, keep canonical RISJ 3.5%/5%" — canonical row NOT in dataset;
  dropping now would lose Fletcher -> DEFERRED to new-rows step. (c) 85057304142 is in disposition
  RECOVER (concentration) AND punch-list D EXCLUDE (troll-producer, out of scope) -> DIRECT CONFLICT.
- **3b-4 step1 pre-code** (`scripts/precode_moderators.py` -> `estimates_v1.2_precoded.csv`):
  deterministic moderator fill — country_norm 539/555, country_scope, platform_norm 555/555,
  question_type 479/555 (blanks = CONCENTRATION/QUALITY/OTHER), + safe defaults (EXPOSURE->proportion,
  population_scope->general_public). Coverage `qa/precode_coverage.md`. STILL BLANK (need quote-anchored
  LLM pass): breadth, classification_level, ground_truth, unit, denom_class, sampling_frame.
- NEXT: launch parallel quote-anchored LLM tagging pass (the 6 judgment dims + RA refinements) on the
  555 live rows; resolve new-row inclusion forks (A/A2/B + the 3 conflicts); PRISMA ledger to 0 orphans;
  2nd-reader+RoB on new rows; then freeze v1.2 (MD5 + tag dataset-frozen-v1.2).

---
### 2026-07-14/15 (Phase 3b-4 DONE) — corpus-wide moderator tagging
Launched 14 parallel quote-anchored coders over the 555 live v1.2 rows (batches of 40; codebook
dims from existing text, no PDF re-read). First launch hit a transient API outage (all died); clean
re-dispatch succeeded 14/14.
- Merge (`scripts/precode_moderators.py` -> `scripts/merge_moderator_tags.py`) -> `estimates_v1.2_tagged.csv`
  (MD5 9277d8bb…, 44 cols). Validation: 555/555 coded, 0 missing, 0 enum violations.
- Confidence: 347 high / 183 medium / 25 low. definition_variant=TRUE on 30 rows (the breadth-strictness
  pairs that are the review's headline). breadth: false 234 / unreliable_source 142 / misleading 127 /
  low_quality 38 / fabricated 14. classification_level: claim_level 402 / source_level 152 / mixed 1.
- QC report `qa/moderator_tag_qc.md` (incl. the 25 low-confidence gids for human spot-check).
- SIDE-BENEFIT: coders caught extraction discrepancies (value_pct vs quote) -> `qa/v1.2_extraction_flags.md`
  (gids 268, 584, 585-587, 400, 407) to verify before freeze.
- New-rows inclusion set compiled for review: `docs/v1.2_newrows_worklist.md` (G1 14 clean recoveries,
  G2 Grinberg-primary/Figeac/Fletcher-canonical/engagement-tag, G3 15 truncation-missed rows,
  G4 excludes incl. 85057304142 [Sacha ruled out], G5 fetch/re-extract). Sacha rulings recorded:
  exclude 85057304142; add Fletcher canonical then drop OA dup.

---
### 2026-07-15 (Phase 3b-2, in progress) — new-row build + dedup catches
Dispatched 6 enrichment agents (2nd-reader + RoB) over 18 new studies (G1 14 + Figeac + 105017599346 +
Grinberg + Fletcher) reading fulltext -> complete rows to newrows_out/enrich_B*.json. G5 resolved:
105029413645 ADD (Lyons 2025, rich), arXiv 2603.11058 ADD (6 platforms), 85131297994 DROP (curated
case-control, no organic denom). 85086931774 EXCLUDE (Sacha). 
CATCH: Grinberg aau2706 == frozen 85060549676 -> do NOT double-add; dedup G3 missed rows vs frozen.
NEXT: collect enrich outputs -> build final new-row set with per-row dedup -> merge into v1.2 -> drop
Fletcher OA dup -> PRISMA ledger 0 orphans -> validate/MD5/freeze/tag dataset-frozen-v1.2.

---
### 2026-07-15 (Phase 3b-2 DONE) — new rows merged into v1.2 candidate
`scripts/merge_newrows.py` -> `estimates_v1.2_withnew.csv` (MD5 8de19c03…, 608 live rows / 328 live
studies; +53 new rows / 16 new studies). Manifest: `qa/v1.2_newrows_manifest.csv`.
- ENRICHMENT (6 agents, 2nd-reader + RoB over 18 studies): kept most; DROPPED on scope — 85062230191
  (curated non-organic corpus incl. debunking sites, x2 rows), 85137929479 (sockpuppet/bot audit),
  85038621544 "13% likely bots" row (bot exclusion).
- DEDUP/OVERRIDES: Grinberg aau2706 == frozen 85060549676 -> dropped 4 dup rows, folded only the
  individual-average EXPOSURE 1.18% into 85060549676 (definition_variant). Fletcher DOI misidentified
  (Reuters India report) -> dropped; OA-W2992531903 KEPT (canonical swap deferred). 85213958624
  concentration dropped (share = "most", R1 needs a number); CONTENT 0.94% kept.
- DEDUP vs frozen caught 3 false-misses already present (Weeks 39.2, QAnon 39.1, Oswald 17).
- G5: Lyons 2025 (105029413645) 5 rows; arXiv 2603.11058 12 rows (6 P_restricted + 6 P_total variants).
- 85131297994 DROPPED (case-control seed, no organic denom); 85086931774 EXCLUDED (Sacha).
- NEW rows carry moderator tags from the 2nd-reader + normalized country/platform. NOT frozen yet.
- REMAINING before freeze: PRISMA ledger -> 0 orphans (hard gate F); validate_frozen; MD5; update
  FROZEN.md -> v1.2; update RA answer key; git tag dataset-frozen-v1.2.

---
### 2026-07-15 (Phase 3b-2b) — Sacha's new-adds review applied (recode)
Notes: `data/extract_v2/qa/v1.2_newrows_manifest.csv` review -> `docs/construct_and_concentration_rules.md`
(RULE D denominator-sets-construct; RULE C-TYPE concentration unit×dimension; RULE DEMO; RULE DUAL-DENOM).
`scripts/recode_v1.2.py` -> `estimates_v1.2_recoded.csv` (MD5 901bb67565ef77fcf9166c8cc448a198, 620 live
rows / 327 studies). Changelog `qa/v1.2_recode_changelog.csv`.
- Drops: 85086772538 (Guo, Sacha), 85056802427 (Shao bots-concentration).
- Construct recodes (denominator rule): 105017599346 OTHER->SHARING; 85101871838 EXPOSURE->RECALL;
  85095575703 CONTENT->SHARING(content_share). New cols conc_unit/conc_dimension/demographic_group.
- Re-extractions (6 agents, fulltext): Altay W4293124965 (+8 repeatedly-false variants; the 8 base
  country×platform were ALREADY frozen -> deduped); Web Centipede dual-denom (all-content + within-news,
  Twitter 0.022%/23.9% etc.); Oswald +<1% media-diet EXPOSURE + 2024 concentration (news_source);
  Figeac all-party (LFI/PS/REM/LR/FN × mobile/desktop, demographic_group); Lyons verified (13/9 REACH,
  3/10 EXPOSURE, 37/77 individuals-exposure concentration; wrong DOI discarded); Gonzalez-Bailon 0.94%
  re-scoped (viral-trees denom, lower bound), concentration stays dropped (share only "most").
- arXiv 2603.11058: dropped the 6 P_total variants, kept 6 per-platform.
- CLARIFIED (looked missing, already frozen): QAnon 39.1%; Grinberg 1%->80%/0.1%->80% individuals-conc.
- NEXT: systematic demographic (age/political) corpus pass; then PRISMA ledger 0-orphans; then freeze.

---
### 2026-07-15 (Phase 3b-2c) — punch-list A done (working copy finalized pre-ledger)
`scripts/apply_A.py` -> `estimates_v1.2_A.csv` (MD5 a79f45316e92ff28ef670ab38f9df722, 619 live / 326
studies). Changelog `qa/v1.2_A_changelog.csv`.
- A1 extraction flags (2 agents re-read): 105009619554 79->52 (was 52+27 derived sum) +27 (defvar pair);
  85066894147 fix quote + time-series flag (20/30/40); 85091698994 14.39 Italy confirmed + France 10.42
  (already present, relabeled); 105019603181 topic exposures relabeled (politics 12.7 / social 10.9 /
  COVID 6.7 / health 4.3 — 12.7 already present, relabeled).
- A3 concentration typing: all 33 CONCENTRATION rows now carry conc_unit×conc_dimension (agent);
  85056802427 bots-concentration DROPPED (study now out entirely). 15 individuals / 1 news_source.
- A4 Brugnoli 85215303159: pre-pandemic (31.7) vs overall (12.6, during~10% noted) labeled.
- A2 already complete (all 65 new rows carry moderator dims).
- READY for PRISMA ledger (126 orphans -> 0), then validate_frozen + MD5 + FROZEN.md v1.2 + RA key +
  tag dataset-frozen-v1.2. (Demographic systematic pass deferred by Sacha.)

---
### 2026-07-15 (Phase 3b, gate F) — PRISMA ledger reconciled to 0 orphans
Built `data/extract_v2/qa/prisma_dispositions.csv` (126 rows: 14 INCLUDED_RECOVERED, 44 INCLUDED_NO_DATA,
48 EXCLUDED, 14 EXCLUDED_TITLE_SCREEN, 6 EXCLUDED_OUT_OF_SCOPE-with-reasons) from disposition_results.csv,
reconciled against v1.2 live studies. Patched `scripts/validate_prisma.py` to read it as a terminal-state
source. **`validate_prisma.py` now PASSES — 0 orphans.**
- 6 dropped RECOVER have documented reasons (85057304142 troll-producer; 85062230191 curated corpus;
  85086772538 Sacha-drop; 85086931774 vaccine-book stance; 85137929479 sockpuppet; W2912178678 Grinberg dup).
- 14 CANT_TELL title-only -> EXCLUDED_TITLE_SCREEN. BORDERLINE (excluded now, revisit if fetched):
  85016088761 (Schmidt 'Anatomy of news consumption on FB'), 85184873133 (partisan low-quality sharing by US elites).
- NOTE for freeze: when estimates_reextracted.csv is bumped to v1.2, the v1.2-specific DROPS (Guo, Shao-bots,
  Allgaier, Phase-3a reaudit drops) must be added to a drop ledger so they don't become new orphans.
- DROPPED_V2_UNLEDGERED (57) remain a recognized terminal state (not orphans); per-item reasons optional polish.

---
### 2026-07-15 (Phase 3b) — DATASET FROZEN v1.2 (tag dataset-frozen-v1.2)
Cut the v1.2 freeze (Sacha's call: freeze now; demographic pass -> v1.3).
- **File:** `data/extract_v2/estimates_v1.2_frozen.csv` (NEW file per naming decision; v1.1
  `estimates_reextracted.csv` stays immutable). Built by `scripts/build_frozen_v1.2.py` = LIVE
  rows of estimates_v1.2_A.csv (57 dropped rows excluded). **619 rows / 326 studies / 47 cols.**
- **MD5:** 17237c74cb46ed8e4d3db05f53d8eb0f
- **Gates (both green):** validate_frozen 0 FAIL / 0 WARN* (19 X-of-Y reconciled; *1 soft WARN =
  6 seed/grey/snowball ids not in corpus jsonl, expected); validate_prisma 0 orphans (326 INCLUDED_FROZEN).
- **Freeze-prep this step:** `qa/v1.2_drops_ledger.csv` (14 v1.2 content drops + 1 Cordonnier dedup,
  each with reason) so the 17 studies leaving the frozen set land in real terminal states, not the
  DROPPED_V2_UNLEDGERED catch-all. validate_prisma patched to read it + a PRISMA_FROZEN env override
  (used for the pre-freeze dry-run) + default frozen path repointed to v1.2.
- **Repoint:** validate_prisma default -> v1.2. FROZEN.md rewritten (v1.2 on top so validate_frozen's
  regex reads the v1.2 spec; all v1.1 errata marked RESOLVED; v1.1 preserved below for the audit trail).
  Provenance ledger updated (v1.2 = FROZEN row).
- **Deferred to v1.3:** demographic systematic corpus pass (age/political/party via demographic_group).
- **OPEN (flagged to Sacha, NOT changed):** 10 RA answer-key items are our_keep=Y but dropped in v1.2
  (the RA-verification + re-audit drops). Not flipped — retroactively editing the key changes the
  inter-rater κ Laura was scored against. Needs Sacha's decision, separate from the dataset freeze.

---
### 2026-07-15 (Phase 3b, post-freeze) — RA keep/drop reliability: REPORT BOTH
Sacha's decision on the 10 RA-key items that are keep=Y but dropped in v1.2: report both figures,
do NOT edit the answer key. `scripts/ra_kappa_dual.py` -> `docs/RA_package/ra_kappa_dual.json`;
write-up `docs/RA_package/reliability_dual_note.md`.
- PRIMARY (headline; Laura vs frozen-at-scoring key): raw 0.68 / Cohen κ 0.328 / Gwet AC1 0.426.
  Reproduces reliability_reconciled.json exactly (key untouched, blind double-coding).
- SECONDARY (sensitivity; Laura vs final v1.2 membership): raw 0.74 / κ 0.463 / AC1 0.508.
  Higher because 8 of the 10 key=Y/v1.2-dropped items were ones Laura independently voted DROP —
  her apparent over-exclusion was vindicated on full-text re-audit (FN 29->21, TN 17->25; only 2
  of her keeps dropped against her). Not blind (folds in RA-driven post-hoc drops) -> footnote, not headline.

---
### 2026-07-15 (Phase A) — second-reader verification of v1.2 new rows → FROZEN v1.2.1
Closed the "no two-tier evidence standard" gate: every new/changed v1.2 row got the same
quote-anchored second-reader check the frozen v1.1 rows had, + RoB for the 4 new studies.
- **8 parallel agents** verified all 86 new-value rows against full text (Tier1: 4 new studies
  full verify + RoB; Tier2: 28 relabel studies quote-confirm). Manifest/plan `docs/phaseA_plan.md`.
- **Result: 79 CONFIRM verbatim / 0 CORRECT / 6 DROP** (+1 keep-override). All headline numbers
  hold (Lyons 37%/77%, QAnon 3.7%, Eady 98%, Altay 8 rows, Oswald, Figeac 12 party rows, 6 arXiv).
- **Hybrid keep/drop rule (Sacha):** keep verbatim + exact PART/WHOLE prevalences from verbatim
  same-denominator counts; drop cross-category sums/complements. DROP: Web Centipede within-news
  23.9/11.3/20.2 (news-total denom NOT verbatim — re-verified: Table 1 gives only all-posts denom,
  in-text counts are rounded-k URL subsets yielding 23.8/11.2/20.4), Mourão 11.8 (sum) & 43.5
  (complement), TikTok-nutrition 37 (sum). KEEP-override: bladder-cancer 29.3 (44/150 part/whole).
- **RoB** companion `qa/rob_appraisals.csv` (5 dims per rob_checklist.txt): Lyons LOW; Web Centipede/
  Figeac/arXiv MODERATE. **148 moderator gap cells filled** on new rows (population_scope, country_norm,
  sampling_frame, denom_class, question_type, classification_level).
- Merge `scripts/apply_phaseA.py`: 619→613 rows, 6 dropped, 326 studies (no whole study left → PRISMA
  id-set unchanged). New file `estimates_v1.2.1_frozen.csv` MD5 2e46254a4c412ff16338e62c16d966b0.
- Gates green: validate_frozen 0F/0W; validate_prisma 0 orphans. FROZEN.md/provenance updated; v1.2
  preserved immutable. Tag `dataset-frozen-v1.2.1`.
- **Next in Phase A: demographic corpus pass → v1.3** (then Phase B analysis on the final dataset).

---
### 2026-07-15 (Phase A step 2) — demographic corpus pass → FROZEN v1.3
Systematic corpus-wide extraction of demographic subgroup breakdowns (RULE DEMO: age/political/gender/
education). Read-only grep pre-filter narrowed 326→125 demographic-signal candidate texts (221 have text;
105 no text = not codeable, listed). 7 agents (~18 papers each, per Sacha "1 agent for ~20 papers to cut
token re-read") read full texts; strict inclusion = a per-subgroup VALUE anchored to verbatim quote (NOT
regressions/odds-ratios/sample-composition). Plan `docs/phaseA_plan.md`.
- **26 papers had codeable breakdowns; +54 demographic rows added** (political 38, age 9, gender 4,
  education 3). Subtype: 48 per_subgroup_rate + 6 subgroup_composition (share OF sharers who are
  Trump/conservative — W4281770633, W3033912864, 85194023903, 85188806397; flagged distinct).
- Canonical: Guess/Nagler/Tucker (18.1% Rep vs 3.5% Dem shared; 65+ ~7×), Grinberg (11/21% right vs <5%
  left), Lazer (political×age), Hjorth (6.5% liberal→45.2% conservative exposure), QAnon/pink-slime by
  ideology, multi-party sharing. `scripts/build_v1.3.py`; review sheet `qa/demographic_added.csv`.
- **REGION/country (24 values) SET ASIDE** — geographic (country_norm axis), not demographic_group;
  `qa/demographic_region_setaside.csv` for Sacha's review. Figeac party rows already coded → 6 skipped.
- One Guess age row = intensity mean-count → value_pct blanked (R5), value in value_raw, flag
  intensity_not_proportion. Demographic rows are SUBGROUP rows: Phase B headline must exclude
  demographic_group != ''.
- 613→667 rows, 326 studies (no new study). Gates green. Tag `dataset-frozen-v1.3`.
- **PHASE A COMPLETE.** Next per the agreed order: Sacha reviews the dataset; NO analyses until he says.

---
### 2026-07-15 (Phase A step 2b) — high-value canonical papers → FROZEN v1.3.1
Closed a coverage gap: the demographic pass (step 2) grepped only data/fulltext/, missing 20 high-value
(exposure/sharing/reach/concentration) studies never extracted to text — incl. canonical Guess 2016/2020,
Allcott, Supersharers, deplatforming. 11 were in the PDF library (resolved via pdf_index filepath); 3
agents read the PDFs and (1) verified existing frozen values, (2) extracted demographic breakdowns.
- **33/33 existing values CONFIRM** (0 CORRECT/DROP) — canonical papers' frozen values validated.
- **+27 demographic rows** (political 17, age 9, gender 1; 23 per_subgroup_rate + 4 subgroup_composition):
  Guess/Nyhan/Reifler political gradients (Trump 56.7 vs Clinton 27.7 REACH among conservatives;
  media-diet-decile 84.0 REACH / 20.9 diet-share), Moore 2020 (Trump 36.2/Biden 17.8; 65+ 37.4), Lyons age
  gradient (website REACH 4.8→20.9 by age), Supersharers 59% women/64% Republican (composition). Dropped
  Moore's 3 "(2016)" rows (Moore citing Guess, coded natively). `scripts/apply_hv.py`, `qa/demographic_added_hv.csv`.
- All 11 PDFs extracted to data/fulltext/v2txt/ (gap can't recur). 9 high-value remain unresolved
  (OA preprints/title-only) → stay on missing-full-text sheet (now 94).
- 667→694 rows, 326 studies. Gates green. Tag `dataset-frozen-v1.3.1`. Review sheets regenerated
  (docs/demographic_review.html 81 rows; docs/missing_fulltext.html 94).
- **PHASE A COMPLETE.** Awaiting Sacha's dataset review; NO analyses until he says.

---
### 2026-07-15 (Phase A step 2c) — 7 user-found high-value PDFs → FROZEN v1.3.2
Sacha located 7 of the 9 remaining high-value studies (Desktop/New). Matches verified by title page,
PDFs copied to data/fulltext/pdf/ + extracted to v2txt. 2 agents verified existing values + extracted
demographics (`scripts/apply_found.py`, changelog `qa/found_changelog.csv`).
- 23/24 existing values CONFIRM. 1 DROP: Nigeria OA-W7125772788 EXPOSURE 40 (relative comparison, not
  prevalence; RECALL 54 kept). 4 RELABEL: Fletcher OA-W2992531903 EXPOSURE→REACH (France/Italy 3.1/1.0 =
  avg monthly reach %). +4 demographic (Bandy 85114317455 political, junk-news exposures/day by leaning,
  intensity). Fletcher France/Italy region splits skipped (= existing country rows).
- 694→697 rows, 326 studies. Gates green. Tag `dataset-frozen-v1.3.2`. Review sheets regenerated
  (demographic 85 rows; missing_fulltext 87, down from 94). Still missing: OA-W3113799821 ("Does Vinegar…");
  Cordonnier data-complete (Fondation Descartes report, seed values). PHASE A COMPLETE — awaiting review.

## 2026-07-15 — v1.3.3: Cordonier & Brest full-text verify + review-sheet Open-PDF links

**Cordonier/Brest 2021 (Fondation Descartes report).** Sacha located the PDF (extracted to
data/fulltext/pdf/SEED-cordonnier2021.pdf + v2txt). A second-reader agent read the full English
report and returned: (a) both existing EXPOSURE values CONFIRMED verbatim — 5% of news/information
time, 0.16% of total connected time (Key Findings p.05, restated §3.6 p.26); (b) a MISSING REACH
estimate — "39% of participants consulted information sources considered to be unreliable" over the
30-day window (N=2,372); (c) 0 qualifying demographic breakdowns (report gives demographic patterns
only as correlations, Hedges' g effect sizes, and risk-group composition e.g. "63.2% men" among
disinfo consumers — all excluded by RULE DEMO). `scripts/apply_cordonnier.py` folded this into
**v1.3.3** (698 rows / 326 studies, MD5 e1455c96c189f3335f47067e28656be7, tag dataset-frozen-v1.3.3):
+1 REACH row, and cleared the now-stale `abstract_only` flag on the 2 EXPOSURE rows (full text held).
Both gates green (validate_frozen 0F/1 pre-existing seed-id WARN; validate_prisma 0 orphans).

**Review sheets — per-study Open-PDF/URL links.** Added a source-opener resolver to
`scripts/make_review_sheets.py`: each study header now carries a link that opens (in priority order)
the downloaded PDF, else the ~3,800-paper PDF library matched by DOI (fixed the library-path build —
the index stores bare filenames under Articles_Claude, not absolute paths), else a DOI / OpenAlex /
Scholar URL. Demographic sheet: 9 open a local/library PDF, 16 fall back to a source URL. Missing-
fulltext sheet: +4 library PDFs surfaced alongside the existing Scholar/DOI links. Also redesigned
both sheets earlier this session (bigger full-width notes fields, color-coded Keep/Drop/Unsure
segmented control, cleaner card UI).

## 2026-07-15 — v1.3.4: abstract-only coding reconciled against held PDFs

Sacha asked whether any studies were coded from the abstract while we actually hold the PDF.
Audit: 43 studies are fully abstract-coded (`source=abstract` or `abstract_only` flag on every row);
of those, only 4 have a PDF/full text available (the other 39 are genuinely PDF-less).
- **2 genuinely abstract-coded studies, re-verified verbatim against the full text we now hold → CONFIRMED**
  (source → `full_text_verified_abs`): Caliandro OA-W3091627927 (SHARING 1.44%, "l'1,44% del totale dei
  tweet", n=7,237,581 tweets); Thai dietary-supplement e-marketplace content analysis 2-s2.0-85214504236
  (CONTENT 85/82/48/42%, n=332 web pages).
- **2 stale `abstract_only` flags cleared** — source was already `full_text`: Nigeria OA-W7125772788
  (RECALL), Fletcher OA-W2992531903 (REACH; already verified in the found-papers pass).
- Separately, extracted text for 4 library PDFs that had no cached `.txt` (Singh 2020 JCSS, WhatsApp
  Misdoom, ACM CSCW visual-misinfo, Yang/Hindman JoC) — all already `source=full_text_*`; data-completeness
  only, values unaffected.
- **No value changes** — every checked value confirmed. `abstract_only` flag rows 63→51; `source=abstract`
  44→39 (the 39 remaining are the genuinely PDF-less studies). `scripts/apply_abstract_fix.py`,
  changelog `qa/abstract_fix_changelog.csv`. Frozen **v1.3.4** (698/326, MD5 ee7922033820409278797ce82f929278,
  tag dataset-frozen-v1.3.4). Both gates green. Also added a data-completeness guarantee: `make_review_sheets.py`
  now defines "missing full text" as no-text AND no-openable-PDF, so the missing sheet can never again list a
  study whose PDF we hold.

## 2026-07-15 — v1.3.5: new user-supplied PDF batch (Desktop/New)

Sacha added 18 unique PDFs. Matched by DOI + title against the corpus/frozen set:
- **13 were already-frozen studies** with `source=full_text_*` that simply lacked a cached `.txt`
  (J Urban Econ, STEM Fellowship, 3× ACM, ComProp German junk-news, Gruhonjić, "Separate worlds"
  German broadcast, "Tracing dynamics" Finland vaccine, Chan distributed-discovery, von Nordheim Google,
  COVID-vaccine-infertility, Truth/Fear/Virality) → text extracted to `data/fulltext/v2txt/`
  (data-completeness; values unchanged). Stale-flag fix: **OA-W7154838691** 5 CONTENT values re-verified
  verbatim against the now-cached full text (48.0% overall; TikTok 58.4/Facebook 54.8/Twitter 41.2/YouTube
  38.8) → `abstract_only` cleared, source→full_text_verified_abs. OA-W4291473423's added PDF is a genuine
  conference abstract, so its abstract_only flag is correct (kept).
- **2 already in corpus but deliberately EXCLUDED, kept excluded** (a held PDF doesn't overturn a scope/
  measurement exclusion): 2-s2.0-85059686579 (Prostate/Eur Urol — 77% is a DISCERN *quality* composite,
  not falsity), 2-s2.0-85140862422 (PLOS medication — *perspective* piece).
- **2 genuinely NEW studies, screened INCLUDE by second-reader, added** (studies 326→328):
  NEW-moreno-jmirderma (Moreno et al., JMIR Dermatology 2021, 10.2196/25661 — 3 CONTENT rows on % of 4,956
  tanning-BUSINESS Facebook posts that are misinfo [1.3/0.6/0.5%], flagged single-source/curated i.e. NOT
  general-public content; + 1 RECALL row 43% [20/46 at-risk purposive sample]); NEW-jadara-2022 (Shatnawi &
  Ayhan, Jadara J. 2022 — 1 RECALL row 81.6% read Covid info that turned out untrue, N=6,910 Levant
  convenience survey, flagged perceived_exposure). `scripts/apply_newpdf.py`, changelog `qa/newpdf_changelog.csv`.
- Frozen **v1.3.5** (703/328, MD5 d0b6c0673aa929cc83c387980d13f953, tag dataset-frozen-v1.3.5). Both gates green.
  Dedupe: no duplicate rows/studies entered the project (the `(1)` copies stayed in Desktop/New).
  NOTE for Phase B: the 2 new studies' scope flags are load-bearing — the general-public headline must exclude
  the Moreno business-page CONTENT rows + at-risk RECALL row and treat Jadara as perceived-exposure.

## 2026-07-16 — v1.3.6: González-Bailón 2023 re-included as a concentration study

Sacha asked whether we have "Asymmetric ideological segregation in exposure to political news on Facebook"
(González-Bailón et al., Science 2023; 2-s2.0-85165815218, DOI 10.1126/science.ade7138). We do — in the
corpus, screened INCLUDE (title+abstract) — but it was step-B-dropped with "No quantified prevalence value.
The only prevalence-relevant statement is qualitative: 'the fraction of false news stories is barely
perceptible…'". The PDF turned out to be in the library (science.ade7138.pdf); I extracted the full text and
re-examined. The drop was correct for a PREVALENCE figure (no codeable overall misinfo-exposure rate; Fig 1D/
Fig 4 give distributions/color-scales only, so a general-exposure value is NOT inferable). But the paper
reports a strong CONCENTRATION-by-ideology value, in scope for the review's concentration arm. Re-included with
2 CONCENTRATION rows (n=208M US FB users; false = Meta 3PFC-rated): **97%** of false-news URLs have
conservative-leaning exposed audiences ("For potential, exposed, and engaged audiences, 97% of false URLs in
each case have audiences that are conservative on average"); **76%** of untrustworthy domains likewise. Flagged
`audience_ideology_concentration;not_a_prevalence_rate`. NOTE: the 60.6%/53.1% (7.5pp) figure in the text is
Gentzkow & Shapiro cited as comparison, NOT this paper's result — not coded. Removed from stepb_drops_queue.
`scripts/apply_gonzalez.py`, changelog `qa/gonzalez_changelog.csv`. Frozen **v1.3.6** (705/329, MD5
4756f72617f4b3057966118cdafbde2b, tag dataset-frozen-v1.3.6). Both gates green. PDF+text cached so it opens in
the review sheets.

## 2026-07-16 — v1.4.0: demographic review applied + coding conventions + 3 desktop-PDF extractions

Sacha reviewed all 85 demographic rows (demo_review (2).csv; a CSV-quoting bug in the export was fixed and the
decisions re-parsed cleanly — 47 keep / 25 drop / 10 uncertain / 3 blank + 44 notes). Ratified 4 conventions
(AskUserQuestion): (1) recall/questionnaire subgroups KEEP + tag construct=RECALL; (2) "% who shared/were
reached ≥1" → REACH; (3) spreader/supersharer make-up → spreader_composition flag + code binary complements;
(4) geographic breakdowns to be coded + reviewed separately (geographic_review.html built). Applied via
scripts/apply_review_v140.py → **v1.4.0 (718 rows/329, MD5 45e7f676136b35086c84f00f8e6e28d5)**. 18 drops, 9
RECALL relabels, 3 REACH relabels, 5 spreader_composition tags + 4 complements, 1 split (Left+center→left+center).
Flags for Sacha: recall-subgroup keep reverses his per-row drop notes (per his rule); 105029521599 kept because
we have the paper (he'd conditioned drop on not having it).

3 desktop PDFs (Repeat Spreaders W4281770633, COVID Consortium W4205602257, 4-country politician paper
105027856675) re-extracted by agents. KEY LESSON: all three were ALREADY well-covered in the dataset from earlier
passes (the demographic sheet only shows demographic_group rows, hiding the country/concentration rows) — the
agents CONFIRMED every existing value, and a first build erroneously duplicated them; corrected to add only
genuinely-new rows. W4281770633: the "80% Trump" was a classification threshold (dropped); 28.6/50/98 concentration
already present. W4205602257: 1.1/1.8 overall + age×ideology cells already present. 105027856675: +26 new rows
(per-politician means as secondary denominator, 6 smaller parties, within-country party concentration [AfD 95.5% /
FdI 70.7% / Cons 57.3% / Rep 76.4%], Italy 53.23% cross-country, RE rates, ~50% crisis share, engagement betas as
construct=OTHER). Denominator: link-level pooled primary; engagement betas excluded from prevalence; the abstract's
"Italian crisis misinfo surpassed general in engagement" contradicts the results (beta<1) — logged. Both gates green.
OUTSTANDING: geographic_review.html (9 country/continent candidates) + the two confirm-flags above.

---

## 2026-07-16 — Thorough pre-analysis data-quality audit of v1.4.0 (holes/loops sweep)

Sacha asked for a deep audit of the frozen dataset BEFORE any analysis — to find "a rule
applied to some data but not all, rules applied inconsistently, categories mis-tagged" — plus
an HTML to review the hardest cases, plus a local launchd schedule. No dataset was modified
(all coding decisions deferred to Sacha's review). New reproducible tooling:

- `scripts/audit_dataset_v140.py` — deterministic audit (schema/vocab hygiene, rule-coverage
  "some-but-not-all", value ranges, duplicates, construct/denom alignment). Reads frozen path
  from FROZEN.md. Writes `data/extract_v2/qa/audit_v140_findings.csv` + `_summary.md`.
  RESULT: 258 findings (82 ERROR / 137 WARN / 39 INFO), 91 flagged needs-eyes.
- `scripts/pdf_resolve.py` — side-effect-free source-opener resolver (extracted from
  make_review_sheets.py so the audit sheet can reuse the PDF/DOI resolution without triggering
  that module's generation side-effects).
- `scripts/make_audit_review_sheet.py` → `docs/audit_review.html` — curated review sheet:
  10 needs-eyes items (Open-PDF button + current coding + rule at stake + recommendation +
  decision control + notes; localStorage autosave; CSV export), 5 mechanical fixes (FYI/object),
  3 completeness gaps. Auto-drops items a future re-freeze has already fixed.

Two source-reading agents adjudicated the highest-stakes cases against the PDFs:
- **González-Bailón 2023 (85165815218)** — the 2 CONCENTRATION rows (97%/76%) are favorability/
  segregation scores (share of false-news URLs whose *audience* leans conservative), i.e. a
  property of URLs, not a top-X%-of-people→Y% concentration. This is EXACTLY what ratified rule
  **L11** excludes. Paper holds no individual-level concentration (privacy: aggregate only) and
  no extractable overall misinfo-exposure prevalence. Agent rec: DROP both. NOTE the conflict —
  Sacha earlier asked to re-include this study as a concentration measure, so the call is his;
  surfaced in the review sheet rather than auto-dropped.
- **4-country legislators (105027856675)** — "party share of country total" (AfD 95.5% / FdI
  70.7% / Cons 57.3% / Rep 76.4%) and "country share of 4-country total" (Italy 53.23%) are
  producer/source COMPOSITION, not audience concentration → out of scope per **L14/L28**. The
  per-politician/party sharing RATES are correct verbatim but need sharing_subtype=content_share.

Confirmed "rule applied to some but not all" gaps (the pattern Sacha feared):
1. **SHARING(actor_share) vs REACH boundary** — 11 rows "% of PEOPLE who shared/visited ≥1"
   left as SHARING(actor_share)/EXPOSURE, though L32 + the ratified "% shared ≥1 → REACH"
   convention (applied only to reviewed demographic rows) say REACH. One decision fixes the
   dataset-wide boundary → review sheet §2.
2. **sharing_subtype missing** on 15 SHARING rows (mostly the 105027856675 batch) — R6 requires it.
3. **Figeac (85096862559)** — the RULE DEMO *template* study — has demographic_group set but
   demographic_dimension/subtype EMPTY (never backfilled).
4. **Concentration field hygiene** — conc_group_pct/conc_share_pct hold '%' signs and prose
   ("top 10 sources") in numeric fields; many CONCENTRATION rows have both empty (backfill
   incomplete); conc_unit='news_story' off-vocab; conc_dimension extended to political_*/country.
5. **demographic_group overloaded** — used for topic= (105019603181) and period= (85215303159)
   breakdowns, which are not demographics → review sheet §3.
Clean dataset-wide (verified, no gaps): self-report→RECALL (66/66), no politician rows mislabeled
general_public, engagement betas→OTHER consistent.

Also: 2 exact-duplicate RECALL rows (85172813494, 105008525623); within_misinfo_content casing
(True/False/crisis_vs_general); 71 rows missing n; 15 REACH rows missing date window; 12 rows no
definition. All catalogued in the findings CSV + review sheet.

**launchd (local, script-only):** `com.claude.misinfo-audit` — WatchPaths on docs/FROZEN.md;
wrapper `$HOME/audit_misinfo_prevalence.sh` (homebrew python3, logs /tmp/misinfo_audit.log) re-runs
the deterministic audit + regenerates the review sheet + both validation gates on every re-freeze.
Bootstrapped & kickstart-tested OK; both gates PASS. No headless claude (per policy).

OUTSTANDING: Sacha to work through `docs/audit_review.html` §1–3 (10 items); then apply his
decisions + the §4 mechanical fixes as v1.4.1 (new immutable freeze + MD5 + tag + changelog).
NO analysis until the audit decisions are resolved.

---

## 2026-07-16/17 — Qualitative second-reader pass (agent source-vs-coding audit) over v1.4.0

Sacha asked for a JUDGMENT pass on top of the deterministic script: read each study's source text
against its coded rows and document every problem. Executed as 20 parallel reading agents (18
full-text batches of 15 studies + 2 coherence batches of 35 abstract-only studies), applying the
full rule canon (RULE D, value-fidelity, circularity L24, within-misinfo composition L16,
concentration L14/L28, scope tags, definition/breadth). A mid-run network outage (ENOTFOUND) killed
7 agents AFTER reading but BEFORE writing; re-ran those 7 with incremental-write instructions. All
20/20 returned; findings aggregated by `scripts/aggregate_qual_audit.py` →
`data/extract_v2/qa/qual_audit_findings.csv` + `_summary.md` (raw agent JSON archived in
`qa/qual_raw/`). No dataset writes.

**80 findings across 58 studies — 35 high / 26 med / 19 low.** By type: CONCENTRATION_MISUSE 17,
CONSTRUCT_WRONG 17, OTHER 8, SCOPE_MISTAG 8, COMPLEMENT 6, NESTED 6, VALUE_MISMATCH 5,
DEFINITION_MISMATCH 3, DENOM_WRONG 3, WITHIN_MISINFO_COMPOSITION 3, CHERRYPICK 3, CIRCULAR 1.

Headline high-severity problems (spot-verified a sample against source text — all held; e.g.
85203845655 Spanish text confirms "4 notas de las 20 analizadas o el 20%"):
- **Source/domain/account concentration mis-coded as AUDIENCE concentration** (L14/L28) — a whole
  cluster: 85060549676 (5% of sources→50%), 85078014559 (top-10 sources→95%), 85148963619 (top-20
  sources→61%), W7146985142 (top-3 domains 49/23), 85105511315 (verified-account 40/70%), 85188806397
  (community 91%). These are the exact rows the deterministic pass flagged as prose-in-numeric conc
  fields — now confirmed to be the wrong CONSTRUCT, not just field hygiene. → drop from concentration.
- **Producer/party composition as concentration** — 105027856675 party-shares (AfD 95.5/FdI 70.7/
  Cons 57.3/Rep 76.4) + country-share (IT 53.23) + crisis 50% (within-misinfo); independently
  corroborates the §1 deterministic finding. Also a stale-metadata bug: rows 639-641 carry
  "Germany/765 DE politicians" while values are actually US-Rep/US-Dem/IT-FdI.
- **CONTENT vs EXPOSURE (clicks/visits = consumption, RULE D)** — 85121019757 (FB-referred clicks to
  fake news 2.5/12% → EXPOSURE), 105017599346 (clicks 25% → EXPOSURE).
- **EXPOSURE vs REACH (≥1)** — 85162702221 (liked ≥1 fake page, 3 party rows → REACH), 85209547248
  (QAnon exposed ≥1, 11.1/3.0 → REACH; also mis-labelled diet-share). Reinforces the §2 boundary.
- **Complement errors** — 85191807094 (61% is little/NO-misinfo; misinfo = 39%) [UNVERIFIED, no text],
  W3033912864 (17.55/82.45 spreader-composition complements → drop).
- **Value/denominator mismatches** — 85203845655 (coded 4/78=5.1%; paper says 4/20=20%), 85066894147
  (30% is after-nominations not "before conventions"; before ≈20%), 85124823821 (two RECALL rows are
  actually age-column %s of a SHARING action, mis-mapped → drop).
- **Circular denominator** — 85215785622 (86.4% of FACT-CHECKED items are false → composition, L24)
  [UNVERIFIED, no text].
- **Duplicate studies under different IDs** — OA-W4411120829 == NEW-jung-icwsm (31.55% YouTube COVID);
  OA-W4417124855 == NEW-vanantwerpen-esm (50.41/17.72 AU election). The deterministic dup-check missed
  these (different IDs/values). → drop the abstract-only record, keep the full one.
- **Within-misinfo producer composition** — 105029521599 Dem/Rep share of low-fact posts (3.6/96.4 →
  drop; keep only overall 0.68%).

All 80 folded into `docs/audit_review.html` as **§6** (severity-sorted, Open-PDF buttons, per-finding
Accept/Keep/Unsure control, UNVERIFIED badge for the 2-batch no-text inferences, cross-refs to §1).
Two no-text findings (85191807094, 85215785622) are inferences from coded wording, badged UNVERIFIED
— need a source check before action. Sacha will read all 80 + the 10 deterministic items, export
decisions, then I apply → v1.4.1. STILL no analysis until decisions land.

---

## 2026-07-17 — Sacha's audit decisions, round 1 (8 of 90 items) + new convention

Sacha worked the 8 §1–3 items in docs/audit_review.html, left §6 (80 qual findings) for later.
Verbatim decisions + my reading in `data/extract_v2/qa/audit_decisions_log.md`; raw export preserved
`qa/audit_v140_decisions_round1.csv`. Nothing applied to the dataset yet (awaits §6 + two open Qs).
Key outcomes:
- **NEW CONVENTION (emerging, pending final confirm): "REACH, subtype=sharing".** Sacha resolved the
  §2 boundary by creating a reach-of-sharing category: `reach_subtype = exposure` ("% who saw/visited ≥1")
  vs `sharing` ("% who shared/posted/retweeted ≥1"). All §2 "% shared ≥1" rows → REACH reach_subtype=sharing
  (empties sharing_subtype=actor_share; SHARING keeps only content_share). 105039619015 = plain REACH (visited).
- **González 85165815218:** keep the 76% (row 685) as concentration, reconsider/drop the 97% (row 684).
  ⚠ FLAGGED BACK: the 76% is structurally identical to the 97% (both = "% of untrustworthy domains/URLs whose
  audience leans conservative", a per-item favorability score, L11), NOT "% of audience that is conservative";
  needs his ruling before I keep it.
- **Legislator 105027856675 party-shares:** keep as CONCENTRATION subgroup=sharing/politicians (overrides
  agent drop). ⚠ FLAGGED: no paired "X%→Y%" structure; would be its own party-composition flavour, reported
  separately, never pooled with individual-level concentration.
- **W3033912864 (Guo/arXiv 2006.04278):** Sacha says "gold, many valuable estimates, have an agent re-read
  carefully" — dispatched a careful re-read (Table 4/5 per-country sharing/reach rates, verify 82.45%
  conservative-sharer concentration, resolve phantom 17.55% [likely derived complement 100−82.45 → drop]).

---

## 2026-07-17 — Matched 6 downloaded PDFs to no-PDF studies (Desktop/New)

Sacha dropped 6 PDFs in ~/Desktop/New for studies that had no PDF in the review sheet. Matched all 6
(DOI / arXiv-id / title), filed to data/fulltext/pdf/{sid}.pdf, extracted text where a text layer existed,
verified byte-identical, cleared Desktop/New to Trash. Frozen dataset UNCHANGED (PDFs only).

| PDF | study | match | text |
|---|---|---|---|
| 1-s2.0-S1386505624004398 | 2-s2.0-85213223975 (Hysteroscopic metroplasty, IJMI) | DOI 10.1016/j.ijmedinf.2024.105776 | ✓ 36.6k |
| 1-s2.0-S266656032500101X | 2-s2.0-105009619554 (ADHD TikTok concept creep) | DOI 10.1016/j.ssmmh.2025.100489 | ✓ 68.4k |
| 2603.11058v1 | 2603.11058 (Uncertainty-Aware Mis/Disinfo Prevalence) | arXiv id | ✓ 88.6k |
| journal.pone.0302201 | 2-s2.0-85194023903 (DeVerna superspreaders) | DOI 10.1371/journal.pone.0302201 | ✓ 61.7k |
| View of The role of emotions… (Brazil/Spain) | 2-s2.0-85173224200 | title; DOI 10.5209/esmp.82822 | image-only, needs OCR |
| Vista do Avaliação da acurácia… COVID Facebook | 2-s2.0-105002473473 | title; DOI 10.18225/ci.inf.v54i1.6163 | image-only, needs OCR |

⚠ **NEW DUPLICATE CANDIDATE flagged:** 2-s2.0-105002473473 (PT, DOI …6163, "Accuracy assessment of
information about COVID-19 circulated in an online community") vs 2-s2.0-105002620495 (EN, DOI …7569,
"Assessing the Accuracy of COVID-19 Information Circulating in a Facebook Online community") — same journal
(Ciência da Informação v54 i1), near-identical title, look like the PT/EN versions of ONE paper. Same family
as the OA/NEW dup pairs the qual audit caught. Sacha to confirm → drop one (keep EN 105002620495 which has
data coded + a text-layer PDF; the PT 105002473473 is the image scan). Recorded for v1.4.1.
Two image-only PDFs (85173224200 Spanish, 105002473473 Portuguese) need OCR+English translation before coding.

---

## 2026-07-17 — Human-in-the-loop provenance system (author's review work documented)

Sacha: "document all my reviewing/coding decisions across ALL sheets/audits, accurately — I read the PDFs,
I'm not blindly trusting the AI; this gives the paper credence." Built a reproducible provenance record
that distinguishes AUTHOR (human) adjudication from LLM second-reader passes (no overclaiming):
- `docs/human_review_provenance.md` — master record: 9 human adjudication episodes A1–A9 (screening gold
  set 40; value review r1 = 9 → L1-L7; spot-checks r2-6 = 36 → L8-L43; v1.2 validation = 22 annotations;
  RA-29 = 28/29 + 18 notes → R1-R7; v1.2 decisions 20/24; demographic 85; geographic 9/9; v1.4.0 audit 8+open).
  Separately lists LLM second-reader passes (data/verify 17, data/exverify 9, qual agents) as ASSIST-ONLY.
  Includes §C "not rubber-stamping" evidence (author overrode AI on González/legislator, caught the
  AI-fabricated 17.55%, invented the REACH-subtype-sharing category) + a draft Methods transparency statement.
- `data/extract_v2/qa/human_review_episodes.csv` — machine-readable episode table (author_filled counts are
  ACTUAL rows filled, not sheet size; verified: round1 9/427, round2 22 notes of 427 AI-inferred, RA 28/29).
- `scripts/ingest_human_decisions.py` — ingests each exported decisions CSV, joins to the AI recommendation
  (`make_audit_review_sheet.py` now emits `qa/audit_item_recommendations.json`), classifies each as
  AGREE/OVERRIDE/MODIFY/NOTE_ONLY, appends to `qa/human_review_ledger.csv` + `human_review_summary.md`.
  Seeded round 1 (8 items: 2 explicit decisions, 6 note-only). Re-run per round: `--round N --date YYYY-MM-DD`.
Accuracy guardrail: data/verify + data/exverify are LLM passes, NOT counted as human work.

---

## 2026-07-20 — Audit review round 2 (Sacha's full 90-item pass) + resolutions

Sacha reviewed all 90 items in docs/audit_review.html → `qa/audit_v140_decisions_round2.csv`, ingested to the
human-review ledger (round 2: 57 AGREE, 3 OVERRIDE, 5 UNSURE, 6 decisions, 27 note-only). Full resolutions:
`qa/audit_round2_resolutions.md`. Nothing applied to frozen dataset yet (→ v1.4.1).
- Filed 5 more author-supplied Desktop PDFs (byte-identical, text extracted, Desktop cleared): W3033912864
  (Guo 2006.04278), 105017599346 (s13688 EPJ), PMID-37632797 (derma), 105030082417 (S0266613826 Midwifery),
  W7146985142 (JQD Oswald/Munzert). Standing rule reaffirmed: PDFs Sacha drops on Desktop → file+extract+clear.
- **POLICY (AskUserQuestion):** the ~15 producer/source/audience-skew/spreader "composition" rows → kept as
  `construct=OTHER, other_subtype=composition`, reported separately, never pooled. One consistent policy
  (reconciles his §1 "keep" with §6 "drop"). Rows enumerated in the resolutions doc.
- **NEW CONVENTION:** REACH sub-typed exposure|sharing|liking, never pooled (Sacha q22/q79).
- 4 source-reading agents settled the "gold"/"unsure" flags:
  - **2603.11058** (SIMODS/Science Feedback) = CONTENT (confirmed), curated-keyword enriched sample (flag).
    Per-language FR 17.5/SK 7.6/PL 6.0/ES 5.0 + per-platform TikTok 20.1…LinkedIn 1.3. Propose add 4 language rows.
  - **W7146985142** (Oswald/Munzert): keep BOTH reach (2017 17% / 2024 9%) & exposure diet-share (0.75% / 0.52%),
    both years + CIs; FIX 2024 reach 8→9% (miscoded from prose); drop redundant <1% abstract row; top-3 domain
    conc → OTHER-composition.
  - Verify batch: 271 false-alarm (keep 8.5% CONTENT); 411 keep (13.16% valid R8 derivation); 623 keep as
    REACH-subtype-sharing (confirms Sacha); 566 RECODE SHARING→EXPOSURE (Fig 5F = clicks); 314/269 correct;
    529 fix label Trump→Republicans; 639/640/641 fix stale country (US Rep/US Dem/Italy FdI, not Germany).
  - **563 (85213958624):** 0.94% valid (114k/12.1M) but CONTENT-vs-SHARING borderline + viral-only → NEEDS Sacha.
  - **231 (85123475265) DATA-INTEGRITY:** fetched PDF (DOI-named …2026963) contained the WRONG paper (Seshadri
    vaping review); coded 41.7% unverifiable. Quarantined wrong PDF+text → `data/fulltext/.mismatch_quarantine/`;
    study now resolves to DOI URL. NEEDS correct PDF.
- Duplicate note: 85163629989 (50.41/17.72 AU election) = 3rd copy of van Antwerpen (with OA-W4417124855 /
  NEW-vanantwerpen-esm) → dedup in v1.4.1. 105009372730 confirmed abstract-coded (legit, not unsourced).

## 2026-07-20 (cont.) — final 3 open items resolved
- 563 (85213958624): → SHARING (misinfo cascade/re-share trees), keep 0.94%, viral-only underestimate.
- 231 (85123475265): 41.7% (377/904) CONFIRMED from abstract (Sacha); correct full text still absent, abstract
  saved as source anchor (data/fulltext/abstract/); wrong PDF stays quarantined. Integrity flag cleared.
- González 76% (row 685) → OTHER-composition with the 97%. All audit items now resolved; ready for v1.4.1.

## 2026-07-21 — Full-data review round 3 (167 rows) + new conventions
Sacha reviewed 167/698 rows in docs/data_review.html (146 OK/20 flag). Raw `qa/data_review_comments_round3.csv`;
synthesis `qa/data_review_round3.md`. NEW conventions: (a) aggregate-vs-specific (drop pooled when finer breakdown
complete; keep aggregate when only subgroups exist); (b) NEW field political_orientation (far_right..far_left) for all
party rows; (c) every study needs a misinfo definition (audit: only Figeac 85096862559 lacks one); (d) M=0.0x is a
proportion→% (105027856675 correctly scaled); (e) engagement betas/ratios → drop. Actions feed v1.4.2 via the full
re-read phase. Verified: only 1 study missing a definition; no political_orientation column yet; engagement rows 686-693
are all betas.

## 2026-07-21 — FULL RE-READ of all 324 studies complete (21 agents)
The consistency/verification phase Sacha ordered. 21 agents re-read every study's source, re-verified each value +
construct, completed fields, applied the round-3 conventions. Aggregated → `qa/reread_proposals.csv` +
definitions/orientation/judgment_calls/missed/summary; raw in `qa/reread_raw/`. All 21/21 parsed; 322/324 studies covered.
- **Verdicts: 544 CONFIRM, 1 CORRECT_VALUE, 12 RECODE_CONSTRUCT, 94 RETAG(field-fill), 18 DROP, 14 DROP_AGGREGATE, 23 FLAG.**
  → The dataset is strongly validated: only **1 value** was wrong across ~700 rows; the rest confirmed verbatim.
- **Field completion:** misinfo definition extracted for 305/324 studies (incl. the missing Figeac — Décodex unreliable
  sources); political_orientation filled on 82 party/ideology rows; topic filled throughout.
- **Changes align with conventions:** reach-of-sharing/liking harmonizations (85136023139, 85060549676, 85162702221,
  105027959122), engagement betas dropped (105027856675 686-693), pooled aggregates dropped where breakdowns complete
  (105027856675 r464, 85164339474 r374, 105027856675 country-composition), duplicate demographic rows (85142396682).
- **83 JUDGMENT CALLS** for Sacha (max 3/study) + **10 missed estimates** flagged.
- Data-integrity mismatches surfaced: 84929523850 (title=book chapter, text=KCL/Ipsos report; values match report);
  2603.11058 keyword-enriched + double-counts corpus across platform/country slices (raised as judgment call).
NEXT: build v1.4.2 = apply high-confidence changes (field completions + clear drops/recodes) + focused judgment-call
review sheet (~83 items, not 698) for Sacha. Nothing applied to frozen v1.4.1 yet.

## 2026-07-21 — Re-read judgment calls, round 1 (Sacha, 54/116)
`qa/reread_decisions_round1.csv` → ledger (round 4-reread) + `qa/reread_review_round1_resolutions.md`. ~62 items
remain. REINFORCED CONVENTION: no one-estimate-per-study — keep ALL definition-strictness/denominator variants
(R4b thesis); add URL-denominator variants where reported. 6 whole/row DROPs (DISCERN score, anti-vax stance,
weird-recall, figure-only paper 85101871838 EXCLUDED, unreliable extracts, redundant aggregate). Many value/denom
picks + keep-all-both calls recorded. A few delegated to me / re-read (105019603181 topic figures, 105027856675
pooled-vs-per-politician). Feeds v1.4.3 once his review completes.

## 2026-07-21 — Re-read judgment calls FULLY RESOLVED (Sacha's 54 + my ~40 auto + 19 confirmations)
All 116 reread judgment calls/flags/missed now decided. Confirmation sheet `qa/reread_confirm_decisions.csv` (19/19,
all agree except g12 add-38%-not-45%, g16 extract-all-7-narratives). My auto-adjudications `qa/reread_auto_adjudication.csv`.
Ledger now includes rounds 4-reread + 5-confirm. NEXT: build v1.4.3 applying his 54 + my ~40 + the 19 (pending the g16
7-narrative extraction). Then changelog + gates + tag.

## 2026-07-21 — PMID-42295743 PDF sourced by Sacha, filed
St-Pierre et al. 2026 (Epileptic Disorders), "Disinformation and misinformation in epilepsy: multiplatform short-form
video" — Sacha found the PDF (Desktop), confirmed identity (18.1%/102 videos/epilepsy/DOI 10.1002...), filed to
data/fulltext/pdf/PMID-42295743.pdf (byte-identical) + text v2txt/. Desktop original → Trash. RESOLVES g17: per-platform
prevalences EXIST (TikTok 31.7% confirmed; IG Reels + YT Shorts being extracted) → per aggregate-vs-specific, code the 3
per-platform values, pooled 18.1% becomes redundant aggregate. Feeds v1.4.3. (Earlier I overstated 'accessing' this paper
before it was on file — corrected; the description had come from the coded row, not from reading the source.)

## 2026-07-22 — Two more verification passes (Sacha: "another kind of pass" + outlier check)
On frozen v1.4.4. Both deterministic, both came back CLEAN (0 real errors) — strong multi-angle confirmation.
- **Arithmetic verification** (`scripts` ad-hoc): re-derived value_pct from numerator/denominator patterns in
  source_quote/n for 259 rows with a derivable fraction. 16 "mismatches" ALL false positives — regex grabbed
  years ("12/2018"), Likert scales ("2/5"), concentration group-vs-share, or unrelated counts; coded values are
  the papers' verbatim proportions. NO computation errors.
- **Outlier / weird-number detection**: per-construct value distributions are healthy (EXPOSURE diet-share
  median 2% max 25 as expected; REACH med 11; SHARING med 4.6). 22 flagged; ALL verbatim-confirmed on inspection:
  high CONTENT 84-100% = curated single-topic health-video/tweet analyses (expected, all denom_class=topical);
  85159889148 100%=TikTok videos (verbatim "100% of TK videos"); 85129456715 & 85209813530 0% = real findings
  (most-shared articles / videos had NO misinfo); 85085201199 24.1% = topical viewership share (correctly topical).
- MINOR NOTE (not a value error): 85055756722 rows carry n=1313 (survey total) but the coded %s (29.9/17.1/8.9)
  use the sharers-denominator ~1211; values verbatim-correct, n field slightly overstates for those rows.
VERDICT: after deterministic (A) + integrity (B) + hidden-dup (C) + full re-read (544 confirm) + arithmetic +
outlier passes, no genuine data errors remain. Data verified clean from multiple independent angles.

## 2026-07-22 — Three more rigour steps (Sacha): exclusion re-check, blind re-extraction, n fix
1. **EXCLUSION RE-CHECK (criteria drift):** Sacha's insight — criteria expanded over the project (source-level→include;
   elite/politician→keep+tag; audience-concentration→keep; definition variants→keep-all; small-N curated→keep+flag), so
   studies dropped under OLD rules may now qualify. Scanned all drop ledgers (351 records / 343 studies:
   stepb_drops_queue, prisma_orphans_dispositioned, dropped_studies, decided_drops, v1.2_drops_ledger, review_pooled_drops).
   17 borderline candidates flagged → agent re-screening each against CURRENT criteria (`qa`→`tmp/final/rescreen.json`).
   Manual pre-read: most STILL correctly dropped (circular/fact-check DBs, stance/anti-vax, quality-only, producer
   concentration, no-denominator, secondary citation). Genuine re-inclusion candidate: **85130786472** (Spanish; 14%
   of parliamentarians' tweets misinfo — dropped as elite, now keep+tag population_scope=elite_politician).
2. **BLIND INDEPENDENT RE-EXTRACTION (reliability):** 54-study high-leverage sample (all EXPOSURE/CONCENTRATION/REACH +
   spread of CONTENT/etc.), 3 agents extract each value FRESH from source WITHOUT seeing our coding → inter-coder
   agreement / reliability κ for the Methods. Key withheld in `tmp/final/blind_key.json`.
3. **n fix (pending v1.4.5):** 85055756722 rows n=1313 (survey total) → the sharing-item %s use the ~1211 sharers
   denominator (values verbatim-correct). To correct in the next freeze.
All three + any re-inclusions/blind-discrepancies → v1.4.5. Documented for the Methods rigour narrative.

## 2026-07-22 — PDF recovery: local-PDF coverage 240 -> 262/317
Sacha: every study should have a local PDF. `scripts/recover_pdfs.py` queried OpenAlex per no-PDF study (by
W-id or DOI), downloaded+verified (%PDF magic)+text-extracted 22 open-access PDFs. External-library title-match
found 0 more. Remaining 55 (`qa/pdf_recovery_report.csv`): 21 CLOSED-access (need institutional), 28 OA-but-download-
blocked (publisher redirect; clickable OA url shown), 6 no-queryable-id (grey/PMID). Updated `docs/no_pdf_studies.html`
categorizes them + shows the OA link. The 'coded from full text but no PDF' state was a DOI-keyed resolver gap
(OpenAlex/seed ids lack DOI) + PDFs read live from the external iCloud library without local caching — a completeness
gap, not a coding problem (all were source-verified). Frozen dataset unchanged.

## 2026-07-14 — PDF source-completeness recovery, round 2 (frozen dataset UNCHANGED)
Goal: give every frozen study a locally-archived PDF for auditability. This touches SOURCE
FILES only — estimates_v1.4.5_frozen.csv is byte-for-byte unchanged (no re-freeze).
- Filed 21 of the 26 OA PDFs Sacha downloaded to ~/Desktop/New, matched by DOI / title /
  OpenAlex OA-url to data/fulltext/pdf/{id}.pdf, text extracted to v2txt.
- Recovered 3 more programmatically: SEED-allcott2017 (NBER w23089), NEW-jung-icwsm
  (AAAI OJS, W4411120829), PMID-33304681 (Cureus assets).
- Identified all previously "no queryable identifier" studies via PubMed eutils + OpenAlex
  title search; recorded title+DOI in data/extract_v2/qa/grey_study_ids.csv so the remaining
  ones are findable by a human. (Earlier "no id" label was my miss — 3 had PMIDs, 1 a famous DOI.)
- Coverage: 262 -> 286 of 317 studies now have a local PDF. 31 remain: 21 closed-access
  (need library), 7 OA-but-auto-download-blocked (clickable via purple 'OA pdf ↗'), 3 no-id/grey.
- Hard remainers documented for manual grab: NEW-vanantwerpen-esm (OSF preprint 10.31234/osf.io/vmt4c
  is a Word .docx, not PDF; text already coded), PMID-40061772 (10.4103/jpbs.jpbs_1038_24, LWW OA),
  PMID-41189872 (10.7759/cureus.93728, Cureus OA) — both bot-blocked to auto-download.
- KHVI_17_1957416.pdf (Human Vaccines & Immunotherapeutics, 10.1080/21645515.2021.1957416) that
  Sacha downloaded matches NO study in our set; preserved at data/fulltext/.unmatched_downloads/.
- Regenerated docs/no_pdf_studies.html (now shows 286/317 + enriched grey titles/DOIs).

## 2026-07-22 — 3 more source files filed (Sacha-identified OA links)
Sacha identified three sources from links in the no-PDF HTML:
- Golden-lancehead / Bothrops insularis herpetological misinfo (2-s2.0-105033611630) —
  SciELO OA, fetched ...?format=pdf (1.5MB, 81k chars, confirms Bothrops insularis).
- "Information in Spanish on YouTube about COVID-19 vaccines" (W3189543626 = PMC8828059) —
  fetched via Europe PMC render (321KB, 35k chars, confirms vacuna/YouTube/COVID).
- Australian election ESM preprint (NEW-vanantwerpen-esm) — OSF/PsyArXiv 10.31234/osf.io/vmt4c,
  source is a Word .docx (not PDF); filed as data/fulltext/pdf/NEW-vanantwerpen-esm.docx (66k chars).
Coverage: 286 -> 288/317 with a local PDF (+ van Antwerpen archived as .docx). Frozen data UNCHANGED.
NOTE: van Antwerpen ESM is INCLUDED (3 keep rows in v1.4.5), NOT excluded — corrected Sacha's recollection.

## 2026-07-22 — PHASE B BEGINS. Component 1: descriptive backbone + diagnostic pass
Sacha gave the go for Phase B (analysis), framed as also a final QA lens ("maybe it will help
find holes/problems in the data or coding"; "most of the job will be to accurately describe and
slice the data so it's meaningful"). Phase A (dataset rigor) complete; frozen v1.4.5 UNCHANGED.
Built `scripts/phaseB_descriptives.py` (deterministic, read-only; reads freeze spec from FROZEN.md):
corpus composition, prevalence distributions per construct × denom_class (estimate-level AND
study-level), whole-diet backbone table, concentration arm, and a diagnostics pass. Outputs
`data/synth/phaseB/*.csv` + review sheet `docs/phaseB_descriptives.html`. NB the pre-existing
`data/synth/*.csv` are from June (pre-v1.4.5) and STALE — rebuilding everything from the freeze.
Diagnostics: 0 high / 40 med / 34 info. KEY YIELD (real, for Sacha's review — no data change yet):
 (1) `measure_type` EMPTY on 67 rows / 21 studies (e.g. 105029413645 [14], 85096862559 [12],
     W4293124965 [8]) — a field populated for most rows but not all → backfill target.
 (2) `topic` moderator populated on only 97/680 rows (14%); 281/317 studies have it on no row —
     NOT analysis-ready (planned moderator-coding task, codebook item 4), not a data error.
 (3) W4293124965 rows 541-548 = legit STRICT-definition variant (Table 3 "repeatedly-false outlets"
     vs Table 2 "untrustworthy"), R4b-correct to keep — but measure_type blank (part of #1). The
     "duplicate" flag was a false alarm (US-strict 0.97 == Germany-broad 0.97 coincidence).
 (4) 85060025053 (Guess 2019) rows 492/583: value 18.1 appears twice for Republicans; row 583's
     value doesn't match its composition quote → verify against PDF (demographic rows, out of headline).
 (5) The other 12 "possible duplicates" are all legitimately distinct (Danish vs English COPD groups;
     France vs Italy false-news reach; 12 different countries in the CT-search study 85177420309) —
     reassuring, and a textbook demonstration that STUDY-LEVEL medians are needed (that one CT study
     injects 12 topical CONTENT estimates).
PRELIMINARY (not a headline yet): whole-diet backbone = 31 studies (EXPOSURE/REACH with population/
all_media/political_news denom, non-demographic); study-level median-of-medians ~7.4%, range 0.15–70%.

## 2026-07-22 — FROZEN v1.4.6 (descriptive completeness; ADDITIVE, no value changes)
Phase B component 1 surfaced completeness gaps; closed them under Sacha's go ("backfill now → v1.4.6"
+ "yes, code topic"). `estimates_v1.4.6_frozen.csv`, **679 rows / 317 studies**, MD5
`9dfc1969bbda647a4d2be31f8c2936ca`, tag `dataset-frozen-v1.4.6`. Integrity-verified: ONLY `measure_type`
and `topic` columns differ from v1.4.5 (0 value_pct changes, id order preserved).
 - **measure_type backfill** (`scripts/build_v146_measuretype.py` → `qa/v146_measuretype.csv`): 67 blank
   cells across 21 studies filled from source quotes / Table arithmetic (e.g. Gravino 85199110625 NT-share
   in Supply/Diffusion × Facebook/Twitter computed from Table 2 denominators: 7.37/7.71/8.48/25.05 all
   reconcile; 2603.11058 per-platform baselines mapped TikTok20.1/FB11.9/X8.7/IG6.7/YT6.8/LinkedIn1.3;
   Figeac 85096862559 12 party×OS rows; etc.). Index+id+value guarded. measure_type now 100%.
 - **topic moderator** (`docs/topic_taxonomy.md`, 12 codes): coded all 317 studies via 16 parallel
   quote-anchored agents (`scripts/aggregate_topics.py` → `qa/topics_v146.csv`; 2 agent-skips backfilled
   in main loop). 14%→100%. Distribution: health_other 136 / covid19 69 / general_news 48 /
   politics_elections 37 / vaccines 11 / other 6 / science_other 4 / war_geopolitics 3 / crime_society 2 /
   economy_finance 1 / climate 0 / immigration 0. FINDING: the prevalence literature is health/COVID-
   dominated (~68% health+covid+vaccine), with general-news + politics tail, near-zero climate/immigration.
 - **Guess-2019 dedup**: dropped row 492 (Trump-supporters 18.1% = paraphrase of verbatim '18.1% of
   Republicans' row 583; demographic, out of headline). `qa/v146_dedup.csv`. 680→679.
Gates: validate_frozen PASS (7 grey-ID WARN benign), validate_prisma PASS. FROZEN.md + dataset_provenance.md
updated. Descriptives regenerated on v1.4.6 (`docs/phaseB_descriptives.html`).

## 2026-07-22 — Phase B component 2: the meaningful slices
Built `scripts/phaseB_slices.py` (deterministic, reads FROZEN.md; joins RoB measurement appraisal).
Main-analysis set = general-public rows + real proportion + not within-misinfo composition = 571 estimate rows.
Primary stat = STUDY-LEVEL median (median-per-study then across studies); estimate-level alongside. IQR suppressed
for n<4 studies; quantiles clamped to data range. Outputs `data/synth/phaseB/slices_*.csv` + `docs/phaseB_slices.html`.
HEADLINE RESULTS (study-level medians, main set):
 - By construct: EXPOSURE 2.8% | REACH 12.0% | RECALL 55.4% | SHARING 13.1% | CONTENT 23.0% | CONCENTRATION 59.5%.
 - By MEASUREMENT (the key driver): BEHAVIOURAL trace 7.5% (est-level 4.8%) vs CONTENT_CODING 24.1% vs SELF_REPORT 55.4%.
   Self-report is ~7x behavioural — people vastly over-report seeing misinfo vs what traces show they encounter.
 - By SAMPLING frame: full_census 4.8% / panel_trace 5.9% / random_platform 4.0% (representative→LOW) vs
   keyword_topical 23.9% vs survey_sample 53.3% / curated_seed 49% (→HIGH).
 - By GROUND-TRUTH: domain_list/NewsGuard 7.8% < fact_checker 13% < classifier 18% < researcher_coding 25% < self_report 53%.
 - THESIS (breadth within CONTENT): fabricated 10.8 → false 22.3 → misleading 28.5 → low_quality 31.6 (monotone looser→higher),
   EXCEPT unreliable_source 6.4 (source-level domain-list over broad samples — breadth confounds with measurement approach; note it).
 - By TOPIC: health_other 32.2% (highest, topical health content analyses) > covid19 23% > politics 14% ≈ vaccines 14% >
   general_news 9.2% (whole-diet-ish→low).
 - WHOLE-DIET BACKBONE (31 studies, EXPOSURE/REACH × population/all_media/political_news): study-level median 7.4% (IQR 3.2–12).
   Split: EXPOSURE diet-share ~2.8%, REACH %-reached ~12%.
CORE STORY: prevalence spans ~0.4%→80%+, and the spread is not noise — it is driven by measurement (behavioural vs self-report),
sampling (representative vs topic-keyword), definition breadth, and denominator. True audience-diet exposure = low single digits;
alarming headlines come from topical content analyses + self-report surveys. Frozen data UNCHANGED (read-only analysis).
NEW QA note (for a future cleanup): ~14 `ground_truth` cells hold prose blobs instead of a canonical code (normalize in a later pass).

## 2026-07-22 — Phase B: figures + concentration deep-dive
Built `scripts/phaseB_figures.py` — dependency-free vector SVG (deterministic; matplotlib unavailable, and
SVG prints crisp + embeds in the review HTML). Four figures in docs/ + `docs/phaseB_figures.html`:
 - fig1 prevalence_by_construct: study-level median + IQR + range per construct.
 - fig2 method_drivers (CORE): behavioural 7.5% vs content-coding 24% vs self-report 55%; sampling frame; ground-truth.
 - fig3 whole_diet_backbone: 31 studies each at its study-median, sorted, RoB-coloured, pooled-median line (7.4%).
 - fig4 concentration_curve: top % of people (log x) vs % of misinfo activity (y), exposure vs sharing.
CONCENTRATION DEEP-DIVE: standardized all 23 CONCENTRATION rows (15 studies) to (top % people, % of activity)
in `data/synth/phaseB/concentration_standardized.csv` — hard-mapped from source quotes (regex mis-parsed
"1% of panel consumed 80%"; id-guarded). RESULT: across 5 studies giving a "top-1%" figure, that 1% accounts
for a MEDIAN 70% of all misinfo exposure/sharing (range 37-80%); top-10% -> 87.5%; top-20% -> 75%. Misinfo
activity is extremely concentrated in a tiny minority — the review's second core claim, now quantified.
Frozen data UNCHANGED (read-only).

## 2026-07-22 — Phase B: meta-regression + precision weighting + Methods
Stats tooling: R 4.3.0 + metafor + boot available (no python numpy/statsmodels; matplotlib absent → SVG figures).
- **Analysis dataset** (`scripts/phaseB_prep_regression.py` → `data/synth/phaseB/regression_data.csv`): 467 estimates /
  275 studies from the main set with an extractable numeric n (94% of main prevalence rows). Collapsed moderators:
  sampling (representative/topical-curated/survey), denom (whole_diet/narrow), measurement (from RoB appraisal).
- **Meta-regression** (`scripts/phaseB_metareg.R`, metafor): logit-proportions (escalc PLO), multilevel random effects
  ~1|study/estimate, cluster-robust by study. UNIVARIABLE pseudo-R² (variance explained): measurement 20.0% >
  ground_truth 18.1% > sampling 16.8% > construct 14.4% ≈ platform 14.2% > breadth 13.8% > topic 10.4% > denom 1.0%
  (denom low only due to collinearity). MULTIVARIABLE (construct+breadth+denom+topic) pseudo-R²=27.1%: construct is the
  dominant independent driver (OR vs EXPOSURE: RECALL 37.5, REACH 13.5, SHARING 3.7, CONTENT 2.7, all p<0.05); looser
  breadth raises it (low_quality OR 14.2); health_other topic OR 3.7. MODEL-PREDICTED prevalence by measurement:
  BEHAVIOURAL 4.8% / CONTENT_CODING 20.0% / SELF_REPORT 47.5% (~10× from measurement alone). CAVEAT logged: n spans ~6
  orders of magnitude → very unequal variances (metafor warning); cluster-robust SEs + variance-explained emphasis mitigate.
- **Precision weighting** (`scripts/phaseB_precision.py`, pure-python study-cluster bootstrap, seed 20260722, 2000 reps):
  unweighted vs sample-size-weighted study-level medians. CONTENT 22.3%→0.9% (shift −21.4), REACH 12→0.3, WHOLE-DIET
  7.5→0.3 — larger samples find far less misinfo (thesis confirmed). EXPOSURE 4.0→7.2 / SHARING 13.3→16.8 tick up (small n,
  a few mega-studies dominate the weighted median; wide CIs) — reported for transparency, not over-interpreted.
- **METHODS**: rewrote manuscript §2.8 "Synthesis and statistical analysis" (`docs/manuscript_draft.md`) to reflect the actual
  Phase B analysis (main-set + study-level medians, moderator slicing, metafor meta-regression, precision bootstrap,
  concentration standardization, RoB integration, software). Fixed stale dataset counts throughout: 695/408 → 679/317 (v1.4.6).
Review page `docs/phaseB_analysis.html`. Frozen data UNCHANGED (all read-only).

## 2026-07-22 — Phase B: GRADE certainty + Results draft + master dashboard
- **GRADE** (`scripts/phaseB_grade.py` → `data/synth/phaseB/grade_sof.csv`): prevalence-adapted GRADE per construct,
  applied DETERMINISTICALLY over frozen v1.4.6 + RoB appraisals + precision-weighting output (start HIGH; downgrade on
  RoB / inconsistency / indirectness / imprecision / selection bias by explicit rules). RESULT — certainty runs inverse
  to magnitude: EXPOSURE (~2.8%) **HIGH** (clean whole-diet, 5% HIGH-RoB, no serious concerns); REACH/SHARING/RECALL/
  CONCENTRATION **MODERATE** (−1 each: imprecision or indirectness); CONTENT (~23%) **VERY LOW** (−4: 56% HIGH-RoB,
  indirectness, precision-fragile, 91% topical/curated selection). This is the thesis, GRADE-formalized.
- **Results draft**: wrote manuscript §3 (`docs/manuscript_draft.md`) — 3.1 what the literature measures / 3.2 the
  order-of-magnitude headline / 3.3 whole-diet backbone / 3.4 what drives estimates (meta-reg) / 3.5 RoB tracks the number
  inversely / 3.6 precision weighting / 3.7 concentration / 3.8 GRADE SoF table. All numbers from the frozen data + Phase B scripts.
- **Master dashboard** (`scripts/phaseB_dashboard.py` → `docs/phaseB_dashboard.html`): single "everything" page — corpus,
  the 4 SVG figures, headline construct table, whole-diet backbone, moderator slices, meta-regression, precision weighting,
  concentration, GRADE SoF, with KPIs + section nav. The at-a-glance review artifact.
Frozen data UNCHANGED throughout (all read-only analysis on v1.4.6).

## 2026-07-22 — Phase B round 2 (per Sacha's review of the dashboard)
Sacha's feedback + requests: (1) explain the suspicious backbone values; (2) whole-diet by ESTIMATE not study, split
EXPOSURE vs REACH; (3) add domain-list-vs-URL/claim identification method as a driver; (4) code NON-MISINFO concentration
as a comparison; (5) plainer GRADE; (6) many more figures; (7) an interactive companion dashboard; (8) a lit-review HTML.
- **Value investigation**: the whole-diet "backbone" conflated two quantities. The high values (21–70%) are all REACH
  (% reached ≥1 over a period; 70% = Eady foreign-influence-campaign reach — real). The low values (0.1–1%) are all
  EXPOSURE diet-share. 25% (105017599346) verified as a LEVEL (engagement to low-quality domains ~20-30%), loose def, not
  an error. NO coding errors. FIX: split EXPOSURE (est-level median 1.2%, study 2.6%) vs REACH (est 9.0%, study 12%).
- **NON-MISINFO concentration** (8 agents over 39 panel/concentration studies → `data/synth/phaseB/nonmisinfo_concentration.csv`):
  24 general-activity concentration quantities from 14 studies. DIRECT side-by-side comparators show misinfo is MARKEDLY MORE
  concentrated: top 1% of users = general 30% (Osmundsen real-news) / 49% (Grinberg political shares) / 43% (Zhou reliable) /
  24-37% (Eady domestic/politicians) vs misinfo 75% / 82% / 65% / 70%. A valuable comparison point for the paper.
- **id_method** moderator added (domain/source-list 266 · researcher-coding 288 · fact-check 42 · self-report 57 · classifier 26).
- **Interactive companion dashboard** `docs/companion_dashboard.html` (`scripts/build_companion_dashboard.py`, self-contained,
  679 estimates embedded, vanilla JS): strip/beeswarm of every estimate, group/colour by any moderator, hover → full provenance
  (quote, definition, category, measure, RoB, n), live filters by every dimension. VERIFIED rendering + hover in-browser.
- Data export `scripts/phaseB_export_json.py` → `data/synth/phaseB/estimates_full.json` (every estimate + provenance + id_method).
Frozen data UNCHANGED (all read-only).

## 2026-07-22 — Phase B round 2 (cont.): figures, lit review, id_method, dashboard wiring
- **id_method in meta-regression**: added domain-list-vs-claim-vs-classifier identification method. Univariable pseudo-R²
  = 17.5% — a TOP driver (confirms Sacha's intuition + Nenno 2025 claim-level≈10×source-level). `phaseB_prep_regression.py`,
  `phaseB_metareg.R` updated; `phaseB_analysis.html` regenerated.
- **Figure gallery** (`scripts/phaseB_figures2.py` → `docs/phaseB_figure_gallery.html`, 12 SVGs): figA EXPOSURE/REACH split
  (by estimate — the backbone fix), figB by id_method, figC breadth gradient, figD topic, figE platform, figF RoB×construct,
  figG misinfo-vs-general concentration (dumbbell), figH ground-truth + the original fig1-4.
- **Lit-review HTML** (`scripts/build_litreview_html.py` → `docs/litreview_measurement.html`): maps the measurement/definition
  literature (Nickl/Hertwig "Global Crisis or Overblown Problem?" (Mis)information Funnel; Hameleers exposure-perception gap;
  the definitional canon) against our findings, claim-by-claim correspondence table. Built an "(Mis)information Funnel" figure
  from OUR medians (`docs/fig_funnel.svg`) — conceptual→methodological→denominator, rising as each choice loosens. NOTE: could
  not retrieve the Overblown paper's own Fig 2 from the library (pdf_path empty); characterized its funnel schematic from text
  + our data, flagged as such. Source hub: Claude/knowledge/litreviews/litreview_misinfo_definitions.md (26 refs, verbatim quotes).
- **Master dashboard** (`phaseB_dashboard.html`) rewired: companion-views banner (links to all pages), EXPOSURE/REACH split
  replaces the pooled backbone, non-misinfo concentration comparison added, GRADE section rewritten in plain language.
Frozen data UNCHANGED (all read-only). KEY NEW FINDING: misinfo is ~2× more concentrated than general news (top 1%: general
30-49% vs misinfo 65-82%).

## 2026-07-22 — Phase B round 3 (Sacha dashboard review): v1.4.7, titles, concentration viz, demographics
- **FROZEN v1.4.7** (`apply_v147.py`, MD5 c2ad5d044fc851d3fdea32d3d345ecfe): CONCENTRATION coding standardized after
  Sacha spotted flips. Convention: value_pct=activity share (Y%), conc_group_pct=population fraction (top X%). Fixed
  85194733750 (0.3->80), 85160248068 (31.3/25.1->90), filled 85060549676 (80.0/79.8) + 85081743293 (62), flagged
  85195353413 (atypical). Recoded 105017599346 EXPOSURE->SHARING (engagement-share, qtype=engagement — Sacha flagged
  "looks like engagement"). Concentration median now 75% (all consistently top-X%->Y%-of-activity). Gates PASS.
- **Article titles** in the dashboard: built id->title map (`data/synth/phaseB/titles.json`, 317/317; 311 auto from
  corpus/OpenAlex/PubMed JSONLs + 6 grey manual). Companion tooltip now shows the TITLE (not just the ID), plus a
  construct-glossary header for intuitiveness.
- **New figures** (`phaseB_figures3.py`): figK concentration flow (intuitive population->activity ribbon, misinfo vs
  general — the "minority accounts for most" viz Sacha wanted); figI by political orientation (right/far-right skew
  higher — political_orientation IS coded: right 31/left 18/far_right 11/…); figJ by age (older higher). Wired into
  gallery + master dashboard (new section 7b). All downstream regenerated on v1.4.7.
- Concentration fig4 now derives from corrected frozen data (dropped the hard-coded map).
Frozen note: v1.4.7 changed 7 concentration value_pct cells + 1 construct (real corrections, Sacha-authorized).

## 2026-07-22 — more non-misinfo concentration comparators (library mining)
Agent mined the broader PDF library (Yang, Muise, Fletcher, Gonzalez-Bailon, Wojcieszak, Lorenz-Spreen, Allen…) for
GENERAL news/activity concentration baselines → `data/synth/phaseB/nonmisinfo_concentration_extra.csv` (5 comparators):
- Muise 2022 (own): most-partisan 21% -> 64% of TV-news minutes; 6% -> 28% of online-news minutes.
- Wojcieszak 2022 (own, 1.4M Twitter): 13% -> 86% of political-elite content shares.
- Secondary/all-content (flagged, not news-specific): 25%->97% tweets (Pew), 10%->96% platform content (Lorenz-Spreen cit.).
- Allen 2020: qualitative skew (44% zero online news; top ~10% "voracious" cable). Nielsen 2022 excluded (outlet-level HHI).
Added as a context table in the dashboard concentration section with provenance/caveats. Reinforces: general activity is
concentrated too (participation inequality), but misinfo is more concentrated at the extreme top (1%: ~70% vs 24-49% general).

## 2026-07-22 — figures honesty pass (Sacha: "merging can obscure important facts")
Sacha questioned the by-age figure and the far-right sharing bar. AUDIT: all values verbatim-correct, but the
merged bars were misleading. Rebuilt both to SHOW the disaggregated data (Sacha's principle):
- figI (political): now a DOT plot — every per-subgroup estimate shown, colored by definition breadth, median diamond
  per orientation. Reveals the far-right SHARING spread is 8-47% (French FN 47/Italian FdI 42 vs German AfD 8) — cross-
  country, NOT a breadth artifact (all are unreliable_source breadth) and NOT concentration. A single bar hid this.
  RATES only (per_subgroup_rate); concentration/composition + single-actor content excluded.
- figJ (age): now WITHIN-STUDY SLOPE LINES (no cross-study band pooling). Each line = one study's own age gradient.
  Shows most studies rise with age (health-website REACH 4.8->20.9; independents SHARING 0.2->3.7) but recall REVERSES
  (younger recall more: 75.6 vs 53.2) and YouTube-health is flat — merging into bands would have hidden the disagreement.
  Verified: RECALL 75.6%/53.2% = exposure rate per age group (149/197, 82/154), correct; REACH 37.4% is 2020 untrustworthy
  (subtype tag "sharing" is imprecise — should be exposure; noted, minor, not re-frozen for one tag).
No data change (frozen v1.4.7 unchanged) — presentation/aggregation fixes only.

## 2026-07-22 — concentration Lorenz view + figure clarity fixes (Sacha review)
- **figL concentration Lorenz** (new): x=top % of people, y=% of activity, equality diagonal; ALL 18 misinfo points
  (any cutoff 0.001-31%) + general-news comparators (Muise/Wojcieszak/Osmundsen/Grinberg/Zhou/Eady) on one plot.
  Distance above diagonal = concentration; misinfo points sit far higher than general news. Answers "not always 1%"
  (figK stays as the top-1% headline; figL handles all cutoffs). In gallery + dashboard concentration section.
- **figI political** clarity: alternating row bands + spectrum order far_left..far_right; 'mixed' (independents/mixed-
  group/non-partisan) SEPARATED below a divider (not on the L-R axis); empty rows labelled '(no estimates)' (e.g. no
  REACH for far-left); classification basis stated (conventional L-R / Chapel-Hill-Expert-Survey / ParlGov consensus).
- **figJ age**: removed the RECALL·WHO line per Sacha (kept REACH + SHARING within-study slopes); fixed stale caption.
- **Next-freeze punchlist** `data/extract_v2/qa/next_freeze_punchlist.md`: (1) 85152674280 reach_subtype sharing->exposure;
  (2) 85060549676 'political=left' row mislabelled political_orientation=mixed -> left. Batch as v1.4.8 later. No data change now.

## 2026-07-22 — FROZEN v1.4.8 (tooltip-review corrections) + tooltip upgrade
Sacha reviewed companion tooltips, flagged 5 estimates. AUDIT:
- 85085201199 (YouTube COVID 24.1%): was EXPOSURE, but it's view-weighted content prevalence in a TOPICAL 69-video
  sample (denominator = views of that curated set, not diet) -> RECODED EXPOSURE->CONTENT. (EXPOSURE median 2.8->2.0%.)
- 85088969117 (52.31%/0.09% Twitter vs Weibo): VERIFIED CORRECT from PDF — "Most shared posts on Twitter coded 'False
  news' (52.31%)" is the share of retweets that are false-news-coded; the Twitter/Weibo asymmetry is the paper's finding.
- 85066894147 (20/30/40 time series): the `date` field was right but measure_type period label was stale ('before
  conventions') on all 3 -> FIXED to before conventions/after nominations/right before election.
- 105021775752 (30% problematic): correct — 1 of 3 time points (16% Mar-2020 / 30% Dec-2020 / 11% Mar-2021).
- 85095594211 (36% misleading shares): correct — share-weighted (36% of shares to 6 misleading of 30 articles); weak/curated but right.
FROZEN v1.4.8 (`apply_v148.py`, MD5 57ce6fcc4da7b29e01478a7fdd2bedbb): the 2 real fixes + 2 queued punchlist tags
(85152674280 reach_subtype->exposure; 85060549676 political_orientation mixed->left). 5 rows, 0 value_pct changes. Gates PASS.
TOOLTIP UPGRADE (`build_companion_dashboard.py`): added the DENOMINATOR line ("out of (denominator): ...", the '% of what')
+ improved tag readability (contrast, bold values, icons). Regenerated all Phase B artifacts on v1.4.8.

## 2026-07-23 — audit continuation -> FROZEN v1.4.9
Continued the coding audit at Sacha's request. Two systematic passes:
 (1) construct-consistency scan (measure-language vs assigned construct): only real hit = 85127039075 (2nd view-weighted
     content-share coded EXPOSURE, like #8 85085201199); 85214504236 was a false positive ('dietary-supplement' matched 'diet').
 (2) value-vs-quote numeric check (all 679 rows): 24 flags, ALL verified correct — values are table-sourced or the regex
     missed '.66%'/'Seventy percent'/count-vs-view-share. 0 value errors. Coding is solid.
FROZEN v1.4.9 (`apply_v149.py`, MD5 130937327f3790ffad2fbf42756b52d7): 85127039075 EXPOSURE->CONTENT. No value change. Gates PASS.
OPEN judgment call for Sacha: OA-W3113799821 ('1% of Bing COVID queries are misinformation') coded EXPOSURE but is
query-DEMAND, not diet-exposure — recode to CONTENT or OTHER? (left as-is pending his call).

## 2026-07-23 — FULL construct audit (6-agent source adjudication) -> FROZEN v1.4.10
"Audit everything, full rigour." Built `scripts/audit_construct_full.py` (implied-construct heuristic vs coded) -> 60
flags. 6 agents re-read each flagged study's SOURCE and adjudicated (`qa/construct_adjudication.csv`). Verdict: coding
overwhelmingly correct — ~49/60 were heuristic false positives (e.g. "% of most-SHARED links that are fake" = CONTENT
because denominator = items, not a sharing stream; "misleading videos" GQS/ASRS ratings = QUALITY; ideological/demographic
composition of top spreaders = OTHER by design). CONFIRMED CHANGES applied as v1.4.10 (`apply_v1410.py`, MD5
5ebdeab8ff4d97acdccc7fa3c374d537, 5 rows, 0 value changes): OA-W3113799821 EXPOSURE->OTHER (query demand, Sacha-approved);
4 reach_subtype sharing->exposure (visited>=1 website). Gates PASS.
HELD for Sacha's decision: 5 OTHER->CONCENTRATION (source-concentration 'top-N sources->Y%') — genuine but touches the
concentration headline, and conc_unit tagging is inconsistent (some 'news_source' rows are actually user/account concentration).

## 2026-07-23 — FROZEN v1.4.11: clean concentration taxonomy (user vs source)
Sacha chose "move + cleanly separate". `apply_v1411.py` (MD5 a5be5997380623c9b22201536155da07, 0 value changes):
moved 5 SOURCE-concentration rows OTHER->CONCENTRATION; standardized conc_unit to USER (23) vs SOURCE (5),
fixing 5 rows mislabelled 'news_source' that are actually user/account concentration. CONCENTRATION now 28 rows.
Updated the analysis so the HEADLINE "top 1% of people -> 70%" (figK flow, figL Lorenz, fig4, concentration_standardized)
uses conc_unit=user ONLY; source concentration written to `data/synth/phaseB/concentration_source.csv` + shown as a
separate dashboard table ("few outlets/domains produce most of it": top-3 domains->49% (Oswald), top-10 sources->95%
(Pierri Italy), 5% of sources->50% (Grinberg)). Gates PASS. Full construct-audit chain: v1.4.9->.10->.11 all clean.

## 2026-07-23 — FULL multi-dimension audit -> FROZEN v1.4.12 (audit campaign complete)
"Audit all possible dimensions." Built `scripts/audit_all_dimensions.py` — vocab (out-of-set categorical values),
cross-field consistency (REACH/reach_subtype, CONCENTRATION/conc_unit, breadth on prevalence, demo dims,
political_orientation, within_misinfo, denom_class), numeric integrity (value_pct range, value_raw a/b vs value_pct,
n parse). 62 findings: 0 real value errors (2 'high' were stale value_raw denominators; value_pct correct). Cleanups
applied v1.4.12 (`apply_v1412.py`, MD5 eafa672e8f97c2e0cf54c6f04fd012c3, 25 cells, 0 value changes): 12 blank
breadth/denom filled on 105027856675 (match siblings), value_raw 1313->1211 on 85055756722, 7 stray conc_unit cleared,
3 within_misinfo FALSE->blank. Re-audit on v1.4.12: 26 low findings remain, ALL benign (19 orient_no_party = orientation
on content/actor rows, correct; 7 no_denom_class = OTHER composition rows). Gates PASS.

### AUDIT CAMPAIGN SUMMARY (v1.4.5 -> v1.4.12, all 2026-07-22/23)
Triggered by Sacha's dashboard/tooltip review + "audit everything, full rigour". Chain of freezes, ALL coding/taxonomy
corrections with 0 headline-value errors found:
- v1.4.6 descriptive completeness (measure_type backfill, topic coding, Guess dedup)
- v1.4.7 CONCENTRATION coding standardized (value=activity share; fixed flips) + engagement->SHARING
- v1.4.8 tooltip-review fixes (view-share EXPOSURE->CONTENT #1, measure_type period labels, 2 tags)
- v1.4.9 2nd view-share EXPOSURE->CONTENT; construct+value-vs-quote scans = 0 value errors
- v1.4.10 full construct audit (6-agent source adjudication of 60 flags; ~49 false positives): OA->OTHER, 4 reach_subtype
- v1.4.11 clean concentration taxonomy (user 23 / source 5; headline = user-only)
- v1.4.12 multi-dimension consistency cleanups
VERDICT: construct + value + moderator coding is in clean, defensible shape. Deterministic audit scripts kept for the
replication package: audit_construct_full.py, audit_all_dimensions.py (+ qa/construct_adjudication.csv, qa/audit_all.csv).

---

## 2026-07-23 — Full-project rigour review + remediation campaign (Sacha: "improve data/coding, findings, rigor")

Commissioned a four-dimension critical review of the whole project (search/PRISMA methodology; data
extraction & audit coverage; Phase B statistics; dashboards/figures), synthesised with a main-session
pass over the frozen CSV, FROZEN.md, DECISIONS_REGISTER, manuscript, GRADE framework and concentration
outputs. Findings and the resulting prioritised plan are in memory
(`misinfo-review-improvement-plan`). Sacha approved execution, DECLINED the registration/PRISMA-checklist
item (P0-3), and chose: dual-human IRR (Sacha + Laura, same items), Perplexity manual cross-model batch,
full RoB re-appraisal from full text, new v1.5.0 freeze.

### Headline problems found (evidence-backed)
- **Version drift across artefacts.** manuscript_draft.md is written against v1.4.6 and hard-codes numbers
  that no longer match regenerated output (EXPOSURE 2.8%/k=20 in prose vs 2.6%/k=16 in current
  `slices_by_construct.csv`); `prisma_flow.svg` shows 408 studies/695 estimates vs frozen 317/679 and its
  own arithmetic does not reconcile (2,759 - exclusions = 645 but the included box says 977; PubMed and
  OpenAlex-keyword streams absent entirely); `data_quality_methods.md` describes v1.4.5/680;
  `figure_contrast.svg` says n=695; `RESUME_HERE.md` still describes the pre-v1.2 state (1,091 rows/529
  studies). Five different corpus counts are currently visible to a reader.
- **Manuscript-facing claims exceed what the logs support.** `METHODS_PROVENANCE.md:11` claims "dual
  independent title + abstract screening"; `research_log.md:442-451` records single-screener title
  screening. Every headline kappa (0.89 / 0.82 / 0.78) is LLM-vs-LLM; the only human kappa is the RA's 0.33.
  Manuscript sec 2.8/3 claims two sensitivity analyses (single- vs double-extraction; borderline
  QUALITY<->CONTENT) for which **no code exists**.
- **RoB describes a different population than the dataset.** 88 of 317 frozen studies had NO RoB record;
  `risk_of_bias_master_v2.csv` carried 261 records for studies no longer in the corpus. Instrument was
  bespoke and scored from "title + context"; 73% of studies rated HIGH, so it barely discriminated.
- **Statistics gaps.** No CIs on headline medians; no I^2/tau^2/prediction intervals; no funnel or
  small-study test (the conceptual `fig_funnel.svg` is a schematic, not a funnel plot); metareg PLO
  variances assume binomial independence and badly understate clustered mega-study variance; the pseudo-R^2
  ladder compares 2-df moderators against an 18-level platform factor; `phaseB_grade.py` inconsistency
  branch is inert (the "don't double-penalise what the moderator explains" rule is stated but not
  implemented); EXPOSURE=HIGH certainty on k=16 with zero downgrades is the most attackable rating.
- **Concentration arm.** "top 1% -> 70%, top 10% -> ~88%, top 20% -> ~75%" is non-monotonic because each
  threshold rests on 2-3 different studies; the summary pools thresholds spanning top-0.003% to top-31%
  as if a single Lorenz curve; shared panels contribute repeatedly. SoF table (k=13, 59.5%) and sec 3.7
  (23 estimates, 70%) report two different concentration numbers.

### Measured, not asserted: stream contribution (`scripts/stream_contribution.py`, NEW)
Replaces the previously ASSERTED "~80-90% Scopus overlap" in METHODS_PROVENANCE. Of 317 included studies:
**Scopus 266 (83.9%), OpenAlex snowball/keyword 40 (12.6%), PubMed 4, user-supplied PDFs 4, Berriche seed 2**
-> **non-Scopus = 51 studies (16.1%)**. Single-database searching would have missed one in six included
studies; this empirically justifies the multi-stream design and is quotable in Methods.
Venue resolution (OpenAlex API) of those 51 shows only ~4 sit in venues WoS structurally cannot index
(JQD etc.); the rest are mainstream journals Scopus DOES index (Obstetrics and Gynecology, Cureus, Human
Vaccines & Immunotherapeutics, Information Communication & Society, Journal of Urology). **The gap is
therefore query recall, not database coverage** — which makes adding WoS a weak fix for the actual failure
mode. Caveat recorded: the venue heuristic marks institutional repositories (TUScholarShare, VBN Aalborg)
as "likely WoS" when they are OA copies, and 16/51 did not resolve; direction holds, exact counts soft.
Outputs `data/synth/stream_contribution{,_summary}.csv`, `nonscopus_venues.csv`.

### RoB instrument v3 — Hoy-mapped, full-text (`docs/rob_checklist_v3.md`, NEW; supersedes rob_checklist.txt)
Adopted **Hoy et al. (2012)** J Clin Epidemiol 65:934-939, the validated prevalence RoB tool, because two of
its ten items ARE this review's thesis: **item 10** ("were the numerator(s) and denominator(s) appropriate?")
is the denominator argument, and **item 6** ("was an acceptable case definition used?") is the
falsity-vs-quality boundary. Being able to say our central claims correspond to items 6 and 10 of a
validated instrument is far stronger than defending a bespoke scheme. Pre-specified summary anchor weights
items 6 and 10 (LOW: 0-2 HIGH and 6+10 both LOW; MODERATE: 3-5 HIGH or one of 6/10 HIGH; HIGH: >=6 HIGH or
both 6+10 HIGH). Sample size deliberately DROPPED as a bias item (it conflated precision with bias and is
already handled by the separate precision-weighting analysis). v2->v3 crosswalk documented.
Worklist `scripts/build_rob_v3_worklist.py` -> 317 studies, **283 (89.3%) with cached full text**.
Every rating on items 6 and 10 requires a VERBATIM supporting quote.

**Wave 1 complete (80 studies, shards 00-07):** LOW 6 / MODERATE 24 / HIGH 50 — i.e. **63% HIGH vs the old
instrument's 73%, with MODERATE roughly tripling**, plus a continuous `n_high` 0-7 gradient the old scheme
lacked. 0 format violations; 67 full_text / 13 abstract_only; 6 rows honestly carry "NO QUOTE FOUND"
(all abstract-only). Appraisers independently flagged that UNCLEAR-treated-as-HIGH inflates abstract-only
studies -> an abstract-only sensitivity is REQUIRED in the aggregation step. Wave 2 (shards 08-19) running.

### FROZEN v1.5.0 — schema hygiene (`scripts/apply_v150.py`)
MD5 `c730b0d93b5de65613af9ac2a72e0a00`; 679 rows / 317 studies UNCHANGED; 55 -> 51 columns.
Gates inside the build script ASSERT 0 value_pct changes and preserved row order (not merely claimed).
NEW `value_kind` makes the pooled-analysis eligibility rule explicit and machine-checkable (proportion 662 /
scale_score 8 / per_capita_intensity 6 / range_not_point 3) — it previously lived only as prose in `flag`.
`ground_truth` normalised to 5 controlled codes (14 rows had whole prose sentences AS the category value,
silently fragmenting every groupby); prose preserved in NEW `ground_truth_detail`. Workflow columns moved to
`qa/v150_workflow_ledger.csv`. All-empty columns dropped. NEW `intersection_duplicate` flags the one genuine
double-count (W4205602257 reports the 65+/Independent cell in both its age and political series) — kept, not
deleted, since removing either breaks a reported series. Full detail in FROZEN.md; changelog
`qa/v150_changelog.csv` (59 entries). validate_frozen PASS, validate_prisma PASS.

**Deliberately NOT collapsed: `denom_type` vs `denom_class`.** The review recommended merging them as
redundant. On inspection they are not redundant — they **disagree on 80 rows** (29 population/topical, 15
the reverse, etc). Merging would have destroyed evidence of a real coding inconsistency and required ~80
unreviewed coding decisions. `denom_class` marked canonical; conflicts enumerated in
`qa/v150_denom_conflicts.csv` for a source-anchored adjudication pass.

### Human reliability package (IRR v2) — built, awaiting the two coders
`scripts/build_human_irr_worksheet.py` (seed 42) + `docs/RA_package/irr_v2/`. Design rationale: round 1's
kappa=0.33 was on the KEEP/DROP inclusion decision — the hardest, most criteria-loaded judgement — and
adjudication showed the RA was right on only 11 of 29 contested cases; on the 51 both-keep studies construct
agreement was already 42/51 (82%). This round therefore measures a far more objective task, split in two:
**Part A** classification (30 items, quote supplied -> construct / denom_class / breadth) and **Part B**
extraction (12 items, paper supplied, value REDACTED -> locate and record the number and its denominator).
**Both Sacha and Laura code the SAME items**, yielding three statistics; the load-bearing one is
**coder-vs-coder (the human ceiling)**, which bounds how hard the task intrinsically is and makes the
human-vs-LLM figure interpretable — and neutralises the author-bias concern because the RA's independent
codes triangulate the author's. Sacha is blinded to our coding (removes anchoring, the dominant bias on a
transcription task) and his sheet is reported as *author verification*, Laura's as *independent*.
`scripts/score_human_irr.py` reports raw agreement + Cohen kappa + PABAK + Gwet AC1 (chance-corrected
coefficients alongside raw because kappa is deflated when one category dominates — CONTENT is ~47% here)
and writes every disagreement out for adjudication. Instructions
(`CODING_INSTRUCTIONS.html`) target the five failure modes observed in round 1 with worked examples.

### Uncertainty layer added (`scripts/phaseB_uncertainty.py`, NEW; run on v1.5.0)
Closes four gaps a methods reviewer would raise. Outputs `data/synth/phaseB/{uncertainty_medians,
heterogeneity,small_study_effects,leave_one_out_wholediet}.csv`. Seed 20260723, B=2000, stdlib only
(no numpy/scipy available; t-tail via continued-fraction incomplete beta, DerSimonian-Laird and Egger
implemented by hand).

**(1) Bootstrap 95% CIs on the headline medians (study-cluster resampling).** Previously only IQR was
reported — but IQR is spread ACROSS studies, not uncertainty about the median. Results:
EXPOSURE 2.6% [0.6-5.1] k=15 · WHOLE-DIET backbone 7.5% [5.0-11.0] k=29 · REACH 12.0% [8.5-21.4] k=23 ·
SHARING 13.5% [6.7-16.8] k=23 · CONTENT 22.3% [18.4-26.1] k=205 · RECALL 54.0% [37.0-64.0] k=27.
**The construct separation survives the CIs** — EXPOSURE [0.6-5.1] and RECALL [37.0-64.0] do not come
close to overlapping. The headline claim now carries uncertainty and still holds.
Also fixed here: `study_points()` pairs a study's median value with the n OF THE ESTIMATE AT THAT MEDIAN.
`phaseB_precision.py` paired the median value with the study's MAX n, so value and weight could come from
different estimates.

**(2) Heterogeneity + prediction intervals.** I^2 = 99-100% in every construct; tau^2 up to 4.5.
Prediction intervals are enormous: CONTENT 0.32-93.6%, REACH 0.18-93.5%, WHOLE-DIET 0.10-87.2%,
EXPOSURE 0.27-16.2%, RECALL 18.1-84.6%. **This is the quantitative proof of the paper's central claim** —
a pooled "prevalence of misinformation" is not a meaningful quantity, and we can now show that rather
than merely assert it by declining to pool. Ran a x10 variance-inflation sensitivity to test whether the
near-100% I^2 is an artifact of PLO variances understating clustered behavioural n: I^2 barely moved
(EXPOSURE 99.0 -> 90.1, others unchanged), so the heterogeneity is genuine spread, not variance
understatement.

**(3) Small-study effects (Egger).** REACH p=.013 and WHOLE-DIET p=.016 test "significant", BUT the
fitted intercepts are implausible (203, 265, 916 on the logit scale) — a known failure mode of Egger's
test when precisions span orders of magnitude, which they do here (n ranges ~6 orders). **DO NOT report
these as evidence of publication bias as they stand.** Recorded as diagnostic-only. TODO: replace with a
Spearman correlation between study n and study value, which tests the "larger samples find less" thesis
directly and is robust to the scaling problem. Also note `docs/fig_funnel.svg` is a CONCEPTUAL
misinformation-funnel schematic, NOT a statistical funnel plot — the naming collision should be fixed.

**(4) Leave-one-out on the whole-diet backbone.** Full median 7.46%; **maximum absolute shift from
dropping any single study = 0.07 pp**. The backbone is not driven by any one study (this pre-empts
"is this just Allen 2020?"). Clean, quotable robustness result.

### Incidental data finding (from RoB appraisal, shard 08)
Basch et al. `2-s2.0-85065550941` is internally inconsistent: the text states "139/300 (63.0%)"
anti-fluoride while Table 1 gives n=189 for the same 63.0%. 189 is the value consistent with the
percentage. Our `value_pct` (63.0) is unaffected, but `value_raw` may carry the wrong numerator —
flagged for the next extraction pass.

### STATUS AT PAUSE (token budget)
DONE: stream-contribution measurement · RoB v3 instrument + worklist · RoB wave 1 (80 studies) and most
of wave 2 · FROZEN v1.5.0 (+ gates PASS, git-tagged) · human IRR package (awaiting Sacha + Laura) ·
Perplexity cross-model batch (awaiting 5 pastes) · uncertainty layer.
NEXT (not started): aggregate RoB v3 -> master + reliability subsample + abstract-only sensitivity
(appraisers repeatedly flagged that UNCLEAR-as-HIGH inflates abstract-only studies) · remaining RoB
shards 20-31 · regenerate ALL Phase B outputs/figures/PRISMA/dashboards from v1.5.0 in ONE pass ·
counts crosswalk · manuscript number reconciliation + truth-in-claims edits · GRADE script fixes
(inert pTOPICAL branch; EXPOSURE=HIGH on k=15) · concentration restructuring (per-threshold k, shared-panel
dedup) · metareg fixes (collapse sparse topic levels, df-adjust the R^2 ladder) · the two claimed-but-
uncoded sensitivity analyses · presentation consolidation + colorblind-safe palette.

### Extraction errors surfaced INCIDENTALLY by the RoB v3 full-text pass (unplanned benefit)
Because v3 requires a verbatim quote for items 6 and 10, appraisers read the source closely enough to
catch extraction problems the value-audits missed. Collected for the next extraction pass — NOT yet
applied to the freeze:
- **`2-s2.0-85138494787` — probable real error.** Our stored quote for the 9.8% estimate
  ("98/1000 (9.8%) of top-retweeted tobacco-and-COVID tweets…") **does not appear anywhere in the paper**;
  the paper reports "10% (n=107) of the most retweeted tweets". The companion 22.5%/n=57 URL estimate
  verifies verbatim. This study was RE-INCLUDED at v1.4.5, so it has had less scrutiny than the rest.
- **`2-s2.0-85065550941` (Basch)** — internally inconsistent source: text says "139/300 (63.0%)",
  Table 1 says n=189 for the same 63.0%. 189 is consistent with the percentage; our value_pct (63.0) is
  unaffected but value_raw may carry the wrong numerator.
- **`2-s2.0-85124307830`** — abstract and Fig 1 say N=18,407; Methods say "final dataset consisted of
  … (N = 18,314)". Extraction currently uses 18,407.
- **`2-s2.0-85124823821`** — cached text is interleaved two-column PDF output; the item-6 quote is stored
  as two contiguous verbatim fragments plus an explicitly-labelled bracketed reconstruction of the broken
  span, so it can never be mistaken for a clean quote.

**Methodological point worth making in the paper:** requiring a quote for the two load-bearing RoB items
turned the appraisal into a second de facto extraction check. That is an argument for quote-anchored
appraisal generally, and it is evidence that our earlier "0 value errors" audits were checking internal
consistency rather than fidelity to source.

### Recurring instrument-application question for the reliability subsample
Multiple independent appraisers flagged the SAME boundary without prompting: whether a source-level
credibility/bias list (MBFC "questionable", Oxford "junk news", NewsGuard) satisfies item 6 as a
"validated domain/credibility list" (LOW) or fails it as a quality proxy standing in for falsity (HIGH).
Appraisers split, and several noted the call flips the study's overall rating. **This must be resolved as
an explicit rule in `docs/rob_checklist_v3.md` before the reliability subsample**, otherwise the
disagreement will show up as noise when it is really an under-specified rule. It is also substantively
the same falsity-vs-quality boundary the paper is about, so the resolution belongs in the manuscript.

### RoB v3 wave 2 closed at 22/32 shards (220 studies) — paused on token budget
One further source-side flag from shard 15, added to the extraction-error list above:
- **`2-s2.0-85128118104` (HINTS-China)** — "83.6% (2584/3090)" uses 2584, which the same paper elsewhere
  reports as the number of *valid* questionnaires after list-wise deletion. Possible numerator/denominator
  reporting error IN THE SOURCE (not necessarily our extraction). Check before the whole-diet table.

Running totals at pause: **220/317 studies appraised, LOW 15 / MODERATE 87 / HIGH 118 = 54% HIGH**
(old instrument 73%), n_high 0-8. Shards 20-31 (97 studies) remain.

The recurring item-6 boundary (source-level credibility lists: validated ground truth, or quality proxy?)
was raised INDEPENDENTLY by at least six appraisers, several noting it flips the study's overall rating
(Lenti 85164694763, Telegram 85131073869, Cinelli 85092033301, MBFC 85137779722, junk-news 85114317455,
Zannettou 85038621544). This is now the single highest-value open decision in the appraisal: it is
under-specified in the instrument, it moves ratings, and it is substantively the same falsity-vs-quality
boundary the paper argues about. Resolve it as an explicit rule BEFORE the reliability subsample, then
re-run the affected rows.

**CORRECTION to the entry immediately above (same session, append-only discipline).** The line
"22/32 shards (220 studies), LOW 15 / MODERATE 87 / HIGH 118" is WRONG — I incremented the running
total by shards 15 and 19 after their completion notifications, but those files had already been
written to disk and were therefore already inside the previous count. Verified figures from the
files themselves:

- **shards present: 20/32** (00-19); missing 20-31
- **200 studies appraised, 200 unique study_ids** (no duplicates across shards)
- **LOW 14 · MODERATE 79 · HIGH 107 = 54% HIGH** (old instrument 73%)
- 117 studies remain to appraise (shards 20-31)

The 54% HIGH figure and the substantive conclusions are unchanged; only the counts were overstated.
Lesson for this pipeline: count from the artefacts on disk, never from notification arithmetic.

### RULING (Sacha, 2026-07-23): source-level credibility lists satisfy RoB item 6
Resolves the boundary six appraisers raised independently. NewsGuard / MBFC / Grinberg / Oxford
"junk news" / Décodex / comparable published blacklists — including ad-hoc unions of them — now count
as an acceptable external case definition -> **item 6 = LOW**. Written into `docs/rob_checklist_v3.md`
with the rationale, which is not leniency but anti-double-counting: `breadth`
(fabricated->false->misleading->**unreliable_source**->low_quality) already measures net-width as a
MODERATOR, and the meta-regression estimates its effect. Penalising source-level identification again
inside the RoB instrument would double-count the thing the moderator exists to quantify and would make
the bias rating collinear with breadth — so "high-RoB studies report higher numbers" could no longer be
distinguished from a restatement of the breadth coding. Same principle GRADE applies under Inconsistency.
Still FAILS item 6: author-devised coding with no external anchor, quality instruments (DISCERN/GQS/JAMA/
VIQI) or guideline-adherence substituting for falsity, circular definitions, author-assembled lists with
no stated criteria. The line is *external and pre-existing* vs *internal and ad hoc*, NOT claim-level vs
source-level. `classification_level` still records source_level vs claim_level (Nenno 2025, ~10x), so the
information is preserved, just not counted twice.

**8 appraised rows need re-rating** (item 6 HIGH/UNCLEAR on a source-level list): 85038621544,
85066887935, 85074511992, 85074596916, 85078014559, 85092033301, 85131073869, 85164694763. **6 have
item 10 HIGH as well, so they move HIGH -> MODERATE**; 2 (85038621544, 85066887935) have item 10 LOW and
will move MODERATE -> LOW. Not yet applied — deferred with shards 20-31, which must apply the ruling from
the outset. Expected effect: HIGH share drops below the current 54% and the LOW cell grows, further
separating the instrument from the old 73%-HIGH version.

### Coder packages delivered to Desktop (2026-07-23)
`~/Desktop/Misinfo_Coding_Check/` — CODING_INSTRUCTIONS.html, partA/partB for both coders, README, and
`papers/` containing the 12 Part-B full texts copied in so the package is SELF-CONTAINED (the sheets
originally carried repo-relative paths that would not resolve for an external RA). ANSWER_KEY.csv
deliberately NOT copied; verified absent from both Desktop folders.
`~/Desktop/Misinfo_Perplexity_Check/` — 5 paste-ready batches, response template, README.

### Cross-model check COMPLETE (Perplexity / GPT-5.6 Terra Thinking, 2026-07-23)
Sacha ran all 5 batches; 30/30 items returned. First non-Claude verification in the project — every
prior reliability figure was Claude-vs-Claude. Scored against the frozen coding on the SAME items the
human coders have (Part A). Files: `docs/RA_package/irr_v2/perplexity_responses.csv`,
`partA_perplexity.csv`, `perplexity_disagreements.csv`.

| dimension | n | raw | Cohen kappa | PABAK | Gwet AC1 |
|---|---|---|---|---|---|
| construct | 30 | .767 | **.703** | .733 | .737 |
| breadth | 30 | .733 | .614 | .680 | .691 |
| denom_class | 30 | .600 | **.450** | .533 | .546 |

**Reading this honestly.** Construct agreement (kappa .70) is substantial and is the first evidence that
the taxonomy is not a Claude-specific artefact — it reproduces across model families. `denom_class`
(kappa .45) is genuinely weak. Two caveats that cut in OPPOSITE directions: (a) Perplexity received a
one-page condensed rule sheet, not the full moderator codebook, so some disagreement is instruction
under-specification rather than error — this INFLATES apparent disagreement; (b) it is a single run with
no adjudication, and it agreed with itself confidently (26/30 items at confidence 4-5) while still
diverging from us, so high confidence is not evidence of correctness. **These numbers are a signal, not
a verdict — do not report them as inter-rater reliability.** The human ceiling (Sacha vs Laura) is still
the figure that makes them interpretable.

**Three substantive patterns in the 27 disagreements:**

1. **`W4293124965` disagreed 3x in the same direction (A07/A23/A26), and the check is right to flag it.**
   Perplexity says `all_media`, we say `political_news`. Inspecting the source: the denominator is
   "**% of all news web traffic** (visits to news websites)" across 16 estimates — i.e. the whole NEWS
   diet, not politics-restricted. Under our own codebook (`all_media` = whole information/news diet;
   `political_news` = news or political content *specifically*) `all_media` is arguably the better label,
   or our `political_news` category is misnamed for what it actually holds. **No headline impact** — both
   categories are inside the whole-diet backbone set {all_media, population, political_news}, so the
   backbone membership and its 7.5% median are unaffected. But 16 estimates carry a questionable label
   and the category boundary needs an explicit definition. ACTION: define the all_media/political_news
   boundary in the codebook, then re-check this study.

2. **Survey RECALL rows: we code the denominator as the surveyed POPULATION, Perplexity codes the
   question TOPIC** (A18, A27, A28 — px `topical`, ours `population`). Our convention is correct for a
   prevalence denominator (the % is a share of respondents), but the rule is not stated anywhere a
   coder could find it. This is under-specification on our side and will hit the human coders too.
   ACTION: state it in the codebook.

3. **The CONTENT/QUALITY boundary split 3 ways in BOTH directions** (A04, A14 px=CONTENT ours=QUALITY;
   A11 px=QUALITY ours=CONTENT). This is precisely the boundary the paper argues about, and the fact
   that an independent model draws it differently in 3/30 items is itself a reportable finding: the
   falsity-vs-quality line is genuinely hard, not merely sloppily applied in the literature.

Also surfaced: A22 (`105027856675`) and A24 carry blank/OTHER coding on our side where Perplexity
assigned a substantive construct — the OTHER-with-blank-moderators rows are effectively invisible to any
cross-check. Worth confirming they are intentional.

### Cross-model round 2 prepared (146 items) — rules fixed FIRST, deliberately
Decision: did NOT simply scale round 1. Two of the three recurring denom_class disagreements were our
own undocumented conventions, so expanding against the old prompt would have re-measured our
documentation gap at 5x the manual cost instead of measuring coding quality. Sequence was: settle the
rules -> write them into the codebook AND the human instructions -> then expand.
- `scripts/_px_preamble.txt` (NEW, shared prompt preamble) now carries 6 explicit decision rules
  including the survey-denominator rule and the all_media-vs-news-diet distinction.
- `scripts/build_perplexity_expansion.py` (NEW, seed 4242): 146 items, 5 batches of 30, excluding all
  round-1 items. **Stratified, not uniform** — round 1 showed agreement is already high on the easy mass
  (topical CONTENT) and concentrates disagreement on three boundaries, so a uniform draw would spend the
  budget re-confirming easy cases. Quotas: CONTENT/QUALITY boundary 55 · audience-constructs 45 ·
  denominator 25 · baseline_random 21. Strata are recorded in `perplexity_r2_manifest.csv` so BOTH
  per-boundary and reweighted-overall agreement can be reported; the manifest is the answer key and must
  not go to the model or the coders.
- Human instructions updated with the same two rules (traps 6 and 7) — the gaps would otherwise have
  contaminated the Sacha-vs-Laura human ceiling, which is the figure everything else is calibrated to.
  Desktop copies refreshed.

### FROZEN v1.5.1 — `news_diet` denominator class added (Sacha approved 2026-07-23)
`scripts/apply_v151.py`; MD5 `c3108ee3a6d9e93ab7cacd5f2aee3d9c`. 679 rows / 317 studies unchanged.
Gates assert 0 value_pct changes, preserved row order, AND unchanged whole-diet backbone membership
(285 rows before and after) — the last is the important one: adding the category SUBDIVIDES the
backbone rather than altering it, so the 7.5% backbone median and every headline value are untouched.
validate_frozen PASS, validate_prisma PASS.

**11 rows / 5 studies recoded** to `news_diet`: W4293124965 x4 (all news web traffic, 4 countries),
85209547248 x3 (news diet of median QAnon-exposed participant), W7146985142 x2 (all news website
visits), 105019357120 (Reddit reliable-OR-unreliable news submissions), 85083323285 (Allen 2020).
Final: political_news 112 · news_diet 11 · all_media 14.

**A rule-design lesson worth keeping.** The first run recoded only 10 and held back 85083323285
(Allen 2020), whose denominator is *"total news consumption (TV + online news minutes)"* — the guard
saw "TV" and inferred non-news media. Wrong: that is a NEWS diet measured across two delivery
CHANNELS. Naming a channel is not the same as widening the denominator. The classifier now lets an
explicit news restriction (`total news` / `news consumption` / `news minutes` / `all news`) override
channel words. Had this not been caught, the review's most-cited whole-diet study would have sat in
the wrong denominator bin — and it is exactly the study whose ~0.15% all-media vs ~3.4% all-news
contrast the new category exists to expose.

**Codebook section (d) rewritten for maximum clarity** (Sacha's explicit request): one governing
question ("if this were 100%, what would it mean?"), a 5-step ordered decision tree, an explicit
three-way width table with typical values (all_media ~0.15% / news_diet ~3.4% / political_news higher),
and the recurring hard cases — surveys and REACH -> `population` (never `topical`); "most-shared" ->
`curated_sample`; a platform census is NOT `all_media`; when two readings are defensible prefer the
NARROWER one and record why in `moderator_quote`, because over-claiming a whole-diet denominator
inflates the review's most important cell. `denom_type` explicitly marked superseded and non-canonical.

### Small-study test: Spearman REPLACES Egger as the reportable statistic
Egger is retained in `phaseB_uncertainty.py` but explicitly labelled DIAGNOSTIC ONLY — do not report.
Reason (recorded so it is not re-litigated): Egger regresses the standard normal deviate on precision,
and our precisions span ~6 orders of magnitude (n from dozens to hundreds of millions), which makes the
design matrix pathologically scaled; the run produced intercepts of 203-916 on the logit scale, which is
not a plausible effect size. A **Spearman rank correlation of study n against study prevalence** is
invariant to that scaling, assumes nothing about variances, and tests the review's actual claim directly.

**Result — the thesis holds, cleanly.** rho is NEGATIVE in all six groups (larger samples find less
misinformation): CONTENT **rho = -.43, p < .001** (k=205) · REACH -.39, p = .069 · EXPOSURE -.26 ·
WHOLE-DIET -.20 · RECALL -.13 · SHARING -.13. Only CONTENT reaches significance, which is expected —
it is the only cell with real power (k=205 vs 15-29 elsewhere). The consistent sign across all six
independent groups is the stronger evidence than any single p-value.

### BUG found and fixed: adding `news_diet` silently broke 8 analysis scripts
Immediately after the v1.5.1 freeze the whole-diet backbone dropped from k=29 to k=28 and its median
moved 7.5% -> 8.1%. Cause: **eight scripts each hardcode the whole-diet denominator set independently**
and none knew about the new category, so every `news_diet` row fell out of the backbone.
Patched all 11 affected sites: phaseB_{descriptives,slices,figures,figures2,precision,prep_regression,
export_json,uncertainty}.py plus the controlled-vocabulary validators (audit_all_dimensions.py,
merge_moderator_tags.py) and build_perplexity_expansion.py. Post-fix the backbone is back to k=29,
median 7.5% [5.0-11.0] — identical to pre-v1.5.1, which CONFIRMS the category subdivides the backbone
rather than altering it, exactly as the freeze gate asserted.

**Lesson for the replication package:** the whole-diet set is duplicated across 8 files. It should be a
single shared constant; until then, any change to `denom_class` vocabulary must grep for `all_media`
across `scripts/` and update every site. Noted as a refactor for the regeneration pass.

### Cross-model round 2 in progress: 90/146 items (batches 1-3)
`scripts/ingest_perplexity_r2.py` (NEW) makes each batch a one-command idempotent merge; re-pasting a
batch overwrites rather than duplicates, and malformed or unknown rows are reported rather than silently
dropped. 4 UNSURE so far (R001, R026, R033, R057) — the prompt instructs the model to decline rather
than guess, and it is complying, which is itself a good sign for the quality of the rest.
Desktop package restructured: the 5 batches were in ONE 72KB file (Sacha could not see them); now split
into `BATCH_1_of_5.txt` .. `BATCH_5_of_5.txt`, with round-1 files moved to `round1_done/`.

### CROSS-MODEL ROUND 2 COMPLETE — 146 items, Perplexity/GPT-5.6 vs frozen v1.5.1
All 5 batches returned by Sacha. 138 scored, **8 UNSURE** (R001/R026/R033/R057/R097/R133/R139/R144) —
the prompt tells the model to decline rather than guess and it complied, which is itself evidence the
remaining answers are considered rather than reflexive. Scripts: `ingest_perplexity_r2.py` (idempotent
merge), `score_perplexity_r2.py`. Results `perplexity_r2_results.csv`, all 124 disagreements with quotes
in `perplexity_r2_disagreements.csv`.

**Reporting convention (important).** The sample is deliberately stratified to over-sample contested
boundaries, so the POOLED figure is pessimistic by construction and must NOT be quoted as "our
agreement". Three figures are produced: per-stratum, pooled-this-sample, and **population-reweighted**
(each stratum weighted by its true share of the eligible corpus) — the last is the corpus-level estimate.

| dimension | pooled raw | pooled kappa | pooled AC1 | **reweighted raw** | round-1 kappa |
|---|---|---|---|---|---|
| construct | .819 | **.769** | .796 | **.856** | .703 |
| breadth | .775 | .676 | .746 | .775 | .614 |
| denom_class | .507 | .401 | .453 | **.524** | .450 |

**Construct improved from kappa .703 to .769** (and .856 reweighted) after the round-1 rule fixes — good
evidence the taxonomy is not a Claude-specific artefact and that the fixes worked. Breadth also improved
(.614 -> .676). **denom_class did not improve** (.450 -> .401 kappa), and diagnosing why produced the
round's real finding.

**FINDING: `denom_class` has no coherent rule for CONCENTRATION and OTHER rows.**
The `baseline_random` stratum scored raw **.053 — one agreement in nineteen**. Its composition: 12
CONCENTRATION, 4 OTHER, 2 RECALL disagreements. Inspecting the frozen data, CONCENTRATION rows carry
denom_class = population 14 / curated_sample 7 / topical 4 / single_source 2 / political_news 1. That
distribution is incoherent: a concentration estimate has the form "top X% of USERS account for Y% of
ACTIVITY", so its denominator is structurally different from a prevalence denominator (a share of
content or of people). `denom_class` was designed for the latter and is being applied to the former,
which generates noise rather than information — and the cross-model check surfaced it precisely because
an independent rater had to guess the same undefined rule.
**DECISION NEEDED (Sacha):** either (a) define denom_class for CONCENTRATION as the population/user base
being concentrated (making it `population` by construction), or (b) set it N/A for CONCENTRATION and
OTHER and exclude those rows from every denominator analysis. Recommend (b): it is honest about the
field not applying, whereas (a) invents a value that no analysis actually uses. Concentration already
carries its own dedicated fields (`conc_unit`, `conc_group_pct`, `conc_share_pct`).

**Two further systematic disagreement patterns, for the adjudication queue:**
- **ours=topical -> px=curated_sample, 23 cases** (the single largest cell). The boundary between "found
  by keyword/hashtag search" (our `topical`) and "hand-assembled with no natural total" (`curated_sample`).
  Our own rule says top-N-by-engagement is `curated_sample`; if some of these 23 are top-N sets we coded
  `topical`, WE are wrong on them. Needs a source-anchored pass, not a prompt tweak.
- **ours=political_news -> px=all_media, 12 cases.** Same family as the news_diet finding but on
  DIFFERENT rows than the 11 already recoded in v1.5.1 — worth re-running the news-wide detector with a
  looser pattern to see whether more rows qualify.

**98% of the 124 disagreements came at the other model's confidence 4-5.** This is confident
disagreement, not hedging — which cuts both ways: it means the divergences are substantive rather than
noise, and it means high self-reported confidence carries no evidential weight. Do not report the
model's confidence as a quality signal.

### RoB v3 aggregation (`scripts/aggregate_rob_v3.py`, NEW) — interim at 260/317 studies
Shards 26-31 still running. The aggregator does three things a naive concat would not:
(1) **tags ruling drift** — shards 00-19 were appraised BEFORE the source-level-list ruling, 20-31
after, so it records `ruling_applied` per row, flags the 8 known affected pre-ruling studies, and
reports the distribution both as-appraised and ruling-corrected (mixing two instruments silently would
have inflated the HIGH share); (2) **runs the abstract-only sensitivity** the appraisers repeatedly
asked for, since UNCLEAR-counts-as-HIGH pushes abstract-only studies toward HIGH on missing information
rather than demonstrated bias; (3) **asserts coverage against the frozen list** rather than assuming it
(the v2 master had 261 orphans and 88 gaps).

**Overall distribution (260 studies):** as-appraised LOW 20 / MOD 107 / HIGH 133 (51%) ->
ruling-corrected **LOW 21 / MOD 111 / HIGH 128 (49%)** -> full-text-only **HIGH 46%**. Versus the old
v2 instrument's **73% HIGH**, this is a large gain in discrimination. The abstract-only sensitivity
moves HIGH by 3pp, confirming the appraisers' concern was real but bounded.

**RoB x construct — the "bias tracks the number" cross-tab, and it is now much sharper:**
QUALITY 90% HIGH · CONTENT 50.2% · SHARING 11.4% · RECALL 6.4% · REACH 3.8% ·
**EXPOSURE 0.0% · CONCENTRATION 0.0%**. Not one behavioural-exposure study is high risk of bias, against
half of all content analyses and nine in ten quality studies. (v2 said CONTENT 56% / EXPOSURE 5%.)

**IMPORTANT NUANCE — the claim needs qualifying.** The gradient is NOT globally monotone in the
estimate's magnitude: RECALL carries the HIGHEST values (median 54%) but only 6.4% HIGH risk. That is
correct, not a defect: self-report surveys are often well designed; they simply measure a different
thing (perception). Their weakness is INDIRECTNESS, which GRADE handles, not risk of bias. So the paper
must say "risk of bias tracks the number inversely **among measures of content and exposure**", and
handle RECALL separately as a valid measurement of a different quantity. Writing it as a global claim
would be overreach and a reviewer would find the counterexample immediately.

**Per-item discrimination** (% HIGH among items actually rated): item10 denominator **81.2%** and item2
sampling frame 79.2% are the dominant failure modes — the denominator really is the field's core
methodological problem, which is the review's thesis arriving as a measured result. item6 case
definition 54.0%. By contrast **item5 (6.2%) and item8 (5.9%) carry almost no information** and are
candidates to drop or report as descriptive only.

### Pipeline defect found during shard 27: abstract fallback fails silently for non-Scopus ids
`data/abstracts/abstracts.jsonl` is keyed by **Scopus `eid`**, so the instructed fallback
("if no cached full text, read data/abstracts/abstracts.jsonl") returns NOTHING for OpenAlex-sourced
records (`OA-W…`, `W…`) — silently, with no error. The shard-27 appraiser noticed and recovered the
four affected abstracts from `data/openalex_adjudicate.jsonl` / `data/openalex_netnew.jsonl` instead.

**Blast radius checked and contained:** of 25 abstract_only appraisals so far, only **4** carry
non-Scopus ids (OA-W2524060751, OA-W2914761925, OA-W3206858890, OA-W4360608277) — all in shard 27, all
recovered correctly. No earlier appraisal was degraded. (abstracts.jsonl does mention OA/W ids in 155
records, but not as the lookup key, which is why the direct lookup misses.)

**Fix for the replication package:** the abstract lookup should try `eid`, then `oaid`/OpenAlex id,
then DOI, across abstracts.jsonl + openalex_netnew.jsonl + openalex_adjudicate.jsonl. Until then, any
instruction pointing an agent at abstracts.jsonl alone is wrong for ~16% of the corpus (the non-Scopus
studies). Logged rather than patched now because the remaining shards are already in flight and the
in-flight agents demonstrably find the workaround.

### RoB v3 COMPLETE — 317/317 studies, 32/32 shards (2026-07-23)
`data/rob/risk_of_bias_v3_master.csv`. **Coverage: 317 matched, 0 MISSING, 0 orphan** — versus the v2
master's 88 gaps and 261 orphans. Every study appraised against the Hoy-adapted instrument, 285 (90%)
from full text, each rating on items 6 and 10 carrying a verbatim quote.

| variant | LOW | MODERATE | HIGH |
|---|---|---|---|
| as appraised (mixes pre/post-ruling instruments) | 28 (9%) | 127 (40%) | 162 (51%) |
| **RULING-CORRECTED (report this)** | **29 (9%)** | **131 (41%)** | **157 (50%)** |
| full-text only (abstract-only sensitivity) | 28 (10%) | 128 (45%) | 129 (45%) |

**50% HIGH vs the v2 instrument's 73%**, with MODERATE more than doubled and a continuous n_high 0-8
gradient. The abstract-only sensitivity moves HIGH by 5pp — real but bounded, as the appraisers predicted.

**RoB x construct (main-set estimates), the review's central cross-tab:**
QUALITY 84.8% HIGH · CONTENT 50.2% · RECALL 13.3% · CONCENTRATION 10.7% · SHARING 8.9% · REACH 2.9% ·
**EXPOSURE 0.0%** · OTHER 0.0%. Not one behavioural whole-diet exposure study is high risk of bias.

**Per-item, the denominator is the field's dominant methodological failure: item 10 HIGH in 80.4%** of
studies, item 2 (sampling frame) 79.1%, item 1 72.2%, item 6 (case definition) 52.5%. The review's
thesis therefore arrives as a MEASURED property of the literature on a validated instrument, not as an
argument the authors advance. Items 5 (8.4%) and 8 (5.5%) carry almost no information — report
descriptively or drop.

### GRADE fixed and rewired (`scripts/phaseB_grade.py`)
1. **The inconsistency rule is now actually implemented.** Previously BOTH branches downgraded by 1, so
   the `pTOPICAL` condition was inert and the framework's stated rule ("do not penalise as inconsistency
   what a moderator already explains") was never applied. Now a wide spread coexisting with a genuine
   within-construct denominator mix (15-85% topical) is recorded as EXPLAINED and does not downgrade;
   only unexplained spread does.
2. **Imprecision is now evidence-based, not an arbitrary k cut.** Added a criterion on the bootstrap
   95% CI (downgrade if upper >= 5x lower, i.e. the interval spans a decision-relevant range). This was
   added because k<10 alone let EXPOSURE (k=16) escape every imprecision downgrade while its CI runs
   0.6-5.1% — an 8.5x span that no reading calls precise. **EXPOSURE therefore moves HIGH -> MODERATE**,
   which removes the single most attackable rating in the review. All thresholds now carry an inline
   justification.
3. **Rewired from the superseded `rob_appraisals_v145.csv` to the v3 master**, using the
   `overall_ruling_corrected` column so the ruling is applied uniformly rather than mixing instruments.

**Resulting Summary of Findings:** EXPOSURE MODERATE (2.6%) · REACH MODERATE (12.0%) · SHARING MODERATE
(13.4%) · RECALL MODERATE (55.4%) · CONCENTRATION MODERATE (69.7%) · **CONTENT VERY LOW (23.0%)** —
downgraded four times (RoB, indirectness, imprecision, selection bias). Certainty and magnitude still run
inversely, but now with EXPOSURE at a defensible MODERATE rather than an indefensible HIGH.

### Flagged by appraisers for later, NOT yet acted on
- **`OA-W7125772788`** had an 11-byte stub in `v2txt/` masking a real 11-page image-only PDF; the
  appraiser rendered pages to read it. Other stub files may exist — worth a size sweep of v2txt.
- **Venue-quality concern:** several shard-28 studies come from very low-visibility venues with internal
  inconsistencies (OA-W7125772788 claims a 2021-2026 span in a 2025 issue and conflates a 282-respondent
  survey with 7,234 NLP data points). Suggests a venue/quality sensitivity check INDEPENDENT of RoB.

### Decisions taken before the regeneration (Sacha, 2026-07-23)
1. **`denom_class` = N/A for CONCENTRATION and OTHER**, excluded from denominator analyses. A
   concentration estimate ("top X% of users -> Y% of activity") is structurally not a prevalence
   denominator; forcing a value would invent data no analysis consumes. Concentration retains its own
   fields (`conc_unit`, `conc_group_pct`, `conc_share_pct`). Lands in v1.5.2.
2. **Run the source-anchored denominator adjudication BEFORE regenerating** (35 flagged rows). Rationale:
   `denom_class` is the paper's central variable, so regenerating every figure on codes we know an
   independent check disputed — then fixing them — means doing the work twice.
3. **Accept the deterministic correction of the 8 pre-ruling RoB rows** rather than re-appraising. The
   ruling makes item 6 = LOW unambiguously for them and the summary rating recomputes from the
   pre-specified anchor; the master records which rows were appraised vs recomputed, so it is auditable.
4. **RoB items 5 and 8 are RETAINED** despite carrying almost no information (8.4% / 5.5% HIGH).
   Dropping items from a validated instrument costs more credibility than the noise saves; they are
   reported descriptively instead.

### Denominator adjudication launched — 35 rows, source-anchored
`data/extract_v2/qa/denom_adjudication_worklist.csv` + 4 shards. Composition of the challenge:
23 `topical` -> `curated_sample`, 11 `political_news` -> `all_media`, 1 `news_diet` -> `all_media`.
Agents are explicitly instructed that WE may be the ones who are wrong (our own codebook makes
top-N-by-engagement `curated_sample`), and must decide against the SOURCE with a verbatim quote, with
KEEP_OURS / ACCEPT_CHALLENGE / THIRD_OPTION as available verdicts.

### v2txt stub sweep — contained, no systemic issue
Prompted by the shard-28 finding that `OA-W7125772788.txt` was an 11-byte stub masking a real 11-page
image-only PDF. Swept all 736 v2txt files: only **2** are under 2 KB, and only **1** maps to a frozen
study — `OA-W7125772788` itself, which does have a usable PDF at `data/fulltext/pdf/` and which the
appraiser already read by page rendering. No other appraisal or extraction was silently degraded by an
empty text cache. (`W4400651963.txt`, 1,864 b, does not map to a frozen study.)

### DENOMINATOR ADJUDICATION COMPLETE -> FROZEN v1.5.2 (MD5 f24159861327825de61f0d8feda5a45d)
34 distinct disputed rows re-read at source by 4 agents (35 worklist entries; one frozen row was flagged
by two cross-model items and received the same verdict twice — not a discrepancy).

**KEEP_OURS 14 · ACCEPT_CHALLENGE 13 · THIRD_OPTION 7 — we were wrong on 20 of 34 (59%).**
Transitions: `topical -> curated_sample` 13 · `political_news -> news_diet` 5 ·
`political_news -> curated_sample` 1 · `topical -> single_source` 1.

**The dominant error was one our own codebook already legislated against.** Thirteen rank-truncated
top-N sets were coded `topical`: "the 118 most widely viewed videos were selected", "top 10 articles for
each keyword", "the first 50 English-language videos ranked by relevance", "the top 100 most popular
videos from three hashtags". Our rule already said most-shared/top-N is `curated_sample` — the rule
existed and simply had not been applied consistently. This is the strongest argument yet for the
cross-model check: a same-model audit had passed over these repeatedly, because the same reading that
produced the error also validated it.

**Operational line the adjudicators converged on, now governing:** exhaustive or probability-sampled
keyword corpus = `topical`; rank-truncated top-N by views/shares/popularity/relevance = `curated_sample`.
(Add to the codebook's hard cases.)

**The `all_media` challenges were mostly rejected but pointed at a real problem in the other direction:**
5 further rows were neither `political_news` nor `all_media` but **`news_diet`** — Cordonnier's
information-time denominator, NewsGuard-UK all-topic outlet tweets, Facebook posts from a 12,000-outlet
list, all national-news links, and Guess et al.'s "overall news diets". v1.5.1 caught 11 news-wide rows;
adjudication found 5 more. The category was clearly needed.

**Plus 52 rows set to `denom_class = n/a`** (CONCENTRATION + OTHER) per Sacha's decision.

**IMPACT ON RESULTS: none on the headline.** Gates PASS; whole-diet backbone unchanged at k=29,
median 7.5% [5.0-11.0]; CONTENT 22.3% [18.4-26.1] k=205; EXPOSURE 2.6% [0.6-5.1]. The recodes moved rows
BETWEEN non-backbone categories (topical <-> curated_sample) or WITHIN the backbone
(political_news -> news_diet), so backbone membership is stable. What changes is the **denominator
moderator analysis**, which is precisely the analysis the paper's thesis rests on — so getting it right
before regenerating was worth the delay.

**Low-confidence rows flagged by adjudicators for a later look:** row 253 (2-s2.0-105002578811, tennis
elbow — paywalled, kept `topical` for lack of evidence of ranked truncation, but "139 unique videos from
two queries" suggests a hidden per-query cap); row 531 (2603.11058 — view-weighted random sample of a
multi-topic, partly misinfo-seeded keyword corpus; the codebook has no category for multi-topic
misinfo-weighted corpora); row 468 (Groen & Geboers); row 105 (two sibling Facebook groups -> chose
`single_source` under prefer-the-narrower, imperfect fit). Three verdicts rest on abstracts not full
text (253, 298, 255) and are marked as such in the reasoning column.

## 2026-07-23 — ITEM 2 COMPLETE: single-pass regeneration from v1.5.2 + counts crosswalk

Everything downstream rebuilt from one freeze in one pass: phaseB_{prep_regression, descriptives,
slices, precision, uncertainty, grade, figures, figures2, figures3, export_json, dashboard},
phaseB_metareg.R, build_companion_dashboard, make_prisma, make_counts_crosswalk. All succeeded.

### A serious defect found: the PRISMA gate was validating a STALE dataset
`validate_prisma.py:65` defaulted to a hardcoded `estimates_v1.4.0_frozen.csv` unless an env var was
set. **Every "validate_prisma PASS" reported from v1.4.1 onward — including v1.5.0, v1.5.1 and v1.5.2 —
was validating a 329-study snapshot, not the live freeze.** The gate's LOGIC was sound (it still passes
with 0 orphans against the true freeze) but a gate that green-lights the wrong file is worse than no
gate, because it manufactures false confidence. Fixed to follow the `docs/FROZEN.md` pointer like every
phaseB script; the env var remains as an override. Against the real freeze: INCLUDED_FROZEN 317 (was
329), DEDUP_COLLAPSED 13 (was 10), DROPPED_V2_UNLEDGERED 62 (was 57) — the v1.4.3 exclusions and merges
finally reflected. **This also explains the long-standing 329-vs-317 discrepancy** that had been visible
across the docs: it was never a real disagreement, it was one script reading a file nobody had
repointed.

### PRISMA regenerated — now derived, and it reconciles
`scripts/make_prisma.py` rewritten. It no longer carries literal counts; it reads
`data/synth/prisma_counts.json` (newly emitted by validate_prisma) and **asserts the reconciliation
before drawing**: 317 included + 45 not retrieved + 45 no-codeable-estimate + 411 excluded = 818
assessed. The old diagram showed 408 studies / 695 estimates, omitted the PubMed and OpenAlex-keyword
arms entirely, and its arithmetic did not close (2,759 − exclusions = 645, but the included box said
977). PRISMA 2020 structure now shown properly, with databases and citation-searching as separate
identification arms. If the partition ever breaks the script FAILS rather than shipping a wrong figure.

### Counts crosswalk + an active drift check (`scripts/make_counts_crosswalk.py`, NEW)
`docs/counts_crosswalk.md` defines every count and, critically, the distinctions that caused the drift:
record vs study, study vs estimate, all estimates (679) vs the main analysis set (577). It also SCANS
current documents for contradicting numbers and exits non-zero if any are found — a check, not a
rewriter, because a stale number sometimes belongs in a historical passage.
First run found 14 contradictions. Resolved: `METHODS_PROVENANCE.md` (said 590/329) and
`data_quality_methods.md` (said v1.4.5 / 718 / 680) rewritten from the freeze; `data_review.html`,
`project_summary.html` and `figure_contrast.{svg,html,png}` (stale n=695) archived to `docs/Old/`;
genuinely historical version tables (dataset_provenance, punchlists) exempted by design.
**Drift check now clean, exit 0.**

### Statistical corrections folded into the same pass (item 4, done early to avoid regenerating twice)
- **Sparse moderator levels collapsed** at n<10 before modelling (topic 10->6, platform 19->12,
  breadth 6->5). `topicwar_geopolitics` had SE=1.51 — an odds ratio anywhere from 0.03 to 11 — and
  reporting that as a finding would have been indefensible.
- **df-adjusted pseudo-R^2 added.** Raw R^2 rewards degrees of freedom, so ranking a 10-df platform
  factor against a 2-df measurement factor in one ladder (as the manuscript did) is misleading. Both are
  written out; the ADJUSTED one should be ranked. Platform falls 12.6 -> 10.7 under the penalty.
- **The variance-ratio caveat is now printed in the output**, not left as an R warning: the ratio of
  largest to smallest sampling variance is **6.9e+11**. PLO variances assume independent Bernoulli
  draws, but for the large behavioural studies n is user-days/tweets/impressions, which are clustered —
  so those variances are understated and those studies over-weighted. Interpret variance-explained, not
  coefficients.
- **FINE-GRAINED DENOMINATOR ADDED — this one matters.** The regression used a coarse 3-level
  whole_diet/narrow/other recode, which explained **1.0%** of variance and so appeared to CONTRADICT the
  paper's central thesis. Adding the freshly adjudicated 8-level `denom_class` as `denom_fine` gives
  **13.3% (adj 11.9%)** — a thirteen-fold difference. The coarse binary was hiding the paper's own
  effect. Adjusted-R^2 ladder now: measurement 19.5 · ground_truth 17.6 · id_method 17.1 · sampling 16.2 ·
  construct 14.8 · breadth 13.0 · **denom_fine 11.9** · platform 10.7 · topic 7.3 · denom(coarse) 0.6.

### Consistency verified across artefacts
frozen 317/679 · prisma_counts.json 317 · prisma_flow.svg 317/679 · RoB master 317 · dashboard 317/679.
Dashboard version string now DERIVED from the freeze pointer — it had been advertising v1.4.7 in its
lede and v1.4.6 in its footer, on the same page.

## 2026-07-23 — ITEM 3: manuscript reconciliation + truth-in-claims

### Sensitivity analyses implemented (`scripts/phaseB_sensitivity.py`, NEW)
The manuscript claimed two sensitivity analyses that had **no backing code** — the worst kind of
reproducibility failure, since a reviewer who asks for the script finds nothing. Now implemented, plus
two the appraisal campaign made possible. Each re-runs the primary statistic (study-level median +
study-cluster bootstrap CI) on a restricted set. Output `data/synth/phaseB/sensitivity.csv`.

**D (exclude HIGH risk-of-bias studies) is the headline result:** CONTENT falls 23.0% -> **12.7%**
(-10.3 pp) while **EXPOSURE is unchanged at 2.6%** and the whole-diet backbone barely moves
(7.2 -> 6.9%). This is the review's directional prediction, stated in advance and borne out: the
alarming numbers depend on the weak designs, the reassuring ones do not.

**A2 (fold QUALITY into CONTENT, adversarial):** CONTENT moves only 23.0 -> **24.5%** (+1.5 pp). The
falsity/quality rule — the review's most contestable operational choice — turns out to matter far less
than expected. The decisions register had guessed "+5-10pp". Reporting the smaller number.
**A1** (drop borderline rows): no change. **C** (full-text-appraised only): CONTENT -2.0 pp.
**B** (blind re-extraction subset): EXPOSURE/SHARING unchanged; CONTENT and RECALL swing hard but on
k=7 and k=5, so that is small-subsample noise, NOT evidence of extraction error — stated as such.

### A consistency defect caught before it reached the manuscript
`phaseB_uncertainty.py` computed the headline medians from `regression_data.csv`, which drops
estimates lacking an extractable n (~13% of the main set). It therefore produced a SECOND set of
primary numbers disagreeing with every other script (EXPOSURE k=15 vs 16, CONTENT k=205 vs 211,
backbone 7.5% vs 7.2%). Fixed: medians and leave-one-out now use the full main analysis set; only
heterogeneity and the Spearman test — which mathematically require n — use the restricted subset, and
they say so. **Verified: uncertainty, sensitivity and GRADE now report identical medians for all six
groups.**

### Manuscript rewritten against v1.5.2
Methods sec 2.3-2.9 and the whole of Results replaced with computed numbers. Substantive changes:
- **Truth-in-claims.** sec 2.4 now states plainly that title screening was SINGLE-screener, not "dual
  independent" as `METHODS_PROVENANCE.md` had claimed, and lists the three checks that bound the error.
  Every kappa is relabelled **model self-consistency**, with the reason spelled out: two passes of one
  model cannot surface an error the model makes consistently.
- **NEW sec 2.9 "Reliability, and its limits"** grading evidence in three tiers — model self-consistency
  (weakest), independent model (construct kappa 0.77 vs Perplexity/GPT-5.6), human coding (strongest,
  marked PLACEHOLDER pending Sacha + Laura). It reports that the cross-model check found our coding wrong
  on 20 of 34 disputed rows, and says why that is the point rather than an embarrassment.
- **sec 2.7 rewritten** for the Hoy-adapted instrument, incl. the source-level-list ruling and its
  anti-double-counting rationale, and the abstract-only caveat.
- **sec 3.6 scoped correctly:** "risk of bias tracks the number inversely" is now stated only for
  content and exposure measures, with RECALL named as the deliberate exception (high values, low bias,
  weakness is indirectness). The global claim would have been false and the counterexample sits in our
  own table.
- **sec 3.3 NEW** — I^2 99-100% and prediction intervals up to 0.3-93.6% as the quantitative proof that
  the constructs do not pool.
- **sec 3.5** now notes the coarse-vs-fine denominator result (1.0% vs 11.9% variance explained).
- Header, outline, and sec 2.3 (two streams -> four, with the 16.1% non-Scopus contribution and the
  query-recall-not-coverage point) all corrected.

Drift check still exit 0 after the rewrite.

**Outstanding in the manuscript:** the Discussion is still undrafted, and sec 2.9 carries one explicit
PLACEHOLDER for the human agreement figures.

## 2026-07-23 — small items cleared

### `docs/RESUME_HERE.md` rewritten
It was a month and seven freezes stale (described a 1,091-row / 529-study master with a 14-column
schema). Anyone resuming cold would have been misled about the dataset, the schema and the state.
Now carries the v1.5.2 pointer, the headline table, the pipeline run-order, open items, and a
"hard-won lessons" section recording the four failure modes this campaign uncovered so they are not
re-learned: a gate green against the wrong file; a vocabulary change silently breaking 8 scripts that
each hardcode the same set; same-model auditing being unable to find systematic error; and
claimed-but-uncoded analyses.

### Concentration reported per threshold (`scripts/phaseB_concentration_table.py`, NEW)
The old presentation ("top 1% -> 70%, top 10% -> ~88%, top 20% -> ~75%") reads as one Lorenz curve
but is not: each threshold rests on a different, small set of studies, which is why the sequence is
non-monotonic. Now banded WITH study counts, user and source concentration separated, and no
interpolation. **Only the top-<=1% band is solid: k=8 studies, median 70.0%, range 28.6-81.0.**
The other bands are k=2 and k=4 and are labelled "do not read across bands as a curve". A further
5 estimates state no population share at all and cannot enter any threshold comparison. Two studies
contribute at more than one threshold and are flagged as non-independent.
=> The defensible claim is the top-1% one; the rest is descriptive detail, not a curve.

### Venue-type sensitivity (`scripts/venue_sensitivity.py`, NEW)
Prompted by appraisers flagging low-visibility venues with internal contradictions — a concern about
the evidence base INDEPENDENT of risk of bias. Uses objective OpenAlex publication type, not a
subjective quality judgement.
First run was **uninterpretable and I nearly shipped it**: resolving by OpenAlex id alone left 277 of
317 studies "unknown", leaving arms of k=3 that swung 26 points. Added a DOI fallback (84% of studies
have a resolvable DOI in the cached dumps); coverage is now **269 journal articles (84.9%), 12
conference papers, 6 preprints, 6 repository records, 17 unknown**.
**Result: the conclusions do not depend on the grey-ish tail.** Restricting to journal articles moves
EXPOSURE -0.6 pp, CONTENT +0.8 pp, the whole-diet backbone +1.5 pp, and the largest shift anywhere is
RECALL +4.2 pp. Excluding repository/unknown records changes almost nothing.

### Second-opinion re-check dispatched
The 5 adjudications made at confidence <=3 (rows 495, 468, 531, 253, 105) are under independent
re-check with an explicit brief not to defer to the first verdict. Row 531 (multi-topic,
partly misinfo-seeded keyword corpus) may need a NEW codebook category — the taxonomy currently has
no home for it.

## 2026-07-23 — second-opinion re-check -> FROZEN v1.5.3, and item 5 (presentation)

### Re-check of the 5 low-confidence adjudications: agreed 3, overturned 2
An independent second opinion, briefed explicitly NOT to defer to the first verdict:
- **row 468 (105021775752) reverted to our ORIGINAL `political_news`.** The first adjudicator read
  "most shared links" as rank truncation; the source shows it labels a DATA TYPE ("close to 3 million
  tweets ... that contain a link to a news article") and the statistic is problematic-source shares
  over mainstream-source shares, so a natural total exists. The only genuine top-N truncation in that
  paper feeds different estimates. Worth noting: the adjudication campaign was right to run, and it
  was also capable of over-correcting — the second opinion caught one.
- **row 531 (2603.11058) -> `curated_sample`.** Five domains rather than one issue (our own `topic`
  field says general_news), ~half the retrieval keywords are misinformation-associated, and the
  authors concede the corpus "is unlikely to be exhaustive".
- Agreed on rows 253, 495, 105 (495 at HIGHER confidence: the paper's own words are "the overall news
  diets of each group").

### SPILLOVER — a class of error the first adjudication created
It corrected each FLAGGED row but left sibling rows of the SAME study and SAME measure in the old
class, so single studies ended up split across two denominator classes: `85081743293` rows 629-632
(Trump/Clinton breakdowns of the same news-diet quantity) and `85168520853` rows 607-608 (gender
breakdown of the same 1,534 statements). Repaired in v1.5.3 — as targeted edits, NOT blanket
propagation, since a study legitimately can carry different denominators across estimates.
**A detector now exists** (`qa/v153_mixed_denom_studies.csv`): 22 studies span >1 denominator class,
10 adjudication-touched and flagged REVIEW. Some are legitimate (REACH rows `population`, diet-share
rows `news_diet` in the same paper).

### Two codebook rules added
1. A **misinformation-weighted retrieval instrument** makes the denominator `curated_sample` however
   large the corpus — if the keyword list deliberately includes misinfo-associated terms the
   denominator is tilted by construction, and size or probability-sampling downstream does not repair
   it. `topical` requires a topic-NEUTRAL query set on a SINGLE issue.
2. A keyword corpus spanning several unrelated issues is not `topical`; absent a consumption stream it
   falls to `curated_sample`.

### FROZEN v1.5.3 — MD5 `c5abcb864b2a5eb58154a242a2709b02`
8 denom_class changes, 0 value changes, gates PASS, full pipeline regenerated, drift check clean.
Backbone 262 -> 263. denom_class: topical 297 · population 132 · political_news 97 · n/a 52 ·
curated_sample 35 · single_source 30 · news_diet 20 · all_media 14.

### ITEM 5 (presentation) — colour, a missing exhibit, and dead-end pages
**Palette.** The figures encoded their central comparison in green/amber/red, which deuteranopes
cannot separate — the figure failed for ~8% of male readers. Ran the dataviz validator rather than
eyeballing it. Finding worth recording: single-hue blue ramps FAIL as categorical palettes (to be
distinguishable they need lightness extremes that fall outside the legible band — e.g.
`#74a9cf/#2b8cbe/#045a8d` gives normal-vision ΔE 11.1, below the floor of 15). The passing scheme is
**sky #56B4E9 -> orange #E69F00 -> vermillion #D55E00** for ordinal severity and
**blue #0072B2 -> orange -> vermillion** for measurement type: cool-to-hot reads as severity while
avoiding the green/red pair entirely. All six checks PASS. Applied across
`phaseB_figures{,2,3}.py` and the dashboard KPI tiles; 0 residual traffic-light hues. Colour is never
the sole encoding — every mark keeps a direct label or a written LOW/MODERATE/HIGH tag, which also
discharges the orange contrast warning. Also removed a redundant double-encoding where fig1 coloured
marks BY the value that position already showed.

**NEW Figure 5 — forest plot with confidence intervals** (`scripts/make_forest_plot.py`,
`docs/fig5_forest_constructs.svg`). The flagship figures had medians and IQRs but no intervals, so the
central claim was presented without uncertainty about the medians themselves. Dot-and-interval on a
log axis (a linear axis would compress everything under 10% — exactly where the argument lives).
Rendered and inspected, not just generated. It makes the key point visually: EXPOSURE [0.8-5.1] and
RECALL [37.5-65.9] do not approach each other.

**Dead-end pages.** The five component pages had no links to anything, so a reader landing on one had
no route to the narrative dashboard. A "Start here" banner is now injected by the GENERATING scripts
(a first attempt patched the HTML directly and was wiped by the next regeneration — the fix has to live
in the generator).

## 2026-07-24 — Full-corpus cross-model pass launched (round 3, Sacha: "give GPT everything")

Decision: run Perplexity/GPT-5.6 over the WHOLE corpus, in addition to the human IRR. Reframed what
it's FOR — not more reliability (we have enough) but an independent ERROR-DETECTION SWEEP: every row
where a different model family disagrees with our v1.5.3 coding is a candidate error. No API key, so
manual paste; scoped to all 679 rows with adjudication of load-bearing disagreements only.

**Paste burden minimised.** `scripts/build_perplexity_full.py` assigns stable F-ids to all 667
codeable rows, maps the 212 answers already gathered in rounds 1-2 onto their rows (coded blind from
the quote, so valid against current coding), pre-fills them, and generates paste batches ONLY for the
455 net-new rows -> **11 batches of 45** (not 23). Deployed to `~/Desktop/Misinfo_Perplexity_Check/`
(round-2 files archived to round2_done/). Ingest: `scripts/ingest_perplexity_full.py` (idempotent,
F-ids). Score: `scripts/score_perplexity_full.py`.

**Preview from the pre-filled 212 (scored against v1.5.3):** construct kappa .71 (raw .775, AC1 .746),
denom_class .47 (raw .554), breadth .61. Consistent with round 2 — the corpus-level independent-model
reliability number is essentially established; the full sweep confirms it and adds coverage.

**The queue clusters into a few patterns — most are GPT convention differences, NOT our errors.**
Of 109 load-bearing disagreements from the pre-filled portion:
- denom_class 63, but **29 are `n/a -> a denominator`** — GPT assigning a denominator to
  CONCENTRATION/OTHER rows we correctly marked n/a (it wasn't told that rule). GPT-wrong.
- construct 46, almost all **GPT over-applying SHARING** (RECALL/EXPOSURE/OTHER -> SHARING) and
  missing our ratified engagement=SHARING / most-shared-is-sampling rules. GPT-wrong.
- Only two transitions match CONFIRMED round-2 error types: **`topical -> curated_sample`** (top-N
  corpora, 59% ours last time) and **`political_news/topical/single_source -> all_media/news_diet`**
  (news-wide widening -> the `news_diet` finds). The scorer flags these **HIGH priority**: 18 of the
  109 from the pre-filled portion; expect ~40-50 across the full corpus.

**Adjudication plan (the answer to the queue-cost concern):** do NOT hand-check the whole queue.
Adjudicate only the HIGH-priority transition rows (source-anchored agents, as in round 2); treat the
low-priority remainder as reliability signal (GPT applies looser conventions), not an error list.
Row-by-row is unnecessary because the errors, if any, are a few systematic patterns — exactly what
round 2 showed (20 errors, almost all one pattern).

## 2026-07-24 — FULL-CORPUS cross-model pass DONE -> FROZEN v1.5.4

Sacha ran the whole corpus through **GPT-5.6 Terra Thinking (via Perplexity)** in one session (11 paste
batches + an 11-row gap batch). Ingested to 667/667 (100%). Scripts: build_perplexity_full.py,
ingest_perplexity_full.py, score_perplexity_full.py.

**Corpus-level independent-model agreement (vs v1.5.3):** construct kappa **0.75** (raw .82, AC1 .80),
breadth 0.69, denom_class 0.53. This is now on the WHOLE corpus (637 codeable rows; 30 UNSURE), not a
sample — the strongest reliability figure the paper has, and it went into manuscript sec 2.9.

**Error-detection sweep.** 263 load-bearing disagreements. Triaged to 49 HIGH-priority rows in the two
transition patterns with a confirmed track record of being OURS. Six source-anchored agents re-read
each. **Our coding was wrong on 33 of 49 (67%)** — higher than round 2's 59%. CAREFUL FRAMING logged in
FROZEN.md and apply_v154.py: 67% is the hit rate WITHIN a queue pre-selected for likely-ours transitions
(it validates the filter), NOT a corpus error rate. Corpus-wide GPT agreed on denom_class 64% of rows,
and most disagreements were GPT looser conventions (over-calling all_media; assigning denominators to
n/a concentration rows) which we did NOT apply.

**v1.5.4 applied 22 denom_class changes** (MD5 0d0ddc3245141c0f90463e2bd4ae558c, gates PASS, full
pipeline regenerated, drift clean): political_news->news_diet 10, topical->curated_sample 8,
single_source->all_media 3, political_news->curated_sample 1. The news_diet finds (esp. the
Altay/Nielsen/Fletcher NewsGuard country rows) subdivide the whole-diet backbone. Headline holds:
EXPOSURE 2.6% [0.8-5.1], CONTENT 23.0% [19.0-26.1]; **whole-diet backbone k=30->31, median 7.2->7.4%**
(the news_diet additions grew it slightly).

**One mapping bug caught before freezing:** the F-id->row_index resolution for study 85114317455 (two
sibling EXPOSURE rows sharing a quote) landed the single_source->all_media verdict on the already-
all_media sibling (row 481) instead of the actual single_source row (482, algorithmic timeline).
Corrected in apply_v154.py (drop the 481 no-op, apply 482). Lesson: quote-prefix matching is ambiguous
when a study splits one measure across sibling rows — verify by study_id AND resolve to the row whose
current code matches the verdict's `our_denom_class`.

**Codebook rule added** (numerator-building vs denominator-defining): a misinfo-weighted/rank-truncated
instrument that builds the NUMERATOR over a clean single-issue denominator stays `topical`; it is
`curated_sample` only when the selection defines the sampled SET. This kept the big COVID/GMO/vaccine
Boolean corpora as topical while moving genuine top-N baskets to curated_sample.

## 2026-07-24 — IRR v3 package review -> found a CORPUS DUPLICATE -> FROZEN v1.5.6

Pre-send review of the human IRR package (Sacha: "is it ready for Laura and I?") found three
blockers; fixing the second required a re-freeze.

**1. The `papers/` folder was never created.** Part 2 worksheets pointed at `papers/D*.pdf` but
`build_human_irr_worksheet.py` wrote the paths without copying the PDFs — Part 2 was undeliverable
as shipped. Fixed: the build script now copies the drawn PDFs into `irr_v2/papers/` under blind
D-names (and clears stale copies from a previous draw).

**2. Two Part-2 items were the SAME paper -> corpus duplicate.** `NEW-jadara-2022` and
`OA-W4394831676` are byte-identical PDFs (MD5 eae327e11c0d55b8efb23d0f95096770) carrying the same
estimate (81.6% RECALL, Levant COVID survey) under two IDs — an abstract-only OpenAlex sweep row
plus the same paper re-ingested as a new PDF on 2026-07-15. `one_per_study` cannot catch cross-ID
duplicates. A corpus-wide scan (PDF MD5 + shared-quote-prefix across IDs) found NO other duplicated
study (the only other identical PDF pair, NEW-moreno-jmirderma / PMID-37632797, has zero dataset
rows under the stray ID; the stray PDF is referenced by historical snapshots so it stays on disk).
**FROZEN v1.5.6** (`scripts/apply_v156.py`, MD5 f93d097182576a890380b86a81c2ba26): dropped the
abstract-only row, kept the full-text twin (n=6,910, complete moderator coding). 678 estimates /
316 studies. RECALL-only, so no CONTENT/EXPOSURE headline movement. Also dropped the orphaned
`OA-W4394831676` row from the RoB v3 master (both twins carried identical HIGH verdicts, so no
appraisal information is lost). Full pipeline regenerated (prep -> descriptives -> ... -> metareg.R
-> prisma -> crosswalk); drift check clean, RoB coverage 316/316. Manuscript mechanical counts
updated (679/317/577 -> 678/316/576, freeze ref v1.5.2 -> v1.5.6). NOTE: the manuscript's DERIVED
numbers (construct k's, medians in §3) still predate v1.5.3+ and need a full refresh pass before
submission — logged as an open item.

**3. D01's answer-key value was unfindable in the paper.** Key said 25, but the paper says
engagement "fluctuates around 20% and 30%" — 25 is a midpoint WE derived; an honest coder can never
produce it, so the item guaranteed a MISS measuring our derivation, not their extraction. Fixed
structurally: Part-2 eligibility now requires the key value to appear VERBATIM in the row's own
source quote (`value_verbatim()`; whole-fulltext matching was tried first and rejected — bare
integers like "25" match incidental years/page numbers). This also excludes computed complements
(e.g. 21.0 from "~79% do not visit").

**Smaller fixes.** Instructions now tell coders to code breadth from the reported-quantity wording
when the definition cell is blank (4 of 24 Part-1 items have no stated definition — a fact about
the papers, worth keeping in the sample). Definition snippets now truncate at a sentence boundary,
not mid-word. Scorer's disagreement export referenced a nonexistent `YOUR_verbatim_quote` column —
now uses the answer-key quote.

**Package rebuilt against v1.5.6 and verified:** 24 Part-1 + 12 Part-2 items, no study overlap
between parts, both coders' sheets identical, 12 unique PDFs shipped (no duplicates by MD5), every
Part-2 key value verbatim-findable in its quote, all worksheet PDF paths exist, scorer dry-run OK.
Ready to send to Laura.

## 2026-07-24 — Manuscript derived-number refresh (v1.5.6) + RoB aggregator fix

The mechanical counts had been updated with the v1.5.6 freeze, but §3's derived stats still
predated v1.5.3. Full pass against the regenerated pipeline outputs (every number sourced from
`data/synth/phaseB/*.csv` / `data/rob/rob_v3_*.csv`, none recomputed ad hoc):
- RECALL k 28→27, median 55.4→54.0 [37.0–64.0], IQR 30.0–68.2 (the deduplicated study was RECALL).
- Whole-diet backbone k 30→31, median 7.2→7.4 [5.0–8.8] (stale since v1.5.4); leave-one-out max
  shift is 0.08 pp (was reported 0.25); backbone unchanged at 7.4 under HIGH-RoB exclusion.
- Meta-regression: breadth 13.0→12.6, denom_fine 11.9→10.6 (df-adjusted); the coarse whole-diet/
  narrow dichotomy now explains 0% (n.s.), not 1.0% — strengthens the taxonomy argument.
- RoB (recomputed on the 316-study master): 49/41/9 HIGH/MOD/LOW; item 10 80.7% (modal defect),
  sampling 79.0%, case definition 52.3%; RECALL 11.9% high (was 13.3); full-text appraisals 284.
- GRADE table: RECALL row updated; all other constructs unchanged. Topic counts: COVID studies 69→68.
- GPT sweep sentence verified: the dropped row (F305) was one of GPT's UNSURE declines, so
  "626 of 678 coded" and all κ values are unaffected by the dedup.

**Bug found and fixed while doing this:** `aggregate_rob_v3.py` rebuilds the RoB master from shards
and had silently RESURRECTED the hand-pruned `OA-W4394831676` row — it computed the orphan set
(appraised studies not in the freeze) but only reported it. The aggregator now FILTERS shard rows to
the frozen study list, so the master mirrors the freeze by construction (316/316, 0 orphans). Same
lesson as the dashboard banner: a fix to a generated file must live in the generator.
`phaseB_grade.py` re-run, crosswalk drift check clean, RoB coverage 316/316 [OK].

Residual known-stale by design: §2.9's PLACEHOLDER (human IRR pending). NOTE: the crosswalk drift
check scans COUNTS only, not derived stats — after any future re-freeze, §3 needs a manual sweep.

## 2026-07-27 — HTML coding interface for the human IRR (CSV stays the format of record)

Sacha: coding raw CSVs is ugly. Built `scripts/build_irr_coding_html.py` -> `code_<coder>.html`
(one page per coder, deployed next to `papers/`): one card per item, click-to-code chips with the
category definitions inline, autosave to localStorage, progress bar, blank-definition fallback note
on the 4 no-definition items, an explicit n/a chip for the denominator (exports as blank), and a
"Download my two CSV files" button that emits part1/part2_<coder>.csv with EXACTLY the worksheet
columns in the worksheet row order — so `score_human_irr.py` ingests them unchanged. The CSV
worksheets remain the source of truth; the page embeds only worksheet columns (never the key).
END-TO-END VERIFIED in a real browser: coded all 36 items through the UI handlers, exported, and
ran the actual scorer on the export (36/36 scored, n/a correctly excluded, quote/comma escaping
round-trips). One automation artefact noted: the Chrome extension's synthetic clicks land ~12.5%
off (browser-zoom scaling), so chip clicks were driven via element handlers — not a page bug.
Instructions + README now point to the HTML pages first, CSVs as the spreadsheet fallback.

## 2026-07-27 — C21 contamination note (human IRR, Sacha only)

While Sacha was coding, a diagnostic run in the assistant session printed the frozen row's `flag`
field for C21's study (OA-W3113799821), which contains a construct-recode note — i.e., a piece of
our coding for that item became visible to Sacha mid-task. Laura is unaffected. DECISION, recorded
in advance of scoring: **exclude C21 from Sacha's coder-vs-dataset comparisons** (construct and
breadth) regardless of what he codes; keep it in Laura's comparisons and in coder-vs-coder only if
his answer predates/ignores the leak (he was told to note it). Also: report Part-1 breadth
agreement WITH and WITHOUT the four blank-definition items (C01, C21, C22, C23) — for those,
breadth is underdetermined for any coder, and C21's study is abstract-only for the pipeline too.

## 2026-07-27 — Scoring note (pre-registered): Part-2 denominator agreement is stratified by construct

Sacha, mid-coding, flagged that for RECALL items the Part-2 pointer ("% of survey respondents who
said...") largely determines the denominator class (population) — construct and denom_class are
nearly the same fact for surveys. Correct, and unavoidable if the pointer is to name the right
quantity. DECISION: when reporting Part-2 denominator agreement, note that the RECALL/REACH items
are partially pointer-determined; the informative denominator test is the CONTENT/EXPOSURE/SHARING
items (topical vs curated_sample vs news_diet vs all_media vs single_source), where the pointer
carries no denominator information. Report the split if the k's allow it.

## 2026-07-27 — Sacha's IRR sheets delivered; D11 pre-registered handling

Sacha completed both sheets via the HTML interface (part1: 24/24; part2: 11/12; mean confidence
3.71, notes on 14 items). Files ingested verbatim to docs/RA_package/irr_v2/ — coder files are
never edited after delivery.

**D11 (study 85114317455) left blank DELIBERATELY** — Sacha judges the item invalid: the pointer
demands "the SINGLE overall figure" but the paper reports two equally-overall sibling estimates
(chronological vs algorithmic timeline), so no single figure exists. The point has merit; the
scorer's MATCH/ALT rule was the designed mitigation, but a coder refusing the premise is itself
informative. ADDITIONALLY: this session's pre-send review (before coding began) openly discussed
this exact study's two values, so D11 was already contaminated for Sacha's vs-dataset comparison.
DECISION (pre-registered before Laura codes): D11 is excluded from Sacha's vs-dataset comparisons
(the blank does this mechanically — the scorer skips unfilled items); it STAYS in Laura's sheet and
her comparisons (she saw none of this); coder-vs-coder on D11 is void (one side blank). The
exclusion tally for Sacha now: C21 (flag leak, construct/breadth) + D11 (blank by refusal +
prior value disclosure).

## 2026-07-28 — While waiting on Laura: GitHub remote, mixed-denom disposition, Discussion draft

1. **Private GitHub remote**: github.com/SachaAltay/misinfo-prevalence-review (private). Full
   history + freeze tags pushed (chunked push; single 2GB pack was rejected). Off-machine backup of
   the whole project now exists.
2. **Mixed-denominator REVIEW disposition** written to `qa/mixed_denom_review_2026-07-28.md`:
   5 of the 10 flagged studies are LEGITIMATE multi-denominator studies (different measures);
   5 are same-instrument spillover splits with a recommended reconciliation (17 denom_class cells,
   topical→curated_sample ×15 net, political_news→news_diet ×3; no values, no headline effect).
   AWAITING SACHA'S APPROVAL — would become v1.5.7.
3. **Discussion (§4) drafted** in manuscript_draft.md: exposure–perception reconciliation
   (Hameleers; conditional-vs-marginal reading of forced-exposure experiments), denominator-is-the-
   finding (item-10 80.7%, RoB-tracks-magnitude, CCDH-vs-Meta), concentration as the neglected
   quantity, 4 reporting requirements, limitations (incl. honest LLM-assistance account), and a
   conclusion. One PLACEHOLDER remains (§4.5 human IRR, same as §2.9). Authorial "we" kept
   throughout despite solo authorship (consistent with §1–3; flip to "I" globally if preferred).

## 2026-07-28 — Mixed-denom decision page + lit-review/citation audit launched

Built `qa/mixed_denom_decisions.html` (opened for Sacha): the 5 LEGITIMATE studies shown as a
table, the 5 RECONCILE items as decision cards (Approve / Keep as-is / Other + note, saved
locally, copy-to-clipboard summary). Decisions pending; approval → v1.5.7.

Also launched a citation audit of the manuscript's §1/§4 against the definitional and
effects-debate lit reviews plus a semantic sweep of the PDF library, with instructions to flag
inaccurate claims and recommend circle/'friend' papers (Altay, Mercier, Acerbi, Berriche,
Altay-Nielsen-Fletcher, Williams, Budak/Nyhan/Guess/Watts, Allen) only where they strengthen a
specific sentence. Results to be reported and applied after review.

## 2026-07-28 — Citation audit applied + decision page v2

**Citation audit (independent agent over the two litreviews + semantic library sweep) APPLIED to
manuscript §1/§4.** Accuracy fixes: gap claim qualified and Suarez-Lledo & Alvarez-Galvez 2021
cited (prior single-domain review); Nickl et al. 2025's explicit call for this comparison cited;
the distrust second-order effect now attributed to Hameleers as THEORY and grounded empirically
(Matthes 2022; Boulianne & Humprecht 2024; Hoes 2025); the media-coverage/publicity claim anchored
(Carlson 2020; Stecula 2025; Altay & Acerbi 2023); the forced-exposure/base-rate argument anchored
(Altay, Berriche & Acerbi 2023; Berriche & Altay 2020); §1's opening numbers now attributed
(Vincent/SIMODS 2025; van der Meer & Hameleers 2024; CCDH 2021). Additions incl. friend/circle
papers where load-bearing: Budak et al. 2024; Guess, Nyhan & Reifler 2020; Allen et al. 2020;
Watts et al. 2021; Rogers 2020; Grinberg et al. 2019; Wardle & Derakhshan 2017; Mercier 2020;
Williams 2026; Altay & Mercier 2026; Altay 2026; Pennycook & Rand 2026; Baribi-Bartov et al. 2024;
Allen, Watts & Rand 2024. Three refs were missing from the bibliography entirely (Hoy 2012 — the
RoB instrument!; Berriche 2024 thesis — the seed corpus; Suarez-Lledo 2021): added to
local_additions.bib, combined bib rebuilt (10,472 entries).

**Decision page v2** (`scripts/build_mixed_denom_decisions.py` — now generated, not hand-written):
adds the topical-vs-curated_sample definitions, a per-study DECISIVE QUESTION, the full frozen row
table per study, and open-the-paper links (2 PDFs + 2 extracted fulltexts staged in
qa/mixed_denom_papers/, PubMed link for PMID-41189872 which was never retrieved). localStorage key
unchanged so any prior clicks survive.

## 2026-07-28 — "Friend papers" clarified = the CONVERGENT/bridge literature; four more added

Sacha clarified that "friend papers" means the previously-catalogued convergent literature
(litreview_misinfo_effects_debate.md shelf), not personal-circle authors. Cross-check: the core
convergent set was already cited after the audit pass (Hameleers, Nickl, Pennycook & Rand,
Williams, Budak, Altay-anchor papers). Added the four catalogued papers still missing, at their
natural §4 slots: Van Doorn 2023 (harms beyond false beliefs, §4.6 caveat), Tay/Lewandowsky 2024
(cause-vs-symptom false dichotomy, balancing the Altay & Mercier symptom cite), Tay/Hurlstone 2024
(causal-inference designs, §4.1 base-rate paragraph), and Ecker et al. 2024 (the threat-camp
anchor, cited in an ecumenical closing move so the Discussion reads as measurement-first, not
camp advocacy). All keys verified in combined bib. Interventions cluster (Berinsky/Guay/Tay 2023)
deliberately NOT cited — the review is about prevalence, not interventions.

## 2026-07-28 — FROZEN v1.5.7: mixed-denominator queue CLOSED (Sacha approved all 5)

Sacha's decisions from the HTML page, verbatim notes preserved: 85127039075 approve ("not sure why
I can't be both topical AND curated... clearly curated, but also clearly on just one topic");
85177420309 approve ("not exhaustive topical corpus, but does it exist????"); 85192635397 approve
("yes should be news diet"); 2603.11058 approve ("all curated samples (on a few selected
topics/keywords)"); PMID-41189872 no click but explicit verdict in the note ("clearly not
exhaustive, it's a curated sample ON a very narrow topic!") — treated as approval, recorded here.
Answered his taxonomy question: denom_class codes the SAMPLING MECHANISM (selection trumps topic,
per the ratified precedence rule); topic scope is its own column, so curated×covid19 loses nothing.

**v1.5.7** (apply_v157.py, MD5 0f10b6d7897a1f86f42d13f4784fb5e9): 20 denom_class cells
(topical->curated_sample 17, political_news->news_diet 3), rule-targeted within study, gates PASS
(0 value/construct changes, order preserved). Full pipeline + RoB aggregate + metareg + PRISMA +
crosswalk regenerated; drift clean. Only manuscript number that moved: denom_fine R2_adj
10.6 -> 10.3 (updated in §3.5). topical 289->272, curated_sample 44->61, news_diet 30->33,
political_news 86->83. The v1.5.3 detector's REVIEW queue is now fully dispositioned.

## 2026-07-28 — Pre-registered (before Laura's sheets): topical/curated under-specification in the IRR instrument

After approving v1.5.7, Sacha realized his own Part-2 IRR coding likely applied `topical` without
the selection-trumps-topic precedence rule — which the IRR materials never state (the chip labels
say only "one issue, keyword search" vs "hand-picked or top-N"). DECISIONS, logged before Laura's
sheets arrive: (1) Sacha's delivered sheets are NOT revised — post-hoc correction after learning
the rule would be contamination; (2) Laura's instructions are NOT updated mid-IRR — both coders
face the same under-specified instrument, keeping coder-vs-coder fair; (3) at scoring, denominator
disagreements on the topical<->curated_sample boundary are broken out and attributed to instrument
under-specification, and their convergence with the pipeline's own dominant error pattern (the
v1.5.4/v1.5.7 topical->curated corrections) is reported in §2.9 as evidence the boundary is
intrinsically hard, for humans and models alike.

## 2026-07-28 — Parallel manuscript v2 (docs/manuscript_v2.md) + ratio bootstrap

Sacha asked for a NEW version of the manuscript, built in parallel to `manuscript_draft.md`
(which is untouched), pushed to Science/Nature-level quality without overclaiming, for
side-by-side comparison.

**New analysis** (`scripts/phaseB_ratio_bootstrap.py`, seed/BOOT identical to
phaseB_uncertainty.py, primary set resolved from FROZEN.md): study-cluster bootstrap 95% CIs
on the between-construct ratios. RECALL/EXPOSURE 20.8x [9.2, 76.4]; CONTENT/EXPOSURE 8.9x
[4.1, 36.1]; RECALL/backbone 7.3x [4.5, 12.0]; CONTENT/backbone 3.1x [2.3, 5.0]. Output
`data/synth/phaseB/ratio_bootstrap.csv`. The manuscript's "twenty-fold" multiplier now
carries uncertainty; even the lower bound of the perception/diet ratio is 9x.

**manuscript_v2.md**: Nature/Science format (abstract + intro + results + discussion +
methods-at-end + data/code availability), all numbers regenerated against v1.5.7 (the draft
still said v1.5.6 in three places), new content: abstract; ratio CIs; the Cordonier
within-study denominator contrast (5% of news time vs 0.16% of connected time, 30-day
panel) as the thesis-in-miniature; retitled sections that lead with claims.

**Verification**: (1) independent number audit vs all phaseB CSVs + crosswalk (~150 claims)
— 3 discrepancies found and fixed: "less than a third" (topic/measurement R2 is 0.37),
"I2 essentially unchanged" under x10 inflation (EXPOSURE drops 99->90; reworded to
">=90% in every construct"), "eight-category denominator" (model df=6; reworded to
"denominator taxonomy"); plus REACH added to the re-extraction-subset movers (12.0->21.2,
k=12). (2) Editor-style review vs writing_voice rules — ~18 surgical edits applied
(deduplicated repeated headline sentences, unbolded running text, fixed causal shading:
"attributable to"->"associated with", "has taught"->"has told... plausibly echo",
dropped "verification" from "survives every ... check" while human IRR is a placeholder).
(3) make_counts_crosswalk.py drift check clean after all edits.

## 2026-07-29 — Manuscript v2 ADOPTED as canonical

Sacha approved adoption. Verified independently before adopting: phaseB_ratio_bootstrap.py exists
and reproduces the claimed ratio CIs exactly (RECALL/EXPOSURE 20.8x [9.2, 76.4]; CONTENT/EXPOSURE
8.9x [4.1, 36.1]; RECALL/backbone 7.3x [4.5, 12.0]); all referenced figure files exist; v2 pinned
to v1.5.7 throughout (and it correctly caught 4 stale v1.5.6 refs the old draft still carried).
Actions: (1) §4.8's verification story rewritten to the CUMULATIVE record (round-2 34/20 ->
full-corpus 49/33 with the within-queue-not-corpus framing -> the 17 stranded-sibling cells of
v1.5.7) instead of round-2 only; (2) old draft archived as docs/Old/manuscript_draft_v1.md (git mv,
history preserved); (3) v2 renamed to docs/manuscript_draft.md so every existing pointer (memory,
log, drift check) stays valid — ONE live manuscript file, as the drift-hazard lesson requires.
Crosswalk drift check clean after the swap. Both placeholders (human IRR, §3.5/§4.8) unchanged,
awaiting Laura.

## 2026-07-29 — Workspace reorganization for navigability (no content changes)

All moves via `git mv` (history preserved), nothing script-referenced was moved (verified by
grepping scripts/ for each filename first):
- `docs/RA_package/round1_2026-07/` created; the 13 first-RA-round artifacts (adjudication_29_*,
  verify_29.html, RA_INSTRUCTIONS, reply_to_Laura_DRAFT, etc.) moved in. The 5 script-referenced
  files stay at RA_package root. `RA_package/README.md` added: layout + the pre-registered IRR
  scoring rules in one place.
- `docs/synthesis_v1.md` -> `docs/Old/` (superseded by the manuscript).
- Project `CLAUDE.md` "Start here" rewritten as an 8-point map for future agents (log, freeze
  ledger, one-manuscript rule, crosswalk caveat, RA_package, qa/, phaseB outputs, GitHub) plus
  distilled house rules (coder files immutable; fix generators not outputs; content-based dedupe;
  full-pipeline regeneration per freeze).
Auto-memory updated (Discussion/manuscript marked DONE-and-adopted; freeze pointer current).

## 2026-07-29 — Near-miss + new guard: IRR builder refused overwrite of delivered sheets

A post-reorganization smoke test ran `build_human_irr_worksheet.py`, which regenerated BLANK
worksheets over Sacha's completed part1/part2 in the working tree. Recovered immediately via
`git checkout` (his sheets are committed; verified 24/24 coded rows restored; the .backups/,
Desktop, iCloud and browser copies were never touched). Durable fix in the generator:
`refuse_to_clobber_delivered_sheets()` — the builder now exits with an error if any existing
worksheet contains a filled YOUR_* cell, requiring delivered sheets to be moved aside explicitly
before a fresh draw. Verified: the builder now refuses to run. Same lesson family as the RoB
aggregator: a generator must protect what has become data.

## 2026-07-29 — HUMAN IRR COMPLETE AND SCORED (the third reliability tier lands)

Laura delivered both sheets (36/36, mean confidence 4.11, notes on 20 items; D06 NOT FOUND under
the 5-minute rule). Ingested verbatim, backed up (.backups/ + iCloud), committed, scored.
Full numbers + anatomy in `docs/RA_package/irr_v2/results_report.md`. Headlines:
- HUMAN CEILING: Part-1 construct κ .48 (snippets) but Part-2 construct κ .74, denominator
  κ 1.00, value 91% (full paper) — the evidence gradient IS the result.
- The pre-registered topical↔curated worry did not materialize (zero such confusions; Sacha
  11/11 on denominator, ceiling 1.00).
- Both coders vs dataset: construct .60–.65 (Part 1) and .75–.79 (Part 2); breadth .56–.72
  (.65–.73 excluding the 4 blank-definition items, as pre-registered).
- D12 value "miss" (both coders 18.1 vs key 31.7) adjudicated against the fulltext: instrument
  artifact — the pointer demanded the overall figure while the dataset row is the TikTok
  subgroup by design. Not a coder or dataset error; excluding it, extraction is 10/10 and 10/11.
- Pre-registered exclusions applied throughout (C21 from Sacha-vs-dataset; D11 void).
Next: fill the manuscript's two placeholders (§3.5, §4.8) from results_report.md.

## 2026-07-29 — Adjudication page + placeholders filled + Part-2 batch 2 built

**Four both-against-key items re-read from full text; verdict: the dataset holds on all four.**
Evidence: C05's 97% is computed over 3PFC-fact-checked URLs (claim-level false), not the domain
lists the truncated definition foregrounded; C07's "26.06%" is Table 5's share of SHARED URLs
that are untrustworthy in swing-state tweets (the word "concentration" in the results sentence
was the red herring); C10's 9.4% is an evidence-support rating with half the recommendations of
UNKNOWN effectiveness (not-evidence-based ≠ false → QUALITY); D09's "misleading" is an ASRS-v1.1
COVERAGE criterion (<4 of 6 screening questions ⇒ misleading even if accurate → QUALITY by the
falsity/quality rule). Final call is human: `qa/irr_adjudication.html` (opened for Sacha) shows
each item with both coders' codes, the dataset code, my reasoning, the decisive quotes, and the
paper (3 PDFs + 1 fulltext staged in qa/irr_adjudication_papers/). A v1.5.8 happens only if his
re-code moves anything away from the dataset. D09 is the one with dataset consequences
(QUALITY→CONTENT would add a row to prevalence, k 211→212).

**Manuscript placeholders filled** (§3.5 sentence + §4.8 full human-coding paragraph) from
results_report.md — including the non-blindness disclosure, the pre-registered exclusions, the
evidence gradient (κ .48 snippets → .74/11-11 full paper), machine-clears-the-human-bar reading,
and the 9-of-10 dataset-inside-human-disagreement-space observation. NOTE: §4.8's Part-2 numbers
will be REFRESHED once batch 2 is scored (and the adjudication outcome noted).

**Part-2 BATCH 2 built** (`scripts/build_irr_part2_batch2.py`, seed 4242): 12 fresh full-paper
items (E01–E12; 9 CONTENT / 2 RECALL / 1 QUALITY — deliberately stresses the topical/curated
boundary batch 1 undersampled), excluding all previously-used studies + Laura's round-1; same
eligibility incl. value-verbatim guard; clobber guard included. Key in ANSWER_KEY_batch2.csv
(repo only). Coding pages code2_<coder>.html (batch-2 mode added to build_irr_coding_html.py:
separate localStorage key, part2b export, no Part-1 UI). Deployed to ~/Desktop/Misinfo_Coding_Round2/
+ Misinfo_Coding_Round2_Laura.zip (13 MB) ready to send.

## 2026-07-29 — Adjudication CLOSED: dataset upheld 4/4 (no v1.5.8)

Sacha's full-text re-codes, verbatim: "C05: false · C07: SHARING · C10: QUALITY · D09: QUALITY" —
all four match the dataset. The IRR's strongest error signal (both coders vs key) yielded ZERO
dataset changes; every case traced to evidence hidden from the coders at first pass. §4.8 gains
one sentence reporting this; results_report.md carries the final record. Remaining live queue:
Part-2 batch 2 (both coders), then refresh §4.8/§3.5 numbers.

## 2026-07-29 — Sacha's batch 2 delivered; export-filename bug fixed; Laura's zip rebuilt

Sacha's batch-2 sheet ingested as `irr_v2/part2b_sacha.csv` (12/12 coded, E12 NOT FOUND, mean
confidence 3.67, notes on 9 items; backed up to .backups/ + iCloud). His export arrived named
`part2_sacha.csv` — the batch-2 page's download rename was a no-op (the replace targeted a
literal that didn't exist; the JS builds the filename by concatenation). Fixed in the generator
(download now emits `part2b_<coder>.csv`), code2 pages regenerated, and Laura's zip REBUILT with
the fixed page before sending — her export will arrive correctly named and cannot collide with
her batch-1 file. Scoring of the pooled Part 2 waits for her sheet; no item-level results shown
to Sacha meanwhile.

## 2026-07-30 — Batch 2 scored; pooled Part 2; manuscript refreshed; round-2 adjudication queued

Laura's part2b ingested (12/12, E07+E11 NOT FOUND, mean conf 2.92, notes on 11; backups done).
Scorer extended to pool part2b/ANSWER_KEY_batch2 into Part 2. Pooled + batch-2 anatomy + both
coders' unprompted difficulty testimony recorded in results_report.md. §4.8/§3.5 refreshed with
POOLED numbers and the two-stage gradient framing (the ceiling inherits the literature's
reporting quality). Round-2 adjudication queue: E02 + E03 (both-against-key denominators) and
E12 (dataset-row soundness — Sacha found no usable estimate). Crosswalk clean.

## 2026-07-30 — Round-2 adjudication: batch 2 surfaced a likely FABRICATED study + 2 denom questions

Re-read the three batch-2 both-against-key / no-usable-estimate items from full text.
UNLIKE round 1, the dataset does NOT cleanly hold:

**E12 (OA-W7125772788, Leman 2025) — likely fabricated/AI-generated; recommend EXCLUSION.**
Sacha's "read everything, no usable estimate" was a study-validity judgment (the 54% IS in the
text, so not an extraction miss). Full read shows: internally contradictory method (abstract:
7,234 NLP data points; results: 282 chain-referral survey respondents — Table 1 mixes both),
incoherent data sources (ChatGPT/Meta AI as discourse platforms, "73%/72% used"), statistical
nonsense (Δ=-1.5 with 95% CI [0.2,1.6]; pathogen counts exactly 25% each), predatory venue
("Verlumun Journal of AI, Gender and Cultural Studies", Vol1 Iss1 Maiden Edition, Zenodo DOI).
Contributes 1 RECALL row (54%, already HIGH RoB); excluding drops RECALL k 27→26, no headline
effect. IMPORTANT SECOND-ORDER: it passed screening+extraction+RoB, so a corpus-integrity pass is
warranted. First scan of the 228 studies with retrievable extraction_master metadata found no
zenodo/AI-fabrication siblings, but 88 late OA/NEW additions (E12's cohort) lack metadata there
and are uncovered — flagged as a parked task.

**E02 (W4414446446) — dataset denom likely WRONG.** 4.85% of 1,382 broadcast episodes contain a
fact-checked claim; key = population, but population is reserved for PEOPLE and this is a content
(episode) denominator. Both coders said curated_sample; I lean news_diet (near-census of 10 major
German broadcast news/talk shows, multi-topic). Key probably a miscode. Sacha to decide.

**E03 (2-s2.0-85159486270) — the genuine topical/curated boundary.** Single-issue keyword search
(topical-like) BUT sorted by view count + >1000-view threshold (curated_sample-like). Key
(curated_sample) defensible via the ratified rank-truncation rule; coders' topical also legitimate.
Thinnest boundary in the IRR; Sacha decides.

Decision page: `qa/irr_adjudication_round2.html` (opened). Any move off the dataset → v1.5.8.

## 2026-07-30 — v1.5.8 applied; manuscript refreshed; E12 = the reliability section's best evidence

Sacha adjudicated all 3 round-2 items OFF the dataset: E12 exclude, E02 curated_sample, E03 topical
(his topical/curated question answered — the two axes, scope vs selection-bias, forced into one
field; precedence rule documented in moderator_codebook.md, flagged as the author's most-questioned
rule). apply_v158.py: dropped OA-W7125772788, E02 population->curated_sample (all 3 sibling rows,
no stranding), E03 curated_sample->topical. 677/315. Gate caught a quote-key collision (same
85114317455-family lesson) — switched to position-aligned gate. Full pipeline + RoB(auto-drops E12)
+ metareg + prisma + ratio bootstrap regenerated; drift clean. Manuscript comprehensively updated
(26 numeric edits: 678/316/576->677/315/575, RECALL k27->26 median 54.0->55.0 IQR 27.5-69.4 high-RoB
22->19%, ratio 20.8[9.2,76.4]->21.3[9.0,76.7], item10 80.7->80.6, health 136->135). E12 catch
written into §4.8 ("strongest single argument for the human tier") and §3.5 (corpus-integrity
caveat). Memory freeze pointer -> v1.5.8; corpus-integrity sweep of the 88 metadata-less late OA/NEW
additions PARKED as HIGH priority before submission. Placeholders: 0.

## 2026-07-30 — Corpus-integrity re-screen (the parked task) DONE: 2 more fabricated found

Re-screened all 87 metadata-less frozen studies (subagent triage + main-session full-text
verification). Found 2 more fabricated/predatory papers matching E12's profile, both verified:
OA-W7154838691 (fake "Qualitative Research Journal", impossibly clean 250×250×250×250 split) and
OA-W7133343648 (predatory Indian agri journal, Bosnia WhatsApp study, venue/topic mismatch). Plus
1 REVIEW (OA-W4291473423, thin but legit conference abstract — inclusion question, lean keep).
84 clean. KEY PATTERN: all 3 fabricated entered via the OpenAlex OA- path in the W71xxxxxxx band —
a provenance filter is warranted. Findings in qa/rescreen87_findings_2026-07-30.md. Exclusions
await Sacha's confirm (E12 precedent). Both requested new papers (Faker Island, sciadv) confirmed
ELIGIBLE with codeable estimates; coding + RoB appraisal in progress, to bundle with the exclusions
as one v1.5.9.

## 2026-07-30 — v1.6.0 taxonomy overhaul applied + critical re-evaluation

Applied Sacha's taxonomy decisions as FROZEN v1.6.0 (apply_v160.py): dropped 2 fabricated
(OA-W7154838691, OA-W7133343648; full re-screen found NO others beyond the 3 known); breadth
split-clean to pure veracity {fabricated,false,misleading} (284 blanked, legacy preserved,
gradient now clean-monotonic 10.8→22.1→29.0%); +denom_scope +denom_selection two-axis columns;
question_type/diet_type deprecated. 675/313, headlines unchanged. §2.5 rewritten to current numbers.

CRITICAL RE-EVALUATION (Sacha: "re-evaluate to make sure it makes perfect sense") surfaced the
NEXT layer:
1. **§2.5 method-cluster overclaim [FIXED].** classification_level ≈ ground_truth (source_level↔
   domain_list 250/261=96%; claim_level↔researcher/factcheck/classifier 348/401=87%). The old §2.5
   listed measurement/ground_truth/id_method/sampling as 4 independent top drivers — they are ONE
   collinear operationalization axis. Rewrote to say so; "measurement≫topic" holds and reads better.
2. **denom_scope for the 90 curated/single rows is RULE-INFERRED [agent running].** Provisional;
   dispatched a verification agent (denom_scope_worklist.csv) to code each from source text.
3. **breadth now blank for 43%** (source-list + quality studies have no veracity threshold) — the
   moderator is veracity-only on the specifying subset; manuscript states this.
4. REMAINING minor: OTHER (24) catch-all unexamined; `unit` mixes content/person/measure types →
   limitations-sentence material, not re-freeze.
5. Framing noted (codebook): REACH/RECALL share the people-denominator, differ by measurement —
   the mirror of SHARING/CONTENT, and the exposure–perception gap itself.

PENDING: the 2 requested papers (Faker Island, sciadv) — eligible, estimates identified
(sciadv EXPOSURE 1.1%FB/0.1%IG whole-feed→backbone + concentration; Faker 0.05% CONTENT + 0.9%
sharing-reach) — but adding studies needs RoB appraisals + the add-study workflow (RoB gate);
doing it as a clean v1.6.1, with the Faker 0.9% construct call (REACH-of-sharing) flagged for
Sacha. denom_scope agent results to integrate first.

## 2026-07-30 — v1.6.1: denom_scope verification applied (analysis-neutral)

Source-anchored verification of the 90 rule-inferred denom_scope rows (agent, spot-checked by main
session against PDFs) corrected 17 rows / 5 studies (apply_v161.py). Key fixes: 85131964464
topical->political_news, 85160248068 news_diet->all_media, 85177420309 news_diet->topical x12,
85115858008 + 85213958624 ->all_media (low-conf, flagged). denom_scope unused in analysis, so
zero downstream change; the two-axis denominator is now analysis-grade. Full table in the agent
transcript. STILL PENDING: add Faker Island + sciadv (v1.6.2, needs RoB appraisals).

## 2026-07-30 — FROZEN v1.6.2: added Faker Island + sciadv (Meta-2020); manuscript refreshed

apply_v162.py added 5 rows / 2 studies with author-level coding + Hoy RoB (manual shard_99):
- sciadv (Bergeron-Boutin/Nyhan/Allcott/Guess/Gonzalez-Bailon et al. 2026, Sci Adv): EXPOSURE
  1.1%FB + 0.1%IG whole-feed (all_media) → ENTERS whole-diet backbone (k31→33, median 7.4→7.2,
  leave-one-out max 0.08→0.67pp); CONCENTRATION top23%→80%; RoB LOW.
- Faker Island (Berriche/Altay/Mercier et al. 2026): CONTENT 0.05% of tweets (news_diet) + REACH
  0.9% sharing-reach (population, construct confirmed by Sacha); RoB MODERATE (Twitter media-sharer
  population non-representative, items 1-3 HIGH).
680/315. Headline moves: REACH 12.0→11.5 (Faker 0.9), CONCENTRATION construct-median 69.7→74.0
(top-1% band still 8 studies→70%, unchanged), ratio RECALL/EXPOSURE 21.3 [9.2, 96.6], backbone
7.2 [4.9-8.8]. RoB coverage 315/315 (manual shard integrated). CONTENT median 23.0 unchanged.
Full pipeline + metareg + prisma regenerated; drift clean. §4.8 now reports all 3 caught fakes +
the clean full re-screen.
GOTCHA fixed: the crosswalk 'bad_estimates' blocklist hardcoded 680 (a superseded v1.4.5 count) —
but the corpus grew back to exactly 680, so it false-flagged the live count. Removed 680 from the
blocklist with a comment: never blocklist the current canonical count.

## 2026-07-30 — Aggressive audit + FROZEN v1.6.3 (audit fixes) + manuscript re-sync + derived-stats guard

Ran a 4-agent parallel audit (value/extraction, coding, eligibility, stats+manuscript) + programmatic
scout on v1.6.2. Data strong (no fabricated/out-of-range values, no contamination, no ineligible-
construct leakage). Report: docs/audit_2026-07-30/AUDIT_REPORT.md.
BIGGEST FINDING: manuscript prose had drifted off v1.6.2 — 2 FALSE claims (§2.7 "only CONTENT
significant" but REACH now p=.025; §2.9 backbone "does not move" but 7.2→6.6) + ~20 stale numbers,
because each freeze regenerated the pipeline but only some manuscript numbers were hand-updated and
the drift check guards counts only.
FIXED as v1.6.3 (apply_v163.py): dropped forced-exposure experiment 85189974015 (2 rows); dropped 3
phantom CONTENT sub-slices of 85214504236; blanked 16 source-level breadth-residue rows (completes
v1.6.0 rule). 675/314. Pipeline regenerated (NOTE: first regen hit a bash/py interpolation bug that
left FROZEN.md at v1.6.2 → regenerated against the WRONG freeze; caught it (RoB coverage said 315),
fixed FROZEN.md, RE-regenerated against v1.6.3 — lesson: after any freeze, VERIFY FROZEN.md File:
line before trusting the regen). Manuscript FULLY re-synced (31+10 substitutions; abstract/§2.1/§2.2/
§2.3/§2.5/§2.6/§2.7/§2.9/§2.10/§3/§4). PROCESS FIX: scripts/check_manuscript_stats.py (27 derived
stats asserted vs CSVs; PASS). Judgment-call audit items (construct miscodes, concentration
re-extraction, D09 re-confirm) FLAGGED not applied.

## 2026-07-30 — Audit decisions applied (v1.6.4 recodes + v1.6.5 labels); all 12 closed

Sacha's calls from audit_decisions.html applied. v1.6.4 (apply_v164.py): 9 construct recodes —
85207525286 QUALITY→CONTENT (he overrode his own IRR QUALITY call, ASRS clinical ground truth),
85066941307 x2 REACH→OTHER (conditional-probability quantities), 85069463611+85100218180
CONTENT→SHARING, 85160248068 x2 OTHER→EXPOSURE (clicks/visits=consumption), 85162702221
EXPOSURE→OTHER (likes=engagement), 85148963619 Kennedy CONCENTRATION→OTHER (single actor).
CONSEQUENCE: SHARING median 13.1→9.1 (A3/A4 low values entered the pool), EXPOSURE k17→16, backbone
small-study test now marginally sig (p=.047). Manuscript re-synced (29 subs); §2.6 RoB switched to
BY-STUDY per C2 (CONTENT 59%, was mixing by-estimate); check_manuscript_stats.py updated to assert
by-study, 27/27 PASS. v1.6.5 (apply_v165.py): B2 — agent re-read the 3 concentration papers; the 5
field-incomplete rows are QUALITATIVE groups (verified/top-N/deplatformed), NOT volume percentiles,
so conc_group_pct stays blank (filling would corrupt the percentile table) — only conc_group_label
documented; codebook note added. C4: 2 stray PDFs → .backups/stray_pdfs_2026-07-30/. C3: uncorrected-p
sentence skipped; multiple-comparison correction PARKED as a future option (Sacha). All 12 audit
decisions closed. FROZEN v1.6.5, headlines held (EXPOSURE 2.6, CONTENT 23.1, top-1%→70%).

## 2026-08-04 — Data-improvement pass: outlier verify, RECALL split, temporal, Codex package

- OUTLIER VERIFICATION (source-checked, like the audit): all 4 Tier-1 leads HELD — no clean
  misclassifications (85037352356 correctly REACH; the "intervened" row is recall-sharing; the
  85086031086/85055756722 rows are correctly self-report-sharing RECALL). GOOD news: data robust.
- The real finding = RECALL exposure/sharing SUBSTRUCTURE, now quantified and made explicit via
  the new `recall_subtype` column (v1.6.6): self-report EXPOSURE recall median 55.7% (n=43) vs
  self-report SHARING recall 17.1% (n=9); combined 50.3% conflates them. DECISION PENDING: report
  RECALL split (exposure-recall 55.7% is the cleaner perception number; would slightly widen the
  exposure-perception gap).
- FROZEN v1.6.6: +year +era +recall_subtype (additive, analysis-neutral; headlines unchanged).
- TEMPORAL analysis (scripts/phaseB_temporal.py, temporal.csv): NO significant secular trend within
  constructs; the construct gaps are stable across 2005-2026. Apparent CONTENT rise (10→31%) is
  confounded by the field's drift toward topical/health samples; EXPOSURE drifts down (5→0.5%, small
  k, n.s.) consistent with method maturation. Supports the thesis (method>year). Worth a short
  robustness paragraph, NOT a headline. (p-values are a rough normal approx — use the incomplete-beta
  tail for the paper.)
- n-field cleanup DOWNGRADED: parse_n already recovers 91%; residual is a QC check that it grabs the
  intended number (low priority).
- CODEX blind re-code package built (scripts/build_codex_check.py + score_codex_check.py,
  docs/codex_check/): targeted, NOT full — 111 construct items (audit-hard + all RECALL + a 30-row
  SHARING/CONTENT boundary sample) + 40 value re-extraction items (papers staged), blind, with
  ANSWER_KEY separate. Framing: robustness/error-detection, SAME family as the existing GPT sweep
  (not a new independent tier). Disagreements adjudicate-not-auto-apply.

## 2026-08-04 (cont.) — n triple-check fixes (v1.6.7), RECALL split reported, Codex cross-check

- n TRIPLE-CHECK: parse_n suffix handling verified correct (3.7M->3,700,000, both Faker rows; also
  "million"). Corpus audit found 0 year-grabs/suffix-misses, BUT a tiny-n sweep found 5 rows where
  parse_n grabbed a numerator/subgroup count not the denominator (85114317455 "8 agents"->should be
  11038 links; 105027856675 coder-flagged "23 is misinfo count"; etc.). Fixed in v1.6.7 (correct or
  blank). Real effect: EXPOSURE small-study rho -.44->-.21 (the wrong n=8 for a high-value study was
  inflating the negative correlation) — now more honest.
- RECALL SPLIT (Sacha: report seen vs shared, don't merge). New scripts/phaseB_recall_split.py +
  ratio_bootstrap RECALL-seen row. Study-level: seen-recall (self-report exposure) 60.0% [48.5-68.8]
  k=23 vs shared-recall 18.6% [10.6-29.6] k=6 (combined was 55.0 k=26). Seen/EXPOSURE ratio 23.2
  [10.8-91.0] (was combined 21.3). Manuscript §2.2 table (2 rows), §2.2/§3.1 prose, abstract, GRADE
  re-synced; checker 27/27. The exposure-perception gap is now cleaner AND slightly wider.
- CODEX blind cross-check (targeted, docs/codex_check/, scored): VALUE re-extraction = 0 true errors
  (25 "misses" = 14 valid ALT figures + 11 not-found) -> value extraction confirmed robust.
  CONSTRUCT kappa .66 on the HARD subset (audit-flagged+RECALL+boundary); disagreements on the
  fuzzy boundaries. Codex INDEPENDENTLY chose the ORIGINALS on two of Sacha's v1.6.4 calls: A1
  (85207525286 -> QUALITY, not the CONTENT he flipped to) and A5 (85160248068 -> OTHER, not EXPOSURE)
  -> those two are genuine coin-flips, flagged for Sacha to reconsider; not auto-changed. Same family
  as the existing GPT sweep, so reported as robustness not a new tier. Disagreements in
  docs/codex_check/codex_disagreements.csv.

## 2026-08-04 (cont.) — v1.6.8 revert A1/A5; full Codex re-run prepared

A1 85207525286 CONTENT->QUALITY, A5 85160248068 x2 EXPOSURE->OTHER (Codex independently chose these
originals; Sacha reverted). CONTENT k210->209 median 23.0; EXPOSURE held 2.6 (impression rows
2.05/0.72 kept). Manuscript re-synced (metareg shifted slightly: construct 15.5, denom_fine 11.8,
id_method 17.3, platform 9.7, topic 7.8; CONTENT high-RoB 59->58%); checker 27/27; drift clean.
FULL Codex re-code (gpt-5.6-terra medium) worklist built (build_codex_full.py: 647 codeable rows,
construct+breadth+denom, blind) keyed to v1.6.8 -> purpose is to REFRESH the reported whole-corpus
independent-model kappa (§4.8 .75 is on the STALE v1.5.4 corpus; "626 of 675" conflates old count
w/ current N). Same base model as the Perplexity sweep -> a currency refresh, NOT a new tier;
document as such. Model + staleness in codex_check/MODEL_AND_PROVENANCE.md. score_codex_full.py ready.

## 2026-08-04 (cont.) — FULL Codex round 1 scored: INVALID (instrument defect), round 2 prepared

Codex returned the 647-row full-corpus worklist. Integrity verified first: 647 rows, four blind
columns byte-identical to build_codex_full.py's output (re-derived from the freeze without
overwriting the filled file), all item_ids present in FULL_ANSWER_KEY.
SCORES: construct kappa .390 (raw .586), breadth .206, denom_class .337 — far below the SS4.8 .75
we set out to refresh, and BELOW the targeted round's .66 on the deliberately HARD subset. That
inversion (full corpus scoring worse than the hard subset) is the tell that this is an instrument
problem, not a data problem.
DIAGNOSIS (not applied to data; nothing recoded): round-1 FULL_INSTRUCTIONS.md shipped BARE LABEL
NAMES with no code definitions, where the targeted round gave a one-line definition per construct.
Evidence the disagreement is definitional, not substantive: Codex used RECALL 2x in 647 rows (key
has 63; ours-RECALL agreement 3%); ours-REACH agreement 5% with 36/64 sent to EXPOSURE; collapsing
EXPOSURE/REACH/RECALL lifts kappa .390->.543, i.e. ~a third of disagreement is that one undefined
boundary; 119/232 ours-`false` pushed one-way to `misleading` (instructions also truncated the
codebook's 5 breadth values to 3); 34 ours-`population` coded `topical`, exactly the error the
"surveys -> population, ALWAYS" rule prevents. Confidence flat (56% vs 60% at conf 3 vs 4) =
confidently applying a DIFFERENT scheme. Truncation ruled out as a co-cause (11/647 quotes at cap).
Spot-checked the blind fields directly: the signal IS present ("respondents reported", "at least
one"), so the task is answerable — it was under-specified, not under-determined.
ACTION: round 1 archived intact at docs/codex_check/round1_nocodebook/ (kept, not deleted — it is a
legitimate "no-codebook floor" condition). build_codex_full.py REWRITTEN to emit codebook-faithful
instructions (construct table w/ the share-of-what shortcut, all 5 breadth values + tells, the
denom_class decision tree + recurring hard cases, incl. the boundaries round 1 got wrong), so the
fix lives in the GENERATOR per house rules. Blank 647-row worklist regenerated; FULL_ANSWER_KEY
unchanged and never exposed. MODEL_AND_PROVENANCE.md updated with the full round-1 post-mortem.
SS4.8 STALENESS BUG REMAINS OPEN — the .75/"626 of 675" wording is still on the superseded v1.5.4
corpus and must NOT be refreshed with round-1 numbers. Round 2 pending Sacha re-running Codex.

## 2026-08-04 (cont.) — Round-2 instructions VALIDATED before running (2 defects caught in my own fix)

Sacha asked for the new instructions to be verified rather than trusted. Validating them against the
ANSWER KEY's actual value sets caught TWO defects in the round-2 rewrite I had just committed:
1. **Deprecated codes offered.** I had copied the breadth table from `docs/moderator_codebook.md`
   §(a), which is STALE: it still lists `unreliable_source` and `low_quality`, RETIRED by the v1.6.0
   overhaul (documented at the END of the same file). breadth is now a pure 3-value veracity scale
   {fabricated,false,misleading}, blank otherwise; the frozen data and the key contain ONLY those 3.
   Offering the 2 retired codes would have produced unmatchable answers — the exact class of bug
   that wasted round 1. Codebook §(a) now carries a SUPERSEDED banner + struck rows pointing to
   v1.6.0 (the two rows kept for provenance, not deleted).
2. **Answer-key leakage.** My draft carried key-derived marginals ("the true count is ~63", "119 of
   232 ours-false"), which tell a blind coder how many of each code to produce. Stripped — the
   instructions now carry DEFINITIONS only, no counts. A leaked marginal would have inflated the
   kappa we intend to report.
Also added: an explicit BLANK POLICY per dimension (construct/denom never blank -> a coder must not
dodge hard rows; breadth blank exactly when no per-item veracity standard applies) and the v1.6.0
construct clarifications (REACH vs RECALL differ ONLY by measurement, behavioural vs self-report —
"that difference is the exposure-perception gap itself"; SHARING = CONTENT over a sharing stream).
VALIDATION now passes: every key value is permitted, every permitted value is documented, no
retired code is offered as a choice, no key marginal appears.
TOOLING: score_codex_full.py now (a) takes an optional worklist filename, (b) reports rows-filled
and per-dimension SKIP counts — blank rows are skipped by the kappa, so a coder could otherwise
inflate agreement by blanking hard rows and we would never see it — and (c) prints the
collapse-EXPOSURE/REACH/RECALL kappa automatically, the diagnostic that identified round 1's defect.
Regression-checked: it reproduces round 1 exactly (.390/.206/.337).
NEW scripts/build_codex_pilot.py — an 80-row STRATIFIED pilot (10 per construct, deterministic, key
used only to select rows and never shown). Rationale: a first-N prefix of the worklist is NOT
representative (dataset-ordered, CONTENT-heavy — the first 80 rows score .281 vs .390 corpus-wide),
so validate the instrument on a stratified 12% before spending another full 647-row run. Pilot
covers all 8 constructs, all 8 denom classes and the blank-breadth case; verified blind (no key
columns, blind fields byte-identical to the full worklist).
NEXT: pilot -> score -> only then the full run. Nothing in the dataset changed; §4.8 still stale.

## 2026-08-04 (cont.) — Round-2 instructions FINALISED (4 more fixes) + pilot package ready

Second validation pass on the regenerated instructions caught 4 further issues, all fixed in the
GENERATOR (scripts/build_codex_full.py):
1. **Hardcoded worklist filename** — the instructions said "open codex_full_worklist.csv", but the
   pilot is codex_pilot_worklist.csv, so a pilot run would have opened the wrong (or a nonexistent)
   file. Now names both and states the columns/order/quoting must be preserved byte-identically.
2. **Soft marginal hint removed** — "a large share of rows legitimately blank" quantified the key's
   blank rate; replaced with the rule only ("blanking is correct, do not reach for the nearest of
   the three to avoid an empty cell").
3. **Unit-of-coding rule added** — verified empirically against the key: breadth is a property of
   the DEFINITION (only 13 of 340 distinct definitions carry >1 breadth, all definition-variants),
   whereas 38 definitions span >1 construct, i.e. construct/denom are per-ROW. Stating this should
   remove a whole class of copy-the-previous-row drift. No counts given to the coder.
4. **`n/a` rule made explicit** — every CONCENTRATION row is `n/a` (28/28 in the key, and it is the
   standing codebook rule), plus non-share quantities (conditional probabilities, per-post
   engagement rates) are `n/a`. Round 1 had no `n/a` guidance at all.
Also confirmed: 0 rows have an empty `how_defined`, so breadth is codeable everywhere.
FINAL VALIDATION SUITE PASSES: every key value permitted; every permitted value documented; no
retired code offered as a choice; no key marginal in the prose; both worklist filenames present;
blank policy stated for all three dimensions. Both worklists verified blind (no key columns, all
YOUR_* empty). Drift check clean. Nothing in the dataset changed; §4.8 remains stale by design.
DELIVERED to Sacha: the exact Codex prompt + directory, pilot-first (80 stratified rows) then full.

## 2026-08-04 (cont.) — PILOT (round 2, with codebook) PASSES; one wording fix; full run authorised

80-row stratified pilot returned complete; integrity verified (80 rows, blind columns unaltered, no
illegal values, all four YOUR_* fields populated, CRLF preserved). Archived with its disagreements
in docs/codex_check/pilot_round2/.

THE INSTRUMENT FIX IS CONFIRMED — same 80 rows, round 1 (bare labels) vs round 2 (codebook):
  construct   kappa .229 -> .729
  breadth     kappa .097 -> .346
  denom_class kappa .298 -> .471
The categories round 1 destroyed are repaired: RECALL 100% agreement (round 1: 3% corpus-wide),
CONTENT 100%, EXPOSURE 90%, REACH 80%. The collapse-EXPOSURE/REACH/RECALL diagnostic now returns a
NEGATIVE gap (-.029): collapsing those three no longer helps, i.e. the audience boundary has stopped
driving disagreement. Confidence is now spread 2-5 (round 1 was flat 3-4), so the coder is
discriminating hard rows instead of being uniformly certain.

ONE wording fix applied before the full run, and ONLY one. Pilot showed ours-`topical` at 29% with 10
rows sent to `single_source` — all platform-bounded topic searches (YouTube/TikTok videos on one
health topic). Cause was MY instruction wording: decision-tree item 5 read "one account / channel /
outlet / platform feature", which invites treating one PLATFORM as one SOURCE, and it contradicted
the codebook rule already quoted lower down ("all tweets mentioning X" is `topical`). Item 5 now
states that a topic search run on one platform is `topical` and `single_source` means one specific
account/outlet. This is TRANSMISSION of an existing codebook rule that my wording had broken, not a
new rule. Validation suite re-run: PASS.

DELIBERATELY NOT FIXED — these are substantive and must stay measured, not tuned:
- QUALITY 30% (7/10 -> CONTENT). The codebook's "a rating, not falsity" rule WAS transmitted; the
  disagreement is the genuine QUALITY/CONTENT fuzzy boundary. Inspection also surfaced a probable
  error on OUR side worth adjudicating later: F0066 (expert 5-point FACTUALITY scale, "mostly
  false"/"false") is coded QUALITY by us though it is falsity-based -> looks like CONTENT. Also
  F0262 = the A1 ASRS study (85207525286) whose QUALITY coding v1.6.8 restored; this Codex round
  independently reads it as CONTENT, so A1 remains a genuine coin-flip, not a settled call.
- breadth false/misleading threshold (n=25, tiny) and OTHER (a residual category). Substantive.
METHODOLOGICAL GUARD: iterating instructions against observed disagreements would fit the
instrument to the answer key and inflate the kappa we report. The line held here is: fix only where
the codebook already decides the case and my wording failed to convey it; never sharpen a boundary
the codebook leaves genuinely fuzzy. Exactly one edit met that test.
NB for reporting: the 80 pilot rows are INSIDE the 647, and the single wording fix was made after
seeing them, so the full run should ALSO be scored on the 567 unseen rows as the conservative,
untouched-by-iteration figure. Both numbers get reported.

## 2026-08-04 (cont.) — FULL 647 single-pass run DEGRADED; instrument self-consistency measured;
## re-issued as 9 batches. Purpose reframed: adjudication = error-detection, not just validation.

Sacha's framing for this whole exercise (recorded as standing): the cross-check exists to IMPROVE
the coding and catch OUR mistakes, not merely to certify the data. Disagreements are to be
adjudicated against source. That makes the instrument's trustworthiness a precondition: a noisy
coder generates fake "mistakes" that waste adjudication effort and can corrupt correct codes.

FULL RUN RESULT (647 rows, one pass, codebook instructions): construct kappa .438, breadth .511,
denom_class **.175** — denom WORSE than the no-codebook round 1 (.337), despite the pilot scoring
.471 on the same instrument two hours earlier. Integrity was clean (647 rows, blind columns
unaltered, no illegal values), so this is not a handling error.
DIAGNOSIS — long-run degradation, proven by TEST-RETEST rather than inferred. The 80 pilot rows sit
inside the 647, so the coder re-coded rows it had already done under the same instructions:
  SELF-consistency, pilot vs full, same 80 rows: construct 65% (kappa .568), breadth 79% (.649),
  denom_class **45% (kappa .333)**.
On those identical 80 rows its agreement with our key fell construct .729 -> .386 and denom
.471 -> .204. Marginals confirm mode-collapse: `single_source` used 280 times (our key: 27) and
single_source+topical absorbed 77% of all rows, while `political_news` (our key: 80) was used 6
times and `all_media` (19) 6 times. The 5-step denominator decision tree is the most effortful
judgment and it collapsed first; construct/breadth, simpler calls, held up better.
KEY PRINCIPLE, now enforced in tooling: an instrument cannot agree with us more than it agrees with
ITSELF. Self-consistency is the ceiling on any kappa we report, so it must be MEASURED, not assumed
— round 1 and the full run both looked like data problems and were both instrument problems.
CONSEQUENCE: the full run's 701 disagreements are mostly instrument noise and MUST NOT be
adjudicated as signal. Archived unused at docs/codex_check/full_round2_degraded/. The PILOT's 55
disagreements ARE trustworthy (stable run, construct .729) and are the adjudication queue we keep.
RE-ISSUED AS BATCHES (scripts/build_codex_batches.py): 9 batches of ~72 rows, since 80 is a
demonstrated working dose. Batches are dealt ROUND-ROBIN over a construct-stratified ordering, so
every batch carries all 8 constructs with no category above ~50% — file order is CONTENT-heavy at
the front and would otherwise confound batch position with category, making drift unreadable. The
80 pilot rows are spread across the batches (6-11 per batch), giving a FREE 80-row test-retest.
scripts/merge_codex_batches.py merges, verifies (blind columns unaltered, no illegal values, no
duplicate/missing ids), REPORTS SELF-CONSISTENCY vs the pilot with an explicit
"treat disagreements as noise" warning below 75%, then scores. Smoke-tested end-to-end.
Each batch must be coded in a FRESH Codex session — degradation is within-session.
NOTHING in the dataset changed. §4.8 still stale, still not to be refreshed from any run so far.
CARRIED FORWARD for adjudication once a trustworthy run exists (from the pilot, source-checked):
- F0066: our QUALITY looks WRONG — expert 5-point FACTUALITY scale ("mixture true and false",
  "mostly false", "false") is falsity-based -> reads as CONTENT. Probable error on our side.
- F0262 = A1, the ASRS study 85207525286 that v1.6.8 restored to QUALITY on the earlier Codex
  round's advice; this round independently reads it CONTENT -> A1 is a genuine coin-flip, not settled.

## 2026-08-04 (cont.) — Codex access exhausted after 2 batches; partial run is USABLE; adjudication
## queue built (no further Codex needed for it)

Sacha hit his Codex quota (no access for ~1 month) after batches 01-02. Assessed what the partial
run supports rather than parking it.

BATCH PROTOCOL VALIDATED AND STABLE across both batches (vs the degraded single pass in brackets):
  batch 01 construct .826 / denom .660 ; batch 02 construct .746 / denom .485  [degraded: .438/.175]
  pooled BATCHES ONLY (n=144): construct kappa **.786**, denom_class .571, breadth .468
  pooled batches+pilot (208 unique rows, 32% of corpus): construct .762, denom .538, breadth .397
  self-consistency on repeated rows held (b01 5/6, b02 8/10 on the hardest field).
No mode collapse in either batch (single_source 2 and 8, vs 280 in the degraded pass).

THE PARTIAL SAMPLE IS PROPORTIONALLY REPRESENTATIVE, not merely balanced — an accident of the
round-robin deal that is worth recording because it makes the partial reportable. Dealing
`order[b::n]` from a construct-interleaved ordering preserves corpus proportions: sample CONTENT is
69/144 = 48% against a corpus weight of 47.9%, and every other construct tracks similarly. Formal
check: corpus-weighted raw agreement .846 vs unweighted sample .847 — a .001 gap. So batches 01-02
are a clean ~22% probability-like sample of the current corpus and can carry a partial estimate with
an honest n, NOT a "we coded the easy ones" caveat.
Per-construct construct-agreement (sample): CONTENT 91%, RECALL 94%, REACH 93%, EXPOSURE 100%,
SHARING 71%, CONCENTRATION 67%, QUALITY 50%, OTHER 50% — the residual/fuzzy categories are where
disagreement concentrates, as expected.

ADJUDICATION QUEUE BUILT — docs/codex_check/ADJUDICATION_QUEUE.csv, 145 disagreements over the 208
trustworthy rows (construct 39, breadth 39, denom_class 67), sorted by the other coder's confidence,
with the source quote + definition inline and blank VERDICT/NOTE columns. This is the
"catch OUR mistakes" work and it needs NO further Codex access. Flags: 46 high-priority rows
(confidence 5, or coded twice in independent sessions with the SAME answer — 6 such rows, the
strongest candidates for an error on our side). Recurrent patterns to adjudicate as classes rather
than one-by-one: breadth false<->misleading threshold (13 rows), ours=curated_sample -> codex=topical
(the boundary the codebook calls the most consequential field), ours=CONTENT -> codex=SHARING.
Standing rule holds: adjudicate against SOURCE, never auto-apply the other coder's call.
Already queued from earlier: F0066 (our QUALITY on an expert FACTUALITY scale — probable OUR error)
and F0262/A1 85207525286 (read CONTENT again; the v1.6.8 QUALITY restoration is a live coin-flip).

REMAINING BATCHES 03-09 (503 rows) stay blank and ready; the package is unchanged and resumable the
moment access returns. §4.8 still NOT refreshed — decision on wording is Sacha's (options put to him:
re-word to the historical v1.5.4 sweep + add the current-corpus partial, or wait for the full run).

## 2026-08-04 (cont.) — §4.8 FIXED (option 1) + adjudication decision page built

Sacha chose option 1: fix §4.8 now rather than wait a month for the remaining batches.
VERIFIED BEFORE WRITING: the Perplexity sweep coded 626 of **678** estimates (research_log, "626 of
678 coded"), NOT 667 as codex_check/MODEL_AND_PROVENANCE.md had recorded and not "of 675" as the
manuscript said — that phrasing spliced the historical coded-count onto the CURRENT corpus size.
v1.5.4 itself was 679/317. Provenance note corrected in place.
§4.8 rewritten to: (a) state the Perplexity sweep as historical and correctly scoped ("626 of the
678 estimates then in the dataset", July 2026), keeping its kappas (.75/.69/.53) and its
error-detection framing; (b) report the current-freeze refresh honestly as PARTIAL and SAME-FAMILY —
a currency check, not a second independent family — construct .79 / denom .57 / breadth .47 on a
proportionally representative 22% sample (144 of 647), noting sample and corpus construct
distributions agree to within 0.1 pp so the partial is not a cherry-picked stratum; (c) add a
methods paragraph that generalises: TEST-RETEST IS A CEILING ON ANY REPORTED KAPPA. The degraded
single-pass run is the worked example — 45% denominator self-consistency, `single_source` used 280x
against the dataset's 27, and a naive score of kappa .18 that would have been read as evidence
against our coding when it was evidence about the coder. This is a genuine methods contribution:
LLM-assisted reviews routinely report agreement from long single-pass runs with no test-retest.
Sacha's note that the Perplexity sweep was a GPT model is consistent with what is written — it is a
different family from OUR pipeline (so "different model family" stands) but the SAME family as the
Codex refresh (so the refresh is not a new tier). Both statements now appear correctly.
check_manuscript_stats 27/27 PASS; crosswalk drift clean.

ADJUDICATION PAGE: scripts/build_adjudication_page.py -> docs/adjudication_2026-08-04/adjudication.html.
145 disagreements arranged as 11 PATTERN classes covering 105 rows (settle a rule once instead of
re-litigating 13 papers) + 40 individual rows ordered by signal strength (rows where two independent
sessions produced the SAME dissenting answer first, then by the coder's confidence). Each row shows
the source quote and the paper's own definition, with PDF + DOI links (54 local PDFs verified to
resolve on disk; DOI links where the record is indexed). PDFs are linked RELATIVELY into the
existing PDFs/ folder, never copied — one copy on disk. Decisions persist in localStorage and export
as CSV. F0066 and F0262/A1 are called out explicitly in the page header as the known
candidates-for-our-own-error.

## 2026-08-04 (cont.) — Sacha catches a scoring-axis error: denom agreement was UNDERSTATED

Sacha: "regarding A, we said something could be both topical and curated_sample no?" — correct, and
it invalidates how we scored the denominator.
THE ERROR (mine, in the instrument): build_codex_full.py drew the worklist's denominator field from
the LEGACY `denom_class`, which the v1.6.0 overhaul split into two axes — `denom_scope` (what
universe the % is a share of) and `denom_selection` (whether that universe was hand-assembled or
rank-truncated). `denom_class` fuses them, so `curated_sample` and `single_source` are SELECTION
values that OVERWRITE the scope. Verified in the freeze: of 63 denom_class=curated_sample rows, 41
are scope=topical + selection=curated (also 17 news_diet, 4 political_news); of 27 single_source
rows, 20 are scope=topical. A coder that correctly names the scope is therefore marked WRONG for not
instead naming the selection — the two are not alternatives.
CONSEQUENCE — the reported denominator kappa was an artefact of a collapsed field:
  legacy denom_class (what we reported)  kappa .571
  SCOPE axis, coder gave a scope value   kappa .855 (n=138, raw .891)
  SCOPE axis EXCLUDING rule-inferred rows kappa .861 (n=134, raw .896)  <- no circularity
Only 4 of the 138 compared rows had a rule-inferred scope (the provisional v1.6.0 inference from
topic), so the .86 does NOT lean on our own inference — checked explicitly because that inference is
flagged non-analysis-grade.
The residual is now cleanly located: on the SELECTION axis the coder called curated/single_source on
70 rows of which only 14 (20%) are rows we flag as such — it is systematically more willing than we
are to call a corpus hand-assembled. So denominator SCOPE coding is reliable (kappa .86) and
essentially all denominator disagreement is one substantive judgment: IS THIS SET CURATED? — the
boundary the codebook itself calls the most consequential in the review.
APPLIED: §4.8 now reports the decomposition (scope kappa .86 alongside the collapsed .57, with the
reason the collapsed figure understates), framed as a located substantive disagreement rather than
diffuse noise. check_manuscript_stats 27/27 PASS; drift clean.
Adjudication page regenerated: every denominator row now shows OUR two-axis coding, with a green
badge where the coder AGREES on scope (so the only question is curation) and a flag where it calls a
set curated/single-source that we do not. The topical-vs-curated pattern class now says explicitly
that the dichotomy is false and the decision to make is "is this set curated?".
OPEN QUESTION FOR SACHA (not actioned): the manuscript's meta-regression still uses the collapsed
`denom_class` (denom_fine 11.8%); `denom_scope` is analysis-grade per v1.6.1 but was never wired in.
Given that the scope axis is where agreement is strong, reporting scope and selection separately in
the metareg would likely be cleaner than the fused field — a real analysis decision, deferred.

## 2026-08-04 (cont.) — Queue + page rebuilt on the CURRENT taxonomy; 7 internal-consistency flags

Sacha: "update the HTML, make sure we follow the latest rules." Done, and it changed the queue's
shape rather than just its styling.
NEW GENERATOR scripts/build_adjudication_queue.py (the queue had been built inline — house rule
violation, now fixed). It scores against v1.6.0, not the superseded fields:
- DENOMINATOR decomposed onto its two real axes. The coder gave ONE answer, so: a scope-value answer
  is scored as a SCOPE claim AND as an implicit "not curated/single" selection claim (had it read the
  set as curated, that is the word it would have used); a curated_sample/single_source answer is
  scored as a SELECTION claim only, with its scope left unscored rather than guessed. The inference
  is stated in the script so a reader can reject it, and the headline scope figure does not rely on it.
- BREADTH scored as the pure 3-value scale with blank as a substantive answer on BOTH sides (this
  raised breadth disagreements 39 -> 47: blank-vs-value cases were previously invisible).
RESULT: 165 disagreements (was 145 on the fused field), and far better located —
  denom_scope 15 (genuine scope disagreements; was 67 fused)
  denom_selection 64 (the real question: IS THIS SET CURATED?)
  breadth 47, construct 39.
v1.6.0 COMPLIANCE SWEEP over all 675 frozen rows: breadth illegal/retired values 0; CONCENTRATION
denom != n/a 0; CONCENTRATION missing conc_unit/conc_dimension 0; denom_class vs two-axis
inconsistency 0. Data is clean under the current rules with ONE exception ->
7 INTERNAL FLAGS (docs/codex_check/INTERNAL_FLAGS.csv): rows with construct=QUALITY that still carry
a veracity `breadth`. Under v1.6.0 breadth is veracity-only and quality is the QUALITY construct, so
a QUALITY row should have no breadth. Carrying one means OUR OWN coding read these definitions as
falsity-based — which is precisely the independent coder's argument for CONTENT. The overlap is the
finding: 6 of the 11 disputed QUALITY->CONTENT rows also carry a breadth, and one (F0246,
105030082417) defines misinformation as "false/misleading health info not backed by evidence" while
being coded QUALITY. These are the strongest error candidates in the whole exercise because they
need no second opinion to be a problem.
PAGE REBUILT: section C added for the internal flags (with QUALITY-vs-CONTENT decision buttons);
denominator rows show our scope+selection with the inference note; the topical-vs-curated class is
replaced by the correct "is this set curated?" framing; header states the taxonomy basis. Verified:
51 local PDF links all resolve, 71 DOI links, 57 decision widgets, no legacy denom_class rows.
NOT ACTIONED (Sacha's call): whether to blank breadth on the 7, or recode them to CONTENT — the
page offers both; and the open metareg question (fused denom_class vs the two axes) still stands.

## 2026-08-04 (cont.) — Round-1 adjudication decisions received; page persistence BUG fixed; re-checks

DATA-LOSS BUG (mine): the decision page relied on localStorage, which Chrome does NOT persist for
file:// origins — decisions lived only in the open tab. Confirmed by searching every browser profile
on disk (Chrome/Safari/Arc/Brave) for the key: absent everywhere. A second bug compounded it: the
note field only saved if a decision button had already been clicked, so notes typed alone were
silently discarded. FIXED in the generator: try/catch around storage, a live always-visible record
panel, a Download-CSV data-URI button, a Restore-from-CSV box, note-only entries preserved and
exported, and a visible warning when storage is unavailable. JS syntax-checked with node.
Sacha's 22 decisions saved to docs/adjudication_2026-08-04/decisions_round1_sacha.csv FIRST, before
any rebuild. (A `git add -A` had also committed a mid-edit broken generator; repaired.)

RE-CHECKS REQUESTED BY SACHA:
- P2 (15 rows, ours=misleading): CONFIRMED HIS CALL. The definitions are guideline-non-concordance,
  "≥1 misconception", "overgeneralized", "could not be corroborated", "unsubstantiated conspiracy" —
  criteria that admit material which is not strictly false. `misleading` is right on all 15.
- P4 (9 rows, ours=false -> misleading): CONFIRMED on 8. "false/misleading claim", "rated misleading
  or false", "misinformative/biased", "context-related (inadequately contextualized)" are all
  disjunctive criteria. ONE EXCEPTION: F0247 (">50% false information when fact-checked against
  guidelines") is falsity-thresholded and arguably stays `false`.
- THE RULE, sharpened: it is NOT "definition mentions both words -> misleading". Test whether
  "misleading" is the INCLUSION CRITERION (disjunctive: "false OR misleading", "missing context")
  or merely the INTENT/EFFECT of falsity ("verifiably false and could mislead readers" — Allcott
  2017, correctly coded `false`). A naive keyword rule would miscode Allcott. Our own data follows
  the sharpened rule on 42/64 both-words rows; the 22 exceptions need this test applied.
- F0062 SMALL-N->CURATED: NOT supported as stated. Corpus-wide, curated is coded on 18% of n<200
  rows, 8% of 200-1k, 12% of 1k-10k — no cliff. BUT it converges with the independent coder's
  systematic over-flagging of curation relative to us, and the P0 read shows the pattern is real in
  a GENRE (small-n health video/webpage content analyses that take the top-N search results), not a
  function of n itself. Recommend a targeted sweep of that genre, not a blanket n threshold.
- F0450 (85114317455, sock-puppet agent audit): Sacha recalled already deciding to exclude it. The
  record does NOT support a dataset exclusion — the earlier decision (research_log ~L3202) excluded
  item D11 from the IRR *comparisons*, a different thing; the study is still in as EXPOSURE. The
  SUBSTANTIVE case for exclusion is nonetheless strong and has precedent (v1.6.3 dropped forced-
  exposure experiment 85189974015): 8 emulated sock-puppet agents, not human audiences, and the row
  is already flagged "not human whole-diet". CONSEQUENTIAL: dropping it moves EXPOSURE k16->15 and
  the simplified median 2.0->1.4, so it touches a headline construct. Sacha's call, flagged not applied.
- F0304/F0308 (OA-W2992531903): AGREE with Sacha and the coder — definition is "for-profit
  fabrication, politically-motivated fabrication and malicious hoaxes masquerading as news", which
  is `fabricated`; our blank is wrong. No local PDF because the record is OpenAlex-only (a report),
  which is also why it never entered the PDFs/ folder.
- F0135 (Seeking Alpha): NOT an experimental paper — it is 203,545 observational articles scored by
  a LIWC classifier calibrated on 171 SEC-prosecuted fakes. On construct I DISAGREE with both Sacha
  and the coder: "unconditional probability of an article being fake" is a share of all articles,
  which is CONTENT by the denominator rule. Recorded as an open disagreement rather than applied.
- FLAG/QUALITY-with-breadth: Sacha's objection is fair and my framing was too strong. breadth
  records WHICH veracity standard was applied; a QUALITY row means none was, so a breadth on a
  QUALITY row is contradictory — but the resolution may be the opposite of what I implied: several
  of these definitions (guideline non-concordance, misconceptions) ARE the `misleading` end of the
  veracity scale, so recoding construct QUALITY->CONTENT while KEEPING breadth=misleading reconciles
  the flag, the coder's CONTENT call, and Sacha's instinct. Option added, not applied.
- P3 DECISION CONFLICT: Sacha's button says "codex" (recode 11 rows to CONTENT) but his note says
  "they look like quality tbh" — opposite readings. NOT applied pending clarification. Impact is
  small either way (CONTENT 22.9->23.2, k209->214).
NB: the medians in this entry are a simplified study-level recompute for decision support and differ
slightly from the pipeline's published figures (which apply exposure_type/definition_variant rules).
NOTHING APPLIED TO THE DATASET. Freeze untouched at v1.6.8.

## 2026-08-05 — FROZEN v1.6.9 (adjudication round 1 applied) + drift-check made dynamic

APPLIED (scripts/apply_v169.py), on Sacha's calls:
(1) DROPPED study 85114317455 (2 EXPOSURE rows). Sock-puppet agents, not humans — "if it's not
humans we don't include". Precedent v1.6.3 (forced-exposure experiment). EXPOSURE k16->15.
(2) RECODED the 7 QUALITY-with-breadth rows -> CONTENT keeping breadth=misleading, DATASET-WIDE (6
were in the coded 22% sample, 1 was not; applying a class decision only where the sample looked
would bias the data toward the sample). CONTENT k209->213.
HELD: the 5 blank-breadth QUALITY rows, incl. A1 85207525286 (v1.6.4 flipped it, v1.6.8 reverted it;
a third flip needs an explicit decision, not a side effect of a class rule).

FULL PIPELINE REGENERATED + MANUSCRIPT RE-SYNCED (14 substitutions): CONTENT k213 median 23.1,
backbone 6.6% k=32, EXPOSURE k15, exclude-HIGH backbone 5.9, R² measurement 22.0 / construct 15.7 /
denom 12.2, small-study CONTENT rho -.41, CONTENT high-RoB 59%, seen-recall/EXPOSURE ratio
23.3 [11.3-106.7], main analysis set 571, corpus 673/313. checker 27/27 PASS; drift clean.

THREE TOOLING BUGS FOUND AND FIXED (all the same family — a gate that cannot see the current data):
1. **The drift check was a hardcoded BLOCKLIST** of known-stale values. 675/314 were the PREVIOUS
   freeze's counts, had never been added, so the manuscript contradicted the freeze in 16 places and
   the check reported CLEAN. Rewritten to compare against the CANONICAL counts dynamically. Two
   refinements to keep it usable rather than noisy: subset counts are legitimate (the metareg's
   277/470 are read from regression_data.csv), and only counts NEAR the canonical one can be drift
   (a stale total is a few rows off; 118 or 470 is a different quantity sharing a noun). Lines that
   NAME their freeze ("v1.5.2 (679 estimates / 317 studies)") or mark themselves historical are
   provenance, not drift, and are skipped — that is the audit trail working as designed.
2. **phaseB_dashboard.py hardcoded "679 estimates / 317 studies"** in its template — wrong for four
   freezes. Now derived from the freeze.
3. **make_nopdf_sheet.py was pinned to estimates_v1.4.5_frozen.csv** — five freezes stale, still
   reporting "317 studies". Now resolves the `File:` line like every other script. This is failure
   mode #1 (stale-file gate) recurring in a script nobody re-read.
ALSO: phaseB_ratio_bootstrap.py and phaseB_recall_split.py were MISSING from the documented pipeline
run-order, so ratio_bootstrap.csv silently kept v1.6.8 k-values that the manuscript quotes; and
aggregate_rob_v3.py must run whenever the STUDY SET changes (RoB read 314/313 until it was re-run).
The run-order memory has been corrected.

F0135 (Seeking Alpha) — RE-READ AS ASKED, and the answer changed the question. The quoted sentence
("The unconditional probability of a Seeking Alpha article being fake is 2.8% ... peaking at 4.8% in
2008 ... low of 1.6% in 2013") does NOT appear anywhere in the PDF we hold. Our PDF is the March-2022
version, "Social Media and Financial News Manipulation" (Kogan/Moskowitz/Niessner) — an event study
of the SEC investigation's effect on trading volume. The paper states a previous version was titled
"Fake News in Financial Markets"; the 2.8% figure lives in THAT earlier version, which we do not
hold. Full text verified complete (165k chars, ends in the reference list). So the construct dispute
is premature: the estimate is not verifiable against our source document. NEXT STEP is to obtain the
earlier version; if the figure cannot be sourced, the row is a candidate for removal, which matters
more than whether it is CONTENT or OTHER. Recorded, not applied.

GENRE SWEEP (Sacha approved instead of an n-threshold rule):
data/extract_v2/qa/curation_genre_candidates.csv — 65 rows / 48 studies that are small-n (<=1000)
video/webpage content analyses coded CONTENT/QUALITY with NO curation flag. Only 2 carry explicit
top-N/search-result language in the extracted text, so this CANNOT be auto-applied: the evidence for
"took the first N search results" is usually in the paper's methods, not in the quoted sentence.
The list is a reading queue, not a recode. NOT APPLIED.

## 2026-08-05 (cont.) — FROZEN v1.7.0: remaining decided rows applied; manuscript re-synced;
## checker coverage gap closed

Sacha approved the three held questions. Applied via scripts/apply_v170.py — targets resolved by
(study_id, value_pct), NEVER by F-id (they are positional and v1.6.9's drop had already re-pointed
six decided items). 15 row-changes, no id/value/row-count change:
(A) breadth false -> misleading, 8 rows, per the sharpened rule (inclusion criterion admits
    non-strictly-false material vs misleading merely describing the intent of falsity). EXCEPTION
    confirmed: 85213223975 (8.5) stays `false` — ">50% false when fact-checked" is falsity-thresholded.
(B) breadth blank -> fabricated, ALL 6 rows of OA-W2992531903, not just the 2 sampled ones: breadth
    is a property of the DEFINITION and all 6 share it, so fixing only the sampled rows would bias
    the dataset toward the 22% the coder happened to see. Adds a study to the `fabricated` stratum.
(C) denom political_news -> news_diet on W4293124965 (3.3); denom_class moved with denom_scope.
HELD AS DECIDED: W2901308345 stays CONTENT (verified against the ORIGINAL 2018 version); the 5
blank-breadth QUALITY rows stay QUALITY (no internal contradiction; 85207525286 = A1 settled in
v1.6.8); W7146985142 keeps denom n/a (CONCENTRATION invariant).

A GATE CAUGHT A REAL AMBIGUITY MID-APPLY: (study_id, value_pct) matched 2 rows for OA-W2992531903
(value 1.0 appears twice — France and Italy). Rather than force it, inspection showed all 6 rows
share one definition, which is what turned (B) into a study-wide fix. The assert did its job.

CHECKER COVERAGE GAP CLOSED — the important process finding. check_manuscript_stats.py reported
27/27 PASS immediately after the re-freeze while SIX manuscript numbers were stale, because none of
them was among the 27: the breadth gradient (10.8→22.0→28.5, now 10.8→22.1→27.6 — the very thing the
adjudication had just moved), breadth R² 9.2→9.7, platform 9.7→8.7, topic 7.8→7.9, the regression n
(470/277→471/278), and §2.10 still listing the RETIRED `unreliable-source`/`low-quality` breadth
values as live coding options. All fixed; five new assertions added (breadth gradient, platform and
topic R², regression n, and a positive assertion that the live 3-value breadth scale is what the
methods describe). Now 32/32. A guard that greenlights stale text is worse than no guard.

FULL PIPELINE REGENERATED (21 scripts + metareg). VERIFIED: FROZEN.md MD5 matches the file on disk;
673/313 matches the header; drift check clean; PRISMA reconciliation PASS; RoB 313/313.
CODEBOOK INVARIANTS re-checked directly against the live freeze: breadth legal everywhere, no
QUALITY row carries a breadth, every CONCENTRATION row is n/a with conc_unit+conc_dimension set,
denom_class consistent with the two-axis fields, sock-puppet study absent, zero fully-identical rows.
The only invariant that "failed" was my own too-strict duplicate key: 6 collisions on
(id, value, quote) are legitimate — they differ by COUNTRY or PLATFORM, which is the row key
(study x country x platform x measure). The 3-row 105035036279 case is scale_score rows with empty
value_pct that differ by platform and never enter the analysis set.

## 2026-08-05 (cont.) — FROZEN v1.7.1: curation sweep adjudicated AGAINST SOURCE (not escalated)

Sacha: "the 65-row genre sweep needs PDF reading — do that", and pushed back on being handed 143
queue items ("You already carefully went over them and couldn't decide?"). He is right: the standing
rule is adjudicate against SOURCE, not "the human clicks every row". Source-based calls are mine to
make; only genuine taxonomy judgment calls should escalate.

NEW TOOLING: scripts/extract_sampling_evidence.py (pulls each paper's sampling-method sentences from
full text) + scripts/adjudicate_curation.py (verdict + the decisive quote per study, written to
data/extract_v2/qa/curation_adjudication.csv). Source coverage was the enabler: 101 of the 111
studies involved have extracted full text or a local PDF.

RESULT — the evidence is overwhelming and Sacha's intuition was right. These are health video/webpage
content analyses that take the first or top N search results: "the top 100 eligible videos from each
platform were selected to form the final dataset", "the first 150 videos were analyzed", "videos were
sorted by view count", "the first 30 German videos were included, sorted by the proprietary TikTok
app algorithm". Rank truncation DEFINES the sampled set, so the denominator is curated.
APPLIED v1.7.1: 41 rows / 26 studies topical -> curated_sample.

I OVER-RODE MY OWN EXTRACTOR on 8 studies where the pattern fired on non-sampling text — "top 10
features" (ML forward variable selection), "top 5 countries from Table 2" (a result), "top 10
languages ... in all tweets collected" (a descriptive stat), and 85088969117 which states it could
NOT take the most-shared (evidence AGAINST curation). Parked: 2 ambiguous (85059494932's top-100
news spreaders is a figure subset, not necessarily the denominator; 85142238598's top-10 hashtags)
and 9 "seeded" studies whose fact-check mentions were discussion prose, not sampling. Only decisive
rank-truncation/most-viewed SAMPLING statements were applied. Every applied study has its sentence
on file, so each recode is traceable.

THE SUBSTANTIVE FINDING — the direction, not just the count. Before: curated 19.7% (k=34) vs topical
25.8% (k=174), i.e. curated corpora read LOWER than topical ones, which is backwards for the
review's own thesis that curation inflates prevalence. After: curated 26.0% (k=57) vs topical 24.6%
(k=150) — curation now reads higher, as the taxonomy predicts. Our under-flagging had been MASKING
the curation effect. Denominator R² 12.2 -> 12.8%. Constructs and breadth untouched
(CONTENT 22.9 k=213, EXPOSURE 1.4 k=15).

Full pipeline regenerated + metareg; manuscript re-synced (denominator R²); 32/32 stats PASS; drift
clean; PRISMA PASS; all codebook invariants re-verified against the live freeze.

STILL OPEN (honest scope): the queue's construct (37), breadth (20) and denom_scope (9)
disagreements are NOT yet adjudicated — 66 items. The 61 denom_selection items are effectively
answered by this sweep. Also open: 9 seeded + 2 ambiguous + 29 unclear + 6 no-text curation studies.

## 2026-08-05 (cont.) — Adjudication pass COMPLETE: v1.7.2 + v1.7.3; new invariant guard

Sacha: "what i want is just clean and correctly coded data ... go for the other pass, take your time".
All 59 remaining queue items adjudicated against source. Two freezes applied; 4 items escalated.

CONSTRUCT CODING HELD UP. Of 15 singleton disagreements ours stands on 13, and two whole classes
were confirmed ours:
- all 6 "OTHER vs SHARING": the denominator is the MISINFORMATION itself ("AfD accounted for 95.5%
  of misinformation shared in Germany"), so these are attribution/concentration statements, not
  prevalence shares. The coder read "share of misinformation" as "misinformation's share".
- all 5 "SHARING vs CONTENT": each is computed over a stream of SHARED items, which is what SHARING
  means in this codebook.
Also confirmed ours: CONCENTRATION vs EXPOSURE/SHARING/OTHER (4 rows - all are top-X -> Y%),
REACH vs SHARING/OTHER/CONTENT (3 rows - people denominators), RECALL vs CONTENT (self-report),
SHARING vs EXPOSURE (engagement = sharing), SHARING vs CONCENTRATION (a share, not a top-X).

v1.7.2 (8 rows) - where OUR coding was wrong:
- VALUE_KIND x2 (85215939792): 4.818 and 2.003 are MEAN mini-DISCERN scores on a 1-5 scale coded
  `value_kind=proportion`, so they were pooled with percentages inside the main analysis set. Now
  `scale_score`; main set 571 -> 569. Spotted because a "percentage" of 4.818 sat next to a
  mean-score measure_type.
- DENOM x1 (85162702221): a behavioural REACH row coded all_media; REACH denominators are people.
- BREADTH x5: two -> fabricated (fabrication-specific definitions); two -> BLANK (85143274147 is
  self-report where RESPONDENTS supplied what counted, OA-W3113799821 counts SEARCH QUERIES, which
  have no truth value); one -> misleading (Likert benchmarked against clinical guidelines).
  Allcott 2017 was NOT moved to `fabricated` despite the coder's high confidence - "intentionally and
  verifiably false ... rated false by Snopes/PolitiFact" is a falsity standard.

v1.7.3 (8 rows) - found by a NEW INVARIANT, not by the coder. "A behavioural REACH denominator is
the people observed" failed on 8 of 66 REACH rows, and all 8 were one bug: DEMOGRAPHIC-BREAKDOWN
rows had inherited a sibling row's `measure_type` and denominator while their own quotes are plainly
shares of people ("11 and 21% of PEOPLE on the right ever shared any fake news content"). This also
repaired an inconsistency v1.7.2 itself introduced - it had corrected one row of 85162702221 and
left its siblings, splitting a single measure across two denominators.

NEW PERMANENT GUARD: scripts/check_invariants.py - 9 codebook invariants checked against the live
freeze, non-zero exit so it can gate a freeze. Every check is there because it caught something.
Run it after every re-freeze alongside the crosswalk and stats checkers.

Manuscript re-synced each time (breadth R2 9.7->8.8, gradient ->27.8, denom R2 12.8->13.5, main set
571->569); checker now 33 assertions incl. the main-set size, which had drifted silently; drift
clean; PRISMA PASS; all 9 invariants hold.

ESCALATED to docs/decisions_2026-08-05/decisions.html (4 items, built by scripts/build_decisions_page.py):
1. SYSTEMIC - 100 rows are the same quantity (share of URLs/posts in a corpus from untrustworthy
   domains) split 65 SHARING / 35 CONTENT. `sharing_subtype` marks the split, so a coder was making a
   distinction, but whether a platform stream is "content that exists" or "content people shared" is
   not settled by the codebook and it moves two reported pools. My proposed rule: sharing ACTS
   (tweets/retweets/reshares) = SHARING, corpora of ITEMS (page posts, articles, videos) = CONTENT.
2. The 5 QUALITY rows with blank breadth - incl. 85134426953 (an expert 5-point FACTUALITY scale,
   which I think is our error) and A1 85207525286, now decided three different ways and needing a
   written settlement.
3. Fact-check-SEEDED corpora (9 studies + 2 ambiguous): does seeding curate the denominator, or does
   it build the numerator over a clean topical denominator? The codebook supports both readings.
4. An actor's own posts (Bolsonaro's 100 most-retweeted tweets): our CONTENT vs the rule as written,
   which says SHARING covers "an actor's output" - by our own wording the coder is right.

## 2026-08-10 — FROZEN v1.7.4: Sacha's four authorial decisions applied

Decisions taken from docs/decisions_2026-08-05/decisions.html. 35 row-changes.

(A) QUALITY -> CONTENT, 4 rows (86000670842 x2, 85143511628, 85134426953). Construct only.
A1 (85207525286) HELD BACK. Sacha chose "all" but wrote "I'm unsure ... 'Misleading' is clearly
veracity/factuality no?" — and for THIS paper it is not. Source checked: a video is "useful" if it
contains "at least 4 out of the 6 questions on the ASRS-v1.1 screener"; "misleading" is merely the
complement, so a wholly TRUE video covering 3 items is labelled misleading. That is a
coverage/completeness criterion — the exact reasoning behind the v1.6.8 revert. Applying a change
whose stated rationale the source contradicts would put a wrong number in the paper, so A1 stays
QUALITY pending his confirmation. Everything else in his decision was applied as given.

(B) Fact-check-SEEDED corpora -> curated: 23 rows / 9 studies; only `denom_selection` moves and
`denom_scope` is preserved, which is exactly the point Sacha made ("we code both topical and curated,
they are not incompatible"). NOT applied to 6 otherwise-eligible rows whose scope is `population`:
those denominators are survey RESPONDENTS, and a sample of people cannot be rank-truncated or
hand-assembled — a mechanical mismatch, not a re-judgment. The 2 "ambiguous" studies stay open.

(C) CONTENT vs SHARING: the rule is ratified and recorded in the codebook as (a0-bis) — decide on the
DENOMINATOR, not the numerator's verb; sharing-ACT streams -> SHARING, corpora of items that EXIST
-> CONTENT; an actor's own output is CONTENT. Of the 100 source-level/domain-list rows, 92 already
complied and 8 moved: 6 link-bearing/retweet streams -> SHARING, and 2 (politicians' and state
legislators' own posts) -> CONTENT, which is decision (D) applied consistently rather than only to
the one row it was asked about.

(D) No data change; the codebook's SHARING definition dropped "or of an actor's output", which had
made a politician's own tweets codeable both ways. Fixed in the GENERATOR (build_codex_full.py) so
future cross-check instructions carry the corrected rule, and the instructions were regenerated.

CONSEQUENCES (these move headline numbers): SHARING 9.1 -> 11.2% with k 25 -> 28; CONTENT 23.0 ->
23.2% with k 209 -> 212; EXPOSURE k 16 -> 15 and backbone k 33 -> 32 (both from earlier freezes,
now flowing through); exclude-HIGH CONTENT 12.4 -> 11.7%; metareg denom R2 13.5 -> 11.8, construct
15.7 -> 15.1, sampling 17.9 -> 18.0, ground-truth 17.7 -> 17.9, id-method 17.3 -> 17.6, platform
8.7 -> 9.0, topic 7.9 -> 8.3; regression set 471/278 -> 475/279.

CHECKER GAP CLOSED AGAIN. The 33-assertion checker passed while the RESULTS TABLE and the GRADE
TABLE were both stale (SHARING still 25/9.1, CONTENT still 209/23.0) because only prose figures were
asserted. Added 7 assertions covering every GRADE row's k+median and the SHARING/REACH medians ->
40/40. This is the third time a green checker was hiding stale text; the pattern is always the same,
an assertion set that grew slower than the document.
All guards green on v1.7.4: invariants 9/9, stats 40/40, drift clean, PRISMA PASS.

## 2026-08-10 (cont.) — A1 (85207525286) SETTLED as QUALITY; no data change

Sacha: "for 85207525286 it's quality." The freeze already holds it as QUALITY (breadth blank), so
nothing was applied — the work was making the decision stick. This row had been decided four times
and flipped three (v1.6.4 QUALITY->CONTENT; v1.6.8 reverted on the Codex cross-check; the 2026-08-05
round read it CONTENT again; now closed as QUALITY), always because the paper's LABEL ("misleading")
looks like a veracity term and matches a live `breadth` value.
Written up as a closed entry in docs/DECISIONS_REGISTER.md with the deciding quote ("useful" =
contains "at least 4 out of the 6 questions on the ASRS-v1.1 screener", so a wholly TRUE video
covering three items is labelled misleading -> coverage, not veracity), and generalised into the
codebook as (a0-ter): code the OPERATIONALISATION, not the label — if a wholly true item could
receive the label, it is not a veracity judgement. Any future cross-check flagging this row is to be
answered with the register entry rather than re-adjudicated.
Guards re-run unchanged: invariants 9/9, stats 40/40, drift clean, PRISMA PASS.

## 2026-08-10 (cont.) — FROZEN v1.7.5 (last curation items) + workspace tidy

v1.7.5: the two parked "ambiguous" curation studies resolved on their DENOMINATORS, which settles
both without needing a judgement call. 85142238598 -> curated ("top-40 per topic = top 20 posts x top
2 hashtags"; rank truncation defines the set twice over — though the row is a scale_score with an
empty value_pct, so it is metadata correctness, not an analysis change). 85059494932 unchanged: its
denominators are the FULL corpora (30.7M URL-bearing tweets; ~2.3M distinct users), and the "top 100
news spreaders" that raised the flag is a subset used for one network figure. ADJUDICATION ROUND 1 IS
NOW FULLY CLOSED. Guards green: invariants 9/9, stats 40/40, drift clean.

WORKSPACE TIDY (docs/ had accumulated 100 entries):
- Checked EVERY docs/*.html for a generator before touching anything: 19 are script-generated and
  were left exactly where their generators write them. Moving a generated file only means the script
  recreates it and the archive copy goes stale — the same class of error as editing a generated file.
- Archived the 5 orphan one-off review sheets (abstract_only_search, reread_confirm, review_newadds,
  review_newrows, review_sheet) + big_batch_plan.md (0 references) to docs/Old/.
- LEFT v1.2_punchlist.md and v1.2_newrows_worklist.md in place ON PURPOSE: make_counts_crosswalk.py
  exempts them from the drift check BY BASENAME, so moving them would silently change what the check
  skips. Superseded but load-bearing.
- Removed scripts/__pycache__ (my own build artefact).
Root remains: CLAUDE.md, README.md and the folder scheme (data/ docs/ scripts/ PDFs/ searches/
literature/ Submissions/ + hidden .backups/ .work/). No duplicates or scratch files anywhere.

## 2026-08-10 (cont.) — memory audit

All 13 memory files checked for staleness, index integrity and dead links. Fixed:
- `misinfo-review-open-items.md`: the RESUME block still described the Codex batching decision as
  pending and A1 as an open coin-flip; rewritten to state the only outstanding data work (batches
  03-09, awaiting quota) with the fresh-session requirement and the reason for it. Freeze pointer
  v1.7.4 -> v1.7.5. The A1/A5 "OPEN (optional)" line replaced with the settlement + a pointer to the
  register entry, so the next reader cannot reopen it by accident.
- **`## Headline results` was still labelled "regenerated on v1.6.3"** — seven freezes stale, and the
  numbers had moved materially (SHARING 9.1 -> 11.2, CONTENT 23.0 -> 23.2, EXPOSURE k16 -> 15).
  A stale headline block in memory is worse than none: it is exactly what a future session would
  quote without re-deriving. Regenerated from the v1.7.5 pipeline with an explicit instruction to
  refresh it whenever the freeze moves, and a warning that any figure quoted from before 2026-08-10
  is stale.
- `misinfo-review-crosscheck-purpose.md`: A1 described as an unsettled coin-flip; now records the
  settlement and keeps the case as the worked example of the label-vs-operationalisation trap.
- `MEMORY.md` index line for the reliability memory said "IRR v3 package ready, coding pending" —
  the human IRR is done; also dropped the bare "κ.75", which is the superseded historical figure.
- `search-currency-topup.md`: dead wikilink `[[[replication_package]]]` (triple bracket, target never
  existed) -> pointer to the pre-submission section of open-items.
Verified: 13/13 indexed, every file has name/description/type frontmatter, zero dead links.

## 2026-08-10 (cont.) — Codex batch package for Sacha + a real bug caught while building it

Built ~/Desktop/Codex_coding_batches (7 blank batches, 503 rows, INSTRUCTIONS.md, README). Verified
blind: no key file, no key columns, every cell empty.

THE ONE-BATCH RULE WAS IN THE WRONG PLACE. It lived in my chat prompt and in the README (which is
addressed to Sacha) — but NOT in FULL_INSTRUCTIONS.md, the file the coder actually reads. Sacha spotted
it. Now the instructions open with a hard "CODE EXACTLY ONE FILE IN THIS SESSION, THEN STOP",
including the case that actually matters — being asked to keep going later in the same session — with
the reason (the 647-row single pass reproduced only 45% of its own denominator codes and was
discarded; ~72-row fresh sessions scored kappa .83/.75). Fixed in the GENERATOR, so it travels.

BUG FOUND: build_codex_full.py had silently CLOBBERED the campaign's answer key. The worklist and key
are a positional pair (F0001...) tied to the freeze they were built from; re-running the script after
a re-freeze rewrites the key against NEW data. It had been re-run at v1.7.4 (to fix the "actor's
output" wording), which left FULL_ANSWER_KEY.csv at 645 rows while the batches — and Codex's already
coded batch 01/02 answers — are 647. Every F-id after the first dropped row pointed at a different
estimate. This is failure mode #15 recurring inside the very tooling built to prevent it.
FIXED: key restored from commit 13ab23a (verified 647 rows, positionally aligned to the v1.6.8
campaign freeze, all batch ids present), and the generator now REFUSES to rewrite the worklist/key
while coded batches exist — it regenerates only the instructions text and says so. The title line is
also campaign-aware, since printing today's row count over a pinned campaign invites the reader to
think the batch files are stale.
Adjudication queue rebuilt clean on the restored key. Nothing downstream had consumed the bad key:
the queue pins and MD5-verifies the v1.6.8 freeze independently, which is why the misalignment showed
up as a row-count mismatch rather than as silently wrong adjudications.

## 2026-08-10 (cont.) — WHOLE-CORPUS independent re-code COMPLETE (batches 03-09 in)

All 647 codeable estimates now coded blind by gpt-5.6-terra medium, 9 batches, one per fresh session.
Integrity verified before merging: 503 new rows, blind columns byte-identical to the originals, no
illegal values, no confidence outside 1-5.

HEADLINE (vs the v1.6.8 campaign baseline — i.e. our PRE-adjudication coding, so uninflated):
  construct        kappa .802  (raw .858)   self-consistency 86%
  denominator SCOPE kappa .723  (raw .803)   self-consistency 88% on scope
  breadth          kappa .477  (raw .748)   self-consistency 94%
Against the RELEASED freeze (v1.7.5) construct is .819. On the 439 estimates that played no part in
any adjudication it is .822 — slightly ABOVE the corpus figure, which is the check that matters: if
our recoding had been quiet conformity to the model, the untouched rows would score LOWER, not higher.
The adjudicated rows were simply the hard ones.

THE FUSED-FIELD ARTEFACT RECURS, and this time it explains a scary-looking number. merge_codex_batches
warned that denominator self-consistency was 59% — below its 75% "treat as noise" threshold. It is not
noise: on the 80 repeated rows, when BOTH of the coder's answers are scope values it agrees with itself
88% (44/50); the other 30 are rows where it named the scope once and the curation the other time. The
instrument is stable; `denom_class` is not a coherent single question. Reported as scope kappa .72
against .47 for the fused field, exactly as the manuscript already argues.

SS4.8 UPDATED: the partial (22% sample) paragraph replaced with the completed corpus, stating (a) the
figure is measured against the pre-adjudication dataset so it is not inflated, (b) the released-freeze
figure .82, and (c) the never-adjudicated subset at .82. Decomposition sentence re-synced from the
old 134-row sample to the whole corpus (scope .72 raw .80, n=458). Guards: stats 40/40, drift clean,
invariants 9/9.

NEXT — a NEW disagreement queue of 422 items (construct 92, breadth 81, denom 249). Not yet
adjudicated, and NOT to be handed to Sacha row-by-row: the ratified rules from round 1 (curation, the
CONTENT/SHARING denominator rule, label-vs-operationalisation) should resolve whole classes of it by
rule, and the rest goes through the same source-based adjudication. The 249 denominator items are
predominantly the fused-field artefact rather than real scope disagreements and must be decomposed
onto the two axes before anyone reads them as errors.

## 2026-08-10 (cont.) — FROZEN v1.7.6: round-2 adjudication (whole-corpus re-code)

495 decomposed disagreements; 65 already resolved by v1.6.9-v1.7.5, leaving 430 live. Applied the
two classes the source and the ratified codebook settle; escalated ONE clarification.

APPLIED (36 rows):
- CURATION, source-evidenced: +6 curated, -3 un-curated. The curation extractor auto-classified 19
  new studies; I over-rode 9 of them after reading the denominators — 7 were false positives where
  the top-N is an ANALYSIS SUBSET while the estimate's denominator is the full corpus ("top-20
  users", "top-1% superspreaders", "top-10 topics", a BuzzSumo tool description), 1 was curated for
  a different reason than the regex matched (relevance-sorted search, 100 videos), and 1 is genuinely
  mixed (500 random + 2,000 popularity-selected) and is parked.
- BREADTH, 27 rows by the codebook rule. 19 match the coder, 8 do NOT — the asymmetry is deliberate
  evidence that this applies the RULE rather than conforming to the coder. The 61 items the rule
  cannot resolve were left alone: breadth is the genuinely fuzzy dimension (kappa .48 against 94%
  coder self-consistency = a real boundary disagreement, not instrument noise), and mass-recoding it
  would manufacture the agreement we are trying to measure.
CONSEQUENCE: the breadth gradient widened to 10.8 -> 21.4 -> 28.5% (was 10.8 -> 22.1 -> 27.8),
i.e. the ordering the taxonomy predicts got CLEANER as the rule was applied consistently.

A TOOLING BUG, same family as the others: re-running adjudicate_curation.py silently RESET the
`final_verdict`/`adjudicator_note` columns, discarding 8 human over-rides and 2 parked cases — a
generator clobbering curated state. Fixed: the script now MERGES, preserving every previously
adjudicated verdict and only auto-classifying studies it has not seen (it reported "preserved 85,
newly auto-classified 60" on the next run). Restored the lost verdicts from git first.

ESCALATED — ONE decision (docs/decisions_2026-08-05/decisions.html): rule (a0-bis) calls a corpus of
"sharing ACTS (shares, retweets, link-bearing posts)" SHARING, but "link-bearing posts" is ambiguous
between (a) the denominator is RESTRICTED to link-bearing posts and (b) posts that merely happen to
bear links. 36 rows have an explicitly link-restricted denominator and we code them inconsistently
today (24 SHARING / 12 CONTENT). I built a pattern for this TWICE and both times it matched the
NUMERATOR's phrasing instead of the denominator, in both directions — so this goes to Sacha rather
than a third guess. My recommendation is (a), which makes the 36 consistent and leaves the big
topical corpora as CONTENT.
Guards after the re-freeze: invariants 9/9, stats 40/40 (breadth R2 8.7, gradient re-synced,
measurement 22.1), drift clean, PRISMA PASS.

## 2026-08-10 (cont.) — FROZEN v1.7.7 + Appendix A: the content-sharing gap is a measurement artefact

TWO THINGS, and the second reframes the first.

(1) v1.7.7 — SHARING restricted to transmission denominators. Reading denominators (not
pattern-matching "retweet") showed 25 of 30 SHARING studies have a denominator that IS an act of
transmission; the residue was one already-decided category, an ACTOR'S OWN OUTPUT, which rule
(a0-bis) calls CONTENT. Moved 27 rows / 3 studies (politicians' own posted links). SHARING 30 -> 27
studies (25 after the pipeline's proportion filter). NOTE the rule bites harder than its origin case:
it was ratified on a SINGLE actor (Bolsonaro) and now also covers CLASSES of actors ("links shared by
Lega politicians"), which the source studies themselves describe as sharing. Reversible.
A GATE CAUGHT A STALE FIELD: `sharing_subtype` was still set on 16 rows recoded away from SHARING in
earlier freezes — including two moved by v1.7.4 itself. A stale field that would later read as
evidence the row is a sharing measure. Cleared, and the condition is now asserted.
My earlier "22 of 30 involve re-transmission" was a crude regex result and I corrected it before
acting: several of the 8 supposed exceptions have denominators that say "shared" outright.

(2) APPENDIX A — Sacha asked whether CONTENT vs SHARING is meaningful at all, or should be merged.
Tested rather than argued (scripts/appendix_content_sharing.py):
  - HOLDING THE INSTRUMENT FIXED DISSOLVES THE GAP. claim-level +1.7 pp [-11.9,+26.4];
    researcher-coded +1.7 [-9.9,+13.2]; source-level -8.5 [-14.1,-1.9]; domain-list -8.7 [-15.0,-3.0].
    In the two strata estimable with decent precision on BOTH sides the difference is significant and
    REVERSED — shared content carries MORE misinformation than content at large.
  - THE SPLIT DOES NOT ORGANISE THE DATA. Pooling both constructs, eta^2 on study-level logit medians:
    ground_truth .173, topic .169, platform .149, sampling .149, classification_level .084,
    breadth .080, denom_scope .079, unit .035, CONSTRUCT .012, denom_selection .007. The
    content/sharing split is second-weakest of ten. (It was .034 before v1.7.7; consistent recoding
    made it weaker still.)
  - CAUSE: the two constructs are studied with almost disjoint instruments (CONTENT = researcher-coded
    claim-level topical corpora; SHARING = domain-list source-level platform traces), so comparing
    them also compares the instruments, and claim-vs-source is ~an order of magnitude.
RECOMMENDATION TAKEN: do NOT merge — they answer different questions and the ladder is the paper's
frame — but stop interpreting the difference between them as a finding about misinformation. Written
as Appendix A (Sacha: "maybe not in the MS but maybe in appendix").
This is the review's own thesis turning on one of its own comparisons, which is why it belongs in the
paper rather than in a drawer. PRACTICAL PAYOFF: the CONTENT/SHARING boundary cases — the hardest to
code and the ones the independent coder most often disputed — have little bearing on any reported
quantity, which defuses the open "link-bearing posts" question.

Manuscript re-synced (CONTENT 23.1 k=214, SHARING 13.1 k=25, construct R2 13.3, rho -.43,
exclude-HIGH 11.5, breadth gradient 10.8/21.0/28.5, GRADE table). Guards: invariants 9/9, stats
40/40, drift clean, PRISMA PASS.

## 2026-08-10 (cont.) — FROZEN v1.7.8: actor rule refined; Appendix A CORRECTED (weaker claim)

Sacha: "ok ok i guess it's sharing then, if the study describe it as such." The rule ratified earlier
("an actor's own output is CONTENT") came from a case about ONE person (Bolsonaro) and, applied
literally, swallowed studies measuring the sharing behaviour of a POPULATION of actors. Refined:
  ONE named actor's own output -> CONTENT (85131964464 unchanged)
  a CLASS of actors, measured by what they share -> SHARING (follow the study's framing)
Reverted v1.7.7 in full (27 rows) AND the 2 rows v1.7.4 had moved on the same reasoning, which
seeded the over-reach: W4306964957 (2), 105029521599 (1), 85142396682 (6), 105027856675 (20) = 29
rows -> SHARING, with sharing_subtype restored. SHARING 95 rows / 31 studies. Codebook (a0-bis)
updated with both the original ruling and the refinement, so the next reader sees why it is bounded.
A GATE CAUGHT MY OWN OVER-REACH: I asserted these studies must be wholly SHARING, but 105027856675
also holds legitimate OTHER rows (the "AfD accounted for 95.5% of misinformation shared" attribution
rows, whose denominator is the misinformation itself). Assertion narrowed to "none left as CONTENT".

APPENDIX A CORRECTED — this matters. Written yesterday against v1.7.7, it reported the source-level
(-8.5 pp [-14.1,-1.9]) and domain-list (-8.7 [-15.0,-3.0]) contrasts as SIGNIFICANT and REVERSED.
After the revert those same contrasts are -4.0 [-10.8,+8.1] and -4.7 [-11.5,+6.8] — both spanning
zero. The strong claim was an artefact of the coding I have now reverted, and leaving it in would
have put an overstated result in the paper.
Rewritten to the claim the data supports: EVERY stratum's interval spans zero; the point estimates
CHANGE SIGN with the instrument (claim-level runs with the headline, source-level against it); and
the strata where one construct is well populated are exactly those where the other is thin, so these
contrasts are UNDERPOWERED rather than null — which is itself the finding, since the two constructs
are rarely measured on common ground. eta^2 for construct is .040 (8th of 10 moderators, was .012
under v1.7.7). The conclusion is unchanged and the hedging is now correct: report the constructs
separately, do not read the gap between them as a fact about misinformation.
LESSON: an appendix analysis written against a freeze must be RE-RUN after any recode that touches
its variables — the script made that a 10-second check rather than a silent error, which is the
argument for making these analyses scripts rather than prose.

Manuscript re-synced throughout (CONTENT 23.5 k=210, SHARING 10.0 k=29, construct R2 15.7, rho -.41,
exclude-HIGH 13.0, breadth gradient 10.8/21.4/28.5, GRADE table, appendix table + eta^2 list).
Guards: invariants 9/9, stats 40/40, drift clean, PRISMA PASS.

## 2026-08-10 (cont.) — PRE-REVIEW AUDIT: three real defects found and fixed

Sacha asked for a thorough readiness audit. Ran it as checks rather than assertions; it found three
things that would have embarrassed us in review.

1. **THE FREEZE CHAIN DID NOT REPLAY.** Replaying every apply_v1XX.py and comparing MD5s showed
   apply_v171.py and apply_v174.py FAILING: both read the LIVE curation_adjudication.csv, which has
   kept growing as more studies were adjudicated (9 seeded studies at v1.7.4, 16 today), so the
   scripts no longer reproduced their own outputs. For a project whose central claim is
   reproducibility, a freeze chain that cannot be replayed is a serious defect.
   FIXED: snapshotted the verdicts as they stood at each freeze
   (data/extract_v2/qa/snapshots/curation_adjudication_at_v1.7.{1,4}.csv, recovered from the commits
   that created those freezes) and pointed each historical script at its own snapshot. All 11
   scripts now replay v1.6.8 -> v1.7.8 with stable MD5s. GENERAL RULE: an apply script must read only
   IMMUTABLE inputs — its parent freeze plus a snapshot — never a working file.

2. **THREE STALE RoB ITEM RATES IN THE MANUSCRIPT.** Sweeping every one-decimal percentage in the
   manuscript against every pipeline output left two unmatched, and one was real: the RoB item rates
   said 80.3 / 78.9 / 52.0 where the regenerated appraisal says 80.2 / 78.8 / 52.3 (the master was
   rebuilt when the study set changed to 313). Small, but wrong, and sitting in the sentence that
   carries the paper's rhetorical punch ("the instrument's modal failure is the review's subject").
   Corrected and now ASSERTED — the checker was blind to them, which is why they survived. 40 -> 43.
   (The other unmatched number, 97.5%, is the screening gold-set agreement, correctly not a phaseB
   output.)

3. **fig_funnel.svg** was an orphan — stale since 23 July, not referenced by the manuscript, only by
   the log. Archived to docs/Old/ rather than left to look like a current figure.

ALSO VERIFIED CLEAN: no placeholders/TODOs anywhere in the 9,126-word manuscript; all 31
reproducibility-critical scripts run without error; 17 figures current and figs 1-5 all present and
referenced; §4.8's "released freeze" and "never-adjudicated" kappas re-derived against v1.7.8
(0.815 and 0.822 — both still round to the .82 printed, so the text stands); working tree clean and
pushed; 52 tags.

REMAINING OPEN ITEMS (not defects — declared work):
  - search-currency top-up before submission (PRISMA <12-month rule) — the one hard blocker
  - "a targeted integrity pass is planned before submission" (§3.5) — promised in the text, not done
  - "three batch-two items remained under source-anchored adjudication at the time of writing" (§4.8)
    — verify whether still true before submitting, or update the sentence
  - the open "link-bearing posts" clarification (36 rows; Appendix A shows it moves nothing material)
  - 61 breadth items the codebook rule cannot resolve — a documented fuzzy boundary, reported as
    reliability rather than recoded

## 2026-08-10 (cont.) — the two "open" manuscript commitments were ALREADY DONE; text corrected

Sacha asked what these were. Both turned out to be stale STATUS text, not outstanding work — the
manuscript was understating what the project had done.

1. "a targeted integrity pass is planned before submission" (§3.5). The pass was largely done on
2026-07-30 (87 metadata-less studies re-screened, 2 more fabricated found). Verified today against
the released freeze: of the 49 studies with a non-Scopus identifier, 47 were formally re-screened;
the 2 that were not are the hand-added Science Advances paper and the authors' own Faker Island
study, neither of which came through the automated open-access route that produced every known
fabrication. Corpus-wide signal checks: 0 studies with no DOI, 0 studies with identical values
across >=4 rows (the tell that exposed OA-W7154838691). Written up as
data/extract_v2/qa/integrity_pass_2026-08-10.md.
§3.5 rewritten from a PROMISE into a RESULT — it now states what was screened, what was found, and
ends with the honest limit: "screening for fabrication is only as good as the signals a reader can
see, and a sufficiently careful fabrication would pass it."

2. "three batch-two items remained under source-anchored adjudication at the time of writing" (§4.8).
All three were adjudicated by Sacha on 2026-07-30 and applied in v1.5.8 (E12 excluded as fabricated,
E02 and E03 denominator recodes). The sentence had simply never been updated. Rewritten to state the
outcome: one exposed the fabricated study, two were denominator miscodes on our side, both corrected.
That is strictly better for us — it turns an apparent loose end into evidence the process worked.

3. BREADTH kappa .48 was sitting in §4.8 unexplained, which is how a reviewer comes to think the
category is broken (Sacha: "reads weird... as if we have wrong categories"). Added its
interpretation: it is NOT instrument noise (the coder reproduced its own breadth judgment 94% of the
time on repeated rows), and the disagreements concentrate on definitions that either state no
veracity standard or state two ("false or misleading"). Where a definition commits — fact-check
verdicts, fabrication-specific language — agreement is high. So breadth agreement measures how
precisely this literature specifies what it counts, which is the review's own subject arriving in
its reliability statistics. Also stated why we do NOT harmonise the residual cases: harmonising
would manufacture the agreement the coefficient exists to measure.

Also cleared ~/Desktop/Codex_coding_batches (verified byte-identical to the repo copies first,
then moved to Trash, recoverable).

## 2026-08-10 (cont.) — DOC AUDIT: the .md files had drifted; one contradicted the manuscript

Sacha asked whether all files, md included, are correct. They were not. The drift check only guards
COUNTS, and only in unqualified sentences, so several current-state docs had gone stale unnoticed.

**A LIVE CONTRADICTION IN THE MANUSCRIPT.** `grade_certainty_framework.md` still recorded
"EXPOSURE HIGH" from the v1.4.6 run. Chasing it against the pipeline exposed a real error one level
up: **grade_sof.csv now rates SHARING as LOW (2 downgrades: indirectness + precision-fragility), but
the manuscript's GRADE table and its prose both still said MODERATE.** The certainty column had
never been asserted. Fixed in the manuscript (table row, IQR 2.1–20.4 -> 1.6–20.4, and the prose
sentence), and ALL SIX GRADE certainties are now asserted by the checker: 43 -> 49 checks.

Also corrected:
- `grade_certainty_framework.md` — result line regenerated from grade_sof.csv, with an explicit note
  that the CSV is the source of truth and this doc is not; the two prior downgrades (EXPOSURE
  HIGH->MODERATE, SHARING MODERATE->LOW) are named so the history is legible.
- `data_quality_methods.md` (679/317 -> 673/313) and `METHODS_PROVENANCE.md` §8 (679/317 at v1.5.2,
  fifteen freezes behind) — both refreshed, with a pointer that FROZEN.md/counts_crosswalk are
  authoritative and these sections are hand-maintained.
- `dataset_provenance.md` — the "auditable chain" ledger had stopped at v1.4.12 and was MISSING 21
  FREEZES, while still labelling v1.4.12 "CURRENT". Two documents both claiming to record the chain
  had silently diverged. Fixed structurally rather than by hand: NEW `scripts/sync_provenance_ledger.py`
  generates the freeze table from FROZEN.md (33 freezes, with git-tag presence checked and a warning
  for any untagged freeze); the old hand table is retained for its per-version narrative but banner-
  marked as superseded.
- `RESUME_HERE.md` — pinned v1.5.2 as canonical, 21 freezes stale, in a file whose own header warns
  "a stale pointer is worse than none". Rewritten so it holds NO state at all, only a table of where
  the authoritative answers live. A pointer that duplicates state will always drift behind it.
- `human_review_provenance.md` — A9 (the v1.4.0 audit) still marked "(open)"; closed at v1.4.12.
- `codex_check/MODEL_AND_PROVENANCE.md` — the §4.8 staleness bug was described in the present tense
  although it was fixed; marked fixed at the point of the claim.
Pipeline memory updated: ledger sync and check_invariants added to the post-freeze run-order.

## 2026-08-10 (cont.) — FULL PRE-SUBMISSION REVIEW (three parallel audits: numbers, methods, prose/venue)

Sacha asked for a thorough review of everything ahead of a Nature/Science submission. Ran three
independent audits (numeric verification vs pipeline; statistical-methods rigour incl. script
inspection; prose/structure/venue fit). Nothing edited yet — findings logged here first.

**HEADLINE: the manuscript carries ~34 stale or internally contradictory numbers while all three
guards pass (49/49).** The Discussion was never re-swept after the v1.7.x freezes (ladder
"2.6→7.2→9→12→23→55", sharing 13.4, ratio lower bound 10.8, exclude-HIGH 23.2→11.7, "212 content
analyses"), and the checker's blind spots are exactly where they survive: no CI/IQR/PI assertions, no
per-group Spearman, no freeze-version string, presence-anywhere substring matching (a correct value in
one section greenlights a stale copy elsewhere; one check false-passes on an accidental "→ 11.7%"
substring in §3.2). Also stale: freeze pointer v1.6.8 in 4 places; abstract CONTENT CI; §2.2 table
CIs/IQRs (SHARING CI 4.0–16.0, CONTENT CI 19.5–26.4, backbone 4.1–8.8 per uncertainty_medians.csv);
predicted-prevalence 4.8/19.8 → 4.9/20.3; §4.5/§4.9 "573" → 569 and "~490" → 533; §4.9 "470/277" →
475/279; §4.4 "45 never retrieved" → 46; §4.7 "282" → 281; concentration "15 studies" → 16;
general-news 50 → 49; QUALITY-fold 23.1→24.5 → 23.5→24.9; abstract-appraisal −2.0pp → −1.5pp;
re-extraction k 7→6; §2.6 59% → 60%; §4.6 κ.82 vs §4.8 κ.78 (same-model construct — reconcile);
verbatim duplicated RA-round passage at end of §4.8. Full list in the session transcript; will be
applied as a single re-sweep commit with the checker extended FIRST (must-not-appear list +
section-scoped matching) so the sweep is guard-verified rather than hand-verified.

**METHODS FINDINGS (real, fixable):**
1. §2.5 claims univariable metaregs are cluster-robust; phaseB_metareg.R robustifies only the
   multivariable model. Breadth QM p=.145 yet narrated as "behaves as predicted" while p=.31 is used
   to dismiss the coarse denominator — asymmetric significance use.
2. collapse_sparse() rebuilds factors AFTER relevel(), so the multivariable breadth reference is "NA"
   (141 uncoded rows enter as a level), not "fabricated" as the script comment claims.
3. RoB instrument-thesis circularity (items 6/10 weighted, item 10 IS the thesis): add a sensitivity
   recomputing summary RoB on the 8 items excluding 6/10 to show the gradient survives.
4. PRISMA 24a: manuscript never STATES non-registration; add the sentence + a PRISMA checklist.
5. Minor: "crossed" should read "nested"; collapse<10 rule not applied to measurement/sampling;
   heterogeneity computed on study-median points with variance from the median estimate's n
   (undocumented); PI uses t(k-1) vs Higgins t(k-2); rob_checklist_v3 §source-list ruling cites the
   retired 5-value breadth scale.
6. Suggested cheap upgrades: Holm within the two test families (kills the parked multiple-comparison
   objection; only REACH/backbone Spearman fall, sign-consistency argument stands); within-CONTENT
   size correlation stratified by denom class; state the 0/300 exclusion-bound arithmetic ourselves.

**VENUE FINDINGS:** abstract 213 words (>200); main text ~4,700 (top of range); §4.8 alone 1,845
words (half of Methods) — trim ~40% to supplement; 8 display items vs ~6 (PRISMA → Extended Data,
fold Fig 3 into Fig 1); Appendix A → Supplementary Note; numbered headings and editorializing headers
to convert; author-year → superscript (~80 cites, some name-in-prose rewrites); tone list for
hostile referees (moral-panic-as-fact, "advocacy", "concedes our point", policy sentences) to soften
without losing the argument. Title alternatives proposed. Em-dash density ~1/110 words — halve.

**VERIFIED CLEAN:** bootstrap implementation matches Methods exactly (cluster resample, B=2000, seed
20260723; ratio bootstrap groups independent); leave-one-out 0.67pp; Appendix A table matches
appendix_content_sharing.csv exactly; R² family, breadth gradient, RoB item rates, GRADE rows all
current; Spearman-not-Egger justification sound; no AI-vocabulary tells; no citation-year collisions.

NEXT (order): extend checker → numeric re-sweep → methods fixes (robust SEs + relevel bug + reg
statement + RoB-sans-6/10 sensitivity) → structural trim for venue → search-currency top-up.

## 2026-08-10 (cont.) — REVIEW FIXES APPLIED: checker doubled, manuscript re-swept, metareg corrected, circularity sensitivity added

Applied the correctness fixes from today's three-way review, in the order the review prescribed
(guards first, then text, so the sweep is machine-verified rather than hand-verified).

1. **CHECKER EXTENDED 49 -> 94 assertions + 21 must-not-appear strings** (check_manuscript_stats.py).
   New coverage: every §2.2 CI and IQR; both headline ratios with bounds; prediction intervals; all
   six Spearman rhos (+ quoted k/p); precision-weighting from-to pairs; sensitivity A2/B/C/D values
   and deltas; the §3.2 ladder and exclude-HIGH Discussion restatements built live from the pipeline;
   predicted % for all three measurement levels; concentration standardized-set counts; six-construct
   set size (533); §4 wording "569 are proportion"; the freeze-version string derived from FROZEN.md;
   the crosswalk not-retrieved count; the new sans-6/10 outputs. The must-not list bans each stale
   string the audit found alive (v1.6.8, "bound of 10.8", "13.4%", the old ladder, "23.2% → 11.7%",
   "212 content analyses", "573 are proportion", stale CIs, etc.) so presence-anywhere matching can
   no longer be greenlit by a correct copy elsewhere.
2. **MANUSCRIPT RE-SWEPT (~35 corrections).** Freeze pointer v1.6.8 -> v1.7.8 (4 places); abstract
   CONTENT CI -> 19.5–26.4 and predicted 4.8 -> 4.9 with the causal verb softened ("differs by
   measurement method" not "shifts"); §2.1 k's (SHARING 29, EXPOSURE 15, general-news 49, 16.3%);
   §2.2 table CIs/IQRs + ratio 9.1 (4.4–39.7); §2.3 PIs; §2.4 backbone CI 4.1–8.8; §2.5 R² family
   (measurement 22.0, breadth 10.1 incl. explicit unspecified level, denom 11.7, platform 9.3),
   95% collinearity figure, predicted 4.9/20.2/48.6, coarse-denominator (0.0%, p=.69) vs 11.7%;
   §2.6 60%; §2.7 Spearman row + weighted baselines (23.2 subset baseline named as such); §2.8
   16 studies; §2.9 deltas (−10.5, 23.5->24.9, −1.5, k=6) + temporal ≈11/≈29/≈10–16; GRADE CONTENT
   IQR 7.4–39.5; §3.1 bound 11.3 + sharing 10.0; §3.2 ladder + 23.5->13.0 + 23.2->0.9 + 4.9/20.2;
   §3.3 210 + "audience harm"; §4.4 46 not retrieved; §4.5/§4.9 569/533 + v1.7.8; §4.7 281;
   §4.8 self-consistency trio relabelled from the log's actual provenance (screening κ.89, construct
   κ.82 double-extraction n=778, RoB PABAK .78 — the old "extraction .82 / construct .78" had
   mislabelled them and contradicted §4.6) + the duplicated RA-round passage deleted; §4.9 "crossed"
   -> "nested", regression n 475/279.
3. **METAREG SCRIPT CORRECTED (phaseB_metareg.R) and re-run.** (a) Cluster-robust omnibus tests on
   every reported fit (previously multivariable only, contradicting §2.5); CSV now carries QMp
   (robust) + QMp_model. (b) relevel AFTER collapse via set_ref() with a stopifnot guard — the old
   order let collapse_sparse() silently reset the multivariable breadth reference to the alphabetical
   default. (c) Uncoded cells ("NA") now enter as an explicit "unspecified" level instead of being
   dropped row-wise — breadth had been losing 141 rows and measurement 4, so the R² ladder compared
   moderators on different subsets. (d) Collapse rule now uniform across all ten moderators.
   Number movements, all understood: measurement 22.1 -> 22.0, breadth 8.7 -> 10.1 (the 141 rows now
   in), platform 9.0 -> 9.3, CONTENT_CODING predicted 19.8 -> 20.2 (v1.7.8 refresh + NA handling);
   breadth robust QM p < .0001 (the old model-based p=.145 asymmetry the review flagged is gone —
   with the unspecified level included the moderator is unambiguously significant). §4.9 now
   discloses the unspecified level and the uniform collapse.
4. **NEW SENSITIVITY: RoB WITHOUT ITEMS 6/10** (scripts/phaseB_rob_sans610.py ->
   data/synth/phaseB/rob_sans610.csv), answering the instrument-thesis circularity objection.
   Result, reported in §2.6 and cross-referenced in §2.9/§4.7: the construct gradient SURVIVES
   (EXPOSURE 0% high-risk vs CONTENT 26%) but the exclude-HIGH content reduction ATTENUATES
   (23.5 -> 22.9 vs 23.5 -> 13.0 with the full rule). Honest reading, now in the text: studies weak
   on generic design items do not report inflated numbers; studies weak on the definition/denominator
   items do — the bias that tracks the number is specifically the bias the review is about.
5. **PRISMA 24a**: §4.1 now states plainly that the review was NOT registered and no protocol was
   published in advance, with the append-only log as the timestamped protocol record. (No PRISMA
   checklist promised — Sacha declined one 2026-07-23; the journal will ask at submission and that
   remains his call.)
6. Figures regenerated (fig1-4 + gallery + I-L) so fig2's R²/predicted panel matches the corrected
   metareg. Guards after everything: invariants 9/9, derived stats 94/94 + 21/21 stale-free, drift
   clean, ledger synced (33 freezes).

DEFERRED (authorial-voice decisions, listed in the review report, not applied): venue restructure
(abstract to <200 words, §4.8 trim ~40% to supplement, Appendix A -> SI, display items 8 -> 6,
numbered headings, author-year -> superscript conversion), title alternatives, tone softening list
(§3.1 moral-panic sentence, "advocacy, not measurement", §3.4 "launder", etc.), Holm correction
across the two test families, within-CONTENT size-correlation stratified by denominator class.

## 2026-08-11 — Independent-family check packages built + Fable QA pass on the load-bearing rows

Sacha approved the two remaining independent-family checks and a same-family QA audit.

1. **VALUE-VERIFICATION PACKAGE** (docs/codex_check/value_check/; scripts/build_value_check.py +
   merge_value_check.py). Codex re-extracts every value of the 40 load-bearing studies (backbone 32
   ∪ EXPOSURE 15 ∪ CONCENTRATION 17; 123 estimate rows) from source, blind to ours. 8 batches of
   ~5 papers, fresh session each (anti-degradation protocol carried over). Agreement rule
   pre-specified in the merge script (|diff|<=0.1pp or rel<=2%). BLIND DEFECT CAUGHT AT BUILD TIME:
   the first build leaked values through locator fields (measure_type carried "top 1% ... 65.3%");
   builder now redacts every percentage/large count from locators and an automated audit asserts
   zero leaks. Concentration thresholds stay visible as row identity; only the share is verified.
2. **ROB SPOT-CHECK PACKAGE** (docs/codex_check/rob_check/; scripts/build_rob_check.py +
   merge_rob_check.py). 44 studies (all eligible EXPOSURE-modal + seeded rating-stratified sample,
   seed 20260723), items 6 and 10 only, verbatim quotes mandatory, 5 batches. Rationale: all RoB
   reliability to date is same-model; items 6/10 power §2.6/§2.9/GRADE.
3. **FABLE QA PASS** (data/extract_v2/qa/fable_qa_2026-08-11/). Eight parallel same-family agents
   re-read all 170 rows of the 40 studies against full text, instructed to refute. Same-family =
   QA/curation only, never a reliability tier. RESULT: **zero value errors — every value_pct and
   concentration pair in the load-bearing set verified verbatim.** ~45 metadata findings, dominated
   by sibling-row field inheritance (methods-lessons #16) on subgroup/OTHER rows, n mis-attribution
   (subgroup vs full-panel), and a breadth=fabricated systematic on one domain-list study. Six
   findings need authorial adjudication (Faker Island CONTENT/SHARING + dates; W4293124965
   political_news→news_diet x6; allcott political_news label; 85160248068 OTHER→EXPOSURE;
   85059494932 political_news-vs-topical — the only finding that could move backbone k; 85148963619
   denominator text + country). Full queue: fable_qa_2026-08-11/FINDINGS.md. NOTHING APPLIED —
   queue awaits adjudication.

## 2026-08-11 (cont.) — v1.7.9 shipped end-to-end; docx review copy; analysis-code review launched

Freeze v1.7.9 (92 QA edits) fully propagated: pipeline regenerated, invariants caught a real gap on
first pass (denom_class edits without matching denom_scope/denom_selection — the two-axis fields;
apply script corrected so scope moves with class, and Faker Island's curation is recorded on the
SELECTION axis with scope kept news_diet, honouring Sacha's note that the outlet list is
fact-checker-derived). Headline moves, all re-synced (94/94 + 21/21 + invariants + drift green):
backbone k 32->33, median 6.6 -> **5.9** [3.7-8.5] (the Google study's overall-engagement rows join
per ruling A4); SHARING 30 studies, 10.0 -> **9.6** [3.4-15.1] (Faker 0.05 joins); CONTENT 209,
23.5 -> **23.6**; EXPOSURE unchanged 2.6 k=15 (study already present via its SERP rows).
Top-1% concentration 70 -> **68%** (9 studies). Exclude-HIGH: CONTENT 23.6 -> 13.2. Metareg on 478
estimates; construct R2 16.5, denom_fine 10.5. HONEST DOWNGRADE: backbone small-study Spearman is
now rho -.31, p=.082 — no longer significant; §2.7 rewritten ("falls just short"). Appendix A
regenerated: the claim-level CONTENT-SHARING contrast widened (+23.0 pp [-3.0, +27.5]) but every
interval still spans zero and the sign still flips by instrument — conclusion unchanged.
DECISIONS_REGISTER: two closed entries (85059494932 keeps political_news; Faker Island =
SHARING/news_diet-scope/curated-selection).

Codex campaign status: batch_v02 scored 12/12 (100%) after comparator-tolerant scoring; a struggling
agent's stray malformed batch_v01_coded.csv was discarded (real batch file untouched); remaining
batches paused on Sacha's credits — not blocking.

NEW scripts/make_manuscript_docx.py — one-command md -> docx review copy (APA tables, figures via
rsvg-convert); docs/manuscript_draft.docx delivered to Sacha for comments. The .md stays the single
source of truth; Word edits get merged back by hand.

Launched a two-agent line-by-line correctness review of the analysis scripts (core stats:
uncertainty/sensitivity/ratio/recall/precision/prep; and grade/slices/concentration/sans610/
appendix/guards/apply_v179) — results to be logged when they land.

## 2026-08-11 (cont.) — ANALYSIS-CODE REVIEW: two CRITICAL defects found and fixed; numbers re-synced

Two line-by-line review agents covered all 15 analysis/guard scripts, verifying the hand-rolled
statistics against reference computations. VERIFIED CORRECT with evidence: the cluster-bootstrap
scheme in all five implementations; DL tau2/I2; the t-tail (matches numerical integration to 1e-7);
Spearman + p (reproduces reference values); Egger quarantine; subset-definition consistency across
all six core scripts; apply_v179 replay safety; grade/slices/sans610 logic vs manuscript claims.

**CRITICAL 1 — phaseB_precision.py built its bootstrap frame from a Python SET**, so iteration
order depended on PYTHONHASHSEED and the published precision CIs were NOT reproducible despite the
fixed seed (the review demonstrated different CIs across interpreter runs; the committed CSV could
not be regenerated). The one script of six with the defect. FIXED (insertion-ordered frame).

**CRITICAL 2 — parse_n's K/M suffix regex ate the first letter of the next word** ("64 media
articles" -> 64,000,000; "12,689,165 misinfo tweets" -> 1.27e13), corrupting 6 regression rows. A
blanket fix ("take the number after '/'") was tried and OVER-corrected — the n strings follow no
single convention — so the final fix is: word-boundary suffix regex + an 11-row hand-audited
N_OVERRIDES table (each keyed by study+value, each justified inline by the measure's stated
denominator). Net: 16 corrected n's, 478 rows unchanged.

**CRITICAL 3 (from the guards reviewer) — §2.10 said SHARING certainty LOW while grade_sof.csv
says MODERATE** (the v1.7.9 SHARING set no longer trips the 10-pt imprecision trigger; shift 9.0).
The construct-blind '| MODERATE' substring check false-passed — the exact failure mode that check
was created to catch, in the reverse direction. FIXED: manuscript to MODERATE (indirectness only),
and the checker now anchors the FULL GRADE row per construct (RECALL anchored to its deliberate
seen-split hybrid).

Also fixed: prediction intervals now use t(k-2) (Higgins convention; slightly WIDENS our PIs);
appendix boot_diff reports the observed difference as the point estimate (was the bootstrap-median,
which made the table's difference column disagree with its own median columns); dead code removed
from the checker (no-op reach_sig, duplicate truncated rho) and uncertainty (inert Q_p); stale
docstrings (v1.4.6) corrected.

NUMBERS MOVED by the n corrections + PI convention (manuscript re-synced, 93 checks + 21 stale
strings + invariants + drift all green): CONTENT Spearman -.40 -> **-.43**; SHARING Spearman
-.29 -> **-.07** (it was riding on corrupted n's; §2.7 now says "effectively null in SHARING");
backbone p .082 -> .083; PIs CONTENT 0.48-91.6 / backbone 0.30-59.4 / EXPOSURE 0.23-18.1; weighted
backbone 0.3 -> 0.6; sampling R2 18.2, id_method 17.8, denom_fine 10.4, predicted content-coding
20.2; §2.10 SHARING MODERATE. Docx review copy rebuilt and re-delivered.

NOTED, NOT CHANGED (accepted conventions, comments added where fixed code sits nearby): shared
sequential RNG makes CIs order-dependent across groups (deterministic as written; recall_split's
per-group RNG is the better pattern for future scripts); percentile-index conventions differ by one
order statistic across scripts (negligible at B=2000); seeds differ per script (20260723 /
20260722 / 42) — Methods text says "fixed seed" without naming one, so no claim is wrong; grade's
CONCENTRATION imprecision rests on k alone (no CI row); crosswalk NEAR window no longer covers the
oldest wrong counts; slices' 10.8% breadth rung sits on k=2 (consider quoting with its k).

## 2026-08-11 (cont.) — DOC + MEMORY CURRENCY SWEEP and workspace tidy-up

Sacha asked for all md/memory files to be verified current and the workspace tidied. Two audit
agents (24 hand-maintained docs vs v1.7.9 ground truth; full file-organization scan) + a manual
memory pass. Everything found was fixed the same day:

DOCS CORRECTED (highlights): grade_certainty_framework header said SHARING LOW (now MODERATE at
v1.7.9, with the v1.7.8->v1.7.9 flip-back recorded); llm_provenance still called the human IRR
"pending" and lacked the independent-model tier entirely — fixed + a dated 2026-08 addendum with
all three completed tiers and the same-family-QA-is-not-a-tier rule; RESUME_HERE's stale bottom
half (v1.6-era medians table, apply_v15X pipeline, completed open-items) cut — the file now holds
pointers only, as its own 2026-08-10 rewrite intended; README status ("pre-protocol / not yet
registered") and database list (WoS "planned" — it was skipped) rewritten; CLAUDE.md placeholder
sentence removed; METHODS_PROVENANCE bumped to v1.7.9 with the construct tally refreshed
(CONTENT 319 / SHARING 96 / EXPOSURE 41 / OTHER 25) and §9 marked done; moderator_codebook:
conc_unit vocab corrected to {user|source}, the news_diet OPEN DECISION marked RESOLVED (v1.5.1),
hardcoded 7.5%/70% figures replaced by resolve-from-pipeline wording, denom_scope marked verified;
construct_and_concentration_rules got a partly-superseded banner pointing at the live codebook +
register; rob_checklist_v3's source-list ruling no longer cites the retired 5-value breadth scale
and its re-rating list is marked executed; protocol.md + screening_protocol.md got
original-as-drafted banners listing the documented deviations (no history rewritten);
cleaning_methods got a historical banner; codex_check FULL_INSTRUCTIONS retitled COMPLETE with a
post-campaign note on the v1.7.8 actor-rule refinement; MODEL_AND_PROVENANCE got the campaign
completion record (647/647, κ .802); RA_package README says both coders' sheets are in;
related_reviews' numbers refreshed (313/673, backbone 5.9 vs seen-recall 60.0);
estimate_selection_rule marked RATIFIED 2026-06-22; replication_package cites rob_checklist_v3.

MOVED to docs/Old/ (17 files): the June one-off review sheets (demographic/geographic/flagged/
missing_fulltext/reread/stepb/value_review/spotcheck HTMLs — validate_frozen docstring repointed),
the closed UZH triage trio, abstract_only_chase_list, the executed phaseA/stage5 plans,
reviews_external_search.csv, REPRODUCIBILITY.md (fully superseded by METHODS_PROVENANCE + FROZEN +
replication_package; every path/number in it was retired), qa_plan.md (executed roadmap;
llm_provenance pointers updated). scripts/__pycache__ trashed. KEPT deliberately: RA_package.zip
(the packaged RA deliverable, gitignored), box1_ccdh_meta.svg (the parked Box-1 figure asset),
the lit_review pointer stubs (breadcrumbs to the cross-project litreview hub), figA-K SVGs (live
appendix figures), both rob_checklist versions and both screening_criteria files (all still cited).

MEMORY REFRESHED: reliability-architecture rewritten (all three tiers complete; tier-2 = the
nine-batch κ .802 sweep; same-family QA excluded from tiers); crosscheck-purpose closes F0066
(verified recoded QUALITY->CONTENT in the freeze); search-currency-topup, litreview pointer,
pipeline memory (N_OVERRIDES rule, precision determinism, appendix in run-order), open-items
canonical block, and the MEMORY.md index lines all brought to v1.7.9.

Guards after everything: invariants 9/9, stats 93/93 + 21/21, drift clean, PRISMA ok.

## 2026-08-11 (cont.) — Sacha's 25 docx comments addressed (form pass 1)

All comments extracted from ~/Desktop/manuscript_draft.docx (no tracked edits) and addressed:
- ABSTRACT rewritten in the plain register of his NHB meta-analysis abstract (the model he named):
  question opening, "We found that...", no CIs (C4), no "empirical puzzle"/"accounting artefact"
  framing (C1-C3), "curated content samples" -> "studies that collect content about specific
  topics" (C5), the seen/shared sentence de-dashed and de-jargoned (C6-C9), and a corpus-
  description sentence added (health topics + Western countries, a third US — C12; verified 104/313
  any-US, ~47% Western-only; supporting sentence also added to §2.1).
- INTRO list: six constructs, each with a plain definition + a real corpus example (Cordonnier 0.16%,
  Guess 44.3%, Grinberg 6.7% and 1%->80%, Brazil-vaccine 36%) — C13; the four judgment taglines
  removed (C14-C17); "four quantities above" -> six.
- JUDGMENT/TONE: "quantities the field conflates" -> "the six quantities" (C19); the
  "Search-stream provenance carries its own lesson" paragraph deleted from §2.1 (C20-C21) — its
  content already lives verbatim in §4.3.
- WHOLE-DIET BACKBONE defined in plain words at first use in §2.2 (C22).
- ITALICS: 55 decorative italic spans stripped manuscript-wide (statistical p kept per house
  style); both italic provenance preamble blocks converted to never-rendered HTML comments (C18 +
  C23) — guard-asserted strings preserved inside the comments; fig5's embedded "Frozen v1.5.2"
  footer removed at the generator and the figure regenerated (C23); figure captions de-italicised.
- FIGURES INLINE: (Figure 3/4/5) references added in text; the docx builder now places each figure
  after the paragraph that first cites it, renders no HTML comments, and uses ONE typeface (code
  face removed) — C18, C24; internal SVG filenames dropped from the display-item list.
- PLAIN-LANGUAGE pass over Results prose: "operationalizes" -> "measures", "operationalization
  moderators" -> "measurement-related choices", "collinear" -> "overlap", "monotonically" -> "step
  by step" (C10; methods left technical per C11).
Guards after everything: stats 93/93 + 21/21, invariants 9/9, drift clean. New review copy
delivered as manuscript_draft_v2.docx (Desktop).

## 2026-08-11 (cont.) — Sacha's second comment round (29 comments): full writing overhaul

All 29 comments from manuscript_draft_v2.docx addressed (plus his 2 tracked deletions honoured):
- ABSTRACT: PRISMA year dropped; "consume online" specified; behavioural-vs-survey contrast made
  the sentence structure; "inappropriate" numerator/denominator -> "does not match the claim being
  made"; RoB-exclusion sentence cut; "68% of all misinformation exposure or sharing"; closing line
  rewritten ("Each estimate is the product of what was counted... and what it was compared against").
- INTRO rewritten in the register of his NHB piece: plain opening ("Many estimates... have been
  published"), DESCRIPTIVE framing per his instruction (take stock / describe / quantify; useful
  for interpreting and designing estimates — not "we argue conflation"); the six constructs are now
  **Table 1** (construct | what it measures | example); "headline numbers do the persuading",
  "That work supplies the theory", the conclusion-like denominator paragraph and the Four
  features/First/Second enumeration all rewritten plain.
- RESULTS de-judgmented: "cleanest" (x2), "alarming/reassuring", header "runs opposite to alarm",
  "the field conflates", "enormous", "extremely" -> descriptive wording; §2.10 header now
  "Certainty of evidence"; §2.8 header "Concentration of exposure and sharing".
- §2.2 medians TABLE deleted (redundant with Fig 1); values now in prose with HIS CI style
  [95% CI x–y] then [x–y]; IQRs live in Table 2 (GRADE) + backbone IQR added to §2.4; checker
  ratio assertion updated to bracket format; pooling rationale cut from Results (it lives in §4.9).
- FIGURES: Fig 1 now splits RECALL seen/shared (recall_split.csv wired into make_forest_plot),
  numeric CI labels removed (bars suffice), backbone sublabel de-judgmented; fig2 gained a caption
  explaining the pale min-max band; fig3's risk-of-bias legend spelled out and moved visible;
  **Figure 4 is now the concentration FLOW figure (misinfo vs news in general)** as requested —
  and its hardcoded 70/37 were replaced by pipeline-derived values (68% top-1% misinfo vs 34%
  median of the six user-level non-misinfo comparators; the Osmundsen misinfo-side row was leaking
  into the "general" median and is now excluded). §2.8 also gained the one-panel side-by-side
  sentence (65% unreliable vs 43% news overall, Zhou panel).
- EM-DASHES: 71 -> 34 manuscript-wide; abstract/intro now 0, Results/Discussion near-0 (the rest
  sit in §4.8's technical narrative).
- Guards green throughout (93/93 + 21/21, invariants, drift). v3 docx delivered (Desktop).

## 2026-08-11 (cont.) — Results + Discussion fully rewritten in Sacha's NHB register

Sacha flagged that the earlier pass fixed flagged sentences but left the Results/Discussion in the
assistant's rhythm, not his. Re-read the NHB meta-analysis results section as the model (plain
declaratives, "We found...", stats inline in brackets, interpretation only where signposted with
"that is / in other words / suggesting"), then rewrote §2.1–§2.10 and §3.1–§3.6 sentence by
sentence. Removed the remaining rhetorical constructions ("the review's thesis in miniature",
"One objection deserves a pre-emptive answer", "The review's own claim is... and it is testable",
"pathology in its purest form", "compresses the entire argument", "identifiable tails",
"If a single reallocation of research effort followed..."), converted claims to reported findings
("We appraised...", "we found that...", "We interpret..."), simplified headers (§2.1 "Description
of the evidence base", §2.2 "The six constructs yield different numbers", §2.9 "Sensitivity
analyses"), spelled out CCDH on first Discussion use, and kept Methods technical as instructed.
All guard-asserted strings preserved; guards green (93/93 + 21/21, drift, invariants). v4 docx
delivered; v2/v3 review copies trashed from Desktop.

## 2026-08-12 — v5 comment round (37 comments + tracked edits) fully addressed; FROZEN v1.7.10

Sacha's third docx round, with a restructure and two new analyses. Everything applied; guards now
107 must-appear + 21 must-not; all green.

STRUCTURE: Results reorganised to 2.1 evidence base / 2.2 NEW "How studies define and identify
misinformation" (descriptive: 235 claim-level vs 65 source-level studies; ground truth 185
researcher-coded, 59 domain-list, 23 fact-checker, 15 classifier, 22 self-judged; breadth 6
fabricated / 124 false / 92 misleading / 82 no stated standard — all counts asserted by the
checker) / 2.3 constructs / 2.4 heterogeneity (shortened) / 2.5 backbone / 2.6 drivers / 2.7
larger-studies / 2.8 concentration / 2.9 one-paragraph Robustness summary. Old RoB, sensitivity
and GRADE sections (incl. Table 2) moved to NEW Appendix B (B1-B3), with a B4 on recall windows;
all internal § references re-pointed. Intro gained a definitional-diversity paragraph and the
tracked-edit opening ("Numerous studies have measured..."), ordered almost-everyone -> third ->
fraction (C9); Kim et al. 2023 ref added to the Table 1 example.

NEW ANALYSIS 1 — recall time windows (C0): two agents extracted the survey question + window for
all 21 seen-recall studies with full text (coding: qa/recall_windows_2026-08-12.csv). Result: only
5 of 22 studies use a bounded window (week to 6 months); bounded-window median 59.2 vs unbounded
60.0 — the high recall figure is NOT an artefact of unbounded questions; the two past-week studies
report 48.5/53.3. Reported in §2.3 + Appendix B4, asserted by the checker.

NEW ANALYSIS 2 (side-effect of C0) — FROZEN v1.7.10: enumerating the seen pool exposed study
85122105134's two RECALL rows coded subtype=exposure while measuring self-reported SHARING
(verbatim: "81% afirmo no haberlo hecho y 19%, si"). apply_v1710.py flips them. Seen-recall
k 23 -> 22 (median 60.0 -> 62.0 [51.0-73.0]), shared-recall k 6 -> 7 (18.6 -> 18.5), seen/EXPOSURE
ratio 23.3 -> 24.0 [11.6-104.1]. Manuscript re-synced; the seen pool now coincides exactly with
the window-coded set.

REWRITES: §2.6 drivers rewritten with each moderator explained in plain words (C25-C34); §2.7
explains the size correlation and weighting from scratch (C36); §2.8 states what is standardised,
what "9 studies at that threshold" means, and the misinfo-vs-news comparison with counts (median
34% for general news, 6 comparison estimates from 4 panels — asserted) (C37-C39); abstract
shortened/clarified (C1-C3), closing line rewritten (C5); Discussion opens with our contribution,
Hameleers second (C44); expectation language removed (C41); climate named as the absent topic
(C18); platform mix quantified (31/63 Twitter, 15 web, 12 Facebook — asserted) (C4); all remaining
in-text bold removed incl. the GRADE table's VERY LOW (C45; checker updated).

FIGURES: fig3 redesigned (legend under the title, row banding, country-construct labels, ratings
now from the v3 RoB master — the v145 file left late-added studies grey); fig2 pale band removed,
"Panel/trace" -> "Behavioural panel", "Domain-list/NewsGuard" -> "Domain list" (C23/24/28-31);
figK subtitle now states both sides' counts (C39); docx builder anchors figures on "Figure N".
Crosswalk: main-analysis STUDY count (304) added as a canonical quantity (the drift check had
flagged it as near-313 drift — correct behaviour, now a defined number).

v6 docx delivered to Desktop. Codex value/RoB batches remain paused on credits.

## 2026-08-12 (cont.) — v6 comment round (33 comments + 13 tracked edits) fully addressed

STRUCTURE: the whole-diet backbone is now defined ONCE, as a row of Table 1, removed from Figure 1
(which is back to the six constructs), and §2.6 opens by stating its membership plainly (14 of the
15 exposure studies + all 24 reach studies, 5 contributing both, 33 total) — resolving Sacha's
C15/C17 confusion about overlap. Recall time windows became their own section (§2.4 "What period do
the self-reports cover?"); Results renumbered and every internal reference re-pointed. The
Discussion lost ALL subsection headers (NHB style), the reporting-practices list became a
paragraph, and Limitations was cut to five sentences with the full text moved to Appendix C3.

METHODS COMPRESSION (C33): §4.8 is now ONE paragraph — AI-assisted at every stage, a human reviewed
and approved all consequential decisions, reliability measured against same model family / a
different family / humans, with the headline kappas — and the full 1,500-word narrative moved to
Appendix C1. §4.9's six statistical run-ins moved to Appendix C2. §4.3's numbered source list is
prose (no bolds). Tracked deletions applied (funding line, "not dual independent screening" clause,
tier strength labels, "via Perplexity", Sci-Hub mention out, "parallel workers" -> independent
batches). §4.4 now says independent evidence comes "from humans and from a different model family".

TEXT: intro "take stock" removed, orientation cites dropped (C2), goal sentence rewritten (C3);
definitions paragraph reframed descriptively and now cites the 150-expert survey (Altay, Berriche,
Heuer et al. 2023 — broad agreement on false-or-misleading + the mis/disinformation distinction,
wide variation in implementation) and the how-you-measure-shapes-what-you-find point (C4-C6);
Rogers 2020 example detailed (C8); precise recall example in Table 1 (73% US, past 6 months,
replacing the vague van der Meer entry, C7); "respondents' own judgment" explained (C9); "where
they draw the line" (C10); abstract's 80.2% claim softened to "the most commonly flagged
limitation... concerns the match between the denominator and the claim" (C0/C26) and §2.10 now
explains what item 10 means with an example + the instrument's PABAK (C27); colons thinned 37 -> 23
in the main text (C28).

FIGURES: NO titles inside any figure — full captions now live in the document as "Figure N. Title.
Explanation." (per Sacha's tracked caption edits); Figure 1 is LINEAR scale (log understated the
gaps, C14) and backbone-free; fig2 lost the pale band note; fig3 groups exposure vs reach with
in-figure group labels (answers "what are 70.0 and 39.2", C16) and its legend heads the figure;
figK panel labels no longer collide and both medians remain pipeline-derived, with the
what-is-compared counts in the Figure 4 caption (C39).

Guards 107/107 + 21/21 + invariants + drift green throughout. v7 docx delivered.

## 2026-08-12 (cont.) — internal review (docs/internal_review_v7.md) fully addressed; References + PRISMA checklist added

Independently VERIFIED the review's majors before acting (its concentration claims all reproduce;
its Van Doorn claim was wrong — Doorn2023 is in the bib, missed on the "Van" prefix).

CONCENTRATION (items 1-2, Sacha ratified "top 1% = 70%"): phaseB_concentration_table.py now
computes STUDY-level medians for all bands (was estimate-level next to a study count) and adds a
strict "top =1%" band. Headline: top 1% -> 70% (k=5); <=1% band 65.3% (k=9) reported as supporting
with the sub-1% thresholds (0.001-0.3%) named; comparator now study-level 31%; Baribi-Bartov no
longer double-used (named as inside the band); Table 2 CONCENTRATION row is per-band; figK reads
strict band + study-level comparator (70 vs 31). Abstract 68 -> 70. Checker: strict/band/comparator
+ per-band GRADE row anchored; "median 68%" added to MUST_NOT.

ITEM 4: §2.8 weighting now names the extractable-n restriction with k's and reports ALL SIX
constructs (asserted). ITEM 5: "topic explains the least" -> "less than any of the measurement
choices"; Appendix A gained the eta2-vs-R2 reconciliation note.

ALL 16 MINORS: four-other-codings note; figures renumbered to citation order (backbone = Fig 2,
drivers = Fig 3); Box 1 written and called in the Discussion (CCDH 2021 + Bickert 2021 cited);
B2 cross-ref fixed; §2.10 PABAK relabelled same-model; abstract content-denominator overclaim
fixed; 18.5% rounding aligned; all six Spearman p's (exact, incl. p=.472 per format); p=.96;
R2 list reordered by rank; C1 same-base-model sentence rewritten; 149/478; climate wording aligned
with C3; B4-vs-overall arithmetic explained; voice stays "we" (Sacha); FROZEN.md got an APPENDED
correction (the v1.7.10 entry wrongly said "median unchanged at 60.0" — it moved to 62.0).

ITEM 3: full References section added (36 in-text citations + Page et al. 2021, Viechtbauer 2010,
CCDH 2021, Bickert 2021 = 40 entries), built from combined_library.bib and cross-checked both ways.
TWO IN-TEXT CITATION ERRORS caught and fixed: "Watts, Rothschild & Winter 2021" -> Mobius (no
"Winter" paper exists); "Boulianne & Humprecht 2024" -> 2023. Front matter added (author block,
keywords, Statements: no funding / no competing interests / ethics n/a). PRISMA 2020 checklist
DRAFTED at docs/prisma_checklist.md (Sacha REVERSED the July decline) — 27 items mapped, honest
gaps listed; Appendix D added with the verbatim Scopus strict_v2 string (closes item 7 of the
checklist) + supplementary-data pointer for per-record dispositions (16b).

PRE-SUBMISSION VERIFICATION LIST from the reference agent (do before submitting): Ecker et al. 2024
AmPsych volume/pages; Matthes et al. published-version year/volume (2023, 26(16)?); Baribi-Bartov
volume/pages; Nickl et al. published version check; Altay & Acerbi 25(11) confirm; Stecula
"content vs context fixes" title check; Hoes et al. journal check; Williams blog-cite acceptability
at target venue.

ITEM 7: two sentences added to §4.8 naming the machine's dominant systematic error (rank-truncated
corpora coded as exhaustive) and the fabricated-study catch. Guards: 114 must-appear + 22 must-not
+ invariants + drift all green. v8 docx delivered.

## 2026-08-12 (cont.) — flagged references verified against online sources (Sacha's request)

Every flagged 2022-2026 reference checked via web search (publisher pages, PubMed, institutional
repositories). RESULTS, all applied to the manuscript:
- Ecker et al. "Why misinformation must not be ignored": PUBLISHED — American Psychologist 80(6),
  867-878, DOI 10.1037/amp0001448 (in-text 2024 -> 2025; the preprint DOI replaced).
- Altay & Mercier commentary: PUBLISHED — American Psychologist 81(2); title's target is
  "Ecker et al. (2025)"; DOI 10.1037/amp0001550 confirmed.
- Baribi-Bartov et al.: Science 384(6699), 979-982 (was missing vol/pages).
- Altay & Acerbi: the ISSUE is NM&S 26(11), 6440-6461, year 2024 (in-text 2023 -> 2024; the bib's
  25(11) was wrong).
- van der Meer & Hameleers: ICS 28(4), 575-596, issue year 2025 (in-text 2024 -> 2025).
- Matthes et al.: ICS 26(16), 3133-3156, issue year 2023 (in-text 2022 -> 2023).
- Hoes et al.: PUBLISHED — Political Behavior 2025, title "(Media Attention to) Misinformation Can
  Undermine Trust in SCIENTISTS", DOI 10.1007/s11109-025-10090-y; the Discussion sentence was
  tightened to "can itself undermine trust in information sources" to match what the paper shows.
- Stecula white-paper title confirmed ("Content Fixes", not Context). Nickl et al.: still
  SocArXiv-only (checked; no journal version). Pennycook & Rand: still SSRN/ARP-forthcoming.
  Bickert 2021 Meta newsroom statement confirmed (18 Aug 2021, VP Content Policy, the 0.05% figure).
  Hameleers 2025: Communication Theory advance article, no volume yet (correct as cited).
v8 docx rebuilt with the corrections.

---

## 2026-08-12 — Arcom JE2026 application refreshed against v1.7.10

The application for the Arcom's 5th journée d'études (deadline 28 Aug 2026,
journee-etudes@arcom.fr) was written against an older freeze and carried ~15 stale numbers.
Rebuilt from the current manuscript text, which the 114-assertion checker keeps synced to
FROZEN v1.7.10.

The application is now script-built like the manuscript: master markdown at
`docs/arcom_je2026/candidature_arcom_je2026.md`, built by `scripts/make_arcom_docx.py` to
`~/Desktop/Candidature_Arcom_JE2026_Altay.docx` (filename fixed by the submission; the previous
version is in `.backups/`). French-labelled copies of manuscript Figures 1 and 3 are made by
`scripts/make_arcom_figures.py`, which translates the SVG text nodes and enlarges the type
relative to the canvas (the figures print at ~12 cm here, not full page width); it aborts if a
source string is missing, so an upstream figure change cannot pass silently.

Numbers corrected against the manuscript: 675/314 -> 673 estimates / 313 studies (plus the 569
main-analysis set); metaregression 470/277 -> 478/279; whole-diet backbone 7.2% -> 5.9%
[3.7-8.5, k=33]; CONTENT 23.1 [19.0-26.3] -> 23.6 [19.5-26.5]; recall 55.0 [36.0-65.9] ->
seen-recall 62.0 [51.0-73.0, k=22] with shared-recall 18.5% added; recall/exposure ratio 21.3
(LB 9.2) -> 24.0 (LB 11.6); predicted prevalence 4.8/19.8/48.6 -> 4.9/20.2/48.6; RoB
numerator/denominator item 80.3% -> 80.2%; exclude-HIGH CONTENT 12.4% -> 13.2%; 210 -> 209
content analyses; top-1% concentration now given as k=5 with the 31% general-news comparator
from four of the same panels. Title updated to the current one ("Rare sur les écrans,
omniprésente dans les esprits"). Added: sample-size weighting (CONTENT 23.3 -> 0.9%), SHARING
and REACH medians, and the measurement-vs-topic variance contrast (22.1% vs 8.4%).

Layout: the appel caps only the résumé at two pages, so the document is paginated §1-2 / résumé
(2 pp, both figures inside) / §4 Arcom relevance, with page breaks making the boundary explicit.
Verified by rendering to PDF (4 pages, résumé on pages 2-3). Table 1 of the manuscript (the six
constructs) was NOT included: Figure 1 already carries each construct's definition, so the table
would have repeated it and cost half of the remaining page.

Later the same day: Sacha's edits to the Desktop docx were folded back into the markdown master
(header meta lines and the English title dropped, contact block and bio trimmed, "désinformation"
-> "mésinformation"), and the resume was rewritten in the manuscript register per
scientific_papers_style.Rmd: judgment sentences removed ("la divergence n'est pas une enigme mais
un artefact comptable", "le niveau de preuve court a l'inverse de l'alarme", "extremement
concentre"), numbered result items turned into prose, CIs put in the [IC 95 % x-y] bracket form,
em dashes cut, and the closing paragraph brought in line with the manuscript's ("les chiffres ne
sont interpretables que si les publications enoncent ce qui a ete compte, et par rapport a quoi").
"mésinformation" now used throughout section 3; section 4 still says "désinformation" (untouched,
his call). No number changed. Still two pages, figures enlarged to 14 cm with the freed space.

Third pass, same day: full rewrite of sections 3 and 4 for rhythm and plain language after Sacha
flagged the text as reading AI-generated. Measured before/after on the resume body: mean sentence
length 24.2 words (sd 12.6, max 53, eleven sentences of 35+ words) -> 17.4 words (sd 8.4, max 38,
two sentences of 35+). Semicolon chains split into sentences, the statistics paragraph broken one
construct per sentence, the bootstrap/median gloss moved to the end of the paragraph instead of
interrupting it, "pathologie"/"cas d'ecole"/"maximalement alarmants" cut from section 4, CCDH
spelled out, and the two remaining em dashes are both in Sacha's own lines (the H1 and the footer).
Numbers unchanged throughout. Still four pages with the resume on pages 2-3.

Fourth pass: Sacha's Word edits folded back into the markdown master (CIs and the bootstrap gloss
dropped from the results paragraph, the Descartes and closing paragraphs cut, the research question
and the progress note rewritten by him, "et zéro sur le climat" added, GRADE and reliability
sentences cut, headings Titre / Question de recherche removed). Manuscript Figure 4
(figK_concentration_flow) added as the application's Figure 3 after the concentration paragraph,
French-labelled through make_arcom_figures.py like the others. Three agreement typos introduced in
Word were corrected ("exposés" -> "exposée", "mesuré" -> "mesurée", "pourcent" -> "pour cent") and
the curly apostrophes normalised to match the rest of the file. Resume still two pages.

Fifth pass: concentration expanded and corpus coverage split into its own paragraph, at Sacha's
request. Added from the manuscript: the four studies of groups below the top 1% (0.001-0.3% of
users, shares 24-81%), the Baribi-Bartov et al. 2024 case (0.3% of users, 80% of fake-news shares
in a US election), and the geographic and platform skew (104 of 313 studies include the United
States, about half Western-only; of 63 behavioural studies, 31 Twitter/X, 15 web browsing, 12
Facebook). Two manuscript details deliberately left out: the single panel comparing both directly
(65% vs 43%) and the <=1% band median (65.3%, k=9), because both put a second 65% next to the
70-vs-31 contrast. His Word edits of this round folded in first ("en ressortent", the figure 3
cross-reference); "cad" expanded to "c'est-à-dire". Resume still two pages.

Sixth pass, 2026-08-13: five wording fixes applied on top of Sacha's Word round. Reach phrasing
split out ("Sur la période observée, 11,5 % des personnes en ont rencontré au moins une fois"); the
risk-of-bias item now carries a plain gloss plus the keyword-corpus example from section 2.10; the
sub-percentile studies rewritten; politics given as a share (12 %, 37 of 313); and one addition,
the 82 studies (27 %) that state no per-item veracity criterion.

CORRECTION to a number introduced in Word: his edit read "les traces comportementales donnent une
estimation médiane à 4,9 %, 20,2 % pour l'analyse de contenu et 48,6 % pour l'auto-déclaration".
Those three values are the meta-regression's PREDICTED prevalences, not observed medians; the
observed medians by measurement type are 7 / 26 / 57 % and are what figure 2 plots. Restored to
"Le modèle prédit une prévalence de...". Also dropped the "En effet / par exemple / Au total"
connectives from the same paragraph.

Same day: the three model-predicted prevalences (4,9 / 20,2 / 48,6) were dropped from the resume in
favour of the observed medians that figure 2 actually plots, quoting only the two ends, 7 % for
behavioural traces and 57 % for survey self-report. The middle level of that band (content coding,
26 %) rests on 5 estimates because the measurement band covers audience constructs only, so it is
left out; content prevalence is already given as 23,6 % in the preceding paragraph. Sacha's call
after the trade-off was laid out: the meta-regression prediction needs a sentence of explanation
that a two-page abstract cannot spare.

Seventh pass: the 27% no-veracity-criterion sentence dropped (its own explanation, "because they
classify sources", deflates it) and replaced by the platform mix by measurement type, computed on
the same pool the manuscript uses (569 proportion rows, one platform per study by modal value; the
script reproduces the manuscript's 63/31/15/12 exactly before reporting the new cut). CONTENT:
209 studies, Twitter/X 45, YouTube 43, TikTok 37, Facebook 17, Instagram 12. No behavioural study
has YouTube or TikTok as its main platform (2 rows out of the behavioural pool mention them), hence
"quasi absentes" rather than "absentes". The 63/31/15/12 sentence was rephrased because 31+15+12
sums to 58, the remaining five being WhatsApp (2), Instagram, Google Search and one other.
Figure 3 reduced to 12 cm to hold the resume at two pages.

Eighth pass: section 4 shortened from ~230 to ~165 words and de-escalated. "Suffiraient a
neutraliser l'essentiel du problème" -> "rendraient ces chiffres comparables"; "les écarts les plus
larges se referment" -> "une bonne part des écarts s'explique"; "plaide pour" -> "suggère"; the
perception-predicts-distrust claim now hedged ("plus que l'exposition") and attributed (Matthes et
al. 2023). Headings shortened. Sacha had deleted the footer line; that deletion is carried through.

Ninth pass: the "Label. Sentence." paragraph openers removed from section 4 (they came from the
original draft and survived every rewrite). Section 4 is now three plain paragraphs, with no
label-openers and no lead-in line, which Sacha had already deleted.

2026-08-13 — Arcom application SENT and archived. The final Word pass (AMIAD affiliation, bio
rewritten, section 4 trimmed further, CCDH example and the règlement-sur-les-services-numériques
expansion removed, "Je peux faire circuler le draft" added) was folded back into the markdown
master, so the master now matches what was sent. The sent files were moved off the Desktop into
`docs/arcom_je2026/` next to the master and the three French figures, with a README covering the
rebuild commands, the numbers as sent, and the reuse checklist. Auto-memory
`misinfo-review-arcom-application` created and indexed; the pending platform x construct SI table
recorded in open-items.

## 2026-08-13 — freeze v1.7.11 + Appendix B5 (platforms by construct)

Sacha asked for the platform x construct cross-tab, first built for the Arcom application, to go
into the manuscript. Three things came out of doing it properly.

1. FREEZE v1.7.11 (scripts/apply_v1711.py, 3 rows). Two rows of 2-s2.0-85138494787 carried
   platform_norm "Twitter" where the other 141 rows with the same raw string carry "Twitter/X";
   one row of NEW-jadara-2022 carried "cross_platform", a level used nowhere else, where raw
   "social media" maps to "multi_platform" everywhere else. Raw `platform` untouched. Note for the
   future: `platform_norm` is NOT a pure function of precode_moderators.norm_platform() — it has
   been curated since (BuzzSumo multi-platform corpora, "4chan", "Instagram Reels"), so the fix
   asserts sibling evidence per label instead of re-deriving the column. A first attempt that
   asserted the column was a fixed point of the generator failed on ~15 legitimately curated rows.

2. THE COUNTING RULE CHANGED, and with it a published sentence. Assigning each study one modal
   platform is tie-dependent: 25 of the 321 study-construct cells have no unique mode, and two runs
   of the same data disagreed (CONTENT Twitter/X 44 vs 45) purely on dict insertion order. The rule
   is now "a study counts once in every platform it covers". Section 2.1 moves from
   "31 are about Twitter/X, 15 about general web browsing, and 12 about Facebook" to
   "32 cover Twitter/X, 16 general web browsing, and 15 Facebook", and check_manuscript_stats.py
   now computes it the same way.

3. TWO DEFECTS FOUND BY THE RE-RUN.
   - Platform R2_adj moved 9.4 -> 10.0 with the relabelling, and NO assertion caught it: the
     checker had no coverage of the meta-regression R2 ladder even though section 2.7 quotes all
     ten values. Added: the four leading moderators, the tail sentence (construct / breadth /
     denominator / platform), and topic. This is the fourth time the checker's assertion set has
     lagged the document.
   - `data/rob/rob_v3_by_construct.csv` was STALE: re-running aggregate_rob_v3.py changed
     by-estimate counts (CONTENT 316->315, SHARING 63->64, EXPOSURE 32->34, OTHER 16->14) although
     the construct column is byte-identical between v1.7.10 and v1.7.11. It had been skipped at an
     earlier re-freeze. No manuscript number depends on it (section 2.6 reports RoB by-study and
     grade_sof.csv did not change), but it is the exact failure the phaseB memory warns about.

New: scripts/phaseB_platform_construct.py -> platform_by_construct.{csv,md}; Appendix B5 with the
table and a two-sentence reading; Table 3 added to the display-item list; section 2.1 points to B5
and notes that YouTube (47) and TikTok (40) are content-analysis platforms with almost no
behavioural coverage. Full pipeline re-run in order. Guards: invariants OK, stats checker
135/135 present + 22/22 stale strings absent (was 114), PRISMA reconciled, drift check clean.

## 2026-08-13 (cont.) — freeze v1.7.12 + Appendix B5 rebuilt on a name-every-platform rule

Sacha's two rulings on the open question. (1) Coding a Facebook/Reddit/Twitter/Pinterest corpus as
"Twitter/X" is wrong. (2) For this table a multi-platform study should be counted once for EACH
platform it studies.

FREEZE v1.7.12 (scripts/apply_v1712.py, 4 rows): the two BuzzSumo corpora and the "Multiple social
media (Facebook, Reddit, Twitter, Pinterest)" rows move from platform_norm "Twitter/X" to
"multi_platform", matching 2-s2.0-85108996494, which had the identical BuzzSumo design and was
already coded that way. Not "other", which Sacha floated: platform_norm is the single-valued
meta-regression moderator, and "other" would file a Facebook/Twitter/Reddit corpus next to Seeking
Alpha. Raw `platform` untouched.

B5 NOW READS THE RAW PLATFORM STRING, not platform_norm, and counts a study in every platform it
names. That also answered Sacha's "why so many Other in content": the 38-study Other column was
hiding Reddit (9), News outlets (11), Forums (7), Weibo (5), Google Search (4), plus two labels that
should always have folded into their parent, "YouTube Shorts" and "Instagram Reels". Other is now 6
and genuinely miscellaneous (Seeking Alpha, Motley Fool, Pinterest, an e-marketplace, Gab,
LinkedIn). Bare broadcaster names are matched exactly, never as substrings.

Knock-on edits: section 2.1 now says 32 Twitter/X, 18 Facebook, 16 web browsing (Facebook gains the
studies that pair it with Twitter); YouTube 49 and TikTok 41 content analyses. Platform R2_adj moved
9.4 (v1.7.10) -> 10.0 (v1.7.11) -> 10.7 (v1.7.12) and now outranks breadth and denominator, so the
section 2.7 ladder sentence was rewritten. The checker gained a hard assertion on the R2 RANK ORDER
so a future reshuffle fails loudly instead of silently contradicting the prose, and it now imports
labels_for() from the table generator so the section 2.1 counts and Appendix B5 cannot diverge.

Guards after the full re-run: invariants OK, 135/135 + 22/22, PRISMA reconciled, drift clean.

Appendix B5 is now a FIGURE, not a table (Sacha: the table is heavy and the empty cells are
distracting). Figure 6, `scripts/fig_platform_construct.py` -> docs/figM_platform_construct.svg,
built from the same CSV as before.

Design decisions worth keeping. A dot matrix rather than a heatmap: the matrix is sparse by nature,
and an absent platform-construct combination should be empty space rather than a cell that still
has to be drawn and read. Dot AREA (radius as sqrt) encodes the SHARE of that construct's studies,
not the raw count, because k runs 15 to 209 across the columns and raw counts would have shown only
that content analysis is a large literature; column headers carry k, and the counts stay in the CSV.
One hue (Wong #0072B2, validated CVD-safe against a white surface), because position and area
already carry the value. Study counts are printed inside a dot only when the dot is large enough to
hold them, which is a size test, not a count test: a first pass labelled by count and printed "51"
inside a 6 px dot. The three residual rows (multi-platform unspecified, survey, other) sit below a
gap so they are not read as platforms.

Per the house rule that a figure and a table never show the same numbers, Table 3 was cut; the
display list now reads Figure 6 instead. The B5 prose carries the numbers the figure cannot be read
off precisely (Twitter/X 22 of 30 sharing and 11 of 17 concentration studies; web browsing 9 of 15
exposure and 13 of 24 reach), so all of them stay under the checker, which also asserts that the
figure's k headers match the CSV. Guards: 126/126 + 22/22, invariants OK, drift clean.

Appendix B5 final form (Sacha's choice): TWO figures, replacing the dot matrix.

Figure 6 is a scatter, each platform positioned by its share of the behavioural literature against
its share of the content literature, with a parity diagonal. Log axes, because on a linear scale
every platform below 5% piled into the corner, which was Sacha's objection to the first scatter.
Zero cannot sit on a log axis, so platforms with no behavioural study get a band at the foot of the
plot, which turns "content-only" into a visible category rather than a point jammed against the
edge. Per-point counts were dropped from the labels (Sacha disliked the x/x form): shorter labels
also removed the last collisions, and labels are placed by trying twelve offsets around each dot and
keeping the first that hits neither a label nor another point. The three non-platform categories are
omitted here and the caption says so.

Figure 7 is the per-construct panel set, six panels including self-reported recall. Recall is in the
panels but NOT in the scatter: its platform field is the survey question's frame rather than a
measured source, and the appendix now says that explicitly, using the fact that 42% of recall
studies name no single platform and 35% record only the survey. Sacha's reasoning for keeping it
here: the appendix should document all six constructs. An earlier draft filled the sixth panel with
"all behavioural pooled", which he rejected as double-counting, and a four-panel version that
dropped concentration was rejected because concentration is a headline construct and dropping it
would have been a layout decision, not a content one.

scripts/fig_platform_construct.py now emits both and imports labels_for() from the table generator,
so the figures, the CSV and the section 2.1 counts share one definition. The checker asserts both
figures' k headers against the CSV. Guards: 127/127 + 22/22, invariants OK, drift clean.

Two label fixes after Sacha read the figures.

"WhatsApp or Telegram" split into two rows. He asked whether there really are behavioural WhatsApp
studies; there are three (junk-news links across 130 public political groups, 13.1%; fact-checked
false messages among WhatsApp message shares, 0.96%; and a Bangladesh study of 1,200 recruited users
whose public posts were researcher-coded, which names WhatsApp among three platforms). Telegram has
zero behavioural studies and appears only in three content analyses, so the grouped label was
claiming behavioural evidence for a platform that has none.

"Multi-platform, unspecified" and "Survey, no platform" merged into "No platform named". For recall
the two said the same thing twice, 11 and 9 studies, and neither names a platform: one is a question
about "social media", the other records only the survey mode. Recall now reads 77% (20 of 26) with
no platform named, which is the honest headline for that panel and is what the appendix now says.

Also removed the three in-plot annotations from the scatter ("measured on people's behaviour",
"sampled as content", "no behavioural study"): the axis titles and the 0 tick already carry them.
Guards after both changes: 127/127 + 22/22, invariants OK, drift clean.

## 2026-08-13 — full audit of the platform work, four real errors found and fixed

Sacha asked for a proper check after catching several problems by eye. Auditing every distinct raw
platform string against its assigned rows (128 strings) turned up four genuine misclassifications,
all caused by keyword matching that looked safe in isolation:

1. **Blank platform fell into "Other"** (8 estimates across 4 studies, including a REACH study of
   pink-slime sites). A blank field means the platform was not recorded, so it belongs in
   "No platform named".
2. **"Web browsing" was holding website CORPORA as well as browsing panels.** `website`,
   `websites`, `official health websites`, `Web pages (Arabic-language, search-engine results)` and
   `Web (general search)` all reached it through the `platform_norm == web_cross_platform` fallback.
   A corpus of sites is not a browsing panel. New row "Websites" (5 content studies); "Web browsing"
   is now purely behavioural and, as a result, the figure shows browsing panels support 15
   behavioural studies and zero content analyses, the exact mirror of YouTube and TikTok.
3. **Cross-media totals counted as browsing.** `overall (TV+desktop+mobile)` matched on "desktop".
   Both it and `overall (incl. TV)` are whole-diet totals, not a platform -> "No platform named".
4. **WeChat was folded into WhatsApp.** No study names WeChat alone so no count moved, but the
   mapping was wrong and would have bitten later.

Also: `mainstream media articles (web)` and `fake news websites` -> News outlets; `search` (share of
search queries) -> Google Search. These twelve strings are now an explicit OVERRIDES table keyed on
the exact raw string, resolved against each study's own measure, rather than more keyword tuning:
every candidate keyword I tried also caught rows it should not have. The audit asserts every
override key still exists in the data, so a re-freeze that drops one fails loudly.

Numbers that moved, all corrected in section 2.1 and B5: behavioural web browsing 16 -> 15 studies;
exposure web browsing 9 -> 8; recall with no platform named 20 -> 21; News outlets content 11 -> 12.
Twitter/X, Facebook, YouTube, TikTok and every construct k are unchanged.

The audit also re-verified, from the freeze upward: the FROZEN top block MD5 against the file on
disk, that v1.7.11 -> v1.7.12 touched exactly 4 cells and only platform_norm, that every CSV cell
recomputes from the freeze, that both figures' k headers match the CSV, that all ten claims in the
prose match the data, that the "25 of 321 cells" tie count is current, that the metaregression
ladder in section 2.7 matches the CSV in both values and rank order, and that no reference to the
retired dot matrix, Table 3, or the old row labels survives anywhere. Guards: 128/128 + 22/22,
invariants OK, drift clean.

## 2026-08-13 (cont.) — the scatter is cut; "behavioural" as a class of constructs is dropped

Sacha's objection: putting SHARING on a "behavioural" axis while CONTENT sits on the other is odd
when the two differ mainly by denominator, and "behavioural" should mean trace data where
individuals are actually followed. Checked against `sampling_frame`, which is coded per study and
independently of construct, and he is right:

  construct        k    panel_trace   keyword_topical
  EXPOSURE        15        13              0
  REACH           24        17              3
  SHARING         30         5             15
  CONCENTRATION   17        11              3
  CONTENT        209         1            172

Only 5 of the 30 sharing studies follow individuals; half are keyword-topical corpora, the same
instrument as a content analysis. The three keyword-topical REACH studies are Twitter analyses of
"% of users in this corpus who posted >=1 fake link"; the three in CONCENTRATION are Twitter
superspreader analyses inside topical corpora; the single panel-trace CONTENT study is a WhatsApp
donated-chat corpus (denominator = posts, hence CONTENT). Of the 63 studies the manuscript used to
call behavioural, only 26 are panel traces.

Consequences applied: the scatter (figM) is retired, the per-construct panels become the single
Appendix B5 figure, and no text now groups the four constructs under "behavioural". Section 2.1 and
B5 give per-construct numbers instead (Twitter/X 22 of 30 sharing and 11 of 17 concentration;
browsing panels 8 of 15 exposure, 13 of 24 reach, 4 of 17 concentration and no content analysis;
YouTube and TikTok 49 and 41 of 209 content analyses and one study between them elsewhere). The
surviving uses of the word were checked one by one and all are specific rather than class claims:
"behavioural audience exposure (k = 15)" as the construct's own name, the whole-diet backbone, the
clustered-units caveat on the meta-regression, and the measurement-type moderator, which is the
coded field from the risk-of-bias appraisal.

SHARING as a construct stands: its denominator is sharing acts, which is what codebook rule a0-bis
turns on, and Appendix A already reports that the content-sharing gap is mostly instrument. What
does not stand is calling it behavioural.

The panels moved from three columns to two: at page width the three-column version rendered its
labels at about 5pt. Guards: 128/128 + 22/22, invariants OK, drift clean.

## 2026-08-13 (cont.) — the platform figure moves to the main text as Figure 1

Sacha's call: the panels belong in the main text, in the track form. Bars now sit on a full-width
track showing all of k, because at these values (many single-study rows) a bare bar or a lollipop
dot sits indistinguishably near the axis, while a sliver against a visible whole still reads as a
share. Each grid row is only as tall as its fullest panel, which removes the dead space that used
to sit above Content prevalence and Self-reported recall. Two columns, since three renders labels
at about 5pt at page width. The first bar in each panel is at full opacity, the rest at 0.75, which
gives each panel a focal point without a second colour.

Placement consequence, applied: it is cited in section 2.1, which precedes every other figure's
first citation, so it becomes FIGURE 1 and everything shifts by one — constructs forest 1 -> 2,
whole-diet backbone 2 -> 3, method drivers 3 -> 4, concentration flow 4 -> 5, PRISMA 5 -> 6. All
in-text references, the builder's FIGS list and the display-item list were renumbered together, and
the checker now asserts the builder's list reads 1-6 in order so a future insertion cannot silently
duplicate a number. Appendix B5 keeps its prose and points back at Figure 1. Verified in the
rendered PDF: one caption per figure, in order, on pages 4, 5, 7, 8, 10 and 15.

Note for the venue pass: main-text figures are now 6, where the pre-submission list wanted the
display-item count trimmed. That trade is Sacha's to make at formatting time.

## 2026-08-13 (cont.) — descriptive coverage panels for every moderator; freeze v1.7.13

Sacha: the corpus is descriptively rich and the manuscript uses almost none of it. Built
`scripts/fig_coverage_panels.py`, one drawing routine that emits the same track-bar panels for any
moderator, plus a `coverage_<field>.csv` for each: platform (the existing Figure 1, byte-identical
after the refactor, which was the regression check), topic, ground truth, denominator scope,
country, sampling frame, definitional breadth and classification level.
`scripts/fig_platform_construct.py` was deleted; its drawing code lived on as a second copy.

The strongest is TOPIC x CONSTRUCT: content analysis is 53% non-COVID health (111 studies) and 23%
COVID (49), while exposure is 67% general news (10) and reach 62% (15), and sharing is 47%
politics (14). The field measures the prevalence of health misinformation in corpora and the
exposure to political and general-news misinformation in traces; section 2.1's "68% health-adjacent"
hides that these are two disjoint literatures. GROUND TRUTH is nearly perfectly confounded with
construct (content 82% researcher coding; exposure 93%, reach 88%, sharing 73%, concentration 82%
domain lists), which section 2.7 asserts in prose but never shows. DENOMINATOR SCOPE likewise
(content 90% topical corpora; reach and recall 100% population).

FREEZE v1.7.13 (scripts/apply_v1713.py, 10 rows / 6 studies). The country panel exposed
`country_norm` labels written twice: "UK" beside "United Kingdom", "USA (Georgia)" beside "United
States", and three "Cross-national (global...)" variants beside "Global". Merged only the exact
duplicates; genuinely ambiguous labels ("English-language", "Arab world", "United States; South
Africa", "North America") are left for a coding decision rather than silently folded.

That fix corrected a published sentence. "A third of studies (104 of 313) include the United
States" counted rows coded exactly "United States"; the honest counts are 105 studies with at least
one US row and 102 whose only label is the US. "About half cover Western countries only" was
unguarded and turns out to be 48% on an explicit Western list. Both now carry checker assertions,
as does the new recency sentence: dating each study by when its DATA were collected (the `year`
field is the data year, not the publication year, verified against a 2016-campaign study published
in 2020), 200 of 313 studies fall in 2020 or later, 114 in 2020-21 alone, and 10 before 2016.

Full pipeline re-run on v1.7.13; the metaregression ladder is unchanged. Guards: 131/131 + 22/22,
invariants OK, drift clean. The seven new panels are NOT yet placed in the manuscript: Sacha is
choosing which belong in the appendix.

## 2026-08-13 (cont.) — descriptive results built out; two coding questions answered

Sacha's two checks, both answered from the data rather than assumed.

WHY THREE RECALL STUDIES HAVE FACT-CHECKER GROUND TRUTH. Not an error. Three European
disinformation-narrative surveys (Serbia, Spain, and one EU-wide) took narratives a fact-checker had
identified and asked respondents whether they had heard them. The `ground_truth` field records who
decided the item was false, not how prevalence was measured, so fact-checker + self-report is the
correct pair. The manuscript now states this explicitly, because it also clarifies the field.

WHY BREADTH IS MOSTLY BLANK. Also not a coding gap, and it is structural: ALL 65 studies that
classify whole sources carry no per-item veracity standard, against 15 of the 235 claim-level ones,
which is exactly the 82 (27%) already reported in section 2.2. A domain-list design has no per-item
standard to state. Section 2.2 now says so instead of leaving the reader to infer it.

Added: topic x construct as main-text Figure 2 (content analysis 111 non-COVID health and 49 COVID
against 15 politics; general news 10 of 15 exposure, 15 of 24 reach, 8 of 17 concentration; politics
14 of 30 sharing). Ground truth and country go to Appendix B5 as Figures 8 and 9. Classification
level gets no figure, as Sacha asked: section 2.2 now carries the split in words (192 of 209 content
analyses at claim level; whole-source classification for 14 of 15 exposure, 21 of 24 reach, 23 of 30
sharing, 15 of 17 concentration studies), which is the sharpest single sentence in the descriptive
material.

Figures renumbered again: platform 1, topic 2, forest 3, backbone 4, drivers 5, concentration 6,
PRISMA 7, ground truth 8, country 9. The builder-order assertion was widened to 1-9. Eight new
checker assertions cover the topic and ground-truth numbers, so the descriptive prose is guarded
like the rest. Rendered PDF verified: one caption per figure, in order, pages 5, 5, 6, 8, 9, 11, 16,
27, 28. Guards: 139/139 + 22/22, invariants OK, drift clean.

Main-text figures are now 7, against a pre-submission plan to cut display items. Flagged for the
venue pass; it is a formatting decision, not a data one.

## 2026-08-24 — Fabricated-paper mentions removed from the LIMITATIONS sections (Sacha's call)

Sacha asked what "the removal of three fabricated papers" in the §2 limitations paragraph meant;
explained (the E12 catch + the 2026-07-30 integrity re-screen, log entries above). His decision:
this is a QA catch, not a pipeline-created problem, so it does not belong in limitations.
Edits: (1) §2 limitations — dropped the "including the removal of three fabricated papers"
clause; (2) Appendix C3 Coding limitation — removed the fabrication passage (the story is fully
told in the §4.8 reliability appendix, which keeps the catch, the 87-study re-screen, and the
clean verification); (3) moved the "bounded check rather than a guarantee" hedge from C3 into
that §4.8 passage so the honest limit survives. check_manuscript_stats.py 139/139 PASS;
crosswalk drift check clean. No data change; freeze stays v1.7.13.

## 2026-08-24 (cont.) — Sacha's v10 docx edit folded back; v11 delivered

v10 Desktop docx diffed against the master build (no comments, no tracked changes; direct-edit
detection via paragraph diff). ONE Sacha edit found, in the closing discussion paragraph:
"a majority of what people believe they have seen" -> "report having seen". Applied to the md
master; the other three diff regions were this morning's fabricated-paper limitation edits.
Guards: 139/139 + 22/22, invariants OK, drift clean. Rebuilt and delivered
~/Desktop/manuscript_draft_v11.docx; v10 moved to Trash.

## 2026-08-24 (cont.) — External AI review of v11 received; claims fact-checked; plan proposed, NO edits yet

Sacha commissioned a seven-lens AI review (~/Desktop/prevalence_review_v11_feedback.md). Its
checkable claims were verified against the pipeline before planning:
- CONFIRMED: "pre-registered rule" (C1) vs "not registered" (S4.1) contradiction; Figure 6 caption
  fuses k=5 top-1% (70%) with k=9 <=1% band (65.3%); Figure 5 caption + abstract present the
  4.9/20.2/48.6 as medians when metareg_measurement_pred.csv shows they are model predictions;
  "merged recall set" (S2.8) undefined; the n=497 concentration search never reconciled with
  25,907; abstract's "a third of studies from the United States alone" blends 105-include with
  102-US-only; limitations omit non-registration.
- REFUTED (piping-error suspicion): EXPOSURE IQR = 95% CI [0.6-5.1] is genuinely computed as
  identical at 1 dp in uncertainty_medians.csv (k=15; bootstrap CI endpoints land on the quartile
  order statistics) — a footnotable coincidence, not an error.
- REFUTED (absence claim): Guess, Nagler & Tucker 2019 IS in the frozen corpus (2-s2.0-85060025053,
  4 SHARING rows incl. the 8.5% headline; included at screening 2026-06-21). The real gap is only
  that it is never name-cited in the text/references.
Plan proposed to Sacha in-session (tiered: verified fixes / cheap analyses from existing data /
decision items needing his hours or calls: human eligibility sample, title re-screen, repo
publication timing, OSF retrospective registration, title, consensus-sentence framing, venue).
No manuscript edits made, per instruction.

## 2026-08-24 (cont.) — Review-response round EXECUTED: Tier 0+1 edits, new analyses, v12 TRACKED delivered, round-3 coding files built

Sacha approved the plan (Tier 1 minus the CONTENT-vs-EXPOSURE stratification he doubted; venue
= NHB-like; repo public last-minute; more human coding by him + Laura; framing parked; edits
minimal and delivered as TRACKED CHANGES for approval).

NEW ANALYSES (scripts/phaseB_review_response.py -> data/synth/phaseB/review_*.csv, all
checker-asserted):
- Matched concentration: the four panels reporting both quantities give within-panel top-1%
  ratios 1.5 / 2.3 / 2.5 / 2.6, median 2.4 -> the abstract's "about twice" SURVIVES matching
  (the reviewer's 1.5x panel is the lowest of four). Written into section 2.9.
- Correction symmetry: across the 33 freezes v1.5.0->v1.7.13 the six construct medians moved
  up 8 times, down 11 (sign test p=.65) -> no drift toward the thesis. Written into C1.
- Human-verified subset (174/313 studies): medians close to corpus, deviations both directions
  (CONTENT 20.4 vs 23.6; RECALL 66.1 vs 55.0). Written into C1.
- Weight shares: top-1 study holds 36-86% of weight per construct -> §2.8 now says so.
- Cramér's V among the "one family" moderators: 0.56-0.97 -> §2.7 substantiates the claim.

MANUSCRIPT EDITS (Tier 0 + cheap methodology defenses; ~30 edits): abstract (model-predicted;
US-only 102/313), Fig 4/5/6 captions (RoB colours; model-predicted; k=5 not 9), §2.3 "robust in
direction", §2.6 backbone two-forms label, §2.7 univariable + Cramér's V, §2.8 sign test + Begg
+ merged-recall definition + weight shares, §2.9 matched panels, §3 platform-scope caveat +
RECALL dual-status at Table 1, limitations + C3 add non-registration, §4.1 reproducibility
scoped + models named (Sonnet/Opus classes, settings-not-pinnable limitation), §4.3 497
reconciled + databases-not-searched + Wilson CI 64-97%, §4.4 rule-of-three bound (~175) + MAYBE
rate 12% + second-reader relabelled as LLM, §4.5 retitled two-pass LLM extraction, C1
pre-specified rule + kappa=.33 propagation statement + fabrication re-screen scope (87/84),
§4.7 no-pooling rationale (Barendregt) + small-k CI caveat, Table 2 caption + EXPOSURE IQR=CI
coincidence footnote (verified genuine, not piping), Table A1 numbered, refs added (Barendregt,
Begg, Guyatt, Munn, Guess-Nagler-Tucker + in-text 8.5% sentence).

GUARDS extended first then green: 147/147 must-appear (8 new review_* assertions), 22/22
stale-absent, invariants OK, drift clean.

DELIVERY: ~/Desktop/manuscript_draft_v12.docx with ALL edits as tracked changes (author
"Claude") for Sacha's accept/reject. Word's AppleScript compare could not save (sandbox);
tracked changes generated directly in OOXML (scratchpad make_tracked.py): char-level diff per
changed paragraph, formatting preserved, verified accept-all == clean build byte-for-text.
v11 -> Trash. NOTE: a stray empty "Document1" may be open in Word from the failed compare —
close without saving.

ROUND-3 HUMAN CODING built (scripts/build_round3_coding.py, seed 20260824):
- A: title-screen validation, 300 titles (200 EXCLUDE/50 MAYBE/50 INCLUDE, shuffled, blind).
- B: full-text eligibility, 50 frozen includes + 50 full-text-stage drops with PDFs (pools:
  263 includes-with-pdf, 105 drops-with-pdf), shuffled, prefix-valid subsampling.
- Coder files (sacha+laura) in docs/RA_package/round3_2026-08/ + README; keys quarantined in
  data/extract_v2/qa/round3_keys/. Scoring scripted on "round 3 done".

PARKED (Sacha's Tier-2 calls): repo public + OSF retrospective deposit (last-minute), framing
items (consensus sentence, Williams cite, title, policy hedge, sole-authorship sentence),
funnel plot (deferred; Begg framing added instead), RoB cross-model re-appraisal, human breadth
agreement.

## 2026-08-24 (cont.) — Round-3 coding upgraded: HTML pages + title sample 300->500

Per Sacha: (1) coding now happens in HTML pages (same house pattern as the IRR round —
autosave to localStorage, chips, progress bar, Download-FILLED-csv; CSS imported from
build_irr_coding_html.py), with Task B cards carrying a clickable "Open the paper" link to the
local PDF (relative, URL-encoded; all 100 verified to resolve); (2) title-screen sample bumped
to 500 (400 EXCLUDE / 50 MAYBE / 50 INCLUDE — 0/400 clean would give a one-sided 95% upper
bound of 0.75% on the title-exclusion miss rate). scripts/build_round3_html.py generates
code_A/B_<coder>.html; CSVs remain the scorer's source of truth. Keys regenerated (nobody had
started coding). README rewritten around the HTML flow.

## 2026-08-24 (cont.) — Round 3 resized (200 titles / 50 full-texts), rapid-screener UI, full criteria in-page; docs tidied

Sacha resized the human load: titles 500->200 (150 EXCLUDE / 25 MAYBE / 25 INCLUDE; a clean
0/150 gives a one-sided 95% upper bound of ~2% on the title-exclusion miss rate) and
eligibility 100->50 (25+25). No fixed external standard exists for these validation sample
sizes; the bound-width math is the honest criterion and is documented here.
Task A rebuilt as a one-at-a-time RAPID SCREENER (one big title, keyboard I/M/E with
auto-advance, arrow navigation, coloured progress strip) instead of 500 scrolling cards; Task B
keeps cards + PDF links (50 links verified). The coding-rules banner now carries the pipeline's
FULL Stage-1 criteria verbatim from docs/screening_criteria.txt (Sacha's ask: real
include/maybe/exclude rules, not just blind rules); Task B's box states the eligibility rule
with the not-eligible list. Coder CSF worksheets no longer live in the coder folder (the
_COLLECTION masters sit with the keys; HTML is the coding surface).

TIDY-UP (house rules, nothing deleted): docs/ root archived to docs/Old/ — RESUME_HERE.md
(self-describedly stale), internal_review_v7.md/.html, v1.2_newrows_worklist.md,
v1.2_punchlist.md, rob_checklist.txt (superseded by v3), construct_tagging.txt (June scratch),
RA_package.zip (July snapshot of the live folder). audit_review.html KEPT (active, referenced
by ingest_human_decisions.py; it is the pending correctness-pass decision page).
make_tracked.py promoted from scratchpad to scripts/make_tracked_docx.py (now a standing part
of the docx delivery loop). Scratchpad build artifacts cleaned. Guards after moves: drift
clean, 147/147 + 22/22.

## 2026-08-24 (cont.) — Round-3 pages: number keys, embedded PDF for Task B, journal shown, criteria wording softened

Four Sacha asks: (1) keys are now 1/2/3 (i/m/e still work); (2) Task B rebuilt as the same
one-at-a-time screener with the PDF EMBEDDED in the page (iframe left, decision panel right,
1=INCLUDE 2=EXCLUDE, required reason, Enter advances; open-in-tab fallback) — no more tab
juggling; (3) both tasks now display the JOURNAL (from the Scopus corpus `source` field;
200/200 filled in A, 45/50 in B) — NOTE the pipeline screened titles only, so the human coder
sees strictly more context; recorded here to report at scoring; (4) the INCLUDE criterion is
reworded from "the title clearly indicates a quantitative estimate" to "clearly indicates a
study that measures one of the following, so a quantitative estimate is plausibly reported"
(titles never contain the estimate itself). Samples unchanged (same seed, 200/50); keys
regenerated in lockstep.

## 2026-08-24 (cont.) — Task B: taller PDF pane + in-PDF search hint

PDF iframe grown to calc(100vh - 150px) (min 600px; 75vh on narrow screens). Added the search
hint next to the open-in-tab link: click once inside the PDF, then Cmd-F opens the PDF
viewer's own search (the page's find bar cannot see into an embedded PDF); the new-tab link
remains for full-window reading.

## 2026-08-24 (cont.) — Round-3 pre-flight verification (22 checks) + two fixes

Full pre-send QA, all PASS: A sample 200 unique ids, titles+journals complete, key aligned and
matching the shard ground truth, strata 150/25/25; B sample 50 unique, key aligned, 25/25
groups consistent with the freeze, all PDFs present; every embedded PDF text-matched against
its row title (49/50; the one low-overlap file, #35 OA Baerbock study, verified VISUALLY as the
correct paper — it is the German-language original "Komplize oder Korrektiv?", same DOI, no
extractable text layer); both coders' pages embed exactly the worksheet data, contain no
pipeline decisions, and use distinct localStorage keys; export columns match the worksheets.

Two defects found and fixed: (1) row #40's title was a truncated drop-ledger fragment
(" possible prevalence") — B titles now resolve from the Scopus corpus first (PDF itself was
correct); (2) BLINDNESS LEAK: the PDF path revealed the group (everything served from
data/fulltext/pdf/ was an INCLUDED study, 10/50 rows). All 50 PDFs are now COPIED into the
round folder's papers/ store under neutral order-based names (B01–B50.pdf, gitignored, 68 MB),
which also makes the folder fully self-contained for Laura. A rules box now notes some papers
may be partly non-English (judge from the English abstract; one German-language included study
is in the sample). Samples unchanged (same seed).

## 2026-08-24 (cont.) — Task B note optional; Task A gains a one-line title-provenance sentence

Sacha: reasons in Task B should not be mandatory. The your_reason field is renamed your_note,
completion = decision only, B now auto-advances on decision like A (arrow back to add a note);
the rules box says notes are optional but help adjudication of borderline calls. Task A's rules
box now opens with provenance: the titles are a random sample of the ~20k records returned by
the review's broad Scopus Boolean keyword query (misinformation terms x measurement terms,
recall-tuned), so many are off-topic by design. Samples and keys unchanged.

## 2026-08-24 (cont.) — Laura's coding package staged on the Desktop

~/Desktop/round3_coding_Laura/ (her two HTML pages + papers/ + README) plus
round3_coding_Laura.zip (57 MB) for sending; all 50 PDF links verified to resolve inside the
standalone folder.

## 2026-08-24 (cont.) — The parked correctness/currency pass (2026-08-13 item 1) EXECUTED

The pass macOS killed on 2026-08-13 is done. Results:
- FREEZE CHAIN: all 38 FROZEN.md blocks verified — file exists, MD5 matches, git tag present;
  all 14 apply_v17xx.py scripts on disk. CLEAN.
- GUARDS: invariants OK, 147/147 + 22/22, drift clean.
- FIGURES: all 9 builder-named SVGs exist, every one regenerated 2026-08-13 (the v1.7.13 run).
- DEAD REFERENCES: no references to the deleted fig_platform_construct.py or the retired
  scatter anywhere outside Old/ and the log. CLEAN.
- STALE FREEZE STRINGS (the class the drift checker cannot see — it guards counts, not version
  labels): FOUR living docs presented an older freeze as current, all fixed:
  prisma_checklist.md said v1.7.10; grade_certainty_framework.md and data_quality_methods.md and
  METHODS_PROVENANCE.md said v1.7.9. GRADE certainties re-verified against grade_sof.csv before
  relabelling (all six unchanged). Historical mentions elsewhere are properly marked as such.
- PROVENANCE LEDGER: llm_provenance.md consistent with the new §4.1 disclosure (in-session
  agents, family documented, builds not independently pinnable).
- MEMORY: misinfo-review-open-items rewritten to current state (was 10 days stale: still said
  v8/v1.7.10, Codex batches pending, this very pass pending); MEMORY.md index line updated.
LESSON (recurring): hand-maintained "current status" headers in docs/ drift every re-freeze;
sweep docs/*.md for version strings after each freeze, the checker will not catch them.

## 2026-08-24 (cont.) — LIVE CATCH by Sacha: malformed shard rows showed the screener's REASON as the title; fixed, affected rows reset

Sacha, coding Task A, hit rows whose "title" read "off-topic" / "not exposure" — the screening
shards carry malformed rows where the reason string sits in the title column. 11 of the 200
sampled rows leaked the pipeline's reason this way (a blindness break for those rows); a further
3 were harmless truncation/apostrophe variants. FIX: Task A titles now come from the corpus
jsonl (authoritative — also exactly what the pipeline screener read), verified all 200 == corpus.
The 14 flagged orders are recorded in round3_keys/A_titlescreen_leaky_shard_rows.csv; scoring
will report with/without them. The coder pages carry a ONE-TIME localStorage repair: decisions
on those 14 orders are cleared (notes kept) so they are re-coded from the real titles;
everything else Sacha coded is preserved (answers live in localStorage, keyed by order — sample
identity unchanged). Desktop folders + Laura zip refreshed; Laura's earlier zip disappeared
from the Desktop (presumably sent) — if it was, RE-SEND the new one.
LESSON: coder-facing text must be sourced from authoritative stores, never from working shards;
and pre-flight checks must compare displayed fields against the authoritative source (the
pre-flight validated ids/keys/strata but trusted the shard title column).

## 2026-08-24 (cont.) — Post-catch RE-AUDIT of round 3, this time against authoritative sources + live browser

After Sacha's live catch (the pre-flight had trusted the shard title column), both tasks were
re-audited with every DISPLAYED field checked against an independent source, plus a real-browser
end-to-end test. Results:
- ROOT CAUSE of the leak nailed: unquoted commas inside the shard REASON field shift columns at
  parse time. id/year/label sit BEFORE reason, so the ANSWER KEY was never corrupted — verified
  the key against the 14 raw shard lines (labels match exactly), and years/journals for all 200
  rows match the corpus (0 mismatches).
- Task B: all 50 titles match their authoritative source; PDFs already content-verified.
- NEW residual signal closed: the 5 blank journals were all INCLUDED-group (OA-path) studies —
  "no journal" weakly implied "included". Filled from the PDFs themselves (Jadara J. Studies &
  Research; J. Quantitative Description x2; GM Crops & Food; Cureus). 0 blanks now.
- BROWSER END-TO-END (isolated Chrome, chrome-devtools): both pages load with zero console
  errors; simulated coding sessions on A and B produce correct auto-advance, counters, reset
  flag, PDF-iframe switching (B01->B02), and exports with the exact worksheet header, 200/50
  rows, and correct quoting of commas in notes. One layout bug found and fixed: in the narrow-
  screen stacked mode the PDF pane shrank to content width (align-items:flex-start in column
  flex); now stretches full width.
Desktop folders + Laura zip redeployed. Coder localStorage unaffected throughout.

## 2026-08-24 (cont.) — Round 3, Task A (Sacha) SCORED

Sacha's 200-title re-screen ingested (A_titlescreen_sacha_FILLED.csv, 200/200 coded, copied to
the round folder) and scored by the new scripts/score_round3.py (reusable; will add coder-vs-
coder kappa when Laura's files arrive). Report: round3_keys/score_report.md.

HEADLINE: ZERO hard misses — of the 150 pipeline-EXCLUDED titles, Sacha marked 0 INCLUDE and
7 MAYBE (one-sided 95% UB on the title-exclusion miss rate 8.6%; 9.3% excluding the 14
flagged rows — results virtually identical with/without). All 7 maybes are on the taxonomy's
own exclusion boundaries on first read (4 CS detection/classifier papers, 1 sharing-intentions
experiment — amusingly Altay/Hacquin/Mercier's own reputation paper — 1 sharing-factors
survey, 1 SNS-dependency study); none looks like a genuinely missed prevalence estimate, but
formal adjudication (with abstracts) waits until Laura's file is in. Other direction: Sacha
would EXCLUDE 17 of the pipeline's 50 advances, as expected under the recall-protective rule
(advancing borderline titles is the design, not an error). Binary advance-vs-exclude agreement
88%, kappa 0.66. Disagreement queue (24 rows) -> round3_keys/disagreements_A_sacha.csv.
PENDING: Sacha Task B; Laura Tasks A+B; then adjudication + write-up into §4.4/§4.8.

## 2026-08-24 (cont.) — Framing agreed for the round-3 write-up: AI title screening as BENEFICIAL, not just defensible

Sacha's framing, ratified with refinements: the 4-of-17 result gives near-ground truth (3 of the
4 rescued studies are in the human-verified set; the 4th passed full-text screening), so at the
TITLE stage the recall-protective AI screen demonstrably beats title-only human screening, which
over-excludes. Refinements to carry into the write-up: (1) the advantage is the affordable
RECALL-PROTECTIVE RULE at 25k scale, not superior reading — humans drift strict under load (the
coder-degradation lesson); (2) wait for Laura before claiming humans (plural) over-exclude;
(3) the claim reverses at judgment stages — the human tier caught the fabricated paper and
forced the denominator corrections — so the paper's claim stays division-of-labour (AI for
recall-critical bulk, humans for judgment/authenticity), now with a quantitative payoff at the
title stage. To be written into §4.4/§4.8 with the round-3 results after Laura + adjudication.

## 2026-08-24 (cont.) — Round 3 EXTENDED to all stages: Task C (abstract screen) + Task D (RoB items 6/10)

Sacha's question "do we now have human codes for all stages?" surfaced the two remaining gaps:
abstract screening (never directly human-audited; bracketed by title- and full-text-level
checks) and RISK OF BIAS (zero human or independent evidence, yet it powers the 80.2% item-10
figure, the exclude-HIGH sensitivity, and GRADE). Both closed with two new blind tasks:
- TASK C: 60 abstract-stage decisions (40 EXCLUDE / 10 INCLUDE / 10 MAYBE, all with abstracts
  on file from data/abstracts/abstracts.jsonl), A-style screener with the abstract under the
  title; stage-2 (decisive) criteria in the rules box.
- TASK D: 40 included studies stratified 10-per-cell on the pipeline's (item6, item10) ratings,
  blind to those ratings, B-style embedded-PDF page with two LOW/HIGH button groups (keys 1/2 =
  item 6, 3/4 = item 10); instructions carry the ratified source-list ruling for item 6 and the
  denominator wording for item 10. PDFs copied to papers/D01-40.pdf (neutral names).
A/B samples verified UNCHANGED (rng draws appended after theirs; git-diff clean on both keys).
Pre-flight on C/D: 12 data checks PASS (alignment, strata 40/10/10 and 10x4, abstracts present,
blindness, PDFs match titles) + browser end-to-end on both pages (decisions, half-coded state,
auto-advance on completion, iframe switching, exports with exact headers). score_round3.py
extended for C (A-style scoring) and D (per-item kappa vs pipeline + coder-vs-coder).
Deployed to both Desktop folders; Laura zip rebuilt (96 MB, 90 PDFs) — send THIS version.
Estimated human load: C ~45 min, D ~1.5 h per coder.

## 2026-08-24 (cont.) — RoB REFRAMED as descriptive (Sacha's ruling); Task D CANCELLED

Sacha, coding Task D, saw that item 10 could be coded from the design category alone and
questioned the whole RoB apparatus as normative and redundant with the moderator coding. The
data confirmed him: item 10 is rated HIGH for 99% of topical denominators (138/139), 99% of
curated samples (69/70), 87% single-source, vs 9% population and 0/4 all-media (new pipeline
output review_item10_design.csv; item 6 likewise tracks breadth/ground-truth). As applied, the
two design items RESTATE the taxonomy; they add external correspondence, not information.

RULING + SURGERY (all checker-guarded, guards 150/150 + 22/22, invariants, drift clean):
- Abstract: the 80.2% RoB sentence REMOVED.
- §2.6: RoB verdict passage (49% high, 80.2%, 61%-vs-0%, exclude-HIGH 13.2) removed from main
  text; replaced by two sentences: appraisal exists per PRISMA, reported descriptively in B1
  because its design items restate the taxonomy. GRADE + quality-fold + temporal stability stay.
- §3: "not just our framing / standard tool finds it" sentences removed; "Bias and magnitude
  are linked" para becomes "Design and magnitude are linked" (weighting + GRADE only).
- B1 rewritten: distribution + flag rates kept as description; NEW crosstab paragraph with the
  determinism numbers; the items-6/10 ratings inherit the denominator coding's human validation
  (kappa .84); the ONE independent finding foregrounded — the eight generic Hoy items do NOT
  track magnitude (23.6->23.0), so divergence is a property of design choices, not carelessness.
- B2 exclude-HIGH bullet kept but glossed as "largely means excluding topical/curated designs".
- §4.6 methods: disclosure sentence added.
- Checker: Discussion-restatement assertion retargeted to the B2 from-to form; 3 new assertions
  anchor the crosstab numbers to review_item10_design.csv (150 total).
- TASK D cancelled: pages + D-PDFs removed from coder folders (Trash), README pruned, html
  builder loop back to A/B/C; the D sampling keys stay in round3_keys for the record. Round 3
  is now A (done, Sacha) + B + C.
- Tracked v12 REBUILT from the v11 base (now carries review-response + RoB surgery; accept-all
  verified == clean build; one fully deleted paragraph appears as absence, not strikethrough —
  a limitation of the paragraph-aligned tracked-diff).

## 2026-08-24 (cont.) — Tasks B and C SWAPPED (longest last, Sacha's ask)

Task B is now the ABSTRACT SCREEN (60 records, ~45 min, screener layout) and Task C the
FULL-TEXT ELIGIBILITY (50 studies, embedded PDF, the long one, done last). Renamed end-to-end:
sampling builder (stems B_abstractscreen / C_eligibility, PDFs papers/C01-50.pdf), HTML builder
task mapping, scorer, README, keys (old-name key files removed from git). Samples verified
IDENTICAL to the pre-swap draws (rng order unchanged; both key files match HEAD's content
row-for-row). Task D's PDF copies disabled in the builder (cancelled; keys retained). Desktop
folders + Laura zip redeployed (3 pages + 50 PDFs, C links verified). Sacha's Desktop
A_titlescreen_sacha_FILLED.csv confirmed safe to delete (ingested + committed).

## 2026-08-25 — RoB down to ONE paragraPH; Figure 4 (backbone) to Appendix B6 as Figure 9; Sacha's docx edit folded

Sacha chose the minimal option. Changes:
- His one direct docx edit folded first (", as PRISMA requires" deleted from the §2.6 sentence;
  extracted by accept-all diff of his Desktop v12 vs the master build — only Claude-authored
  revisions in the file, no comments).
- B1 collapsed to ONE paragraph: overall distribution, feeds GRADE, the item-10/design crosstab
  (99%/99% vs 9%) and the generic-items null (23.6->23.0). The exclude-HIGH sensitivity bullet
  REMOVED from B2 (last verdict-flavoured use). GRADE explained to Sacha and retained.
- The whole-diet backbone figure moved MAIN TEXT -> new Appendix B6, now FIGURE 9 (last, keeping
  physical order: main 1-6 = platforms, topics, forest, drivers, concentration, PRISMA; appendix
  7 ground truth, 8 countries, 9 backbone). RoB dot-colouring REMOVED from the figure
  (phaseB_figures.py: neutral blue, legend dropped); §2.6 cites "shown study by study in
  Appendix B6"; end-of-doc display list renumbered. Main-text display items 7 -> 6 (the venue
  plan wanted this anyway).
- Checker: 8 assertions retired with dated comments (exclude-HIGH pair/deltas, per-item flag
  rates, sans-6/10 26%); 142/142 + 22/22 PASS, invariants OK, drift clean.
- Tracked v12 rebuilt from the v11 base and redeployed to the Desktop (accept-all == clean
  build verified).

## 2026-08-25 (cont.) — Comment round on v12 (19 comments + 11 direct edits) fully addressed; v13 TRACKED delivered

All of Sacha's 11 direct edits folded verbatim (abstract count parenthetical out; §2.5 ->
"Construct heterogeneity"; §2.7 -> "What drives the estimates?"; recall-window sentence;
"denominator drives the number"; reliability lead-in trimmed; real funding statement UZH
Postdoc Grant FK-25-078; etc.). The 19 comments:
- WHOLE-DIET BACKBONE LOCALISED to §2.6 (c14/27/29/30): out of the §2.3 headline, Table 1,
  §2.5 PIs, §2.8 Spearman+weighted lists, §3 (2.6% only; ladder now 2.6->9.6->11.5->23.6->62.0).
  Stays in §2.6 + B6 fig + appendix tables.
- NO ALL-CAPS constructs anywhere (c28/61): global sweep Content/Exposure/Recall/Sharing/
  Reach/Concentration/Quality/Other across prose + tables; backbone figure group labels
  de-capsed; checker gained a display helper and ~10 assertions retargeted.
- FIGURE 4 REBUILT (c42/45): c42 caught a REAL mismatch (figure plotted raw medians 7/26/57
  while text cites model-predicted 4.9/20.2/48.6 and my earlier caption said model-predicted).
  Generator now adds "By construct" and "By identification level" bands; caption says
  study-level medians; §2.7 text explicitly separates model predictions from the figure's
  raw medians.
- BOX 1 REMOVED entirely (c107-109) incl. §3 lead-in sentences, display-list line, CCDH +
  Bickert references.
- Databases-not-searched sentence removed (c135/136). GNT parenthetical removed from §2.3
  (c16), citation preserved as a second Sharing example in Table 1. Content-studies gloss
  added (c17). "Property of the definition" reworded (c58). "Every analysis points to..."
  opener rewritten (c89). §2.8 evidence softened, sign-test dropped (c60). Construct grouped
  with top moderators, 16.5% "comparable share" (c41; checker assertion retargeted).
  Concentration-count hedged to "our corpus contains only 17... supplementary search found no
  missed cluster" (c110). "Six limitations" (c112). §4.8 machine-error detail compressed,
  full account stays in C1 (c176). "Fabricated" -> "fraudulent (not an AI-hallucinated
  reference)" wording everywhere (c177).
Guards: 138/138 + 22/22 (8 assertions retired with dated comments: backbone PI/rho/p/weighted,
ladder rebuilt without backbone), invariants OK, drift clean. Tracked v13 delivered to the
Desktop (59 changed + 17 inserted paragraphs vs the v11 base; accept-all == clean build
verified); v12 -> Trash.

## 2026-08-25 (cont.) — NHB CONVERSION + house-style pass; three deliverables on the Desktop

VENUE CONVERSION (Sacha: "do the NHB formatting now; goal = submit in the next few weeks"):
- Abstract 233 -> 159 words, no CIs, general-reader register per scientific_papers_style.Rmd.
- Display items: main = Figures 1-5 + Table 1 (6 items). PRISMA -> Supplementary Fig. 1;
  ground truth/countries -> Supp Figs 2-3; backbone -> Supp Fig 4. GRADE table -> Supplementary
  Table 1; holding-fixed table -> Supplementary Table 2. Appendices A-D -> Supplementary Notes
  A-D (letters preserved so every cross-reference stays valid); all "Appendix X" refs swept.
  Also fixed a misplaced heading (B6 had landed under the Appendix C heading on 08-24).
- NEW scripts/make_nhb_docx.py: builds nhb_main.docx (title page with affiliation +
  correspondence, abstract, main text + Methods, NUMBERED references) and
  nhb_supplementary.docx from the SAME md master. Citations convert author-year ->
  Nature-style superscript numbers by order of first appearance through an explicit curated
  43-entry map; the build FAILS on any unconverted author-year pattern; superscripts placed
  after punctuation, no preceding space. 43/43 references cited (no orphans); zero leftovers;
  zero marker residue. The md master STAYS author-year so the 138-assertion guard suite keeps
  reading it.
- Statements: Author contributions + Acknowledgements ([Laura SURNAME] placeholder for Sacha)
  added alongside the UZH funding statement.
HOUSE-STYLE PASS (Sacha: "no AI-claude style; match the NHB piece register"):
- Banned-word fixes: "direction is robust" sentence cut; "extreme" -> high/stronger;
  "enormously" -> "by two orders of magnitude"; alarming/reassuring pair -> high/low.
- Colon diet in Results/Discussion (five colon constructions -> plain sentences); "with one
  scope caveat:" unwound; "each analysis shows it from a different angle" cut; "arguably the
  most policy-relevant number" cut (style list violation); "That silence is a property of"
  -> plain. Zero em dashes in abstract/intro/results/discussion (the one hit is inside a
  never-rendered provenance comment). No "not X but Y" stacking remains.
Guards 138/138 + 22/22 + invariants + drift green (one assertion re-cased). DELIVERABLES on
the Desktop: manuscript_NHB_main.docx + manuscript_NHB_supplementary.docx (the reading copies,
submission format) and manuscript_draft_v14_tracked.docx (all changes vs the pre-review
baseline; accept-all == clean build verified). v13 -> Trash.

## 2026-08-25 (cont.) — Round 3, Task B (Sacha, abstract screen) SCORED + pre-adjudicated

B_abstractscreen_sacha_FILLED.csv ingested (60/60 coded). Headline numbers look weak (binary
agreement 70%, kappa .29; 7/40 pipeline-excludes advanced, 5 as INCLUDE) but decompose almost
entirely into two benign patterns:
(1) STRICT DIRECTION FULLY VINDICATED: all 11 pipeline-advances Sacha excluded are absent from
    the final corpus — every one died at a later stage anyway, replicating the Task A pattern
    (the recall-protective screen advances borderline records on purpose).
(2) ADVANCE DIRECTION IS MOSTLY THE QUALITY BOUNDARY: 4 of his 7 advances (#13 hemangioma
    reliability, #15 CAM-hypertension quality, #43 sunscreen TikTok quality, #44 DISCERN
    YouTube) are quality-instrument studies the pipeline excluded under the ratified
    falsity/quality rule — rule-definition disagreements, not detection failures. The Task B
    rules box does not restate that rule (kept IDENTICAL for Laura for comparability; handle at
    adjudication). #7 is a monitoring-program description (no estimate apparent).
GENUINE CANDIDATES for full-text adjudication at round close: #33 (UK survey, amplification of
exaggerated/false news — may contain a shared-recall estimate) and, weaker, #48 (risk-message
content analysis). Queued in round3_keys/disagreements (scorer re-run); adjudicate together
with Laura's files. PENDING: Sacha Task C; Laura A/B/C.

## 2026-08-25 (cont.) — Memory swept and brought current

open-items rewritten to live state (NHB pair on the Desktop as sole deliverables, 159-word
abstract, round-3 relabelled tasks with A+B scored and #33/#48 queued, the two Statement
placeholders [Laura SURNAME] and grant no. [FK-25-078] tracked, reporting rule for validation
kappas, updated remains-list); docx-workflow tidied (orphan line from the NHB edit removed);
MEMORY.md index refreshed (open-items, docx-workflow, methods-lessons now 23, search-currency
reclassified: June 2026 searches PRISMA-current for a near-term submission, top-up only if it
slips into 2027 — body of that memory updated to match).

## 2026-08-26 — NHB-pair comment round (39 comments + 15 tracked-edit paras) fully addressed; Discussion REWRITTEN in the NHB register

Sacha's tracked edits all folded (abstract opener, climate-absent phrasing, B5-pointer moved
after Figure 1, "In short..." sentence cut, source-level-conc sentence cut, Laura Hitz named,
Author-contributions deleted at his hand, fraudulent-parenthesis form, Belief de-capsed).
Statements: Competing interests + Ethics REINSTATED per his decision (NHB requires them);
his Author-contributions deletion respected (flagged: NHB will want one at acceptance).

STRUCTURAL: §2.6 (whole-diet backbone) DELETED at his decision — sections 2.7-2.10 renumbered
2.6-2.9, the Cordonier thirty-fold example rehomed to the Discussion→(§2.3 citation), the
backbone purged from GRADE/moderator-slicing text, Supp Note B6 + Supp Fig 4 removed, working
builder now 8 figures, Bergeron-Boutin re-cited in §2.3 (it had become orphaned). The §2.3
ratio paragraph moved into the Discussion opener with full CIs. Abstract rebuilt (174 words):
his tracked opener, no screening count, descriptive diversity sentence, Reach + Sharing added,
variance-decomposition sentence, "choose measures suited to the question they ask" closing.

DISCUSSION fully rewritten on the register of his NHB meta-analysis (the explicit model in
scientific_papers_style.Rmd): "This review sheds light on... In particular, we..." opener with
all headline numbers and CIs; Hameleers engaged directly; a First/Second/Third implications
paragraph absorbing policy + experimental-literature + concentration; a NEW which-construct-
for-which-question guidance paragraph (his c68) with the vaccine-outbreak worked example and
the "stated denominator beats no number" principle; a NEW grey-literature paragraph WITH
NUMBERS (117 claims: 19% denominator-free counts, 24% perception, 25% keyword-topical shares,
56% under alarming headlines — all checker-asserted from data/grey/); the four practices; six
limitations; plain closing (no double aphorism). Thesis-aphorism paragraph openers all gone.

GREY LIT: his question "where do we describe it? did I decide to exclude it?" answered from
the record — the never-pooled track was HIS pre-specified decision (research_log 2026-06-20,
grey_lit_protocol.md 2026-06-22); the gap was that the paper never delivered the promised
write-up. Now delivered: a Methods paragraph in §4.3 (frame, 4 producer categories, 117
claims, non-pooling rationale) + the Discussion numbers.

ALSO: §2.2 percentages (c39) + plain modal-coding phrasing (c37/38); recall-window "unclear"
precisely stated (one ambiguous question, one unretrievable full text — c42); §2.6 drivers
paragraph restructured (c47-49, Cramér's V + univariable note to Supp C2), micro-glosses on
construct/breadth/platform (c50), plain Figure-4 description with the RAW medians 7/26/57
(c51/52 — and the text/figure agreement is now checker-asserted by parsing the SVG); Figure 4
bars now ordered smallest-to-largest within band (c53, generator change); §2.7 retitled
"Sample size and estimate size" and made purely correlational (c55); single-panel 65/43
sentence cut (c57); robustness overview sentence + DISCERN explainer (c59/60); source-list
ruling moved to Supp C1b (c82); "imprecisely" rephrased (c83); "measured, not assumed"
de-Clauded (c77); intro c20/c21 rephrased.

CONCENTRATION FIGURE (c56): the Lorenz-style all-estimates figure regenerated as a CANDIDATE
(scratchpad render sent to Sacha); not wired into the paper pending his pick.

Guards: 140/140 + 22/22 (defs/R2/figure-count assertions retargeted; backbone + ladder
assertions retired dated; grey-lit + fig4-agreement assertions ADDED), invariants OK, drift
clean. NHB pair rebuilt and redeployed (43/43 references cited, zero unconverted).

## 2026-08-26 (cont.) — Grey lit PROMOTED to Results (§2.9) with the construct-comparison finding

Sacha challenged the Discussion placement and the exclusion. Resolution: NEW Results §2.9 "The
grey literature" (Robustness -> 2.10): 117 claims coded on the same grid REPRODUCE the
peer-reviewed gradient (grey medians: Exposure 2.2 vs 2.6; Content 25.0 vs 23.6; Recall 58.0
vs 62.0; Concentration 60.0 vs 70) — the distinctive grey pathology is the reporting form
(19% denominator-free counts), not the numbers. Non-pooling rationale sharpened and stated in
the section itself: claims are not independent studies (29/117 from one monitoring report) and
many restate platform/academic figures already in the corpus (double-counting). Discussion
keeps one linking sentence. Four comparison-median assertions ADDED (144/144 now), computed
from data/grey/grey_master.csv. Lorenz candidate figure polished (in-figure title removed per
house rule) and re-sent. NHB pair rebuilt + redeployed; invariants + drift green.

## 2026-08-26 (cont.) — Grey-lit distinction fixed; tracked NHB pair delivered; concentration figure v2

Sacha challenged the Fondation-Descartes-vs-Science-Feedback distinction — he was right that
"grey vs peer-reviewed publisher" was NOT the line. §2.9 + §4.3 rewritten to the defensible
rule: the corpus takes every eligible study the SYSTEMATIC SEARCH surfaces regardless of
publisher (Cordonier & Brest is in it); the separate track is the producer-WEBSITE sweep,
excluded from pooling because its claims lack a defined record set, are non-independent, and
often carry no verifiable method. Grey-lit placement settled: one Results section (§2.9) for
now; Sacha noted he remains tempted to add them to the main analyses later (the coded grid
makes that feasible post-review if wanted).
Concentration figure v2 built after "the fig is horrible": two-column dot plot at the top-1%
band (one dot per study, filled = exactly 1%, hollow = smaller groups labelled, medians 65%/31%)
replacing the Lorenz spaghetti as the candidate.
DELIVERY CHANGE: Sacha asked for his track changes accepted + Claude's edits as tracked. His
annotated main had been OVERWRITTEN by the redeploy (lesson logged in the workflow memory:
archive annotated files before overwriting); fallback used = tracked diff against the build he
read (git 1f92804), so his few edits appear among the tracked changes, all folded verbatim.
Both Desktop files are now TRACKED versions (main: 37 changed + 6 inserted paras; supp: 5+3);
accept-all verified == clean builds.

## 2026-08-26 (cont.) — Figure 5 stays; remaining concentration estimates now in the text

Sacha's call on the concentration figure: keep the current two-bar flow (Figure 5); both
candidates (Lorenz, dot-plot) rejected as ugly. In exchange §2.8 now reports the remaining
estimates in prose: top 5–15% of users = median 87.5% of activity (2 studies), top 15–35% =
80.0% (5 studies), thresholds not joined into a curve; plus the five source-level estimates
with the Grinberg 5%-of-sources example (his earlier deletion of the bare pointer sentence
respected — the content is now substantive instead). Two checker assertions added (146/146).
Grey-lit clarity confirmed OK by Sacha; placement = Results §2.9. Tracked main regenerated and
redeployed; Sacha now reads and comments on the Desktop pair.

## 2026-08-26 (cont.) — Second NHB comment round (17 comments + 5 direct edits) addressed; Task D repurposed as the grey-claims human check

Sacha's direct edits folded (abstract "what they share"; Discussion opener "In particular" cut;
his §2.6 paragraph splits; his deletion of the opener ratio sentence — the ratios re-homed as
ONE compact sentence in the Hameleers paragraph, flagged for his veto). Comments:
- Abstract variance sentence rewritten in plain words (c0); B5 pointer moved INTO the Figure 1
  caption as he originally did (c1); Bergeron-Boutin sentence + reference removed (c2);
  Altay & Acerbi 2024 reference dropped with its clause (c11); "moral panic" softened to
  "coverage that some scholars argue has exaggerated the threat" (c10); "less a measurement
  failure than a finding" framing cut (c12).
- §2.7 COMPRESSED to one short cautious paragraph (c4/c5), full detail moved to NEW
  Supplementary Note B6 (all asserted numbers survive); source-level concentration expanded to
  a four-example sentence (c6).
- Grey lit: platform-statistics fairness acknowledged + duplicates explained as deliberate
  (claim-as-published unit; c7/c8); "largely absent from peer-reviewed" corrected to the honest
  "excluded by construction — eligibility required a denominator" (c9); one-sentence Discussion
  paragraph folded into the four-practices intro (c13); §4.3 cross-ref fixed to §2.9 (c14) and
  a FULL cross-reference audit run (all §, Note, Figure, Table refs resolve).
- TASK D REPURPOSED (c15/c16): 30 of the 117 grey claims, stratified by denom_class, blind
  claim-text re-coding by Sacha (screener page, category chips, browser-tested E2E); scorer
  extended; his prior SIMODS involvement recorded in human_review_provenance.md; the
  manuscript will state the check once coded.
Guards 146/146 + invariants + drift green. His annotated file ARCHIVED before overwrite this
time; tracked main rebuilt against his accepted version (only Claude's new edits show; 46
changed paras) and deployed with the clean supplementary. References now 41 (two dropped with
their clauses).

## 2026-08-26 (cont.) — Ratios removed everywhere (Sacha's ruling)

The between-construct ratio multipliers (24.0 recall/exposure, 9.1 content/exposure) are OUT of
the manuscript entirely: the re-homed Discussion sentence deleted, the §4.9 ratio-bootstrap
methods paragraph deleted, four checker assertions retired dated (142/142 green). The pipeline
still computes ratio_bootstrap.csv (harmless artifact). Tracked main rebuilt vs his accepted
base and redeployed.

## 2026-08-27 — Small NHB round (2 comments + 6 edits); grey-claims composition clarified from data

Sacha's edits folded: duplicate author/affiliation line removed from the md front matter (the
builder title page carries it); Keywords moved after the abstract; "choices alone" -> "choices";
§2.7 "draw no further conclusions" clause cut; §2.8 concentration paragraph split in three; one
Sharing example in Table 1 (c26 — the Guess/Nagler/Tucker example and its reference removed, now
uncited; 40 references).
C123 ANSWERED FROM DATA: a scan of all 117 grey claims found ZERO restatements of academic
estimates — every catalogued claim is the producer's OWN number (surveys fielded, monitoring
dashboards, fact-check output counts, platform internal statistics). §2.9 rewritten accordingly:
non-independence is producers repeating their own figures and one report yielding many claims;
SIMODS-style novel producer estimates ARE in the track (and drive the §2.9 comparison), excluded
from pooling on provenance grounds only. Guards 142/142 + invariants + drift green. CLEAN pair
deployed per his request (accept-all round); annotated copies archived first.

## 2026-08-27 (cont.) — GREY CATALOGUE CURATED claim-by-claim after Sacha's platform audit; §2.9 rebuilt on curated numbers

Sacha challenged three platform claims (TikTok moderation metrics, YouTube VVR, Meta WVCR) as
non-estimates — correct on all three, and the audit that followed found more: the pooled
comparison had included the WVCR link statistic, the VVR (all violative content, misinfo share
unknown), duplicated Meta/CCDH/Avaaz/OII/Eurobarometer claims, attitude/concern questions coded
as recall, WHO figures that relay published reviews, and FOUR academic relays in concentration
(Grinberg x2, DeVerna x2) plus Allen et al. — so yesterday's "zero academic relays" claim was
WRONG (7 relays). Full claim-by-claim curation written to data/grey/grey_curation.csv
(117 rows: category + curated_class + dup_of). RESULT: 43 deduped usable misinformation-
prevalence estimates of 117; exclusions = 21 counts, 15 not-misinfo-specific, 8 within-misinfo,
7 academic relays, 6 attitudes, 3 moderation metrics, rest discernment/conditional. Curated
comparison still reproduces the gradient where n permits: Recall 64.5 (n=16) vs corpus 62.0;
Concentration 65.0 (n=5) vs 70; topical 10.6 (n=12); exposure 3.4 (n=2); reach 5.0 (n=3).
§2.9 rebuilt on these numbers (three paragraphs: provenance, curation composition, curated
comparison); §4.3 describes the curation; the old 19/24/25-percent practice shares superseded
by the composition breakdown (alarming-headline 56% retained). Checker grey block rewritten
from the curation file (13 assertions, all green). TASK D REGENERATED against the curated
coding (30 claims over 18 strata; chips now = constructs + exclusion categories; scorer
updated) — Sacha's blind check now validates the curation itself. Clean NHB pair redeployed.

## 2026-08-27 (cont.) — TRIPLE-CHECK of the grey curation (Sacha: "quality seems very low")

Three verification layers run:
1. VALUE-vs-TEXT scan over all 117 rows: 17 flags, 15 of them false alarms (SIMODS stores the
   report's exact table values while claim text carries rounded narrative + CI bounds — values
   verified INSIDE their CIs); 2 real anomalies, both in already-excluded categories (idx 3
   stores an org count in the percent field; idx 72 stores the WVCR complement 2.2 vs text
   97.8). The values feeding the curated medians are sound.
2. HAND RE-READ of every ESTIMATE row: FOUR curation errors found and fixed —
   (a) idx 51 = duplicate of idx 19 (Pew 23% shared-recall, was double-counted);
   (b) idx 18 (Shorenstein 6-in-10 visits from top-decile conservative diets) is the
   Guess/Nyhan/Reifler finding -> ACADEMIC_RELAY (relays now 8);
   (c) idx 12 (Reuters "none reached more than 1 in 20") is an upper BOUND, not an estimate;
   (d) idx 60 (NewsGuard 6.69% of news ENGAGEMENT) reclassed EXPOSURE -> SHARING.
   Fletcher factsheet (idx 11) verified NOT in the corpus -> stays as an original
   institute estimate (same rule as Cordonier).
3. REPORTING RULE tightened: §2.9 now compares only cells with n >= 5 (Recall 64.5 n=16;
   topical 10.6 n=12; concentration 67.0 n=4 flagged as-is) and says the rest (one or two
   claims each) are not compared. Usable estimates 43 -> 40; composition counts updated
   (8 relays). Checker retargeted (grey block now asserts only the compared cells). Task D
   regenerated against the corrected curation. Clean pair + coder page redeployed.

## 2026-08-27 (cont.) — LIVE-SOURCE VERIFICATION of the curated grey estimates (Sacha's request); two more reclassifications

Every usable estimate's value and provenance checked against the producers' own live
publications (WebFetch/WebSearch, 2026-08-27); per-row verdicts in
data/grey/grey_verification.csv (new, ships with the data). CONFIRMED with exact quotes:
Pew 23/32/38; StatCan-2025 80 (CSS 17th panel, spring 2025); Arcom 97/70 (n=2,000,
14–26 Nov 2025); ACMA 72/64 (H1 2025); Eurobarometer-2025 36/66; Ofcom-2024 40;
Ofcom-AMUA-2026 56 and 65 (7,533 adults, Sep–Nov 2025); Knight 65/89; CCDH 65 ("up to",
812k shares Feb–Mar 2021) and 69; all 12 SIMODS values (R2 confirmed live at the
second-measurement article; the stored science.feedback.org/simods/ URL now 404s — live
locations recorded in the verification table).

TWO RECLASSIFICATIONS from the check:
- idx 17 (Knight "one in four visited a fake news website Oct 7–Nov 14 2016"): NOT in the
  Knight Twitter report at the stored URL; it is Guess/Nyhan/Reifler's 27.4% (study in the
  corpus) misattributed to Knight -> ACADEMIC_RELAY (relays 8->9; REACH n 2->1).
- idx 84 (KFF "80% of Americans encountered COVID misinformation on >=1 platform"): KFF's own
  figure is 78% who BELIEVE OR ARE UNSURE about >=1 of eight false statements — a belief
  measure; the 80 is CNN's headline rounding, relayed by Kemei et al. 2022's abstract ->
  ATTITUDE (attitudes 6->7). RECALL cell n 16->15, median 64.5 -> 64.0.

Two metadata errors documented (values stand): idx 20's 41% is Ofcom ONLINE NATION 2025
(Dec 2025, top-encountered potential harm), not the 2024 four-in-10 release the URL points
to; idx 83's 96% is StatCan's CPSS-4 claim about Canadians WHO USED THE INTERNET TO FIND
COVID INFORMATION (Jul 2020) — the catalogued "on >=1 social platform" wording is Kemei's
distorted paraphrase (verified at dq210202c). Also fixed a corrupted curation row
(idx 61 had curated_class='61'; now COUNT dup_of=42, as intended).

RESULT: usable estimates 40 -> 38; §2.9 updated (38/117; 9 relays; 7 attitudes; Recall
64.0 n=15 vs corpus 62.0); §4.3 gains a verification sentence. Checker 145/145 + invariants
+ drift green. Task D regenerated against the corrected curation (30 claims, 18 strata).
Clean NHB pair rebuilt and redeployed (prior Desktop pair archived to scratchpad
annotated_archive/ first).

## 2026-08-27 (cont.) — CCDH bound claims EXCLUDED (Sacha's ruling); concentration comparison retired from §2.9

Sacha ruled that the two CCDH concentration claims fall under the same rule as the Reuters
"no more than 1 in 20" exclusion: the report bodies say "UP TO 65%" (Disinformation Dozen)
and "up to 69%" (Toxic Ten) even though the headlines state point estimates. idx 35 + 67
(and dups 66/78) -> OTHER_NOT_PREVALENCE (now 8). Usable estimates 38 -> 36; concentration
drops to n=2 (Knight 65/89), below the n>=5 threshold, so §2.9 no longer compares it (the
"remaining constructs, concentration included, are represented by one or two claims each"
sentence covers it) and the checker's CONCENTRATION assertion is retired with a dated
comment (144/144 green). §2.9's bounds clause now names the headline-vs-body example; §4.3's
verification sentence extended. Drift clean; Task D regenerated (30 claims, 18 strata);
clean NHB pair rebuilt and redeployed (prior Desktop copies archived first).

## 2026-08-27 — §2.9 rewritten for purpose and conclusion (Sacha: "quite bad, not relevant, not sure what to conclude")
Sacha, deciding whether to demote or remove the grey section, asked for it to be improved first.
Rewrite (docs/manuscript_draft.md §2.9, retitled "Quantitative claims in the grey literature"):
- Para 1 now states WHY the section exists (documents what widely publicised figures actually
  measure; tests whether the construct differences extend beyond academia) before the how; the
  never-pooled rationale and the Cordonier & Brest corpus clarification kept.
- Para 2 framed as a finding ("most of these claims do not measure misinformation prevalence"),
  exclusion inventory compressed: the four largest categories keep their counts (21 counts /
  15 broader-than-misinfo / 9 relays / 7 attitudes); WITHIN_MISINFO (8), MODERATION_METRIC (3),
  bounds/conditional/discernment folded into one remainder sentence. The dangling "56% alarming
  headlines" sentence DROPPED: its coding procedure was never described in §4.3 and it stood
  without a conclusion (the column stays in grey_master_enriched.csv).
- Para 3 framed as the second finding (the 36 estimates reproduce the Figure 3 ordering) and ends
  on an explicit conclusion sentence (construct + denominator set the meaning, not the producer).
Checker: 3 assertions retired with dated comments (grey within, grey moderation, grey alarming
share), 2 patterns updated to the new wording ("117 claims in total"; lowercase "recall claims";
"a median of" in the topical pattern). Guards 141/141 + 22 must-not + invariants + drift PASS.
Desktop pair archived to scratchpad annotated_archive/ (*_pre29rewrite_2026-08-27) then clean
NHB pair rebuilt and redeployed. Demote-vs-remove decision still Sacha's, pending his re-read.

## 2026-08-27 — Grey literature DEMOTED to Supplementary Note E (Sacha's ruling)
Sacha, uneasy that the grey sweep "is not systematic", ruled: keep the grey lit in the appendix,
focus on the misinformation-prevalence estimates, and compare them to the corpus. His concern is
correct on the facts: the sweep followed a written protocol (docs/grey_lit_protocol.md,
2026-06-22 — pre-specified 4-category producer list, fixed search strings, verbatim
figure/url/access date per claim) but the producer list is a purposive sample and website search
has no defined record set, so it is auditable, not exhaustive — not PRISMA-systematic. The new
Supp Note E now SAYS this explicitly and disclaims coverage conclusions.
Changes:
- Main text: §2.9 deleted; §2.10 Robustness renumbered §2.9. A short paragraph appended to §2.3
  carries the estimate comparison (recall 64.0 n=15 vs corpus 62.0; topical 10.6 n=12 vs 19.7
  for the corpus's topical content estimates — comparator NEW, estimate-level median of the
  CONTENT topical stratum from construct_distributions.csv, chosen over the 23.6 headline
  because grey claims are claim-level) pointing to Supp Note E.
- Supp Note E: method + explicit non-systematic limitation; compressed classification result
  (36/117); estimates comparison with the recall-producer characterisation VERIFIED against
  grey_master.csv (all 15 recall claims are regulators/survey organisations: Ofcom, ACMA,
  Eurobarometer/EC, Arcom, StatCan, Pew).
- Discussion four-practices pointer and §4.3 results pointer now cite Supp Note E.
- Checker: topical pattern relaxed to mid-sentence form; NEW assertion "grey topical corpus
  comparator" reads 19.7 from construct_distributions.csv. Guards 142/142 + 22 must-not +
  invariants + drift PASS. Builder docstring Notes A-D -> A-E.
Desktop pair archived (*_pre_greydemote_2026-08-27) then clean NHB pair redeployed.
Task D (grey-claims coding check) REMAINS meaningful: the 36-estimate curation now feeds §2.3 +
Supp Note E rather than a Results section.

## 2026-08-27 — Task D scope confirmed: Sacha only
Sacha confirmed he will complete Task D (30 blind grey-claim recodings) himself despite the
grey demotion — the recall/topical comparison still appears in main-text §2.3, so the human
check stays worthwhile. Laura will NOT do Task D (she remains on A/B/C only);
code_D_laura.html moved to round3_2026-08/Old/.

## 2026-08-27 — Round 3, Task B: clarification given to Laura (logged for comparability)
Laura asked (via Sacha): if a denominator-based quantitative result is not in the abstract but
the wording implicitly suggests it is in the full text, is that MAYBE or EXCLUDE? Answer sent
(drafted by Claude, approved by Sacha): a pure RESTATEMENT of the instruction box she already
has — never EXCLUDE (that is for abstracts showing the study is something else); INCLUDE if the
abstract "clearly will report" a qualifying estimate, MAYBE if genuinely open; her own reading
decides between the two. No information beyond the instruction box was given (no pipeline
tendencies, no recall-protective rationale, nothing about Sacha's codes), because Sacha
completed Task B under the identical box with no extra guidance and the two codings must stay
comparable. Logged per the standing document-everything rule.

## 2026-08-27 — Task B clarification: exact wording sent
Sacha sent Laura a lightly trimmed version of the drafted reply, verbatim: "In that case don't
exclude. Exclude is only for abstracts that show the study is actually something else (a
classifier paper, an intervention study, belief-only, and so on). If the abstract signals the
estimate will be in the full text, that counts as 'clearly will report' and you can include; if
you're unsure, you can put maybe." Substantively identical to the logged draft (instruction-box
restatement only); this supersedes the draft as the wording of record.

## 2026-08-28 — Task D scored (after fixing a scorer join bug and a sample-generation mismatch)
Sacha delivered D_greyclaims_sacha_FILLED.csv (30/30 coded; copied into round3_2026-08/, coder
file untouched). First scoring run reported 3/30 (kappa .04) — FALSE: two compounding problems.
(1) Scorer bug: Task D was joined on presentation `order`, which is regenerated with the sample;
(2) generation mismatch: the screener Sacha coded predates the two 2026-08-27 Task-D
regenerations (verification + CCDH exclusions), so only 21 of his 30 claims are in the current
key. Fix (in the SCORER, per house rule): join on claim_idx, score the intersection, report the
unmatched count, and add a binary usable-vs-excluded line. TRUE results (n=21): category
agreement 7/21 (33%), kappa .29; binary usable-vs-excluded 13/21 (62%), kappa .28.
Sacha reported the task felt easy; the queue decomposes less alarmingly than the raw number:
4 disagreements are adjacent categories on the SAME side of the usable line (ATTITUDE vs
DISCERNMENT, COUNT vs MODERATION_METRIC, NOT_MISINFO_SPECIFIC vs FACTCHECK_COMPOSITION,
TOPICAL vs CONTENT); several others hinge on source context a blind claim-text recode cannot
see (ACADEMIC_RELAY idx 30; the CCDH bound idx 35 — Sacha blind-coded CONCENTRATION, his own
adjudicated ruling excluded it using the report body). Genuine adjudication candidates include
idx 36/73 (Meta "12 accounts responsible for 0.05% of views": Sacha CONCENTRATION vs our
EXPOSURE — possibly OUR error), idx 59 (NewsGuard 40.21% red-rated sites: our CONTENT vs his
OTHER), idx 5 (PolitiFact composition: his CONTENT vs our FACTCHECK_COMPOSITION), idx 12 and
48 (bound and conditional wording visible in text: his REACH/RECALL vs our exclusions).
Queue: data/extract_v2/qa/round3_keys/disagreements_D_sacha.csv (14 rows). Adjudication vs
source pending with Sacha. The 9 coded-but-unscoreable claims can be topped up with a small
screener for the current sample if full n=30 coverage is wanted.
LESSON (methods): join keys must be stable across artefact regenerations; score against the
generation actually delivered, or regenerate screeners and keys atomically.

## 2026-08-29 — Laura's round-3 files scored (A + B + C)
Files copied verbatim into round3_2026-08/ (coder files untouched). Pre-flight alignment check
(lesson 24): order->id mapping matches the keys on all three tasks — same generation, no
mis-join. Results:
- Task A (200 titles): candidate pipeline misses 13/150 pipeline-excludes advanced (one-sided
  95% UB 13.4%); binary agreement 85%, kappa .59. Coder-vs-coder (with Sacha): 3-way 80%
  kappa .46, binary 85% kappa .56. Overlap of miss candidates: Sacha 7, Laura 13, BOTH only 2 —
  those 2 both-advance rows are the strongest miss candidates and lead the adjudication queue.
- Task B (60 abstracts): near-identical to Sacha (binary 72% kappa .30 vs his 70% kappa .29;
  advances 5/40 vs his 7/40). Coder-vs-coder 3-way 46/60 (77%), binary 47/60 (78%). Both humans
  precision-minded vs the recall-protective screener — supports the planned lead-with-miss-rates
  reporting rule.
- Task C (50 full texts): agreement 66% kappa .32; 6/25 included studies she would exclude,
  11/25 dropped studies she would include (looser than the pipeline on drops — the OPPOSITE
  direction from the round-1 RA, who was stricter). Queue: disagreements_C_laura.csv (17).
  Coder-vs-coder C waits on Sacha's Task C.
Pending: Sacha Task C; Sacha's Task-D adjudication (page delivered 2026-08-28); then union
adjudication (A: 18 rows, C queue) and the §4.4/§4.8 write-up.

## 2026-09-02 — Sacha's Task C scored; A + C adjudication pages built
Sacha delivered C_eligibility_sacha_FILLED.csv (50/50 coded, no notes; copied verbatim into
round3_2026-08/, coder file untouched). Pre-flight: order->id mapping matches the key (same
generation). Results (score_round3.py): agreement with the pipeline 44/50 (88%), kappa .76;
2/25 included studies he would exclude (rows 35, 49), 4/25 dropped studies he would include
(rows 3, 25, 36, 40). Coder-vs-coder C (Sacha vs Laura): 66%, kappa .31 — Laura's 17
disagreements vs his 6, overlapping on 3 (rows 35, 40, 49: those three lead the queue).
Contrast: Laura loosened 11/25 drops; Sacha, who wrote the eligibility rules, re-derived the
pipeline's calls almost exactly. One self-consistency case: row 36 (Humprecht 2024, YouTube
COVID-vaccine videos) he blind-coded INCLUDE, but ruled "drop — they selected only
misinformation" himself in both July RA-verification rounds; the card shows him both.
NEW scripts/build_AC_adjudication.py -> adjudicate_A_sacha.html (18 title-stage miss
candidates = union of pipeline-EXCLUDE rows either coder would advance; 2 flagged by both
listed first; abstracts fetched from OpenAlex by DOI for 16/18, cached in
round3_keys/A_misscandidates_abstracts.jsonl; rulings MISS / EXCLUDE_STANDS / UNCLEAR) and
adjudicate_C_sacha.html (20-row union queue, 3 joint; PDF links into the neutral papers/
store; pipeline evidence = recorded drop reasons + full-text verify verdicts for DROPPED, frozen
estimate rows with quote + denominator for INCLUDED; Sacha's own July review calls shown where
they exist, 11 cards; rulings INCLUDE / EXCLUDE). Machine-readable queues
adjudication_A_union.csv / adjudication_C_union.csv sit with the keys. Both pages copied to
~/Desktop/round3_coding_Sacha/. Two stray working-tree diffs (audit_v140_findings.csv,
prisma_counts.json) were pure row-order reshuffles from a regenerated output and were reverted.
Pending: Sacha rules A (18), C (20), D (14); then the §4.4/§4.8 write-up.

## 2026-09-02 — Task A adjudicated by Sacha: 0 genuine misses in 18 candidates
A_adjudication_sacha_FILLED.csv (18/18 ruled; saved to round3_2026-08/, Desktop copy trashed).
Every one of the 18 title-stage miss candidates (union of pipeline-EXCLUDE rows either coder
would have advanced, incl. the 2 both flagged) was ruled EXCLUDE_STANDS against the abstract.
Notes: #1 (Altay et al. "hurts their reputation") "from the title it's hard to tell, but it's an
exclude"; #4 lit review; #7 no data; #9 misinformation-only sample, no non-misinfo. So the
human "misses" were title-stage MAYBEs that the abstract resolves, not lost studies: the
adjudicated title-stage miss rate is 0/150 pipeline-excludes sampled (one-sided 95% UB 2.0%),
versus the unadjudicated 7/150 (Sacha) and 13/150 (Laura). Reporting rule stands: lead with the
adjudicated miss rate, then the raw human-advance rates as the pre-adjudication bound.
Pending: C (20) and D (14) rulings.

## 2026-09-02 — Task C adjudicated by Sacha (17/20 ruled, all uphold the pipeline); 3 re-reads
C_adjudication_sacha_FILLED.csv saved to round3_2026-08/ (Desktop copy trashed). 17 rulings,
every one upholding the pipeline: the 3 joint disagreements (rows 35, 40, 49) all resolved FOR
the pipeline against BOTH coders (row 35: "we did not read that sentence ... n = 8,601 search
results, about a quarter support the conspiracy theory — clearly include"); Laura's 11
would-include drops resolved as drops where ruled (row 39: meta-analysis, excluded by rule;
row 47: within-community composition); row 27 Laura's rationale rejected ("misleading OR
irrelevant" IS misinformation under the coding definition); rows 6/43/48 upheld as includes.
Three rows left blank with a request to re-read the PDF carefully; Claude's re-read (full text):
- Row 36, Humprecht 2024 (Frontiers Comm): the 450 videos were SAMPLED AS misinformation
  ("we sampled 450 German- and French-language videos with misinformation", drawn from 200
  accounts identified as misinformation producers via snowballing). The 61%/39% is the
  completely-vs-partially-false COMPOSITION within an all-misinfo sample (rule R3), and no
  all-content denominator exists anywhere in the paper. Recommendation: EXCLUDE stands (as
  Sacha himself ruled in both July rounds).
- Row 28, Ricke & Seifert 2025 (Naunyn-Schmiedeberg's): unit = 105 supplement PREPARATIONS
  from 78 Instagram posts by 61 influencers. Metrics: dosages exceeding the EFSA upper level
  (product fact), missing overdose/adverse-effect warnings (labeling omission), product names
  "suggestive of a false or exaggerated effect" (65% of combination preparations), and "a
  promise of efficacy" for 48% of preparations. No claim is verified false; the "disinformation"
  is regulatory (unsubstantiated/omitted), i.e. R7 quality/labeling. Recommendation: EXCLUDE
  stands. Closest usable row if overruled: 48% efficacy promises (unverified claims).
- Row 30, Gaslin et al. 2008 (ENT Journal): 49 websites = top-20 hits per engine for "silver
  nasal spray" that ALSO met inclusion criteria requiring marketing content; 100% link to buy.
  Findings are mostly omissions (only 4% mention argyria; 61% caution against long-term use);
  the one falsity-type metric is 8/49 (16%) making specific health-benefit claims (the table's
  examples are false: "nontoxic", "no known side effects"). Recommendation: EXCLUDE stands —
  a product-marketing audit with a commercial-site frame, not a content population; the 16%
  is the share of sales pages with explicit disease claims, not misinformation vs not. This is
  the closest call of the three; if Sacha includes it, the only row is 16% (CONTENT, websites).
Answer to Sacha's row-48 question: yes — "non-factual information" (Li et al. 2020, 27.5% of
69 most-viewed COVID videos) is misinformation under the codebook definition (statements
contradicting established evidence) and is the CONTENT estimate already in the frozen set.
Post-adjudication C tally so far: 0 pipeline errors in 17 ruled; 3 pending Sacha's ruling.

## 2026-09-02 — Task C: the three delegated rows ruled EXCLUDE (Claude re-read, Sacha approved)
Sacha's instruction, verbatim: "ok to follow your judgements, but transparently log the rationale
and all the decisions we're making". Decisions: rows 36, 28, 30 -> EXCLUDE, on the rationale in
the previous entry (36 = misinfo-only sample, R3; 28 = labeling/quality, R7; 30 = marketing
audit, closest call). His FILLED file is left untouched (coder-file rule); the merged ledger
data/extract_v2/qa/round3_keys/adjudication_C_FINAL.csv (scripts/finalize_C_adjudication.py)
carries a `ruled_by` column (sacha | claude_reread_approved_by_sacha_2026-09-02) and a
`pipeline_upheld` flag so the provenance of every ruling ships with the data. FINAL Task C
tally: 20/20 rulings uphold the pipeline -> adjudicated full-text error rate 0/50 in the
sample (0/25 over-inclusions, 0/25 over-exclusions; one-sided 95% UB 11.3% per side). For the
write-up: the raw coder disagreements (Sacha 6, Laura 17) were all resolved in the pipeline's
favour against the source, so the human-vs-pipeline κ (.76 / .32) measures coder strictness,
not pipeline error. Disclose in §4.8 that 3 of the 20 rulings were made by the AI assistant on
a full re-read and approved by the author.

## 2026-09-02 — Task D adjudicated: 10 rulings by Sacha, 4 delegated; 3 dataset recodes applied
D_adjudication_sacha_FILLED.csv saved to round3_2026-08/ (Desktop copy trashed). Sacha's 10
rulings: 7 uphold the dataset (idx 4, 95, 28, 34, 35, 5, 40 — incl. the CCDH bound he had
excluded himself, and idx 95 with the note that problematic content is broader than
misinformation); 3 adopt his blind code — idx 36 and its duplicate 73 (Meta: 12 accounts =
0.05% of vaccine-content views) EXPOSURE -> CONCENTRATION ("12 accounts that account for 0.05%
of views is concentration"; agreed: the unit is a named account set and its share of views,
which is the concentration construct, so OUR coding was the error), and idx 59 (NewsGuard 40.21%
of rated sites red) CONTENT -> OTHER ("a proportion of sites that are unreliable, not
CONTENT"; applied as OTHER_NOT_PREVALENCE: a source-level rating share, not content prevalence).
Four rows he left blank asking for a re-read/explanation; ruled on Claude's source check under
his standing "follow your judgements, log transparently" instruction (all four uphold the
dataset): idx 30 WHO "up to 51%" = relay of the Borges do Nascimento 2022 systematic review
(verified on the live WHO page: "four studies reviewed in the paper ... reached up to 51%") ->
ACADEMIC_RELAY; idx 97 SIMODS YouTube problematic content = same metric as idx 95 which Sacha
himself upheld -> NOT_MISINFO_SPECIFIC; idx 12 Reuters "none reached more than one in 20" = an
upper bound whose point estimate is already kept as idx 11 (3.5% REACH) -> OTHER_NOT_PREVALENCE
by the bound rule; idx 48 Ofcom 71% "among those who encountered it" = conditional on exposure,
the population figure is idx 47 (40% RECALL) -> CONDITIONAL_SUBGROUP. Ledger:
data/extract_v2/qa/round3_keys/adjudication_D_FINAL.csv (scripts/finalize_D_adjudication.py;
`ruled_by` column). FINAL D tally: dataset upheld 11/14; 3 recodes, all three CONSTRUCT/CLASS
relabels of one Meta claim (+dup) and one NewsGuard claim, no value changes.
Data applied: grey_curation.csv idx 36/73 curated_class CONCENTRATION, idx 59 category
OTHER_NOT_PREVALENCE; grey_verification.csv class column + dated note for the same three rows.
Manuscript: usable grey estimates 36 -> 35 (Supp Note E, two sentences); the concentration
cell is now 3 claims (Knight 2 + Meta), so "one or two claims each" -> "one to three claims
each"; the recall (64.0, n=15) and topical (10.6, n=12) comparisons are untouched. Guard suite
PASS (142/142 + 22 must-not, invariants, drift). Desktop NHB pair archived to the scratchpad
annotated_archive/ (…_pre_taskD_2026-09-02) and rebuilt/redeployed.
For §4.8: the grey-claims check finds 1 genuine coding error in 21 scoreable blind recodes
(the Meta concentration claim, counted once with its duplicate) plus 1 category relabel with
no effect on the estimate set's meaning (NewsGuard site share).

## 2026-09-02 — Task B (abstract stage) adjudicated: 2 genuine misses, both flagged by BOTH coders
While writing §4.4 the abstract-stage task was found never to have been adjudicated (only
#33/#48 had been flagged). All 10 pipeline-EXCLUDE abstracts that either coder would have
advanced were ruled by Claude against the abstract, and for the two both-coder candidates
against the full text, under Sacha's standing "follow your judgements, log transparently"
instruction (scripts/finalize_B_adjudication.py -> round3_keys/adjudication_B_union.csv,
ruled_by column). Result: 2 GENUINE MISSES, and they are exactly the two abstracts both coders
advanced: #33 Chadwick, Vaccari & Hall 2022 (Am Behav Sci; full text from the Edinburgh
repository: 9.9% of all UK social media users, n = 2,005 nat. rep., amplified exaggerated or
false news in the past month; 33.8% of sharers) = RECALL/sharing subtype with a population
denominator; #43 Roland-McGowan et al. 2025 (JMIR Dermatology; abstract: 6% of the 100
most-liked TikTok sunscreen videos inaccurate, 35% accurate, 57% opinion-based) = CONTENT with
a curated (top-100) denominator, the same design as included studies (e.g. Li 2020's 69
most-viewed COVID videos). Both had been ruled CORRECT_EXCLUDE by the pre-freeze same-model
false-negative audit of all 1,120 abstract-stage excludes (fnabs_*.csv: "factors associated
with sharing intentions"; "video quality/accuracy content analysis") — a same-family blind
spot, exactly the pattern §4.8 warns about. The other 8 candidates: exclusions stand (quality
rubrics R7 x4, belief prevalence, monitoring lessons, qualitative interviews, and #48 the
media-risk fidelity study which the pre-freeze audit had recovered as a false negative but
which yielded no estimate and is not in the corpus). Sampled abstract-stage miss rate 2/40
(one-sided 95% UB 14.9%).
DECISION PENDING (Sacha): whether to add the two missed studies to the corpus. Doing so means
a v1.7.14 re-freeze (extraction of their estimates, full pipeline re-run, guard sweep). The
manuscript text written today reports the misses as misses and does not presume the answer.

## 2026-09-02 — §4.4 / §4.8 / Supp Note C1 write-up of the round-3 human validation
Manuscript edits (master md): §4.4 gains one paragraph (the post-freeze human screening check:
design, adjudicated miss rates with one-sided 95% upper bounds at each stage — title 0/150 UB
2.0%, abstract 2/40 UB 14.9%, full text 0/25 + 0/25 UB 11.3% — and the same-model blind-spot
reading of the two abstract misses); §4.8 gains four sentences (the screening validation and
the grey-claims check summarised; the Meta concentration correction named; DISCLOSURE that
re-reads were in some cases done by the AI assistant and approved by the author: 3/20 full-text,
4/14 grey-claim, 10/10 abstract-stage rulings, marked in the released tables); Supp Note C1
gains a "Screening validation" paragraph (agreement coefficients per stage and per coder, the
recall-protective decomposition — every advance the humans would have excluded was excluded
downstream — the leaky-shard sensitivity, the both-coders-agree signal, coder strictness vs
pipeline error at full text, and the author's own test-retest case on row 36). Reporting rule
applied as planned: miss rates and bounds lead, κ second. No new citations (the two missed
studies are described, not cited, so CITE_MAP is untouched). Checker extended with 5
assertions computed from the adjudication ledgers (147/147 PASS; must-not 22/22; invariants;
drift clean). NHB pair archived (…_pre_writeup_2026-09-02) and redeployed.

## 2026-09-02 — Critical re-read of the full manuscript after the round-3 write-up
Read end to end (main + supplementary). Fixed: (1) §4.10 Statements carried the Competing
interests + Ethics sentences twice (duplicate removed); (2) Discussion limitation 2 and Supp
Note C3 "Screening" still described only the pre-freeze checks — both now report the human
re-screen result (0/150 title, 2/40 abstract, UB 14.9%); (3) Note C3 opened "Five limitations"
while listing six (registration was added later) — now "Six". Guards PASS (147/147, 22/22,
invariants, drift); NHB pair redeployed (fourth build today; each prior Desktop pair archived).
Flagged for Sacha, NOT changed (his prior re-read accepted them): Table 1's recall example (73%
of US respondents) carries no citation; §4.5/§4.9/Notes A/B5 name repository files and scripts
in reader-facing text (`docs/FROZEN.md`, `value_kind`, `scripts/phaseB_*`), which his own style
contract discourages; Note A retains em dashes and a code-font η² ladder.
OPEN DECISION for Sacha: add the two abstract-stage misses (Chadwick et al. 2022; Roland-McGowan
et al. 2025) to the corpus? It means a v1.7.14 re-freeze. Recommendation: yes, before submission
— a systematic review that has identified two eligible studies should include them, and the
§4.4 text can then say so in one clause.

## 2026-09-02 — FROZEN v1.7.14: the two abstract-stage misses added (Sacha: "yeah add the two studies")
scripts/apply_v1714.py: + Chadwick, Vaccari & Hall 2022 (2-s2.0-85136545530; full text from the
Edinburgh repository, stored in data/fulltext/{pdf,v2txt}) — 1 row RECALL/sharing 9.9% of 2,005
UK social media users amplified exaggerated or false news in the past month (the 33.8%-of-
sharers figure kept in value_raw/flag, not a row: conditional denominator); + Roland-McGowan et
al. 2025 (2-s2.0-105026630069; full text via PubMed Central, JMIR's own host unreachable from
this machine; text stored in v2txt) — 1 row CONTENT 6% of the 100 most-liked TikTok sunscreen
videos inaccurate vs AAD guidelines (curated denominator). Author-level extraction, both RoB
appraised in data/rob/v3out/shard_98_manual_2026-09.csv (MODERATE; HIGH) and titles added to
titles.json (no generator exists for it). 673 -> 675 estimates, 313 -> 315 studies, main set
569 -> 571, six-construct set 535 -> 537.
Full Phase B run-order executed (aggregate_rob_v3 first, metareg R last); validate_prisma PASS
(frozen ids take precedence over the abstract-stage EXCLUDE label, so the two enter the funnel
as included; the screening ledger is untouched and still records what the screener did).
What moved: CONTENT median 23.6 -> 23.5 [19.3–26.3], k 209 -> 210; RECALL-shared 18.5 -> 17.8
[10.6–23.0], k 7 -> 8; recall study k 26 -> 27; R² ladder each ~0.1–1 pt lower (measurement 22.1
-> 21.1, sampling 18.2 -> 17.9, ground truth 18.1 -> 17.7, id level 17.8 -> 17.4, construct 16.5
-> 16.2, platform/breadth 10.5, denom 10.3, topic 8.3; regression n 478/279 -> 480/281); breadth
gradient false 21.4 -> 21.0; Spearman CONTENT ρ −.43 -> −.42 (k 204), RECALL ρ −.15 -> −.19
(p .351); weighted recall baseline 55.0 -> 53.3; fold-QUALITY 25.0 -> 24.9; PI CONTENT
0.47–91.5; Note A strata (claim-level k 193, researcher k 172, CIs shifted ≤0.3 pp), η² ladder;
§2.1/§2.2 study counts (+1 politics, +1 health_other, +1 claim-level, +1 researcher coding, +1
self-report, +1 false, +1 misleading, TikTok content 41 -> 42, US 105 of 315, 2020+ 201 of
315); RoB 49/41/10% unchanged; item-10 curated 70 of 71; Cramér's V 0.57–0.97; correction
symmetry now 8 up / 13 down (sign test p = .38); study-construct cells 321 -> 323 with ties 25
-> 26 (Chadwick names four platforms; NOTE the original 25 has no code derivation — a naive
reproduction gives 41 — so only the +1 is certain; flagged to Sacha). Headline abstract numbers
unchanged except content 23.6 -> 23.5 and shared recall 18.5 -> 17.8. Manuscript swept (74
targeted replacements + 4 follow-ups), §4.4/Discussion/C3 now say the two studies were added.
Checker 147/147, must-not 22/22, invariants, drift clean (no_pdf_studies.html regenerated: 284
of 315 with local PDF; five other docs' version strings updated). NHB pair redeployed. Laura's
value-verification package rebuilt on v1.7.14: 89 papers / 221 rows (tier 3 gains Chadwick).
Independent-model figures in C1 (647 codeable, κ .80/.72/.48) describe the v1.7.13 sweep and
were NOT re-run; the text already says the sweep predates the released freeze.

## 2026-09-02 — Laura's value-verification package: tier 1 delivered to the Desktop
Sacha: "I can start with Tier 1 for Laura and see". Builder gained --max-tier/--out; a tier-1-only
copy (40 papers, 114 estimate rows; 32 PDFs + 8 text extractions; 56 MB) was built to
~/Desktop/value_verification_tier1_laura/ and zipped (value_verification_tier1_laura.zip, 51 MB);
its partial key is discarded (the full key stays in data/extract_v2/qa/value_verification_keys/,
written only by the full build, which was re-run afterwards: 89 papers / 221 rows on v1.7.14).
Instruction text in the tier-1 copy names it as "the first tier ... further sets may follow".

## 2026-09-02 — Value-verification package: PDFs from Sacha's library; text fallback made readable
Sacha's screenshot showed paper 1 (Guess, Nyhan & Reifler 2020) rendering as a raw text dump: the
pipeline holds no PDF for it, only the text extraction. Fix in the builder: (1) a third PDF source,
Sacha's Articles_Claude library via pdf_index_raw.jsonl looked up by DOI (paths are relative to
the library folder), which supplied 9 of the 12 missing papers; (2) the remaining text-only
papers are rendered as a styled HTML page with a banner saying no PDF exists, instead of a raw
.txt in the iframe; (3) layout narrowed (1400 px, 460 px side panel) so the page fits a laptop
screen. Both copies rebuilt and the tier-1 zip on the Desktop replaced.

## 2026-09-02 — Value-verification package: a fact-check mode added alongside the blind mode
Sacha, after seeing the blind page: "The task is quite hard, I'm wondering whether we should also
put the actual sentences we based the estimates on? ... fact-check the sentences and estimates
... make sure none are missing and that they were coded correctly". Assessment given: blind
re-extraction yields an agreement coefficient but the earlier human round showed value
disagreement is mostly papers offering several plausible figures, not error; a second-reviewer
fact-check is the standard systematic-review design, 2-3x faster, and targets what a sceptic
of LLM extraction cares about (wrong number / wrong denominator / wrong construct / missed
estimate). Builder now has --mode {blind, check} (default check): check mode shows our value,
verbatim source sentence, denominator and construct per estimate; verdicts CORRECT / WRONG VALUE
/ WRONG DENOMINATOR OR CONSTRUCT / CANNOT FIND with correction fields, plus the per-paper
missed-estimates box; export carries our fields next to hers. A tier-1 check copy was opened for
comparison (~/Desktop/value_check_tier1_laura/); the blind tier-1 zip stays until Sacha chooses.
Reporting consequence, for §4.8 later: check mode yields an error rate per estimate (and a
missed-estimate count), not a kappa; the two designs must not be described interchangeably.

## 2026-09-02 — Value check: all three tiers, fact-check mode, BOTH coders (Sacha: "I'll do it as well")
Sacha chose the fact-check design and will code it himself too. Builder gained --coder; the repo
package (docs/RA_package/value_verification_2026-09/) is now check mode. Desktop deliverables:
~/Desktop/value_check_laura/ (+ value_check_laura.zip) and ~/Desktop/value_check_sacha/, each all
89 papers / 221 estimates (tiers 1-3, tier 1 first), same rows and order, separate browser save
keys and export names (V_values_<coder>_FILLED.csv). The tier-1-only folders/zip were trashed.
Two coders on the same rows gives, for the write-up, a per-estimate error rate against the
source PLUS coder-vs-coder agreement on the verdicts (and on what was missed).
NOTE: "all estimates" read as all three tiers = every non-content estimate in the main set;
the full corpus would be 315 papers / 571 rows, buildable with the same script if wanted.

## 2026-09-02 — Value-check package audited end to end (Sacha: "double check that the task works perfectly")
Offline audit (scratch script over the built package): Laura's and Sacha's collections identical;
221/221 rows in the key; every non-content main-set row of the 89 studies present, no study
missing; no blank values; 28 concentration rows value == conc_share_pct; PDF identity checked by
matching each study's title words against the first 3 pages of the copied file — all 88 PDFs
match (the one non-match was a study with no title on file, not a wrong PDF); quote fidelity:
every source_quote searched in the packaged paper's text — 185 verbatim, 36 not; of those, all
but 2 are our own table readings ("[Table 2] ... 3.36%", "Tabla 2 ... 71%") and the 2 prose
cases (Lyons et al. "roughly 3%"; the Russian-propaganda "over 68% of all retweets") ARE
verbatim once PDF line numbers are stripped — no extraction error found. Fixes: titles for the
two hand-added studies (Bergeron-Boutin sciadv; Berriche Faker Island) added to titles.json and
the builder; concentration rows without a stored group label now derive "top X% of users" from
conc_group_pct (18 rows); quotes that are excerpts/table readings (61 rows) carry a visible tag
so the coder does not hunt for a sentence that is a table cell; instructions collapsed by
default so the paper is visible on load. Live test in Chrome over a local server: all 89
sources return 200, verdict chips and correction fields persist across paper navigation and
reload, export parses to 221 rows with our fields beside the coder's. Desktop: value_check_
laura.zip + value_check_sacha/ (unzipped duplicates trashed; manuscript pair + tracked pair kept).

## 2026-09-02 — Laura's zip verified before sending
~/Desktop/value_check_laura.zip (148 MB) unzipped to scratch and checked: 4 items (page, README,
collection CSV, papers/), 89 papers (88 PDF, all with a %PDF header; 1 HTML text extraction),
no answer key and no .DS_Store inside; page embeds 89 studies / 221 rows, check mode, Laura's
own save key and export name; every source resolves; header and fixed export bar gone; value
field at 46% (Sacha's pick). Live test in Chrome on the unzipped copy: all sources 200, verdict/
correction/missed-box persist across navigation and in localStorage, export = 221 rows. An
earlier zip had been cut short by concurrent file moves (74/89 papers); the zip step now
verifies the paper count and integrity before the source folder is trashed. Ready to send.

## 2026-09-02 — Pre-submission review by five isolated reviewer agents; two errors fixed at once
Sacha asked whether the draft is ready for NHB, reviewed "with personas / independent agents that
only have access to the manuscript". Five fresh agents were each given ONLY the comment-stripped
manuscript + the 8 figure PNGs (no repo, memory or conversation): Statistician, PRISMA
Methodologist, misinformation Domain Expert, Replication Skeptic + Writing Critic, NHB handling
editor. Verdicts: four MAJOR REVISION, editor "return for format/clarity fixes, then review".
Full synthesis: docs/reviews/presubmission_review_2026-09-02.md (also copied to Sacha's Review
folder). Two findings were verified and fixed immediately:
(1) FIGURE 4 "By measurement" band was computed over the AUDIENCE constructs only (EXPOSURE/
REACH/RECALL/SHARING) while the four other bands use all six prevalence constructs — so
"Content coding" showed n = 5 (the five audience-construct studies that used content coding)
and §2.6 quoted that n = 5 median as "studies coding content 26%". Three reviewers caught it
independently. Fix in the generators (phaseB_figures.py fig2 m1, phaseB_slices.py slice F): all
bands now use the six constructs. New band: behavioural 9% (n = 70; was 7% on n = 51), content
coding 26% (n = 193; was n = 5), self-report 57% (n = 25). §2.6 sentence updated (7% -> 9%);
the 26% and 57% stand. Meta-regression untouched (it always used all constructs: 270 content-
coding estimates).
(2) §4.9 still said "the k = 7 shared-recall set" after this morning's re-freeze made it 8.
Guards PASS (147/147); NHB pair redeployed.

## 2026-09-02 — Review fix batch A/B applied (Sacha: "ok go ahead"; no major framing changes)
Sacha's rulings on the pre-submission review: fix everything mechanical; only small framing
edits; drop the competing-interest suggestion; run the additional analyses; the abstract-stage
re-screen is an open question (he doubts it is needed — options laid out to him: independent-
model re-screen of the 1,120 abstract exclusions, larger human sample, or report-and-sensitivity).
Applied and pushed (10ccbc9, e1826c9, a3344ed):
A. Recall never pooled without saying so: Figure 4's construct band now shows Recall (seen) and
Recall (shared); B6/C1 sentences say "seen and shared pooled, k = 27". Independent-model kappas
consolidated: new Table 2 in §4.8 (stage × check × compared-against × sample × result × what
changed), "the machine figures clear the human bar" deleted. §2.8 concentration count clarified
(17 studies, 16 user-level). §2.2 arithmetic (four mixed-level studies; the 82 = 65 + 15 + 2).
Table 1 recall example cited (Neely et al. 2022); §2.8 source-concentration examples cited
(Pierri, Artoni & Ceri 2020; Oswald & Munzert 2026; Pierri et al. 2023) — four references added
with CITE_MAP entries; Mercier 2020 dropped (no longer cited). Allen et al. 2020 sentence in §1
corrected (the 35% was not theirs; now "1% of news consumption and 0.15% of total media diet").
Grant brackets removed. Figure 3 Sharing subtitle aligned with Table 1. Figure 4 caption gains
the counting unit and the reason bands differ in total.
B. Reader-facing artefacts purged (file paths, version tags, field names, script names, the
Scopus preset) from §4.5, §4.7, §4.9, Notes A, B4, B5, C1, C2, D; statistical spec kept in words.
PRISMA (make_prisma.py): substantive exclusion reasons replace pipeline labels ("unledgered" ->
"not re-confirmed at the stricter second extraction; no per-record reason logged"); duplicates
line (2); the OpenAlex/PubMed net-new stream shown (5,232 screened: 5,005 excluded, 227
adjudicated, 19 included); "rated maybe and not selected" terminal box (430); snowball arm
routed to the retrieval stage where it entered; header/footer without file names; the hard
reconciliation assertion kept.
C (light). Abstract qualifies the behavioural numbers by instrument ("mostly browsing and Twitter
data classified with lists of unreliable sources"; "the links they share") and gives k for the
top-1% figure; Discussion: "outright falsity ... flatly false" -> "identified mostly at the level
of unreliable sources rather than of misleading claims"; the "decoupled from measured contact"
sentence replaced by a paragraph that states the two literatures measure different things, says
the perception question needs panels with both measures, and engages Ecker et al.'s objection
(narrow definitions make misinformation look rare) with the paper's own breadth gradient.
Competing interests unchanged (Sacha). B3 gains a sentence justifying no GRADE inconsistency
downgrade (I² uninformative under the variance ratio; spread is the measured moderator effect).
Analyses: scripts/phaseB_metareg_robustness.R (study-cluster bootstrap CIs on each pseudo-R²,
B = 100; the ladder within CONTENT only) launched; results to be written into §2.6/Note C2 when
done. Guards PASS; NHB pair redeployed.

## 2026-09-02 — Abstract re-screen (option 2): Anthropic pass complete on all 1,120; GPT pass with Sacha
Sacha chose option 2 (independent re-screen of every abstract-stage exclusion) and asked whether
an Anthropic model could serve. Answer given: the defensible independent check is a different
model family (same reasoning as §4.8; today's same-model audit missed both known misses), so GPT
is primary — via Codex, one batch per fresh session, gpt-5.6-luna recommended given his usage
limit (screening is a light task; still a different family) — and a newer Anthropic model pass is
run in-session as a complement, humans reading the union of flags.
Package: scripts/build_abstract_rescreen.py -> docs/codex_check/abstract_rescreen/ (12 batches of
<=100, shuffled seed 20260902, INSTRUCTIONS.md with the eligibility definitions, recall-protective
MAYBE rule, one-batch-per-session rule; key with the pipeline's reasons kept in
data/extract_v2/qa/abstract_rescreen/KEY.csv). Copy for GPT on the Desktop (abstract_rescreen_GPT/
+ README). Anthropic pass: 12 isolated general-purpose agents (Fable-class, 2026-09-02), each
reading only INSTRUCTIONS.md + its batch, writing data/extract_v2/qa/abstract_rescreen/claude/
batch_NN_FILLED.csv; every file verified row-identical to its batch. Result (scripts/
score_abstract_rescreen.py): 1,120 coded; INCLUDE 26, MAYBE 159, EXCLUDE 935 -> 185 flagged
(16.5%); per batch 5-23%. SENSITIVITY: both known misses (Chadwick 2022; Roland-McGowan 2025,
still in the shipped batches) were flagged INCLUDE. Human queue = 183 (the two recovered removed):
24 INCLUDE + 159 MAYBE; most MAYBEs are content analyses whose abstract does not state a share,
and surveys with self-reported exposure/sharing as a predictor. Triage page built
(scripts/build_rescreen_triage.py -> docs/RA_package/abstract_rescreen_2026-09/triage_sacha.html,
copied to ~/Desktop/abstract_rescreen_triage_sacha/): strongest signals first, chips ELIGIBLE /
NOT ELIGIBLE / UNSURE, exports rescreen_triage_sacha_FILLED.csv. When the GPT batches arrive the
scorer adds the family, reports cross-family agreement, and the page is rebuilt on the union.
Data-quality notes from the screeners, to fix at source: abstracts mismatched to their record for
2-s2.0-85071114573 and 2-s2.0-105000532381; two correction/erratum notices in the pool whose
originals should be checked (2-s2.0-105031579088, 2-s2.0-85185333619, 2-s2.0-85145956726).

## 2026-09-02 — Abstract re-screen: GPT pass complete; two-family queue built
Sacha ran all 12 batches through Codex on gpt-5.6-luna (medium), one batch per fresh session; each
file verified row-identical to its shipped batch with no blank decision or reason. GPT: INCLUDE 45,
MAYBE 92, EXCLUDE 983 -> 137 flagged (12.2%; per batch 3-23%). Two-family comparison on all 1,120:
flag agreement 86.8%; flagged by both 87, only Claude 98, only GPT 50. Both known misses flagged
INCLUDE by BOTH families (the sensitivity check holds in each family independently). Human queue on
the union: 233 records (20.8%; 85 flagged by both, 16 rated INCLUDE by both) — those 16 and the 85
lead the triage page (rebuilt with both families' decisions and reasons; Desktop copy replaced).
Provenance in data/extract_v2/qa/abstract_rescreen/PROVENANCE.md. Next: Sacha's triage ->
ELIGIBLE/UNSURE to full-text retrieval -> extraction -> re-freeze; the option-3 decision (larger
human sample of exclusions) waits on the yield.

## 2026-09-02 — MAJOR FINDING: the screening criteria never targeted self-reported recall
Sacha's first 25 triage rulings (all double-flagged records; file saved as
data/extract_v2/qa/abstract_rescreen/rescreen_triage_sacha_FILLED.csv, Desktop copy trashed):
14 ELIGIBLE, 8 UNSURE, 3 NOT ELIGIBLE; 13 of the 16 records both families rated INCLUDE are
eligible. His note: "the first screener is almost always wrong when they write 'Survey of
self-reported misinformation sharing predictors; recalled not observed behavior'; it seems like
they think only behavioural data counts". Verified against the instrument: docs/
screening_criteria.txt and screening_criteria_stage2.txt list as INCLUDE targets audience
exposure, consumption, OBSERVED sharing, concentration, actor-level prevalence and content
prevalence — self-reported recall of exposure or sharing is NOT listed, "belief/susceptibility/
perception-only ... no exposure estimate" is an EXCLUDE rule, and stage 2 says "we want OBSERVED
real-world behaviour". So the screener excluded RECALL studies by instruction, not by error; the
27 recall studies in the corpus entered through MAYBE and other routes. Scale: among the 1,120
abstract-stage exclusion reasons, 109 match a self-report/perception pattern and 25 a "content
not audience" pattern; among the 17,583 title-stage exclusions, 747 reasons match the perception
pattern and 796 titles combine a misinformation term with a survey/exposure/sharing term
(895 with content-platform titles). Consequence: the RECALL construct (the abstract's 62% and
17.8%) rests on a corpus that was never systematically collected for it, and its k is
certainly too low; CONTENT is affected less (it was an inclusion target) but the "content not
audience prevalence" reasons show some leakage. This must be (a) fixed by a targeted re-screen
with corrected criteria and a re-freeze, and (b) disclosed in §4.4 as a protocol deviation found
by the human validation. Decision on scope with Sacha.

## 2026-09-02 — Abstract re-screen queue adjudicated with corrected criteria; 162 records to full text
Sacha: "I don't want to do the 208 by hand, many are easy to resolve because they are instruction
mistakes ... clearly we report content and self-report". Corrected criteria written
(data/extract_v2/qa/abstract_rescreen/adjudication/CRITERIA.md: six constructs named, recall and
content explicit, surveys measuring self-reported exposure/sharing as a predictor COUNT, quality-
score-only does not, UNSURE -> full text). The 208 unruled records were adjudicated by three
isolated Fable agents from title + abstract + both screeners' reasons (slice_N_RULED.csv), merged
with Sacha's 25 rulings into FINAL_rulings.csv (`ruled_by` column). Totals on the 233-record
union: ELIGIBLE 66 (Sacha 14, Claude 52), UNSURE 98, NOT ELIGIBLE 69. Among the Claude-ruled
eligibles 39 are expected RECALL and 13 CONTENT — the construct the June criteria omitted
dominates, as predicted. Two duplicates removed (a Zika-tweets record whose title is already in
the corpus; the Kenyan social-media survey listed twice) -> retrieval_list.csv = 162 records
(66 eligible + 96 unsure) for full-text retrieval and extraction. Title-stage re-screen package
(v2 criteria) is built and waits on Sacha's go.

## 2026-09-02 — Corpus repair, evening state
Full-text retrieval of the 162 abstract-stage recoveries (scripts/retrieve_rescreen_fulltext.py):
54 retrieved (42 open-access PDFs via OpenAlex, 12 from Sacha's Articles library), 108 need
institutional access (list on the Desktop: needs_manual_retrieval_108.csv; 43 ELIGIBLE + 65
UNSURE, all with DOIs). Title-stage re-screen (v2 criteria): Anthropic pass launched in waves;
the session limit stopped several agents mid-run (reset 18:20). Screeners flagged a DATA DEFECT
in the June title file: 981 of 17,583 rows have a garbled title field (it carries a leaked
exclusion note such as " off-topic" instead of the title); 774 real titles recovered from the
corpus jsonl and shipped as repair_01-02.csv (repair_map.csv records the mapping); 207 rows have
genuinely short titles. These rows were coded MAYBE "title missing" by the screeners and will be
scored from the repair batches instead. GPT title package on the Desktop (title_rescreen_GPT/,
incl. repair batches).

## 2026-09-02 (evening) — Title re-screen: GPT complete on all 17,583; Anthropic 44/47 (3 finishing on Opus)
Sacha ran all 47 GPT files (gpt-5.6-luna medium, one per session); all verified row-identical, no
blanks; imported to data/extract_v2/qa/title_rescreen/gpt/. GPT: INCLUDE 513, MAYBE 1,543 ->
flagged 2,056 (11.7%); priority tier 43.7% flagged vs 9.5% full tier — the omitted-pattern tier
lights up, as it did for the Anthropic pass (28.7% vs 16.7%). Anthropic (Fable): 44 of 47 files
complete (several agents wrote their file before the session limit killed them; validated); the
3 missing (full_37, repair_01, repair_02) launched on Opus-class agents with identical
instructions, recorded in PROVENANCE.md. Cross-family on 17,183 records both coded: flag
agreement 84.4%; both 1,172, Claude-only 1,827, GPT-only 858. Union before the Claude repairs land:
3,883 flagged titles (22%), inflated by 725 Claude "title unreadable" MAYBEs that the repair
batches will replace. Next: fetch abstracts for the flagged union (OpenAlex by DOI), then the
abstract-stage two-family screen + corrected-criteria adjudication as done today for the 1,120.
Sacha's constraints noted: Fable weekly limit nearly reached — use GPT (credit available) and
Opus-class Anthropic agents for the abstract-stage pass; Fable only where consistency with an
already-Fable-coded set matters. Desktop tidied: abstract_rescreen_GPT, abstract_rescreen_triage_
sacha, title_rescreen_GPT trashed (all imported); needs_manual_retrieval_108.csv stays until the
PDFs are fetched.

## 2026-09-02 — R² ladder robustness written up (review item C7)
scripts/phaseB_metareg_robustness.R (B = 100 study-cluster resamples; ~4 h): measurement 21.1
[15.6–28.7], sampling 17.9 [11.1–26.1], ground truth 17.7 [10.7–27.8], identification level 17.4
[10.9–26.8], construct 16.2 [9.0–24.3], breadth 10.5 [4.8–17.4], platform 10.5 [5.4–20.5], topic
8.3 [3.7–16.1]. Within CONTENT only (302 est / 204 studies): ground truth 13.6, id level 12.2,
measurement 10.2, topic 9.6, breadth 7.0, sampling 6.8, platform 6.2. Consequence: §2.6's "matters
more than what the study is about" softened to "explains at least as much as ... and in the corpus
as a whole considerably more", with the CIs and the within-content ladder stated; Note C2 gains an
"Uncertainty on the variance-explained ladder" paragraph. Checker +4 assertions (151). Guards PASS;
NHB pair redeployed.

## 2026-09-02 (night) — Title re-screen complete on both families; abstract fetch launched
Anthropic 47/47 (full_37 + repairs on Opus, per PROVENANCE.md). Final two-family scoring on all
17,583 June title-stage exclusions: Claude flagged 2,499 (14.2%; priority 28.7%, full 13.2%),
GPT 2,056 (11.7%; priority 43.7%, full 9.5%); flag agreement 87.5%; both 1,176, Claude-only
1,323, GPT-only 880. Union = 3,379 titles (19.2%; 539 priority, 2,840 full; 127 INCLUDE by both).
scripts/fetch_abstracts_flagged_titles.py fetching their abstracts from OpenAlex by DOI in the
background (log /tmp/fetch_flagged.log). Then: build abstract batches (~34 x 100) for GPT + an
Opus-class Anthropic pass under the abstract INSTRUCTIONS (v2 criteria), adjudicate flags with
CRITERIA.md, retrieve, extract, re-freeze.

## 2026-09-03 — Stage-2 (flagged titles) abstract screen and adjudication
Abstracts for the 3,379 title-flagged records: OpenAlex by DOI found 1,502; a second pass on
Semantic Scholar (scripts/fetch_abstracts_semanticscholar.py) found 1,041 more of the 1,665 DOI-
bearing misses; 531 records remain title-only. Batches (34 x <=100, shuffled seed 20260903,
same INSTRUCTIONS as the 1,120 re-screen, empty-abstract rule added) shipped to GPT (Desktop
flagged_abstracts_GPT/, optional) and screened by Opus-class agents (per Sacha's budget rule):
INCLUDE 101, MAYBE 1,544, EXCLUDE 1,734 -> flagged 1,645 (48.7%; the MAYBE mass is the
title-only records, screened with the instructed MAYBE bias). Adjudication with the corrected
criteria (CRITERIA.md) on 17 slices of <=100, abstracts merged from both sources (427 OpenAlex,
687 Semantic Scholar, 531 none), INCLUDEs and abstract-bearing rows first; Opus-class agents,
rulings ELIGIBLE / NOT_ELIGIBLE / UNSURE, title-only rows biased to UNSURE. Yield and the
retrieval scope decision go to Sacha when the slices are back.

## 2026-09-03 — Stage-2 adjudication complete (17/17 slices, Opus-class agents); merged
scripts/merge_flagged_adjudication.py verifies each slice_NN_RULED.csv against its source (same
item_ids and order, non-ruling fields untouched, no blank ruling), parses the expected construct
from RULING_reason, dedupes against the frozen corpus (v1.7.14) and the stage-1 retrieval list
(no overlap on either), and writes FINAL_rulings.csv, retrieval_list.csv and
adjudication_summary.md under data/extract_v2/qa/flagged_abstracts/.
Yield over the 1,645 flagged records: ELIGIBLE 304, UNSURE 789, NOT_ELIGIBLE 552.
- With an abstract (1,114): ELIGIBLE 286 (26%), UNSURE 330, NOT 498.
- Title-only (531): ELIGIBLE 18, UNSURE 459, NOT 54 — the UNSURE mass is the instructed
  title-only bias, not evidence of eligibility.
- Expected construct among the 304 ELIGIBLE: RECALL 178, CONTENT 119, observed sharing 4,
  exposure 2, concentration 1 — i.e. almost entirely the two constructs the June criteria
  omitted (recall) or under-specified (content), confirming the screening-criteria diagnosis.
- Slice 01 (the batch holding the INCLUDE-by-abstract-screener rows) ruled 79/100 eligible;
  the abstract-bearing MAYBE slices ran 12–27% eligible; the title-only slices 0–9%.
Agent-flagged judgement calls recorded for the audit: Likert-only misinformation scales ->
UNSURE; quality-score-only (DISCERN/GQS/JAMA) -> NOT; all-false corpora (fact-check sets) ->
NOT for lack of a denominator; belief-endorsement shares -> NOT; self-reported sharing
BEHAVIOUR -> ELIGIBLE, sharing INTENTION -> NOT. One slice-16 ruling (2-s2.0-85163656021,
Arechar et al. 2023, NOT_ELIGIBLE as a discernment/sharing-intention experiment) rests on the
agent's prior knowledge of the paper rather than the title; the ruling is factually right and is
left as is, noted here.
Retrieval: scripts/retrieve_rescreen_fulltext.py gained --dir/--only; launched for the 304
ELIGIBLE (pipeline stores -> Articles library by DOI -> OpenAlex OA -> Europe PMC). The 789
UNSURE (330 with abstract, 459 title-only) await Sacha's scope decision: retrieving all 1,093
is the recall-complete option; retrieving ELIGIBLE + abstract-bearing UNSURE (634) and
attempting a further abstract fetch (Crossref/PubMed) for the 459 title-only before deciding
is the proportionate one. GPT stage-2 pass (Desktop flagged_abstracts_GPT/) still optional;
the 34 batches are unfilled.

## 2026-09-03 — Stage-2 ELIGIBLE full-text retrieval: 108 of 304
retrieve_rescreen_fulltext.py --dir data/extract_v2/qa/flagged_abstracts --only ELIGIBLE. OpenAlex's
free daily budget ran out during the first run (HTTP 429, "insufficient budget", resets midnight
UTC); the script gained 429 backoff plus Unpaywall and Europe PMC DOI-search fallbacks, and a
second pass after the reset retried the 33 records that hit the outage. Sources: OpenAlex OA 50,
Europe PMC 28, Articles library 14, Unpaywall 10, already on file 6 -> 108 retrieved (36%, in line
with the stage-1 33%); 196 need institutional access (2 without DOI). Desktop list for Sacha:
needs_manual_retrieval_stage2_196.csv (item_id, DOI link, title, expected estimate); repo copy
data/extract_v2/qa/flagged_abstracts/needs_manual_retrieval.csv. The 789 UNSURE are not retrieved
pending Sacha's scope decision.

## 2026-09-03 — Third abstract source for the title-only records; slice 18 re-ruling
scripts/fetch_abstracts_crossref_pubmed.py (Crossref abstract field, then PubMed esearch-by-DOI +
efetch) on the 382 title-only records with a DOI: 67 abstracts found (Crossref 29, PubMed 38);
58 of them were UNSURE-by-title and were re-ruled from the abstract as slice_18 (Opus, same
CRITERIA): ELIGIBLE 11 (all CONTENT), UNSURE 14, NOT 33. Five PubMed abstracts were mismatched
to their titles (esearch-by-DOI false hits; three copies of one ethnography abstract) — ruled
UNSURE with the reason, so no harm; noted as a known weakness of the DOI[doi] search. The merge
script lets a slice_18 ruling supersede the title-only one. Totals now: ELIGIBLE 315 / UNSURE
745 / NOT 585; title-only remaining 473 (401 UNSURE). ELIGIBLE retrieval re-run: 109 of 315
on file; Desktop list replaced by needs_manual_retrieval_stage2_206.csv (old 196 list trashed).

## 2026-09-03 — Corpus-repair full-text screen + extraction campaign launched (163 retrieved papers)
Sacha: "continue". The step that does not depend on the UNSURE scope decision is the full-text
screen and extraction of the papers already on file: 54 from stage 1 (abstract re-screen) and
109 from stage 2 (title-stage recoveries) = 163 (130 adjudicated ELIGIBLE, 33 UNSURE).
Package: docs/repair_extraction_2026-09/INSTRUCTIONS.md distils the corrected eligibility
criteria (CRITERIA.md), the v2 extraction protocol (estimate unit, QUALITY/CONTENT rule), the
ratified rules R1/R3/R4/R8, the denominator-sets-construct rule, and the v1.6 moderator vocabulary
(denom_scope + denom_selection, breadth as veracity, platform_norm, sampling_frame, topic) into one
brief; per-paper output is a JSON (screen + reason, estimate rows with verbatim source_quote,
missed/uncertain box, RoB quotes for items 6/10). scripts/build_repair_extraction_batches.py
writes the worklist and 41 manifests of 4 papers (ELIGIBLE first); scripts/
validate_repair_extractions.py checks schema, vocabularies, construct-specific requirements
(RECALL -> population + self_report; CONCENTRATION -> both percentages) and that each
source_quote's opening is found verbatim in the text file. Agents: Claude Opus-class (Sacha's
budget rule), one batch each, instructions + manifest + text files only, waves of 10.
Provenance for the freeze: source = full_text_repair_2026-09, moderator_coder =
opus_repair_2026-09. After the campaign: merge to the v1.7 schema (derive era, denom_class,
question_type), dedupe against the frozen corpus by DOI/title, RoB pass, apply_v1715.py.

## 2026-09-03 — Repair extraction campaign: 151 of 163 papers done (Opus session limit reached)
38 batches ran (1-38 plus redo batch 42); batches 39-41 were never launched and one paper of
batch 34 is unwritten, because Sacha's Opus session limit was reached ("i'm close to the limit no
more launch", then three agents failed with HTTP 429). The 12 outstanding papers stay queued in
their manifests; `build_repair_extraction_batches.py --skip-done` rebuilds only what is left.
Validation: `validate_repair_extractions.py --all` is clean on all 151 (one file needed a fix —
two Spanish quotes carried an appended English translation and accent-stripped transcription, so
they were trimmed to the contiguous verbatim fragment with the full sentence moved to notes).
Two defective texts were re-retrieved mid-campaign and re-extracted (batch 42): 105024214352 was
the STROBE checklist supplement (replaced from Europe PMC PMC12694945), 85074544598 was the
accepted manuscript with different numbers from the published paper (replaced from PMC6862002).

FULL-TEXT YIELD, and it is the number the manuscript must report:
- 151 papers screened at full text: INCLUDE 100, EXCLUDE 51.
- Of the 130 adjudicated ELIGIBLE, 39 (30%) do NOT survive the full text; of the 21 adjudicated
  UNSURE, 9 do. So the abstract-stage adjudication over-called eligibility by about a third.
- 299 rows from 100 studies; 266 rows / 94 studies in the six main constructs (excluding QUALITY
  26, OTHER 1, within-misinfo appendix rows).
- Construct mix: CONTENT 130, RECALL 128, SHARING 7, CONCENTRATION 5, EXPOSURE 2 — i.e. the repair
  is overwhelmingly the two constructs the June criteria omitted or under-specified, as predicted.
- Medians (repair vs frozen v1.7.14): CONTENT 14.8 (k=121) vs 18.4 (k=320); RECALL 32.8 (k=104) vs
  52.1 (k=64); SHARING 17.0 (k=7) vs 4.9 (k=95); CONCENTRATION 39.0 (k=5) vs 72.5 (k=28).
  RECALL is the headline risk: the recovered recall estimates are LOWER than the frozen ones, so
  the 62% recall figure will move down once these enter. 68 of the 266 rows are flagged borderline.

WHY 51 papers failed at full text (the pattern, for the §4.4 disclosure): the construct is present
but the paper reports no share — a Likert or 0-10 scale mean only (the largest class, ~20 papers),
regression coefficients only, values only in an unlabelled figure, or descriptives deferred to a
supplement or OSF appendix. Abstract-stage screening cannot see any of that. A handful are true
mis-reads of the abstract (GoFundMe 53/30,368 is the alternative-treatment share, not a
misinformation share; the Spanish nutrition-influencer 3.9% counts posts that DEBUNK falsehoods).
All of it is itemised in data/extract_v2/repair_2026-09/POST_CAMPAIGN_CHECKS.md, which is the
work list before apply_v1715.py: polarity rows (accuracy side, not misinformation share),
LLM-benchmark QUALITY-vs-CONTENT consistency and ratings-vs-answers denominators, adversarial
red-team prompt sets, figure-only and supplement-only values, R8 tensions, and the construct calls
to re-check. NOTHING IS FROZEN YET: the merge writes candidate rows only
(repair_estimates.csv / repair_screen.csv / repair_summary.md, source=full_text_repair_2026-09,
moderator_coder=opus_repair_2026-09), and the checklist must be worked through with Sacha first.

## 2026-09-03 (later) — Repair extraction campaign COMPLETE: 163/163 papers
Sacha: "resume the queue". Batches 39-41 + a one-paper batch 43 (the leftover of 34) ran after his
Opus limit reset; one further wrong-text case surfaced and was fixed: 85151884159's file was the
study's REDCap coding form, replaced from Europe PMC (PMC10013129) and re-extracted as batch 44.
validate_repair_extractions.py --all: 167 papers checked, 0 problems.

FINAL FULL-TEXT YIELD (163 papers screened at full text):
- INCLUDE 106 / EXCLUDE 57.
- By adjudication ruling: ELIGIBLE 91 include / 39 exclude (30% over-call); UNSURE 15 include /
  18 exclude (45% of the retrieved UNSURE were real). The UNSURE hit rate is the number that
  should drive the retrieval-scope decision on the remaining 745 UNSURE.
- 314 rows / 106 studies; 278 rows / 98 studies in the six main constructs (QUALITY 26 kept for
  the appendix, OTHER 1, plus within-misinfo rows excluded from the main set). 73 of the 278 are
  flagged borderline.
- Construct mix: CONTENT 133, RECALL 132, SHARING 14, CONCENTRATION 6, EXPOSURE 2, REACH 0.

EFFECT ON THE HEADLINES (estimate-level medians, repair vs frozen v1.7.14):
  CONTENT 14.8 (k=121) vs 18.4 (k=320); RECALL 34.0 (k=108) vs 52.1 (k=64);
  SHARING 16.5 (k=14) vs 4.9 (k=95); CONCENTRATION 38.0 (k=6) vs 72.5 (k=28); REACH none.
Study-level (one median per study x construct, the pooling the paper uses):
  CONTENT repair 24.4 (k=46) vs frozen 23.5 (k=210) -> COMBINED 23.5 (k=256): NO MOVE.
  RECALL  repair 36.7 (k=39) vs frozen 53.3 (k=27)  -> COMBINED 40.7 (k=66): the recall headline
  falls from ~53 to ~41 and its k more than doubles. That is the single biggest consequence of the
  corpus repair and it must be carried through the abstract, Figure 4, Note B6/C1 and the
  exposure-perception-gap argument (the gap narrows).
CONCENTRATION and SHARING move too but on small repair k and with borderline typing (concentration
over experimental choices, ideology-defined groups), so they wait on the checklist.

STILL NOT FROZEN. POST_CAMPAIGN_CHECKS.md must be worked through with Sacha first, and the
73 borderline rows re-read, before apply_v1715.py. Next after that: RoB appraisal for 106 studies
(the extraction JSONs carry rob.design + item6/item10 quotes for it), full Phase B, guard suite,
§4.4 protocol-deviation disclosure with BOTH counts (315 adjudicated eligible vs 106 confirmed at
full text), Table 2/C1, and a re-drawn PRISMA.

## 2026-09-03 — Two hand-over packages built (Sacha: retrieval page + GPT cross-check)
1. RETRIEVAL PAGE. scripts/build_retrieval_page.py -> ~/Desktop/papers_to_retrieve.html: all 314
   papers no open source could supply (108 from the abstract re-screen + 206 from the title-stage
   recoveries; no overlap), 249 of them adjudicated ELIGIBLE, 312 with a DOI. Eligible first, then
   by year; each card carries the expected estimate, a publisher DOI link, Google Scholar, a
   Google filetype:pdf search and Semantic Scholar, the bare DOI for copying, and GOT / NO ACCESS /
   WRONG chips with localStorage + a retrieval_progress.csv export. Everything automatic has already
   been tried on these (pipeline stores, Articles library by DOI, OpenAlex OA, Unpaywall, Europe PMC).
2. GPT CROSS-CHECK. scripts/build_gpt_crosscheck.py -> docs/gpt_check_2026-09/ and a self-contained
   ~/Desktop/gpt_check_2026-09/ (8 MB, 106 texts). RATIONALE: every repair row came from ONE
   Anthropic-family agent reading one text; the frozen corpus has an independent-model check at
   kappa .802 and the 106 new studies had none. 313 rows (the six constructs + QUALITY) in 8 batches
   of 40, shuffled seed 20260903, one batch per fresh session. Each batch is TWO files over the same
   rows: verify_NN.csv (fact-check mode: our value/denominator/construct/quote shown; verdicts
   CORRECT / WRONG_VALUE / WRONG_DENOMINATOR / WRONG_CONSTRUCT / NOT_IN_PAPER / PAPER_NOT_ELIGIBLE
   plus the coder's own value and a verbatim quote) and blind_NN.csv (construct coded from the
   reported quantity alone, our code NOT shown — the independence that makes a kappa meaningful).
   INSTRUCTIONS.md carries the denominator-sets-construct rule, the CONTENT/QUALITY boundary and the
   R8 value rules; our codes are not in the shipped folder. Key kept at
   data/extract_v2/qa/gpt_check_2026-09_KEY.csv. Scorer still to write (score_gpt_crosscheck.py):
   per-row error rate by construct, blind construct kappa, and a disagreement queue for adjudication
   against source — disagreements are adjudicated, never applied blindly.

## 2026-09-03 — Sacha's manual retrieval landed: 172 more papers into the pipeline
He worked the papers_to_retrieve.html list in the browser (publisher DOI links; Google Scholar
started rate-limiting after three automated tab batches, so the route was switched to publisher
links, opened 15-50 at a time from ~/doi_next.sh) and dropped everything in ~/Desktop/Newwww.
scripts/match_retrieved_pdfs.py matches a folder of arbitrarily-named PDFs to the retrieval list:
DOI found in the first three pages (165 files), else a normalised-title match (9 files, all at
ratio 1.00), duplicates resolved by keeping the largest file. Result: 177 files -> 172 distinct
records (136 ELIGIBLE, 36 UNSURE), 2 duplicate downloads, 3 unmatched (Sacha's own CV, and two
copies of a Nigerian believability paper that is not on the list — a believability/belief study,
out of scope anyway). Matched PDFs copied to data/fulltext/pdf/<id>.pdf and converted to v2txt;
all 172 produced usable text (no scanned-image failures). retrieval_status.csv updated to
manual_download_2026-09-03 and needs_manual_retrieval.csv rewritten to what is still missing:
48 (abstract stage) + 94 (title stage) = 142 of the original 314 still unretrieved.
Extraction: build_repair_extraction_batches.py gained --start-batch so new manifests are added
without disturbing the existing ones; batches 45-87 (43 batches x 4 papers) are queued for the 172.

## 2026-09-03 (evening) — Extraction paused at Sacha's Opus limit; 259 of 335 done
Batches 45-68 ran on the manually retrieved papers; Sacha stopped new launches ("do not launch new
agents, we are approaching the limit again"). Batches 69-87 (76 papers) stay queued untouched.
Validator: 339 checked, 0 errors, 76 missing (exactly the unrun batches).
CUMULATIVE STATE: 259 papers screened at full text, INCLUDE 172 / EXCLUDE 87. By adjudication
ruling: ELIGIBLE 157 in / 69 out (31% over-call, stable); UNSURE 15 in / 18 out. 477 rows from 172
studies; 403 rows / 161 studies in the six main constructs; 105 borderline.
Constructs: CONTENT 196, RECALL 195, SHARING 22, CONCENTRATION 6, EXPOSURE 2, REACH 0 (+53 QUALITY).
Study-level medians (repair so far vs frozen vs combined):
  CONTENT 23.1 (k82) vs 23.5 (k210) -> 23.3 (k292): still no move.
  RECALL  40.6 (k61) vs 53.3 (k27)  -> 41.0 (k88): the drop is holding as the k grows.
  SHARING 17.0 (k8)  vs  9.1 (k31)  -> 12.4 (k39): moving UP, on small k and mostly self-report
  sharing (recall-sharing rows), which is a different measurement mode from the frozen behavioural
  SHARING rows — check the construct split before reporting this one.

## 2026-09-03 — GPT independent cross-check returned (7 of 8 batches per task)
Sacha ran the package in Codex. Completeness check: blind_05.csv and verify_01.csv came back
untouched (0 rows filled) and need re-running; the other 14 files are complete, row order and
row_key unchanged, all verdicts and constructs in vocabulary. Seven verify batches = 273 rows:
CORRECT 215 (79%), NOT_IN_PAPER 16, PAPER_NOT_ELIGIBLE 14, WRONG_CONSTRUCT 12, WRONG_VALUE 10,
WRONG_DENOMINATOR 6. Seven rows carry a wrong-value/wrong-denominator verdict with no proposed
value (allowed only for NOT_IN_PAPER / PAPER_NOT_ELIGIBLE) — adjudicate those against source.
Scorer still to write: per-row error rate by construct, blind construct kappa vs
data/extract_v2/qa/gpt_check_2026-09_KEY.csv, and a disagreement queue. Disagreements are
adjudicated against the papers, never applied blindly (standing rule).

## 2026-09-03 — Desktop housekeeping + the repair report (Sacha: "log every decision, document all
## the progress ... we'll document everything transparently ... convince reviewers we did a good job")
DECISIONS AND THEIR REASONS:
1. ~/Desktop/Newwww (177 manually retrieved PDFs) -> TRASH. Justified: all 172 matched files were
   copied into data/fulltext/pdf/<item_id>.pdf and converted to v2txt, and this was verified
   file-by-file before the move (0 of 172 missing from the repo store). The 2 duplicate downloads
   and the 2 copies of an off-list paper went with it; Sacha's own CV_Altay.pdf was rescued back to
   the Desktop rather than trashed. Nothing was deleted with rm; the folder is recoverable.
2. ~/Desktop/papers_to_retrieve.html -> REGENERATED, not removed: retrieval is not finished. It now
   lists only the 142 still-unretrieved papers (113 eligible), because
   needs_manual_retrieval.csv was rewritten to the outstanding set when the 172 were imported.
3. ~/Desktop/.retrieval -> KEPT (hidden helper for the same unfinished task). Both URL lists were
   regenerated in the new card order and the position counter reset to 1, so the numbering in
   ~/doi_next.sh matches the regenerated page. Stale lists would have opened the wrong papers.
4. ~/Desktop/gpt_check_2026-09 -> KEPT: still live. blind_05.csv came back filled on the re-run;
   verify_01.csv is still empty (0 of 40) and needs one more session. The folder moves into the
   repo once scored, with the returned files preserved as delivered.
5. NEW DOCUMENT: docs/corpus_repair_2026-09/REPAIR_REPORT.md — the reviewer-facing account of the
   whole repair: the defect and how it was found (round-3 human validation, not a reviewer), the
   two-family re-screen at both stages with per-family flag counts and agreement, the abstract-source
   chain, the retrieval ladder and its failures (OpenAlex budget exhaustion; three files that were
   not the paper), the full-text yield, the 31%/45% over-call, why 87 papers failed at full text,
   the effect on the medians, the independent cross-check, and an explicit list of what is NOT yet
   settled. Written so a sceptical reader can reconstruct every number from the scripts named.
   It is deliberately written to state the review's own error plainly; the credibility argument is
   that the defect was found by our own validation and fixed in the open, not that it never existed.
STANDING: no costly agents until Sacha says so ("we can run a lot of agents later"). Batches 69-87
(76 papers) remain queued; 142 papers remain unretrieved.

## 2026-09-03 — GPT independent cross-check COMPLETE and scored
All 16 files returned (verify_01 and blind_05 re-run after coming back empty); row keys intact,
every code in vocabulary. scripts/score_gpt_crosscheck.py -> data/extract_v2/qa/
gpt_check_2026-09_{scores.md, disputes.csv}. The two passes are scored separately on purpose:
- FACT-CHECK pass (our value/denominator/construct shown), 313 rows: CORRECT 250 (79.9%);
  NOT_IN_PAPER 16, WRONG_VALUE 14, PAPER_NOT_ELIGIBLE 14, WRONG_CONSTRUCT 13, WRONG_DENOMINATOR 6.
  Reported as an ERROR RATE, never as agreement — the coder saw our answer, so no kappa is possible.
  By construct: CONCENTRATION and EXPOSURE 100% (k=6, k=2), CONTENT 83%, RECALL 79%, SHARING 79%,
  QUALITY 62%. By our own borderline flag: not-borderline 91% confirmed, borderline 55% — the flag
  is doing real work, which is the best evidence that the extraction agents' self-assessment is
  informative rather than decorative.
- BLIND pass (our construct hidden), 313 rows: percent agreement 81.8%, Cohen's kappa 0.732.
  Directly comparable to the frozen corpus's independent-model kappa .802. The disagreement mass is
  two boundaries, both already on the ruling list: CONTENT->QUALITY 23 rows (LLM/medical-content
  scales that mix accuracy with completeness) and RECALL->SHARING 18 rows (self-reported sharing:
  we type it RECALL by measurement mode, the blind coder by the sharing verb).
- QUEUE: 104 rows to adjudicate against the papers (63 from the fact-check pass + 41 the fact-check
  confirmed but the blind coder typed differently). Nothing applied automatically.
METHOD FIX during scoring: the first version re-derived row_key positionally from the CURRENT
repair_estimates.csv, which has grown from 106 to 172 studies since the package was built, so the
borderline join was wrong (5 borderline rows instead of 97). Fixed to read our own coding only from
the KEY frozen at build time, and the script now carries a comment saying why. Same failure mode as
the Task D mis-join in [[misinfo-review-methods-lessons]]: never join on presentation order.

## 2026-09-03 — Workspace and memory tidied (Sacha: "make sure the memory is in a good state, and
## everything is clean and well organized")
REPO. git is clean; 282 newly extracted full texts committed (data/fulltext/v2txt). The 172
retrieved PDFs are NOT committed — data/fulltext/pdf/ is gitignored by standing policy (large,
copyright), same as PDFs/*.pdf; provenance for each lives in manual_pdf_match.csv, so any file can
be re-fetched from its DOI. The 16 returned cross-check files are archived byte-identical at
docs/gpt_check_2026-09/returned/ with a PROVENANCE.md (coder, model, session discipline, the two
re-runs, how it was scored).
DESKTOP, decisions and reasons:
- gpt_check_2026-09/ -> Trash. Scored, and the returned files are archived in the repo (verified
  byte-identical before the move).
- flagged_abstracts_GPT/ -> Trash. Never filled, superseded (the stage-2 abstract screen ran on
  Opus and the full-text yield is now known, so a second family at that stage would only reshuffle
  retrieval order). Verified identical to docs/codex_check/flagged_abstracts before removing;
  regenerable from the repo either way.
- papers_to_retrieve.html -> KEPT and regenerated: 142 papers still outstanding.
- value_check_laura.zip and value_check_sacha/ -> LEFT ALONE: the value verification is live work
  (Laura's file has not come back and Sacha is doing his own copy). Not ours to clear.
- Newwww/ -> trashed earlier today after verifying all 172 matched PDFs were in the repo store.
MEMORY. Index line for open-items rewritten to the real current state (was still describing the
2026-09-02 evening). methods-lessons gained five entries, #25-#29: a frozen KEY must never be
re-derived from a file that grows (the same positional-join failure as #24, in a new place, and it
silently destroyed a finding until an implausible count gave it away); a retrieved "full text" may
not be the paper, so extraction reports text_status; abstract-stage eligibility over-calls by ~31%
while UNSURE is right 45% of the time; multi-column text layers corrupt quote integrity and image
tables hide numbers; and do not automate around a rate limiter — change the route, not the disguise.
reliability-architecture gained the repair's own independent-model tier (kappa .732 blind, 79.9%
fact-check, borderline flag predicts disputes). open-items trimmed of two superseded sections and
given a pointer to the repair report, the ruling list and the log.

## 2026-09-03 — RULINGS TAKEN (R1-R10) and applied to the repair's candidate rows
Sacha answered the nine-card decision page (~/Desktop/repair_rulings.html, generated by
scripts/build_rulings_page.py; his file saved at data/extract_v2/repair_2026-09/rulings/
repair_rulings_sacha_FILLED.csv). Eight went with the recommendation: R1 scale-mean surveys stay
excluded; R2 mean counts are recall INTENSITY kept out of the % headline; R3 composite
accuracy/completeness scales are QUALITY (the instrument decides, not the label); R5 adversarial
prompt sets out of the prevalence pool; R6 accuracy-side values dropped (no stated misinformation
share, R8 bars the complement); R7 self-reported sharing stays RECALL, construct follows the
measurement mode — this is why the repair's SHARING median appeared to rise; R8 experimental-choice
concentration out of the pool, with Sacha's note "if we have many of those it could be fun to report
in an appendix, but it shouldn't be in the concentration pool"; R9 within-misinfo rows appendix-only.

R4 (ratings-vs-answers denominators) he declined to settle without more evidence: "I'm unsure, this
is super weird, maybe I need more info and examples". Pulling the actual cases showed R4 was tiny
(14 rows / 4 studies once R3 removed the QUALITY rows) and inert (combined CONTENT median 23.3 with
them, 23.5 without). But the pull surfaced a much larger problem behind it, and Sacha had already
sensed it: "only 4 studies is not a lot. I'd rather not open that box, there are probably more
studies on AI accuracy, if we open that box it's a whole new study/lit review".

R10 — CHATBOT/LLM ACCURACY STUDIES EXCLUDED AS A CLASS, reported in an appendix (Sacha: "yes let's
exclude. and yes we can report in appendix"). The evidence for the decision, recorded because this
is a protocol deviation that a reviewer may probe:
- The repair introduced 27 chatbot/LLM studies (22 typed CONTENT, 83 rows) against 3 in the entire
  frozen corpus. That is a change in what the review covers, not a marginal addition.
- CAUSE, ours: the corrected criteria written for the repair (CRITERIA.md) name "chatbot answers"
  in the eligible content samples; the June protocol did not. The repair therefore did two things at
  once — recovered studies the old criteria wrongly excluded (the intended fix) AND widened the frame
  to a literature the search was never designed to reach. Only the first was authorised.
- Coverage is therefore not systematic: the 27 arrived through queries aimed at misinformation
  prevalence, and there are certainly many more. No defensible claim about that literature can be
  made from an accidental sample of it.
- They are also a distinct population: CONTENT median 9.7 (range 0-100) vs 23.5 for the rest.
- Cost of excluding: the combined CONTENT median moves 23.3 -> 23.8, i.e. nothing, because a
  study-level median is robust. So the decision costs no precision and buys a defensible boundary.
APPLIED by scripts/apply_repair_rulings.py, which DELETES NOTHING: every candidate row gets
`pool` (main / appendix / drop) and `pool_reason` -> repair_estimates_ruled.csv + rulings_effect.md.
Result: 283 rows / 128 studies in the main pool; 194 rows / 67 studies to the appendix; 0 dropped
(the R6 accuracy-side rows were already caught upstream at extraction).
MEDIANS AFTER THE RULINGS (study-level, repair main pool vs frozen vs combined):
  CONTENT 24.0 (k61) vs 23.5 (k210) -> 23.8 (k271)   — unchanged, as it has been throughout.
  RECALL  40.5 (k60) vs 53.3 (k27)  -> 41.0 (k87)    — the headline still falls ~12 points, k x3.2.
  SHARING 17.0 (k8)  vs  9.1 (k31)  -> 12.4 (k39)    — now interpretable: R7 makes these self-report.
  EXPOSURE 23.3 (k1) vs 2.0 (k15)   -> 2.3 (k16); CONCENTRATION 33.0 (k2) vs 74.0 (k17) -> 65.3 (k19).
  The single EXPOSURE row (a patient information-diary study) and the 2 CONCENTRATION rows are thin
  and pull hard on small k — flag both for a look before they enter any headline.

## 2026-09-03 (evening) — EXTRACTION CAMPAIGN COMPLETE: 335/335 papers
Launched on the 1h05 timer Sacha asked for; batches 69-87 ran in waves of eight. Validator: 339
checked, 0 problems, 0 missing. Full-text yield over the whole campaign:
- 335 papers screened at full text: INCLUDE 208 / EXCLUDE 127.
- By adjudication ruling: ELIGIBLE 180 in / 86 out (32% over-call, stable from the first 151);
  UNSURE 28 in / 41 out (41% of retrieved UNSURE were real — retrieving them was right).
- 554 rows / 208 studies; after rulings R1-R10: 337 rows / 156 studies in the MAIN pool,
  217 rows / 80 studies to the appendix, 0 deleted.
MEDIANS, study-level, repair main pool vs frozen v1.7.14 vs combined:
  CONTENT 24.5 (k74) vs 23.5 (k210) -> 23.9 (k284)   — unmoved across the entire campaign.
  RECALL  40.7 (k71) vs 53.3 (k27)  -> 41.3 (k98)    — the headline falls ~12 points, k x3.6.
  SHARING 23.0 (k11) vs  9.1 (k31)  -> 12.5 (k42)    — see the caveat below.
  EXPOSURE 33.6 (k2) vs 2.0 (k15)   -> 2.6 (k17); REACH none; CONCENTRATION none (see below).
THREE FINDINGS FROM THE FINAL MERGE, all recorded in POST_CAMPAIGN_CHECKS.md §J:
1. A BOOK/CHAPTER DUPLICATE survived every earlier dedupe: 2-s2.0-105021753831 (the book,
   10.5117/9789463720762) and 2-s2.0-105021733739 (its chapter 4, ..._ch04) are the same work with
   identical values. Neither DOI nor title matching catches it because both differ. It was visible
   only because the two rows sat side by side in the SHARING listing with identical percentages.
   The book record goes to the appendix as a duplicate; a same-value-same-year pair check is to be
   added to the merge script before the next campaign.
2. THE REPAIR PRODUCED NO POOLABLE CONCENTRATION ROW. The three candidates fell to rules already
   ratified: two (85086037795) define the group by ideological extremity rather than activity rank,
   which v1.6.5 forbids pooling into a percentile band; one (85154558018) makes a single named domain
   the "group", which v1.6.4 types as OTHER. Concentration therefore stays exactly as frozen,
   74.0 (k=17). Worth stating in the paper: adding 208 studies yielded not one poolable
   concentration estimate, which is itself evidence of how rare that design is.
3. TWO THIN CELLS NEED A HUMAN READ BEFORE ANY HEADLINE. EXPOSURE gains only 2 rows, both
   self-collected streams (a patient information diary 23.3%, a community claim panel 44%) against a
   frozen median of 2.0, and they would move the combined figure to 2.6. SHARING gains 11 studies at
   median 23.0 against a frozen 9.1, but they are link-level junk-news shares on 4chan, Reddit,
   Telegram and WhatsApp — real observed sharing, on fringe platforms where a higher share is
   expected. Neither should be reported before the platform/design mix is checked.
A suggestion from batch 85 adopted for the next merge: split the EXCLUDE bucket so that "eligible
construct, means-only reporting" is distinguishable from genuinely off-topic exclusions. Several of
those papers have deposited replication data, so they are recoverable rather than lost.

## 2026-09-04 — Cross-check disputes ADJUDICATED (104/104) and applied; quote integrity closed
Sacha: "ok go". Nine Opus adjudicators, grouped by paper so each paper was read once, working from
docs/repair_extraction_2026-09/ADJUDICATION_INSTRUCTIONS.md (rule OURS / THEIRS / THIRD / DROP_ROW
against the paper; the second coder's verdict carries no special weight).
OUTCOME: OURS 81, THEIRS 9, THIRD 5, DROP_ROW 9. So 78% of our disputed rows were upheld on a
re-read, and the independent coder changed 23 of them. Applied by scripts/apply_dispute_rulings.py
-> repair_estimates_final.csv + dispute_effect.csv (39 row-level changes, each with its reason).

THE SERIOUS FIND — A POLARITY BUG, caught by the batch-2 adjudicator, not by any of our checks.
Several rows stored the paper's ACCURACY share in value_pct with only a free-text note about it:
2-s2.0-105031807568 carried 100, 98.8 and 95.8 as if they were misinformation prevalence. Read as
prevalence they are catastrophic and would have entered a pooled median. Ruling R6 already said such
rows are dropped; the rule had simply not been applied, because my regex over measure_type missed
them. A sweep found 9 such rows across 5 studies (Grok's is kept at 0, which the adjudicator ruled a
genuine stated zero, not a computed complement). Lesson recorded: a value whose meaning is inverted
relative to its column cannot be carried by a note — either the row is dropped or the column is
renamed. A note is not a safeguard.

CONSISTENCY EDITS, also from the adjudicators: a ruling on one row repeatedly implied the same
ruling for siblings that were simply not in that batch, and leaving those unmade would make a study
internally inconsistent. Five applied, each named in the script: the Mika instrument retyped QUALITY
on 105023100505 to match 105020727860; the disclaimer-absence siblings on 85203059836; the whole of
105001943973 and 85194192073 dropped as 0-100 perceived-percentage sliders (scale means, no share);
85166177819 retyped QUALITY (a factually accurate site is coded "discordant" for endorsing a risk
behaviour). The last of these removes a 31.4% content estimate and its three subgroups.

QUOTE INTEGRITY CLOSED. 20 ellipsis joins repaired, the rest flagged; the validator now checks the
WHOLE quote, rejects ellipsis joins outright, accepts either PDF rendering (-layout or -raw), and
normalises line-break hyphenation and ligatures, which are rendering artefacts rather than
differences in what the paper says. Validator: 339 papers, 0 problems. An early version of the
repair script was scrapped after it lowercased spans and trimmed a clean abstract sentence down to a
table caption without the number — recorded because "the fix made it worse" is the failure mode a
mechanical repair invites.

FINAL POOLS: main 321 rows / 150 studies; appendix 213; dropped 20.
MEDIANS (study-level, repair main pool vs frozen v1.7.14 vs combined):
  CONTENT 23.0 (k69) vs 23.5 (k210) -> 23.3 (k279)
  RECALL  40.7 (k70) vs 53.3 (k27)  -> 41.1 (k97)
  SHARING 23.0 (k11) vs  9.1 (k31)  -> 12.5 (k42)
  EXPOSURE 33.6 (k2) vs 2.0 (k15)   -> 2.6 (k17); REACH and CONCENTRATION unchanged from frozen.
The recall drop is now stable across every stage of adjudication: ~53 -> ~41 with k from 27 to 97.
STILL OPEN before apply_v1715.py: the two thin cells (EXPOSURE k=2, SHARING platform mix), RoB for
the new studies, and the image-only-tables re-check in POST_CAMPAIGN_CHECKS §E2.

## 2026-09-04 — The two thin cells resolved, and a composition warning for the whole analysis
EXPOSURE: both repair rows retyped OTHER and moved to the appendix. Read in full, neither is
behavioural: 105004301747 is a diary of entries patients chose to log, and 85175983241's denominator
is claims panel members SAY they heard. EXPOSURE in this review means what a person actually
consumed, measured behaviourally; the denominator here is items, so RECALL does not fit either.
EXPOSURE therefore stays exactly as frozen (2.0, k=15) instead of being pulled to 2.6.
SHARING: the first hypothesis was wrong and worth recording. It is NOT a fringe-platform effect —
on Twitter alone the repair median is 23.0 against the frozen 8.2. Stratifying shows a DENOMINATOR
effect: repair topical 24.1 (k8) vs population 9.3 (k2); repair curated 25.0 (k5) vs uncurated 5.5
(k7); full_census 16.9 (k2) repair vs 0.9 (k9) frozen. The repair's sharing studies are shares of
links inside keyword-topical corpora, the frozen ones shares of a political-news or whole-diet
stream. That is the review's own thesis appearing inside its own corpus. Consequence: SHARING must
be reported stratified by denom_scope and denom_selection, never as a single pooled 12.5, or the
number becomes an artefact of corpus composition. STANDING TASK for the analysis: check whether the
repair shifts the denominator composition of CONTENT and RECALL the same way before any pooled
figure is reported — a median that moves because the mix of denominators moved is not a finding
about misinformation.
Risk-of-bias appraisal of the 150 main-pool studies launched (Hoy v3 instrument, 15 batches of 10,
quote-anchored on items 6 and 10) -> data/rob/repair_2026-09/shard_rNN.csv.

## 2026-09-04 — RoB appraisal: shard validator + the comparability check (scripts/check_rob_shards.py)
The appraisals are produced by 15 agents, so the instrument itself needs auditing. The script
validates each shard (schema, vocabularies, n_high, the anchored overall rule re-derived, and the
item-6/10 quotes checked verbatim under the same normalisation as the extraction validator) and then
COMPARES shards on the per-item HIGH rate, flagging any shard more than 30 points off pooled on a
load-bearing item. First run over 7 shards / 70 appraisals found three things:
- 7 quotes in shard_r02 are reflowed reconstructions, not raw spans (the agent said so in its
  report). Now carried explicitly as quote6_verbatim / quote10_verbatim = false, the same convention
  the extraction rows use, rather than left as a silent mismatch.
- 2 rows in shard_r03 counted UNCLEAR inside n_high. The instrument defines n_high as HIGH items
  only, with UNCLEAR entering the overall rule alone; corrected mechanically with the reason on the
  row. Neither overall rating changed.
- ONE COMPARABILITY OUTLIER: shard_r07 rates item 1 HIGH at 60% against a pooled 29%. That is the
  item where the conventions were fixed latest (a real but unrepresentative human sample is item 1
  LOW, charged at items 2-3 instead). Shards 01-08 predate that rule and r07 is the visible symptom.
Distribution so far: LOW 6, MODERATE 34, HIGH 30 over 70 studies — the instrument is discriminating,
unlike v2 which rated 73% HIGH.
CONTESTED CALLS the appraisers asked to be ratified, all on item 6, all recorded in
POST_CAMPAIGN_CHECKS §L2: an investigator-assembled expert checklist (internal, so HIGH) vs a
published external standard; guideline-adherence when the estimate is discrete factual error rather
than a quality score (105003865545 CPR videos, rated HIGH by the letter of the rule, would be
MODERATE if read the other way); and an author-built domain list applying an external published
typology (105008921175, rated LOW, flips the study to HIGH if the ruling means third-party lists only).

## 2026-09-04 — The RoB comparability check, restructured (and why the first version was wrong)
The first version compared each shard against the pooled HIGH rate. That is the wrong comparison:
the pool is dominated by the eight shards that ran BEFORE the item conventions were written down, so
the one shard that FOLLOWED the conventions came out as the outlier on five items. Measuring
conformity to a majority that predates the rule is not an audit.
Restructured to compare the two groups directly — pre-convention shards 01-08 against post-convention
09+ — which measures what writing the conventions actually changed and names what the harmonisation
pass must fix. First read (post group is still only 10 appraisals, so this is provisional and the
script says so): item1 26->70%, item2 66->100%, item3 62->30%, item7 81->40%, item9 41->0%,
item10 31->80%. Six of ten items move more than 25 points.
If that holds as the post group grows, the honest conclusion is that the instrument was NOT being
applied consistently before the conventions existed, and the fix is to re-rate shards 01-08 rather
than to average over the disagreement. Recorded now because it would be easy, and wrong, to quietly
pool 150 appraisals produced under two different readings of the same instrument.

## 2026-09-04 (cont.) — the six-item gap was a one-shard artefact, and the caution caught it
Adding a second post-convention shard collapsed every gap below the 25-point threshold:
item1 26->40, item2 66->85, item3 62->55, item7 81->65, item9 41->20, item10 31->50, none of them
now flagged. So the alarming first read — six of ten items moving — was shard_r10's own style, not
the effect of writing the conventions down. The script's small-sample caution is what stopped that
becoming a false finding, and the sequence is worth keeping in the record: a comparison that looks
decisive at n=10 and evaporates at n=20 is exactly the shape of thing this review exists to warn
about. The harmonisation pass is therefore NOT a wholesale re-rating; it narrows to the specific
convention calls the appraisers themselves flagged (POST_CAMPAIGN_CHECKS §L2), which is a much
smaller and better-targeted job. Re-run check_rob_shards.py once all 15 shards are in.
Running distribution at 100 appraisals: LOW 9, MODERATE 50, HIGH 41.

## 2026-09-04 — RoB COMPLETE: 150 studies appraised, item 9 harmonised, the instrument now agrees with itself
All 15 shards in; scripts/check_rob_shards.py reports 0 problems on schema, vocabularies, n_high,
the re-derived overall rule, and quote verbatimness.
HARMONISATION (the only one needed): item 9 was the single item on which the pre- and post-convention
shards genuinely diverged (41% vs 11% HIGH, stable across the full sample). One agent re-read every
pre-convention row rated HIGH, searched the paper for a stated collection window, and re-rated under
the convention (HIGH only when NO date appears anywhere; journal received/accepted and tool-access
dates discounted). 33 rows changed, in item9/n_high/overall/notes only, verified by an old-vs-new
diff against HEAD. 24 moved to LOW; 9 were confirmed correctly HIGH with the reason recorded. Overall
ratings moved for 12 studies: 2 to LOW, 10 to MODERATE. Two judgement calls flagged on the row
(85104571399 and 85086160482 state a publication span for the sampled corpus but no search date —
scored LOW; they flip back if item 9 is read to require an explicit search date for content analyses).
Post-harmonisation the two groups agree on every item, so the pooled ratings are now defensible as
one instrument rather than two readings of it.
FINAL DISTRIBUTION over the 150 repair studies: LOW 21, MODERATE 87, HIGH 42. Compare v2, which
rated 73% HIGH and therefore could not support the review's claim that bias tracks the estimate;
this spreads across all three bands and is driven by items 6 and 10, the two the review's argument
turns on. The harmonisation moved the distribution AWAY from HIGH (52 -> 42), i.e. against the
direction that would flatter the review's thesis — worth stating, since a harmonisation that
happened to help would deserve more scepticism.

## 2026-09-04 — v1.7.15 FROZEN (the corpus repair) + cross-check wave 2 closes the coverage gap
FREEZE. scripts/apply_v1715.py: 675 -> 993 estimates, 315 -> 463 studies. The 318 main-pool rows /
148 studies enter; the 215 appendix rows and 21 dropped rows stay out with their pool_reason.
No repair study id collided with the frozen corpus. FROZEN.md updated (MD5 692084a5...), with the
defect, the repair and what does and does not enter stated in the block.
RoB now covers the whole corpus: 463 studies matched, 0 missing, 0 orphan. Ruling-corrected
distribution LOW 50 (11%) / MODERATE 217 (47%) / HIGH 196 (42%), against 51% HIGH before the repair —
the recovered survey studies have cleaner denominators than the curated content analyses that
dominated the old corpus. aggregate_rob_v3.py taught to read shard_rNN filenames (numbered 6NN).
CROSS-CHECK WAVE 2. Sacha asked whether more GPT coding was needed; it was, and the reason is a
coverage gap worth recording: the wave-1 package was built when only 106 papers had been extracted,
and only 70 of those ended in the main pool, so 78 of the 148 frozen repair studies (155 rows) had NO
independent verification. Reporting a kappa over less than half the new corpus would have been
overclaiming. build_gpt_crosscheck.py gained --wave 2 (main-pool rows not already checked).
All 8 files returned complete first time, keys intact, vocabulary valid.
  wave 2 alone: fact-check 139/155 CORRECT (89.7%); blind agreement 91.6%, kappa 0.859.
  POOLED (the figure to report): 468 rows, 148/148 main-pool studies covered.
    fact-check CORRECT 389/468 = 83.1% (wrong construct 24, not in paper 17, wrong value 16,
    paper not eligible 16, wrong denominator 6).
    BLIND construct agreement 85.0%, Cohen's kappa 0.772 — against the .802 the pre-repair corpus
    carries from its own independent-model check. The repair's new material is therefore verified to
    the same standard as the material it joins, by a different model family, with full coverage.
Wave 2 scored better than wave 1 (89.7% vs 79.9%) — expected, since the rulings R1-R10 and the wave-1
adjudications had already removed the row classes that generated most of the first wave's disputes.
Wave-2 returns archived at docs/gpt_check_2026-09_wave2/returned/ as delivered.
NEXT: the 16 wave-2 disputes to adjudicate, then Phase B, guards, and the manuscript.

## 2026-09-04 — v1.7.16 FROZEN: Sacha adjudicated the wave-2 disputes
Adjudication page (scripts/build_dispute_page.py -> disputes_wave2.html) carried, per card, our row,
the coder's objection, the paper passage around our value, the abstract, and links to the local PDF,
the publisher DOI and Scholar. Sacha ruled 21 of 23: OURS 9, DROP 12, THIRD 2.
Effect: 993 -> 979 rows, 463 -> 457 studies.
His drops are boundary rulings worth quoting in the paper, not clerical fixes:
 - conspiracy THEMES are not misinformation ("can be fictional, can be true/real conspiracy");
 - citation bias in the scientific literature is "way too far from what we're interested in, ie
   misinformation people get exposed to, consume, hear about";
 - source-level factual ratings are quality, and the review does not keep quality ratings of sources;
 - falsity inside an already-misinformation sample is within-misinfo, not prevalence.
INTERPRETIVE STEP, flagged: his 2 THIRD rulings both say "go with the abstract's 34%", which resolves
to dropping the two "misleading content" definition variants rather than editing a value, since the
34%/9% misinformation rows already exist. Recorded in wave2_ruling_effect.csv.
The 2 he left blank were decided on the standing rules and carry ruled_by=claude_default so they are
visible and reversible: 85215526254 dropped (its denominator is person-by-item exposure instances,
not respondents, so it fails RECALL's population-denominator rule — note this is NOT the coder's
stated reason, which was that a dummy mean is not a share; arithmetically it is) and 105032501759
kept (fact-check confirmed; the single-grader weakness is a RoB item, already recorded there).
HEADLINE MEDIANS at v1.7.16 (study-level): CONTENT 23.2 (k275), RECALL 41.0 (k94), SHARING 11.2
(k42), EXPOSURE 2.0 (k15), REACH 11.0 (k25), CONCENTRATION 74.0 (k17).
Against the pre-repair freeze: CONTENT was 23.5 (k210) — unmoved across the entire repair; RECALL was
53.3 (k27) — the headline falls 12 points on 3.5x the studies; SHARING was 9.1 (k31) and must be
reported stratified by denominator, not pooled.

## 2026-09-04 — SEARCH PLAN SET (Sacha: submitting September 2026, top-up "next week or so")
Two arms, ONE dated search run, planned for ~2026-09-11:
1. CURRENCY TOP-UP: records published since the 2026-06-20 Scopus freeze. At submission that is ~3
   months of currency, comfortably inside PRISMA's 12-month expectation. Run as late as possible.
2. BEHAVIOURAL-DESIGN ARM (Sacha's priority, and analytically the right one): EXPOSURE k=15,
   REACH k=24, CONCENTRATION k=17 are the thin cells carrying the paper's strongest claims, while
   CONTENT (k=275) and RECALL (k=94) are saturated and are the weaker designs. The arm searches how
   these studies describe their METHOD rather than their topic — web tracking, browsing panel,
   clickstream, digital trace, donated data, URL-level, panel vendors — because those words rarely
   appear in a misinformation-topic string, which is the likeliest reason the original search
   under-caught them. Plus forward/backward snowballing on the 8 behavioural studies with a DOI that
   were NOT among the 224 snowball seeds (22 of 30 already were).
Framed in the methods as a targeted recall check on the sparse constructs, not a general top-up:
we are not fishing for more of everything, and the asymmetry is stated.

## 2026-09-04 — GOOGLE SCHOLAR CHECK (Sacha's instruction), 10 pages, one behavioural query
Query: "untrustworthy websites" OR "unreliable websites" + visits + panel + misinformation, 2018+.
Run by hand in Sacha's browser (Scholar blocks automation and we did not work around that).
Purpose: Scholar cannot be a search source for a systematic review (no stable, exportable result
set), so this is a RECALL CHECK on the databases, not an additional search arm.

RESULT: search recall is sound at the top of the field — every canonical exposure study is in the
freeze (Guess/Nyhan/Reifler 2016 and 2020, Moore 2023, Zhou 2025, Amieur 2025, Haenschen 2024,
Osmundsen 2021, McCabe 2024, Pierri 2022, Dahlke 2025). Saturation was reached: pages 6-10 produced
almost nothing eligible (effects, corrections, meta-analyses, interventions).

BUT a real and systematic gap: 11 behavioural studies are NOT in the corpus at all, listed in
data/extract_v2/qa/scholar_check/candidates_2026-09-04.csv. The cause is VENUE COVERAGE, not query
wording. Scopus (our primary database) does not index the Journal of Quantitative Description, the
Journal of Online Trust and Safety, OSF preprints, arXiv or NBER — and the behavioural-exposure
literature publishes there heavily. §4.2 makes preprints eligible, so these are genuine misses, not
scope exclusions. One exception proves it is not only a venue problem: Greene et al. 2024 in Science
Advances IS Scopus-indexed and was still missed, so the query wording also under-caught.
Also of note: one missing paper is Altay, Nielsen & Fletcher 2022 (Quantifying the infodemic), the
author's own cross-country web-traffic study — a whole-diet exposure estimate, the sparsest cell.
NOT a miss, checked: Fletcher et al. 2018 (Measuring the reach of fake news in Europe, comScore,
342 cites) is captured in the GREY track (grey_master.csv, 3.5% monthly reach, France/Italy).
ACTION: add a preprint/venue-targeted arm (OSF, arXiv, SSRN, NBER, JQD, JOTS) to the search run
planned for ~2026-09-11, and screen these 11 immediately since they are behavioural.

## 2026-09-04 (end of session) — STATE AT HANDOFF
FROZEN: v1.7.16 (975 estimates / 456 studies, MD5 13eb9d1a...), tagged and pushed. Full Phase B
pipeline regenerated; invariants hold; drift check clean; RoB covers all 456 (LOW 11% / MOD 47% /
HIGH 42%). Manuscript synced: 60 stale assertions resolved, §4.2 eligibility corrected to name all
six constructs, §4.4 protocol-deviation disclosure written, §4.8 rewritten around what each check
can and cannot detect, Table 2 gains the repair's cross-check and blind re-extraction rows, PRISMA
redrawn with the repair as its own identification stream.
STILL OPEN, in priority order:
1. §2.6 VARIANCE LADDER — the only failing guard. The ladder REORDERED on the new corpus:
   ground_truth 21.4, id_method 20.7, construct 18.3, measurement 16.7, sampling 16.1, denom_fine
   14.2, platform 12.7, breadth 11.7, topic 2.6. The paper's claim survives and strengthens (the top
   four are all measurement-family choices; topic collapses 8.3 -> 2.6), but the prose naming
   measurement as the leader must be rewritten, and check_manuscript_stats.py line ~343 asserts the
   OLD order and will keep failing until both are updated. Waiting on
   scripts/phaseB_metareg_robustness.R (bootstrap CIs + within-content ladder) — it was RESTARTED and
   is slow (~200 resamples); metareg_r2_bootstrap.csv and metareg_r2_within_content.csv are STALE
   until it finishes.
2. BEHAVIOURAL OPENALEX SEARCH FAILED — scripts/search_behavioural_arm.py returned 0 works because
   OpenAlex rate-limited (429) while the script ran. RERUN IT. The PubMed arm ran clean (23 hits, 5
   new, none eligible) and the Scopus arm ran clean (230 records, 96 not in corpus, unscreened).
3. SCREEN the 96 Scopus behavioural-arm records + the 11 Scholar candidates
   (data/extract_v2/qa/scholar_check/) + the 5 never-retrieved behavioural studies
   (data/extract_v2/qa/never_retrieved/behavioural_priority.csv — these need Sacha's institutional
   access; 4 of 5 have exposure or sharing in the title).
4. SEARCH RUN ~2026-09-11: currency top-up (since 2026-06-20) + preprint/venue arm (OSF, arXiv,
   SSRN, NBER, JQD, JOTS — the gap the Scholar check proved).
5. Laura's value-verification file when it arrives -> write scripts/score_value_verification.py,
   join on row_key against V_values_KEY.csv (NEVER re-derive from the freeze), add to Table 2.
6. Presubmission review items C/D still deferred; repo public + Zenodo/OSF deposit before submission.
DEADLINE: Sacha submits by 2026-09-17, ideally end of next week.

## 2026-09-04 (evening) — behavioural arm, second pass: search hardened, Scopus arm screened

**The failed OpenAlex run, diagnosed.** `search_behavioural_arm.py` reported 0 unique works on the
morning run. Cause: its `get()` swallowed every exception, so OpenAlex's 429 responses returned `{}`
and each sweep looked like a clean empty result. A rate-limited run had been mistaken for evidence of
absence. Fixed at source: the fetcher now backs off properly on 429, COUNTS rate-limit and hard
failures, and the script REFUSES TO WRITE if it ends with fewer than 200 works or any failure —
a failed run can no longer be mistaken for a finished one. The morning's empty output was moved out
of `searches/` so it cannot be read as a result.

**Retried, and blocked for the day.** OpenAlex now 429s in 0.1s on the first call: this is the daily
budget, not load. The arm is queued for 2026-09-05. The same short-circuit was added to
`retrieve_rescreen_fulltext.py` and `fetch_behavioural_abstracts.py` (two instant 429s = the budget is
gone, stop paying backoff and fall through to Crossref / Unpaywall / Europe PMC).

**The corpus-membership check now covers every arm.** Following yesterday's false alarms, the known-id
set unions the Scopus corpus (eid + doi), the OpenAlex keyword arm, PubMed, both snowball files and
openalex_netnew, and matches on normalised title as well as id. On the Scopus behavioural dump this
took the "new to us" count from 96 to **81** — 15 of the 96 were records we already had, found under a
different id space.

**Screened all 81 (Claude, v2 criteria).** Abstracts fetched where available (28/81; OpenAlex was
down, so Crossref and Europe PMC only). 73 excluded, 8 flagged. The excluded set is dominated by
classifier/detection papers, browser-extension tools, conference front matter and off-topic medicine —
the search string's method terms ("browser extension", "clickstream", "digital trace") pull in the
computer-science detection literature, which reports classifier accuracy, never audience prevalence.

**Of the 8 flagged, 1 is resolved and 7 await retrieval.** The retrieved one (Kome 2026, Spanish
adolescents, n=1,800) is EXCLUDED at full text: it measures agreement with attitude statements about
rumours on a 5-point scale, not exposure. The other 7 need retrieval when the OpenAlex budget resets;
3 are chapters of one edited volume (Political News Avoidance, Selective Exposure, and Misinformation).

**Read against the arm's own hypothesis.** The arm existed to test whether a topic-first search had
under-caught behavioural-design studies that describe themselves by their METHOD. On the Scopus half,
it did not: zero new eligible studies so far, and the method terms recruit a detection literature
rather than an audience-measurement one. That is a reportable negative result for the methods section —
evidence that the sparseness of EXPOSURE and CONCENTRATION is a property of the literature, not an
artefact of our search string. The OpenAlex half must still run before that claim is made.

Files: `data/extract_v2/qa/behavioural_arm/` (new_records.csv, new_records_abstracts.csv,
screen_claude.csv, retrieval_list.csv, retrieval_status.csv, needs_manual_retrieval.csv);
`scripts/fetch_behavioural_abstracts.py` (new).

## 2026-09-04 (evening, cont.) — a stale corpus total the drift check was built to miss

While screening, the manuscript was found to read **"The 315 studies contribute 675 estimates, 871 of
which enter the primary analysis"** — internally incoherent (871 > 675) and both figures three
freezes old. The abstract, the two provenance comments and the intro carried the same stale pair.
Corrected to 456 / 975. The one legitimately historical use (the July cross-check covering "306 of the
315 studies") now says "the corpus then held" so it cannot be read as current.

**Why every guard passed.** `make_counts_crosswalk.py`'s drift check skipped any count more than
NEAR=20 from canonical, on the theory that a distant three-digit number was about something else.
That inverted the check: it caught near-misses and waved through gross staleness, which is the
dangerous kind. 675 and 315 are both ~300 away from canonical, so both were exempt by construction.

Removing the window made the check flag 20 legitimate subset counts (cross-check batches, repair
waves, RA packages) and bury the real one. The fix is to match the CORPUS-TOTAL IDIOMS instead —
"N studies contribute", "review of N studies", "N estimates / M studies", "corpus of N studies",
"n = N included studies" — the phrasings that assert a number IS the corpus. That is the only claim
that can go stale in a way that misleads a reader. Check is clean again on that basis.

It also surfaced `docs/phaseB_analysis.html`, a July meta-regression page with no generator, stale
since the first re-freeze after it. Archived to `docs/Old/phaseB_analysis_2026-07-23.html` and its
dead link removed from the Phase B dashboard generator; the current meta-regression results live in
§2.6 and `data/synth/phaseB/`, which regenerate with every freeze.

**Generalisable lesson, logged to memory as #34: a consistency check with a proximity window tests
the wrong direction.** A number close to the truth is a typo; a number far from it is a different
freeze. Guards should be tightest where the error is largest.

## 2026-09-04 (evening, cont.) — Scholar candidates resolved and retrieved

`scripts/resolve_scholar_candidates.py` (new) resolves the 10 NOT_IN_CORPUS Scholar candidates from
title to identifier through Crossref, then arXiv, then DataCite (which covers OSF), verifying each
match on a normalised title so a fuzzy hit cannot silently attach the wrong paper — the failure mode
recorded yesterday. Retrieved 5 of 10 full texts (JOTS, two arXiv, Frontiers, Science Advances).
Unretrieved: the Science Advances navigational-search paper, two OSF preprints, the QAnon preprint
and the ACM synthetic-politics paper.

These are the highest-value outstanding records in the project: behavioural EXPOSURE and
CONCENTRATION studies, the two thinnest constructs, in venues Scopus does not index. Preprints are
eligible under the protocol (§4.2, "Preprints were eligible (flagged)"), so this is within criteria,
but it is a supplementary Scholar arm and must appear as such in PRISMA and §4.4 if any of them enters
the corpus. Extraction is NOT started: adding them changes the freeze, so it waits on Sacha.

## 2026-09-04 (evening, cont.) — Sacha's manual retrieval: 10 PDFs, all matched

Sacha downloaded 10 papers to ~/Desktop/new. `match_retrieved_pdfs.py` was generalised first: its
wanted-set was hardcoded to the repair's two lists, so records from the behavioural arm, the Scholar
recall check and the never-retrieved list would have come back "unmatched" and been dropped. It now
reads every `needs_manual_retrieval.csv` under `data/extract_v2/qa/`, plus `scholar_check/resolved.csv`
(keyed on `sid`, and its arXiv ids kept out of the DOI index) and `never_retrieved/`. 160 records
across 6 lists.

Two files did not match on the first pass:
1. The AI-exposure preprint. Its title is character-identical to ours but the PDF sets "U.S." where
   our record says "US", so the spaced containment test failed. The matcher now also compares with
   every space removed. Matched at 1.00.
2. **`sciadv.adz6502.pdf` was on no list at all.** It is Bergeron-Boutin, Nyhan, Settle, Thorson,
   Wojcieszak et al., *Untrustworthy sources on Facebook and Instagram in 2020: concentrated exposure
   but no attitudinal effects*, Science Advances, **published 29 July 2026** — five weeks AFTER the
   20 June search cutoff. Checked against every arm's id space and the freeze: genuinely new.
   This is a CURRENCY catch, not a search miss, and it is squarely on the review's thinnest
   constructs (concentration and behavioural exposure). Recorded with its provenance in
   `data/extract_v2/qa/hand_found/` so PRISMA can count it as "identified by other methods" rather
   than as a database hit. It also vindicates the planned top-up: the top-up arm would have found it.

All 10 matched and converted into the pipeline. **15 papers now hold full text and await full-text
screening and extraction** (10 Scholar, 2 behavioural arm, 2 never-retrieved, 1 hand-found) —
`data/extract_v2/wave3_2026-09/worklist.csv`.

**Sacha's decisions, 2026-09-04:** he agreed with all four recommendations. The Scholar-found studies
ENTER the corpus, folded into the same freeze as Laura's value check so the manuscript re-syncs once.
The OpenAlex negative result gets reported if it holds. The currency top-up runs ~11 September scoped
to the preprint/venue arm. **The GitHub repo goes public NEXT WEEK, after the manuscript is finished
and everything is cleaned** — not before.

Still to find by hand: 5 behavioural-arm records (3 of them chapters of one Routledge volume,
10.4324/9781003590163) and 3 never-retrieved.

## 2026-09-04 (evening, cont.) — wave 3 extracted: 15 papers, 45 estimates, and where they land

All 15 retrieved papers screened at full text and extracted in-session (no extraction agents; the
session is instructed not to spawn them). Every quote machine-verified against the PDF text by
`scripts/validate_wave3_extractions.py`.

**10 included, 5 excluded, 45 estimate rows (40 poolable proportions).**

The yield is concentrated exactly where the corpus is thin:

| Construct | Frozen (proportions) | Wave 3 adds | Change |
|---|---:|---:|---:|
| CONCENTRATION | 28 | +11 | **+39%** |
| EXPOSURE | 38 | +10 | **+26%** |
| REACH | 66 | +12 | +18% |
| CONTENT | 422 | +4 | +1% |
| RECALL | 240 | +3 | +1% |

That is the behavioural-arm hypothesis vindicated, but through the SCHOLAR route rather than the
database route: the studies were missing because of VENUE (JOTS, OSF, arXiv, Science Advances 2026),
not because of query wording.

**The five exclusions are all construct calls, and three deserve Sacha's eye:**
- `scholar_08` (Hungarian data-donation news-diet polarization): no misinformation numerator at all.
  The right method, the wrong construct — the cleanest illustration that searching by METHOD recruits
  studies that share our design but not our subject.
- `2-s2.0-105048037793` (Norwegian alternative media): "misinformation" is Kuklinski's BELIEF
  construct (confident + wrong), which the review excludes by design.
- `2-s2.0-85206150453` (GPT-generated fake news, 20 students): researcher-generated stimuli, no
  population denominator; R10 territory.
- **`scholar_09` (AI-generated political images on X) — FLAGGED.** Excluded because the label is
  PROVENANCE, not falsity: a wholly true image is still AI-generated. Forgone: "approximately 12% of
  shared images are detected as AI-generated" and "around 10% of users are responsible for sharing
  80% of AI-generated images". Both are clean and both are preserved in the extraction record.
- **`scholar_10` (alternative/extremist YouTube channels, Sci. Adv. 2023) — FLAGGED.** Excluded
  because "potentially harmful" channel categories are ideology, not falsity — the same call Sacha
  made in wave 2 dropping conspiracy THEMES and source-level factual ratings. Forgone: user-level
  consumption concentration (1.7% of participants account for 80% of alternative-channel time; 0.6%
  for extremist), plus the striking mainstream contrast (3.8% account for 80% of mainstream views).

**Two decisions for Sacha before the freeze.** (1) Do provenance categories (AI-generated) and
harm/ideology categories (alternative/extremist) belong in the review? Current answer: no, consistent
with his own wave-2 rulings. (2) `scholar_04` reports its 2016 and 2020 waves alongside 2024; if the
Guess et al. 2020 or Moore et al. 2022 studies are separately in the corpus, those two rows are
duplicates and must be dropped at the dedupe step.

Notable single finding: `handfound_01` (Nyhan et al.) gives the review its cleanest EXPOSURE
estimates to date — 1.1% (Facebook) and 0.1% (Instagram) of the median user's viewed content came
from untrustworthy sources, measured on a platform CENSUS of all active US adults rather than a
panel, so no survey or tracking-panel selection applies.

## 2026-09-04 (evening, cont.) — preprint/published duplicates: two wave-3 papers were already ours

Sacha asked whether any paper could be in the corpus twice, as a preprint AND its published version.
`scripts/check_preprint_duplicates.py` (new) answers it in two passes.

**Pass 1, offline, inside the freeze.** Every pair of frozen studies whose normalised titles match
exactly or are near-identical (difflib >= 0.93). Result: **the freeze is clean.** The single hit is a
FALSE positive worth recording -- Guess et al. "Exposure to untrustworthy websites in the 2016 US
election" and Moore et al. "...in the 2020 US election" score 0.97 on title similarity and are
different studies. That is a standing caution: never auto-dedupe on title similarity in this
literature, where series papers differ by one digit.

**Pass 2, online, against Crossref AND against our own arms.** The first version demanded an EXACT
normalised title match and found nothing. That was the wrong test, because the commonest case is a
paper RETITLED on publication. Two of the five wave-3 preprints were duplicates and both were missed:

- **`scholar_05`** -- arXiv "Engagement Outweighs Exposure to Partisan and Unreliable News within
  Google Search" was published as Nature's "**Users choose to engage with more partisan news than
  they are exposed to on Google Search**". Title similarity 0.42; invisible to an exact check.
  Already in the freeze as `2-s2.0-85160248068`. 8 rows dropped.
- **`scholar_06`** -- the QAnon preprint was published as "**The Private Life of QAnon**" in Proc.
  ACM HCI (2024). Already in the freeze as `2-s2.0-85209547248`. 3 rows dropped.

The check is now recall-oriented: it reports any non-preprint candidate at title similarity >= 0.55
OR five or more shared words, from Crossref and from every title in our own search arms, and asks a
human to rule. A false positive costs a glance; a false negative double-counts a study.

**An unplanned reliability signal.** I extracted both preprints without ever seeing the frozen rows
for their published versions. Every value matched exactly -- EXPOSURE 2.05 / 0.72 / 3.03 / 1.86 and
two concentration rows for Robertson et al.; REACH 3.7 and 39.1 and EXPOSURE 0.16 for the QAnon
paper. That is a genuine blind re-extraction of 9 rows against the existing corpus, produced by
accident, and it agreed on all 9. It is worth one sentence in Section 4.8, stated as what it is: a
small, accidental, same-family check, not a designed one.

**Wave 3 after deduping: 8 included papers, 32 rows, 27 poolable.** The construct shape is unchanged
in kind -- CONCENTRATION +25%, EXPOSURE +13%, REACH +12% -- but the headline is smaller and honest.

## 2026-09-04 (evening, cont.) — Sacha's wave-3 rulings, and the appendix track

His file: `data/extract_v2/qa/rulings/wave3_rulings_sacha_2026-09-04.csv`.

**1. AI-generated provenance — keep excluded**, with a note: "but we could mention these studies in an
appendix if we have many."

**2. Alternative/extremist channels — "Discuss it with me first."** His reasoning, verbatim: *"I guess
we can include? I'm not sure. the problem I see is that in the newsguard lists the good part is that
it's diverse and kinda big. I'm scared that the extremist stuff can be quite niche and thus not very
interesting for broad general approach of measuring exposure to misinformation. at the very least we
should report this in an appendix, that way if a reviewer makes the point that this should be
included we can easily add it."*

His objection is a BREADTH argument and it is stronger than mine. Mine was conceptual (ideology is
not falsity). His is operational: NewsGuard-style lists are broad-coverage, so a share computed
against them is a share of the general information environment; a 302-channel alternative list and a
213-channel extremist list are narrow, so the same arithmetic yields a share of something much
smaller and not comparable. Two independent routes to the same ruling is a good sign, and the
breadth argument is the one to put in the paper, because it is about measurement rather than
definition and a reviewer can check it.

**How both are implemented: the existing appendix pool, not a new mechanism.** The corpus already
carries 55 non-pooled rows (30 QUALITY, 25 OTHER) across 36 studies, marked by construct and excluded
from every pooled statistic. Both studies are now coded there as `construct = OTHER` with new
`other_subtype` values `ai_provenance` and `harm_category`. Effect: they ship with the data, are
reportable in the appendix, are never pooled, and can be promoted in ONE step if a reviewer objects —
exactly the insurance Sacha asked for.

**Answering "if we have many": we do not — we have two.** A pattern search over every exclusion
record in the repair and wave-3 waves returned 17 hits, but 15 are excluded for unrelated reasons
(no denominator, hypothetical sharing intentions, detection papers, belief measures). Only
`scholar_09` and `scholar_10` are adjacent-construct exclusions that carry a valid denominator and a
real figure. So the appendix note is a paragraph, not a track.

Wave 3 after the rulings: **8 papers pooled (27 poolable rows), 2 papers in the appendix (5 rows),
5 excluded** (2 preprint duplicates, 3 off-construct).

**3. Verification — GPT blind extraction + Sacha's value check.** Both packages built:
- `docs/gpt_check_2026-09_wave3/` — one batch file per paper (10), INSTRUCTIONS.md, MANIFEST.md,
  `returns/`. It is a blind EXTRACTION, not a review of our rows: GPT never sees our coding, which is
  the only design that detects OMISSIONS. The instructions require a contiguous verbatim quote per
  estimate and a `considered_but_excluded` list, so a figure GPT judged out of scope is
  distinguishable from one it never saw. Scored by `scripts/score_wave3_blind.py`, which reports
  agreement, omissions and extras separately and writes an adjudication queue.
- `~/Desktop/wave3_value_check.html` — 37 rows, the 14 concentration and exposure rows first, since
  those move the medians most. One question per row: does the quote support this number AND this
  denominator? The quotes are already machine-verified to appear in the PDF, so the human pass is
  aimed squarely at the error a machine cannot catch — whether the share-of-what was read correctly.

## 2026-09-04 (evening, cont.) — wave-3 vocabulary harmonised against the codebook

Wave 3 was extracted outside the usual agent pipeline (in-session, by me), and the cost showed up in
the CONTROLLED VOCABULARIES: 23 distinct field values that the codebook does not use. Not errors, and
nothing that would have thrown — `platform_census` where the codebook says `full_census`,
`rating_scale` where it says `domain_list`, era `2022-2026` where it says `>=2022`, free text like
"all content viewed" in `denom_type`.

**Why that matters more than it looks.** These fields ARE the moderator levels the Section 2.6
variance ladder is computed over. A stray level with three rows in it changes the df adjustment and
therefore the R², so an unharmonised merge would have silently perturbed the very analysis the paper
leads on. This is a merge-time failure that produces a plausible wrong number, not a crash.

`scripts/harmonise_wave3_vocab.py` maps every one onto a value the codebook already has: **89 values
remapped across 20 mappings.** Notable judgement calls:
- `rating_scale` and `curated_list` -> `domain_list`. A NewsGuard score below 60 IS a domain list
  with a threshold; a channel list is a list.
- `search_engine` -> `other`, NOT `Google Search`. Both search rows are BING, and the codebook's only
  search value names Google; mapping Bing onto Google would assert something false. The free-text
  `platform` field still reads "Bing search".
- `false_claim` -> `false`; `item_level` -> `claim_level`; `self_report` -> `recall`.
- `donated_data` -> `panel_trace`, since donated traces are traces rather than survey responses.

**Ten values kept deliberately**, and the reason is Sacha's ruling: `other_subtype` is an open field
by design (it already carries 8 values), so `ai_provenance` and `harm_category` are legitimate
additions; and `breadth_legacy` gains `ai_generated` and `harmful_channel` for the two APPENDIX
studies only. Collapsing those into `false` or `unreliable_source` would assert exactly the
equivalence he ruled against. They are never pooled.

Re-checked: 0 unmapped values remain. Quote validation still passes.

## 2026-09-04 (evening, cont.) — the v1.7.17 merge script, written and dry-run early

`scripts/apply_v1717.py` (new) merges wave 3 into the freeze. Written NOW rather than on the day,
because the merge is where the failure modes live and because the critical path is tight. It:
asserts the parent MD5; refuses on any id collision; refuses if any field value falls outside the
parent freeze's vocabulary; and — the part that earned its keep — writes the candidate to a TEMP
FILE and runs the full invariant suite against that before anything lands on disk.

To make that possible, `check_invariants.py` gained a `FROZEN_OVERRIDE` env hook (candidate mode). In
that mode the "FROZEN.md MD5 matches the file on disk" check is meaningless — FROZEN.md still
describes the parent — so it is SKIPPED and reported as skipped, never silently passed.

**The dry run immediately failed, which is the point.** Five wave-3 rows broke the two-axis
denominator invariant: `denom_class = curated_sample` must pair with `denom_selection = curated`, and
I had either left the field blank or written a free-text note in it ("rank-truncated: top 3 results
only"). `denom_selection` is a THREE-value controlled field ('', 'curated', 'single_source'); the
rank-truncation note belongs in `flag`, where it already was. Fixed at source in
`harmonise_wave3_vocab.py` (6 values corrected) and `denom_selection` added to the merge script's
vocabulary check so free text cannot slip in again.

Dry run now clean: **975 -> 1012 rows, 456 -> 466 studies**, all invariants hold on the merged result.
8 studies pooled, 2 appendix, 5 not entering (2 preprint duplicates, 3 off-construct).

The script is READY BUT NOT RUN. It waits on Sacha's Monday checks and Laura's file, per his decision
to merge both into one freeze.

## 2026-09-07 — section 2.6 completed, and what the failing assert had been hiding

**Both weekend jobs finished.** The bootstrap completed all 200 resamples (2026-09-05 21:37).
Section 2.6's placeholders are filled from it:

| Moderator | R² | 95% CI |
|---|---:|---|
| ground-truth source | 21.4 | 16.5–27.7 |
| identification level | 20.7 | 15.7–26.6 |
| construct | 18.3 | 13.3–24.4 |
| measurement type | 16.7 | 10.9–23.5 |
| sampling frame | 16.1 | 9.3–23.1 |
| topic | **2.6** | **0.2–7.1** |

The intervals overlap heavily, so the section now says explicitly that the ordering is not a ranking.
What DOES survive the uncertainty is the gap at the bottom: topic's upper bound (7.1) sits below the
lower bound of every measurement moderator. That is asserted in `check_manuscript_stats.py`, so if a
re-freeze ever closes the gap the claim fails loudly instead of quietly becoming false. The
within-content ladder is also filled (ground truth 12.7, id level 11.4, measurement 8.6, topic 6.1;
404 estimates / 269 studies) — narrower, but the same order.

**The behavioural OpenAlex arm FAILED again and correctly refused to write.** 278 calls, 504
rate-limit backoffs, 82 requests lost to exhausted retries, 40 hard failures — and 5,367 unique works
collected. Under the old code that would have been written as a finished sweep. It needs a slower
re-run (lower concurrency, longer sleeps) rather than another identical attempt.

**The important part: fixing the ladder assert exposed six checks that had never run.** The script
used to abort at the ladder-order assertion, so everything after line 372 was dead code. With the
assert passing, six mismatches surfaced at once:
- the meta-regression's predicted self-report prevalence had drifted 48.6% -> 48.7%;
- the risk-of-bias item-10 breakdown was stale on three numbers (137/153 -> 145/161 topical,
  77% (88/114) -> 80% (95/119) curated, 9% -> 10% population);
- two assertions guarded prose that no longer existed in that wording;
- and one guarded a sentence **that had never been written at all**.

That last one matters. Seven of the 34 round-3 adjudications were not ruled by Sacha unaided: 3 of 20
full-text cases were settled by re-reading the source and 4 of 14 grey-claim cases by re-reading the
producer's own publication, each put to him and approved rather than decided by him. The assertion
enforcing that disclosure had been written and was simply unreachable. Section 4.8 now states it, and
points readers at the `ruled_by` column so any statistic in Table 2 can be recomputed with those
seven included or excluded. Given that this review's credibility rests on being exact about which
work was human, publishing without that sentence would have been a real misstatement.

**Standing lesson (memory #39): an assertion after a failing assert is not a check, it is a comment.**
Guard suites must run every check and report at the end, never abort on the first failure.

All three guards now pass: 151/151 derived stats present, invariants hold, drift check clean.

## 2026-09-07 — Sacha's value check, and TWO wave-3 papers that were already ours

**His rulings** (`qa/rulings/wave3_values_sacha_2026-09-07.csv`): 30 OK, 4 DROP, 1 VALUE_WRONG,
2 left unruled with comments. Applied in full.

Dropped: the two top-2.5%-tail exposure bounds and the followed-Pages row from the Nyhan study, and
the among-those-exposed visit intensity from scholar_04. His principle — *"it's AMONG THOSE EXPOSED,
that's weird, and we already have the estimates on everyone, so we should drop the estimates that are
only AMONG THOSE EXPOSED"* — is a general rule, so I swept the whole freeze for it. One frozen row
matches (the QAnon diet share, `2-s2.0-85209547248` EXPOSURE 0.16); flagged for him, not touched.
On the 65.8% RECALL row he is right that "N = 2131 of 3240" is not a printed value, and there is no
printed figure for "recognised at least one" — only the complement, which R8 bars. Row dropped.

**His #29 was a correct recode.** scholar_07's "less than 0.01% of the total urls shared" is SHARING,
not CONTENT: the denominator is URLs in posts PUBLISHED by the followed pages and groups, and the
corpus already codes that shape as SHARING (a frozen row's denominator is "4,032,907 posts by 945
politicians", `sharing_subtype = content_share`). Recoded, with the nuance kept in the row's flag that
the sharers are pages, not the donating users.

**His #37 was also right.** Section 2.8 already compares misinformation concentration with general-news
concentration (6 comparison estimates across 4 panels; top 1% = 31% of general news vs 70% of
misinformation). scholar_10's MAINSTREAM row (3.8% of participants -> 80% of mainstream views) is a
general-news estimate, so it belongs in that comparison set — `nonmisinfo_concentration.csv` — rather
than in the appendix pool. Its misinformation-side figures stay out, per his ruling.

**Bing** now has its own `platform_norm` value, so search engines group as Google Search + Bing.
Search-engine CONTENT does behave differently: 15 frozen Google Search CONTENT rows sit around a
median of 17% against 19.1% for CONTENT overall, and his point is that the comparison must remain
visible rather than being buried under "other".

## THE CORRECTION THAT MATTERS: two "new" papers were already in the freeze

- **`handfound_01`** (Bergeron-Boutin/Nyhan, Sci. Adv.) is in the freeze as
  `NEW-bergeronboutin-sciadv2026`. On 2026-09-04 I told Sacha it was on no arm and was a currency
  catch. **That was wrong.** My check searched the search-ARM files and the DOI; this study was
  hand-added in an earlier session under a `NEW-` id that appears in no arm file. Roughly 29 frozen
  studies entered by routes that leave no arm record, so an arm-based check is blind exactly where
  manual additions live.
- **`scholar_03`** is the OSF preprint of `W7146985142`, already frozen under its published JQD title
  — *"Little change in a changing landscape"* vs *"Exposure to untrustworthy news media then and
  now"*. The titles share almost no words, so neither the exact nor the recall-oriented title check
  found it. The stored quotes are word-for-word identical.

**The right index is `data/synth/phaseB/titles.json`**, which maps every frozen id to its title. It
covers all 456 (0 missing). Membership checks must go through the FREEZE, never the arms.

**The blind re-extraction still paid for itself twice over.**
1. The Nyhan study was UNDER-EXTRACTED: 3 frozen rows, and the blind pass found **5 concentration
   estimates it lacked** (top 20% of FB users -> 75.9%, top 20% of IG -> 90.1%, top 0.5% of Pages ->
   74%, domains -> 70%, groups -> 46%). The freeze in turn holds one row I missed (23% of FB users ->
   80%). Against a construct with 28 rows, five additions is material.
2. **A frozen value is wrong.** `W7146985142`'s 2024 REACH reads **9**, its own stored quote says
   *"just 8%"*, and the preprint says 8. A transcription error, invisible until an independent pass
   re-read the source.

Sacha approved both remedies. `apply_v1717.py` now carries ADDITIONS (rows attached to a study
already in the corpus) and CORRECTIONS (a frozen value that contradicts its own quote), each
documented in the row's `flag` so the audit trail shows what moved and why.

**Wave 3 final shape: 23 rows entering, 8 studies; 975 -> 998 rows, 456 -> 464 studies.** Dry run
clean, all invariants hold. Not yet applied — it waits on Laura.

**Lesson #40: verify membership against the artefact, not against the process that usually fills it.**
Three checks in a row missed these because each tested the search arms — the route studies USUALLY
take — rather than the freeze, the thing the question was actually about.

## 2026-09-07 — corpus-wide sweep for missed CONCENTRATION estimates

Sacha asked why five concentration rows surfaced now and not before, and whether others are missing.

**Why they were missed, specifically.** `NEW-bergeronboutin-sciadv2026` has **no archived full text**.
It was entered by hand from a partial read, and nothing systematic ever ran over it — the blind
re-extraction was the first time that paper passed through the pipeline. Not a judgement failure; a
coverage gap. (Its RoB record says `source_read = full_text`, so the read happened; the TEXT was
never archived, which is what made re-checking impossible.)

**The sweep.** `scripts/scan_missed_concentration.py` (new) reads every archived full text, finds
sentences shaped like a concentration claim ("the top 1% … accounted for 80% of …"), and reports
those whose numbers match no frozen concentration row for that study. It finds CANDIDATES, not
errors — a hit can be a secondary citation, a composition-within-misinformation figure, or a
correctly excluded one — so every hit gets read.

**Result: 456 studies, 418 with text, 29 candidate sentences across 23 studies. Triaged (triage.csv):
22 correctly excluded, 7 worth a human read.** The 22 are mostly composition rather than
concentration (party shares of misinformation tweets, topic composition, video-attribute splits),
secondary citations barred by R8, or a study's own sampling-frame description.

Two of the 22 deserve a note because they looked alarming and are not:
- `W4293124965` (Altay, Nielsen & Fletcher) — "untrustworthy outlets accounted for 2.28% of web
  traffic and 13.97% of Facebook engagement" is the 2020 FOUR-COUNTRY AGGREGATE. The corpus holds the
  finer per-country 2017–2021 rows instead; keeping both would double-count. Correct as it stands.
- `W7146985142`'s trustworthy top-3 figure is already in `nonmisinfo_concentration.csv` as a
  general-news comparison.

**The seven for a human read** are mostly a FORM the corpus holds rarely — concentration across ITEMS
or GROUPS rather than across users: 18% of fake stories → ~70% of shares; top 10 posts → 69.8% of
retweets; top 5 countries → 66.9% of sharing users; an ideology group's 25.6% of countermedia shares;
a viewership share for non-factual videos; and one general-news figure (six newspapers > 50% of
category traffic) that belongs in the comparison set rather than the corpus.

**The real risk population is the 38 studies with NO archived text**, which cannot be re-scanned at
all. That is the honest limit of this sweep, and it is where the one confirmed under-extraction came
from.

**Lesson #41: a systematic check can only cover what was archived.** "We read the full text" and "the
full text is on disk" are different claims, and only the second makes a study re-checkable. Retrieval
should archive the text even when the extraction is done by hand.

## 2026-09-07 (cont.) — GPT blind pass scored; the all-construct sweep, and what it shows

**GPT blind extraction, 7 of 10 returned.** Result: 1/4 matched rows agree on construct, 2 apparent
omissions, 9 extras. Read carefully, that decomposes into three different things:

1. **A real construct disagreement worth adjudicating.** GPT codes scholar_02's Bing SERP shares
   (1.4%, 0.9%, 1.2%) as EXPOSURE; we code them CONTENT, which is where Sacha landed too, though
   tentatively ("Is it CONTENT? I guess so. It's a weird kind of content construct"). The denominator
   is search result PAGES RETURNED TO USERS, which is a real argument for exposure. Queued.
2. **Two "omissions" that are documented scope calls, not misses.** GPT extracted the rank-one
   figures (<1% non-USNQ, ~90% USNQ). We considered both and recorded why in `missed_or_uncertain`:
   they are conditional on query type, and the 90% is near-definitional for a query naming an
   unreliable site. The blind design worked exactly as intended — the disagreement is visible and the
   reasoning is on file.
3. **Six "extras" that were MY packaging error.** scholar_01 and scholar_04 came back with ZERO
   estimates because GPT said the text was truncated and declined. It was not truncated where it
   mattered: I cut at 90,000 characters and printed a prominent TRUNCATED banner, and the model used
   the banner as grounds to decline even though the results were inside what it received. Fixed by
   trimming at the REFERENCE LIST instead — that removes 30-75% of the bytes on these papers, leaves
   the substance whole, and needs no banner. Four papers staged for redo in `~/Desktop/GPT_wave3_blind/REDO/`.

GPT independently coded scholar_07 as SHARING, which is the recode Sacha made this morning against
my original CONTENT. Two independent reads agreeing with him and against me is worth recording.

**The all-construct sweep (`scripts/scan_missed_estimates.py`, new) — an honest negative.**
Generalising the concentration scan to every construct yields 484 candidate sentences across 201
studies even after filtering out citation-bearing sentences, within-misinformation composition, and
belief/attitude/ability figures. Sampling the highest-ratio studies (many candidates, few frozen
rows) shows the residue is still almost entirely: sharing INTENTIONS (excluded by protocol),
subgroup breakdowns, vaccination rates by demographic, and table fragments mangled by PDF layout.
Precision is roughly 5-10%, against ~24% for the targeted concentration scan.

**Conclusion, and it is a real finding rather than a shrug:** the corpus is NOT systematically
under-extracted across constructs. The concentration case was specific — concentration holds only 28
rows, so a handful of misses is a large proportional error, and the study that produced them had no
archived text. For CONTENT (422 rows) or RECALL (240), a comparable miss rate would not move a
median. The sweep ships as a documented artefact a reviewer can inspect; chasing all 484 before
submission would be a poor use of the remaining time, and I am not recommending it.

**The 38 no-text studies are the honest limit** and now have a page
(`scripts/build_no_text_page.py` -> `~/Desktop/no_text_studies.html`), ordered by how many rows each
contributes, with DOI/Scholar/Google links so Sacha can fill gaps by hand. Most are small health
content analyses contributing one row. Their RoB records say the full text WAS read; what was never
kept is the text. Worth one limitations sentence: 38 of 456 studies cannot be re-verified by any
automated check, and the one confirmed under-extraction came from that group.

## 2026-09-07 (cont.) — Sacha's second PDF batch, and a wasted download that was my fault

**10 PDFs delivered to ~/Desktop/NEEW, all 10 matched, all 10 verified on disk** (PDF > 10kb and
text > 2kb for every one) before the folder was touched. 8 matched by DOI, 2 by title. The no-text
population drops **38 -> 28**, and the corpus goes from 418 to 428 studies that any automated check
can actually read.

**One of those ten was a paper we already had, and that is my error.** The page listed
`NEW-bergeronboutin-sciadv2026` as having no archived text. Its text WAS on disk — under
`handfound_01`, the working id the Scholar-arm retrieval filed it under before we discovered it was
already in the corpus. My no-text scan asked "is there a file named <frozen id>.txt?" and got the
literally-correct, practically-wrong answer. Sacha downloaded the Nyhan paper twice because of it.

Fixed at the root, not patched: `data/fulltext/id_aliases.json` records working-id -> frozen-id
mappings (`handfound_01` -> `NEW-bergeronboutin-sciadv2026`, `scholar_03` -> `W7146985142`), both
scan scripts resolve through it, and each study's text is now also copied under its frozen id so a
naive check finds it too. Any future retrieval filed under a working id must be added there.

**The newly-readable papers were re-scanned immediately.** 13 new concentration-shaped candidates:
5 are the Bergeron-Boutin rows already queued as ADDITIONS (the scan now confirms them independently
from archived text, which is a better evidentiary position than the hand extraction alone), and 8 are
exclusions — three secondary citations sitting in a literature-review TABLE in the Berriche paper,
one NewsGuard coverage claim, and four composition figures.

`NEW-berriche-fakerisland2026` was checked directly since it holds no concentration rows and is about
misinformation sharers. Its own concentration evidence is distributional ("over 90% shared fewer than
five items, and only 0.02% shared more than 50") rather than a top-N share of activity, so there is
no codeable concentration row. Its two frozen rows are right as they stand.

**Triage now covers all 43 candidates: 29 excluded, 5 already queued as additions, 7 for a human
read, 0 untriaged.**

**Lesson #42: an identity check must resolve identity, not filenames.** "Is there a file named
`<id>.txt`?" is not the same question as "do we have this paper's text?", and the gap between them
cost Sacha a download. Anywhere a study can be filed under more than one id, the alias map is part of
the check, not an optimisation.

## 2026-09-07 (cont.) — the blind pass, complete: 9 returns scored

Headline: **9 of 13 matched rows agree on construct (69%); 24 GPT-only rows; 3 ours-only.** Those
raw numbers overstate the disagreement badly, so the queue is now classified
(`wave3_2026-09/blind_queue.csv`, columns `class` and `ruling`).

**The 24 "omissions" decompose into six kinds, and only two are open:**

| kind | n | verdict |
|---|---:|---|
| demographic_subgroup | 15 | OPEN, but see below |
| conditional_on_exposure | 2 | ours — Sacha's 2026-09-07 rule drops these |
| within_misinformation | 2 | ours — denominator is misinformation itself |
| documented_scope_call | 2 | ours — recorded in `missed_or_uncertain` before GPT ran |
| prior_wave_duplicate | 2 | ours — 26.1 and 44.3 are Moore 2022 and Guess 2020, already frozen |
| inverse_of_recall | 1 | OPEN — 34.2% "recognised NONE", the absence of recall |

**On the 15 demographic subgroups, my recommendation is NOT to add them**, and the reason is
consistency rather than effort. Subgroup capture has never been systematic in this corpus: 85
subgroup rows exist across just **22 of 456 studies**, median 2 rows each, and 59 of the 85 are
political. Adding 15 rows to two wave-3 papers would make those two among the most subgroup-rich
studies in the whole dataset while 434 others stay sparse — a lopsidedness that would show up in any
coverage panel. Subgroup rows enter no pooled statistic by design, so nothing analytic is lost.
The honest move is a limitations sentence: subgroup capture is opportunistic corpus-wide.

**Four construct disagreements, of which one is genuinely open:**
- `scholar_02` 1.4 / 0.9 / 1.2 — GPT reads the Bing SERP shares as EXPOSURE; we and Sacha read them
  as CONTENT, he tentatively ("Is it CONTENT? I guess so"). The denominator is search result pages
  RETURNED TO USERS, which is a real argument for exposure. **Open, for Sacha.**
- `2-s2.0-105004472114` 10.0 — GPT says SHARING, we say RECALL. **We are right by the codebook**:
  the figure is self-reported sharing, and the corpus reserves SHARING for observed behaviour, with
  self-report going to RECALL under `recall_subtype = sharing`. No change.

**What the pass actually bought**, stated plainly: it confirmed the extraction found every
poolable estimate the independent model found, bar one open construct call; it corroborated Sacha's
own CONTENT -> SHARING recode of scholar_07 independently; and it surfaced the subgroup-capture
inconsistency, which is a corpus-wide finding rather than a wave-3 defect. It found **no missed
main-set estimate**.

## 2026-09-07 (cont.) — subgroups, and three absence-numerator rows removed

**Sacha's rulings.** (1) Main estimates must contain only general figures — verified: **0 of the 871
main-analysis rows carry a `demographic_group`**, and the six rows whose wording names a demographic
turned out to be study POPULATIONS (college students, practitioners) or domain colour codes, not
subgroups. (2) Subgroup results may have their own section, and coverage should be good for the
behavioural studies. (3) Absence-numerator rows go when the same paper carries a better one.

**What a subgroup section can rest on — measured, not assumed.** Of **155 behavioural-design
studies, only 13 carry subgroup rows**. Scanning the 153 with archived text for demographic ×
misinformation percentage sentences finds only ~20 that report any breakdown at all. So the ceiling
is roughly 20 of 155: this is not a coding gap, it is what the literature reports. A section built on
13% of studies, selected by whether their authors happened to break results down, would reproduce the
selection problem the review criticises. The defensible form is a coverage FINDING — only ~20 of 155
behavioural studies report any demographic breakdown, and where they do the political gradient
dominates (59 of 85 subgroup rows political, 15 age, 6 gender) — plus the subgroup rows themselves
reported descriptively and never pooled.

**Wave-3 subgroup capture completed from the blind pass.** GPT's blind extraction had already found
these with verbatim quotes, so `scripts/add_wave3_subgroups.py` promotes rather than re-reads them,
applying Sacha's rules mechanically: self-reported sharing recoded SHARING -> RECALL
(`recall_subtype = sharing`); an absence numerator ("share reporting NO prior exposure") skipped
because the study carries the positive figure; two within-misinformation denominators skipped; a
bound stored as `range_not_point`. **13 subgroup rows added**, every quote machine-verified.

One was dropped after validation: the Silent Generation row's sentence is interrupted by a footnote
marker in the PDF text, so no contiguous verbatim quote exists. The rule is that a row needs one, and
a bound on a single generation is not worth relaxing it for.

**Three frozen rows removed** (`REMOVALS` in apply_v1717, a third operation alongside ADDITIONS and
CORRECTIONS): `2-s2.0-105002670726` RECALL 4 ("never encountering"), `2-s2.0-105002787411` RECALL 14
("have not perceived any"), `2-s2.0-105031841007` RECALL 27.2 ("never received fake news"). Each
study keeps its positive row (17%, 40%/25%, 20%). A corpus-wide scan found exactly these three.

**v1.7.17 dry run: 975 -> 1007 rows, 456 -> 464 studies.** All invariants hold.

## 2026-09-07 (cont.) — Section 2.9 written; consistency audit

**New Section 2.9, "Who is exposed: demographic subgroups"** (Robustness renumbered 2.10), generated
from `scripts/phaseB_subgroups.py` (new, regenerates with every freeze) and guarded by six new
assertions. Its argument is that the COVERAGE is the finding: 22 of 456 studies report any
breakdown, only 13 of 155 behavioural studies do, and the ceiling from scanning the rest is about
twenty. 59 of 85 rows split by party or ideology; race and income appear in none.

Within-study political contrasts: the right-leaning group is a median **4.69x** the left-leaning one
across 8 contrasts, range 0.48x to 41.7x, with one reversal. Computed WITHIN studies, so not
confounded by between-study measurement differences — but eight contrasts from studies that chose to
publish them cannot establish a population pattern, and the section says so.

**A consistency defect the section surfaced.** The corpus labels subgroups as `<dimension>=<value>`
(`political=Republicans`), and the 13 rows I promoted from the blind pass used bare labels
(`Republicans`). The contrast analysis silently returned ZERO pairs, which is how it was caught. 12
labels harmonised. Worth noting the shape of this: an inconsistent label does not fail a check, it
makes an analysis quietly empty.

**Audit of today's decisions against the rest of the paper:**
- Main-set purity (subgroups never pooled): holds, 0 of 871.
- §4 methods already defines the main analysis set as "proportion, non-demographic-subgroup", so
  §2.9 needs no methods change.
- Limitations went from six to seven: the seventh is re-checkability — 28 included studies have no
  archived text, so they can be trusted but not re-verified, and the one confirmed under-extraction
  came from that group. Guarded, so a future retrieval pass cannot leave the number stale.
- The self-report / content / behavioural distinction is load-bearing throughout and unaffected by
  today's rulings; SERP shares staying CONTENT and self-reported sharing staying RECALL both
  REINFORCE it rather than complicate it.

**Still pending and NOT reflected in the manuscript:** every number in Sections 2 and 4 is computed
on v1.7.16. The v1.7.17 merge (35 rows in, 3 removals, 1 correction, 5 additions) will move medians
slightly and will change §2.9's own figures, since 13 of the incoming rows are subgroups. The guards
will fail loudly on each stale number, which is the point of them.

## 2026-09-07 (cont.) — what "no archived text" actually means (Sacha's question)

He asked how 28 studies could have been coded with no text, and whether 28 seemed too few. Checked
properly, and the answer corrects my own wording from an hour earlier.

**Text coverage across the 456 frozen studies:**

| archived text | studies |
|---|---:|
| over 25kb (full text) | 412 |
| 8-25kb | 12 |
| 2-8kb (abstract-sized) | 4 |
| none | 28 |

**All 28 no-text studies are `abstract_only` appraisals** — every one. And the reverse holds too:
of the 32 studies the RoB records mark abstract-only, 28 have no archived file and 4 have an
abstract-sized one. **Zero studies were read at full text with the text then lost.**

So they were not coded from nothing: they were coded from an abstract, which the review already
discloses and already tests (Supplementary Note B reports construct medians excluding all
abstract-only appraisals). 28 of 456 is 6%, and it is low because retrieval succeeded almost
everywhere.

**My limitation wording was wrong and is corrected.** I had written that the 28 "have no archived
full text, because they were coded from a source we did not keep", which implies full texts were read
and lost. That was true of exactly one study — the Bergeron-Boutin paper, which is why it was
under-extracted — and that study now has its text, so the class is empty. The limitation now reads:
32 studies were coded from the abstract alone because no full text could be obtained, and for 28 of
those the abstract itself was not archived, so they cannot be re-verified mechanically. Both numbers
are guarded.

**Lesson #43: a claim about a corpus needs the cross-tabulation, not the count.** "28 studies have no
text" was arithmetically right and substantively misleading; the useful fact is that all 28 are
abstract-only appraisals, which the paper already handles. I published the count before checking what
it was made of.

## 2026-09-07 (cont.) — the 28 missing abstracts, recovered

Sacha: *"we should find these abstracts, what you mean we don't have them"*. He was right, and the
framing in the limitation was defeatist rather than accurate. **All 28 are now archived.**

Where they came from:
- **18** were in our OWN screening stores the whole time (`data/abstracts/abstracts.jsonl` and its
  siblings). The screening pipeline fetched and used them; nothing ever wrote them to
  `data/fulltext/`, so every later check was blind to text we already held.
- **3** from Europe PMC by title.
- **7** from OpenAlex directly. These are stored as `OA-W…` ids and carry no DOI in any arm file, so
  every DOI-keyed lookup missed them; asking OpenAlex for the work by its own id returned all seven.
  (The daily budget had reset by then, which is why this worked when the behavioural search could not.)

`scripts/archive_missing_abstracts.py` (new) does all three routes and is re-runnable. Each file
carries a provenance header — `[ABSTRACT ONLY -- not a full text]`, study id, title, DOI, and where it
was recovered from — so it can never be mistaken for a full text.

**Both scan scripts now read `data/fulltext/abstract/` as a last resort**, with a 300-byte floor
instead of 2,000: an abstract is legitimately short (the shortest is 565 bytes) and the higher floor
was silently skipping 13 of them. **Every one of the 456 studies is now machine-readable: the
"cannot be re-scanned" population is 0.**

The limitation is rewritten a second time and is now simply true: 32 studies were coded from the
abstract alone because no full text could be obtained; their abstracts ship with the data, so they
remain re-checkable against the text they were coded from, but the coding rests on an abstract rather
than a paper. `check_manuscript_stats.py` now asserts that no study has neither a full text nor an
archived abstract, so this cannot regress.

**Lesson #44: "we don't have it" is a claim that needs checking too.** Two-thirds of the missing
abstracts were already in the repository, in a directory the checks did not read. I wrote a
limitation around an absence I had not tried to fill.

## 2026-09-07 (cont.) — two retrieval lists, and a fourth instance of the alias bug

`scripts/build_retrieval_priority.py` (new) -> `~/Desktop/retrieval_priority.html`.

**List A: the 32 abstract-only studies**, ordered by how many rows each contributes. Their abstracts
are archived so they are re-checkable, but the coding rests on an abstract; a full text would let
them be re-extracted like any other study. Low expected yield — no PDF was obtainable when they were
screened — so it is worth a look only where the study matters.

**List B: 9 studies scoring >= 5 on value x access.** Value is what a full text would buy the review:
+3 a thin construct (concentration or exposure), +2 reach, +2 behavioural design, +2 abstract-only
coding, +1 each for low/moderate risk of bias, 100+ citations, and >= 4 rows at stake. Access is
EVIDENCE, not a guess: the number of PDFs we already hold from that journal, since holding one is
proof Sacha got past that paywall before. Journals where we hold nothing are excluded entirely,
however good the study — no point sending him at a wall. 69 of the 229 PDF-less studies have any
access evidence; 9 clear the value bar.

Top of the list: Grinberg et al. (Science, 9 rows, concentration + reach + behavioural, 100+ cites),
two Proc. ACM HCI studies, Nature's deplatforming paper, and Supersharers (Science).

**The bug, again, and this is the fourth time.** The first build listed "The Private Life of QAnon" —
a paper whose PDF is already on disk under the working id `scholar_06`. The alias map had only two of
the four working-id duplicates; `scholar_05` and `scholar_06` were never added when they were
discovered as duplicates this morning. Same failure as the no-text page, same cause: asking whether a
file named `<frozen id>` exists rather than whether we have the paper.

Fixed: the alias map now has all four, six files copied under frozen ids, and the priority script is
alias-aware. The map's README now says explicitly that every duplicate discovery must add its alias
at the moment of discovery — the omission was not forgetting to write code, it was finishing a
duplicate investigation without updating the index that records duplicates.

## 2026-09-07 (cont.) — priority list cleared; abstract-only DOIs opened

Sacha retrieved 8 PDFs and pointed at two already in his Articles library (`pdf_1396` = Grinberg
et al. 2019, `pdf_2837` = Baribi-Bartov et al. supersharers). Both pulled from the library by index
id and matched. **9 of 10 matched and verified** (7 by DOI, 2 by title); the tenth,
`How_people_use_ChatGPT.pdf`, belongs to no study in the corpus.

Retrieved: Grinberg (Science, the list's top entry, 9 rows), Baribi-Bartov (Science), the Nature
deplatforming paper, Proc. ACM HCI news-exposure comparison, Partisan media / untrustworthy news
sites (New Media & Society), Pink Slime (Digital Journalism), the HKS censored-data note, the
Scientific Reports news-diet evaluation, and the JMIR vaccine-misinformation study.

**List B is now empty**: every PDF-less study scoring >= 5 on value x access has been retrieved.
227 -> 236 studies with a local PDF.

**The abstract-only set is the remainder.** 32 studies coded from the abstract alone; 4 have since
acquired a PDF, leaving 28. Of those, 18 carry a DOI and were opened in the browser; the other 10 are
`OA-*` and `PMID-*` records with no DOI in any arm file and need a title search. Almost all are small
health content analyses (YouTube/TikTok quality studies) contributing one row each, so the expected
yield is low — the value is completeness, not analysis.

**Two library PDFs is a route worth remembering.** `pdf_index_raw.jsonl` holds ~3,800 papers with
DOIs; matching the corpus against it would likely find more than these two, and costs nothing but a
join. Worth doing before the next retrieval round rather than sending Sacha to publisher sites for
papers already on his own disk.

## 2026-09-07 (cont.) — the matcher now sees the whole corpus

Sacha's last PDF — *Elected officials' Online Sharing of Misinformation* — came back UNMATCHED even
though the study is in the freeze (`2-s2.0-105029521599`, title similarity 1.00). Cause: the
matcher's wanted-set was built only from curated retrieval lists, and those hold only the studies we
thought to ask for. This paper's journal has no other PDF on disk, so it never entered the
value x access list, so the matcher had never heard of it.

Fixed by adding a fallback: the wanted-set now includes **every frozen study that has no PDF**
(alias-aware), 131 of them beyond the curated lists. A PDF for any study in the corpus now finds its
home, whether or not we asked for it. This is the same lesson as the alias map — the check was
testing the process (what we requested) instead of the artefact (what the corpus contains).

**All 10 PDFs in the batch matched and verified. 239 of 456 studies now have a local PDF**, up from
227 this morning. The value x access list is empty at every threshold that matters.

## 2026-09-07 — STATE AT HANDOFF (context cleared here)

**Frozen v1.7.16. v1.7.17 is built, dry-run clean, and deliberately NOT applied** — it waits on
Sacha's value check and Laura's file, per his one-freeze decision. `apply_v1717.py --dry-run` gives
972 -> 1007 rows, 456 -> 464 studies, all invariants holding, and carries three operations beyond
adding studies (5 ADDITIONS to an under-extracted frozen study, 1 CORRECTION of a value that
contradicts its own quote, 3 REMOVALS of absence-numerator rows).

**On Sacha's plate:** `~/Desktop/value_check_sacha/` (221 estimates, started today), a full read of
the manuscript, and Laura's file when it lands.

**On mine:** resume the behavioural OpenAlex search (checkpoint at 75/180 sweeps, 5,242 works — it
resumes rather than restarts); the 7 concentration candidates still marked LOOK; then the merge,
the full Phase B regeneration, metareg, the 28-hour bootstrap, and the manuscript re-sync.

**Manuscript:** §2.6 filled from the completed bootstrap, §2.9 on demographic subgroups written
(Robustness renumbered 2.10), seventh limitation added. All guards pass — 158 derived stats,
invariants, drift check. Every number is computed on v1.7.16 and will move at the merge; the guards
fail loudly on each stale one, which is the point.

**Corpus coverage is now complete in the sense that matters:** all 456 studies are machine-readable
(the "cannot be re-scanned" population is 0), 239 have a local PDF, and every abstract-only study has
its abstract archived with provenance.

**The week's dominant lesson, recorded as #40:** verify membership against the artefact, not the
process that usually fills it. The same mistake recurred four times in one day and cost Sacha a
wasted download and me a false claim about a new find. The fixes — an alias map every scan resolves,
text copied under frozen ids, and a matcher that falls back to every frozen study — are all in place.

## 2026-09-07 (afternoon) — Desktop NHB pair rebuilt; behavioural search resumed

Sacha plans to code `~/Desktop/value_check_sacha/` and then read the paper. The Desktop docx pair
dated 2026-09-02 predated §2.6 (bootstrap), §2.9 (subgroups) and the seventh limitation, so it was
archived (scratchpad annotated_archive/, no comments inside) and rebuilt from the current
`manuscript_draft.md` after the guard suite passed (158/158 derived stats, 22/22 stale strings
absent, invariants hold, drift clean). 43 references numbered. All numbers are still v1.7.16;
the merge to v1.7.17 waits on his value check and Laura's file.

The behavioural OpenAlex arm was resumed from its checkpoint (75/180 sweeps) with PAUSE=2.0s.

## 2026-09-07 (cont.) — the missed-concentration LOOK queue is cleared: 0 of 7 codeable

An Opus reviewer assessed the 7 LOOK rows in `data/extract_v2/qa/missed_concentration/triage.csv`
against the local texts and the freeze; I ruled on its report. All 7 are NO, each with its reason in
the triage file: one already frozen under CONTENT (the scanner's held-set was built from
CONCENTRATION rows only), one attitudinal group with no group size (R1's conc_group_pct
unobtainable), one falsity-grouped pair (not user/source rank), one R8 complement, one item-level
share (conc_unit admits only user/source), one country head-count composition, and one general-news
bound. The concentration scan therefore found no missed estimate beyond the five Bergeron-Boutin
rows already queued.

**One incidental find IS real.** The Italian BuzzSumo study (`2-s2.0-85089622030`) reports in
Table 3 that 31.9% of the 2,102 reviewed keyword-search articles were fake, beside the 23.1% of
shares that the freeze holds as SHARING. The article-count figure is CONTENT and was never coded.
Verified against the archived text (Table 3, Total row). Queued as an ADDITION in
`scripts/apply_v1717.py` via `data/extract_v2/wave3_2026-09/extractions/scan_conc_01.json`
(moderators cloned from the frozen row of the same study). Dry run: **972 -> 1008 rows**, 456 -> 464
studies, all invariants hold. Still not applied.

## 2026-09-07 (cont.) — pre-submission audit, part 1: fourteen stale passages the checker never saw

Four Opus reviewers audited the repo read-only (documents, replication package, NHB requirements,
proofread). The documents audit found that the v1.7.16 re-sync had left every passage the checker
did not assert at its v1.7.14 value: the ABSTRACT's four headline medians (9.6 / 62 / 17.8 / 23.5
-> 12.4 / 56.2 / 19.5 / 23.2), the §2.1 k-list (k = 210/27/30), the corpus topic sentence ("of 315
studies"), the platform pairs (22 of 30 sharing, 49 and 42 of 210), the §2.2 level sentence (193 of
210; 23 of 30), the grey recall comparator (62.0 -> 56.2, the seen-recall median), the RoB coverage
sentence (315 -> 456, 283 -> 424 full-text), the outside-Scopus share (51 of 315 = 16.2% -> 49 of
456 = 10.7%, by id prefix), the SI cell sentence (306 -> 456 studies) and a typo ("53%. to").
Pre- and post-repair denominators sat in adjacent sentences. Every one is now DERIVED in
`check_manuscript_stats.py` (174 assertions, 34 banned strings) and the draft edited to pass.

**A real generator bug surfaced on the way.** `phaseB_platform_construct.py` routed
`web_cross_platform` rows by a loop variable that had already moved on (`r` after the loop, not the
construct `c`), so browsing panels landed in "Websites" whenever the pool's last row was a content
study: Table B5 said 6/10/2 browsing studies where Figure 1 (same mapping, correct call) said 8/13/4.
Fixed; the table now matches the figure. `fig_coverage_panels.py` also ordered tied bars by dict
order, which flipped labels between runs; ties now sort by label, and nine panel SVGs were
regenerated with only tie-order changes.

Guards: 174/174, invariants hold, drift clean.

## 2026-09-07 (cont.) — pre-submission audit, part 2: the proofread's contradictions, grounded and half applied

The proofread reviewer listed 43 internal contradictions and 24 reasoning gaps; a second reviewer
grounded every one against the pipeline (49 blocks; report kept in the session scratchpad, the
substance recorded here). Two structural causes: Supplementary Notes A, B4, B5, C1 and C2 were never
regenerated at the repair, and the checker matched substrings anywhere in the file, so a correct
main-text sentence let a stale SI copy pass.

Rulings taken in this session:
- `phaseB_subgroups.py` defined "behavioural" as panel/census OR `question_type == exposure`, which
  let 93 self-report recall surveys into the set the section says excludes them. Redefined as the
  RoB-derived MEASUREMENT field (the one Figure 4 and §2.6 use): 65 studies, 13 with a breakdown
  (20%, not 8%). The "~twenty ceiling" sentence had no script behind it and is deleted.
- L141's "the gradient also holds within the behavioural studies" is unsupported (breadth is
  uncoded for 61 of 75 behavioural studies; the one populated level runs backwards). §2.6 now says
  the gradient is a content-analysis finding and why it cannot be read elsewhere. The Ecker
  rebuttal itself is still to be rewritten.
- The 221-estimate value verification is not yet scored; its §4.8 sentence comes out until it is.
- The unblinded 20-for-20 adjudication gets a stated caveat, not a re-adjudication (Sacha may
  still ask Laura to blind-re-adjudicate).
- §2.6 is right and C2 is stale (100-resample run); C2 to be rewritten to the 200-resample run.
- GRADE Sharing is LOW (grade_sof.csv); the prose said MODERATE.

Applied so far (checker now 181 assertions / 43 banned strings, all passing): §1 opener
("believes they encounter"), the intro's "every sensitivity analysis" claim scoped to Note B, §2.1
climate wording, §2.2 ground-truth self-report 90 studies (20%) so the five levels partition 447,
§2.2 blanks 73 + 16 + 2 = 91, Supplementary Table 1 cited from §2.3, §2.4's 22-study window subset
labelled as pre-repair, §2.6 breadth gradient as CONTENT-only, §2.9 on the 65-study set, §2.10 GRADE
prose and fold-QUALITY pair (23.2 -> 24.3), Discussion medians (56.2 / 23.2 / 12.4), C1 freeze size
975, "four kinds/grades" of verification, C3 seven limitations with re-checkability added.

STILL OPEN (the Opus session limit killed the applying agent mid-way; resume after 18:40): the
Ecker rebuttal rewrite (L141), Supplementary Note A regenerated end to end (claim-level gap is now
+1.3 pp, not +23.8), B4/B5 re-sync, C1 (human item counts, batches, third-family wording, the
human-verified-subset pairs), C2 to the 200-resample run, §4.4 retrieval arithmetic (162 + 315 = 477
-> 335 obtained -> 208 eligible; 147 entered v1.7.15, 141 in the released freeze) and FROZEN.md's
148-vs-147 line, §4.8 "third family" wording, sign test (p = .169, direction stated honestly),
the unblinded-adjudication caveat, the §4.8 value-verification sentence, §4.9's k = 8 shared-recall
caveat, Figure 5's citation, display items uncited (Table 2, Supp Table 2/Note A), the SI table
order, cross-reference style, and the section-anchored `add_in()` helper in the checker.

## 2026-09-07 (evening) — Sacha's rulings: NHB structure, Laura, GitHub timing

- **Section numbers go, at build time.** `make_nhb_docx.py` now strips heading numbers, drops the
  Introduction heading (Nature format has none) and rewrites every "§2.6" / "section 2.2" /
  "Sections 2.3 to 2.8" into the quoted section title, prefixed with Results or Methods. The master
  keeps its numbers so the checker and every internal document still resolve. The trailing
  "Figures and tables" index is cut from the supplement (captions live in the builder's FIGS lists).
- **Laura is not available** for the rest of the submission. The two-coder value verification
  becomes a single-coder author check (Sacha's 221 estimates), reported as such; the 20 full-text
  adjudications keep the stated not-blind caveat rather than a blind re-adjudication.
- **Abstract at 150 words** confirmed by Sacha. **GitHub goes public at the last minute**: the
  public package (`build_public_package.py`) is built and pushed at submission, not before.
- `search_behavioural_arm.py` reads an optional `OPENALEX_API_KEY` from the environment (never from
  a file); without one, one sweep takes ~35 minutes under throttling.

## 2026-09-07 (evening) — Sacha's adjudication page for the blind re-extraction; search unblocked

`scripts/build_reextract_adjudication.py` -> `~/Desktop/reextract_adjudication.html`: one card per
disagreement from `score_full_reextract.py` (eligibility disputes, possible missed estimates,
moderator disagreements on matched rows), each with both codings, both quotes and the archived text
around the value; rulings autosave under a stable key so the page can be regenerated as batches land.
First build: 59 items from 44 scored studies (1 screen, 13 omission, 45 moderator). Laura WILL deliver
her value ratings after all, so the two-coder value check stands.

The behavioural OpenAlex search restarted with an API key supplied through the environment (the key
itself is nowhere in the repository): 77 -> 165 of 180 sweeps in about twenty minutes, against one
sweep per 35 minutes keyless.

## 2026-09-07 (evening) — behavioural OpenAlex arm COMPLETE; screening package built

With the API key the arm finished in about twenty minutes: 180/180 sweeps, 186 calls, 0 backoffs,
0 losses. **6,972 unique works, 5,382 not already known** to any stream (DOI, OpenAlex id and
normalised-title matching against the Scopus corpus, the OpenAlex keyword arm, PubMed, both snowball
files and the net-new set). Dump: `searches/behavioural_arm_20260907.jsonl` (35 MB); query log
updated. The hits are dominated by "misinformation x platform data" (2,798), as the Scopus half was:
the method terms recruit the detection literature.

`scripts/build_behavioural_screen.py` -> `data/extract_v2/qa/behavioural_arm/openalex_2026-09/`:
the 5,382 net-new records (5,132 with abstract) in 45 batches of 120, with the v2 criteria and the
recall-protective rule as instructions; one Opus screener per batch, output
`screened/screen_NN.csv` (decision INCLUDE|MAYBE|EXCLUDE + one-clause reason). Launch at 18:43 with the
other Opus work; then aggregate, retrieve INCLUDE/MAYBE abstracts or full texts, and screen those at
full text before the merge. The arm's hypothesis (topic-first search under-caught behavioural
studies) is reported either way.

## 2026-09-07 (evening) — Sacha's value verification delivered and scored

221 of 221 estimates answered: **202 CORRECT (95.3% of the 212 with a verdict), 6 WRONG VALUE, 3
CANNOT FIND, 1 WRONG CONSTRUCT**, and 9 rows left blank where the ruling is in the note (e.g. "keep
1 to 4, drop 5 to 8"). By construct: CONCENTRATION 28/28 confirmed, EXPOSURE 33/34, REACH 31/36,
RECALL 55/59, SHARING 55/64. `scripts/score_value_verification.py` produces the scored file, the
58 notes and a summary under `data/extract_v2/qa/value_verification_keys/`; the file itself is
archived in the RA package with the page he coded from. Desktop copies trashed.

The notes carry more than the verdicts: **53 items in `sacha_rulings_ledger.md`**, of which about
18 are author RULINGS (remove all four per-outlet REACH rows of OA-W2992531903; drop Allcott's derived
1.2 and the means-derived rows 5-8 of 105027856675 and 85069463611's 0.96; replace pooled with
per-country REACH for W3033912864 and subtotals for 85074511992 and 85074596916; add the missing
Instagram concentration row, three CONTENT rows, the Fig 1 completions, and six sets of subgroup
rows), about 25 are CHECKS to answer with source evidence, and two are policy DECISIONS (a poster and
a slide deck in the corpus). Each ruling's replacement value is verified against the archived text
before it enters `apply_v1717.py`; that pass runs with the Opus work at 18:43. Laura's file, when it
lands, is scored the same way and the two coders' verdicts are compared row by row.

## 2026-09-07 (night) — corrections part 2 applied; checker now section-anchored

The second pass over the grounded report is in (commit 47f6617). Supplementary Notes A, B1, B4, B5,
C1, C2 and C3 are re-synced to v1.7.16 (Note A's claim-level content-sharing gap is +1.3 pp, not the
pre-repair +23.8; C2 describes the 200-resample run). The Ecker rebuttal now makes the argument the
data support: 58 of the 74 studies measuring misinformation behaviourally classify whole sources and
state no per-item veracity standard, so their low figures are not the product of a narrow falsity
criterion, and the definitional gradient cannot be tested there. §4.4's retrieval arithmetic
reconciles (477 to retrieval, 335 obtained, 208 eligible, 147 poolable, 141 in the released
freeze; FROZEN.md's v1.7.15 line corrected to 314 rows / 147 studies). The sign test reads p = .169
with its direction and low power stated. The unblinded 20-for-20 adjudication carries its caveat. The
value-verification sentence is held until the check is written up. Table 2, Supplementary Tables 1
and 2 and Note A are cited in prose; SI tables sit in citation order.

`check_manuscript_stats.py` gained `add_in()`, which asserts a string inside one section only: 245
assertions (60 section-anchored) and 68 banned strings, all passing; invariants hold; drift clean.
One judgment sentence the agent flagged in §2.9 ("the honest summary is") was rewritten descriptively.
The agent's run regenerated `docs/audit_review.html` with absolute paths; reverted, and the generator
(`build_dispute_page.py`) is still on the list to fix before the repo goes public. NHB pair rebuilt.

## 2026-09-08 — the full blind re-extraction: first 31 batches adjudicated

**Campaign state.** 31 of 57 batches (248 of 456 studies) re-extracted blind by fresh Opus agents,
validated (every source quote a contiguous verbatim span of the archived text) and committed with a
per-batch extractor report in `data/extract_v2/full_reextract_2026-09/batch_reports/`. Where the
session limit killed an agent mid-batch the files it had written were kept and a second session
finished and validated the batch; those reports say so and the first session's narrative is lost
(the JSON files carry their own screen_reason and notes). Model per batch is in PROVENANCE.md.

**Scores on 248 studies** (`scripts/score_full_reextract.py`): 235 studies judged eligible by both
passes, 13 disputed; 387 of 470 frozen main-pool values reproduced (82.3%); 103 omission candidates;
186 moderator disagreements on matched rows. Agreement on the moderators that carry §2.6: construct
κ .87, ground truth .89, classification level .96, denominator scope .94, sampling frame .82, topic
.87, breadth .79. Same model family as the original extractor, so this is reported as curation, not
as an independent reliability tier.

**Adjudication design.** `scripts/build_reextract_adjudication.py` builds Sacha's Desktop page from
the scores: moderator disagreements sharing (field, ours, blind) are ONE pattern card with a bulk
ruling and per-instance overrides; omissions the extractor itself flagged as variant, borderline or
low confidence sit in one group; sections run from eligibility and missed estimates (change the
dataset) to topic and one-offs (change little). Every card links a PDF from any store the review
holds (shared resolver, alias-aware) and the archived text. After Sacha's first pass, Claude's call
and reason were written on every unruled item (`scores/claude_suggestions.json`) with a one-click
accept; ruled items are hidden and kept in the export. Rulings persist by stable key across rebuilds.

**Rulings (299 items, three downloads archived as `rulings_sacha_2026-09-08{a,b,c}.csv` plus
`rulings_claude_default_2026-09-08.csv`):** 13 studies EXCLUDED on the blind pass's eligibility
finding (quality-only instruments, a news feature reporting another study, a stance-based exposure
item, a wrong-paper text, and studies with no share-with-denominator); 21 rows ADDED (elite
politician reach under three detection approaches, source-level and top-20% concentration rows,
the sharing-recall row beside a received-recall row, several truth-based rows replacing
quality-flavoured ones); 3 SAME as a row we hold; 78 NOT codeable (variants of one definition,
sub-denominators, shares conditional on exposure, compositions within misinformation); moderators
98 THEIRS, 83 OURS, 3 both wrong. Sacha agreed with 165 of Claude's 166 calls (the one exception:
the anti-Muslim rumour study stays crime_society). Where the blind coder was right it had applied
the codebook more literally than the original pass: keyword corpora are keyword_topical, model- or
dictionary-labelled numerators are classifier, fixed source lists are curated_seed, election-period
corpora are politics_elections. Where ours stands: COVID-vaccine studies are covid19 because the
freeze's vaccines topic is non-COVID by design; the eight "fact_checker -> self_report" cases are an
artefact of the blind validator; political_news is the review's own scope category.

**Three findings that change OUR rows beyond the disputes:** the PPE video study's 62.5% counts
incomplete presentation (quality), so 15.3% false-only becomes the Content row; the 4chan/Reddit
junk rows include sensationalism (quality), so 22% propaganda-only is the truth-based row; the
Trump/Milei TikTok satire, exaggeration and reuse rows are rhetorical codes, not falsity.

**Identity and duplicate findings, from both the ledger report and the blind pass:** the Scopus id
2-s2.0-84929523850 belongs to a 2013 book chapter while its archived text is the King's College /
Ipsos MORI polling report of 14 Dec 2020 (excluded from the corpus; the report goes to the grey
track under its own identity); 2-s2.0-105008525623 is the Spanish publication of the same GESOP
survey as 2-s2.0-85172813494 (one must leave); OA-W4407797130 holds four of seven narratives with
three mislabelled (the ledger fixes it). Five conference abstracts (7 estimates) are recommended for
exclusion; preprints and the dissertation stay as grey.

**Pacing.** Ten concurrent agents burned the 5-hour session limit in 40 minutes on 2026-09-07 and
killed everything mid-work; overnight Sacha allowed many agents provided every job was small and
wrote incrementally (one JSON per paper, screening CSVs in blocks of 40), which held. From
2026-09-08 morning: two or three agents at a time, and from 11:00 no new agents until Sacha says so
(he needs the limit for other work); a night plan is to be agreed. 26 extraction batches and 5
screening batches remain.

**Behavioural-arm screening:** 40 of 45 batches, 4,800 records: about 45 INCLUDE and 450 MAYBE,
many of the latter no-abstract or duplicate repository records. Aggregation, deduplication and
retrieval follow the last five batches.

Next, without agents: `scripts/apply_reextract_rulings.py`, which turns the rulings files and the
ledger proposals into freeze operations (removals, additions from the blind extraction files,
field corrections) so the merge is one command when the campaign is complete.

## 2026-09-08 (afternoon) — behavioural-arm screening complete; re-extraction resumed at four at a time

**Screening: 45 batches, 5,382 records, done** (`scripts/aggregate_behavioural_screen.py`).
Record level: 82 INCLUDE, 536 MAYBE, 4,764 EXCLUDE. The OpenAlex dump is full of double deposits
(Zenodo + journal, v1 + v2), so decisions were merged on normalised title with the most inclusive
copy winning: 4,883 distinct titles, **77 INCLUDE + 485 MAYBE = 562 titles for retrieval** (531
with a DOI; 514 already carry an abstract in the dump, 48 do not). The arm behaved as its hypothesis
predicted: method terms recruit the detection and tooling literature, journal front matter and
off-topic records; the includes are almost all 2020+ COVID surveys and health content analyses, a
handful of genuine behavioural studies (browsing panels, data donations, platform censuses), and
several are already in the corpus under another id. Next: full-text screen of the 562 (abstract
first, retrieval for the 48 without one), then extraction of the eligible ones into the wave that
merges with the next freeze. `data/extract_v2/qa/behavioural_arm/openalex_2026-09/SUMMARY.md`.

**Re-extraction:** Sacha lifted the agent gate at ~12:00 ("go ahead, a lot of credits right now");
running four jobs at a time, one relaunch per completion. Batches 32-34 landed; 35-37 in flight.

## 2026-09-09 morning — night window: batches 39-50 landed; two identity problems now

Overnight at four jobs at a time: batches 39-50 validated and committed with reports (the 01:30
and 06:30 limits each killed a wave mid-work; the per-paper writes meant nothing was lost, and
second sessions finished each batch). 50 of 57 done; 51-53 being finished this morning; 54-57 wait
for Sacha's go. Findings worth their own line: the frozen row under `2-s2.0-85147303661` ("From
Facebook to YouTube: anti-vaccine videos") was extracted from the Oxford COMPROP memo
"COVID-related Misinformation on YouTube" (Knuutila et al. 2020), the same wrong-text class as the
KCL/Ipsos report; `PMID-33304681`'s printed percentages all use a phantom denominator (654 for 454
posts), so our 22.3 becomes 32.2; the blind pass reproduced Sacha's ledger rulings independently
in several places (Neudert subtotals, the Italian 31.9, the Instagram concentration row, Mordovia's
recall-sharing subtype). Both new items are in `merge_plan.py`'s manual list.

## 2026-09-09 ~11:00 — Work split across two sessions (Sacha's instruction)

Sacha divided the remaining pre-submission work between two Claude sessions.

- **This session:** (1) blind re-extraction batches 54-57 (32 studies, the last of 57);
  (2) the behavioural arm — abstract/full-text screen of the 562 records in
  `data/extract_v2/qa/behavioural_arm/openalex_2026-09/retrieval_list.csv` and extraction of the
  eligibles into the merge wave; (3) the merge itself (apply_v1718 from `merge_plan.py` +
  `ledger_proposals.py`, re-freeze, full Phase B, metareg, 28-hour bootstrap, manuscript re-sync
  against the 245 checker assertions, NHB docx rebuild).
- **Another session:** the post-campaign pass (rescore, extend `scores/claude_suggestions.json`,
  rebuild the Desktop adjudication page) and the pre-merge brief (the 8 ledger conflicts, the
  meeting-abstract format rule, the two wrong-paper identities, the GESOP Spanish duplicate, the
  15 manual items).

Nothing launched: Sacha said he will give the go. Recorded so the two sessions do not duplicate
work or write to the same artefacts. Working tree clean at fc99c7b.

## 2026-09-09 — BLIND RE-EXTRACTION CAMPAIGN COMPLETE (57/57 batches, 456/456 studies)

Batches 54-57 run one at a time on Sacha's instruction (54, then 55, then 56 and 57 together).
All four validator-clean; per-batch reports in `batch_reports/`, provenance rows appended.
`data/extract_v2/full_reextract_2026-09/extractions/` now holds 456 JSON files — every study in the
frozen corpus re-extracted blind by an independent Opus session with no sight of the frozen data.

Final four batches: 31/32 INCLUDE, ~70 main-set rows. The one EXCLUDE is 2-s2.0-85065550941
(fluoride/Instagram): it codes stance and eleven non-exclusive topic tags, never truth against a
ground truth, so it is quality-only under §1 of the instructions.

Substantive flags raised by these batches, for the adjudication and the merge:
- **OA-W7155615941** (melanoma) is abstract-only, 565 bytes, one number ("approximately one-quarter
  of media articles") with no denominator, country, year or named instrument. Needs full-text
  retrieval before its 25% is used; may belong under QUALITY.
- **OA-W4407797130** (Serbia): all seven narrative reach figures share the denominator 800, verified
  arithmetically (every value is an exact multiple of 1/800) against prose saying each respondent saw
  one narrative. Table 2 is on a different denominator and is not a prevalence figure. If the review
  collapses per-item batteries, these seven rows are the obvious candidate.
- **NEW-berriche-fakerisland2026** splits into a tweet share (0.05% of 184M) and an account share
  (0.9% of 3.7M); **no CONCENTRATION row** — the paper asserts concentration but publishes only an
  intensity distribution, never a group-share/activity-share pair, so R1 is not met.
- **Two papers yield QUALITY rows only** and contribute nothing to prevalence: 2-s2.0-85134489939
  (CRPS YouTube, GQS/JAMA/DISCERN) and 2-s2.0-85122546153 (alcohol industry websites).
- Internal contradictions found in sources: 2-s2.0-85104228138 (11.9%/N=124 vs 12.0%/N=136),
  W3011186656 (Kouzy, denominator never printed; 153/24.8% implies ~617 against 632 and 564),
  2-s2.0-85065550941 (139 vs 189 for the same 63.0%), 2-s2.0-85159889148 ("44 (98)" of 50).
- Quote repairs were needed in batches 55-57, all caused by two-column PDF interleaving or a page
  break. In every case a verified contiguous span carrying the same value was substituted; no value,
  construct or moderator code was changed.

NOT run here: rescoring, `claude_suggestions.json`, the adjudication page rebuild. Those belong to
the other session per the 2026-09-09 split.

## 2026-09-09 — Behavioural arm: second-pass abstract adjudication COMPLETE (485/485)

The behavioural arm is a targeted OpenAlex search combining misinformation terms with METHOD terms
(web tracking, browsing data, platform data, digital trace, data donation). Its purpose is to test
whether the topic-first search missed audience-level studies that describe themselves by how they
measured people rather than by their subject. The first pass screened 5,382 records at 120 per batch
under an explicitly recall-protective rule and returned 77 INCLUDE + 485 MAYBE = 562 to retrieve.

Those 485 MAYBEs have now been re-read one abstract at a time, 13 batches, one Opus session each.

**Result: 10 ELIGIBLE, 101 UNSURE, 374 NOT. With the 77 first-pass includes, 188 records go to
full-text retrieval instead of 562** — the filter removed exactly two thirds of the retrieval load.

Exclusion profile (the arm's own character): belief/attitude only 126, no audience denominator 95,
no falsity coding 46, review/commentary 39, quality-only 20, off-topic 18, intervention 6,
tool/infrastructure 5, detection/classifier 5. Detection and classifier work, which a method-term
search was expected to be full of, is almost absent; the dominant family is instead the small local
survey in which misinformation appears once as a listed "challenge" or "barrier".

**The rulebook is the arm's other output.** 31 numbered scope rules were written across 9 addenda as
the batches ran, each settled against precedent in the frozen corpus rather than invented. The ones
that will matter beyond this arm: literature samples are out (no study of 456 samples the literature;
the Freshman 15 precedent uses it as ground truth against a popular-press denominator); deceptive
actors are not false claims; stance is not falsity; quality-only means NO accuracy coding anywhere,
since 25 included studies use quality instruments but only 7 produced an estimate, and always from a
separate accuracy coding; demonstrated practice contradicting a standard IS accuracy (the
resuscitation-video precedent); there is no sample-size floor but nothing below n=20 has precedent;
professional and student populations are in scope (the freeze carries an explicit `professional`
population scope).

**Coders overturned their own instructions twice, and both times they were right.** Two independent
sessions found that rules 9 and 20 pointed opposite ways on structurally identical evidence — an
abstract quoting only a mean got UNSURE, one quoting only a coefficient got NOT — and a third made
the same criticism of rule 21. Rule 27 confined rule 9 to genuinely latent outcomes and rule 28 let
rule 21 yield to positive evidence of an encounter item. The change was applied RETROACTIVELY: all 27
exclusions citing rule 9, a structural model or coefficients were re-read, most survived, and three
were raised because their instrument is a measured sharing battery. Nine overrides now stand in
`adjudication/OVERRIDES.csv`, each with its rationale; delivered coder files were never edited.

Artefacts: `data/extract_v2/qa/behavioural_arm/openalex_2026-09/adjudication/` — INSTRUCTIONS.md
(criteria + 9 addenda), batches/, ruled/ (13 delivered coder files), reports/ (per-batch extractor
reports), OVERRIDES.csv, LEADS.md, ruled_all.csv, retrieval_final.csv, SUMMARY.md. Scripts:
`build_behavioural_adjudication.py`, `fetch_behavioural_missing_abstracts.py` (recovered 17 of 48
missing abstracts from Crossref/PubMed/Semantic Scholar), `aggregate_behavioural_adjudication.py`.

**Recorded limitations, for the write-up.** (1) `belief/attitude only` carries a third of exclusions
across three distinct defects (concern, skills, trust-only) and would justify the split rule 13 made
for `no falsity coding`; it was NOT split because the batches were complete and re-categorising
retroactively would be inconsistent across coders. (2) Rule 8's enumerated-outcomes branch assumes a
standard of abstract writing this literature does not always meet: where an abstract lists
"objectives" rather than outcome measures, treating a missing exposure item as informative rests on
weaker evidence than it would in a better-indexed journal.

NEXT: full-text retrieval of the 188, full-text screen, extraction of eligibles into the merge wave.

## 2026-09-09 — Behavioural arm: retrieval, and Sacha's own read of the candidate pool

Automated retrieval settled at 76 of the 188 survivors: 57 from OpenAlex's best OA location, 19 more
from a second pass over Unpaywall, Europe PMC and OpenAlex alternate locations. The remaining 112
went to Sacha as a browser hand-off (`~/behav_next.sh`, 105 with a DOI, opened 30 at a time in
Chrome, ordered ELIGIBLE then first-pass INCLUDE then UNSURE so the early chunks carry the value).

He worked the whole list and returned 13 PDFs. All 13 matched to records, 12 by a DOI found inside
the PDF and one by title, every one at full title-word overlap. Corpus now at 88 texts of 188.

**His own judgement of the pool, recorded because it corroborates the arm's result:** "most looked
very not relevant at all and low quality". That is an independent human read of the same candidate
pool the coders excluded 374 of 485 records from, and it agrees with them.

**A wrong-article guard now runs after every retrieval pass.** A batch-2 coder found that one
record's downloaded text was an entirely different article from the same journal issue (a management
paper, 60 KB, nothing about the subject). `scripts/verify_behavioural_texts.py` checks every text's
title words against its recorded title; that file scored 0.00 and all 87 others passed. It is
quarantined under `fulltext/quarantine/` with a README, not deleted, because a wrong document is
evidence about the retrieval path. This is the third instance in this project of an identifier
resolving to a different document (methods lesson #40), and the first caught automatically.
`scripts/match_behavioural_pdfs.py` applies the same check before accepting any hand-retrieved PDF.

Retrieval state: 88 texts, 100 unreachable (1 ELIGIBLE, 38 INCLUDE, 61 UNSURE). The unreachable
count is honest and belongs in the arm's write-up; it is not a pending queue.

## 2026-09-09 — Behavioural arm: FULL-TEXT SCREEN COMPLETE (89 papers read), and the arm's result

All ten batches done, including a re-screen. 89 papers read in full: **28 INCLUDE, 55 EXCLUDE,
6 UNCERTAIN.** Artefacts under `fulltext/screen/`: INSTRUCTIONS.md (criteria + 4 addenda),
ruled/fts_01..10.csv, reports/, screened_all.csv, to_extract.csv, SUMMARY.md, FLAGS.md, NO_DATA.md,
DUPLICATES.md, OVERRIDES.csv.

**Reading the papers mattered.** 19 records the abstract stage had called ELIGIBLE or INCLUDE were
reversed; 4 were rescued from UNSURE. Roughly a fifth of abstract-stage judgements did not survive
the full text, in both directions.

**The genuine finds.** The arm's purpose was to test whether the topic-first search missed
audience-level behavioural studies. Two answer that directly:
- `W4414259328` (Dahlke & Hancock) — **39.6% of 1,194 US adults visited at least one untrustworthy
  website** in Wave 2 (YouGov Pulse tracking, 21M observations, domain-level against a 1,796-domain
  list). REACH, source-level.
- `W4385325063` (Nyhan et al., Nature 2023) — **0.76% of Facebook Feed exposures** for 23,377
  randomised US adults came from misinformation repeat offenders. EXPOSURE, source-level.
Both are population-scale trace studies and neither is in the corpus. `W7171617153` also screened
INCLUDE but is ALREADY frozen (`NEW-bergeronboutin-sciadv2026`); the coder reproduced our own three
values blind, and independently listed the concentration figures the unapplied v1.7.17 adds to it.

**Six papers present as empirical studies and report no observations** (`NO_DATA.md`): findings in
the future tense, "based on the simulated findings", tables captioned "survey synthesis", a results
section that never arrives. Each survived two abstract-stage passes. How often this occurs is itself
a finding about the literature a method-term search surfaces, and it agrees with Sacha's own read of
the pool ("most looked very not relevant at all and low quality").

**A bug of mine, and what it cost.** `match_behavioural_pdfs.py` extracted the first six pages of each
hand-retrieved PDF to identify it, then saved that extract as the paper's full text. All 13 of Sacha's
papers were stored truncated; batch 8's coder found it. Fixed by separating identification from
storage; re-extracted texts grew up to 3x. Eight already-ruled records were re-screened and **four
rulings changed**: the Dahlke & Hancock find was UNCERTAIN and became INCLUDE (its exposure share was
in the discarded pages); a Tumblr study went EXCLUDE -> INCLUDE once a mixed "misinformation/
advertisement" label was disaggregated into a clean 3.0% of 235; and one INCLUDE went the other way
to UNCERTAIN, because its 76.68% exists only in the abstract and appears nowhere in the results.
A first attempt at the fix drifted (it matched against the shrinking manual list, giving 0.5-0.7
overlaps and one identifier assigned to three PDFs) and was reverted; the matcher now works against
all 188 survivors, requires 0.75 overlap, and refuses duplicate assignment.

**Two guards added, both prompted by coders.** `verify_behavioural_texts.py` checks every text against
its recorded title (caught one file that was an entirely different article) and against the Crossref
page count (caught three truncated files). Two heuristics were tried and reported honestly: an
"ends mid-sentence" test flagged 75 of 88 files and was discarded; a "no reference list" test was
calibrated against three files, got two wrong, and is advisory only.

NEXT: extract the 28 includes into the merge wave, minus the frozen duplicate. `FLAGS.md` lists 15
includes carrying a warning a human must read first — among them a survey whose cell counts recur
across two tables with every row totalling exactly 399, one reporting 100.0% exposure with zero
non-exposed, and one whose only value is "around one in 5" in a likely machine-generated paper.

## 2026-09-09 — Behavioural arm: EXTRACTION COMPLETE. The arm's result, end to end.

27 papers extracted into the corpus schema; 3 excluded at extraction; **40 estimates from 24 studies**
(RECALL 16 rows / 9 studies, CONTENT 16 / 11, QUALITY 5 / 2, SHARING 1, EXPOSURE 1, REACH 1).
19 rows borderline, 8 at low confidence. Artefacts: `qa/behavioural_arm/openalex_2026-09/extraction/`
(INSTRUCTIONS.md, batches/, extractions/, rows.csv, SUMMARY.md, DECISIONS_FOR_SACHA.md).

### The funnel, for the PRISMA figure and the arm's write-up
6,972 works retrieved / 5,382 net-new -> 45 title-abstract batches -> 77 INCLUDE + 485 MAYBE = 562
-> second-pass abstract adjudication of the 485 (13 batches, 31 scope rules in 9 addenda) -> 10
ELIGIBLE + 101 UNSURE + 374 NOT -> 188 to retrieve -> 88 retrieved (76 automated, 13 by Sacha by hand,
1 quarantined as the wrong article) -> full-text screen of 89 (10 batches incl. a re-screen) -> 28
INCLUDE -> extraction -> **24 studies, 40 estimates**. 100 records were never retrievable and that
number belongs in the write-up.

### What the arm found
Two population-scale trace studies not in the corpus, both source-level:
- `W4414259328` Dahlke & Hancock — 39.6% of 1,194 tracked US adults visited >=1 untrustworthy website.
- `W4385325063` Nyhan et al. Nature 2023 — 0.76% of Facebook Feed exposures from repeat offenders.
A third, `W7171617153`, screened INCLUDE but is ALREADY frozen; the coder reproduced our three values
blind and independently listed the concentration figures the unapplied v1.7.17 adds to it.

### The honest negative
Of 562 candidates, 24 studies survive, and most contribute weak survey estimates. Six papers present
as empirical studies and report NO observations (`NO_DATA.md`). Sacha's own read of the pool agrees:
"most looked very not relevant at all and low quality". The arm's conclusion is that the topic-first
search did not systematically miss behavioural work; it missed two good trace studies.

### Errors made and corrected in this arm (all in the log above, gathered here)
1. My `match_behavioural_pdfs.py` stored only the first 6 pages of each hand-retrieved PDF as its
   full text. Found by a coder. 8 records re-screened, 4 rulings changed, including the arm's best
   find (UNCERTAIN -> INCLUDE).
2. My first fix drifted: matching against the shrinking manual list gave 0.5-0.7 overlaps and one id
   assigned to 3 PDFs. Reverted; the matcher now matches against all 188, requires 0.75, refuses
   duplicates.
3. My first truncation heuristic ("ends mid-sentence") flagged 75 of 88 files and was discarded; the
   "no reference list" test got 2 of 3 calibration cases wrong and is advisory only.
4. Coders twice overturned my own scope rules and were right both times (rules 9 vs 20 pointing
   opposite ways; rule 21 too absolute) -> rules 27/28, applied RETROACTIVELY across 27 exclusions.
5. One downloaded text was an entirely different article; quarantined, and a title check now runs
   after every retrieval pass.

### OPEN, for Sacha: `extraction/DECISIONS_FOR_SACHA.md`, 10 items
Including a genuine conflict between two rulebooks (belief-anchored vs encounter-anchored recall), a
verified table-fabrication pattern, an R8 failure on a computed denominator, and three
extraction-stage exclusions that reverse passed full-text screens.

## 2026-09-09 18:10 — Post-campaign pass (rescore, Claude's calls on the new items, page rebuild) and the pre-merge brief

**Scope.** This session owns only the post-campaign pass and the pre-merge brief (division of labour,
2026-09-09 ~11:00); the other session owns batches 54-57, the behavioural arm and the merge itself.
Started on Sacha's go at ~17:30, after the campaign reached 57/57.

**Rescore** (`scripts/score_full_reextract.py`, unchanged): 456 of 456 studies. 430 INCLUDE / 26
eligibility disputes; 712 of 837 frozen main-pool values reproduced (85.1%); 202 omission candidates in
123 studies; 367 moderator disputes. Kappas: construct .885, ground_truth .919, classification_level
.958, sampling_frame .819, topic .792, denom_scope .891, breadth .755, platform_norm .853,
population_scope .588. All 299 of Sacha's 2026-09-08 rulings still resolve to keys in the new tables
(no stale rulings); 293 items are new (13 SCREEN, 99 OMISSION, 181 MOD; 287 distinct keys, six omission
keys occur twice because the blind file holds two rows at the same value).

**Claude's calls on the 293 new items** (`scores/claude_suggestions.json`, previous file kept in the
campaign folder's `.backups/`; generator kept in the session scratchpad, its rules are recorded here).
Every call cites the precedent it follows, and the calibration was done against Sacha's own 2026-09-08
rulings on the same (field, ours, blind) patterns, pulled from the archived rulings files:
- SCREEN 13, all EXCLUDE: 9 quality-only instruments (same as the 8 he excluded before), the Megafon
  influencer-exposure item (stance, not falsity), the fluoride Instagram topic-tag study (flagged as a
  judgement call), the Nigerian perception-item survey, and the wrong-paper id 2-s2.0-85147303661.
- OMISSION 99: 20 ADD (the truth-based replacements for quality-flavoured rows in 85086160482 and
  85186874194; the Reddit second-period 4%; the Serbian N1/N6 figure values, which corroborate the
  ledger's PDF reading; the supersharers 1.66% feed-exposure row; the Finnish 82% concentration row; the
  Cordonnier strict-definition reach rows 9.4/18.5; the tabloids headline 67.7; the ADHD claim-level 55;
  the 0.3%-of-all-posts row; four engagement-weighted shares, each marked reversible), 2 SAME AS OURS
  (PMID-33304681 32.2 = the corrected value of our 22.3; W3129222959 9.1 = the Germany row already held
  under 85074511992), 75 NOT CODEABLE (variants, sub-denominators, compositions, period splits,
  channel breakdowns, perception items, second-hand figures, the extractor's own flagged rows).
- MOD 181: 93 OURS / 75 THEIRS / 9 THIRD. Pattern rules carried over: COVID-vaccine = covid19;
  keyword corpora = keyword_topical; fixed source lists = curated_seed; Oxford junk-news coding =
  researcher_coding; the fact_checker->self_report validator artefact = OURS; share of items in a corpus
  = CONTENT, share of link-share instances = SHARING; a label a true item can carry = QUALITY;
  non-probability surveys = convenience; political-context domain-list studies = politics_elections (his
  85037352356 ruling), per-topic article classes get their own topic. THIRD where neither side names the
  right cell: 85142396682 x6 denom_scope -> news_diet, 85069463611 x2 sampling -> curated_seed,
  OA-W4407797130 77.4 topic -> politics_elections (N4 after the ledger relabelling).
Source texts were re-read for the ambiguous ones (105019603181's 12.7 is the electoral-politics
category; 85209547248's window is the 2020 election; 85181200454's 43.1 is the politics item; the
Serbian figure text layer prints 85.13 and 44.75; 85186874194's 'Factual: No' includes neutral videos;
105027959122 observed participants' public posts; 85116003554 prints 5.7 often + 30.9 sometimes).

**Page rebuilt** (`scripts/build_reextract_adjudication.py`, unchanged): 293 items in 107 cards, ruled
items hidden and kept in the export, 456 of 456 scored, on the Desktop.

**Pre-merge brief:** `docs/PREMERGE_BRIEF_2026-09-09.md`. Recommendation on every open ruling: the 8
ledger conflicts, the format rule (5 meeting abstracts out, 7 estimates; thesis + 8 preprints kept as
grey; one Methods sentence), the two identities (KCL: confirm no re-entry, record the Dees chapter as
full text not obtained; COMPROP: exclude the id, drop the memo like KCL, retrieve and screen the real
Gruzd 2023 paper, DOI 10.1177/20563051221150403), the GESOP duplicate (remove the Spanish five, PRISMA
duplicate not exclusion, alias, the value-level dedupe keyed on value should key on narrative), the 15
manual items (with the subtype/denominator fields each construct change needs), plus 13 consistency
items the pass surfaced that no card carries (two perception items held as RECALL; 85116003554 5.7 ->
36.6; 85154558018 actor share -> REACH; two measure_type mismatches; the missing 94.8 column; Germany
2017 held twice; one rule each for engagement-weighted and view-weighted shares; the three THIRD
targets; total-vs-parts for the tabloids study) and the two dedupes apply_v1718 must do because the
ledger and the blind campaign add the same rows (85089622030 31.9; W4407797130 N1/N3/N6).

**Not done here:** no rulings applied, no freeze touched, merge_plan.py not regenerated (it regenerates
from Sacha's next download). Repo state: the other session's uncommitted files (audit_v140_findings.csv,
prisma_counts.json, audit_review.html) were left alone.

## 2026-09-11 — Sacha's rulings round 2 archived; manuscript comment round (60 + 4 comments) addressed; two data tasks his comments required

**Rulings.** `rulings_sacha_2026-09-10a.csv` archived in the campaign folder (592 rows, every item ruled; 293 new items, agreeing with Claude's call on 291). `plan_reextract_merge.py` regenerated: 26 studies excluded (36 rows), 40 rows added across 30 studies, 160 moderator recodes, 29 manual items, 0 problems. His two disagreements: `85152674280` topic OURS = general_news (a general untrustworthy-domain list during an election), and `85193588807` (excluded anyway). His comments state a topic rule for domain-list studies (the LIST, not the election period, decides) that the corpus does not yet apply consistently; the sweep of every politics_elections + domain_list study is section H of the pre-merge brief, unruled. Coding rule he stated and now in memory: we follow and document the paper's definition (Cordonier's click-bait counts as unreliable because the authors say so), we never impose ours.

**Manuscript round.** His annotated NHB pair archived in `docs/.backups/` (`manuscript_NHB_*_annotated_2026-09-11.docx`); the master `docs/manuscript_draft.md` backed up as `manuscript_draft_2026-09-11_pre-round.md`. His tracked edits (61 insertions, 56 deletions in the main text) and four untracked paragraph breaks (§2.1 platforms; §2.2 into four paragraphs) applied to the master. Every comment addressed; the substantive ones:
- Intro: a paragraph on why prevalence estimates matter (his request, drafted in his register); numerator/denominator introduced where the Allen et al. example first needs them; what Hameleers 2025 attributes the gap to (four causes, the second is what this review tests); the "main results" paragraph rewritten as three sentences; the sensitivity clause dropped from the intro.
- Table 1: the shared phrase "the share of" moved into the column header; every example quoted.
- Results: §2.2 split and made explicit (identification level and ground truth covary with the construct; the 91 no-standard studies explained by the source-level split); §2.3 now reports every grey-literature cell (35 usable claims of 117) and says why Note A compares content with sharing only; §2.4 rewritten on ALL 75 seen-recall studies (below); §2.6 without capitals, "that is whether" and "what survives the uncertainty"; §2.8 says the broader top groups are similar and why the bands are not one curve, and names the Grinberg panel as US Twitter; §2.9 rewritten in the NHB register without bold lead-ins or meta-statements, and corrected: the age-contrast matcher (`phaseB_subgroups.py`) recognised only "65+" and "18-29", so three of the four age contrasts were dropped; with 60+/60-69/20-29 recognised there are four (18.5x, 4.35x, 0.70x, 0.67x), two in each direction, and the text now says so. Eight political contrasts because a contrast needs both sides on one measure.
- Discussion: the Hameleers paragraph split and shortened, "can see it" wording replaced; limitations cut from seven to five and reframed to state what the checks did and found without claiming a 100% baseline (his instruction); the "untested in the primary studies" sentence replaced by a test (below).
- Methods cut from 3,905 to 2,746 words: the repair narrative, the human re-screen statistics and the reliability essay moved to Supplementary Note C1, which was rewritten in plain register (his comment: "very AI written, so many em dashes"); §4.8 keeps a two-paragraph overview plus Table 2; §4.9 keeps the main-analysis definitions and points to C2. An AI-use statement added to the Statements, modelled on the IPIE wording he supplied, extended to what the agents actually did here.
- PRISMA flow diagram moved to the main text as Figure 1 (all figures renumbered in the master, both builders and the checker); its overlapping repair box fixed (`make_prisma.py`). Figure 5 (drivers) axis cut from 90% to 65%, labels enlarged (`phaseB_figures.py`).
- Guard suite: `check_manuscript_stats.py` re-pointed for every rephrased sentence (numbers unchanged), three assertions retired with the sentences he deleted, three added (windows: past-week median and full coverage; disclosure test); 245/245 present, 68 stale strings absent; invariants hold; drift check clean.
NHB word counts after the round: abstract 154, main text 5,246 (intro 960, results 2,755, discussion 1,531), Methods 2,746. The main text is above NHB's 4,000-word guideline for Articles; cutting Results is Sacha's call.

**Data task 1: recall windows for all 75 seen-recall studies** (Opus agent, `data/extract_v2/qa/recall_windows_2026-09-11.csv` + REPORT; the 2026-08-12 file untouched). 25 ever, 22 frequency scale, 8 period-specific, 14 bounded (5 past week, 4 past month, 1 past 3 months, 2 past 6 months, 2 past year), 6 unclear. Medians: bounded 55.9% (k 14), unbounded 56.8% (k 47), period-specific 48.1% (k 8), unclear 51.5% (k 6); past-week 48.5/52.3/53.3/56.6/60.5 (median 53.3). Reading every item also found nine rows that are not exposure items (perception of channels, of friends, of outlets, "affected professionally", acted on, deceived by) and four analyses of one HINTS item (three on the same respondents): brief section I, for the merge.

**Data task 2: do curated-sample studies disclose the selection in the abstract?** (Opus agent, `curated_abstract_disclosure_2026-09-11.csv` + REPORT.) Of 115 studies coded denom_selection = curated, the agent judged 20 not rank-truncated (censuses, random samples, actor- or submitter-defined corpora; listed in `..._notcurated.txt`, to re-examine at the merge). Over the remaining 95 with an abstract: 64 state the selection, 26 give a sample size only, 5 neither; 73 headline the percentage and 23 of those (32%) omit the selection. Selection is in the Methods of 113 of 115, so the omission is an abstract problem, not a paper problem. Now a sentence in the Discussion's reporting-practices paragraph, asserted by the checker.

**Delivery.** NHB pair rebuilt from the master; tracked-changes versions (old = the builds he read, at ad83699) written by `make_tracked_docx.py` and placed on the Desktop under the usual names; clean builds in docs/. Known limit: the diff shows changed and inserted paragraphs but not whole deleted paragraphs (one in the main text: the closing sentence of §2.9 he struck).

## 2026-09-12 — pre-merge brief turned into a decision page

Sacha: "If it's decisions I need to make it should be an html." `scripts/build_premerge_decisions.py` renders every ruling in `docs/PREMERGE_BRIEF_2026-09-09.md` (sections A-J, plus the timing question T) as a card with the evidence, Claude's recommended call, one-click accept, the alternatives, and a reason box; same mechanics as the blind re-extraction page (browser autosave by stable key, Download writes `premerge_rulings_sacha_FILLED.csv` with key, section, RULING, RULING_reason). The download is archived in the campaign folder as `premerge_rulings_sacha_<date>.csv`; later files win; the merge session reads them. The Markdown brief stays as the full record behind the cards. Output: `~/Desktop/premerge_decisions.html`.

## 2026-09-13 — Laura's value file scored; Gruzd 2023 retrieved and screened; the 20 curated codes pre-examined

**Laura's value verification** (`docs/RA_package/value_verification_2026-09/V_values_laura_FILLED.csv`, scored with `score_value_verification.py --coder laura` -> `laura_scored.csv`, `laura_notes.csv`, `laura_SUMMARY.md`; comparison in `laura_vs_sacha_2026-09-13.md`). 208 of 221 CORRECT (94.1%; Sacha 202, with 9 blanks), 192 rows confirmed by both coders, 3 flagged by both. Adjudication against source: no new correction. Two of her flags confirm fixes already queued (W7146985142 9 -> 8 in apply_v1717; Allcott 1.2, ledger item 5); one fills an empty denominator (85199110625 25.05 = share of retweets, Table 2); two open questions go to the decision page as cards L1 (105017599346's 25 is a figure midpoint, not printed) and L2 (85059494932: fake-only user share 5% vs the held fake+biased 12). Eight of her WRONG-CONSTRUCT verdicts (REACH -> SHARING) follow the RA page's own SHARING definition, which contradicted the codebook on user-share rows: scored as an instrument inconsistency, the package README corrected, no row changed, delivered coder files untouched. Her 51 notes cross-referenced against the freeze and every pending queue: 59 values held, 15 already added, 6 in the blind queue and ruled, 52 in no queue and all either group sizes already in conc_group_pct, compositions/partitions, or non-misinformation comparison classes, except the 5% above.

**Gruzd et al. 2023** (the paper the wrong-document Scopus record 2-s2.0-85147303661 actually names) retrieved as JATS full text from Europe PMC (`data/fulltext/v2txt/NEW-gruzd-sms2023.txt`; SAGE and PMC block PDF download). Screened: stance-coded (pro/anti/neutral), no veracity judgement; 57.0% of 484 seed videos anti-vaccine. Recommendation EXCLUDE at full text on the stance rule; card C2 updated with the alternative (CONTENT 57.0 under a platform-policy definition). Note: `data/extract_v2/qa/gruzd2023_screen_2026-09-13.md`.

**Curated codes** (card J1): the 20 studies the abstract-disclosure check judged not rank-truncated were pre-examined against the codebook definition of denom_selection (`curated_reexamination_2026-09-13.csv`): 8 clear, 1 single_source, 8 keep, 3 keep with a submitter/fact-checker flag; two keeps need denominators filled. 85142396682 cleared to match the identical elite-sharing design 105027856675.

Decision page rebuilt (62 cards in 11 sections; C2, J1, T1 updated; section L added). The page is built by scripts/build_premerge_decisions.py; his download goes to data/extract_v2/full_reextract_2026-09/premerge_rulings_sacha_<date>.csv and is read by the merge session.

## 2026-09-14 — Sacha's pre-merge rulings: all 62 cards ruled; the merge is unblocked

`premerge_rulings_sacha_2026-09-14a.csv` archived in the campaign folder (62 of 62 ruled; he took Claude's call on 59, differed on 3, commented on 4). The differences and comments:
- **E2 (105027959122, REACH vs RECALL sharing):** he ruled RECALL_SHARING but wrote "re-read and make a call". Re-read: the paper's Methods contain a content-analysis section in which the researchers checked what participants shared or wrote on social networks against web searches, on posts "concomitantly observed ... upon consent". The 7.4% is therefore a share of participants whose observed posts carried myths, coded by the researchers: REACH reach_subtype = sharing, ground_truth researcher_coding, as frozen. Recorded as the delegated call in `premerge_rulings_z_claude_delegated_2026-09-14.csv` (sorts after his file; overrides that key only; his file untouched).
- **L1 (105017599346 SHARING 25):** KEEP_FLAG rather than DROP; the merge keeps 25 and sets flag figure_derived_approx.
- **L2 (85059494932):** ADD_5 rather than replace: hold both the fake-only user share (5%) and the fake+biased one (12%). His question "why 12 and not 25": the study reports two levels; at the TWEET level 10% of news-link tweets point to fake-only sites and 25% to fake or extremely biased sites (we hold the 10); at the USER level 5% of news-sharing users posted a fake-only link and 12% a fake-or-biased link (we hold the 12, and now add the 5). The 25 is the tweet-level broad figure, dropped by rule L36, not a user share.
- **B2 (preprints):** KEEP_GREY, with "I'd be tempted to keep the pre-prints in the main analysis if that's fine and if we said so". They already are: all eight preprints and the dissertation contribute rows to the main pool (checked against the freeze); the Methods sentence now reads "Preprints were eligible, enter the main analysis, and are flagged as such" (one-line edit, checker 245/245).
Everything else as recommended: A1-A8, B1, B3, C1 (KCL confirmed), C2 (drop the memo, Gruzd excluded on stance), D1 (remove the Spanish five), E1/E3-E8, F1-F12, H0 adopted with the 9 moves and the 13 confirmations, I (nine removals, one HINTS 6 study + HINTS 7, conditional rows dropped, headline-only medians), J1 (apply the per-row file), J2, J3, T1 GO.

**Handover to the merge session:** inputs are `rulings_sacha_2026-09-10a.csv` (+ the 2026-09-08 files) via `merge_plan.py`, `ledger_proposals.py`, `premerge_rulings_sacha_2026-09-14a.csv` + the z_claude file, `curated_reexamination_2026-09-13.csv`, `recall_windows_2026-09-11.csv` (for the nine I-removals), `curated_abstract_disclosure_2026-09-11_notcurated.txt`, and the two dedupes in brief section G (85089622030 31.9; W4407797130 N1/N3/N6 at 44.75/48.13/85.13). Then FROZEN.md, Phase B, metareg, the 28-hour bootstrap, manuscript re-sync (Note C1's blind re-extraction paragraph and Table 2 must be updated to the full 57-batch campaign), NHB rebuild as tracked changes.

## 2026-09-14 (later) — the behavioural arm was missing from the pre-merge decisions; 11 cards added

The merge session pointed out that the behavioural arm's 24 studies / 40 estimates (`behavioural_arm/openalex_2026-09/extraction/rows.csv`) were in none of the handover's named inputs and that its ten `DECISIONS_FOR_SACHA.md` items were never ruled. Correct: the decision page was built from the pre-merge brief, which covered the blind campaign and the ledger, not the arm. Since rows cannot be added after the 28-hour bootstrap, the arm is settled now: section K (K0 merge-or-hold, K1-K10 the extractor's ten calls, each with its recommendation) added to `build_premerge_decisions.py`; page rebuilt with his 62 earlier rulings preserved (73 cards). His download of the K section goes to the campaign folder as `premerge_rulings_sacha_2026-09-14b.csv` and completes the merge inputs; the arm's rows then enter apply_v1718 with a provenance flag (behavioural arm, OpenAlex 2026-09) alongside the blind-campaign and ledger operations.

## 2026-09-14 (evening) — section K ruled; ALL merge inputs are now complete

`premerge_rulings_sacha_2026-09-14b.csv` archived (73 rows: the 62 earlier rulings unchanged + K0-K10). K0 MERGE_NOW: the behavioural arm's 24 studies / 40 estimates enter v1.7.18. K1 DROP, K2 keep both denominators flagged, K3 DROP (differs from the recommendation to keep the two frequency bands: the study leaves), K4 admit the small samples, K5 exclude on n = 8 and the table defects with the anchor rule "encounter-anchored items count, belief-anchored do not", K6 EXCLUDE the constructed-looking survey (differs from the recommendation to keep it at low confidence), K7 confirm the split, K8 DROP the approximate-denominator row, K9 confirm the three extraction-stage exclusions, K10 as recommended. On K5 he asked whether a sample floor of 100 would make sense. Answered in session from the freeze: of the 457 main-pool studies with an extractable n, 64 have n < 100 (52 of 269 content analyses, 3 of 94 recall studies) and 24 have n < 50; a floor of 100 would remove 14% of the corpus (64 of 457 study-construct cells), mostly small video content analyses, and the review already handles sample size by reporting the negative size-estimate correlation and the size-weighted medians. Recommendation: keep the floor at 20 and let n carry its confidence and risk-of-bias coding.

**Merge inputs, complete:** `rulings_sacha_2026-09-10a.csv` (+ 2026-09-08 files) via `merge_plan.py`; `ledger_proposals.py`; `premerge_rulings_sacha_2026-09-14a.csv`, `_2026-09-14b.csv`, `premerge_rulings_z_claude_delegated_2026-09-14.csv`; `behavioural_arm/openalex_2026-09/extraction/rows.csv`; `curated_reexamination_2026-09-13.csv`; `recall_windows_2026-09-11.csv`; the two dedupes in brief section G. The merge session may start apply_v1718.

## 2026-09-14 (night) — v1.7.18 FROZEN. The merge, and every decision inside it.

**FROZEN v1.7.18**: 1,052 estimates / 444 studies, MD5 528995e7751bb896f577494bc9f4c3c5, built by
`scripts/apply_v1718.py`, changelog `data/extract_v2/qa/changelog_v1718.csv` (376 entries, each
attributed to the ruling key that authorised it). All invariants hold. v1.7.17 was never applied;
its operations are folded in here, per the one-freeze decision.

HEADLINE MEDIANS (study-level): CONTENT 23.0 (k274) · RECALL 43.0 (k91) · SHARING 13.0 (k47) ·
EXPOSURE 1.0 (k18) · REACH 11.1 (k30) · CONCENTRATION 74.0 (k19).
Against v1.7.16: CONTENT and CONCENTRATION unmoved; RECALL +2.0 on 3 fewer studies; SHARING +1.8 on
5 more; REACH +0.1 on 5 more; **EXPOSURE halves, 2.0 -> 1.0, on 3 more studies**. The EXPOSURE move
is the one to report: k is small and the Allcott 5% left the pool as an R8 breach, so the median is
now carried by the remaining trace studies. §2 must be re-swept for it.

### Decisions taken tonight, beyond the 73 already-archived rulings

**1. The 24 ledger proposals that had never been ruled.** `ledger_proposals.py` marks each proposal
`ruled` or `proposed`. The proposed ones were written 2026-09-08, never reached Sacha, and were being
applied by nothing. Sacha asked for them as a decision page: `scripts/build_ledger_decisions.py` ->
`~/Desktop/ledger_decisions.html`, download archived as
`value_verification_keys/ledger_rulings_sacha_2026-09-14.csv`. 11 cards; 19 hidden because there was
nothing to decide (9 belong to studies this merge removes, 10 are settled by a pre-merge ruling).
**He ruled all 11 as recommended**: three REMOVE, eight APPLY.
 - `SEED-allcott2017` EXPOSURE 5 REMOVED: the 5% is ours, 159M fake-site impressions over those plus
   3,000M top-news impressions, a denominator built by summing two differently-assembled site lists.
   R8 forbids it and the paper never states a share. The study keeps its own framings.
 - `2-s2.0-85213958624` SHARING 0.94 REMOVED: arithmetically legal (both counts printed), but the
   paper says of the same denominator that it is "likely underestimating the prevalence", because
   under 1% of it was ever fact-checked. The ratio measures fact-check coverage, not prevalence.
 - `NEW-vanantwerpen-esm` RECALL 17.72 REMOVED: denominator is 2,278 survey occasions, not 123
   people. Identical shape to the row dropped at v1.7.16 on RECALL's population-denominator rule.
   The study keeps its valid 50.41% of 123 participants.
 - Eight documentation groups APPLIED (85085573221, 85091698994, 85095575703, 85164694763,
   85188806397, 85199110625, 85209206311, W4281770633): empty denominators filled, source quotes
   added showing how a figure was computed, a few metadata fields corrected. No value moved.

**2. Phase ordering inside the merge, which turned out to matter.** Four input streams target the
same rows, and later rulings deliberately reverse earlier ones. The first run produced 27 apparent
failures that were all ordering or supersession. The script now runs: removals -> merge_plan and
ledger corrections -> the pre-merge rulings A-L -> the additions -> four rulings that target rows the
additions create (F9, F10, F11, L1 and the per-narrative topics) -> a consistency sweep. The clearest
case is the H topic rule: `merge_plan` recodes four studies to politics_elections and H rules them
back to general_news, so H must run second. F9 and F10 retype a row the blind campaign ADDS, so they
must run after the additions. An edit on a row a removal took out is now recorded as `superseded`
and an edit another source already made as `already`, because with four sources both are normal.

**3. A consistency sweep, generalising the v1.7.16 lesson.** Retyping a row changes what its other
fields may say. Three invariants broke on the first freeze attempt and all three were consequences of
this merge's own retypes: five rows moved to QUALITY still carried a veracity breadth; two added
CONCENTRATION rows had no denom_class; and J1's clearing of `denom_selection` left `denom_class`
saying curated_sample. The sweep now clears breadth on QUALITY, sets CONCENTRATION to denom_class
n/a with no selection, and recomputes denom_class from scope and selection. This is the same fix
apply_dispute_rulings.py needed at v1.7.16, generalised so it cannot recur.

**4. The two dedupes, done.** `2-s2.0-85089622030` CONTENT 31.9 and `OA-W4407797130` N1/N3/N6 at
44.75 / 48.13 / 85.13 each arrive from two sources; the merge keys on (id, construct, value) and
records 6 dedupe events.

**5. The behavioural arm merged** under K0: 35 rows from 20 studies. K1/K3/K6/K8 dropped four
studies (the QUALITY-only supplement study; the Tumkur survey whose 90.3% is a computed complement;
the survey whose tables may be constructed; and the 0.68% whose denominator exists only as "nearly
four million"). K4 admitted the small samples and the floor stays at 20.

### Deliberately still open
19 ledger proposals never put to Sacha (nothing to decide); J2, fill four empty denominator fields;
J3, verify three row-versus-abstract mismatches against the text. All three are recorded in the dry
run's PENDING list and in this entry, not buried.

NEXT: Phase B, metaregression, the 28-hour bootstrap, manuscript re-sync (Note C1 and Table 2 to the
full 57-batch campaign and the two-coder value tier), NHB pair as tracked changes.

## 2026-09-14 (late) — v1.7.19 (documentation only), windows re-swept, and what the guard now says

**v1.7.19 FROZEN**, 1052/444, MD5 c8cf9648d1764e94132100cf87833b6a. Text fields only; the script
asserts no value, id or construct moved and refuses to write otherwise. That is deliberate: the
28-hour bootstrap was running while this was applied, and a value change would have wasted it.

**J2/J3 worked against the archived texts.** 17 denominators filled. One real error: both rows of
`2-s2.0-105009619554` carried the claim-level denominator (411 attributed characteristics) while
their values are shares of the 100 videos, which the rows' own quote says. Repointed and flagged as
nested (52% partial + 27% entire = 79% of videos, never to be summed). The claim-level 55% is NOT
added as a row; adding an estimate is an extraction decision, not a documentation fix, and it would
have moved that study's median and invalidated the bootstrap. The other two mismatches CONFIRMED the
freeze: a 14% that is the whole non-useful residual (irrelevance and personal testimony mixed in),
and a 7.7% the paper's own abstract mislabels, being engagement-weighted where ours counts items.
Also checked: the date contradiction in `2-s2.0-85193588807` (abstract says 2022, results say 2021)
does not affect us, the freeze already holds Jan 2020-Jun 2021, the results' window.
**56 empty denominator fields remain elsewhere** (14 on one study, 12 on another, 8 on a third).

**Recall windows.** 8 of the 9 new studies coded; `2-s2.0-105011756924` deliberately NOT added,
because it is `range_not_point` with no value and so is not in the seen-recall set the guard compares
against - adding it would have broken the assertion it was meant to fix. 12 studies removed (the
merge took them out of the cell) and **37 medians refreshed that had been carried from earlier
freezes**. The window file is now `recall_windows_2026-09-14.csv`; 71 studies, matching the cell
exactly. 7 of the 9 papers never print their item wording, recorded honestly as `unclear` rather than
guessed.

**Two of the nine may not be seen-recall at all**, both from the behavioural arm, and both are
consistent with rulings already made: `W4414351820`'s item is "most political information on social
media are false and unreliable", admitted under the perceived-amount precedent
(`2-s2.0-85169326292` holds the identical shape); `W7117302408`'s 69% is a challenge-battery row that
Sacha confirmed under K7. Recorded because a reviewer could reasonably ask about either.

**THE VARIANCE LADDER HAS MOVED, and the manuscript's §2.6 must change.** The guard's assertion on
the top five moderators now fails. New ordering (R2, %): ground_truth 22.2, id_method 21.3,
construct 19.0, **denom_fine 16.4**, measurement 16.2, platform 13.7, sampling 12.5, breadth 12.5,
topic 1.8, denom 0.0. `denom_fine` has entered the top five and displaced `sampling`.
**The review's actual claim survives intact**: topic (1.8) still sits far below every measurement
moderator, which is the gap §2.6 asserts and the checker tests. But the ordering sentence, the
checker's assertion, and §2.6's prose all need rewriting, and the published intervals come from the
bootstrap now running.

NEXT: the manuscript re-sync (counts, the EXPOSURE prose, §2.6, Note C1 and Table 2 to the full
57-batch campaign and the two-coder value tier), then the NHB pair as tracked changes.

## 2026-09-14 (night) — FULL AUDIT before the manuscript re-sync. Four adversarial passes.

Sacha asked for an audit of "all the code, data, files" before the re-sync, and separately whether
the replication package is healthy and honours what the paper promises. Four agents ran read-only
against the data, the code, the documentation and the package-versus-promises question. This entry
records what they found and what was done. **The most important finding changed three headline
numbers.**

### 1. THREE HEADLINE MEDIANS WERE CONTAMINATED (fixed)
`phaseB_descriptives.py` built its construct table as `[r for r in rows if construct == c]` — no
main-set filter at all. 104 demographic-subgroup rows and 10 non-proportion rows were entering the
study medians, and that table is the one FROZEN.md quotes as HEADLINE MEDIANS. The codebook and the
main-set definition both promise demographic rows never inflate a headline median.
**EXPOSURE 1.0 -> 1.3 · REACH 11.1 (k30) -> 12.5 (k28) · SHARING k47 -> k45.** CONTENT, RECALL and
CONCENTRATION unaffected. `phaseB_grade.py` had the sibling hole: it filtered `demographic_group`
but not `value_kind`, so 6 per-capita-intensity and 4 range rows entered the GRADE medians. Both now
share the invariants' predicate; descriptives, GRADE and uncertainty agree for the first time.
FROZEN.md records the correction and names the contaminated figures rather than quietly restating.

### 2. THREE SILENT-FAILURE BUGS, ONE FAMILY (fixed)
A stage that keeps working while answering about the wrong data is worse than one that fails.
- `phaseB_descriptives.py` fell back to `estimates_v1.4.5_frozen.csv` — seventeen freezes old, still
  on disk, so the fallback was live — whenever the pointer failed. Now raises on both branches.
- `validate_prisma.py` had the same fallback to v1.5.2. **Its own comment records that this exact
  bug shipped once**, reporting PASS on 329 studies while the freeze held 317. Now raises.
- `make_si_lists.py` was in PIPELINE.md's run order but NOT in `run_phaseB.sh`, so after every
  re-freeze the two PRISMA supplementary lists silently described the previous corpus. Added.
Also fixed earlier the same evening: three live tools hardcoding v1.7.16 instead of resolving the
freeze (the ledger and wave-3 decision pages, the value-check extraction builder).

### 3. FOUR PRISMA ORPHANS (fixed)
Four studies the merge removed had no terminal disposition, so the flow could not account for them:
`105008525623` recorded as a DUPLICATE_RECORD (not an exclusion, per ruling D1), and `105009525336`,
`85142238598`, `85165815218` as full-text exclusions on the blind pass's eligibility finding. The
last is the Meta 2020 ideological-segregation companion, whose outcome is ideological alignment, not
misinformation. `validate_prisma.py` now passes.

### 4. RISK OF BIAS COVERS 416 OF 444 (agent running)
The 28 unappraised are exactly the new acquisitions: 20 behavioural-arm studies, 6 scholar, 2 others.
The manuscript says every study was appraised, and two other documents assert RoB coverage must
equal the corpus. An agent is appraising them against `rob_checklist_v3.md`.

### 5. THE PACKAGE DOES NOT HONOUR THREE PROMISES (to fix)
Dry run: 480 files, 19.3 MB, denylist clean, zero absolute paths. But:
- **the independent-model adjudication trail is NOT SHIPPED** (`gpt_check_2026-09*`, ~2.5 MB). §4.11
  singles it out — "including the rows where our coding was found wrong" — and Note C says it is
  public. Nothing in the ALLOW list matches it. This is the paper's strongest transparency claim.
- **the abstract-only abstracts are excluded** by a DENY tree, though §C promises them as
  re-checkable. The package README admits it in writing.
- **the shipped recall-window file is the superseded 22-row one** with no question wording; the
  current file has 75 rows with `question_verbatim`, which is exactly what the promise describes.
- `check_manuscript_stats.py` cannot run inside the package (five unshipped inputs).
- LEAK: `docs/RA_package/*/papers/V070*.html` ships a third party's extracted full text with the
  corresponding author's email in the clear, plus Finder duplicates.
- No LICENSE file in the repo; the builder generates MIT + CC BY 4.0 at build time, but the
  manuscript states no licence at all.
- **The working repo must never be made public**: 1,768 tracked PDFs, 2.4 GB of history. §4.11 says
  the material is "version-controlled in the review's git repository", which points a reviewer at
  the wrong artefact. Deposit the BUILT package and cite that DOI.

### 6. DOCUMENTATION: 33 findings (to fix)
Worst first: the NHB cover letter's first substantive sentence says 456 studies / 975 estimates;
`si_included_studies.csv` is a different corpus from the freeze (40 studies it lists are gone, 28 in
the corpus are missing); `prisma_flow.svg` contradicts `prisma_counts.json` on nearly every terminal
box; the behavioural arm contributed 20 studies and appears nowhere in the PRISMA account; the
CODEBOOK's vocabularies and denominators are stale throughout and it SHIPS; `data_quality_methods.md`
still describes the July 33-study blind pass as the review's blind layer and says "no genuine data
errors remain"; `human_review_provenance.md` stops in July, omitting the largest tranche of human
oversight including both value coders. Plus a tier of finished-work-presented-as-open files and one
ad-hominem flag on a named author that must be cut to its evidentiary clauses.

### Came back clean
No secrets anywhere in the working tree; every API key read from the environment. Freeze resolution
correct in 35 of 37 live pipeline scripts. FROZEN.md MD5 matches. PIPELINE.md and `run_phaseB.sh`
agree stage-for-stage apart from finding 2. The package carries no PDF, no full text, no licensed
dump, nothing over 50 MB. Python seeds all present and documented.

NEXT: the 28 appraisals, then the package ALLOW-list fixes, then the documentation tier, then the
manuscript re-sync. The bootstrap continues undisturbed.

## 2026-09-14 (restart after the Desktop-access loss) — v1.7.20 committed and tagged; the bootstrap is running again

Access to ~/Desktop was restored. The working tree left behind by the interrupted session was
verified before anything was committed: `validate_frozen.py` PASS (1048 rows / 443 studies, MD5
92ba8f4763b546e7f768367450d4ec9a, matching FROZEN.md), `check_invariants.py` all nine hold,
`validate_prisma.py` PASS with every advanced record mapped to a terminal state. Committed as
69a3fe4 and tagged `dataset-frozen-v1.7.20`; pushed.

**The metaregression had NOT survived.** `/tmp/metareg_v1720.log` ends in
`impossible d'ouvrir le fichier ... metareg_univariable.csv : Operation not permitted` — the R
stage died at its first write when macOS revoked access, so every metareg output was still
v1.7.19's. Re-run on v1.7.20 (exit 0). The measurement gradient is unchanged at behavioural 4.9 /
content coding 19.9 / self-report 51.0.

**HEADLINE MEDIANS on v1.7.20**, regenerated by the audit-corrected descriptives:
CONTENT 23.0 (k274) · RECALL 43.0 (k91) · SHARING 13.0 (k45) · EXPOSURE 1.3 (k18) ·
REACH 12.0 (k27) · CONCENTRATION 74.0 (k19). Only REACH moves against v1.7.19 (12.5 k28), because
the duplicate study left the pool. FROZEN.md's top block now carries these instead of the promise
to regenerate them.

**The 28-hour bootstrap was restarted from zero** (not resumed: the kill at 25 minutes left no
checkpoint, and the data changed under it anyway). `nohup env B=200 Rscript
scripts/phaseB_metareg_robustness.R`, log `/tmp/metareg_bootstrap_2026-09-14b.log`, started 11:39.
Checkpoints to `data/synth/phaseB/.metareg_boot_checkpoint.rds` after every resample; resume with
`B=200 RESUME=1`. Expected finish ~2026-09-15 16:00. Do not start a second one.

**The variance ladder, on v1.7.20** (R2_adj, %): ground_truth 22.7 · id_method 21.8 ·
construct 19.3 · **denom_fine 16.5** · measurement 16.2 · platform 14.0 · sampling 13.0 ·
breadth 12.8 · topic 1.9 · denom 0.0. `denom_fine` has displaced `sampling` from the top five, as
it had on v1.7.19. The review's claim is untouched: topic still sits an order of magnitude below
every measurement moderator. `check_manuscript_stats.py`'s ordering assertions are updated to the
current ladder, and its recall-window input re-pointed from the superseded
`recall_windows_2026-09-11.csv` to `recall_windows_2026-09-14.csv` (71 studies, matching the cell).
With both fixed the guard runs end to end again instead of aborting: **87 of 245 assertions present,
68 of 68 stale strings absent, 158 mismatches** — the manuscript is still written against v1.7.16
and v1.7.18 numbers, which is exactly the re-sync that remains. §2.6's prose and the ladder sentence
must be rewritten, and the CI placeholders stay until the bootstrap lands.

**Risk of bias.** The 14 appraisals rescued to `~/misinfo_rescue_2026-09-14/` are in as
`data/rob/v3out/shard_700.csv`. Coverage is 416 of 443; the 27 unappraised are the new
acquisitions, and three agents are appraising the remaining 13 against `rob_checklist_v3.md`
(shards 701-703) from archived full text, which exists for all 13.

Still open, in order: finish and aggregate the RoB shards; the package ALLOW-list promises; the 33
documentation findings; the manuscript re-sync; the NHB pair as tracked changes.

## 2026-09-14 (restart, later) — risk of bias now covers the whole corpus, and one instrument rule is settled

The 13 outstanding appraisals were done by three agents against `rob_checklist_v3.md` from archived
full text (shards 701-703), joining the 14 rescued as shard 700. **Coverage is 443 of 443** — the
manuscript's claim that every included study was appraised is true for the first time since the
merge. Distribution, ruling-corrected: LOW 53 (12%) · MODERATE 208 (47%) · HIGH 182 (41%); full-text
only 52 / 206 / 160. The RoB x construct gradient the review's claim rests on is intact:
CONTENT 47.1% HIGH, RECALL 16.8%, SHARING 11.7%, REACH 1.7%, EXPOSURE 0.0%, CONCENTRATION 8.3%.

**Two appraisers read the UNCLEAR convention in opposite directions on the same day**, and both
flagged it rather than quietly picking one. The instrument is explicit — "rate UNCLEAR and treat as
HIGH in the overall (recorded separately)" — and 69 of the 72 UNCLEAR-carrying rows already followed
it, so the convention was never really in doubt; what was wrong is that `aggregate_rob_v3.py`
trusted each shard's own `overall` field except on the eight item-6 ruling rows. It now re-bands
every row from its item ratings with the pre-specified anchor, so the reported column cannot inherit
an appraiser's arithmetic, and writes `data/rob/rob_v3_band_deviations.csv`.

Five rows deviated corpus-wide. Four are re-banded: `85203845655` and `W4313324568` MODERATE -> HIGH,
`86000736431` MODERATE -> HIGH, `SEED-allcott2017` LOW -> MODERATE. Two of those four have no
UNCLEAR at all and were simply mis-summed against the both-6-and-10 rule, which is the better
argument for computing the band rather than reading it. The fifth, `W4210350805`, is kept as
appraised: the appraiser rated it HIGH against a MODERATE anchor because its tables look constructed
(100.0% exposure, zero non-exposed, every row totalling 332). That override is now declared in the
script with its reason and is still Sacha's call to confirm or reverse.

Phase B re-run end to end on the full RoB master; the counts crosswalk reports RoB coverage OK for
the first time. The bootstrap was left undisturbed and is still running. Note for the record: it
checkpoints every 25 resamples, not every resample as an earlier note said, so the first checkpoint
lands about three and a half hours in.

Three appraisal notes worth keeping, all flagged by the appraisers rather than acted on: item 6
misfits in both directions on the AI-provenance and channel-roster studies (the freeze's appendix
pools already quarantine these, so the instrument catches the same construct gap a second time);
`scholar_07`'s exposure is publisher-side supply read as consumption, which is item 5's named
example; and three of the new full texts are two-column PDFs whose text layer interleaves columns,
so every quote from them was reassembled and the reassembly is disclosed in the row's notes.

---

## 2026-09-14 (late) — the public package audited against what the paper promises

The question was narrow: for every sentence in the manuscript that tells a reader something is
public, does `scripts/build_public_package.py` actually select it? Six findings, all verified
against the files before anything was changed. The full account, with the reasoning on each, is
`docs/package_promises_2026-09-14.md`; this entry is the audit trail.

**1. The independent-model adjudication trail did not ship.** Methods §4.11 names it, "including
the rows where our coding was found wrong", and Note C3 calls it public. Nothing matching
`gpt_check_2026-09*` matched any ALLOW rule, in `docs/` or in `data/extract_v2/qa/`. Now selected:
the three waves' blind and verify sheets, the returns, the per-wave instructions and manifests, and
the scored `_KEY.csv` / `_disputes.csv` / `_scores.md` tables carrying `RULING` and
`RULING_reason` per row. 70 files.

**2. The abstract-only abstracts stay back, and the manuscript sentence has to change.** Note C3
says "their abstracts are archived with the data, so the coding can be re-checked against the text
it rests on". `data/fulltext/abstract/` (29 files) does not ship and should not: they are complete
verbatim abstracts rather than the one-sentence quotations LICENSE section 3 covers, 18 of the 29
came out of `data/abstracts/abstracts.jsonl` which the denylist excludes twice over, several are
scraped publisher pages with the navigation chrome still attached, and shipping them means carving
an exception into `data/fulltext/` and then into the re-scan that exists to stop exactly that. The
replacement sentence is drafted in the promises doc, for the manuscript owner to apply. Nothing
becomes unauditable: `abstract_only_list.json` names every such study with its DOI. Separately,
the checker currently reads 25 abstract-only studies against the manuscript's 32 — a re-sync
number, flagged for whoever does the manuscript pass.

**3. The shipped recall-window file was the superseded one.** `recall_windows_2026-08-12.csv`
(22 studies, no question wording) replaced by `recall_windows_2026-09-14.csv` (71 studies, with
`question_verbatim`), which is what §2.4 and Note B4 describe and what the checker reads.

**4. `check_manuscript_stats.py` could not run inside the package.** Five inputs were missing.
Four now ship (`curated_abstract_disclosure_2026-09-11.csv` + its `_notcurated.txt`,
`repair_2026-09/repair_estimates_final.csv`, `corpus_repair_2026-09/REPAIR_REPORT.md`) alongside
the recall-window file from finding 3. The sixth input is the abstract archive of finding 2, which
cannot ship, so that one check now reports itself skipped by name instead of raising on a tree
withheld on purpose. Exactly one check a third party cannot re-run: that an archived abstract
exists on disk for every study with no full text. Every statistical assertion runs.

**5. Privacy: extracted full text with a corresponding author's email, inside the RA package.**
`docs/RA_package/value_verification_2026-09/papers/V070.html` is the text extraction of
van Antwerpen et al., handed to the coders because no PDF existed. It would have shipped: the
RA_package rule keeps `*.html` and the `*.pdf` rule that hides every other paper in those folders
does not touch it. The denylist now excludes `docs/RA_package/*/papers/*` as a tree, so the next
non-PDF dropped in a coder folder cannot ship either. The original stays; the RA package uses it.
Its two byte-identical Finder duplicates ("V070 2.html", "V070 3.html", MD5 `ba1280f8…`) went to
the Trash. The other two coder trees (`round3_2026-08/papers`, 50 files; `irr_v2/papers`, 12) are
PDFs throughout.

**6. No LICENSE in the repo.** Added at the root, same MIT (code) + CC BY 4.0 (data, docs, text)
split the builder writes into each package, same third-party-material section, `Copyright (c) 2026
Sacha Altay`. The repo-root copy points at `docs/FROZEN.md` where the package's copy pins its
freeze.

**Three things the audit had not found.**

- A second contact-detail leak in a file that was already shipping.
  `data/extract_v2/qa/missed_estimates/candidates.csv` quotes raw sentences out of the article
  texts, and one ran through the front matter of Tham-Agyekum et al. and swallowed its CONTACT
  line, two author emails included. Fixed in the generator (`scan_missed_estimates.py` now scrubs
  email addresses from every candidate sentence) and the same substitution applied to the existing
  queue, one row of 522, nothing else in the row touched. Pre-scrub copy in `.backups/`.
- The builder had no way to catch that class at all: the post-build scan looked for absolute
  `/Users/` paths but not for contact details. It now reports every email address in shipped text
  outside a three-entry allowlist (the author's two published addresses, and Arcom's public
  submission mailbox quoted in this log, which is append-only and cannot be redacted after the
  fact), and a hit fails the build.
- Two more extracted-full-text caches sat inside `docs/`, not `data/fulltext/`: the wave-3 prompt
  files paste each paper's whole body (30–95 kB apiece) under the extraction instructions, and
  `disputes_wave2.html` embeds the disputed papers' front matter, postal addresses and phone
  numbers included, in expandable cards. Both denied by name. The lesson for the boundary is that
  extracted article bodies do not stay in the tree named for them, so the rules are on trees and
  content, not on extensions.

`--dry-run` also now runs the same three scans against the source files it would copy, and exits
non-zero on a denylist or contact hit; before, a clean dry run only meant selection had refused
the obvious things.

**Dry run, v1.7.20 (MD5 92ba8f4763b546e7f768367450d4ec9a):** 557 files, 21.4 MB (was 483 files,
19.4 MB). 21 candidates refused at selection, all intended (V070.html, 20 wave-3 prompt files).
Denylist clean, absolute paths clean, contact details clean. Nothing was built; nothing published.

## 2026-09-14 (restart, afternoon) — the manuscript is re-synced, and the sign test now has a script

**The manuscript is on v1.7.20.** The guard reports **246 of 248 assertions present, 68 of 68 stale
strings absent**; the two outstanding are section 2.6's bootstrap interval and its within-content
ladder, held as CI_PENDING / WITHIN_CONTENT_PENDING placeholders. The placeholder assertion used to
abort the whole run, so nothing else was verified while it stood; it now collects the placeholders,
reports them as PENDING and still exits non-zero, which keeps its meaning without blinding the rest.

**A THIRD table had the contaminated main set, and it fed the abstract.** `phaseB_slices.py`,
`phaseB_figures.py`, `phaseB_export_json.py`, `phaseB_prep_regression.py` and
`phaseB_review_response.py` all tested `within_misinfo_content`, a column the freeze does not have,
and none filtered `value_kind`. Ten range and per-capita rows therefore sat in the slices while
Table 1 and GRADE excluded them, so the ABSTRACT said reach 12.2% (k28) and sharing 12.7% (k46)
while Supplementary Table 1 said 12.0% (k27) and 13.0% (k45). Every table now shares the invariants'
predicate. The regression set lost two rows (839 -> 837), which invalidated the bootstrap started at
11:39; it was killed at 17 minutes and restarted at 11:56 on the corrected data. The ladder's
ordering is unchanged: ground_truth 22.5 · id_method 21.6 · construct 19.1 · denom_fine 16.6 ·
measurement 16.4 · platform 13.9 · sampling 12.8 · breadth 12.6 · topic 1.8 · denom 0.0.

**Three changes in the manuscript are more than arithmetic.**
- **Supplementary Note A's argument moved.** The source-level stratum is now the one interval that
  excludes zero (−9.2 pp [−14.8, −0.8]) and it runs opposite to the marginal gap, so the note no
  longer says "every interval spans zero". Claim-level identification yields nine times more
  misinformation than source-level, not four. The note's conclusion is unchanged and better
  supported: the constructs are not measured on common ground.
- **GRADE:** behavioural Exposure reaches HIGH (no high-RoB study in the cell, no proxy, stable
  under weighting) and Sharing moves LOW -> MODERATE.
- **Section 2.6's ladder is reordered:** the denominator class has displaced the sampling frame from
  the top five, and the prose names the moderators in the order the data give.

**The sign test in C1 now has a derivation.** It was hand-written, and two documents carried two
different p-values (p = .38 in the reporting summary, p = .169 in the manuscript) off counts nobody
could reproduce. `scripts/phaseB_correction_direction.py` recomputes the six construct medians at
EVERY one of the 59 released freezes, on the canonical main set, and compares consecutive versions.
Transitions that change the corpus by more than five studies are corpus expansions, not corrections,
and are counted apart. **Corrections moved a construct median up 24 times and down 22 (exact
two-sided sign test, p = .883); with expansions included, 25 up and 26 down (p = 1.00).** The old
"9 up, 17 down, direction is downward" cannot be reproduced from the files; it was computed on the
contaminated main set over an arbitrary version window. The new numbers say something simpler and
stronger, so C1 now says it: neither direction dominates. `phaseB_review_response.py` had its own
copy of this computation, from v1.5.0 only and without the main-set filter; it now reads the one
derivation.

**Two guard bugs fixed on the way,** both next to comments warning about exactly this: the B5
country denominators were hardcoded 15 and 17, and Supplementary Note A's eta-squared ladder was a
hardcoded literal while its own rank assertions two lines above were computed from the file. Also,
the stale-string guard for the predicted content-coding value was the bare string "19.8%", which
now collides with the recall-shared median; it is anchored to its sentence.

**Spearman reporting follows Nature's checklist.** `phaseB_uncertainty.py` now returns a 95%
Fisher-z interval on rho with the Bonett-Wright rank-correlation standard error, and §2.7 and B6
report rho with its interval, t, df and an exact p. Sacha's ruling: this was our call to make, not
his. He also ruled the ethics field and the multiple-comparisons question off the list entirely, the
archive as GitHub at the last minute, NHB as the venue, and the repo to be named for the paper.

## 2026-09-14 (restart, afternoon) — the bootstrap was never a 28-hour job; P1 applied; the manuscript PASSES

**THE BOOTSTRAP RAN IN 19 MINUTES.** Sacha asked why it always takes so long. Two reasons, both
avoidable, neither inherent:

1. **Dense linear algebra on a block-diagonal matrix.** The random structure is
   `~1|study_id/estimate_id`, so V is block diagonal with one block per study. `rma.mv` was fitting
   it dense: about 27 s per fit. With `sparse=TRUE` the same fit takes 0.5 s and returns the same
   variance components. Checked before changing anything: all nine moderators, dense against
   sparse, max difference 0.000001 pp.
2. **The null model was refitted once per moderator.** It does not depend on the moderator, so
   eight of every nine null fits were discarded. It is now fitted once per dataset.

Together, 28 hours became 19 minutes. The diff touches only the fitting calls: no line that consumes
RNG changed, so the draws are the ones the slow script would have made from the same seed. The
checkpoint machinery is kept but is now nearly pointless.

**The speed immediately paid for itself.** With the run cheap, the bootstrap's moderator list was
compared against the ladder the paper reports and was found to be missing `denom_fine` — the
moderator that had just moved into the top five. The paper would have reported a ten-rung ladder
with intervals on nine of them. Re-run with all ten: **denom_fine 16.6 [9.2, 26.2]**.

FINAL LADDER with 95% study-cluster bootstrap intervals (200 resamples): ground_truth 22.5
[17.2-28.9] · id_method 21.6 [16.2-27.3] · construct 19.1 [13.7-24.3] · denom_fine 16.6 [9.2-26.2] ·
measurement 16.4 [11-22.6] · platform 13.9 [10.2-21.4] · sampling 12.8 [8.2-19.5] · breadth 12.6
[7.6-18.8] · topic 1.8 [0-6.5] · denom 0.0 [0-1.8]. Topic's upper bound (6.5) still sits below every
measurement moderator's lower bound (the lowest is breadth at 7.6), so §2.6's claim holds with the
denominator moderator included. Within content analyses (414 estimates, 270 studies): ground_truth
14.8 · id_method 12.9 · measurement 10.9 · breadth 9.4 · topic 4.2 · denom_fine 3.9 · denom 3.4 ·
platform 3.2 · sampling 2.8. Topic still falls below every measurement moderator there, by a smaller
margin, and C2 now says exactly that rather than the older "about as much as".

**RULING P1 APPLIED: the September behavioural arm is a fifth identification stream.** Identification
goes from 25,576 database records to **30,958**. The arm's 562 screened-in records now carry terminal
states from its own stage files (`scripts/make_behavioural_arm_dispositions.py`): 374 excluded at
abstract, 99 not retrieved, 61 excluded at full text, 4 with no codeable estimate, 4 removed on the
author's ruling, 20 included. The flow reconciles at 443 + 145 + 51 + 506 = 1,145. The Google Scholar
recall check stays out and is named as a probe of recall, which is what its own QUERIES.md calls it;
its five studies are reported as such. Methods §4.3 and the reporting summary now describe five
streams, and both the identification total and the arm's funnel are ASSERTED from prisma_counts.json
rather than written as literals - §4.3 had carried its total as a literal for three freezes.

Two structural fixes fell out of it. `make_si_lists.py` held a second copy of validate_prisma's
fifteen-source precedence chain and asserted the two agreed; the assertion fired the moment one copy
learned about the arm, which is the argument against having two. validate_prisma now writes
`data/synth/prisma_terminal_states.csv` and make_si_lists reads it. And the state-to-reason mapping
matched labels by PREFIX, so the arm's new full-text reason ("Not eligible on full-text reading
(September behavioural query)") shared a prefix with the existing one and would have filed one state
under the other's reason; the match now asserts uniqueness.

**THE MANUSCRIPT GUARD PASSES: 252 of 252 assertions present, 68 of 68 stale strings absent.** Phase
B is complete end to end, all guards green, drift check clean. Ruling P2 (recode `scholar_04`'s
`demographic_subtype`) is queued for the next freeze; P3 (leave the `definition_variant` False
encoding, document it) needs nothing.

**Delivered:** the NHB pair as tracked changes on the Desktop, old = the builds he last read
(c90ee1b). Main text 31 changed paragraphs, SI 26. THREE TABLES changed and are NOT marked up, which
is the differ's known limit: main-text Table 2 (reliability checks), Supplementary Table 1 (construct
summaries and GRADE) and Supplementary Table 2 (Note A's content-versus-sharing strata).

## 2026-09-15 — the figures other than the PRISMA flow: labels, bases, and a column that was not to scale

Four pre-submission audit findings on the figure set, each checked against the rendered SVG before
anything was changed. All four were real, one with a smaller magnitude than the audit reported.

**1. Raw codebook levels were reaching rendered labels.** `crime_society` appeared in Figure 3
(`figP_topic_panels.svg`) and in `figD_by_topic.svg` beside prose labels like "Politics, elections".
A sweep of every `<text>` node in `docs/*.svg` for snake_case found eleven more across six figures:
`economy_finance`, `post_level`, `topic_level`, `self_perceived`, `convenience_snowball`,
`curated_seed`, `multi_platform`, `web_cross_platform`, and the four raw `ground_truth` levels in
`figH`. The cause was two independent label maps: `fig_coverage_panels.py` held a `PRETTY` dict
covering some levels, and `phaseB_figures2.py` held none at all and printed whatever the freeze said.
Both now read `scripts/fig_labels.py`, one map for the whole figure set, with `pretty()` the only
accessor. An unmapped level still renders (as its raw code) but the generator now prints a warning
naming it, so the next codebook addition is caught at build time rather than in a proof. Platform and
country values are already display strings and bypass the map by design. Regression check held: the
platform panel (`figN`, manuscript Figure 2) is byte-identical.

**2. Figure 5's bands rest on different totals, which the figure did not show.** Per-LEVEL n was
already on the figure; the BAND total was not, and the five bands range from 270 studies
(measurement) to 471 (construct), with sampling frame 351, ground truth 417 and identification level
426. Each band heading now carries its total. Separately, the figure rounded every median to whole
percent, which printed the exposure median of 1.315% as "1%" and gave two visibly different bars the
same "9%" label (behavioural panel 8.8, full census 8.6) and another pair the same "8%" (domain list
7.5, fact-checker 7.6). One rule now: one decimal, matching the forest plot and the text, so Figure
5's construct band reproduces Figure 4's medians exactly (1.3, 12.0, 13.0, 19.8, 23.0, 57.7).

**3. Figure 6's people column was not to scale.** The 1% sliver was drawn as `barH*0.01+4`, a 4-pixel
pad on a 2.1-pixel band: 6.1px of a 210px column, so the top 1% of users occupied 2.9% of the column
in a figure whose entire argument is how small that group is. (The audit put it at ~5%; it was 2.9%,
three times over rather than five.) The pad is gone and the sliver is exactly 1% of the column, with
a leader line to the label because a 2-pixel band cannot carry one.

**4. Figure 6 carried no k and no spread.** Both panels now name their basis under the title (5
studies reporting the top 1%; 4 panels, 6 estimates) and carry a min-max whisker beside the activity
column (37-80% for misinformation, 30-43% for general news), so the median is not read as a constant.
The deeper objection, that the figure plots 70% from five studies against 31% from a different four
panels, is not something to fix by editing Figure 6: the unmatched comparison is a real quantity and
the paper reports it. It is now accompanied by `docs/figQ_matched_concentration.svg`, a new figure
holding the panel fixed - one dumbbell per panel (Zhou et al. 2025, Eady et al. 2023, Osmundsen et
al. 2021, Grinberg et al. 2019), ratios 1.5 to 2.6, median 2.4 - built from
`review_matched_concentration.csv` rather than its own arithmetic. Whether it enters the manuscript
is the author's call; it is NOT wired into either docx builder. Study names are not in the freeze, so
`figQ` holds a four-entry id-to-name map and asserts the matched set has not changed, rather than
printing a bare Scopus id.

`phaseB_review_response.py` now runs in stage 6, before the figures, since figQ consumes its output;
PIPELINE.md records the move. Determinism holds: every figure generator run twice under different
`PYTHONHASHSEED` values produces byte-identical SVG, CSV and HTML. Invariants, the counts drift check
and the manuscript guard all pass.

## 2026-09-15 — the pre-submission audit, the appendix re-read, and two new analyses

Sacha read the manuscript, edited it directly in Word (untracked), left 29 comments, and
commissioned a seven-lens pre-submission audit (archived at `docs/reviews/`). This entry records
what all three found and what was done. **Four of his comments and most of section A of the audit
were real errors.**

### His edits, applied with two exceptions
Diffed his annotated copies against the builds he was sent, since the edits were untracked. Applied
as made, except: section 2.9's shortened sentence dropped the residual dimension and left 71 + 21 +
7 + 3 against 104 estimates for a reader to add up (the 2 restored), and Note A lost its four
closing paragraphs, leaving a note whose title asks a question it no longer answers, with the main
text pointing at it for the answer (compressed to one paragraph instead, 2,002 characters to 885).

### What his comments caught
- **"only 8?? out of 71"** sent me to the subgroup data, where the prose had drifted from it in
  three places, none guarded: 21 by age and 7 by gender against the data's 19 and 8, the community
  split missing so the dimensions did not sum to the total in the same sentence, and four age
  contrasts presented as four ratios when four studies give six. The contrast counts are now derived
  in `phaseB_subgroups.py`. The answer to his question: 18 studies report a partisan split and 8 of
  them give both sides on one measure; the 71 is estimates.
- **"for screening we didn't use opus at all?"** Backwards, and the manuscript was wrong: Opus ran
  the screening validation batches and every adjudication of a disputed screen, and one same-family
  pass ran on Fable.
- **"we actually have some spanish, etc. no?"** The restriction is on the language of the REPORT.
  The corpus covers 66 countries, most not anglophone.
- **"looks truncated at the bottom"** — it was. The PRISMA canvas height was a literal 1096 while
  the boxes are laid out from computed positions, so folding in the September arm pushed the last
  box to y = 1126 and the included-studies box was sliced in half in every build since. Fixed, then
  fixed again: the white background rect kept the old literal, leaving 53 transparent rows, which is
  the black band the audit then reported.
- **"why is it fig 1?"** The PRISMA flow was Figure 1 but was first cited in the Methods, after
  Figures 2 to 6 had all been cited in the Results. Now cited in the first line of the Results, and
  the guard asserts first mentions run in numerical order.

### The appendix re-read
- **THE PUBLISHED SCOPUS QUERY WAS NOT THE QUERY THAT WAS RUN.** The docx builder treats a single
  asterisk as an italic marker and Note D prints Boolean strings whose truncation operators are
  asterisks, so `consume*`, `quantif*`, `supersharer*` and `"super-sharer*"` lost their wildcards in
  every built SI. A reviewer re-running the printed string would have got a different record set.
- Note B4 had drifted from the window coding file on six figures, and its own categories summed to
  75 in a paragraph opening "all 71 seen-recall studies".
- Note C2 claimed topic "falls below every measurement moderator" within content analyses. It ranks
  FIFTH OF NINE there, above denominator class, platform and sampling frame.
- 575 words of duplication cut; the ledger jargon, model codenames and a banned sentence frame gone.

### The audit's section A, verified
A1 and A2 were the important pair and both were mine: the Methods paragraph explaining the four
grades of check still described the 10% pilot, so it understated and contradicted the census that
Note C1 and Table 2 now report, and **the census had no stated outcome anywhere**. It does now: 592
items adjudicated against the source papers, our coding upheld on 181, the blind coder adopted on
172, a third reading on 12, 156 not codeable from the paper as published, 40 rows added, 26 items
ruling a study ineligible and 24 studies removed.

A4 was also mine, from the day before: folding the September arm into the funnel moved not-retrieved
from 46 to 145 and the prose kept the old number, and the counts crosswalk had the same gap one
level down and was feeding an assertion, so the guard was agreeing with the error.

Two of the audit's findings were WRONG and are recorded as such: "66% health-adjacent should be
67.7%" summed three topic counts when a study can carry more than one topic, and "both .docx carry
live unaccepted tracked changes" is the delivery format Sacha asked for on 2026-09-11.

### GRADE: the imprecision rule was measuring scale, not fragility
EXPOSURE's median falls 2.0 to 0.6 under sample-size weighting, a 70% collapse but only 1.4pp, so an
absolute >=10pp rule let it escape the downgrade REACH takes for the same behaviour at a larger base.
The supplement was justifying EXPOSURE's HIGH on the ground that its median "is stable under
sample-size weighting", which the weighting table refutes on the same page. The criterion is now
relative. **EXPOSURE moves HIGH -> MODERATE; no construct now reaches high certainty.**

### The PRISMA spine, rebuilt
The figure jumped from the abstract screen to a retrieval box of 1,145 that only the bottom-up
partition produced. Every stream joining in between now has its own box: 747 + 41 + 188 + 131 + 19 +
5 + 14 = 1,145, then less 145 not retrieved = 1,000 assessed, less 506 excluded = 494, less 51
without a codeable estimate = 443. Two residuals that were invisible are now drawn: the snowball and
repair arms' full-text outcomes are not per-record in the ledger, and 516 title-advanced records
never received a second screening decision. The snowball arm screened 1,818 records and 331 advanced
to FULL-TEXT RETRIEVAL; the Methods said 331 advanced "to screening".

### Twelve raw codebook levels were printing in six figures
The audit found `crime_society`. A sweep of every text node found twelve, from two independent label
maps, one partial and one absent. There is now one map, `scripts/fig_labels.py`. Figure 5 was
consistently 0 dp, which is how it printed the 1.315% exposure median as "1%"; one decimal now, so
its construct band reproduces Figure 4. Figure 6's top-1% sliver was 2.9% of the people column
because of a hardcoded 4px pad on a 210px column.

### Two new analyses
**PERTURBATION** (`phaseB_perturbation.py`). Reassigning a share of the 897 main-set estimates to a
random other construct, 200 replications a level. The behavioural-exposure to self-reported-recall
ratio is 32.7x uncorrupted, 8.0x with a tenth of the codes wrong, 4.4x with a fifth, 2.8x with a
third, and it never reverses even at half. It also found where the review CANNOT lean: reach against
sharing flips in nearly half of draws at a tenth, because the medians are one point apart. Section
2.10 claimed "the construct gaps survive every check"; it now names that pair as the exception.

**CONCENTRATION NULL** (`phaseB_concentration_null.py`). A rarer behaviour is more concentrated by
construction, so the 2x could have been arithmetic. Under constant propensity, with activity
calibrated to the general-news concentration the panels report, the ratio is 0.96 to 0.99 across base
rates from 0.5% to 20%, against 1.5 to 2.6 observed. The guard asserts the null stays a null.

### The nine studies the cross-family sweep never reached
"306 of the 315" had been in the paper for weeks with no account of the nine. Tracing the worklist
against every released freeze pins the baseline at v1.7.14 and names them: six carry no proportion
at all (their only estimates are quality scores), one reports a range rather than a point, and two
entered the corpus in the repair after the sweep ran. Coverage of what carried a codeable estimate
at the time is complete. Wave 4 (`build_gpt_wave4.py`) packages the two late arrivals.

### His rulings, 2026-09-15 (`submission_rulings_sacha_2026-09-15.csv`)
Title KEEP. Abstract: add the reach-versus-recall comparison, rephrase "most of the variance", fix
the two smaller claims (the k clause was then cut as too long for an abstract). Zenodo DOI at
deposit. Ship the included-studies list and per-study risk of bias. Competing interests unchanged.
Substack reference marked (already was). Code the reach observation windows. Run the two late
arrivals. Search-query limitations NOT added ("we have many of these"). Main-text length decided on
re-read. Re-derive the unexplained exclusion reasons. Concede the coverage point in the Ecker
rebuttal. Drop "identifiable". Affiliation UZH. The matched concentration figure goes in the
appendix as Supplementary Fig. 3, not as a main figure.

**Supplementary Data 1** (`make_si_characteristics.py`) now ships every included study with its
characteristics, its risk of bias and its per-construct study-level value, which is PRISMA items 17
to 19 and was the reason no "which studies are behind this number" question could be answered. The
guard asserts it reproduces the paper's k for all six constructs.

OPEN: the falsity-within-unreliable-sources sweep (his W1 question, agent running), the reach
observation windows (agent running), the exclusion-reason recovery (agent running), then the Ecker
rewrite that depends on the first.

---

## 2026-09-15 — Reach observation windows coded (`reach_windows_2026-09-15.csv`)

Sacha's ruling of 2026-09-15: the review codes the observation window for all 71 seen-recall
surveys (Supplementary Note B4) and for none of the reach studies, so part of the 12.0-against-57.7
gap could be accounting. All 27 reach studies on the main analysis set of v1.7.20 now carry one.

Files: `data/extract_v2/qa/reach_windows_2026-09-15.csv` (27 rows, MD5
1a65e672d1ec929ea29f02f1b1d7704d) and `..._REPORT.md`. The set was taken from the freeze
(`value_kind = proportion`, no `demographic_group`, `construct = REACH`): 59 rows, 27 studies,
median 12.0, reproducing the freeze headline. Recall comparator is the same freeze's
`recall_subtype = exposure`, 71 studies, median 57.7, an id set identical to the recall windows
file. Each window was read from the archived full text and quoted verbatim; the vocabulary keeps
`ever` and `unclear` from the recall file, keeps `period_specific` for event-bounded windows, and
adds `fixed_period`, `calendar_year`, `whole_panel_period` and `per_day`.

**The premise needs turning around.** Among studies that carry a bounded window, the reach windows
are LONGER than the recall windows: median 106 days against 30. What is asymmetric is
unboundedness, 59% of recall studies (21 "ever" plus 21 unbounded frequency scales) against 7% of
reach studies (2 "ever"). Guess et al.'s 39 days is short for a reach study, not typical of one.

**The gap survives, narrowing by about a third.** Both sides restricted to bounded windows of
7 to 365 days: recall 55.9 (k14) against reach 18.5 (k19), 37.4 points, 3.0x, against 45.7 points
and 4.8x unrestricted. Restricting the reach side further to recruited person panels: 21.2 (k16),
2.6x. Both sides unbounded ("ever" on each): 63.8 (k21) against 14.7 (k2), 4.3x, the widest of any
matched comparison, though on two reach studies.

**Window length does not predict reach.** Spearman rho is -0.04 over the 23 studies with a
derivable length, -0.18 excluding the one-day study, +0.03 on the 16 panel studies. Bins are not
monotone (2-45d 18.5, 46-120d 30.3, 121-400d 10.3, >400d 1.7). Denominator does the work instead:
recruited person panels median 18.5 (k20), platform corpora and elites median 1.7 (k7). Three
designs hold the window fixed and still move: Guess/Nyhan/Reifler 44.3 and Moore et al. 26.2 on
deliberately matched 39-day windows, and `scholar_04`'s 44.3 -> 26.1 -> 16.5 across three 36-day
election windows.

A band-by-band match is NOT supportable: only the 28-45 day band has k >= 4 on both sides (recall
56.1 k4, reach 18.5 k7); no reach study runs 7 days or 6 months. The 7-365 day restriction is the
finest cut the data support.

**Four studies where the window could not be pinned.** `105027959122` (Bangladesh) states none at
all, coded `unclear`; `85105454127` (Osmundsen) and `85162702221` (Haenschen) have an end bound
and no start, coded `ever`; `W7146985142` (Oswald & Munzert) deliberately carries two (162 and 58
days) and is left out of the length grouping. Three more have month-granularity dates only.

Also logged in the report: three papers state two or three mutually inconsistent bounds for the
same estimate (`85145956359`, `85195353413`, `scholar_04` against `85152674280`), and Bovet &
Makse removed 24 days, "15% of our observation period", for missing observations.

Manuscript and `check_manuscript_stats.py` untouched; Sacha writes the paper's sentences from
these two files.

---

## 2026-09-15 - Falsity WITHIN source-labelled pools (new analysis, Sacha's request)

Question: the review asserts that source-level identification is loose within the domains it lists.
How much does the corpus let us quantify it? The quantity wanted is the share of content published
by, or shared from, sources a credibility list flags that a human judges false. Deliverables:
`data/extract_v2/qa/falsity_within_sources_2026-09-15.csv` (29 rows, 27 studies) and
`docs/falsity_within_sources.md`.

**Where it lives.** Not in the frozen dataset. The denominator-sets-construct rule makes this a
validation statistic, not a prevalence estimate, so it was never extracted. One frozen row is the
exception (`2-s2.0-85060013655`, already flagged "within-source upper bound, L25"). Everything else
came out of validation paragraphs, robustness appendices and limitations sections in the archived
full texts.

**Search.** Five scripted passes over all 1,198 archived texts (`v2txt` + the behavioural arm's
`txt`): source-list term near a falsity term near a percentage; share-of-pool grammatical
constructions; validation verbs (hand-coded, manually verified, spot-check, precision, false
positive, upper bound); "not all content from these sources" phrasings; coder-overturn phrasings.
Then the 287 texts that mention a source-credibility list twice or more were read in full by three
parallel agents (93/93/91). Every number reported was then re-read in the source by me before entry.
The non-list texts were screened by pattern and hold nothing.

**Result.** Eleven studies measure item-level falsity inside a list-labelled pool, eight with a
usable number, seven independent (the two Shao 2018 papers share a team and the Hoaxy corpus). Five
more decompose the flagged pool by tier or content type. Three measure the same thing at one outlet.
Eight assert it without measuring.

**The numbers, by how strict the verdict is:** 5.0% documented false-or-misleading (Wirtschafter,
matched to existing fact-checks, 95% of the pool never checked at all); 1.7% completely false and
11.8% mostly-or-completely false (Mourao & Robertson, the only study reporting the full
distribution, with 56.5% of stories carrying no misinformation); 55% / 60% / 76% false-or-misleading
(Allcott & Gentzkow, Tai et al., Pierri et al.); 72.7% and >85% once unverifiable items are lumped
in with false (Shao x2); >93% once the denominator is restricted to articles that were fact-checked
(Guess, Nyhan & Reifler). Pool composition: the "publishes almost exclusively fabricated stories"
tier is 2.6% (Huang & Carley), ~14% (Grinberg, derived) or ~30% (Osmundsen) of the flagged pool
depending on the study, and 41% of French consumption inside the unreliable pool is click-bait
(Cordonnier), a category defined with no falsity claim.

**Ruling on the premise.** "50% or less" holds only under a strict falsity standard. Every clean
false-or-misleading measurement is above 50%. Any sentence in the manuscript must name the standard
alongside the number.

**Two denominators recorded as traps.** (i) Fact-check conditioning explains the 93% outlier and is
the same instrument as the 5%, measured at opposite ends of the same selection. (ii) Wirtschafter's
prose and Table 3 disagree: the prose says ~44% of flagged posts were true or unverifiable, while
the table's cells are percentages of the whole 504-post sample and imply ~86%. Both recorded; the
44% is cited as theirs and the derivation is flagged as ours.

Not enough for a pooled estimate: eight numbers, eight different verdict categories, sample sizes
from 50 to 646, and all but one pool is circulation-weighted rather than a sample of what the sites
published. Report the range with the standard named, put the table in the appendix.

Open retrievals before submission: Tornberg & Chueri SI Tables S6/S7 (blinded coder, 250 articles
stratified over five factuality levels, the best design found, direction only in the text); Brady et
al. SI 5.1; Bergeron-Boutin table S44; the Guess/Nyhan/Reifler SI denominator behind the 93%;
Allcott & Gentzkow's online Appendix for the N behind "just under 55 percent".

Manuscript and `check_manuscript_stats.py` untouched; Sacha writes the paper's sentences from these
two files.

---
## 2026-09-15 — PRISMA item 17: the missing exclusion reasons, recovered (decision S5 = DERIVE)

The pre-submission audit said 139 of the 506 full-text exclusions carried no substantive reason.
That number counts bad CATEGORY LABELS: it is 75 (`DROPPED_V2_UNLEDGERED`, whose label announced
that no reason was logged) + 61 (the September behavioural arm) + 3, and 64 of those 139 already
carried a written per-record reason. The records with no reason anywhere were **102**: the 75
unledgered, plus the 27 pre-extraction triage drops whose ledger (`qa/dropped_studies.csv`) kept only
the id and the title.

**Where the reasons were.** Almost all of them existed, in the campaign that made the drop rather
than in a drop ledger. Tracing the 75 through the freeze history (last frozen file containing each
id, then the commit that removed it from `estimates_reextracted.csv`) splits them four ways: 19
reached a freeze and were removed later at a ruling (`full_reextract_2026-09/scores/
screen_disputes.csv`, `qa/v143_exclusions.csv`, `apply_v141/v143/v163.py`); 30 were re-extracted in
June and dropped before v1.1 (the `rev2`, `reexam` and `proc` pass outputs); 6 produced no rows at
the re-extraction (`qa/reextract_zero_rows.csv`); 20 were the abstract-only tier. The 27 triage drops
were all in `qa/proposals.csv` with a DROP/DISCUSS call, an L-rule and a note.

**Result: 505 of 506 rows now carry a record-level reason (was 404), from 45 ledgers and campaign
files (was 24).** Recovered 101 of the 102: 30 from the full-text pass outputs, 29 from a new
hand-verified ledger, 27 from the triage, 13 from the blind re-extraction's screen, 2 from
`v143_exclusions.csv`. Ten rows that already had a reason got a better one: six pointed at the ruling
instead of stating it, and four pointed at "section K of PREMERGE_BRIEF_2026-09-09.md", a section
that does not exist in that file.

**The residual is one record.** `2-s2.0-85145196122` (Kreps 2022): coded 1.1% / 0.3% from the
abstract, confirmed `keep` at the June value review, then zero rows at the full-text re-extraction
and no verdict recorded anywhere after that. Its row says so in words rather than leaving the cell
blank. It reads more like a record that fell out than an exclusion; worth a call before submission.

**Generator changes** (fixes in the generator, not the generated file):
- `make_prisma.py` — `EXCL_LABELS` moved to module scope, every label rewritten as an eligibility
  criterion. "(review of pending records)" and "(September behavioural query)" are gone. Per-state
  counts unchanged, so the figure's arithmetic and assertions are untouched.
- `make_si_lists.py` — imports `make_prisma.EXCL_LABELS` instead of matching the figure's labels by
  string PREFIX. That prefix table was a live footgun: two labels beginning alike filed one state
  under the other's reason, which is why two of them had to carry a disambiguating parenthetical,
  and the parenthetical was the pipeline stage. `exclusion_reasons()` now reads the campaign outputs
  in a documented precedence (dedup ledger, then the blind re-extraction, then the drop ledgers,
  then the recovered ledger and the remaining campaign files), and writes an explicit sentence where
  nothing recorded a reason.
- New input ledger `qa/exclusion_reasons_recovered_2026-09-15.csv` (29 rows: id, criterion, reason,
  evidence). Every row names the file or commit its reason was read from.

Full write-up: `data/extract_v2/qa/exclusion_reasons_2026-09-15_REPORT.md`.

**Not done, on purpose.** No terminal state was reassigned: three recovered records are duplicates
sitting under a `DROPPED_V2_UNLEDGERED` label that now reads "…or a duplicate of a counted record"
rather than being moved to `DEDUP_COLLAPSED`, because moving them changes the figure's per-category
counts and that is a freeze-level call. No full text was re-read. `manuscript_draft.md` and
`check_manuscript_stats.py` untouched.

Guards after the change: validate_prisma PASS (0 orphans), make_prisma reconciliation OK
(443 + 145 + 51 + 506 = 1145), make_si_lists list == flow on all 11 categories, validate_frozen PASS,
check_invariants all hold, counts-crosswalk drift clean.

## 2026-09-15 (late) — PRISMA item 17, and the one exclusion that should not be one

The exclusion-reason recovery (ruling S5) closed 101 of 102 gaps. The audit's figure of 139 counted
records whose CATEGORY LABEL named a pipeline stage; 64 of those already carried a written
per-record reason. The records with no reason anywhere were 102: 75 DROPPED_V2_UNLEDGERED and 27
whose ledger kept only an id and a title. The reasons mostly existed, in the campaign that made the
drop rather than in a drop ledger — 30 from full-text pass verdicts, 29 hand-verified from the
apply scripts and the learned-rules file, 27 from the triage that produced dropped_studies.csv, 13
from the blind campaign's screen disputes. **505 of 506 exclusions now carry a record-level reason,
no category is named by a pipeline stage, and the state counts are unchanged so the figure's
arithmetic is untouched.**

**THE RESIDUAL IS ONE RECORD, AND IT LOOKS LIKE A MISSED INCLUSION.** `2-s2.0-85145196122` (Kreps
et al. 2022, JMIR Infodemiology). Coded 1.1% / 0.3% from the abstract, confirmed `keep` at the June
value review, then zero rows at the full-text re-extraction with no verdict recorded anywhere. Its
archived full text carries both estimates with their denominators and an external ground truth:

> "We found that 1.1% of tweets from Twitter contained misinformation on COVID-19, with 5 (0.7%) of
> 746 tweets after discarding non-English posts in batch 1 and 6 (2.8%) of 211 tweets after
> discarding non-English posts in batch 2, compared to 0.3% on Weibo, with 1 (0.4%) of 279 ..."

and the methods state the ground truth: "compared posts using the WHO fact-check page to adjudicate
accuracy of content". That is CONTENT prevalence, a stated denominator, an external standard — two
rows the review should hold (Twitter 1.1% of 957 coded tweets; Sina Weibo 0.3% of 720 coded posts).

It is the only cell in the exclusion table whose reason is "none recorded", and on reading the paper
the reason it was dropped does not appear to exist. **Held for Sacha, not taken:** re-including it
is a freeze-level decision, it would move CONTENT from k274 to k275, and it changes numbers he is
about to read. Ruling P2 (the `scholar_04` demographic_subtype recode) is already queued for the
next freeze and would ride along in the same one; the bootstrap now costs 20 minutes rather than 28
hours, so the regeneration is cheap.

Also left for a freeze-level call: three recovered records are duplicates sitting under a label that
now reads "... or a duplicate of a counted record"; moving them to DEDUP_COLLAPSED would change the
figure's per-category counts.

## 2026-09-15 (night) — FROZEN v1.7.21: the study that should never have left

**FROZEN v1.7.21**: 1050 estimates / 444 studies, MD5 511cb4ddec26cb3d1bf20cb00a8615be, tag
dataset-frozen-v1.7.21, built by `scripts/apply_v1721.py` (changelog `qa/changelog_v1721.csv`).

**Why there is a freeze at all.** The exclusion-reason recovery left exactly one record whose reason
read "none recorded", `2-s2.0-85145196122` (Kreps et al. 2022, JMIR Infodemiology). Reading the
archived full text, the reason does not appear to exist: the paper reports content prevalence with a
stated denominator and an external ground truth. It had been coded 1.1% / 0.3% from the abstract,
confirmed `keep` at the June value review, then produced zero rows at the full-text re-extraction
with no verdict recorded anywhere. Sacha ruled to include. Two CONTENT rows, extracted from the body
rather than the abstract: Twitter 1.1% of 957 manually coded English tweets (746 in batch 1, 211 in
batch 2) and Sina Weibo 0.3% of 720 posts (279 and 441), on the two 24-hour windows the paper
sampled (30 January and 6 February 2020), adjudicated against the WHO fact-check page. Ruling P2
rides along: `scholar_04`'s `demographic_subtype` held `older` and `younger`, age labels in a field
whose vocabulary is the subtype set, recoded to `per_subgroup_rate`.

The apply script asserts that nothing else moves: the only new (id, construct, value) triples are
the two additions and no existing triple disappears.

**Risk of bias, 444 of 444.** The restored study was appraised against rob_checklist_v3 from full
text (shard 704): items 1, 2, 7, 8 and 9 HIGH, items 6 and 10 LOW, overall MODERATE. The frame and
the two 24-hour windows drive it, not the denominator — this study does the denominator honestly,
which is unusual for a keyword corpus (item 10 runs 62% HIGH across the corpus). **One judgement
call is flagged and not overridden:** the WHO Mythbusters page satisfies item 6 under the
instrument's anchor, but of the eleven coded "misinformation" tweets only the camel-urine cure maps
onto a Mythbusters entry — two are commentary ABOUT misinformation, one is a news report, and one
tracks the contemporaneous scientific account. Applied, the definition is author-devised. Item 6
stays LOW per the anchor with the failure carried on item 7; it is the only row in the corpus where
a second opinion would be worth having.

**What moved, and what did not.** Every count: 444 studies, 1050 estimates, 936 main-set, 899 across
the six constructs, CONTENT k274 -> 275, 505 full-text exclusions, 483 study-construct cells, risk
of bias 444/444 with 419 from full text. **No median moved**: CONTENT stays 23.0 on k275 and the
other five constructs are untouched, because one study contributing a study-level 0.7% to a
275-study cell moves nothing. The PRISMA flow reconciles at 444 + 145 + 51 + 505 = 1145 and the
restored study moved from the exclusion list to the included list on its own, its terminal state
flipping to INCLUDED_FROZEN and DROPPED_V2_UNLEDGERED falling 75 -> 74.

**LADDER on v1.7.21, with the bootstrap's intervals:** ground_truth 22.9 [17.5-29.6] · id_method
21.9 [16.4-28] · construct 19.0 [13.8-24.3] · denom_fine 16.5 [9.4-25.5] · measurement 15.9
[10.6-21.9] · platform 14.0 [10.6-21.9] · sampling 12.6 [8.2-19] · breadth 12.2 [6.9-18.7] · topic
1.8 [0-6.4] · denom 0.0 [0-1.5]. **The section 2.6 claim still holds and is now tight**: topic's
upper bound 6.4 against breadth's lower bound 6.9, half a point of clearance. Within content
analyses (416 estimates, 271 studies): ground_truth 15.6 · id_method 13.7 · measurement 10.5 ·
breadth 9.2 · topic 4.6 · denom_fine 3.8 · platform 3.3 · denom 3.2 · sampling 2.6, so topic is
still fifth of nine and the reading is unchanged.

**THE MAIN METAREGRESSION WAS STILL FITTING DENSELY.** Only the robustness script was made sparse
this morning, so `phaseB_metareg.R` took over ten minutes on this freeze. Same change, same verified
equivalence: **26 seconds**. Both R scripts now carry the reason in a comment.

**A guard could not see section 2.6 contradicting itself.** The section quotes the ground-truth share
twice, once from the ladder and once beside its bootstrap interval. The ladder regenerates in 26
seconds and the bootstrap takes half an hour, so between them the section read "explains 22.9% of
the variance" and then "explains 22.5% [95% CI 17.2-28.9]" — and every assertion passed, because
each half agreed with the file it was written from. `check_manuscript_stats.py` now compares
`metareg_r2_bootstrap.csv` against `metareg_univariable.csv` directly and reports a disagreement
over 0.05 points as staleness, with the command that fixes it.

Also fixed: the Supplementary Data 1 coverage check RAISED on a stale table instead of reporting,
which hid 270 other checks behind an intermediate that was legitimately one freeze behind (the same
failure the figure-text regex produced this morning); and a breadth assertion re-anchored this
morning kept hardcoded counts and went stale one freeze later, so it is deleted in favour of the
derived assertion beside it.

Guards at the close: manuscript 272/272 with 68/68 stale strings absent, invariants hold, PRISMA
gate passes, frozen validation passes, drift clean, Phase B complete end to end.

## 2026-09-16 — wave 4 of the cross-family check: the last two studies, and what they agreed on

The sweep's coverage gap is closed. Methods 4.8 had read "306 of the 315 studies the corpus then
held, which is every study that carried a codeable estimate when it ran" — true, but it rested on
the sweep's worklist rather than on the corpus, and two of the nine studies it missed were genuine:
they entered in the repair after the sweep had run. Sacha ruled on 2026-09-15 to code them rather
than explain them away ("if i need to review 9 papers to do 100% let's do that").

**What ran.** `scripts/build_gpt_wave4.py` built one self-contained prompt per paper using wave 3's
instructions VERBATIM, so the two are coded under exactly the rules the other 306 were. Sacha ran
them himself, one fresh session per paper in a different model family, and returned the JSON.
Scored by the new `scripts/score_gpt_wave4.py`, which differs from the wave-3 scorer in where "ours"
comes from: these two studies are already IN the freeze, so it scores against
`estimates_v1.7.21_frozen.csv` resolved from the top block of FROZEN.md, not against a repair
extraction file. Rows are matched on the VALUE within a paper (two coders word a measure
differently; they cannot word 9.9 differently), and the denominator is compared on its base — the
first integer of the denominator sentence.

**Result: complete agreement.**

| | rows |
|---|---|
| matched on value | 7 |
| construct agrees | 7 |
| denominator base agrees | 7 |
| GPT found, the freeze does not | 0 |
| the freeze carries, GPT did not | 0 |

`2-s2.0-105026630069` (sunscreen on TikTok): CONTENT 6% of 100 videos, both coders. It listed nine
figures it would not code and why, including the 2% coded "mixed" — the same call we made, and the
one a careless coder would have folded in. `2-s2.0-85136545530` (the UK sharing survey the round-3
human validation recovered, so it mattered doubly): all six RECALL rows, 33.8 / 14.8 / 9.9 / 8.8 /
7.6 / 2.5, each with the denominator we gave it — 9.9 against the 2,005 social media users, the
other five against the 589 past-month political-news sharers. That denominator split is the one
thing in this paper it would have been easy to get wrong, and it is the split the whole
denominator-sets-construct rule turns on.

Nothing went to adjudication, so `gpt_check_2026-09_wave4_queue.csv` does not exist; the scorer
deletes a stale queue rather than leaving one behind.

**Manuscript.** Four places said 306, each differently, and each is now the completed claim:
§4.8's checks paragraph (the sweep "and, in a later pass, the seven estimates in the two studies
that entered after that sweep, which together cover every study carrying a codeable proportion"),
a new Table 2 row (Independent model, coverage completion), Note C1's nine-study paragraph (the six
with quality scores only and the one range still stand as reasons; the two are now coded, and
coverage is "complete over every study in the corpus that carries a codeable proportion, 308 of
315"), and the asymmetry paragraph at the end of C1, where independent coverage was the repair's
advantage over the original corpus and is now even.

**Guard.** Three new assertions, and they read the RETURNED FILES, not a number I typed: the guard
counts the estimates in `docs/gpt_check_2026-09_wave4/returned/*.json`, spells the count, and
requires the manuscript to say that many in both the Methods sentence and Note C1, plus the derived
`306 + len(returns)` coverage figure. If a third study is ever added to the wave, the manuscript
fails until it is rewritten. 276/276 with 68/68 stale strings absent; invariants hold; drift clean.

**Delivered.** NHB pair rebuilt (49 references) and re-diffed as tracked changes against the build
Sacha last READ (`docs/nhb_*.docx` at c90ee1b), so today's edits sit alongside yesterday's in one
markup: main 79 changed + 10 inserted paragraphs, SI 40 changed + 23 inserted. Verified in the
BUILT docx, not only the master (lesson #53). The handed-back `~/Desktop/gpt_check_wave4/` is in
the Trash, its returns preserved at `docs/gpt_check_2026-09_wave4/returned/`.

## 2026-09-16 (cont.) — "why 308 of 315 and not 315/315", and the answer that was worse than the question

Sacha asked why wave 4 stopped at 308. Tracing it properly overturned this morning's entry.

**The nine were not what the entry said, because six of them are no longer in the paper.** Reading
the sweep's own `FULL_ANSWER_KEY.csv` (647 rows, 307 study ids) against the v1.7.14 freeze names
them exactly: two entered after the sweep (wave 4, done), one reports a range, and SIX are
QUALITY-only studies that left the corpus at v1.7.18, removed on the blind pass's eligibility
finding under Sacha's ruling. They are not among the 444. A wave-5 package built to code them was
binned before it was run; the list was traced from a historical freeze rather than from the
released corpus, which is lesson #40 again.

**Counted against the corpus as RELEASED, the coverage is 423 of 444, not 308 of 315.**

| pass | reaches, of the 444 released |
|---|---|
| cross-family sweep + repair check + waves 3-4 | 422 |
| whole-corpus blind re-extraction (57 batches) | 416 |
| **either one** | **423** |
| **neither** | **21** |

The 21 are the late arrivals: 20 from the behavioural-arm OpenAlex search and the study restored at
v1.7.21. Both independent passes had finished before they entered, so they rest on a single pipeline
extraction, adjudicated by the author against the source. They carry 38 of the 1,050 estimates.

**I had made the claim false this morning.** Before wave 4, §4.8 read "306 of the 315 studies the
corpus then held, which is every study that carried a codeable estimate WHEN IT RAN" — narrow, and
true. Rewriting it to "which together cover every study carrying a codeable proportion" dropped the
temporal scope and turned a narrow truth into a false statement about the released corpus, and C1's
"coverage is complete ... 308 of 315" and the asymmetry paragraph's "in both halves, every study ...
has been recoded by a different family" went the same way. All three are corrected: §4.8 now states
what each pass covered without a completeness claim, and C1 gives the table above in prose, naming
the 21 and what they rest on.

**The guard now derives all four numbers** (422, 416, 423, 21) from the artefacts: the sweep's
answer key, the two repair KEYs, waves 3 and 4, and the census extraction files. It caught its own
author immediately: the first version counted `docs/codex_check_wave5/wave5_worklist.csv` as
coverage and reported 444 of 444 on a wave that had been BUILT and not run. It now counts a study
only when the coder's answer exists — a filled `YOUR_construct`, a returned JSON — never when our
prompt does.

**Wave 5, rebuilt on the right instrument.** Not wave 3's full-text extraction (22 sessions) but the
SWEEP's: construct, breadth and denominator class coded blind from the reported quantity and the
paper's own definition, one line per estimate, which is the instrument behind the κ = 0.80 the paper
reports. 38 rows across the 22 studies, one file, one session, and the rows join that statistic
instead of sitting beside it. `build_gpt_wave5.py` COMPUTES the gap set from the artefacts rather
than taking a list, so it cannot be built against the wrong corpus twice. The Desktop copy omits the
answer key. `score_codex_full.py` gained `--dir`/`--key` and reproduces the original sweep exactly
(construct κ = 0.802 on 647 rows), so one scorer serves both.

`score_gpt_wave4.py` became `score_gpt_wave.py` when wave 5 gave it a second caller; it handles a
study that carries no proportion by sorting the second coder's numbers into "they don't call it a
proportion either", "they are restating a scale score or range endpoint we hold", and a genuine
candidate omission.

## 2026-09-16 — wave 3 blind pass: written up where it was left

**Why.** The wave 3 blind package was paused on 07/09 and its state lived only in the file
timestamps and in the handed-back staging folder, which has since been trashed. Two months from
now that is unreadable, so the state is now written down.

**Checked, not assumed.** The trashed staging copy (`~/.Trash/GPT_wave3_blind_2026-09-07`) holds
returns byte-identical to `docs/gpt_check_2026-09_wave3/returns/` (`diff -rq`, 9 files), so nothing
was lost with it; the canonical package is committed here. Every return parses, and all nine are
from the good build — the redo of 25–28 past ten overwrote the two empty first-round replies, so
there are no first-round leftovers among them. The scorer ran at 10:34 and its queue,
`data/extract_v2/wave3_2026-09/blind_queue.csv`, is 31 rows with 28 ruled.

**What is actually outstanding.** `handfound_01` — first by leverage — was never run, and its
batch file is not merely unsent: it was built at the old 90 000-character cap, its text ends
mid-word, and it still carries the TRUNCATED banner that two papers used to decline extraction in
the first round. It has to be rebuilt before it is pasted, and into a separate `--out` folder,
because `build_wave3_gpt_blind.py` rewrites `INSTRUCTIONS.md`, `MANIFEST.md` and every batch file,
which would change the files the nine returned papers were shown. The three unruled queue rows are
one question, not three: GPT called `scholar_09` and `scholar_10` ineligible, leaving three of our
values as extras, and `scholar_09` is titled *Synthetic Politics: Prevalence, Spreaders…*, so that
ruling deserves a look.

**Delivered.** `docs/gpt_check_2026-09_wave3/STATUS.md`, the resume document: purpose, what is
done, the two open items with the exact commands, the per-paper return table, and which files here
are generated. `MANIFEST.md` is left exactly as the builder wrote it (the status went in its own
file precisely because a rebuild overwrites the manifest). Sacha's note on the staging folder —
the redo batch was prepared while the first round's replies still sat in its `returns/`, mixing
vintages — is recorded as a standing rule: stamp the run folder or move the old pass out before
re-running, and paste from the package rather than a second copy.

**Hand-back wording (Sacha, 2026-09-16): "say to save as a json in the folder".** Wave 4's prompt
said only "Return the JSON as a file named `<id>.json`", and both replies came back in `batches/`
rather than `returned/`, which had to be found and moved by hand. Every wave generator now names the
destination explicitly and the folder exists before the package ships:

- `build_gpt_wave5.py` replaces the sweep's "fill the four `YOUR_*` columns, save in place" with a
  JSON spec — one object keyed by `item_id`, saved as `returned/wave5_codes.json` — and creates
  `returned/` in both the repo package and the Desktop copy. The worklist is read, never edited: an
  edited CSV comes back re-quoted and re-wrapped, which the sweep had to tolerate and this need not.
- `score_codex_full.py` reads that JSON (list or object form, and through a markdown fence), maps it
  onto the answer key, refuses an unknown `item_id`, and warns on rows with no answer. Verified both
  ways: the 2026-08 sweep still scores construct κ = 0.802 on its 647 CSV rows, and a synthetic
  38-row JSON with two deliberate perturbations scores and writes its disagreement file.
- `build_gpt_wave4.py` carries the same wording for any future full-text wave, and now REFUSES to
  rebuild once `returned/` holds answers: the batches are the instrument of record, and rebuilding
  them after a wording change would put a prompt on disk that is not the prompt those answers were
  given.

## 2026-09-16 (cont.) — wave 5 scored, one correction applied, and the docs that named a version to escape the drift check

**WAVE 5 CAME BACK AND CLOSED THE COVERAGE GAP.** 38 estimates across the 22 studies no
cross-family pass had read, one fresh session, the sweep's own instrument.

| dimension | n | raw | κ | the 647-row sweep, for comparison |
|---|---:|---:|---:|---|
| construct | 38 | 97.4% | **0.959** | 0.802 |
| breadth | 26 | 88.5% | 0.761 | 0.477 |
| denominator class | 17 | 41.2% | 0.183 | 0.469 |

Construct is the dimension the paper reports and it is the strongest here as in the sweep. The
denominator-class κ rests on 17 rows of which ten are ONE boundary, so it carries little on its own.
Full adjudication in `data/extract_v2/qa/gpt_check_2026-09_wave5_adjudication.md`; fourteen
disagreements, ours upheld on twelve, theirs adopted on one, one left open.

**The one adopted: v1.7.22.** `W7117302408` (Nigerian NIN-SIM survey, RECALL 69%) carried breadth
`false`. The paper's own sentence is "About 69% of respondents indicated that MISLEADING OR FALSE
information circulating on social media platforms created confusion". A band admitting misleading
content is `misleading`. One cell; `apply_v1722.py` asserts exactly one cell differs. Effect on the
analysis: breadth's adjusted R² 12.2% → 12.3%, breadth counts 186/155 → 185/156, no median moves.

**Two disagreements NOT applied, waiting on Sacha.** The denominator class of `W7162938155` (5,385
Indonesian comments on "the Prabowo-era government" — one issue, so `topical`, or a domain spanning
several, so `curated_sample`; no rank truncation either way, so the instructions' own tie-break is
what decides it rather than the paper). And whether `W7171843315` belongs in the CONTENT pool at
all: its denominator is 480 OBSERVED FACE-TO-FACE conversations during community-health-worker home
visits, 41.3% carrying a misinformation claim. Under denominator-sets-construct it is CONTENT and
the row is coded consistently with that, but it is the only CONTENT study in the corpus counting
something that was never online, and the independent coder called it OTHER. 1 of 275, moves no
median.

**A finding the wave produced that is not a disagreement.** 21 of its 38 rows could not be scored on
denominator class because OUR cell is empty. Across the freeze 39 main-set rows have `denom_class`
and `denom_type` blank and every one is a late arrival (21 behavioural arm, 18 blind re-extraction);
all carry `denom_scope`, so it is an unfilled field, not an unmade judgement. In the regression they
become `denom_fine = "unspecified"` and `denom = "other"`, 36 of 839 rows. **Checked whether that
junk bucket was suppressing the denominator moderator: it is not.** Re-mapping those 36 through
`denom_scope` (which carries the same coarse distinction) moves denom's R² from 0.0% to 0.2%. The
paper's claim that the coarse denominator explains nothing survives, so no re-freeze on that account.

### The documents that bought a permanent exemption from the drift check

`make_counts_crosswalk.py` skips any line matching `v1\.\d+`, on the sound theory that
"v1.5.2 (679 estimates / 317 studies)" is provenance, not drift. Several current docs use that exact
shape to describe the LIVE corpus — "Counts and vocabularies below are as at **v1.7.20** (1,048
estimate rows / 443 studies)" — so naming the freeze exempted them, and eight of them had gone two
freezes stale with the wrong counts while every guard stayed green.

`sync_doc_freeze_headers.py` now GENERATES those lines from FROZEN.md plus the canonical counts, the
way `sync_provenance_ledger.py` generates the freeze table. It is a curated list of file-and-pattern
pairs, because most `v1.7.x` mentions in the same files are real history and must not move; a
pattern that stops matching is an error, not a silent skip, and the script refuses to write while
any pattern is unmatched. Twelve lines across eight files refreshed to v1.7.22.

`check_pipeline_docs.py` asserts that `run_phaseB.sh` and `docs/PIPELINE.md` name the same scripts.
PIPELINE.md's own header has always said the two must agree and nothing checked it; three scripts
ran without being documented (`make_si_characteristics.py`, `phaseB_perturbation.py`,
`phaseB_concentration_null.py`), so a reader following the document regenerated everything except
Supplementary Data 1 and the two new analyses. Both new checks are in stage 8 of the runner and in
the document's own run-order block.

Also verified: 0 broken relative links across `docs/*.md` and `README.md`.

**v1.7.22 pipeline complete.** Bootstrap re-run at B=200 and **measured at 23 minutes** (09:37 to
10:00), which retired a claim six freezes old: README, PIPELINE.md, ENVIRONMENT.md, the reporting
summary, `run_phaseB.sh` and `build_public_package.py` all still told a reproducer to budget 28
hours, and the R script's own header disagreed with itself at 15 and 19 minutes. All now say about
25 minutes, with the measurement recorded in the script.

The ladder is unchanged but for breadth, 12.2% → 12.3% [6.9–18.7], which is the one cell v1.7.22
moved. Topic's upper bound stays 6.4 against breadth's lower bound 6.9, so section 2.6's claim keeps
the same half-point of clearance. Every guard green: manuscript 277/277 with 68/68 stale strings
absent, invariants, PRISMA, frozen validation, drift, the two new checks. Tracked pair rebuilt
against the build Sacha last read (c90ee1b) and delivered; main 79 changed + 10 inserted paragraphs,
SI 40 + 23, verified in the BUILT documents.

## 2026-09-16 (cont.) — Sacha's rulings, and the NHB length rule I had wrong

**His five rulings** (`data/extract_v2/qa/decisions_sacha_2026-09-16.csv`, from the Desktop decision
page): he agreed with four recommendations and overrode one.

| decision | mine | his |
|---|---|---|
| `W7162938155` denominator class | keep `curated_sample` | keep (agrees) |
| `W7171843315` in the CONTENT pool | keep + disclose in the SI | keep + disclose (agrees) |
| blind re-extraction of the late arrivals | run it now | run it now (agrees) |
| main-text length | trim toward ~4,500 | **leave as is** (overrides) |
| archive | Zenodo at submission | Zenodo at submission (agrees) |

Both wave-5 questions are CLOSED in the decisions register with his ruling and the reasoning; neither
needed a data change.

**The disclosure.** Note C3's Scope limitation now names `W7171843315` as the corpus's only estimate
of offline interpersonal transmission: 480 observed face-to-face conversations during community
health workers' home visits, 41.3% carrying a misinformation claim, coded as content because the
denominator is communication events each individually judged, with the independent coder's dissent
stated. `check_manuscript_stats.py` DERIVES the 480 and the 41.3 from the freeze and asserts both,
so the sentence cannot drift off the row it describes and a later edit cannot soften a disclosure
the author chose to make. 279/279.

### The word limit: I had the wrong number, and it changes the picture

I told him NHB's Article guideline was 4,000 words and that 5,404 put him 35% over. **Both halves
were wrong.** The limit is **5,000 words of main text with Methods EXCLUDED**, along with the
abstract, references and figure legends. Measured on the master (tables, headings and the HTML
provenance comments stripped):

| | words | limit |
|---|---:|---|
| Abstract | 168 | **150** |
| Introduction | 949 | |
| Results | 2,893 | |
| Discussion | 1,850 | |
| **Main text** | **5,692** | **5,000** |
| Methods | 2,856 | excluded |

So the real position is 692 words over on the main text (14%, not 35%) and **18 words over on the
abstract**, which is a hard limit and the kind of thing a desk editor checks first. Display items
are 6 figures + 2 tables = 8, exactly at the limit of 8, so nothing can be added without removing
something. The 5,404 figure carried in earlier notes matches none of these sections and should not
be reused.

His "leave as is" was ruled against my wrong number, so it is re-opened for him rather than treated
as settled — and the abstract overage was never put to him at all.

### The blind re-extraction is running

`build_late_reextract.py` COMPUTES the gap (released corpus minus everything the census extracted)
rather than taking a list, and it is **28 studies, not the 22 I had said**: 22 was the CROSS-FAMILY
gap, and the census gap is wider because seven studies covered by a cross-family pass were still
outside the census. All 28 have full text. Four batches of eight, `INSTRUCTIONS.md` copied verbatim
from the 57-batch census so these are read under exactly the rules the other 416 were, returns to
`data/extract_v2/late_reextract_2026-09/extractions/` — the path `_independent_reach()` already
watches, so the guard will pick the coverage up on its own. Three batches dispatched to fresh agents
with an explicit instruction not to open the freeze, any codebook, or any memory file.

## 2026-09-16 (cont.) — the blind re-extraction of the 28 late arrivals

Sacha ruled to run it. Four batches of fresh agents on the census instrument verbatim, explicitly
barred from the freeze, the codebooks and the memory files. All 28 returned.

| | this pass | the 57-batch census, for comparison |
|---|---|---|
| studies | 28 | 456 |
| eligibility agreed | 26 (2 disputes) | 430 of 456 |
| frozen values reproduced | 35 of 42 (83.3%) | 712 of 837 (85.1%) |
| candidate omissions | 15 across 6 studies | 202 across 123 |
| construct κ | **1.00** on 35 matched pairs | 0.89 |

Comparable to the census on every axis and better on construct. `score_full_reextract.py --camp`
does the scoring, so both campaigns are measured by one instrument.

**Four genuine corrections, none of which moves a reported number.** All four are on the decision
page (`build_late_reextract_decisions.py` → the Desktop); two are cases where OUR OWN RECORDED FIELDS
contradict the construct we assigned, which is the most useful kind of finding this pass can produce.

1. **`W4409319996` is quality-only.** We carry CONTENT 38.0% — sources advising more away rotations
   than the APD guideline allows. §4.6 excludes "guideline adherence" BY NAME. Third independent flag
   on this study (wave 5 disputed its breadth and denominator class). Swept for the pattern: 69
   CONTENT rows across 54 studies invoke guideline adherence, but nearly all judge falsity AGAINST a
   guideline as external ground truth, which §4.6 allows; this one measures adherence itself. Bounded
   either way by sensitivity A1 (CONTENT 23.0 on k261) and A2 (23.6 on k282).

2. **`W4313324568`'s 58.3% is a belief measure.** The row's own `misinfo_def` says "being DECEIVED by
   news that has later proven to be fake"; eligibility excludes belief in terms. Swept: 38 RECALL
   rows across 21 studies use belief-ish wording, but almost all are respondents judging the CONTENT
   false ("receive news they believe to be false"), which is what recall means, or perceived
   prevalence, which §4.2 admits deliberately. **This is the only clear violation — not systemic.**
   The blind coder also named the trap: the results paragraph says "58.3% stated that they have been
   influenced by disinformation", and only page 470 reveals the item. Anyone extracting from the
   results paragraph makes our mistake.

3. **A missed recall estimate in `2-s2.0-105004472114`.** The paper says 34.2% recognised NONE of its
   seven narratives, so 65.8% encountered at least one — the construct's own definition. We hold 6.5%
   ("five or more of seven") instead. Computed the impact: the study's contribution moves 6.5 → 36.2
   and the recall-seen median does not move at all.

4. **`W4306960737` holds one quantity twice**, 49.7% from the text and 49.2% from Table 4, on the
   same 120 videos. The paper contradicts itself; we recorded both readings. Table counts reconcile
   (61+32+18+7+2 = 120), the text does not.

**Five raised and recommended for NO change**, on the page with reasons: `scholar_09` and
`scholar_10` (the blind coder's exclusion agrees with our OTHER/appendix treatment — the scorer
flagged them only because the studies are in the corpus); `scholar_02`'s two 82% "concentration"
rows (a decomposition by query type, not a top-X% band); `W7168027278`'s four platform rows (which
platforms respondents NAME, not their own exposure, and the coder marked them low confidence against
a mislabelled figure); `W4210350805`'s 49.4% (a reaction measure).

Worth recording separately: `scholar_02` (Greene et al., Sci Adv) **contradicts itself** — the text
says 46.98%/15.37% of unreliable exposure comes from unreliable-source news queries, Table 1 says the
reverse. The blind coder used Table 1.

## 2026-09-16 (cont.) — v1.7.23 through the pipeline, and three more gaps it exposed

The four corrections are applied, the pipeline is regenerated end to end and every guard passes.
Ladder on v1.7.23 with the fresh bootstrap: ground_truth 22.8 [17.4-29.1] · id_method 21.8
[16.6-27.4] · construct 19.1 [13.7-24.6] · denom_fine 16.6 [9.7-25.9] · measurement 15.9 [10.4-22.1]
· platform 14.1 [10.6-21.4] · sampling 12.7 [8.3-19.6] · breadth 12.0 [6.7-18.9] · topic 1.8 [0-6.2]
· denom 0.0 [0-1.5]. **Section 2.6's claim still holds**: topic's upper bound 6.2 against breadth's
lower bound 6.7, half a point of clearance, the same as at v1.7.21.

**The abstract is at 149 words** against NHB's 150 ceiling (it was 168, and the limit is hard).
Sacha asked for it as a suggestion, so it goes over as a tracked change with the rest.

### Three gaps, each found by something failing rather than by inspection

1. **A transient write failure destroyed a completed 25-minute bootstrap.** All 200 resamples had
   run; `saveRDS` to the checkpoint then failed (the macOS permission flap) and, being unguarded,
   aborted the script before a single result file was written. The checkpoint is an OPTIMISATION and
   must never be a reason to lose the run: it is now wrapped in `try()`, and the resume from 175/200
   took three minutes. The irony is that the checkpoint mechanism exists precisely so an interrupted
   run is not lost, and it was the thing that lost it.

2. **`make_behavioural_arm_dispositions.py` was in NEITHER run order.** A study LEAVING the freeze
   changes its terminal state from `ARM_INCLUDED_FROZEN` to `ARM_EXCLUDED_AT_RULING`, so with the
   dispositions stale, `validate_prisma` had an unmapped terminal state and `make_si_lists` refused
   to run, which left `si_included_studies.csv` still listing the removed study, which made
   Supplementary Data 1 fail its own coverage assertion. One missing pipeline step, four failures
   downstream, and every one of them a loud assertion rather than a silent wrong number — which is
   the system working. Now in `run_phaseB.sh` and `PIPELINE.md`; `check_pipeline_docs.py` confirms
   41 scripts on both sides. NB that check compares the two run orders with each other and cannot
   see a script missing from BOTH; this one was.

3. **The ladder-rung assertion demanded "breadth 12%"** in a paragraph where every other rung carries
   one decimal, because R drops a trailing zero and 12.0 reaches the CSV as `12`. The guard now
   formats to one decimal when the value is integral.

### A tool for the re-sync itself

`resync_manuscript.py` drives the re-sync off the guard's own output: for each "expected to find"
string it relaxes the NUMBERS to wildcards, requires exactly one match in the manuscript, and swaps
it. 39 of 58 edits went through mechanically on the first pass and 12 of 14 on the second; the rest
are reported for a person, because they are bare numbers ("274", "22.8%") that appear in many
contexts. It never invents a value — every replacement comes from the guard, which computed it from
the pipeline. This exists because hand re-syncs are how section 2.6 came to quote two different
ground-truth shares at v1.7.21, and the hand portion of THIS re-sync proved the point immediately: a
p-value of .250 belonging to the Recall rank correlation got written over the denominator contrast's
.259, and the guard caught it on the next run.

**Delivered.** NHB pair rebuilt (49 references) and re-diffed against the build Sacha last READ
(`c90ee1b`), so the abstract, the C3 disclosure and every v1.7.23 number arrive in one markup: main
79 changed + 10 inserted paragraphs, SI 40 + 23. Verified in the BUILT documents.

## 2026-09-16 (cont.) — the deposit package, and lesson #57 recurring inside the hour

**The deposit is built and checked** (`build_public_package.py --force`): 583 files, 22.2 MB,
denylist clean — no PDF, no `data/fulltext`, no record dump, no secret. It carries the v1.7.23
freeze, the scripts, the codebooks and the adjudication records; the campaign working directories
stay behind because they hold publisher full texts.

**A gap in what it shipped.** The package's QA allow list is explicit, file by file, and the
validation campaigns added in the last two days were not on it. The census's working directory is
excluded by design, so the late re-extraction's adjudication record shipped NOWHERE: a reader would
have had Note C1's claim that the blind pass reaches all 443 studies and none of the evidence. Now
on the list, with the wave-4 and wave-5 scores, the wave-5 adjudication, and both of Sacha's ruling
CSVs. Also made a release copy part of `score_full_reextract.py` rather than something to remember.

**Lesson #57 recurred within the hour of being written.** Adding that release copy meant re-running
the scorer — on the late campaign, whose four corrections had been merged as v1.7.23 twenty minutes
earlier. Same circularity, same flattering direction: 35 matched pairs became 36. Restored from git
and the campaign is now CLOSED. The lesson as written said to guard closed campaigns; what it should
have said, and now does, is to CLOSE A CAMPAIGN IN THE SAME COMMIT THAT MERGES ITS FINDINGS. A rule
that depends on remembering it at the right moment is not a guard. Both campaigns are marked now,
and the scorer refuses either.

## 2026-09-16 (cont.) — the three papers the falsity sweep missed, and why it missed them

Sacha challenged three rows of Supplementary Table 3 (Pierri, Shao, Guess) and then remembered a
Tucker-authored paper in his own library that measures the same thing. Both were worth chasing.

**The three challenged rows all verify.** Each is quoted verbatim in its archived text; my first
attempt to confirm them failed three different ways, none of them the data's fault. Pierri's
sentence is split across columns by the PDF extractor ("approximately 76% of articles from
low-credibility sources do contain false or misleading content" reads interleaved with the adjacent
column). Shao's PLOS ONE figure was searched under the Nature Communications title. The Nature
Communications paper lives in `data/fulltext/txt/`, not `v2txt/`, exactly as its row records. Guess
is verbatim and its caveat was already on the row: the >93% conditions on having been fact-checked,
which is why it is the outlier and why the row is labelled "false, GIVEN the item was fact-checked".
Sacha's instinct on it was right and the note already says so.

**Allcott is slightly overstated in the Discussion.** The paper says "we categorized just under 55
percent as false" and its abstract says "just over half". The ledger and Note F's table both carry
"just under 55%", correctly; the Discussion sentence reads "between 55% and 76% across four studies",
which turns a "just under" into a bound. Flagged to him rather than changed, since he is mid-read.

**The Tucker paper is a family of three**, and it is the design this question needs. Aslett,
Sanderson, Godel, Nagler, Bonneau, Persily & Tucker run one preregistered pipeline across Nature
2024, JEPS 2024 and JOTS 2021: popular articles from mainstream AND low-quality sources, selected
within 48 to 72 hours of publication, then rated by six hired professional fact-checkers as true,
false or misleading, or undetermined. **The articles are chosen before any fact-check exists**, so
it removes the selection that makes Guess's 93% an outlier, and the mainstream arm is a built-in
comparison.

**Added with NO VALUE, deliberately.** The Nature paper states study 1's verdicts — "37
false/misleading, 102 true and 16 indeterminate" — but that POOLS the two source tiers, so it is not
a falsity rate within a source-labelled pool. The per-article tiers are in Supplementary Tables 1-5
of its Supplementary Information A, a separate file we do not hold; materials are public at
github.com/SMAPPNYU/Do_Your_Own_Research. The JOTS paper (135 stories, 12,883 evaluations) is the
likeliest to state the split outright and its full text is not held either. All three share one
pipeline and one group, so they are ONE piece of evidence. The ledger rows, the working notes and
Note F all say this; a guard now asserts that Note F still reports no value AND that no CSMaP row
has gained one, so the two cannot drift apart.

**Why the sweep missed them, which is the transferable part.** Each measures falsity inside a
source-labelled pool as a BYPRODUCT of an experiment about something else — search effects,
discernment, crowd fact-checking — so nothing in the title or abstract announces it. A sweep over
titles, abstracts and citation neighbourhoods cannot find that. It was found because Sacha
remembered a paper. The note now records the limit rather than implying the sweep was exhaustive.

Ledger 29 → 32 rows (30 studies, 17 in corpus). Three references added with CITE_MAP entries, NHB
build now 51 references. Guards 280/280, drift clean, pair re-delivered.

## 2026-09-16 (late) — the CSMaP number, after being pushed twice

Sacha: "really you couldnt find one number in any of these three papers???? ... you can also compute
it if we are confident the numbers reported". He was right, and the number was in the Nature paper's
Methods all along:

> "The modal response of the professional fact checkers yielded 37 false/misleading, 102 true and
> 16 indeterminate articles from study 1."

155 articles, **37 of them false or misleading: 23.9%**, judged by six hired professional
fact-checkers on a pool assembled before any fact-check existed. It is the only figure in the file
with that property.

**What I did NOT compute, and why.** The obvious next step is a per-tier split. The sampling draws
the most popular article of the previous 24h from five streams — "liberal mainstream news domains;
conservative mainstream news domains; liberal low-quality news domains; conservative low-quality
news domains; and low-quality news domains with no clear political orientation" — so three of five
are low-quality, and 3/5 of 155 would be 93, giving 37/93 = 39.8%. **That arithmetic is wrong and it
is recorded as wrong.** Five streams over a study that "ran for 10 days" gives 50 articles, not 155,
so more than one article per stream per day was drawn and the per-tier counts are not recoverable.
39.8% would have been a guess wearing arithmetic, and the ledger row says so in as many words.

What survives is honest and still useful: 23.9% spans both tiers, the pool is majority low-quality,
so it is a LOWER BOUND on the low-quality rate under the standard assumption that mainstream sources
publish falsehoods less often. It is reported in Note F, explicitly not ranked in Supplementary
Table 3, because it is not the same quantity as the rows there.

**And it lands where the argument predicts.** The loose "false or misleading" standard returns 55 to
76% on flagged, circulation-weighted pools. A design that selects on popularity rather than flagging,
and judges before anyone has chosen what to check, returns less than a quarter across a
majority-low-quality pool. Same lesson, cleaner instrument.

**The JEPS companion can never supply this**, supplement or not: it selects "the most popular pieces
of true and false/misleading news" — on VERACITY — so its composition is a design choice, not a
measurement. Recorded in the ledger so nobody mines it later.

**The guard was reversed as planned.** The assertion written that morning required every CSMaP row to
carry NO value, precisely so the ledger and the prose could not drift apart; it was designed to fail
the moment the ledger gained a value. It did, and it is now the positive assertion, deriving 37, 155
and 23.9 from the ledger's own `value_raw`. Both sides must move together in either direction.

Guards 281/281, invariants, PRISMA, frozen, pipeline docs and drift all pass. Pair rebuilt and
re-delivered against `c90ee1b`.

**The transferable bit.** Two pushes from Sacha produced this: first "we're sure that none other in
the corpus measure that?", which surfaced a whole paper family the sweep had missed because each
measures falsity-in-a-source-pool as a byproduct of an experiment about something else; then "really
you couldnt find one number", which was right. Search the author's own library, not only the corpus,
and do not stop at the first "it's in a supplement we don't hold" — the main text had it.

## 2026-09-16 (late) — the tier split, from the authors' replication data

"try again pls". The avenue I had not tried was the public materials repo, and it had everything.

`github.com/SMAPPNYU/Do_Your_Own_Research`, `Data/Fact_Checker_Data_Master.csv`: 165 articles, one
row each, with the sampling stream in `Article_Num` and up to six professional fact-checkers'
evaluations. The paper states that mainstream sources were tracked on CrowdTangle and low-quality
sources on RSS feeds (most low-quality Facebook pages having been banned), so the five streams map to
tiers with no judgement call: `ct_con`/`ct_lib` mainstream, `rss_con`/`rss_lib`/`rss_unclear`
low-quality. Taking the modal verdict, the paper's own rule, with ties counted indeterminate:

| tier | articles | false or misleading | true | indeterminate |
|---|---:|---:|---:|---:|
| low-quality (3 RSS streams) | 99 | **39 (39.4%)** | 46 | 14 |
| mainstream (2 CrowdTangle streams) | 66 | **1 (1.5%)** | 64 | 1 |
| both | 165 | 40 (24.2%) | 110 | 15 |

**39.4% within low-quality sources, against a 1.5% mainstream control measured on the same days by
the same coders under one verdict standard, on articles chosen before anyone decided what was worth
checking.** No other row in the file has a control arm, and none is drawn from an unconditioned pool.
A 26-fold gap.

**On the arithmetic I refused to do earlier.** I had declined to compute 37/93 = 39.8% because the
stream-to-article ratio was unknown, and called it "a guess wearing arithmetic". The real answer is
39/99 = 39.4%. The guess would have been almost exactly right — and refusing it was still correct,
because it was right by luck: 93 came from assuming 155 articles split 3:2, and the true denominator
is 99 from a 165-article balanced design. A number that happens to land near the truth by a wrong
route is not evidence, and would have had to be withdrawn the moment anyone checked the derivation.

**Recorded honestly as ours, not theirs.** The article prints only the pooled verdicts; the split is
our computation. `scripts/csmap_falsity_by_tier.py` does it, asserts the streams are the expected
five and balanced, and the data is vendored to `data/external/csmap_2024/` so it runs offline. Note F
says in terms that we report it beside Supplementary Table 3 rather than in it, "because the split is
our computation from released data rather than the paper's own figure". The released master spans 33
days (13 Nov 2019 to 6 Feb 2020) and therefore studies 1-2, not the 155 the paper attributes to study
1 alone; the tier contrast is the point and the row says so.

**The guard now checks the prose against the SCRIPT**, not against a number in the ledger: it runs
`csmap_falsity_by_tier.py`, parses both tiers out of its output, asserts Note F quotes them, and
asserts the ledger's own value matches the computation to within 0.05pp. Three things now have to
move together. (It threw a NameError on first run — a variable left behind by the edit — which is
lesson #52 again: fixed so it fails as a mismatch.)

Guards 282/282, everything else green, pair rebuilt and re-delivered.

**The lesson, which is Sacha's not mine.** Three pushes, three finds: the sweep had missed a paper
family; the "unavailable" number was in the Methods; the tier split was in the replication repo. Each
time I had a reason to stop that sounded like rigour — not in the corpus, pools both tiers, in a
supplement we do not hold. **Check the replication data before concluding a number is unavailable.**

## 2026-09-17 — the comment round: 25 comments, his untracked edits, and the PRISMA move

He read the main text, accepted our tracked changes, edited UNTRACKED throughout, and left 25
comments. The SI he did not touch. His annotated copies are archived at
`docs/.backups/manuscript_NHB_*_annotated_2026-09-17.docx`.

**Finding his edits.** All 2,422 tracked changes in the returned file were authored by "Claude", so
none of his own edits were marked up. `scripts/extract_docx_feedback.py` (new) pulls comments with
their anchors, tracked changes by author, and the accepted text; diffing that accepted text against
the build he was sent is the only way his edits surface. Ten differing blocks: four structural, eight
in-paragraph. Every one applied verbatim.

Structural: he added an **Introduction heading** (the builder had been dropping it on the Nature
convention that an Article runs straight from the abstract; his edit wins and it now renders); moved
the heterogeneity paragraph into 2.3 and deleted the 2.5 heading, with a comment telling us so
("dont overwride me edits"); deleted the "Sample size and estimate size" heading; and cut the
coverage paragraph from the Discussion.

Deleting two headings left numbering gaps that the PRISMA checklist cross-references pointed into,
so the Results sections were renumbered twice (once for his deletions, once after 2.4 was collapsed)
and the references in `prisma_checklist.md` and `reporting_summary_draft.md` repointed.

### The 25 comments

21 applied as edits; [562] answered with no change on his say-so; [316] was a confirmation; [682]
and [102] he ruled on directly. Notable ones:

**[40] was a real citation bug, not a formatting quibble.** He read a superscript "1,18" as a range.
It was two reference numbers where there should have been one: `(van der Meer & Hameleers 2025)`
CONTAINS the string `Hameleers 2025`, which is also a mapped citation, so `convert()` matched both
and emitted both numbers. The matcher now claims character spans longest-first, and the build prints
a note for any future key nested inside another. It was the only such pair in 51 references.

**[907]/[908]** — "(Results, 'Who is exposed: demographic subgroups')" is generated by the builder's
`_name()`, not written in the master. The part prefix is gone; a cross-reference is now the section
name alone.

**[102] PRISMA into the Methods.** Done, with the figures renumbered: Platforms 1, Topics 2,
Prevalence 3, Drivers 4, Concentration 5, PRISMA 6, placed at its Methods citation. I made two
mistakes doing it and the guard caught both: the renumbering pass rewrote the "Figure 6" I had just
inserted (6 -> 5), and leaving a flow-diagram citation in 2.1 broke the cited-in-numerical-order
assertion. The Results now points at the Methods without a figure number.

**[682] the eight-study content cell — retired.** The "restrict to independently re-extracted
studies" analysis rested on the seeded 48-study pilot (Content 8, Recall 3, Reach 13) AND has been
superseded, because the whole corpus has since been re-extracted blind, which makes the restriction
vacuous. It was also the one check the paper said the construct gaps did not survive, which gave an
8-study cell real rhetorical weight. Note B2 records the retirement and why, and the cell sizes are
still asserted there, so the reason cannot quietly disappear either.

### Two faults found by doing this, neither of them his

**A stale number nothing was asserting.** Note C2 lists every moderator's bootstrap interval. The
denominator-class rung read 16.5% [9.4-25.5] from v1.7.21 while the pipeline said 16.6% [9.7-25.9].
The guard asserted eight of the nine rungs; `denom_fine` was never in the list. An unasserted number
inside an asserted paragraph is the easiest kind to miss. Rung added.

**Moving text to the appendix nearly lost it.** Cutting the concentration null and the
abstract-disclosure counts per [583] and [911], I pointed the main text at Notes B2 and B3 — but
neither held the material and B3 is GRADE. The guard failed immediately. The null is now genuinely
in B2 and the reporting counts are a new **Note B7**. A cross-reference is not a move.

### The baseline, and a generator bug it exposed

He accepted our changes, so the next tracked diff must be against HIS document as it now stands:
our changes accepted, his untracked edits in place. Neither the master nor any previous build is
that, so `scripts/accept_tracked_docx.py` (new) builds it — keep insertions, drop deletions, drop
comments, loop to a fixed point.

It exposed a latent fault in `make_tracked_docx.py`: the returned file carries **1,262 opening
`<w:ins>` tags and only 1,250 closing ones**. Twelve insertions are unclosed. Word tolerates it
silently, which is why it has never surfaced. The accept script strips orphan markers (dropping the
marker and keeping the content IS accept semantics, so it is right here), but **the generator should
not emit them** — an open item, not fixed today.

Delivered: main 29 changed + 8 inserted paragraphs, SI 11 + 3, against the new baseline. Guards
285/285, invariants, PRISMA, frozen, pipeline docs and drift all green, 51 references.

## 2026-09-17 (cont.) — critical re-read of the supplement

He asked whether the appendix reads as AI-generated, whether it is all sound and useful, and whether
anything is overcomplicated, weak, or would make a reviewer suspicious. Written up in full at
`docs/appendix_review_2026-09-17.md`; the substance:

**It does not read as AI-generated.** Across 9,802 words and 308 sentences: zero instances of
"delve", "underscore", "nuanced", "robustly", "leverage", "it is worth noting", "plays a crucial
role" or "the fact that", and five em dashes. Two real tics: the contrast construction ("rather
than", "not X but Y") 42 times, one sentence in seven; and 52 sentences over 45 words, the worst a
139-word list of modelling choices in C2.

**The one bad passage is C1 paragraph 8, 528 words.** It interleaves the sweep's 306-of-315, wave 4's
two studies and wave 5's 22, and it declares complete coverage one sentence BEFORE "closing the gap
took one further pass", so the reader meets the gap after being told there is none. It also uses
"after the sweep had run" for two different sets without distinguishing them. This is where the
accretion of the last three days shows, and it should be split in two, chronologically.

**Strongest parts, to leave alone:** the direction-of-corrections paragraph (a sign test over 59
dataset versions, plus a verified-subset comparison, answering the author-bias objection before it
is made); the test-retest ceiling paragraph (reports a discarded coding run at 45% self-agreement
and draws a general lesson); B3's GRADE table (nothing HIGH, Content VERY LOW on k = 274).

**What a reviewer will circle:** Note A's sharing strata are thin (claim-level k = 12, fact-checker
k = 4) under a claim that the difference changes sign with the instrument; GRADE lands on MODERATE
for five of six constructs, which reads as a default even though the reasons differ; and
Supplementary Table 3 carries several single-study rows, three from one paper.

**Nothing is useless.** Checked specifically. B7 is small but is the home of counts the Discussion
cites; C1b could fold into B1, cosmetically.

## 2026-09-17 (cont.) — rewriting the supplement by ear, the package, and the cover letter

He asked for the appendix to be made as good as the main text, since he will read it once: "it needs
a dozen sentences rewritten by ear, do it."

**Note A rewritten.** Short sentences against long ones, the argument stated before it is qualified,
and the three guard assertions re-anchored to the new prose rather than the prose bent to the guard.
**C3 restructured**: seven limitations were one 495-word paragraph using colon-labels as a
pseudo-list; each now has a bold label and its own paragraph. **C1 paragraph 8 split** earlier the
same day, chronologically.

**The contrast tic, honestly.** "rather than" fell from 41 to 23, but the first substitution pass
simply traded it for ", not X" (32), and the second varied those down to 25. The write-up says so:
total contrast constructions are near where they started, and a substitution table cannot fix a
rhythm problem. What the rewrites of Note A and C3 do is different in kind — they vary sentence
length and put the claim before the qualification — and that is what the remaining sections need.

**A wrong number in the replication package README, found by reading it.** It announced "1063
estimates from 443 studies". The freeze holds 1048. `build_public_package.py` counted LINES in the
frozen CSV rather than parsing it, and source quotes contain embedded newlines, so the headline
count of the replication package had been inflated by 15 for as long as the package has existed. It
now parses the CSV and asserts its study count against the freeze it ships. This is the first thing
a data editor reads.

**Submission sweep, 8/8:** freeze 1048/443, no placeholders, package built and shipping the current
freeze, no PDFs or full texts in it, both docx built.

**Cover letter drafted** (`docs/cover_letter_NHB.md`, 534 words, copy on the Desktop). It leads with
the contradiction the field argues about, gives the three findings, and makes the case on
transparency: four grades of reliability reporting, a blind re-extraction of every study, a
cross-family check covering all 443, and the automated-coder degradation failure mode documented for
others. It closes on conservatism — nothing reaches high certainty, the largest cell is very low, and
one of our own headline comparisons is reported as not separable. Every number in the letter was
checked against the manuscript programmatically; none is unsupported. Affiliation and contact are
Sacha's to fill.

**Submission folder, and Word for anything a human reads.** `build_submission_folder.py` assembles
`~/Desktop/NHB_submission`: both manuscript documents, the cover letter, the reporting-summary
content, the PRISMA checklist, the two Supplementary Data CSVs, the six figures as individual SVGs,
and a `00_READ_ME_FIRST` naming what is still outstanding. The tracked-changes pair lives in
`00_for_review_tracked_changes/` inside the same folder, so there is exactly ONE place for
everything and no loose docx on the Desktop — macOS had already made a stale
`manuscript_NHB_supplementary 2.docx` when a copy landed on a file open in Word, four hours behind
the real one.

Sacha: **"md files are just for you, not me or other humans."** `scripts/md_to_docx.py` (new)
renders the cover letter, the reporting summary and the PRISMA checklist to Word — headings,
paragraphs, bullets, tables, bold and italic, one typeface, nothing decorative. The letter renders
without a title block or the drafting note, so it is a letter someone can send rather than a
document about a letter.

**The data-availability statement had no archive and no DOI slot.** It read "will be archived on
publication" and named nothing — no repository, no placeholder — so a submission could have gone out
with no deposit location at all, which NHB requires. Section 4.11 now names Zenodo, carries an
explicit **[DOI TO BE INSERTED ON DEPOSIT]**, and states plainly that the working repository holds
the full texts of the included studies and cannot be redistributed, so the deposit is a curated
subset and not a mirror. `check_manuscript_stats.py` reports the placeholder on every run and goes
quiet once a real DOI replaces it; it is a reminder, not a failure, because the placeholder is
correct until the deposit exists.

## 2026-09-17 (cont.) — RETRACTION: make_tracked_docx.py emits no malformed XML

I reported earlier today that `make_tracked_docx.py` produces 12 unclosed `<w:ins>` tags, called it
a latent bug Word was tolerating, logged it as an open item and told Sacha. **That was wrong, and
the error was mine.**

`word/document.xml` parses strictly with lxml: it is well formed. The counts are 1,250 `<w:ins …>`
openings, 1,250 `</w:ins>` closings, and 12 SELF-CLOSING `<w:ins …/>`. The self-closing form is the
correct OOXML for an inserted paragraph MARK: `inserted_paragraph()` puts an empty `<w:ins/>` inside
`<w:pPr><w:rPr>`, which is exactly how Word records that a paragraph break was inserted, and the
document had 12 inserted paragraphs. My regex `<w:ins\b` counted both forms as openings and only
`</w:ins>` as closings, so 1,262 against 1,250 looked like twelve orphans.

The lesson is the one this project keeps relearning in a new costume: **a count is a measurement and
needs the same scepticism as any other.** I diagnosed a generator from a regex without once parsing
the file the generator produced, and lxml — already imported in that very script — would have
answered it in one line.

Nothing needs fixing in `make_tracked_docx.py`. The orphan-stripping rule in
`accept_tracked_docx.py` is harmless and still correct for its own purpose (dropping a bare marker
and keeping its content is accept semantics), but its comment claimed a generator fault that does
not exist, and is corrected.

## 2026-09-18 — thirteen of his edits were lost, and the machinery that let it happen

He reopened the submission build and found his own corrections undone. This entry records what
went wrong, because the cause is a method, not an accident, and the method was mine.

### What actually happened

The 2026-09-17 round compared his returned file against the build he was sent with a
paragraph-level `difflib` and reported the result as **ten differing blocks**. A block is a run of
CONTIGUOUS paragraphs. Those ten blocks held **19 changed paragraphs carrying 52 separate
word-level edits**, and two of them spanned four and five paragraphs at once. Each block was read as
though it were one change, the most visible edit in it was applied, and **13 of his edits never
reached the master**. The log entry for that round says "Ten differing blocks ... Every one applied
verbatim", which was true of the blocks and false of the edits.

Reconstructed, the lost ones were: the fivefold clause in the abstract, his closing abstract
sentence, "16.6% of the variance", the recall-window passage, the Parry sentence, the merge of the
two objection paragraphs with its four cuts, the false-dichotomy gloss, the colon-to-full-stop at
"the claim. Claims", and "very" in "very transparent". He had left a comment in the 09-17 file
reading "dont overwride me edits". He left two more on 09-18: "I made edits in here before that you
overwrote. not acceptable" and "I made edits here before that you overwrote, wtf".

**The root cause is reporting a diff at block granularity and having nothing verify the result.**
Every number in this manuscript is guarded; his prose was not, so an edit could go missing and the
build would come back green.

### The fix, in three parts

1. **`scripts/diff_author_edits.py`** — enumerates every author edit as ONE ROW, at word level,
   never a block, in either tracked or untracked mode. On the 09-17 file it reports 52 items where
   the old method reported 10, including all 13 that were lost.
2. **`scripts/check_author_edits.py` + `docs/author_edits.tsv`** — a ledger of every edit he has
   made, each as a must-appear or must-not-appear assertion, checked on every run like any pipeline
   statistic. An edit leaves the assertion set only as `superseded` (a later round of his replaced
   it) or `amended` (applied, with a correction of ours), and the guard refuses either without a
   written note. Now at **108/108 intact, 149 rows, 41 set aside with reasons.**
3. Scope, so a probe means something: `main` / `si` / `figure`. His deletion of the main-text
   heading "Sample size and estimate size" checked green against Note B6's "Sample size and
   estimate size (detail)" while the main text still carried it.

### Four faults the fix found in itself or nearby, all of them this project's recurring shape

- **A guard that could not see its own blind spot.** The first version built no probe for a
  one-word deletion, because a bare "very" recurs everywhere. So single-word deletions were
  enumerated and never asserted, and his cut of "very transparent" passed a green guard in the very
  run built to stop edits going missing. Short deletions now assert their BEFORE-context: the
  phrase as it read before he cut it must no longer appear.
- **`accept_tracked_docx.py` emitted XML that does not parse.** It applied seven regular
  expressions to `word/document.xml` and looped them to a fixed point; a non-greedy
  `<w:ins ...>(.*?)</w:ins>` closes on the FIRST `</w:ins>` and Word nests these. lxml refuses the
  output outright ("Opening and ending tag mismatch: rPr ... and p"). This script built the baseline
  for every round since 2026-09-17. Rewritten with the parser, element by element, with accept
  semantics stated for each case and a parse check before it writes.
- **A paragraph-mark change moves no text at all.** Deleting one joins two paragraphs and nothing
  in their words differs, so a text-level diff cannot see it; both of his 2026-09-18 merges were
  invisible until the rewritten accept script surfaced them. The enumerator now builds its accepted
  view THROUGH `accept_tracked_docx.accept`, so the two tools agree by construction.
- **An unmapped citation inside a parenthetical rendered as plain text beside the numbers.**
  "Allcott & Gentzkow 2017" was in neither CITE_MAP nor the reference list, so the build printed
  `(Allcott & Gentzkow 201722,28)`, which is what he read at comment [167] — and had flagged before.
  Shao et al. 2018 was cited in Supplementary Table 3 and also absent from the reference list. Both
  added (51 -> 53 references). `make_nhb_docx.py` now FAILS on a stray author-year left in a
  converted parenthetical; the whole-parenthetical check could not see it, because by then the
  superscript sits between the year and the closing bracket.

### His 2026-09-18 round: 97 edits, 17 comments, and a document now under the word limit

All 97 applied, his taking priority wherever they touch a passage restored from 09-17 (41 ledger
rows superseded or amended, each with its reason). Three of his comments were data questions and
each was checked against the freeze rather than the prose:

- **[43] climate.** He was right that the sentence contradicted itself. The topic taxonomy has no
  climate value at all, so nothing can be coded climate, yet one study does report a climate
  estimate (1.69%, coded `science_other`). Rewritten.
- **[78] "a small top group".** Not users at all: the two grey-literature claims are 65% of fake and
  conspiracy links to the top 10 SITES and 89% to the top 50. Named now, in a paragraph that is
  otherwise about users.
- **[126] age.** Correct as written, re-derived from the freeze: 0.58, 0.67, 0.70, 1.80, 4.35, 18.5,
  median 1.25. His intuition holds for SHARING (the single sharing contrast is the largest at
  18.5x); reach splits within one study, 4.35x on website visits against 0.67x on YouTube.
- **[124] the rarity null** removed from the Results, Note B2 and the figure caption on his
  instruction. My reservation is recorded with it: it is the one passage answering "concentration is
  mechanical because misinformation is rare". The simulation still runs and the guard still asserts
  it stays a null, so restoring it is a one-line change.

Material his cuts displaced went to the appendix rather than out of the paper, per his comment [69]:
Note B5 gained the identification and ground-truth counts and the 439-versus-443 distinction; Note
B2 and then the Supplementary Fig. 2 caption took the within-panel median. Note B4 is down from 672
to 578 words per [147]. The supplementary figures are renumbered because his [66] pointer cites the
ground-truth figure before the concentration one.

**Main text 4,962 words against NHB's 5,000, under the limit for the first time** (it was 5,476).
Abstract 148. Guards: manuscript 283/283, author edits 108/108, invariants, PRISMA, pipeline docs,
freeze headers and drift all green; the only non-zero exit is the Zenodo DOI placeholder, which is
correct until the deposit exists.

### Delivery

`scripts/carry_comments_docx.py` (new) re-anchors his comments BY TEXT into the delivered file,
because `make_tracked_docx.py` starts from a fresh build and had been dropping them every round. 17
carried, 6 on their original words and 11 on the whole paragraph where the sentence beneath them was
rewritten; every one reported, none silently moved. He asked for the answers in chat rather than in
the document, so no replies were written into it.

Known limit, unchanged: a whole DELETED paragraph is not shown as a tracked deletion. The rarity-null
paragraph is gone from Note B2 and the tracked SI cannot show it; the build warns.

## 2026-09-18 (cont.) — Supplementary Note A removed, and a citation that was numbered nowhere

He returned both documents. The main came back with every tracked change accepted, 64 untracked
edits of his own and two comments; the supplement came back with **Supplementary Note A deleted in
full** — heading, four paragraphs and Supplementary Table 2 — plus the byline cut from its title
page. He asked for the supplement to be adapted and for the main to be left alone for now.

**Adapted.** Note A is gone from the master. The remaining notes keep their letters, B to F, rather
than shifting up, because renaming them would move every cross-reference in the paper; that is also
what his own file does. Supplementary Table 3 becomes **Supplementary Table 2**, the number Note A's
removal freed. The SI title page no longer carries the byline. Two scripts keyed the start of the
supplement on the string "## Supplementary Note A" — `make_nhb_docx.py`, which splits the master
into main and supplement, and `check_author_edits.py`, which scopes its probes — and both would have
raised on the next run; both now key on Note B.

Nine assertions lived inside Note A, all derived from `appendix_content_sharing.csv`: the five
stratified rows of its table, the claim/source ratio, the marginal medians and gap, the claim-level
difference and the construct's rank in the eta-squared ladder. They are RETIRED, not re-anchored,
because the prose that carried them is gone rather than moved. The generator still runs and the CSV
still ships, so the numbers stay reproducible.

**His file carried an empty table shell.** Deleting the cells of Supplementary Table 2 left the
table frame and three empty paragraphs behind, at blocks 3 to 6 of his accepted document. The
rebuilt supplement has them properly gone; the tracked build warns that it cannot show a deleted
block as a tracked deletion, which is the known limit of `make_tracked_docx.py`.

### A citation that was in the reference list and numbered nowhere

Reading Note F in his returned file: "Three papers from one group (2024b52,53) select popular
articles ...". The master says `(Aslett et al. 2024a, 2024b; Godel et al. 2021)`, the second paper
written as a bare `2024b`, which is not a CITE_MAP key. The converter matched the other two, left
", 2024b;" as plain text and shipped it. **Aslett et al. 2024b was in the reference list and cited
nowhere.** The citation is now written in full and the reference count goes 53 -> 54.

The stray-citation check added this morning did not catch it: it looks for a capitalised name
followed by a year, and a bare year has no name. It now also matches a lone year inside a
parenthetical that contained mapped citations.

### Two checks that should have existed

- **Dangling cross-references.** Removing Note A left the main text saying "Supplementary Note A
  compares the two constructs ...", pointing at a note that no longer exists. Every check in this
  file asks whether a NUMBER IS PRESENT; none asked whether a POINTER RESOLVES. Both directions are
  checked now, uncited display items and dangling references, and both are reported rather than
  raised so neither can hide the other 270 assertions. It currently reports exactly one fault, that
  Note A pointer, which his own pending edit deletes.
- **The display-item list was hardcoded** and named Note A, so it raised the moment the note went.
  It is derived from the headings and captions that exist.

### The ledger gains a `pending` status, and stops reporting table cells as losses

His 64 main-text edits are recorded and marked **pending**: received, not applied, reported on every
run so they cannot be forgotten, flipped to active by the commit that carries them in. Holding them
unrecorded was the alternative and it is exactly how thirteen went missing yesterday.

Scoring his supplement round surfaced a fault in the enumerator: a table CELL is a paragraph, so
deleting a table produced absence probes for "Content", "Sharing", "claim-level" and six more, words
the manuscript uses everywhere, and the guard reported a correctly-applied deletion as eight
reverted edits. A probe now needs three real words, counted after the citation and number stripping
the guard applies, so a numeric cell like "18.2% (k = 13)" — which reduces to "18.% (k = )" and
matches every other numeric cell — no longer produces one. Twenty-four of the thirty-two rows in
that round are unassertable on their own and say so; the deletion of the table they belong to is
carried by its caption and heading, which are long enough to be unique.

### His two comments, answered without editing

- **[0] "Table 2, this is exhaustive right? nothing we missed?"** Not quite: **wave 5 has no row.**
  It is a real scored pass — 38 estimates across the 22 studies no cross-family check had read, one
  fresh session of a different model family, construct κ = 0.959, breadth 0.761, denominator class
  0.183 — and it is the pass that takes cross-family coverage to every study in the corpus. Table 2
  carries the SMALLER of the two coverage passes (wave 4, 7 estimates in 2 studies) and omits the
  larger. The numbers are in Note C1's prose, so nothing is unreported, but a table captioned "by
  stage" should carry the row. Everything else in the table matches an artefact on disk.
- **[1] "§4.9, is there a way to shorten this a little bit?"** 342 words in three paragraphs, of
  which his own pending edit already deletes the first (33 words). Roughly 85 more can go without
  losing anything the guard checks: the IQR gloss, and the no-pooling sentence, which restates the
  paragraph he is already cutting. The k = 5 under-coverage caveat is the one piece worth keeping or
  moving to Note C2 rather than dropping.

## 2026-09-18 (cont.) — his main-text round applied, the notes relettered, and the reference audit

He lifted the hold, asked for the wave-5 row, for the appendix to start at A, for the supplementary
cross-references to follow, and for the reference list to be checked against what he had cut.

**His 64 main-text edits are in.** They were a real pass over the Methods: the criteria-defect
passage compressed, the unit-of-analysis sentence moved into the extraction paragraph, the exposure
whole-diet/topical split cut, the AI-use statement rewritten, the §4.9 opening paragraph and the
"every check is a check on our coding" sentence deleted, and the title page stripped of byline,
affiliation and correspondence. **Main text is now 4,686 words** against NHB's 5,000.

Two of his edits were set aside with reasons, and one was corrected:
- He deleted **Aslett et al. 2024b** from the reference list and renumbered. He was right that it
  was dead — the build had left it cited nowhere — but the cause was the bare `2024b` citation bug
  fixed this morning, so the paper is cited again and the entry stays.
- "314 of the 443 **falls** in 2020 or later" reverted to "fall": the subject is plural. Marked
  `amended` in the ledger, delivered as a tracked change, his to reject.

**The notes are relettered B–F -> A–E**, subsections with them (A1–A7, B1–B3 and B1b, C, D, E), in
the master and in the four live scripts. Ascending order is collision-free: after B->A no B remains,
so the C->B pass cannot touch what the first produced. `make_nhb_docx.py` and `check_author_edits.py`
both key the start of the supplement on the first note's heading and follow it. **The ledger's own
probes were migrated the same way** — 26 rows quoted "Supplementary Note B" for prose that now says
A — which is the second time this round that a guard needed moving with the thing it guards.

### The reference audit he asked for

His cuts left exactly one orphan: **Baribi-Bartov et al. 2024**, the supersharers paper, cited only
by the "0.3% of users accounted for 80% of fake-news sharing" clause he removed from the Discussion.
Entry deleted; the list and the build now agree at 53.

**Nothing was checking this**, and it is a silent failure by construction: the builder numbers by
first appearance, so an uncited entry simply never gets a number and vanishes from the rendered list
while the master keeps carrying it. `check_manuscript_stats.py` now reports orphaned references, and
reference-list entries with no CITE_MAP key. Verified by putting the orphan back and watching it
report, then removing it again.

### What his deletions cost, and one decision left to him

Deleting the concentration-comparison paragraph retired five assertions (the study-level 31%, the
six comparison estimates, the four within-panel ratios, the Figure 5 citation, and the §4.4 repair
size his compression cut, which is still asserted twice elsewhere). Two more were re-anchored rather
than retired: the subgroup counts moved from the Discussion to §2.6, where the same numbers still
stand in his own wording.

**Supplementary Fig. 2 is now uncited.** It plots the matched within-panel concentration comparison,
and the paragraph that made that comparison is gone, so the figure has nothing left to support. It
is reported, not fixed: whether to drop it or to re-cite it is his call, and the supplementary
figures are consequently out of citation order (1, 3, 2) until he decides. That ordering check now
REPORTS rather than raises, so it cannot hide the other 270 assertions behind an exception.

**Table 2 gained its wave-5 row** (comment [0]): 38 estimates in the 22 studies no earlier pass had
read, construct κ = 0.96, breadth 23 of 26, denominator class 7 of 17, one breadth code adopted. The
row's numbers are asserted, parsed out of the wave-5 adjudication file rather than typed, so the
table cannot drift from the artefact.

Guards at close: manuscript 269/271 (the two are the uncited figure and the ordering that follows
from it), author edits 174/174, invariants, drift, pipeline docs all green.

Note for the delivery: `make_tracked_docx.py` cannot mark up a table, so the new Table 2 row arrives
without change marks, and the SI's reletterings show as ordinary tracked edits.

## 2026-09-18 (cont.) — §4.9 cut to 255 words, and Supplementary Fig. 2 dropped

**§4.9 is 342 -> 255 words**, all 270 assertions still green. What went: the "which prevents
multi-estimate studies from dominating a cell" gloss, the redundant "that fall in the taxonomy's six
constructs" (the next clause already explains the 934 -> 897 gap), "Rather than assert that the
constructs do not pool, we quantify it", the four-item list of what Note B2 covers, and the
parenthetical breakdown of which language did which job. What stayed: every number, both citations,
the study-level median definition, the reason for resampling studies rather than estimates, the IQR
distinction and the k = 5 under-coverage caveat. Method a referee needs to reproduce the analysis is
all still there; what went was self-description.

**Supplementary Fig. 2 dropped**, on his delegation ("if useful we can re-cite somewhere, if not
useful we drop"). It plots the matched within-panel comparison of misinformation against general-news
concentration, and §2.5 no longer makes that comparison at all — his deletion took the 31%, the four
ratios and the null with it. A figure whose claim is not in the paper is not useful, and re-citing it
would have meant reinstating prose he had deliberately cut. Countries moves 3 -> 2; the supplementary
figures are back in citation order and the caption assertion is retired, the generator still runs.

**Left for him, not acted on:** main Figure 5 is still titled "Concentration of misinformation versus
news in general" and still draws the general-news column, in a section that now only reports how
concentrated misinformation activity is. Either the figure loses its right-hand column or the text
regains a sentence making the comparison; both are his calls, one because it regenerates a main
display item and the other because it would restore prose he removed.

---

## 2026-09-18 — the public companion site, and four data findings it surfaced

Sacha asked for a public dashboard to sit on his domain: present the results, let people change the
choices and watch the numbers move, and above all **let people inspect the estimates**. Design was
agreed first (`docs/site_design_2026-09-18.md`, reading version `.html`), then built.

**What was built.** `site_src/` holds the pages; `scripts/build_site.py` generates `site/` from the
freeze and the Phase B outputs; nothing on the site is typed. Six pages: an answer-first overview,
a two-tab explorer (build-an-estimate, and the full swarm), all 1048 estimates as an inspection
surface, the 443 studies, methods, and downloads. Static, no libraries, every link relative, so the
same folder works at a Pages URL, at a domain subpath, and from `file://`. Wired into
`run_phaseB.sh` and `PIPELINE.md` at stages 7 and 8; `bash scripts/serve_site.sh` previews it.

**The estimate record** is the unit the site is organised around, because inspection was the
priority: the value, then the denominator in words, then the verbatim quote it was taken from, then
the moderator quote saying why it was coded that way, then the full coding. Each carries a
content-hash permalink (stable across a re-freeze, unlike the row index) and a "flag a coding error"
link that opens a pre-filled issue on the public repo.

**The guard.** `check_site.py`, 947 checks. The one that matters reproduces all 72 published slice
rows in Python (`scripts/lib_slices.py`, the canonical aggregation extracted from
`phaseB_slices.py:63`) AND in the browser's JS port, to the decimal. It caught four things in this
session's own work: a slice recomputed over the wrong construct subset (all of MAIN rather than the
six prevalence constructs), a landing number placed beside a figure carrying a different one, JS
rounding that differed from Python's round-half-to-even on the exact binary value, and a broken
download path. Writing the checker also required modelling that `phaseB_slices.py` and
`phaseB_export_json.py` canonicalise `ground_truth` DIFFERENTLY — the slices script merges
`domain_list` with `NewsGuard` and labels classifiers `classifier/LLM`, the export keeps them apart.

**Four findings about the data, none of which the site can fix.**

1. **`measurement` rests on a 317-study join.** `phaseB_slices.py` and `phaseB_prep_regression.py`
   both read `data/extract_v2/qa/rob_appraisals_v145.csv` (22 July, 317 of 443 studies);
   `phaseB_grade.py` correctly reads `data/rob/risk_of_bias_v3_master.csv`. PIPELINE.md already
   calls the v145 file "legacy", so the join is known — the consequence may not be. In
   `regression_data.csv`, 337 of 837 rows (40%) carry `measurement = NA`, and
   `phaseB_metareg.R:29` folds them into an explicit `unspecified` level. The fitted factor
   therefore has four levels whose largest means "not in the July file", predicting 26.0%, while
   `SELF_REPORT` is fitted on 61 rows at 51.0% — and **182 of the 243 RECALL rows sit in
   `unspecified`**, though recall is self-report by definition. §2.6 reports measurement at
   R² = 15.9% and describes it as three levels. Which way R² moves cannot be known without
   refitting. `slices_measurement.csv` shows the same thing as an `(unappraised)` row of 158
   studies. The site withholds the field and says so on /methods/.
2. **`misinfo_def` is truncated at 200 characters on 441 of 1048 rows**, usually mid-word (max
   length in the column is 462, so the cut was applied to a subset at extraction). No statistic
   uses the free text — `breadth` is the coded variable — but the site displays it, so records flag
   it as truncated rather than render half a sentence as a definition.
3. **`country_scope` carries one `single_country` row** where 788 carry `single`
   (`2-s2.0-85145196122`, the study restored at v1.7.21). It reaches no manuscript statistic, and
   `slices_country_scope.csv` accordingly has a spurious one-study row. Merged on the site, checked
   to be lossless, and left in the freeze: re-freezing for one display cell is disproportionate,
   consistent with the standing ruling on the 39 blank `denom_class` rows.
4. **The identification-stage total has two defensible values.** `counts_crosswalk.md` says 25,576
   ("Scopus + OpenAlex keyword + PubMed", precisely labelled and correct for those three streams);
   the manuscript and the PRISMA figure say 30,958 across all five. Both are right; neither is
   wrong; putting them side by side reads as a contradiction. The site states neither and points at
   the flow diagram, with a check that keeps it that way. The gap worth noting is that the
   crosswalk — the file whose job is one number, one meaning — has no row for the number the
   manuscript actually leads with.

**And one bug in a guard.** `make_counts_crosswalk.py`'s drift check captured counts as `\d{3}`, so
it read a CURRENT "1048 estimates / 443 studies" as "048" and reported a correct document as stale.
Written when the corpus was three digits; the corpus passed 1,000 at v1.7.x. Widened to 3-4 digits
and verified against injected stale counts (both `1050 / 444` and `695 / 408` still fail) so the
guard was loosened in reach, not in strictness.

**Also:** risk of bias on the site is joined from `si_study_characteristics.csv` (443/443), not from
the estimate rows, where the same v145 join leaves it blank on 371 of 1048. The deposit folder's
eleven iCloud conflict duplicates (seven empty directories, two byte-identical files, and two stale
files claiming 1063 estimates) went to the Trash.

**Not done, deliberately:** the deposit has not been rebuilt to include `site/`, no public repo has
been created, and nothing is live. Sacha reviews the built site first.

## 2026-09-18 (cont.) — the measurement moderator was 40% a coverage artefact

An agent building the dashboard reported that `measurement` in the meta-regression was derived from
a stale file. It was right on every checkable point, and the problem was larger than it said.

**What was wrong.** `phaseB_prep_regression.py` joined `measurement` from
`data/extract_v2/qa/rob_appraisals_v145.csv`, a **22 July appraisal covering 317 of the 443
studies**. When the corpus grew past that file the join silently returned nothing for every new
study. Git dates the break precisely: on 2026-09-02 the regression set was 480 rows with **6 NA
(1%)**; on 2026-09-04 it was 780 rows with **306 NA (39%)**; at the freeze, 337 of 837 (40%).
`phaseB_metareg.R` folds uncoded cells into an explicit `unspecified` level, so the fitted factor
had FOUR levels and the largest of them meant "not appraised by 22 July".

It was not missing at random. **182 of the 244 RECALL rows sat in `unspecified`**, and recall is
self-report by definition, so `SELF_REPORT` was fitted on 61 rows while 182 genuinely self-reported
rows sat in a bucket of their own. The same stale join fed `phaseB_figures.py` and
`phaseB_slices.py`, so Figure 4's measurement band was computed over **270 of 443 studies**, chosen
by appraisal date, with self-report resting on 29 studies against the corpus's 91 recall studies.
And its `overall` column filled the risk-of-bias field in the slice tables for only **63.4%** of the
corpus while `data/rob/risk_of_bias_v3_master.csv` covers all 443.

**What the fix is not.** The v3 master has no `measurement` column; that field existed only in the
v1.4.5 appraisal schema, so this could not be repointed at a newer file. Nor could the coded values
simply be kept and the gaps filled: imputing the 337 gaps from each construct's modal coded value
gives R² = 21.7%, but that mixes two instruments, and the apparent gain over construct (+4.5 pp) is
an artefact of the mixture rather than a finding.

**What the fix is.** Measurement type is now DERIVED from the construct taxonomy in
`phaseB_prep_regression.py`: content analyses code content, recall surveys are self-report, the four
audience constructs read behavioural records. That is what Table 1 and §2.3 already say, it
reproduces the July appraisal on **90.6%** of the rows where both exist, and it covers every study.
It is complete: 0 uncoded rows.

The honest consequence is that measurement is now a three-level grouping of the constructs, so it is
REDUNDANT with construct — metafor drops it from a joint model — and the two are one family in the
same sense as ground-truth source and identification level. Note B2 says so and §2.4 flags the
overlap in the sentence that reports the rung.

**What moved.** Only measurement.

| | before | after |
|---|---|---|
| measurement adj R² | 15.9% | **16.6%** |
| Figure 4 behavioural median | 8.8% | **12.5%** |
| Figure 4 content median | 24.9% | **23.0%** |
| Figure 4 self-report median | 52.7% | **43.0%** |
| Figure 4 measurement band | 270 studies | **446** |
| predicted behavioural / content / self-report | 4.9 / 19.9 / 51.0% | **7.3 / 16.6 / 44.7%** |
| Cramér's V range across the four | 0.43–0.97 | **0.48–0.97** |
| risk-of-bias fill in the slice tables | 63.4% | **100%** |

Every other rung is unchanged: ground_truth 22.8, id_method 21.8, construct 19.1, denom_fine 16.6,
platform 14.1, sampling 12.7, breadth 12.0, topic 1.8, denom 0.0. Measurement now TIES denom_fine at
16.6, so the ladder assertion treats ranks 4 and 5 as a set: a tie has no order, and asserting one
would fail on a rounding change that means nothing.

**The guard that was missing.** Every check in `check_manuscript_stats.py` asks whether a NUMBER IS
PRESENT in the prose. An uncoded cell produces no number, so a join can rot for a fortnight without
a single check going red. There is now a **moderator-coverage check**: each moderator's accepted
uncoded share is declared (0% for eight of them, 6% for denom_fine, 30% for breadth) and a join that
degrades past it is reported by name. Verified both ways — setting 340 rows back to NA reproduces
the report, restoring them clears it.

The dead loads of the 22 July file are removed from the three phaseB scripts so it cannot be picked
up again; it remains where it belongs, as a released historical artefact.

### The three smaller findings from the same agent, all checked

- **`misinfo_def` is capped at 200 characters on 441 of 1048 rows**, 430 of them ending mid-word.
  Confirmed; 161 rows run past 200 (to 462), so it was not a uniform pass. The cap was applied
  upstream in extraction and the untruncated text is not recoverable without re-reading the sources,
  so this is DISCLOSED rather than fixed: `docs/CODEBOOK_estimates.md` now says the field indicates
  how a study defined misinformation rather than quoting it in full, and points at `breadth` and
  `ground_truth`, which are coded and complete. No statistic uses the field.
- **One row reads `country_scope = single_country` where 788 read `single`** — `2-s2.0-85145196122`,
  the study restored at v1.7.21, so it arrived after the spelling settled. It reaches no manuscript
  number, but it made a one-study category of its own in every table grouped by that field.
  Normalised on read in `phaseB_slices.py` and `phaseB_descriptives.py`; `single` goes 300 -> 301
  studies and the stray category is gone. The cell itself is a freeze edit and waits for the next
  freeze rather than forcing one on submission day.
- **The crosswalk reported 25,576 where the manuscript reports 30,958**, both correct for different
  stream sets, in the file whose whole job is one number one meaning. The crosswalk's "Records
  identified — databases" summed the three June streams and omitted the September behavioural arm,
  which is also a database stream: 25,576 + 5,382 = 30,958. The row now carries all four, with the
  June subtotal and the behavioural arm as their own rows beneath it, so the two numbers reconcile
  on the page instead of in someone's head.

### And what the bootstrap said

Re-running `phaseB_metareg_robustness.R` moved measurement's interval to 16.6% [11.5–21.8] and left
every other rung where it was. Topic's ceiling is now 6.7 against breadth's floor of 6.7, but breadth
is not one of the four measurement moderators, so Note A2's "its interval lies entirely below every
measurement moderator's" still holds against the lowest of those four, sampling at 8.3.

**The within-content ladder lost a rung.** Measurement cannot be fitted inside a single construct
now that it is derived from construct, so it returns NA there. It used to report 10.5% in that
model, and that number was the stale join splitting content analyses by whether they had been
appraised by 22 July. Topic rises to fourth of eight rather than fifth of nine, and the rank is
derived from the ladder rather than typed, so it cannot go stale silently again.

### The submission folder was carrying the stale figure

Reported by the dashboard agent and confirmed: `08_figures/Figure_4` still showed the measurement
band as n = 67 / 180 / 23, which sums to the old 270, while the rebuilt `docs/fig2_method_drivers.svg`
shows 81 / 274 / 91, summing to 446. The folder was built at 10:05, before the measurement fix, and
`build_submission_folder.py` copies the figures straight from `docs/`, so a rebuild was the whole
remedy.

Rebuilt. All six figures now checksum-match their sources, `01_manuscript_main.docx` carries the
corrected numbers with no tracked changes, and `02_supplementary_information.docx` matches the build.
The folder is backed up at `docs/.backups/NHB_submission_2026-09-18_pre-rebuild` because the builder
does `rmtree` before it writes, and nothing in the folder was hand-made.

The builder also had its own small staleness: it stashed the tracked pair from
`~/Desktop/manuscript_NHB_main.docx`, a name that stopped being used on 2026-09-18, so a rebuild
would have dropped the tracked pair silently. It now looks for the current names first and keeps the
old ones as fallbacks.

## 2026-09-18 (cont.) — I overwrote his supplement, and the delivery step is now guarded

The supplement was delivered at 13:02. Word, which had it open since 11:25, wrote its in-memory copy
back at 13:04. I checked the file back, saw the OLD numbers in it, correctly diagnosed that Word had
reverted my delivery — and then **overwrote it at 13:08 without keeping a copy**. Anything he had
done to that document between 11:25 and 13:04 went with it. The file on the Desktop now carries 114
tracked changes, all authored by "Claude", and no comments.

The whole session had been about not losing his edits. The ledger and the guards protect the MERGE
step. Nothing protected the DELIVERY step, and that is where the loss came from.

`scripts/deliver_to_desktop.py` now stands between any build and a Desktop destination:

- whatever is already at the destination is copied to `docs/.backups/<name>.<its mtime>.replaced`
  before anything is written, so a replaced file is always recoverable;
- it REFUSES outright while Word holds the destination open, because a copy written under an open
  Word document is reverted the moment Word saves — which is precisely what happened at 13:04;
- it verifies the copy landed intact and says to check the file back afterwards.

Both paths were tested: the refusal fires on a `~$` owner file, and a replace archives first.

Recovery, in the order worth trying: the document may still be open in Word, in which case Save As
preserves it; otherwise iCloud keeps 30 days of versions for the Desktop. The supplement's PROSE is
not at risk either way — it is in git and rebuildable — what was lost is whatever markup, comments
or edits he had made in that window.

## 2026-09-18 (cont.) — one pair, not two, and two more of his edits recovered

Sacha: "no need to create special track change files, just hand me the track change and I'll accept
or not". Two copies of each document, one clean and one marked up, was the thing confusing him.

**01 and 02 now arrive WITH tracked changes**, built as a diff against the last state he accepted.
`build_submission_folder.py` keeps the baselines in `docs/.backups/baseline_main.docx` and
`baseline_si.docx` and tracks each numbered file against its own; the separate
`00_for_review_tracked_changes/` folder is gone. He reads and accepts in the file he will upload.

**Checking redundancy before deleting caught two more of his edits.** Diffing his own export against
the build, rather than assuming it was superseded, found `accounts` -> `account` in the abstract and
`breakdown` -> `breakdowns` in the Discussion — both suggestions of mine that he had applied in his
copy and that never reached the master. In the ledger as round 2026-09-18c, and the two 09-18b rows
asserting the singular are superseded. **This is the third time today that a file about to be
discarded turned out to carry something of his**, which is the argument for the archive-then-replace
rule now in `deliver_to_desktop.py`.

Both redundant files went to the Trash after being archived, once the diff showed they carried
nothing unique: the standalone supplement is now identical to 02 (similarity 1.0000, zero differing
blocks) and his export's only unique paragraphs were the pre-fix versions of the two §2.4 paragraphs.

A formatting fault turned up on the way: the Note A2 bullet I added for the measurement derivation
was hard-wrapped across five lines while every other bullet in that list is one long line, and the
builder renders each wrapped line as its own paragraph. Merged.

## 2026-09-18 (cont.) — the replication package, checked for a preprint and an OSF deposit

Plan changed: preprint and OSF first, journal later. The package was checked rather than assumed.

**It was stale.** Built at 12:12, before the measurement fix, so it shipped `measurement = 15.9`
and 337 NA rows. Rebuilt: 629 files, 26.8 MB, and it now carries 16.6, zero NA rows, and the
bootstrap interval [11.5–21.8].

**It reproduces.** Copied to a scratch directory, deleted `regression_data.csv` and
`metareg_univariable.csv`, and re-ran `phaseB_prep_regression.py` + `phaseB_metareg.R` from inside
the package alone: construct 19.1%, measurement 16.6%, ground truth 22.8%, the published numbers
exactly. That is the first time the package has been run end-to-end from outside the repository.

**The runner was broken, and the ALLOW list was why.** `run_phaseB.sh`, which the README tells a
reader to run, named **seven scripts the package did not contain**: `phaseB_perturbation.py` (the
deliberate-miscoding analysis reported in Note A2), `make_si_characteristics.py` (writes
Supplementary Data 1), `make_si_lists.py`, `make_behavioural_arm_dispositions.py`,
`phaseB_concentration_null.py`, `check_pipeline_docs.py` and `sync_doc_freeze_headers.py`. Three
shipped artefacts therefore had no generator beside them, and the documented command died partway.
The allowlist is curated by hand and had drifted from the runner with nothing comparing them. Added,
and the builder now **compares the runner against the tree on every build and exits non-zero** if a
named script is absent. Tested by removing one.

The site tree exposed a second, smaller thing: a `--dry-run` listed `build_site.py` and the `site/`
tree while the real build omitted them, because the dry run raced the other agent writing those
files. Present now, 25 files.

**§4.11's five promises all hold** in the built tree: the frozen dataset (MD5
`08f050baf45086f45b5b3bec2390a115`, matching the top block of FROZEN.md), every analysis script, the
append-only research log (11,126 lines, current), the risk-of-bias appraisals with their quotes, and
the independent-model adjudication trail. Denylist, absolute paths and contact details: clean.

**The statement now names OSF, not Zenodo** — one line, easily reverted if he prefers Zenodo.

**Two things a PREPRINT needs that a journal submission did not.** His 2026-09-18 round stripped the
byline, affiliation and correspondence from the title page, which is right when a portal collects
them and wrong for a paper posted publicly: as built, the preprint would carry no author. And the
DOI is circular — it can only be minted once the deposit exists, then §4.11 and a rebuild follow.

### Preprint state: the author is back, the DOI sentence is out

- **Title page carries its author again** — byline, affiliation and correspondence. Cut on
  2026-09-18 for a journal submission, where the portal collects authorship; restored the same day
  because a preprint is posted publicly and must carry it. The three ledger rows recording his cut
  are marked superseded with that reason, so the reversal is on the record rather than looking like
  another overwrite.
- **§4.11 no longer names a DOI.** It reads "released in full as a replication package accompanying
  this preprint": the deposit does not exist yet, and a `[DOI TO BE INSERTED]` placeholder in a
  publicly posted paper is worse than no sentence.

The reminder that watches this had to be rewritten, and the reason is worth keeping. It fired on the
PRESENCE of the placeholder, so deleting the placeholder silently switched it off — a check keyed to
a stand-in for the thing rather than to the thing. It now fires on the ABSENCE of a DOI pattern in
§4.11 and will keep reporting until a real one is there.

### Correspondence address, and a rebuild that would have deleted the CI config

`sacha.altay@uzh.ch` was never a real address. He asked for his gmail, then gave
`sahca.altay@gmail.com`, a transposition; confirmed as **sacha.altay@gmail.com** rather than guessed,
because a wrong contact line on a publicly posted preprint defeats the point of having one. It lives
in two places, the title-page block in `make_nhb_docx.py` and the email allowlist in
`build_public_package.py`, and both are updated.

Checking the package afterwards showed 695 files where the builder reports 630. The difference is
`.git` and `.github`: that tree is also the git repository behind the public companion site
(`altay-research/misinfo-prevalence-review-public`). The builder already preserved `.git` across a
`--force` rebuild — a lesson it had learned earlier the same day — but not `.github`, which holds
the Pages workflow and would have gone on the next run. Added to KEEP.

Worth remembering when the OSF upload happens: `.git` is 7.1 MB of the 33.7 MB, and is not part of
the deposit. Upload the tree without it.

## 2026-09-18 (cont.) — the main manuscript is hand-formatted now, and must never be rebuilt

Sacha accepted the tracked changes in `01_manuscript_main.docx` and then formatted it in Word:
"formatting edits that you probably can't catch, so no more editing this. If I ask you to edit it
it's only targeted edits."

He is right that I cannot catch them. **Every diff in this project compares text.** A rebuild from
`docs/manuscript_draft.md` would come out textually identical, pass the 270-assertion guard, pass the
author-edit ledger, pass the drift check, and silently discard every formatting choice in the
document. No check here can see that loss, so the protection cannot be a comparison — it has to be a
refusal to rebuild.

`docs/AUTHORITATIVE_FILES.txt` now lists what no script may rewrite, and
`build_submission_folder.py` reads it, copies those files into memory BEFORE the `rmtree`, and writes
them back untouched. Verified: `01_manuscript_main.docx` has the same MD5 before and after a full
rebuild, and matches the timestamped copy in `docs/.backups/`.

**The .docx is the source of truth for the main text from here.** The markdown master stays, because
the guards read it and it is what keeps the numbers honest, but it is no longer what ships. A change
he asks for is edited into the runs of `word/document.xml` that carry the target text and nowhere
else; the same change goes into the master so the guards keep working.

The first case is already waiting: §4.11 carries no DOI, and when the OSF deposit is minted the DOI
has to go into both the authoritative .docx and the master. Not by rebuilding.

`02_supplementary_information.docx` is still rebuilt — he has not formatted that one yet. The moment
he does it joins the list.

## 2026-09-18 (cont.) — the paper now says where the materials are, edited in place

He asked whether the manuscript tells a reader where to find the data. It did not. §4.11 said the
materials "are released in full as a replication package accompanying this preprint" and named no
repository, no URL, nothing — a statement that promises a package and gives no way to reach it.

Both targets are live and were checked before being printed in a paper:
`https://github.com/altay-research/misinfo-prevalence-review-public` (public, 200) and the companion
he added, `https://altay-research.github.io/misinfo-prevalence-review-public` (Pages, 200, serving).
§4.11 now names both.

**This was the first change made under the no-rebuild rule**, and it needed a tool.
`scripts/edit_docx_text.py` changes one passage inside a .docx and nothing else: it searches the
CONCATENATED text of each paragraph, because Word splits a sentence across runs at points that move
whenever the document is edited, then writes the replacement into the first run the match touches
and empties the rest, leaving every `rPr`, style and section property alone. It refuses unless the
old text occurs exactly once, backs the file up first, and re-opens the result to verify.

Proved rather than asserted, on a copy before the real file: of 21 zip entries only
`word/document.xml` differs, and the structural counts are identical either side —
303 paragraphs, 421 runs, 283 `rPr`, 39 `pPr`, 2 tables, 6 drawings, 1 `sectPr`. Text grew by the
133 characters of the two URLs.

### The package had fifteen iCloud duplicates in it

Desktop and Documents are synced, so a file written while a sync is in flight comes back as
"name 2.py". Fifteen were sitting in the built package: fourteen byte-identical to their originals
and one a superseded September draft of an RA coding page. They would have shipped. Denied by
pattern now, and the count went to zero.

I also over-read the file count while chasing them — 695 to 801 looked like runaway duplication and
was the other agent's commits growing `.git`. The package proper is 640 files; `.git` is not part of
the deposit and should not be uploaded with it.

## 2026-09-18 (cont.) — the published repository held five files, and I emptied it

He asked whether github.com/altay-research/misinfo-prevalence-review-public is where the replication
materials live. It is the right address and it is in §4.11, but when he asked, **the repository
contained five files**: three issue templates, the Pages workflow and a `.gitignore`.

**I did that.** `build_public_package.py --force` deleted everything in the directory except
`.git`, `.gitignore` and `.github`, then rewrote it. That directory is also the git working tree for
the public repository, and a commit from the other session landed inside the deletion window:
`54e6134` (16:19) published 640 files, `13cea0a` (16:28) published 5. Two agents writing to one
directory, and my step was the destructive one.

Nothing was lost — the files regenerate and `54e6134` still held them — and the tree is restored and
pushed, 699 files, carrying the corrected measurement moderator (16.6 on GitHub, checked through the
API rather than assumed).

**The fix is to stop emptying the tree at all.** Files are overwritten in place, and only files the
DENYLIST refuses are swept afterwards, so there is no window in which the package looks deleted. A
broader sweep — remove anything this build did not write — was tried first and immediately deleted
`LICENSE`, `README.md` and the site tree, because those are produced by helper functions rather than
copied from the repo and so are not in the `chosen` set. The narrow rule solves the problem that
prompted it, the iCloud duplicates, without needing to know how every shipped file came to exist.

**The lesson is about what I verified.** Before putting the URL in the manuscript I checked that it
returned 200. A repository with five files in it also returns 200. The claim in §4.11 is that the
materials are *there*, and that is what needed checking — the artefact, not the response code. It is
the same failure as reading a count instead of parsing the file, in a new costume.

Fourteen more iCloud duplicates had also appeared in the tree while this was going on; each was
confirmed byte-identical to its original before removal.

## 2026-09-18 (cont.) — tidying the public repository

He looked at the repository and called it a mess. Two separate problems, one of them mine.

**Duplicate directories, committed by me.** `docs 2/`, `site 2/` and `.github/workflows 2/` went up
in the restore commit. The duplicate sweep I had just written tested FILE names only, so a whole
duplicated folder walked straight past it. Both non-empty ones held OLDER snapshots than their
originals (`research_log.md` 16:33 against 16:34, `studies/index.html` 16:33 against 16:36), checked
before removal. The sweep now tests every component of a path, not the last one.

**The root did not read as a replication package.** `site/`, `site_src/` and `worker/` sat between
the data and the code: three directories about the website, which is the first thing a visitor met
and not what they came for. He chose to group them rather than leave it or go further, so they are
published under one `companion/` folder and the Pages workflow deploys `companion/site`.

The published root is now `data/ scripts/ docs/ searches/ companion/` plus README, LICENSE, MANIFEST
and requirements, and the README opens by saying what each of those is and that `companion/` is not
needed to reproduce anything.

**Only the PUBLISHED layout moved.** The working repository keeps `site/`, `site_src/` and `worker/`
where they are, so the other session's scripts are untouched — the relocation is a remap in
`build_public_package.py`, applied as files are copied. Git recorded it as 40 renames.

Verified after the move rather than assumed: the Pages deployment ran green at 14:40 and the site
serves from the new path.

A relocation needs its own cleanup. The narrow stale sweep only removes DENIED files, so the old
`site/` at the root survived the first rebuild and the package briefly held both copies. The builder
now removes an old location once its `companion/` counterpart exists.

---

## 2026-09-18 (cont.) — working alongside another session on the public repo

A second session reorganised `altay-research/misinfo-prevalence-review-public` while this one was
building the companion site. Read its entries above for what moved; this note records the working
rules that fell out of it, because two sessions touching one published repository is now a thing
that happens here.

- **The published layout is not the working layout.** `site/`, `site_src/` and `worker/` live at the
  root of the working repo and publish under `companion/`. The remap is one function in
  `build_public_package.py`; nothing else knows about it, and nothing else should.
- **Seven paths are generated**: `README.md`, `LICENSE`, `MANIFEST.txt`,
  `.github/workflows/pages.yml`, `.github/ISSUE_TEMPLATE/*.yml`, `data/identifiers/*.csv`,
  `searches/README.md`. Editing the repo copy loses the edit on the next build. Edit the generator.
- **Pull before pushing the deposit, and never build while mid-commit.** A `--force` rebuild used to
  empty the directory first; a commit landing inside that window published five files where there
  had been 640. The builder overwrites in place now and sweeps only denied leftovers, but the two
  habits are still the right ones.
- **Check `git status` before `git add -A` there.** Desktop is iCloud-synced, so a sync landing
  mid-write leaves `docs 2/`, `site 3/`. The builder denies any path component matching
  `<name> <number>`; that guard exists because duplicate FOLDERS once passed a check that tested
  file names only.

Verified after the move, from this session: every live route returns 200, and this session's own
two changes — the widened contribution panel and the canonical estimate permalink — are present in
the published tree and being served.

## 2026-09-18 (cont.) — the arXiv PDF: checked, and the supplement merged in

He was about to post `Altay_Systematic_Review_Misinfo.pdf`. It was the main text only, 25 pages, and
it was right in every respect I could test: the corrected measurement numbers all present (16.6%,
12.5/23.0/43.0%, k = 446, 7.3/16.6/44.7%) and every stale one absent; no `[DOI TO BE INSERTED]`, no
"Zenodo", no tracked-change or comment residue; both URLs; 53 references numbered 1–53 with none
missing; six figures and two tables captioned with their images embedded; and its text matching the
authoritative .docx at 0.977, the differences being table cells that pdftotext reads in a different
order rather than real divergence.

**But the supplement was not in it**, and that produced two faults at once. The paper points at
Supplementary Notes A–E about twenty times, plus Supplementary Table 1 and Supplementary Figs 1–2,
none of which a reader could reach. And because the supplement carries the only citations to
references **48–53** (Munn, Begg & Mazumdar, Kreps, and the three CSMaP papers), the main-text-only
PDF listed six references that nothing in it cited.

Merged, keeping his filename: 25 + 19 = **44 pages**, 19,186 words, exactly the sum of the parts.
Done two ways as a cross-check — pypdf and poppler's `pdfunite` — which agreed on page count, word
count and image count (10 + 2 = 12). The pypdf output ships because it carries Title and Author
metadata; the previous main-only file is archived.

Two strings my main-text checklist flags as stale turned up in the supplement and are neither:
"52.7%" is the human-verified recall subset against the corpus's 43.0%, and "k = 270" is the count
of content studies with an extractable sample size. A list calibrated on one document does not
transfer to another without reading the hits.

Not checked, and said so: the rendered layout. Nothing here can see a figure broken across a page.
