# Rules learned from Sacha's review decisions (2026-06-22)

Inferred from the first 9 manually-reviewed values (`data/extract_v2/qa/sacha_review_round1.csv`).
These extend `estimate_selection_rule.md` with the patterns behind Sacha's actual calls.
Applied as PROPOSED calls to the untouched values (flagged "inferred"), for his validation.

## DROP rules (a value is not a usable prevalence/exposure estimate if…)
- **L1 — Pre-selected/curated denominator.** The sample was chosen *to be* misinformation, so
  the "prevalence" is true by construction. *Ex: Humprecht — "450 videos pre-selected for
  misinformation" → drop ("they selected only misinformation, not about the prevalence").*
- **L2 — Modelled / simulated number, not empirical.** *Ex: Alamsyah — fake news "reaches
  0.64 more fractions" in an SI/SNA cascade simulation → drop.*
- **L3 — Construct mismatch (not actually misinformation).** The number measures general
  use/activity, the true-information complement, speed, or a proxy — not misinfo exposure.
  *Ex: Tan — 94.7% "reported COVID WhatsApp use" → drop ("not a direct measure of misinfo
  recall").*
- **L4 — Off-topic / irrelevant paper.** *Ex: Morar (diagnostic radiology) → drop ("looks
  irrelevant").*
- (already in protocol) **secondary citations** of other studies are dropped.

## VALUE-FIDELITY rules (the number must be the misinformation share itself)
- **L5 — Use the misinfo figure, not its complement.** *Ex: Yin — extracted 65.8% but that
  is % TRUE; the misinformation share is 27.5% → CHANGE value to 27.5.*
- **L6 — Use the paper's OWN measured metric, not a number it cites from others.** *Ex:
  DeVerna — the 0.1%/80% figure is cited from Grinberg; the paper's own concentration result
  is "0.003% of accounts → 34% of retweets" and "0.25% of accounts → >70%" → CHANGE to the
  paper's own metric.*

## MINE-THIS rules (high-value secondary sources to dig into, not single data points)
- **L7 — Systematic reviews / meta-analyses of prevalence or recall are goldmines.** Extract
  their pooled estimate AND, where possible, the underlying primary studies. *Ex: Çeleğen
  (BMC 2026) — meta-analysis of survey-based recalled misinfo exposure: pooled 59%, range
  10–87% → "we can use their data, dig into this." Kemei (J Glob Health 2022) — scoping
  review of COVID mis/disinfo, 80% US / 96% Canada recall → "dig into this."*

## Summary of the underlying logic
Two principles drive every call: **(a) denominator representativeness** — reject anything
whose base is curated, simulated, or not the real population/diet; and **(b) construct
fidelity** — the number must be the *measured share of misinformation itself*, not its
complement, a proxy, a simulation, or a borrowed citation. Reviews/meta-analyses are treated
as sources to mine, not as single estimates.

## L8–L13 — error patterns from Sacha's canonical-paper spot-check (2026-06-25)
- **L8 NEWS ≠ fake news.** Don't code a "% that is news / news share of media diet" as misinfo (Allen 14.2% was news-of-diet, NOT fake news; real number 0.15%). Bovet "national news fake-or-real" row dropped.
- **L9 Differentiate CONCENTRATION sub-type:** keep construct=CONCENTRATION but measure_type must say "concentration of EXPOSURE" vs "concentration of SHARING" (Grinberg 1%=80% exposure vs 0.1%=79.8% shares).
- **L10 Regression slope ≠ prevalence.** Cinelli stored 0.70 was a ρ slope; real shares are Gab 0.38 / Twitter 0.10 (Table 4). Always confirm a % is a share-of-denominator, not a coefficient/ratio.
- **L11 Audience-lean/segregation ≠ misinfo prevalence.** González-Bailón "97% of false URLs have conservative audiences" is a favorability/segregation score → drop.
- **L12 Echo-chamber/bot metrics ≠ prevalence.** Ferrara 53%/89%/13% (retweet homophily, bot share) → drop; keep only %-of-users-sharing-misinfo with a denominator.
- **L13 Absolute reach w/o denominator = unusable.** Nelson&Taneja 675k visitors (no %-of-total) → not a usable prevalence estimate.
- **REQUIRED FIELD: every row needs n** (# participants AND/OR # content/sources; state which in measure_type).

## L14–L17 + date field (Sacha spot-check 2026-06-25, round 2)
- **L14 No concentration-of-CREATORS/sources.** Only document concentration among the AUDIENCE (exposure)
  or among USERS who share. Drop "X% of accounts produce Y% of misinfo content" (Eady 89%-of-Russian-accounts dropped).
- **L15 Prefer all-participants / broadest denominator.** Drop conditional-on-exposed figures when the
  all-participants version exists (Cordonier: keep 0.16%/5% of all-participants time; drop the n=921-exposed 11%/0.4%/39%-reach).
- **L16 No within-misinfo composition breakdowns.** Shares WITHIN the misinfo/unreliable set (Cordonier
  generic 43%/clickbait 41%/health 14%/pseudo 2%/satire 1%) are composition, not prevalence → drop.
- **L17 Drop redundant restatements** of the same concentration finding (Eady 98% ~ 70%; keep the cleanest).
- **NEW REQUIRED FIELD `date`:** record the MEASUREMENT period/year of the data (e.g. "Sep-Oct 2020",
  "2016 election"), distinct from publication year. Added to schema; fill for every row (Step B enrichment).
- Robertson R.E. 2023 = Sacha-validated as correct (good reference example).

## L18–L22 + small-content-N flag (Sacha spot-check 2026-06-26, round 3)
- **L18 "% of content items" = CONTENT, not EXPOSURE/SHARING.** Bovet 25% (share of news-link TWEETS that are fake/biased) = CONTENT; the word "share" does NOT imply SHARING.
- **L19 distinguish tweet-share vs user-share.** Bovet: 25% of TWEETS are fake/biased (CONTENT) vs 12% of USERS post fake/biased (SHARING) — differ because such users tweet ~2x more. Code separately.
- **L20 SMALL-CONTENT-N FLAG (`flag` column).** Flag content-prevalence studies with extremely small content samples (Ahmed 2020 n=233 tweets/10% sample; Li 2020 n=69 videos). Step B records exact content-N + flags small ones; threshold never ratified (candidates were <100 extreme, <300 small); no content-N cut-off is applied anywhere in the released analysis, so the flag stayed descriptive. NOTE: ~60% of CONTENT/QUALITY/EXPOSURE studies have content-N<300 — a thesis-relevant finding (alarming CONTENT %s rest on tiny curated samples). Audit: data/extract_v2/qa/content_n_audit.csv.
- **L21 drop OTHER/engagement-overlap rows** with curated denominators (Bessi 2015 "80% of troll-likers are conspiracy consumers" = not a misinfo prevalence → drop).
- **L22 drop complement rows** (Guess 2019 "91.5% shared zero" = complement of 8.5% shared >=1 → keep only the misinfo-direction 8.5% + the 0.75 avg). Guess-type "% who shared >=1" is kept though imperfect (no diet-share available) — important study.
- **NEW `flag` column** added to schema (15 cols).

## L23 — small-N curated-topic studies ARE valid estimates (Sacha, 2026-06-26)
"50% of my 300-tweet vaccine sample is misinfo" IS a prevalence estimate — a CONTENT estimate against a
CURATED/TOPICAL denominator, just imprecise. DO NOT exclude on N alone. Empirically, small content-N is a
near-perfect marker for curated-topic content analysis (median content-N=166; ~all <300 studies are
topic-curated, none whole-diet). Treatment: KEEP; carry TWO independent flags — (1) `small_content_n`
(drives a precision sensitivity analysis), (2) denominator-type topical/curated vs population (the thesis
split, Step B). These inform the CONTENT bucket and the CONTENT-vs-EXPOSURE contrast; they do NOT speak to
population exposure. Synthesis reports them in the topical/curated cell, separate from whole-diet EXPOSURE.

## L24 — SAMPLING-FRAME NEUTRALITY (circular-denominator test) — Sacha 2026-06-26 ⭐
Before accepting any CONTENT/QUALITY %, confirm the sample was drawn NEUTRALLY (topic/keyword/popularity/
random/full-census), NOT selected by misinfo status. "X% of [already-misinfo items] are misinfo" is
COMPOSITION, not prevalence → DROP. Confirmed drops (read methods): 105028607759 (TikTok: "only
disinformation posts selected" → 207), 85130316440 (fluoride: 500 pre-filtered to "false or misleading"),
85111547179 (1679 IFCN fact-check articles → "% false among fact-checked" curated by construction),
85047304648 (22 hand-"traced"/suspected WhatsApp claims, no population denom). KEEP: 85083965254 (Berriche &
Altay Sante+Mag = full 500-post census of one page; 28% misinfo — neutral denominator, but flag single_source).
This is INDEPENDENT of N (dropped 207/500/1679-item studies on circularity). Step B must apply this test to
EVERY curated content study; the crude regex over-flags neutral frames (most "hits" are valid: JQD news-traffic,
"all 99,386 classified posts", browsing-history panels) — verdict requires reading the sampling frame.

## L25 — SINGLE-SOURCE samples: keep but document (Sacha 2026-06-26)
A content census/sample drawn from ONE outlet/page/channel/account estimates prevalence WITHIN THAT SOURCE
only — not health/news content generally. KEEP (it's a real estimate) but FLAG `single_source_sample` and
state the source + that it's a within-source rate (often an upper bound when the source is misinfo-prone).
Examples: Berriche & Altay Sante+Mag (500-post page census, 28%); the "anti-vaccine Facebook page" row (66.5%,
extreme upper bound). DISTINGUISH from multi-source/keyword samples in the SAME paper (85212060458 also has a
general-keyword sample across Facebook pages → 2.4%, kept unflagged). Step B tags every content estimate's
sampling scope: single-source / multi-source-topical / population. Synthesis must not read single-source rates
as general prevalence.

## L26–L31 (Sacha spot-check 2026-06-26, round 4 — OTHER/Hard cases)
- **L26 conspiracy-hashtag-selected = drop.** Ahmed 2020 sampled #5GCoronavirus tweets → composition within a conspiracy-defined set, not prevalence. (Same family as L24 circularity.)
- **L27 source/website-level != content prevalence.** Cuan-Baltazar 2020 rated 110 COVID *websites* → we measure content-item exposure, not source quality → drop.
- **L28 concentration must be AUDIENCE/individual-level, not source-level.** Waszak 2018 "21% cumulative shares of fake-news links" = which sources get shares → drop (extends L14). We care about concentration of EXPOSURE across people.
- **L29 out-of-scope deception types.** Greenwashing/misleading ads (Baum 2012) and anti-vaccine *stance* (Basch 2017) are NOT misinformation-prevalence → drop.
- **L30 drop subgroup rows that nest inside a broader estimate** (Moon 2020: 47 independent-user videos ⊂ 105 → keep only the 105-video 37.14%). Extends L22.
- **L31 fact-check-database samples = circular, drop** (Garcia-Marin 2020: 511 IFCN fake-news items). Reaffirms L24.
- **N check:** Chew 2010 N filled = 5,395 (random H1N1-keyword tweets, topic-neutral → KEEP).
- **[DONE, Step B] Each kept study's OWN misinformation DEFINITION** (fact-check vs author-coded; what counts) is recorded in the `definition` field. Completed in the Step-B full-text pass; the frozen dataset carries a definition for every study.

## L32–L37 (Sacha spot-check 2026-06-26, round 5)
- **L32 REACH != EXPOSURE.** "% of people who visited/were exposed to/liked >=1 [misinfo] in a period" is REACH
  (a distinct construct), NOT diet-share EXPOSURE. Moved out: Guess2020 44.3, Eady 70/63, +others (13 rows). Don't pool reach with intensity.
- **L33 self-reported sharing = RECALL(sharing), not observed SHARING.** Survey "X% admitted/acknowledged sharing"
  (Rossini 2021, Chadwick 2018) -> RECALL. Sub-type ALL recall: `recall-exposure` (self-report saw) vs `recall-sharing` (self-report shared).
- **L34 engagement != exposure.** Robertson 2023 "overall engagement 3.03%/1.86%" (clicks/follows) -> OTHER, not EXPOSURE; keep only the "URLs exposed to on Google Search" 2.05%/0.72% as EXPOSURE.
- **L35 relative virality/velocity out of scope.** "Inaccurate articles 28x more likely to be shared than true" (Alsyouf 2019) and all "false spreads faster/farther than true" (Vosoughi-style) -> drop; not a prevalence quantity.
- **L36 keep-one tie-breaks:** aggregate vs individual-mean -> keep AGGREGATE for cross-study comparability (Grinberg 5.0% over 1.18%); fake+extremely-biased vs fake-only -> keep FAKE-ONLY (Bovet 10% over 25%; "biased" != false).
- **L37 bot/account spreading concentration = concentration of SHARING** (Shao 2018: 6% bot accounts -> labeled concentration of sharing). Distinct from dropped source/creator concentration (L14/L28): this is who SPREADS, kept per Sacha.

## L38–L43 (Sacha spot-check 2026-06-26, round 6)
- **L38 drop narrow sub-topic when the broad estimate exists** (Moore: drop QAnon 3.7, keep "exposed to misinfo site" 39.1; Dahlke: drop pink-slime 3.7, keep 39.1). One reach per study.
- **L39 REACH requires the TIME WINDOW in `date`** — "X% encountered >=1" is meaningless without the period (Eady ~7 mo Apr-Nov 2016 vs Guess final weeks 2016). Document for every reach row.
- **L40 mean-count / intensity (e.g. "mean 1.19 visits/person") is neither a share nor reach** -> flag `intensity_mean_count`, exclude from the diet-share EXPOSURE synthesis (like absolute-reach L13).
- **L41 non-English: TRANSLATE; fact-check-platform samples = composition -> drop.** Almansa 2022 = 255 Maldito-Bulo/Newtral "bulos" (debunked hoaxes); "% about virus/vaccines" is composition-within-fact-checks, not prevalence -> drop.
- **L42 corpus-composition by country/platform = not prevalence.** Al-Zaman 2022 "India 15.94% / Facebook 66.87% of the misinformation [corpus]" = shares of a collected misinfo set -> drop.
- **L43 keep-one denominator pick:** when a study reports the misinfo share over multiple denominators, keep the cleanest CONTENT denominator (Singh: 2.7% of LINKS over 0.3%/0.83% of all tweets; reclassified EXPOSURE->CONTENT).
