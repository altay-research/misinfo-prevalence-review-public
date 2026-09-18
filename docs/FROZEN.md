# FROZEN DATASET v1.7.23 (2026-09-16)
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.7.23_frozen.csv
- Rows: 1048 estimates / 443 studies
- MD5: 08f050baf45086f45b5b3bec2390a115
- Git tag: dataset-frozen-v1.7.23 (supersedes v1.7.22)
- Built by: scripts/apply_v1723.py (changelog: data/extract_v2/qa/changelog_v1723.csv)

## v1.7.22 -> v1.7.23 - the four corrections from the blind re-extraction of the late arrivals

The 28 studies that entered after the 57-batch census had finished were re-extracted blind by fresh
agents on the census instrument (`data/extract_v2/late_reextract_2026-09/`). 26 of 28 eligibility
agreements, 35 of 42 frozen values reproduced, construct kappa 1.00 on the matched pairs. Sacha
ruled all four corrections on 2026-09-16 (`qa/reextraction_rulings_2026-09-16.csv`); five further
disputes were raised and ruled NO CHANGE.

1. **`W4409319996` leaves the corpus.** Its CONTENT 38.0% is the share of sources advising more away
   rotations than the APD guideline allows - guideline adherence, which Methods 4.6 excludes BY NAME
   as Quality. Third independent flag on this study.
2. **`W4313324568`'s 58.3% goes.** The row's own misinfo_def is "being deceived by news that has
   later proven to be fake"; eligibility excludes belief. The study stays on its 25.2% row.
3. **`2-s2.0-105004472114` gains RECALL 65.8%**, the complement of the 34.2% who recognised none of
   its seven narratives - the any-recall figure the original extraction missed while quoting the
   very sentence that contains it.
4. **`W4306960737` loses the 49.7% row**, a second recording of the 49.2% quantity on the same 120
   videos; the paper's text and Table 4 disagree and the table counts reconcile.

No headline median moves.

# FROZEN DATASET v1.7.22 (2026-09-16)
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.7.22_frozen.csv
- Rows: 1050 estimates / 444 studies
- MD5: 12e80fe355a666f6305c479b6449c040
- Git tag: dataset-frozen-v1.7.22 (supersedes v1.7.21)
- Built by: scripts/apply_v1722.py (changelog: data/extract_v2/qa/changelog_v1722.csv)

## v1.7.21 -> v1.7.22 - one breadth code, corrected by the wave-5 cross-check

**ONE CELL.** `W7117302408` (Nigerian NIN-SIM survey, RECALL 69%) carried definitional breadth
`false`. The wave-5 independent coder said `misleading` and the paper is on their side: "About 69%
of respondents indicated that MISLEADING OR FALSE information circulating on social media platforms
created confusion", under a Table 4 row labelled "Exposure to misinformation and fake news". A band
that admits misleading content is `misleading`. Ruled against the source and recorded in
`data/extract_v2/qa/gpt_check_2026-09_wave5_adjudication.md`. No value, id or construct moved, and
the apply script asserts that exactly one cell differs.

Two further wave-5 disagreements are NOT applied and wait on the author: the denominator class of
`W7162938155` (one topic or a domain spanning several) and whether `W7171843315`, which counts
observed face-to-face conversations rather than media items, belongs in the CONTENT pool.

# FROZEN DATASET v1.7.21 (2026-09-15)
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.7.21_frozen.csv
- Rows: 1050 estimates / 444 studies
- MD5: 511cb4ddec26cb3d1bf20cb00a8615be
- Git tag: dataset-frozen-v1.7.21 (supersedes v1.7.20)
- Built by: scripts/apply_v1721.py (changelog: data/extract_v2/qa/changelog_v1721.csv)

## v1.7.20 -> v1.7.21 - one study restored, one vocabulary recode

**A STUDY RETURNS THAT SHOULD NEVER HAVE LEFT.** `2-s2.0-85145196122` (Kreps et al. 2022, JMIR
Infodemiology) was coded 1.1% / 0.3% from the abstract, confirmed `keep` at the June value review,
then produced zero rows at the full-text re-extraction with no verdict recorded anywhere. It
surfaced on 2026-09-15 as the single residual of the exclusion-reason recovery: the one cell in a
506-record exclusion table whose reason read "none recorded". On reading the archived full text the
reason does not appear to exist. The paper reports content prevalence with a stated denominator and
an external ground truth - "1.1% of tweets from Twitter contained misinformation on COVID-19, with
5 (0.7%) of 746 tweets ... in batch 1 and 6 (2.8%) of 211 ... in batch 2, compared to 0.3% on
Weibo, with 1 (0.4%) of 279 posts in batch 1 and 1 (0.2%) of 441 posts in batch 2", adjudicated
against the WHO fact-check page. Two rows, one per platform, on the two 24-hour windows sampled
(30 January and 6 February 2020). Sacha ruled to include.

- **Ruling P2 applied**: `scholar_04`'s `demographic_subtype` held `older` and `younger`, age labels
  in a field whose vocabulary is the subtype set. Both recoded to `per_subgroup_rate`; both rows are
  demographic and enter no headline.

No other value, id or construct moves, and the script asserts it.

## v1.7.19 -> v1.7.20 - repairs found by the 2026-09-14 audit
Four adversarial audit passes ran before the manuscript re-sync. Three findings were defects this
project's own merge introduced or failed to apply, and each is something a reviewer with the dataset
could find in an afternoon.

- **A DUPLICATE STUDY.** `scholar_01` and `W4414259328` are the same paper (Dahlke & Hancock, DOI
  10.54501/jots.v3i1.250): same title, same REACH 39.6, same n, byte-identical source quote. Two
  arms found it on the same day and the alias map caught neither. The behavioural-arm id is kept,
  because that arm screened and extracted it at full text; `scholar_01` is now aliased to it.
- **FOUR OPERATIONS THIS LEDGER CLAIMED WERE APPLIED, AND WERE NOT.** apply_v1718 imported
  apply_v1717 but read only its ADDITIONS, never its REMOVALS or CORRECTIONS. Now applied: three
  absence-numerator rows removed (each study keeps its positive row) and `W7146985142` REACH 9 -> 8,
  a row that contradicted its own stored quote, "compared to just 8%".
- **THREE ROWS CLOBBERED BY A NON-UNIQUE MATCHER.** apply_v1718's edit() matched on
  (id, construct, value_pct), which is not unique, so the last write won. A RULED value was
  destroyed - `2-s2.0-85074596916`'s 24.1 became 18.2 - and one row's value_raw was cloned across
  three different elections in `2-s2.0-85074511992`. Both are restored from the ledger that ruled
  them, and the matcher now REFUSES a non-unique match on any value-bearing field.
- `definition_variant` had three spellings of a boolean, so any grouping treated two as different
  levels. Normalised.

HEADLINE MEDIANS (study-level, MAIN SET, regenerated on this freeze): CONTENT 23.0 (k274) -
RECALL 43.0 (k91) - SHARING 13.0 (k45) - EXPOSURE 1.3 (k18) - REACH 12.0 (k27) -
CONCENTRATION 74.0 (k19). Only REACH moves against v1.7.19 (12.5 k28 -> 12.0 k27): the duplicate
study leaves the pool. Every other construct is unchanged.

## v1.7.18 -> v1.7.19 - DOCUMENTATION ONLY. No value moves.
Every change is to a text field (`denominator`, `measure_type`, `flag`). Not one `value_pct`, `id`
or `construct` changes, and the script asserts that and refuses to write otherwise. So every Phase B
output computed on v1.7.18 stays valid, INCLUDING the 28-hour bootstrap that was running while this
was applied. The headline medians are v1.7.18's, unchanged.

- **J2, 17 empty `denominator` fields filled** from the papers, across four studies. The largest
  block is an arXiv preprint's ten rows, whose `n` is the sampled corpus rather than the estimate's
  denominator, because the paper never prints the restricted set it divides by; those ten now carry
  a flag saying exactly that.
- **J3, one real error corrected.** Both rows of `2-s2.0-105009619554` carried the CLAIM-level
  denominator (411 attributed ADHD characteristics) while their values are shares of the 100 VIDEOS,
  which the rows' own stored quote says outright. Repointed, `measure_type` rewritten, and flagged
  as nested in the same 100 videos so the two are never summed. The paper's claim-level 55% is a
  third denominator and is NOT held as a row; that would be an extraction decision, not a
  documentation fix.
- The other two J3 cases **confirmed the freeze as it stands** and changed nothing: a 14% that turns
  out to be the whole non-useful residual, mixing in irrelevance and personal testimony; and a 7.7%
  the paper's own abstract mislabels, which is engagement-weighted where ours counts items.

STILL OPEN: 56 empty `denominator` fields remain elsewhere in the corpus, the largest blocks being
14 rows on one study, 12 on another and 8 on a third. Worth clearing before the data goes public.

## v1.7.16 -> v1.7.18 - the merge (superseded by v1.7.19, which changes no value)
Everything that accumulated after v1.7.16 lands in one freeze. Five input streams, every operation
attributed in the changelog to the ruling key that authorised it:
 - **the wave-3 acquisitions** apply_v1717 prepared but never applied (Google Scholar recall check,
   the earlier behavioural screen, one hand-found paper), plus its three absence-numerator removals
   and its W7146985142 REACH 9 -> 8 correction;
 - **the full 57-batch blind re-extraction** via merge_plan.py, from Sacha's 2026-09-08 and
   2026-09-10 rulings: 36 removals, 30 addition sets, 160 corrections, 29 manual items;
 - **the two-coder value-verification ledger** via ledger_proposals.py (Sacha 202/221, Laura
   208/221), plus the 11 proposals he ruled on 2026-09-14 (ledger_rulings_sacha_2026-09-14.csv):
   three removals and eight documentation groups;
 - **the 73 pre-merge rulings** (premerge_rulings_sacha_2026-09-14a/b.csv + the delegated E2 file),
   sections A-L and K, brief at docs/PREMERGE_BRIEF_2026-09-09.md;
 - **the behavioural arm** (K0 MERGE_NOW): 35 rows from 20 studies; K1/K3/K6/K8 dropped four.

HEADLINE MEDIANS (study-level, MAIN SET): CONTENT 23.0 (k274) - RECALL 43.0 (k91) -
SHARING 13.0 (k45) - EXPOSURE 1.3 (k18) - REACH 12.5 (k28) - CONCENTRATION 74.0 (k19).
CORRECTED 2026-09-14 after an audit. The table these were read from applied NO main-set filter, so
104 demographic-subgroup rows and 10 non-proportion rows entered the study medians. The figures
first recorded here - SHARING k47, EXPOSURE 1.0, REACH 11.1 k30 - were contaminated. The fix is in
phaseB_descriptives.py and phaseB_grade.py, which now share the invariants' main-set predicate, and
all three median tables agree. Against v1.7.16 (CONTENT 23.2 k275, RECALL 41.0 k94, SHARING 11.2
k42, EXPOSURE 2.0 k15, REACH 11.0 k25, CONCENTRATION 74.0 k17): CONTENT and CONCENTRATION unmoved,
RECALL +2.0 on 3 fewer studies, SHARING +1.8 on 3 more, REACH +1.5 on 3 more, and EXPOSURE falls
2.0 -> 1.3 on 3 more studies because the Allcott 5 left the pool as an R8 breach. Re-sweep section 2
for the EXPOSURE move.

THREE REMOVALS RULED ON 2026-09-14, each following a rule already applied elsewhere: Allcott &
Gentzkow's EXPOSURE 5 (a denominator we built by summing two site lists, which R8 forbids); a
SHARING 0.94 whose own paper says under 1% of its denominator was fact-checked, so it measures
coverage not prevalence; and a RECALL 17.72 whose denominator is survey occasions rather than
people, the identical shape dropped at v1.7.16.

STILL OPEN, deliberately: 19 ledger proposals never put to Sacha because there is nothing to decide
(their study leaves the corpus here, or a pre-merge ruling settles them), and two manual follow-ups
recorded in the dry run as J2 (fill four empty denominator fields) and J3 (verify three
row-versus-abstract mismatches against the text).

## v1.7.15 -> v1.7.16 - the independent cross-check's disputes, adjudicated by the author
23 disputes from the wave-2 cross-check went to Sacha on an adjudication page
(docs/gpt_check_2026-09_wave2/disputes_wave2.html; his file at rulings/disputes_wave2_sacha_FILLED.csv).
He ruled 21: 9 OURS, 12 DROP, 2 THIRD. Effect: 14 rows removed, 6 studies leave the corpus. (Rebuilt 2026-09-04 after check_invariants
found that a dispute ruling retyping a row to QUALITY had not moved it out of the prevalence pool;
the fix is a sweep in apply_dispute_rulings.py, and 4 rows moved to the appendix as a result.)
His drops are substantive, not clerical, and each names a boundary the review cares about:
 - conspiracy THEMES are not misinformation ("can be fictional, can be true/real conspiracy");
 - citation bias in the scientific literature is "way too far from what we're interested in, ie
   misinformation people get exposed to, consume, hear about";
 - source-level factual RATINGS are quality, and the review does not keep quality ratings of sources;
 - falsity computed inside an already-misinformation sample is within-misinfo, not prevalence.
The 2 THIRD rulings (both on 105026138407) are read as: keep the abstract's headline misinformation
figures (34% media, 9% government), drop the "misleading content" definition variants. That reading
is flagged in wave2_ruling_effect.csv and is the one interpretive step in this freeze.
The 2 he left blank were decided on the standing rules and are marked ruled_by=claude_default:
85215526254 dropped (denominator is exposure instances, not respondents, so it fails RECALL's
population-denominator rule) and 105032501759 kept (the fact-check confirmed it; the single-grader
weakness is a risk-of-bias matter, already recorded there). Either can be overturned in one edit.

# FROZEN DATASET v1.7.15 (2026-09-04)
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.7.15_frozen.csv
- Rows: 989 estimates / 462 studies
- MD5: 298ab1e3d36eecd3d8b8ffa906807ab3
- Git tag: dataset-frozen-v1.7.15 (supersedes v1.7.14)
- Built by: scripts/apply_v1715.py (the corpus repair: 314 rows / 147 studies added; the freeze
  files are the authority, and the id-set difference from v1.7.14 is 147 studies / 314 rows)

## v1.7.14 -> v1.7.15 - the corpus repair
The June 2026 screening criteria never named self-reported RECALL and under-specified CONTENT
prevalence, so both were excluded by instruction; the 27 recall studies in the June corpus entered
despite the criteria, not because of them. Found 2026-09-02 by our own round-3 human validation.
The repair re-screened every title- and abstract-stage exclusion with two independent model
families, adjudicated the flags under corrected criteria, retrieved 335 full texts, screened and
extracted them, cross-checked the rows with a third model family (blind construct kappa .732), and
applied Sacha's class-level rulings R1-R10. Full account: docs/corpus_repair_2026-09/REPAIR_REPORT.md.
ENTERS THE FREEZE: the 314 rows / 147 studies whose pool is `main`.
DOES NOT: 215 appendix rows (QUALITY, within-misinformation, scale scores, intensity, chatbot/LLM
accuracy studies, adversarial prompt sets) and 21 dropped rows, each with its pool_reason in
data/extract_v2/repair_2026-09/repair_estimates_final.csv.
Headline effect: RECALL study-level median falls ~53 -> ~41 with k from 27 to 97; CONTENT unchanged
at ~23; SHARING must be reported stratified by denominator, not pooled.

# FROZEN DATASET v1.7.14 (2026-09-02)
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.7.14_frozen.csv
- Rows: 675 estimates / 315 studies
- MD5: e73fb8f6d7199fa1d8c1b34f887c5124
- Git tag: dataset-frozen-v1.7.14 (supersedes v1.7.13)
- Built by: scripts/apply_v1714.py (2 studies added: the round-3 abstract-stage misses)

## v1.7.13 -> v1.7.14 - the two abstract-stage misses recovered by the human validation
The round-3 human re-screen (docs/RA_package/round3_2026-08/) found two pipeline abstract-stage
exclusions that both coders would have advanced; adjudication against the full text ruled them
eligible (round3_keys/adjudication_B_union.csv). Sacha ruled 2026-09-02 that they enter the corpus.
Chadwick, Vaccari & Hall 2022 (UK survey, n = 2,005): RECALL/sharing 9.9% of social media users
amplified exaggerated or false news in the past month. Roland-McGowan et al. 2025 (JMIR
Dermatology): CONTENT 6% of the 100 most-liked TikTok sunscreen videos inaccurate (curated
denominator). Author-level extraction; RoB appraisals in data/rob/v3out/shard_98_manual_2026-09.csv
(MODERATE, HIGH). Main set 569 -> 571; recall-sharing k 7 -> 8; content k 209 -> 210.

# FROZEN DATASET v1.7.13 (2026-08-13)
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.7.13_frozen.csv
- Rows: 673 estimates / 313 studies
- MD5: bda27bb945cbee7629559d257b48bf03
- Git tag: dataset-frozen-v1.7.13 (supersedes v1.7.12)
- Built by: scripts/apply_v1713.py (6 studies, duplicate country_norm labels merged)

## v1.7.12 -> v1.7.13 - country labels written twice
Surfaced while building the country coverage panel. "UK" merged into "United Kingdom",
"USA (Georgia)" into "United States", and three "Cross-national (global...)" variants into
"Global". Only exact duplicates; genuinely ambiguous labels ("English-language", "Arab world",
"United States; South Africa", "North America") are left for a coding decision. Raw `country`
untouched. Section 2.1's US count is affected and was corrected in the same commit.

# FROZEN DATASET v1.7.12 (2026-08-13)
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.7.12_frozen.csv
- Rows: 673 estimates / 313 studies
- MD5: d82cd32e94cb6af59f0129fb02e630f8
- Git tag: dataset-frozen-v1.7.12 (supersedes v1.7.11)
- Built by: scripts/apply_v1712.py (4 multi-platform corpora miscoded Twitter/X)

## v1.7.11 -> v1.7.12 - cross-platform corpora coded as one platform
Four rows describing corpora that span Facebook, Twitter, Reddit, Pinterest or LinkedIn (two
BuzzSumo designs and one "Multiple social media" corpus) carried platform_norm "Twitter/X", while
a fourth study with the identical BuzzSumo design was already coded "multi_platform". All are now
multi_platform. Raw `platform` untouched, so Appendix B5 still counts each study once per platform
it names.

# FROZEN DATASET v1.7.11 (2026-08-13)
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.7.11_frozen.csv
- Rows: 673 estimates / 313 studies
- MD5: e5d8869ebe79c4c09fd9a36555fd2cf1
- Git tag: dataset-frozen-v1.7.11 (supersedes v1.7.10)
- Built by: scripts/apply_v1711.py (3 stale platform_norm labels)

## v1.7.10 -> v1.7.11 - two platform labels inconsistent with their siblings
Surfaced while tabulating platform x construct for the manuscript SI. Two rows of
2-s2.0-85138494787 carried platform_norm "Twitter" where the other 141 rows with the same raw
string carry "Twitter/X"; one row of NEW-jadara-2022 carried "cross_platform", a level used
nowhere else, where "social media" elsewhere maps to "multi_platform". Raw `platform` untouched.
No behavioural row is affected, so the section 2.1 platform sentence cannot move.

# FROZEN DATASET v1.7.10 (2026-08-12)
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.7.10_frozen.csv
- Rows: 673 estimates / 313 studies
- MD5: 73a0fd6c5f98a06cff3d006859b081e1
- Git tag: dataset-frozen-v1.7.10 (supersedes v1.7.9)
- Built by: scripts/apply_v1710.py (2 recall_subtype miscodes: exposure -> sharing)

## v1.7.9 -> v1.7.10 - two shared-recall rows were sitting in the seen-recall pool

The recall-window extraction (Sacha's v5 comment C0: "what time window do the recall questions ask
about?") required enumerating the seen-recall studies, and the enumeration surfaced a mismatch:
study 2-s2.0-85122105134's two RECALL rows (19% social networks, 18% WhatsApp) are coded
recall_subtype=exposure but measure self-reported SHARING, verbatim: "En el caso de redes sociales,
81% afirmo no haberlo hecho y 19%, si" (sharing false news). Flipped to sharing. Seen-recall k
23 -> 22 (median unchanged at 60.0), shared-recall k 6 -> 7. The seen pool now coincides exactly
with the 22 studies whose question windows are coded in qa/recall_windows_2026-08-12.csv.

CORRECTION (2026-08-12, same day): the paragraph above initially said "median unchanged at 60.0".
That was wrong — the seen-recall median moved 60.0 (k=23) -> 62.0 (k=22) when the two miscoded rows
left the pool, and the manuscript reports 62.0. Recorded here as a correction rather than an edit,
because this file is append-only. (Caught by the 2026-08-12 internal review, item 16.)

---

# FROZEN DATASET v1.7.9 (2026-08-11)
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.7.9_frozen.csv
- Rows: 673 estimates / 313 studies
- MD5: 58feb4d0ac5a734673b654364f47c298
- Git tag: dataset-frozen-v1.7.9 (supersedes v1.7.8)
- Built by: scripts/apply_v179.py (Fable QA pass adjudicated: 92 field edits, no rows added/removed)

## v1.7.8 -> v1.7.9 - the source-anchored QA pass applied (queue: qa/fable_qa_2026-08-11/FINDINGS.md)

Eight same-family agents re-read all 170 rows of the 40 load-bearing studies (backbone u EXPOSURE u
CONCENTRATION) against full text. ZERO value errors; 92 metadata edits, adjudicated by Sacha
(six Section-A rulings) or verbatim-verified in session:

  * A1 Faker Island 0.05 -> SHARING + curated_sample (link-bearing post stream by a class of
    actors); dates 2018-2020 on both rows. NB: settles THIS study only; the general
    link-bearing-posts rule (36 rows) remains a declared open item.
  * A2 W4293124965: six political_news rows -> news_diet (denominator is ALL news traffic /
    engagement; table siblings already news_diet); eight stale TOPICAL diet_type flags cleared.
  * A3 allcott2017 5% -> news_diet; breadth blank (domain-list rule).
  * A4 85160248068: 3.03/1.86 OTHER -> EXPOSURE + all_media (shares of overall web engagement);
    denominator text corrected; dataset-specific n's fixed (2018 SERPs 275; 2020 engagement 688).
    EXPOSURE gains a study (k 15->16) and the backbone gains one (k 32->33).
  * A5 85059494932 KEEPS political_news (authorial ruling; DECISIONS_REGISTER entry).
  * A6 85148963619 + 85194023903 -> country "English-language" (no stated geo restriction);
    85037352356 keeps United States (US ZIP-code telemetry).
  * B: sibling-row descriptor inheritance fixed on 8 studies (supersharer demographics, QAnon
    ideology rows, partisan page-like rows, political-sharer ideology rows, superspreader
    composition rows, YouTube-by-age instrument fields).
  * C: verified n fixes (Google datasets; Guess/Nyhan supporter rows 2,525 -> 2,170; gender rows).
  * D: breadth=fabricated cleared on OA-W2992531903 (domain-list rule) + one sibling harmonised;
    diet_type fixes (cordonnier 5% row WHOLE_DIET); conc pairs/units completed.

NOT applied: 105029413645 subgroup-n corrections (the QA evidence conflicted internally); the
36-row link-bearing-posts generalisation (open); 85159153364 top-15 conc pairs (not computable
as a percentage).

---

# FROZEN DATASET v1.7.8 (2026-08-10)
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.7.8_frozen.csv
- Rows: 673 estimates / 313 studies
- MD5: a16a78ecaf8d2f8e006018a404b11c33
- Git tag: dataset-frozen-v1.7.8 (supersedes v1.7.7)
- Built by: scripts/apply_v178.py (actor rule refined: single actor CONTENT, class of actors SHARING)

## v1.7.7 -> v1.7.8 - the actor rule refined (Sacha: "it's sharing then, if the study describes it as such")

Rule (a0-bis) said "an actor's own output is CONTENT", ratified from a case about ONE person
(Bolsonaro's own tweets). Applied literally it swallowed studies measuring the sharing behaviour of a
POPULATION of actors - 945 politicians, 4,787 state legislators, parliamentary parties - which are
behavioural sharing RATES and which the source studies frame as sharing. Refined:

  * ONE named actor's own output       -> CONTENT  (85131964464 Bolsonaro: unchanged)
  * a CLASS/population of actors,
    measured by what they share        -> SHARING  (follow the study's own framing)

Reverts v1.7.7 in full (27 rows) AND the two rows v1.7.4 moved on the same reasoning, which seeded
the over-reach: W4306964957 (2 rows), 105029521599 (1), 85142396682 (6), 105027856675 (20).
`sharing_subtype` restored where it had been cleared. SHARING now 95 rows / 31 studies.

NB these studies also legitimately hold OTHER rows (105027856675's "AfD accounted for 95.5% of
misinformation shared" attributions, whose denominator is the misinformation itself). Those stay OTHER.

---

# FROZEN DATASET v1.7.7 (2026-08-10)
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.7.7_frozen.csv
- Rows: 673 estimates / 313 studies
- MD5: b97643f98790813141a54b46f6e3c880
- Git tag: dataset-frozen-v1.7.7 (supersedes v1.7.6)
- Built by: scripts/apply_v177.py (SHARING restricted to transmission denominators; 27 rows + 16 field clears)

## v1.7.6 -> v1.7.7 - SHARING = a transmission denominator; actors' own output is CONTENT

Reading the denominators (rather than pattern-matching for "retweet") shows 25 of the 30 SHARING
studies have a denominator that IS an act of transmission. The residue is one already-decided
category: an ACTOR'S OWN OUTPUT, which rule (a0-bis) calls CONTENT.

MOVED SHARING -> CONTENT, 27 rows / 3 studies, all politicians' own posted content: W4306964957 (1
row, re-joining its sibling), 85142396682 (6), 105027856675 (20). SHARING 30 -> 27 studies.

THE RULE BITES HARDER THAN ITS ORIGIN CASE, which is worth recording. It was ratified on a SINGLE
actor (Bolsonaro's own tweets); applied consistently it also covers CLASSES of actors - "links
shared by Lega politicians", "misinfo-sharing rate of UK regional executives". Those are naturally
described as sharing and the studies frame them that way, but by the ratified test they measure what
an actor PUT OUT, not what circulated through a public. Reversible if Sacha wants the rule confined
to a single named actor.

A GATE CAUGHT A STALE FIELD: `sharing_subtype` describes a SHARING measure, but 16 rows recoded away
from SHARING in earlier freezes (incl. two moved by v1.7.4 itself) had kept it - a field that would
later read as evidence the row is a sharing measure. Cleared on every non-SHARING row, and the
condition is now asserted in the apply script.

---

# FROZEN DATASET v1.7.6 (2026-08-10)
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.7.6_frozen.csv
- Rows: 673 estimates / 313 studies
- MD5: 9d32a82b3d4f6ab6e3229ce533efd122
- Git tag: dataset-frozen-v1.7.6 (supersedes v1.7.5)
- Built by: scripts/apply_v176.py (round-2 adjudication: curation + breadth; 36 row-changes)

## v1.7.5 -> v1.7.6 - round-2 adjudication (whole-corpus re-code), by rule and source

(A) CURATION, source-evidenced: +6 rows curated, -3 un-curated. I over-rode the extractor on 9 of the
19 newly auto-classified studies - 7 false positives where the top-N is an ANALYSIS SUBSET while the
estimate's denominator is the full corpus ("top-20 users", "top-1% superspreaders", "top-10 topics"),
1 curated for a different reason than the regex matched, 1 parked as genuinely mixed (500 random +
2,000 popularity-selected).

(B) BREADTH, 27 rows, by the codebook rule (does the INCLUSION CRITERION admit non-strictly-false
material?). 19 of the 27 match the coder and 8 do NOT - the asymmetry is the point: this applies the
rule, not the coder's opinion. The 61 items the rule cannot resolve were NOT mass-recoded; breadth
stays the genuinely fuzzy dimension (kappa .48 against 94% coder self-consistency = a real boundary
disagreement, not instrument noise).

NOT APPLIED - CONTENT vs SHARING (~34 rows). Rule (a0-bis) calls a corpus of "sharing ACTS (shares,
retweets, link-bearing posts)" SHARING; applying it corpus-wide turns on whether "link-bearing posts"
means the corpus is RESTRICTED to link-bearing posts or merely that posts happen to bear links. The
two readings move ~34 rows between two reported pools. Two pattern-based attempts matched the
NUMERATOR's phrasing rather than the denominator, so this goes to Sacha as one clarification instead
of a third guess.

---

# FROZEN DATASET v1.7.5 (2026-08-10)
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.7.5_frozen.csv
- Rows: 673 estimates / 313 studies (main analysis set 569)
- MD5: aa9260e5e7096714afea9ffce9a3d5fe
- Git tag: dataset-frozen-v1.7.5 (supersedes v1.7.4)
- Built by: scripts/apply_v175.py (last 2 ambiguous curation studies resolved; 1 row-change)

## v1.7.4 -> v1.7.5 - the two parked curation studies, resolved on their denominators

85142238598 -> CURATED. Denominator: "top-40 per topic = top 20 posts x top 2 hashtags; 234 posts" —
rank truncation defines the set twice over. The row is a scale_score with an empty value_pct, so it
sits outside the analysis set: this is metadata correctness, not an analysis change.
85059494932 -> NOT curated, unchanged. Its denominators are the FULL corpora (30.7M URL-bearing
tweets; ~2.3M distinct users). The "top 100 news spreaders" that raised the flag is a subset used for
one network figure, not the denominator of either estimate.

This closes every curation item. ADJUDICATION ROUND 1 IS FULLY CLOSED.

---

# FROZEN DATASET v1.7.4 (2026-08-10)
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.7.4_frozen.csv
- Rows: 673 estimates / 313 studies
- MD5: 404b1029e1847eb2e3ff51967a6578c5
- Git tag: dataset-frozen-v1.7.4 (supersedes v1.7.3)
- Built by: scripts/apply_v174.py (Sacha's four authorial decisions; 35 row-changes)

## v1.7.3 -> v1.7.4 - Sacha's four decisions (docs/decisions_2026-08-05/decisions.html)

(A) QUALITY -> CONTENT, 4 rows (86000670842 x2, 85143511628, 85134426953). Construct only; breadth
stays blank, which is legal for CONTENT.
HELD: 85207525286 (92) = A1. Sacha marked himself unsure and reasoned "'Misleading' is clearly
veracity/factuality" - but not in this paper: it defines a video as "useful" if it contains "at least
4 out of the 6 questions on the ASRS-v1.1 screener", so "misleading" is the complement and a wholly
TRUE video covering 3 items is labelled misleading. That is coverage/completeness, which is why
v1.6.8 reverted it. Applying a change whose rationale the source contradicts would be wrong; A1 stays
QUALITY pending his confirmation.

(B) Fact-check-SEEDED corpora -> curated: 23 rows / 9 studies. Only `denom_selection` moves;
`denom_scope` is preserved, per Sacha ("we code both topical and curated, they are not incompatible").
NOT applied to 6 eligible rows whose scope is `population` - those denominators are survey
RESPONDENTS, and a sample of people cannot be rank-truncated or hand-assembled. The 2 "ambiguous"
studies (85059494932, 85142238598) remain open - a different question.

(C) CONTENT vs SHARING, 8 rows, by the ratified rule: decide on the DENOMINATOR, not the numerator's
verb. Sharing-act streams (link-bearing/retweet corpora) -> SHARING (6); an actor's own output
-> CONTENT (2: W4306964957 politicians' posts, 105029521599 state legislators' posts). The other 92
of the 100 rows in scope already complied.

(D) An actor's own posts are CONTENT. No data change (the Bolsonaro row was already CONTENT), but the
codebook's SHARING definition dropped the phrase "or of an actor's output", which had made a
politician's own tweets codeable both ways. Rule recorded in moderator_codebook.md (a0-bis) and fixed
in build_codex_full.py so future cross-check instructions carry it.

---

# FROZEN DATASET v1.7.3 (2026-08-05)
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.7.3_frozen.csv
- Rows: 673 estimates / 313 studies (main analysis set 569)
- MD5: 1d0dda1facbf97aef770e4c4c4dbd892
- Git tag: dataset-frozen-v1.7.3 (supersedes v1.7.2)
- Built by: scripts/apply_v173.py (8 REACH rows -> population denominator)

## v1.7.2 -> v1.7.3 - REACH rows whose denominator contradicted their own quote

An invariant check ("a behavioural REACH denominator is the PEOPLE observed") failed on 8 of 66 REACH
rows. All 8 are one bug: DEMOGRAPHIC-BREAKDOWN rows inherited a sibling row's `measure_type` and
denominator while their own quotes are unambiguous shares of PEOPLE - "11 and 21% of PEOPLE on the
right ever shared any fake news content" (85060549676), "the proportion of PARTICIPANTS ... exposed
to QAnon sites (11.1%)" (85209547248), "Independents had the highest rate of liking any fake news
pages, at 23.6% ... Democrats (15.4%)" (85162702221), "39% of participants consulted ... unreliable
sources" (SEED-cordonnier2021). Only the denominator fields move; constructs were already correct.
Backbone membership is unaffected (all scopes involved are inside the whole-diet backbone).

NB this also repaired an inconsistency v1.7.2 introduced: it corrected 85162702221's 20.4 row alone,
which would have left one measure split across two denominators.

---

# FROZEN DATASET v1.7.2 (2026-08-05)
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.7.2_frozen.csv
- Rows: 673 estimates / 313 studies (main analysis set 569)
- MD5: 7958e27cf3d3d40fa373acbc1b8e9641
- Git tag: dataset-frozen-v1.7.2 (supersedes v1.7.1)
- Built by: scripts/apply_v172.py (construct/breadth/denom_scope adjudication, 8 row-changes)

## v1.7.1 -> v1.7.2 - construct/breadth/denom_scope adjudicated against source

The CONSTRUCT coding held up: of 15 singleton disagreements, ours stands on 13 (the 2 exceptions are
QUALITY rows held for Sacha). Whole classes were confirmed OURS - all 6 "OTHER vs SHARING" (the
denominator is the misinformation itself, e.g. "AfD accounted for 95.5% of misinformation shared",
so it is an attribution statement, not a prevalence share) and all 5 "SHARING vs CONTENT" (computed
over a stream of shared items, which is what SHARING means). Fixes applied:

(1) VALUE_KIND, 2 rows (85215939792): 4.818 and 2.003 are MEAN mini-DISCERN scores on a 1-5 scale,
not percentages, but were `value_kind=proportion` and therefore pooled inside the main analysis set.
Recoded `scale_score`; main set 571 -> 569. Found by noticing a "percentage" of 4.818.

(2) DENOM_SCOPE, 1 row (85162702221, 20.4): a behavioural REACH row coded `all_media`; the codebook
is explicit that a REACH denominator is the PEOPLE observed -> `population`.

(3) BREADTH, 5 rows: 105018276467 (68.8) and 85122105134 (19) false -> fabricated (fabrication-
specific definitions); 85143274147 (36.3) and OA-W3113799821 (1) false -> BLANK (no per-item veracity
standard - the first is self-report with respondent-supplied examples, the second counts SEARCH
QUERIES, which have no truth value); 85159889148 (88) false -> misleading (5-point Likert benchmarked
against clinical guidelines = guideline non-concordance). Allcott 2017 was NOT changed despite the
coder saying `fabricated` - "intentionally and verifiably false ... rated false by Snopes/PolitiFact"
is a falsity standard and is the worked example for keeping `false`.

---

# FROZEN DATASET v1.7.1 (2026-08-05)
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.7.1_frozen.csv
- Rows: 673 estimates / 313 studies
- MD5: 363cb62bef25a9f29007af40c990b0b9
- Git tag: dataset-frozen-v1.7.1 (supersedes v1.7.0)
- Built by: scripts/apply_v171.py (curation sweep adjudicated against paper methods; 41 rows / 26 studies)

## v1.7.0 -> v1.7.1 - curation sweep (Claude, adjudicated against source; Sacha commissioned it)

41 rows across 26 studies move denom `topical` -> `curated_sample` (denom_selection=curated). The
evidence for curation is in each paper's METHODS, not in the extracted quote - which is why the
earlier candidate list could not be applied directly. scripts/adjudicate_curation.py pulled the
sampling statements from full text and every applied study carries a decisive sentence in
data/extract_v2/qa/curation_adjudication.csv ("the top 100 eligible videos ... were selected to form
the final dataset", "the first 150 videos were analyzed", "videos were sorted by view count").
Rank truncation DEFINES the sampled set, so the denominator is curated however large the corpus.

Adjudicator over-rode the extractor on 8 studies where the pattern fired on non-sampling text (ML
feature selection, results tables, and one paper stating it could NOT take the most-shared), and
parked 2 ambiguous + 9 "seeded" studies for a human read. Only decisive rank-truncation /
most-viewed sampling statements were applied.

CONSEQUENCE: curated stratum median 19.7% -> 26.0% (k 34 -> 57); topical 25.8% -> 24.6% (k 174 ->
150). DIRECTION MATTERS: before this fix curated corpora read LOWER than topical ones, which is
backwards for the review's thesis; after it curation reads higher, as the taxonomy predicts - the
under-flagging had been masking the curation effect. Constructs and breadth untouched.

---

# FROZEN DATASET v1.7.0 (2026-08-05)
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.7.0_frozen.csv
- Rows: 673 estimates / 313 studies
- MD5: f8987995911eb6955e812d85f6cc97d9
- Git tag: dataset-frozen-v1.7.0 (supersedes v1.6.9)
- Built by: scripts/apply_v170.py (adjudication round 1, remaining decided rows; 15 row-changes, no id/value change)

## v1.6.9 -> v1.7.0 - adjudication round 1, remaining decided rows (Sacha, 2026-08-05)

Targets resolved by (study_id, value_pct), NEVER by the positional F-id - F-ids shift on any
add/drop, and v1.6.9's 2-row drop had already re-pointed six decided items.

(A) breadth false -> misleading, 8 rows. Rule sharpened during adjudication: code `misleading` when
the definition's INCLUSION CRITERION admits non-strictly-false material ("false OR misleading",
"misinformative/biased", "inadequately contextualized"); keep `false` when misleading only describes
the intent/effect of falsity (Allcott 2017 "verifiably false and could mislead readers" stays
`false`). EXCEPTION confirmed by Sacha: 85213223975 (8.5) stays `false` (">50% false information
when fact-checked" is falsity-thresholded).

(B) breadth blank -> fabricated, ALL 6 rows of OA-W2992531903 ("for-profit fabrication,
politically-motivated fabrication and malicious hoaxes masquerading as news"). Applied study-wide,
not just to the 2 sampled rows: breadth is a property of the DEFINITION and all 6 rows share it.
Adds a study to the `fabricated` stratum (k 3 -> 4).

(C) denom political_news -> news_diet, 1 row (W4293124965, 3.3) - NewsGuard-rated news web traffic
is all news, not political news. denom_class moved with denom_scope (selection blank).

NOT CHANGED, decided: W2901308345 (2.8/2.7) stays CONTENT - verified against the paper's ORIGINAL
2018 version ("We classify 2.8% of articles as fake"), now archived; the 2022 PDF we held is a
retitle that drops the figure. The 5 blank-breadth QUALITY rows stay QUALITY (no internal
contradiction; 85207525286 = A1 was settled in v1.6.8). W7146985142 (23) keeps denom n/a (every
CONCENTRATION row is n/a; what it is concentration OF lives in conc_unit/conc_dimension).

---

# FROZEN DATASET v1.6.9 (2026-08-05)
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.6.9_frozen.csv
- Rows: 673 estimates / 313 studies
- MD5: 231416afda6ce3fbcce71c8d6fa00cf0
- Git tag: dataset-frozen-v1.6.9 (supersedes v1.6.8)
- Built by: scripts/apply_v169.py (adjudication round 1: drop sock-puppet-agent study; QUALITY-with-breadth -> CONTENT)

## v1.6.8 -> v1.6.9 - adjudication round 1 (Sacha, 2026-08-05)

(1) DROPPED study 2-s2.0-85114317455 (2 EXPOSURE rows, 6.9/9.9). Bandy & Diakopoulos junk-news
audit: the "audience" is 8 emulated sock-puppet AGENTS, not humans. Sacha: "if it's not humans we
don't include". Precedent: v1.6.3 removed forced-exposure experiment 85189974015. The row was
already flagged "emulated/sock-puppet agents, not real users; not human whole-diet". EXPOSURE k16->15.
NB Sacha recalled having excluded this before; the record shows the earlier decision excluded item
D11 from the IRR COMPARISONS only - the study had never been removed. Now it is.

(2) RECODED construct QUALITY -> CONTENT on all 7 rows carrying a veracity `breadth`, keeping
breadth=misleading. A QUALITY row with a breadth contradicts v1.6.0 (breadth = pure veracity scale;
quality = the QUALITY construct): our own coding had applied a veracity standard while labelling the
row a quality rating. The independent re-code called exactly these rows CONTENT. Their criteria
(guideline non-concordance, ">=1 misconception", "could not be corroborated", "overgeneralized") sit
at the misleading end of the veracity scale. Applied DATASET-WIDE (6 of 7 were in the coded 22%
sample, 1 was not) - applying a class decision only where the sample looked would bias the data
toward the sample.

HELD: the 5 QUALITY rows with BLANK breadth (86000670842 x2, 85143511628, 85134426953, 85207525286).
No internal contradiction, so the reconciliation does not reach them. 85207525286 is A1, flipped to
CONTENT in v1.6.4 and deliberately reverted in v1.6.8 - a third flip needs an explicit decision.

---

# FROZEN DATASET v1.6.8 (2026-08-04)
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.6.8_frozen.csv
- Rows: 675 estimates / 314 studies
- MD5: 6955b903f340c30508847af60905eb4b
- Git tag: dataset-frozen-v1.6.8 (supersedes v1.6.7)
- Built by: scripts/apply_v168.py (revert A1/A5 coin-flips; NO id/value change)

## v1.6.7 -> v1.6.8 - revert the A1/A5 coin-flips (Codex chose originals; Sacha reverted)

A1 85207525286 92 CONTENT->QUALITY (breadth blanked): ASRS "misleading" = coverage criterion,
compatible-with-true -> quality, excluded from prevalence. A5 85160248068 x2 (3.03/1.86)
EXPOSURE->OTHER: click/engagement share, not diet; the study's impression-level EXPOSURE rows
(2.05/0.72, % of results SHOWN) STAY EXPOSURE as the clean diet-share. Both were the ORIGINAL
codings, independently re-chosen by the Codex (gpt-5.6-terra) cross-check. Negligible on headlines
(CONTENT loses a 92% outlier; EXPOSURE keeps the study via 2.05/0.72).
---

# FROZEN DATASET v1.6.7 (2026-08-04)
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.6.7_frozen.csv
- Rows: 675 estimates / 314 studies
- MD5: 6fcd0743c16d2208f1b3b2386b0b4f53
- Git tag: dataset-frozen-v1.6.7 (supersedes v1.6.6)
- Built by: scripts/apply_v167.py (n-field mis-parse fixes; NO value/construct change)

## v1.6.6 -> v1.6.7 - n-field mis-parse fixes (2026-08-04 triple-check)

parse_n takes the first integer; 5 rows led with a numerator/subgroup count, giving a wrong tiny n
that distorted the n-restricted analyses. Fixed: 85114317455 x2 (EXPOSURE, n 8-agents -> 11038
links, the share denominator), 85148963619 (OTHER Kennedy, n 1 -> 98612), 85105511315 x2 +
105027856675 x2 (denominator unreported -> blanked, so they drop from n-restricted rather than
enter wrong). Suffix handling verified correct (3.7M -> 3,700,000). Headlines (full-set medians)
unaffected; the EXPOSURE small-study test is slightly more accurate.

---

# FROZEN DATASET v1.6.6 (2026-08-04)
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.6.6_frozen.csv
- Rows: 675 estimates / 314 studies
- MD5: 967b59354e70ba8383597cc3a3fc8689
- Git tag: dataset-frozen-v1.6.6 (supersedes v1.6.5)
- Built by: scripts/apply_v166.py (+year/+era/+recall_subtype enrichment; analysis-neutral)

## v1.6.5 -> v1.6.6 - analysis-enrichment columns (data-improvement pass)

Additive derived columns, no value/construct/denom change (headlines unchanged): `year` (data
end-year), `era` (<=2016 / 2017-2019 / 2020-2021 / >=2022, for the temporal moderator), and
`recall_subtype` (RECALL rows: exposure vs sharing self-report). The outlier-lead verification found
NO clean misclassifications (all 4 source-checked and held); the real finding is the RECALL
exposure/sharing substructure now made explicit in recall_subtype (exposure-recall median 55.7% vs
sharing-recall 17.1% vs combined 50.3%).

---

# FROZEN DATASET v1.6.5 (2026-07-30)
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.6.5_frozen.csv
- Rows: 675 estimates / 314 studies
- MD5: ee43710fbe6292ada06a64ed505895fd
- Git tag: dataset-frozen-v1.6.5 (supersedes v1.6.4)
- Built by: scripts/apply_v165.py (B2 concentration labels; analysis-neutral)

## v1.6.4 -> v1.6.5 - B2 concentration group labels (audit decision, analysis-neutral)

The B2 re-extraction (agent read all 3 papers) found the 5 field-incomplete CONCENTRATION shares
belong to QUALITATIVELY-defined groups (verified/top-N accounts, deplatformed set), NOT clean volume
percentiles -> conc_group_pct stays BLANK (filling would wrongly enter them in the top-X%->Y%
percentile table; they are correctly excluded). Only conc_group_label documented. Pipeline output
unchanged. The top-1%->70% headline (k=8) uses only genuine volume-percentile studies.

---

# FROZEN DATASET v1.6.4 (2026-07-30)
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.6.4_frozen.csv
- Rows: 675 estimates / 314 studies
- MD5: 1c827067f9ab11473a38481c6042a246
- Git tag: dataset-frozen-v1.6.4 (supersedes v1.6.3)
- Built by: scripts/apply_v164.py (Sacha's audit-decision construct recodes; NO id/value changes)

## v1.6.3 -> v1.6.4 - audit-decision construct recodes (Sacha, audit_decisions.html)

9 construct recodes: 85207525286 QUALITY->CONTENT (breadth=misleading; Sacha overrode his own IRR
QUALITY call, ASRS clinical ground truth); 85066941307 x2 REACH->OTHER (conditional-probability
quantities, non-pooled); 85069463611 CONTENT->SHARING + 85100218180 CONTENT->SHARING (shared-stream
denominators); 85160248068 x2 OTHER->EXPOSURE (clicks/visits = consumption); 85162702221
EXPOSURE->OTHER (page-likes = engagement, kept out of SHARING/EXPOSURE pools); 85148963619 13.4
CONCENTRATION->OTHER (single actor @RobertKennedyJr, not a distribution). NO id/value changes.
Kept OPEN: B2 concentration group%/share% re-extraction (analysis-neutral, separate pass).

---

# FROZEN DATASET v1.6.3 (2026-07-30)
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.6.3_frozen.csv
- Rows: 675 estimates / 314 studies
- MD5: 7f38ca720b5aa3d587ba0572980871ee
- Git tag: dataset-frozen-v1.6.3 (supersedes v1.6.2)
- Built by: scripts/apply_v163.py (audit fixes: sure/objective subset)

## v1.6.2 -> v1.6.3 - aggressive-audit fixes (verified/objective subset)

From docs/audit_2026-07-30/AUDIT_REPORT.md (4 parallel audit agents + scout). Applied only the
verified/deterministic items: (1) DROPPED 2-s2.0-85189974015, a forced-exposure EXPERIMENT (planted
article, share-clicks + intention -- named exclusion categories); (2) DROPPED 3 phantom CONTENT
sub-slices of 2-s2.0-85214504236 (82/48/42 carried the 85% headline quote; kept 85 only); (3)
BLANKED breadth on 16 source-level residue rows (completes the v1.6.0 pure-veracity rule; legacy in
breadth_legacy); (4) conc fields on 2-s2.0-85160248068 already complete (no-op). 675/314. NO
value/construct/denom_class change on survivors. Judgment-call audit items (construct miscodes,
concentration re-extraction on 85148963619/85159153364/85195353413, D09 QUALITY-vs-CONTENT
re-confirm) are FLAGGED in the audit report, NOT applied.

---

# FROZEN DATASET v1.6.2 (2026-07-30)
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.6.2_frozen.csv
- Rows: 680 estimates / 315 studies
- MD5: 9c3cbee67039dcb0a52f5d3f40989673
- Git tag: dataset-frozen-v1.6.2 (supersedes v1.6.1)
- Built by: scripts/apply_v162.py (add 2 requested papers + RoB shard_99_manual.csv)

## v1.6.1 -> v1.6.2 - add Faker Island (Berriche et al. 2026) + sciadv (Bergeron-Boutin/Nyhan et al. 2026)

Two author-requested papers, both confirmed eligible with codeable estimates and given Hoy RoB
appraisals. sciadv (Meta-2020 consortium, US FB/IG): EXPOSURE 1.1% FB + 0.1% IG whole-feed
(enters the whole-diet backbone) + CONCENTRATION top 23%->80%; RoB LOW. Faker Island (French
Twittersphere): CONTENT 0.05% of tweets + REACH 0.9% sharing-reach (% of accounts that shared >=1;
construct confirmed by Sacha); RoB MODERATE (Twitter media-sharer population non-representative).
5 rows, 2 studies. sciadv's whole-feed EXPOSURE enters the backbone -> EXPOSURE/backbone medians
may shift.

---

# FROZEN DATASET v1.6.1 (2026-07-30)
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.6.1_frozen.csv
- Rows: 675 estimates / 313 studies
- MD5: 01f36b9d8cb0a6f2ea5efdcdc914282f
- Git tag: dataset-frozen-v1.6.1 (supersedes v1.6.0)
- Built by: scripts/apply_v161.py (denom_scope verification; analysis-neutral, no value/construct/denom_class change)

## v1.6.0 -> v1.6.1 - denom_scope verification pass

The v1.6.0 denom_scope column was rule-inferred for the 90 selection-shaped rows. A source-anchored
verification (agent + spot-check) corrected 17 rows across 5 studies: 85131964464->political_news
(Bolsonaro tweet stream), 85160248068->all_media (whole Google-Search diet), 85177420309->topical
x12 (conspiracy-query search results), 85115858008 + 85213958624 ->all_media (whole message/cascade
streams; low-confidence, flagged). denom_scope is not yet used in analysis -> headline numbers and
all pipeline outputs unchanged; this is data-quality only.

---

# FROZEN DATASET v1.6.0 (2026-07-30)
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.6.0_frozen.csv
- Rows: 675 estimates / 313 studies
- MD5: 2a03cb27ec83cf22cf08c069eb91d4a0
- Git tag: dataset-frozen-v1.6.0 (supersedes v1.5.8)
- Built by: scripts/apply_v160.py (taxonomy overhaul + 2 integrity exclusions; NO value/construct changes)

## v1.5.8 -> v1.6.0 - taxonomy overhaul + full-re-screen exclusions

Full-corpus authenticity re-screen (all 315 studies) found NO fakes beyond the 3 known; the 2 new
ones (v1.6.0 drops them) were from the earlier metadata-gap re-screen: OA-W7154838691 (fake
"Qualitative Research Journal", 250x4 split), OA-W7133343648 (predatory agri journal). All 3 fakes
entered via the OpenAlex OA-W71 path.
Taxonomy critique (Sacha's decisions): (a) breadth split-clean -> pure veracity {fabricated, false,
misleading}; unreliable_source (dup of classification_level=source_level) and low_quality (QUALITY
territory) blanked, 284 rows; old values in breadth_legacy. (b) denominator two-axis: + denom_scope
(scope only) and + denom_selection (curated/single_source), so a curated single-issue study is now
denom_scope=topical AND denom_selection=curated. (c) question_type + diet_type deprecated in the
codebook (redundant/never-controlled), columns kept for provenance. NO value/construct/denom_class
changes; headline medians unaffected. The breadth MODERATOR now measures veracity only (see re-eval).

---

# FROZEN DATASET v1.5.8 (2026-07-30)
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.5.8_frozen.csv
- Rows: 677 estimates / 315 studies
- MD5: e95ff1f2b78fd1e1bea138490214f12f
- Git tag: dataset-frozen-v1.5.8 (supersedes v1.5.7)
- Built by: scripts/apply_v158.py (drop 1 fabricated study + 2 denom_class recodes)

## v1.5.7 -> v1.5.8 - round-2 human-IRR adjudication (Sacha, 2026-07-30)

Batch-2 IRR surfaced 3 items where the dataset did not hold; Sacha adjudicated all 3 from full text.
1. DROPPED OA-W7125772788 (Leman 2025) - likely FABRICATED/AI-generated paper in a predatory
   maiden-issue journal (contradictory method: 7,234 NLP points vs 282 survey respondents;
   ChatGPT/Meta AI as "platforms"; non-inferiority Delta=-1.5 with 95% CI [0.2,1.6]; Verlumun J.
   AI Gender & Cultural Studies Vol1 Iss1, Zenodo DOI). Caught by Laura's "no usable estimate" +
   Sacha's full read. 1 RECALL row, already HIGH RoB. RECALL k 27->26.
2. W4414446446 (x3 sibling rows) denom_class population -> curated_sample (content analysis of
   broadcast episodes; population is for people).
3. 2-s2.0-85159486270 denom_class curated_sample -> topical (>1000-view threshold is an inclusion
   filter, not a set-defining truncation; author override of the rank-truncation rule, documented).
RECALL main-set median 50.4->50.3 (study-level 54.0 holds); no CONTENT/EXPOSURE headline move.
Gates PASS. SECOND-ORDER: E12 passed screening+extraction+RoB -> corpus-integrity sweep parked.

---

# FROZEN DATASET v1.5.7 (2026-07-28)
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.5.7_frozen.csv
- Rows: 678 estimates / 316 studies
- MD5: 0f10b6d7897a1f86f42d13f4784fb5e9
- Git tag: dataset-frozen-v1.5.7 (supersedes v1.5.6)
- Built by: scripts/apply_v157.py (20 denom_class cells; NO value/construct changes)

## v1.5.6 -> v1.5.7 - reconcile the 5 mixed-denominator spillover studies

The v1.5.3 mixed-denominator detector left 10 studies marked REVIEW. Disposition
(qa/mixed_denom_review_2026-07-28.md + decision page, SACHA APPROVED all five 2026-07-28):
5 studies are legitimately multi-denominator (different measures); 5 were same-instrument splits
where a targeted adjudication corrected one row and stranded identical-instrument siblings.
Reconciled by rule (selection-shaped sets -> curated_sample; NewsGuard news-outlet census ->
news_diet): 85127039075 (1), 85177420309 (10), 85192635397 (3, political_news->news_diet),
2603.11058 (5), PMID-41189872 (1). All CONTENT rows; headlines cannot move. Gates PASS.

---

# FROZEN DATASET v1.5.6 (2026-07-24) - SUPERSEDED by v1.5.7, snapshot preserved
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.5.6_frozen.csv
- Rows: 678 estimates / 316 studies
- MD5: f93d097182576a890380b86a81c2ba26
- Git tag: dataset-frozen-v1.5.6 (supersedes v1.5.5)
- Built by: scripts/apply_v156.py (drop 1 duplicate study row; NO other changes)

## v1.5.5 -> v1.5.6 - remove duplicate study (same paper under two IDs)

Found while vetting the human IRR sample: two Part-2 items pointed at byte-identical PDFs
(MD5 eae327e11c0d55b8efb23d0f95096770). `OA-W4394831676` (abstract-only OpenAlex sweep row) and
`NEW-jadara-2022` (full-text re-ingest, 2026-07-15) are the SAME paper carrying the same estimate
(81.6% RECALL, Levant COVID survey). Kept the full-text twin (n=6,910, complete moderator coding);
dropped the abstract-only row. Corpus-wide duplicate scan (PDF MD5 + shared-quote-prefix across IDs)
found no other duplicated study. RECALL-only, so CONTENT/EXPOSURE headlines cannot move. Gates PASS.

---

# FROZEN DATASET v1.5.5 (2026-07-24) - SUPERSEDED by v1.5.6, snapshot preserved
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.5.5_frozen.csv
- Rows: 679 estimates / 317 studies
- MD5: a64386c3eb0aa925a1d296657a383819
- Git tag: dataset-frozen-v1.5.5 (supersedes v1.5.4)
- Built by: scripts/apply_v155.py (normalise 3 legacy vocab cells; NO value changes)

## v1.5.4 -> v1.5.5 - normalise 3 legacy vocab cells

The v1.5.0 vocabulary normalisation missed 3 cells in two later-added RECALL studies; found while
vetting the human IRR sample (they were ungradeable: a coder cannot produce a code that isn't in the
controlled list). All RECALL, so no headline moves. Gates PASS.
- NEW-moreno-jmirderma denom_class at_risk_sample -> population (a defined group of people; its
  non-representativeness is a RoB property, not a denominator class)
- NEW-jadara-2022 denom_class survey_selfreport -> population (respondents are people)
- NEW-jadara-2022 breadth misinfo_broad -> false ("read Covid info that turned out untrue")
Controlled vocabularies are now fully standard (0 non-standard denom or breadth values remain).

---

# FROZEN DATASET v1.5.4 (2026-07-24) - SUPERSEDED by v1.5.5, snapshot preserved
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.5.4_frozen.csv
- Rows: 679 estimates / 317 studies
- MD5: 0d0ddc3245141c0f90463e2bd4ae558c
- Git tag: dataset-frozen-v1.5.4 (supersedes v1.5.3)
- Built by: scripts/apply_v154.py (full-corpus cross-model adjudication; NO value changes)

## v1.5.3 -> v1.5.4 - full-corpus cross-model error-detection sweep

**0 value_pct changes, row order preserved** (gates in the build script). 22 denom_class changes.
Changelog `qa/v154_changelog.csv`; verdicts + verbatim quotes in `qa/fulladjud/out_*.csv`.

**What happened.** GPT-5.6 Terra Thinking (via Perplexity) coded the ENTIRE corpus blind to our coding
(667/667 rows, run by Sacha as manual paste batches). Corpus-level agreement vs our coding: construct
kappa 0.75, breadth 0.69, denom_class 0.53 - the independent-model reliability number on the whole
corpus, not a sample. The pass doubled as an error-detection sweep: 263 load-bearing disagreements were
triaged to 49 HIGH-priority rows in two transition patterns with a confirmed track record of being our
error (topical->curated_sample; news-wide widening). Six source-anchored agents re-read each.

**Result: our coding was wrong on 33 of the 49 (67%) HIGH-priority rows** (collapsing to 22 distinct
frozen rows). FRAMING: 67% is the hit rate WITHIN a queue pre-selected for likely-ours transitions, NOT
across the corpus - it validates the priority filter, it does not mean the dataset is 67% wrong.
Corpus-wide GPT agreed with our denom_class on 64% of all rows, and most disagreements were GPT applying
looser conventions (over-calling all_media, assigning denominators to n/a concentration rows), which we
did NOT apply.

**Changes:** political_news->news_diet 10 (all-news denominators coded politics-restricted - incl. the
Altay/Nielsen/Fletcher NewsGuard country rows, the Reddit and Pierri all-news panels; these subdivide
the whole-diet backbone), topical->curated_sample 8 (rank-truncated top-N / multi-topic / misinfo-seeded
baskets), single_source->all_media 3, political_news->curated_sample 1. Whole-diet backbone 263->265.

**A rule the agents sharpened (add to the codebook's hard cases):** a misinfo-weighted or rank-truncated
instrument that builds the NUMERATOR over a clean single-issue denominator stays `topical`; it becomes
`curated_sample` only when the truncation/seeding/multi-topic scope defines the sampled SET itself. This
correctly kept several large single-issue prevalence studies (COVID/GMO/vaccine Boolean corpora) as
`topical` while moving genuine top-N baskets to `curated_sample`.

---

# FROZEN DATASET v1.5.3 (2026-07-23) - SUPERSEDED by v1.5.4, snapshot preserved
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.5.3_frozen.csv
- Rows: 679 estimates / 317 studies
- MD5: c5abcb864b2a5eb58154a242a2709b02
- Git tag: dataset-frozen-v1.5.3 (supersedes v1.5.2)
- Built by: scripts/apply_v153.py (second-opinion re-check + spillover repair; NO value changes)

## v1.5.2 -> v1.5.3 - second-opinion re-check + spillover repair

**0 value_pct changes, row order preserved** (gates in the build script). 8 denom_class changes.
Changelog `qa/v153_changelog.csv`.

**Re-check of the 5 low-confidence adjudications.** An independent second opinion, briefed not to
defer to the first verdict, agreed on 3 and overturned 2:
- `105021775752` row 468 curated_sample -> **political_news** (back to our ORIGINAL coding). "Most
  shared links" turned out to be a label for a data type, not rank truncation; the source describes
  "close to 3 million tweets ... that contain a link to a news article", so a natural total exists.
- `2603.11058` row 531 topical -> **curated_sample**. Five domains rather than one issue, and roughly
  half the retrieval keywords are misinformation-associated, so the denominator is tilted by
  construction.

**Spillover repair - the more valuable finding.** The first adjudication corrected each FLAGGED row
but left sibling rows of the SAME study and SAME measure in the old class, leaving single studies
split across two denominator classes: `85081743293` rows 629-632 (Trump/Clinton breakdowns of the
same news-diet quantity) and `85168520853` rows 607-608 (gender breakdown of the same 1,534
statements). Fixed. These are targeted, evidence-backed edits, NOT blanket propagation - a study
legitimately can carry different denominators across estimates, which is the point of estimate-level
coding.

**A detector now exists** (`qa/v153_mixed_denom_studies.csv`) listing every study spanning more than
one denominator class, separating adjudication-touched studies (likely spillover) from the rest
(often legitimate - e.g. a study whose REACH rows are `population` while its diet-share rows are
`news_diet`). 22 studies span multiple classes; 10 are flagged REVIEW.

**Two codebook rules added** from this round: a misinformation-weighted retrieval instrument makes the
denominator `curated_sample` however large the corpus; and a keyword corpus spanning several unrelated
issues is not `topical`.

---

# FROZEN DATASET v1.5.2 (2026-07-23) - SUPERSEDED by v1.5.3, snapshot preserved
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.5.2_frozen.csv
- Rows: 679 estimates / 317 studies
- MD5: f24159861327825de61f0d8feda5a45d
- Git tag: dataset-frozen-v1.5.2 (supersedes v1.5.1)
- Built by: scripts/apply_v152.py (denominator adjudication + CONCENTRATION/OTHER n/a; NO value changes)

## v1.5.1 -> v1.5.2 - denominator adjudication + `denom_class` n/a for CONCENTRATION/OTHER

**0 value_pct changes, 0 rows added/removed, row order preserved** (gates in the build script).
Changelog `qa/v152_changelog.csv`.

### (1) Source-anchored adjudication of 34 disputed rows
The cross-model check disputed our `denom_class` on 35 items (34 distinct rows; one row was flagged
by two items and received the same verdict twice). Four agents re-read each study's SOURCE and returned
a verdict with a verbatim supporting quote, explicitly told that WE might be the ones in error.

**Result: KEEP_OURS 14 - ACCEPT_CHALLENGE 13 - THIRD_OPTION 7. Twenty of the 34 rows changed.**
Transitions: `topical -> curated_sample` 13 - `political_news -> news_diet` 5 -
`political_news -> curated_sample` 1 - `topical -> single_source` 1.

We were wrong on 20 of 34 disputed rows. The dominant error was exactly the one our own codebook
already legislated against: **rank-truncated top-N sets coded as `topical`** ("the 118 most widely
viewed videos", "top 10 articles for each keyword", "the first 50 videos ranked by relevance", "the
top 100 most popular videos"). These are `curated_sample` by our stated rule; the rule existed but had
not been applied consistently. The adjudicators converged on a clean operational line, now the
governing test: **exhaustive or probability-sampled keyword corpus = `topical`; rank-truncated top-N
by views/shares/popularity/relevance = `curated_sample`.**

The `all_media` challenges were almost all rejected - but they correctly pointed at a real problem in
the other direction: 5 rows were neither `political_news` nor `all_media` but **`news_diet`**, the
category added in v1.5.1 (Cordonnier's information-time denominator, NewsGuard UK all-topic outlet
tweets, Facebook posts from a 12,000-outlet list, all national-news links, Guess et al.'s "overall news
diets"). So v1.5.1 caught 11 news-wide rows and adjudication found 5 more.

### (2) `denom_class` = "n/a" for CONCENTRATION and OTHER (52 rows)
The field answers "what is this a share OF" for a PREVALENCE estimate. A concentration estimate has the
form "top X% of USERS account for Y% of ACTIVITY" - a structurally different object. The existing values
proved the field was never meaningful here: CONCENTRATION rows were spread across population 14 /
curated_sample 7 / topical 4 / single_source 2 / political_news 1. Forcing a value would invent data no
analysis consumes. "n/a" is honest and makes the exclusion explicit and machine-checkable. Concentration
retains `conc_unit`, `conc_group_pct`, `conc_share_pct`.
Found because an independent rater had to guess a rule that did not exist - that stratum scored raw
.053 agreement (1 of 19).

Final distribution: topical 300 - population 132 - political_news 100 - n/a 52 - curated_sample 35 -
single_source 28 - news_diet 16 - all_media 14 (+2 legacy singletons).

---

# FROZEN DATASET v1.5.1 (2026-07-23) - SUPERSEDED by v1.5.2, snapshot preserved
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.5.1_frozen.csv
- Rows: 679 estimates / 317 studies
- MD5: c3108ee3a6d9e93ab7cacd5f2aee3d9c
- Git tag: dataset-frozen-v1.5.1 (supersedes v1.5.0)
- Built by: scripts/apply_v151.py (adds `news_diet` denominator class; NO value changes)

## v1.5.0 -> v1.5.1 - new `news_diet` denominator class (Sacha approved 2026-07-23)

**0 value_pct changes, 0 rows added/removed, row order preserved, whole-diet backbone membership
unchanged at 285 rows** - all asserted by gates in the build script. Changelog `qa/v151_changelog.csv`.

**Why.** The cross-model verification pass (Perplexity/GPT-5.6) disagreed with our `denom_class` on the
same study three times in the same direction. It was right: news-wide denominators were split across two
categories. `all_media` held *"all news website visits 2017"* while `political_news` held *"% of all news
web traffic"* - the same quantity under two labels. Our own audits had missed this.

**Why it mattered enough to refreeze.** `all_media` also holds genuinely whole-media denominators
(Allen-style *"total daily media consumption across TV, desktop and mobile"*, ~0.15%), whereas an
all-news denominator gives ~3.4% for the same phenomenon. That ~20x gap is driven purely by the
denominator and is the single cleanest demonstration of the review's own thesis. Merging the bins would
have destroyed it; leaving them muddled confounded the moderator analysis. So: three explicit widths -
`all_media` (news AND non-news) / `news_diet` (all news, any topic) / `political_news` (politics only).

**11 rows / 5 studies recoded** to `news_diet`: W4293124965 x4, 85209547248 x3, W7146985142 x2,
105019357120, 85083323285. Final distribution: political_news 112 - news_diet 11 - all_media 14.

One edge case worth recording: `85083323285` (Allen et al. 2020) has denominator *"total news
consumption (TV + online news minutes)"*. A first pass held it back because the rule saw "TV" and
inferred non-news media. That was wrong - it is a NEWS diet measured across two delivery channels. The
classifier now lets an explicit news restriction override channel words. Naming a channel is not the
same as widening the denominator.

Codebook section (d) rewritten with a single governing question, a five-step decision tree, the
three-way width table, and the recurring hard cases (surveys -> population; most-shared ->
curated_sample; platform census != all_media; prefer the narrower reading when ambiguous).

---

# FROZEN DATASET v1.5.0 (2026-07-23) - SUPERSEDED by v1.5.1, snapshot preserved
Estimate dataset frozen. Downstream analysis refers to THIS snapshot.
Each frozen version is its own immutable file on disk, each git-tagged.

- File: data/extract_v2/estimates_v1.5.0_frozen.csv
- Rows: 679 estimates / 317 studies
- MD5: c730b0d93b5de65613af9ac2a72e0a00
- Git tag: dataset-frozen-v1.5.0 (supersedes v1.4.12)
- Built by: scripts/apply_v150.py (schema hygiene; NO value changes)

## v1.4.12 -> v1.5.0 — schema hygiene (2026-07-23 project review)

Structural and documentary only. **0 value_pct changes, 0 rows added or removed, row order
preserved** — asserted by gates inside `apply_v150.py`, not merely claimed. 55 -> 51 columns.
Changelog `qa/v150_changelog.csv` (59 entries).

- **NEW `value_kind`** (proportion 662 · scale_score 8 · per_capita_intensity 6 ·
  range_not_point 3). `value_pct` itself was already clean, but 17 rows deliberately leave it
  blank and park a NON-proportion quantity in `value_raw` (DISCERN/GQS/VIQI scale scores,
  per-capita intensity counts, per-item ranges). That exclusion rule previously existed only
  as prose inside the `flag` column, so every pooled statistic depended on remembering it.
  Pooled analyses now filter `value_kind == 'proportion'` explicitly.
- **`ground_truth` normalised to the controlled vocabulary** (5 codes: researcher_coding 293 ·
  domain_list 255 · self_report 57 · fact_checker 48 · classifier 26). 14 rows previously held
  entire prose sentences as the *category value*, which silently fragmented every groupby;
  `newsguard` and `domain_list (Decodex)` folded into `domain_list`; `human_coded` into
  `researcher_coding`. Nothing lost — original strings preserved in **NEW `ground_truth_detail`**
  (44 rows).
- **Workflow columns moved out of the analysis file** (`v12_action`, `v12_note`, `v12a_status`,
  `v12a_action`, `v12a_note`) -> `qa/v150_workflow_ledger.csv`. These are 77-94% empty
  provenance residue from the v1.2 campaign and belong with the audit trail.
- **All-empty columns dropped:** `period_label`, `within_misinfo_content` (both 100% blank).
- **`diet_type` NA-token soup normalised** (NA / N/A / na -> empty).
- **NEW `intersection_duplicate` flag.** W4205602257 reports one cell twice — once in its
  political series ("political=Independent (age 65+)") and once in its age series
  ("age=65+ (political independents)"), both 3.7. Both rows are KEPT (deleting either breaks a
  reported series); the flag lets demographic analyses de-duplicate. Follows the project's
  established keep-and-flag convention.

### Deliberately NOT done in this freeze
`denom_type` and `denom_class` were expected to be redundant and slated for collapse. They are
not: they genuinely **disagree on 80 rows** (e.g. 29 rows `denom_type=population` /
`denom_class=topical`, 15 the reverse). Collapsing would have destroyed evidence of a real
coding inconsistency and required ~80 unreviewed coding decisions. Both columns are retained,
**`denom_class` is canonical for analysis**, and the conflicts are enumerated in
`qa/v150_denom_conflicts.csv` for a source-anchored adjudication pass.

---

# FROZEN DATASET v1.4.12 (2026-07-23) — SUPERSEDED by v1.5.0, snapshot preserved
- File: data/extract_v2/estimates_v1.4.12_frozen.csv
- Rows: 679 estimates / 317 studies
- MD5: eafa672e8f97c2e0cf54c6f04fd012c3
- Git tag: dataset-frozen-v1.4.12
- Built by: scripts/apply_v1412.py (comprehensive-audit consistency cleanups)

## v1.4.11 -> v1.4.12 — full multi-dimension audit cleanups (Sacha: audit all dimensions)
`scripts/audit_all_dimensions.py` checked vocab + cross-field consistency + numeric integrity across all 679 rows:
0 value errors (the 2 'high' flags were stale value_raw denominators, value_pct correct). Consistency cleanups
(25 cells, 0 value_pct changes): filled breadth=unreliable_source + denom_class=political_news on 12 blank SHARING
rows of 105027856675 (matches its 8 siblings); value_raw /1313->/1211 on 85055756722 (value_pct already right);
cleared 7 stray conc_unit on OTHER rows; within_misinfo_content FALSE->blank (3). orient_no_party flags (19) were
false positives (orientation on content/actor rows, correct).

## v1.4.10 -> v1.4.11 — concentration taxonomy cleanup (Sacha: move + cleanly separate)
Moved the 5 SOURCE-concentration rows OTHER->CONCENTRATION (85060549676/85078014559/85148963619/W7146985142 x2:
'top-N sources/domains -> Y% of activity'). Standardized `conc_unit` to a clean binary: USER (top X% of
people/accounts -> Y%; 23 rows) vs SOURCE (top-N sources/domains -> Y%; 5 rows) — fixing 5 rows previously
mislabelled 'news_source' that are actually user concentration. CONCENTRATION now 28 rows. So the headline
"top 1% of people -> 70%" uses conc_unit=user ONLY; source concentration is reported separately. 0 value changes.

## v1.4.9 -> v1.4.10 — full-rigour construct audit (6-agent source adjudication, Sacha 2026-07-23)
Comprehensive construct-consistency scan (60 flags) -> 6 agents re-read each flagged study's SOURCE and adjudicated.
Result: coding overwhelmingly correct (~49/60 flags were heuristic false positives confirmed against source).
APPLIED (5 rows, 0 value changes): OA-W3113799821 EXPOSURE->OTHER (search-query demand, Sacha-approved); 4
reach_subtype sharing->exposure (105039619015, 85152674280 x3 — 'visited >=1 website' = exposure). HELD for Sacha:
5 OTHER->CONCENTRATION candidates (85060549676/85078014559/85148963619/W7146985142 x2) — genuine source-concentration
'top-N sources -> Y%' statements, but moving them touches the concentration headline AND the conc_unit field is itself
inconsistent (existing 'news_source' rows actually describe user/account concentration). Needs a taxonomy decision.
Full adjudication log: qa/construct_adjudication.csv. Changelog qa/v1410_changelog.csv.

## v1.4.8 -> v1.4.9 — audit continuation (Sacha 2026-07-23)
Systematic construct-consistency + value-vs-quote audit. RESULT: construct coding clean, 0 value errors
(all 24 value-vs-quote flags were table-sourced values / regex artifacts like '.66%' or spelled 'Seventy percent').
ONE fix: 85127039075 11% EXPOSURE -> CONTENT (view-weighted content prevalence in a topical 122-video sample;
same pattern as 85085201199 in v1.4.8). No value change. OPEN judgment call flagged to Sacha: OA-W3113799821
'1% of Bing COVID queries are misinfo' is coded EXPOSURE but is query-demand, not diet-exposure (CONTENT or OTHER?).

## v1.4.7 -> v1.4.8 — small coding corrections (Sacha tooltip review 2026-07-22)
5 rows, NO value_pct changes. (1) 85085201199: 24.1% EXPOSURE -> CONTENT (view-weighted content prevalence in a
topical 69-COVID-video sample; denominator = views of that curated set, not audience diet). (2) 85066894147: fixed
stale measure_type period labels (all said 'before conventions') to match each time point (before conventions /
after nominations / right before election). (3) 85152674280: reach_subtype sharing->exposure ('visited >=1 website').
(4) 85060549676: 'political=left' row's political_orientation mixed->left. Changelog qa/v148_changelog.csv.

## v1.4.6 -> v1.4.7 — CONCENTRATION standardization + engagement/exposure fix (Sacha review 2026-07-22)
CONVENTION now enforced for CONCENTRATION: `value_pct` = SHARE OF ACTIVITY (% of exposure/sharing accounted for
by the top group); `conc_group_pct` = POPULATION FRACTION (top X%). Fixed flipped rows where value_pct held the
population % instead of the activity % (85194733750 0.3->80; 85160248068 31.3/25.1->90) and filled blanks
(85060549676 ->80.0/79.8; 85081743293 ->62). Backfilled population fractions for consistency. Flagged one
atypical measure (85195353413 deplatformed-user share). Also RECODED 105017599346 EXPOSURE->SHARING (its
'% of engagement directed at low-quality domains' is engagement-share, question_type=engagement, not diet-exposure;
consistent with the project's engagement->SHARING convention). Changelog qa/v147_changelog.csv.

## v1.4.5 -> v1.4.6 — descriptive completeness (additive; NO value changes)
Phase B component 1 (descriptive + diagnostic pass, `scripts/phaseB_descriptives.py`) surfaced
completeness gaps; this freeze closes them. ONLY `measure_type` and `topic` columns differ from
v1.4.5 (verified: 0 value_pct changes, id order preserved).
- **measure_type backfill:** 67 rows across 21 studies had a blank `measure_type` (a field populated
  for most rows but not all). Filled from source quotes / Table arithmetic (`scripts/build_v146_measuretype.py`,
  index+id+value guarded; `qa/v146_measuretype.csv`). measure_type now 100% populated.
- **topic moderator:** was populated on only 14% of rows. Coded ALL 317 studies via a 16-agent LLM
  pass (taxonomy `docs/topic_taxonomy.md`, quote-anchored; `qa/topics_v146.csv`), one primary topic
  per study. Distribution: health_other 136, covid19 69, general_news 48, politics_elections 37,
  vaccines 11, other 6, science_other 4, war_geopolitics 3, crime_society 2, economy_finance 1
  (climate/immigration = 0). topic now 100% populated.
- **Guess-2019 dedup:** dropped 1 within-study duplicate (row 492 = 'Trump supporters 18.1%',
  a paraphrase of the verbatim '18.1% of Republicans' in row 583; demographic row, out of headline).
  `qa/v146_dedup.csv`. 680 -> 679 rows.

## v1.4.4 -> v1.4.5 — exclusion re-check + blind reliability + n fix

## v1.4.4 -> v1.4.5 — exclusion re-check + blind reliability + n fix
Three additional rigour passes (Sacha 2026-07-22):
- **Exclusion re-check (criteria drift):** re-screened all drop ledgers (351 records/343 studies) for studies dropped
  under OLD criteria that the EXPANDED criteria now accept; agent re-adjudicated 17 borderline drops -> **2 re-include,
  15 keep-dropped**. RE-INCLUDED **85138494787** (Silver vaping/COVID; the old drop hit only a secondary Pew citation,
  but the paper has its own topical content-prevalence: 9.8% of top-retweeted tweets endorse 'nicotine prevents COVID',
  22.5% of top URLs). **85042209380** (Nelson & Taneja) re-screened but KEPT DROPPED (L13 absolute-reach + concentration
  not codeable; documented `qa/v145_rejections.csv`). The re-check also corrected a keyword false-candidate
  (85130786472 = 'themes susceptible to disinfo' = stance, correctly stays dropped).
- **Blind independent re-extraction (reliability):** 54-study sample, 3 agents extracted each value FRESH from source
  WITHOUT seeing our coding. 79% exact auto-match; the 21% non-matches were ALL multi-estimate studies where the two
  coders picked different VALID values (or unit/range representations) -> **no coding errors found** (effective
  agreement ~100% on the same quantity). Surfaced one completeness gap (85066894147 time points) -> fixed.
- **n fix:** 85055756722 n=1313 (survey total) -> ~1211 (sharing-item respondents; values were verbatim-correct).
- **85066894147:** added the missing 20% (before conventions) and 40% (before election) time points; the existing
  30%-row was mislabeled 'before conventions' -> relabeled 'after nominations' (keep-all, jc23).
Gates: validate_frozen + validate_prisma PASS.

---

# FROZEN DATASET v1.4.4 (2026-07-21) — SUPERSEDED by v1.4.5, snapshot preserved
- File: data/extract_v2/estimates_v1.4.4_frozen.csv
- Rows: 676 estimates / 316 studies
- MD5: 492d3f48bfb4357d5d19e22642eec841
- Git tag: dataset-frozen-v1.4.4 (supersedes v1.4.3)
- Built by: scripts/apply_v144.py (highest-rigour re-audit cleanup; scripts/reaudit_v143.py = the audit)

## v1.4.3 → v1.4.4 — highest-rigour final re-audit cleanup
Sacha requested a maximum-rigour re-audit. Three pillars: (A) deterministic convention-completeness +
schema/vocab/value integrity, (B) apply-integrity (all excluded/merged studies verified gone, no field
corruption — PASSED), (C) fresh hidden-duplicate detection. Findings report `qa/reaudit_v143_findings.csv`;
cleanup applied via `scripts/apply_v144.py`:
- **1 hidden DUPLICATE caught & deduped:** SUPP-ice2026-antimicrobial == 105032253077 (identical verbatim
  quote/value/N; the "ice2026" name matches the DOI 10.1017/ice.2026...). 3 other title/value near-matches
  investigated = genuinely different papers (US vs EU elections; Pinterest vs Twitter; stroke-2025 vs covid-2020).
- **Convention-completeness backfills** (the "applied-to-some-but-not-all" gap): reach_subtype on 33 REACH rows,
  sharing_subtype=content_share on 15 SHARING rows, conc-field normalization on 16 (strip %, prose→conc_group_label),
  1 vocab fix, 2 orphan/orientation fixes. New col: conc_group_label.
- Re-audit re-run on v1.4.4: 0 ERROR, remaining 4 WARN/4 INFO all benign (false-alarm title pairs, Figeac
  ‘overall’ rows correctly without a party orientation, legit OTHER rows). Gates: validate_frozen + validate_prisma PASS.

---

# FROZEN DATASET v1.4.3 (2026-07-21) — SUPERSEDED by v1.4.4, snapshot preserved
- File: data/extract_v2/estimates_v1.4.3_frozen.csv
- Rows: 677 estimates / 317 studies
- MD5: 6d9449c4b34d4f0071f02af862b80857
- Git tag: dataset-frozen-v1.4.3
- Built by: scripts/apply_v142.py → scripts/apply_v143.py

## v1.4.1 → v1.4.2 → v1.4.3 — full re-read of all 324 studies + resolved judgment calls
The verification campaign Sacha ordered ("re-read all texts, double-check every estimate, ensure all fields
detailed"). 21 agents re-read every study; **544 CONFIRM / only 1 value wrong** = dataset strongly validated.
- **v1.4.2 (intermediate, MD5 `cec2dda6cc33389204a1aa57053ce48b`, apply_v142.py):** high-confidence auto-apply —
  filled a misinfo definition for EVERY study + political_orientation on all party rows + topics; 23 deletes
  (engagement betas, redundant aggregates, nested, dedups), 12 reach-of-sharing/liking recodes, 1 value fix. 675/324.
  Changelog `qa/v142_changelog.csv`.
- **v1.4.3 (final, apply_v143.py):** applied the 116 judgment calls (Sacha's 54 + ~40 auto-adjudications + 19
  confirmations + 2 targeted re-reads). 3 study DEDUP-merges (Moreno PMID-37632797→NEW-moreno; Allcott
  W2582561810→SEED-allcott2017; PT 105002473473→EN 105002620495, values ported); **4 EXCLUSIONS**
  (`qa/v143_exclusions.csv`: OA-W4413457235 predatory-journal, 85101871838 figure-only, 85114503116 unreliable,
  105018193928 quality-only); per-platform split of PMID-42295743 epilepsy (TikTok 31.7/IG 16.8/YT 8.0 replace
  pooled 18.1, PDF sourced by Sacha); restored 85214504236 per-criterion 82/48/42; +11 adds (missed estimates,
  Serbia narratives N3/N5 flagged approx, pink-slime overall, other-partisans reach-liking). New col from v1.4.2:
  political_orientation. Changelog `qa/v143_changelog.csv`. Human-review ledger: 206 documented decisions.
- Gates: validate_prisma PASS (0 orphans, 317 studies); validate_frozen PASS.

---

# FROZEN DATASET v1.4.1 (2026-07-21) — SUPERSEDED by v1.4.3, snapshot preserved
- File: data/extract_v2/estimates_v1.4.1_frozen.csv
- Rows: 698 estimates / 324 studies
- MD5: 740927724f942b92cd93599ee97030a5
- Git tag: dataset-frozen-v1.4.1 (supersedes v1.4.0)
- Built by: scripts/apply_v141.py (Sacha's round-2 audit decisions + agent verify/gold re-reads + §4 mechanical)

## v1.4.0 → v1.4.1 — round-2 data-quality audit applied
Sacha's full 90-item review of `docs/audit_review.html` (rounds 1+2) + 4 agent re-reads (2 "gold"
papers, 2 verify batches) + the §4 mechanical fixes. Full changelog `qa/v141_changelog.csv`;
resolutions `qa/audit_round2_resolutions.md`; decisions ledger `qa/human_review_ledger.csv`.
**New columns:** `reach_subtype` (exposure|sharing|liking) · `other_subtype` (composition sub-label) ·
`topic` · `period_label`.
- **24 deletes:** circular fact-check denom (85215785622); 2 mis-mapped RECALL (85124823821);
  3 within-misinfo composition (105027856675 crisis, 105029521599 Dem/Rep shares); 3 complements
  (85134325788, 85159889148, W3033912864 17.55-phantom); bot-presence (105017960510); nested reach-dup
  (85105454127 r576); redundant abstract (W7146985142 r591); 4 nested sub-topics (OA-W7154838691);
  2 exact-dup RECALL (85172813494, 105008525623); **5 dedup rows / 3 duplicate studies**
  (85163629989 + OA-W4417124855 = van Antwerpen; OA-W4411120829 = jung). → 5 studies drop entirely.
- **87 field-sets:** composition→`OTHER/other_subtype` (19; policy: kept, reported separately);
  REACH sub-typing of "% did ≥1" rows (9 sharing + liking + exposure); construct recodes
  (clicks→EXPOSURE 438/439/566; self-report→RECALL 166; SHARING↔CONTENT 354-356/503/402/403/316;
  cascade-trees→SHARING 563); metadata fixes (105027856675 stale country 639/640/641; 85060025053
  label 529; Oswald reach 8→9); demo `topic=`/`period=` moved out of demographic fields (kept);
  denom retags; Figeac demographic backfill; within_misinfo casing.
- **+4 new rows:** 2603.11058 (SIMODS/Science Feedback) per-language CONTENT — FR 17.5 / SK 7.6 /
  PL 6.0 / ES 5.0 [curated-keyword sample, enriched — flagged].
- **12 FLAGGED for the full re-read phase** (not guessed): 85060549676 construct tangle; 85162702221
  reach-liking-vs-diet; 85101871838 mean-of-11; 85108273495 value/denom; **105002473473 PT/EN dedup
  HELD** (PT 3 values 60/12.9/33 ≠ EN single 11.1 — not a clean dup); 85123475265 abstract-verified.
- Gates: validate_prisma PASS (0 orphans, 324 studies); validate_frozen PASS.

---

# FROZEN DATASET v1.4.0 (2026-07-16) — SUPERSEDED by v1.4.1, snapshot preserved
- File: data/extract_v2/estimates_v1.4.0_frozen.csv
- Rows: 718 estimates / 329 studies
- MD5: 45e7f676136b35086c84f00f8e6e28d5
- Git tag: dataset-frozen-v1.4.0 (supersedes v1.3.6)
- Built by: scripts/apply_review_v140.py (Sacha's demographic review + conventions + 3 desktop-PDF extractions)

## v1.3.6 → v1.4.0 — Sacha's demographic-review decisions + coding conventions + PDF enrichment
Sacha reviewed all 85 demographic rows (demo_review CSV) and set coding conventions (2026-07-16).
Applied via `scripts/apply_review_v140.py`; changelog `qa/review_v140_changelog.csv`.
- **18 DROP**: ideology-continuum splits (85066941307 most cons/lib), 'extreme ideologies' labels (85209547248),
  redundant party aggregates (85060549676 R/L), media-/info-diet decile extremes (85081743293),
  simulated-agent rows (85114317455, not humans), real-news-URL row (W3033912864), no-counterpart Rep (85142396682),
  intensity-not-proportion (85060025053 0.75), and the **W4281770633 "80%" mis-extraction** (a classification
  threshold, not an estimate — caught on re-read).
- **CONVENTIONS**: (a) "% who shared/were reached ≥1" → **REACH** (3 rows: 85060025053, 85060549676, 85066941307
  potential-exposure→reach). (b) recall/questionnaire subgroups **kept + tagged RECALL** (9 rows: 85096102360,
  85124823821, 85085573221, 105027959122) — Sacha's rule, reverses his earlier per-row drop notes. (c) spreader/
  supersharer make-up → **spreader_composition** flag + **4 binary complements added** (Men 41 / Dem-Ind 36 /
  non-conservative 9 / non-conservative 17.55) for 85194733750, 85194023903, W3033912864, W4281770633.
- **SPLIT**: 85060549676 "Left and center 5%" → separate left 5% + center 5%.
- **105029521599** (Dem 3.6 / Rep 96.4) KEPT — dropped only conditionally ("if we don't have the paper"); we DO
  (Political Communication 2026, full text). **Flag for Sacha to confirm.**
- **3 desktop PDFs re-extracted** (agents; PDFs cached to data/fulltext/pdf + v2txt). All existing values CONFIRMED;
  the studies were already well-covered, so the only NEW rows are for **105027856675** (4-country politician study,
  all ELITE): per-politician-mean country rates (secondary variant), the 6 smaller party rates, within-country party
  **concentration** (AfD 95.5% / FdI 70.7% / Cons 57.3% / Rep 76.4% of each country's legislator misinfo), Italy's
  53.23% cross-country share, regional-executive rates (US 11.1/UK 6.8), crisis(COVID) share (~50%), and the
  **engagement 'beta' ratios tagged construct=OTHER** (excluded from prevalence; abstract-vs-results contradiction
  logged). Denominator convention: link-level pooled is primary, per-politician means secondary.

---

# FROZEN DATASET v1.3.6 (2026-07-16) — SUPERSEDED by v1.4.0, snapshot preserved
- File: data/extract_v2/estimates_v1.3.6_frozen.csv  (immutable; tag `dataset-frozen-v1.3.6`)
- Rows: 705 estimates / 329 studies
- MD5: 4756f72617f4b3057966118cdafbde2b
- Built by: scripts/apply_gonzalez.py (Phase A step 2g — González-Bailón re-inclusion as concentration)

## v1.3.5 → v1.3.6 — Phase A step 2g: González-Bailón 2023 re-included as CONCENTRATION
2-s2.0-85165815218 (González-Bailón et al., *Science* 2023, "Asymmetric ideological segregation in exposure
to political news on Facebook", DOI 10.1126/science.ade7138) passed title+abstract screening but was
step-B-dropped for "no quantified prevalence value" — correct for a PREVALENCE figure (the paper states the
false-news fraction is only "barely perceptible… very small"; Fig 1D/Fig 4 give distributions, no codeable
rate). PDF found in the library; full text cached. It DOES report an in-scope **concentration-by-ideology**
value, so re-added with **2 CONCENTRATION rows** (n=208M US FB users; false = Meta 3PFC-rated):
- **97%** of false-news URLs have conservative-leaning (exposed) audiences [primary].
- **76%** of untrustworthy domains have conservative-leaning (exposed) audiences.
Flagged `audience_ideology_concentration;not_a_prevalence_rate`. No general-exposure row (not codeable).
Removed from `qa/stepb_drops_queue.csv`. Changelog `qa/gonzalez_changelog.csv`. Both gates green.

---

# FROZEN DATASET v1.3.5 (2026-07-15) — SUPERSEDED by v1.3.6, snapshot preserved
- File: data/extract_v2/estimates_v1.3.5_frozen.csv  (immutable; tag `dataset-frozen-v1.3.5`)
- Rows: 703 estimates / 328 studies
- MD5: d0b6c0673aa929cc83c387980d13f953
- Built by: scripts/apply_newpdf.py (Phase A step 2f — new user-supplied PDF batch)

## v1.3.4 → v1.3.5 — Phase A step 2f: new user-supplied PDF batch (Desktop/New)
Sacha added 18 unique PDFs. Matched by DOI + title:
- **13 were already-frozen studies** (`source=full_text_*`) that merely lacked a cached `.txt` → text
  extracted to `data/fulltext/v2txt/` (data-completeness; no value change). One stale-flag fix among them:
  **OA-W7154838691** (Truth/Fear/Virality) — 5 CONTENT values re-verified verbatim (48.0% overall; TikTok
  58.4/Facebook 54.8/Twitter 41.2/YouTube 38.8) → `abstract_only` cleared, source→`full_text_verified_abs`.
  (OA-W4291473423's PDF is genuinely a conference abstract — `abstract_only` kept, correct.)
- **2 were already-excluded, kept excluded**: 2-s2.0-85059686579 (Prostate, DISCERN *quality* composite not
  falsity), 2-s2.0-85140862422 (PLOS medication *perspective* piece).
- **2 were genuinely NEW studies → screened INCLUDE, added** (studies 326→328):
  - **NEW-moreno-jmirderma** (Moreno et al., JMIR Dermatology 2021, 10.2196/25661): 3 CONTENT rows
    (Vitamin-D 1.3%, medical-treatment 0.6%, base-tan 0.5% of 4,956 tanning-BUSINESS Facebook posts —
    flagged single-source/curated, not general-public) + 1 RECALL row (43%, 20/46 at-risk purposive sample).
  - **NEW-jadara-2022** (Shatnawi & Ayhan, Jadara J. 2022): 1 RECALL row (81.6% read Covid info that turned
    out untrue, N=6,910 Levant convenience survey — flagged perceived_exposure).
- Changelog `qa/newpdf_changelog.csv`. Both gates green.

---

# FROZEN DATASET v1.3.4 (2026-07-15) — SUPERSEDED by v1.3.5, snapshot preserved
- File: data/extract_v2/estimates_v1.3.4_frozen.csv  (immutable; tag `dataset-frozen-v1.3.4`)
- Rows: 698 estimates / 326 studies
- MD5: ee7922033820409278797ce82f929278
- Built by: scripts/apply_abstract_fix.py (Phase A step 2e — abstract-only vs held-PDF reconciliation)

## v1.3.3 → v1.3.4 — Phase A step 2e: abstract-only coding reconciled against held PDFs
Audit: of 43 fully abstract-coded studies, only 4 have a PDF/full text on hand (the other 39 are
genuinely PDF-less). Also extracted text for 4 studies whose PDFs were in the library but had no cached
`.txt` (all were already `source=full_text_*`, values unaffected — data-completeness only). The 4
abstract-flagged-with-PDF studies were reconciled:
- **2 genuinely abstract-coded, re-verified verbatim against full text → CONFIRMED, source→`full_text_verified_abs`**:
  Caliandro OA-W3091627927 (SHARING 1.44%, "l'1,44% del totale dei tweet", n=7,237,581);
  Thai dietary-supplement content analysis 2-s2.0-85214504236 (CONTENT 85/82/48/42%, n=332 web pages).
- **2 stale flags cleared** (source already `full_text`): Nigeria OA-W7125772788 (RECALL), Fletcher
  OA-W2992531903 (REACH; verified in the found-papers pass).
- **No value changes** — all confirmed. `abstract_only` flag rows 63→51; `source=abstract` rows 44→39
  (the 39 remaining are the genuinely PDF-less studies). Changelog `qa/abstract_fix_changelog.csv`.

---

# FROZEN DATASET v1.3.3 (2026-07-15) — SUPERSEDED by v1.3.4, snapshot preserved
- File: data/extract_v2/estimates_v1.3.3_frozen.csv  (immutable; tag `dataset-frozen-v1.3.3`)
- Rows: 698 estimates / 326 studies
- MD5: e1455c96c189f3335f47067e28656be7
- Built by: scripts/apply_cordonnier.py (Phase A step 2d — Cordonier/Brest full-text verify)

## v1.3.2 → v1.3.3 — Phase A step 2d: Cordonier & Brest 2021 full-text verify
Second-reader read the full Fondation Descartes report (English translation, March 2021), whose PDF
Sacha located and we extracted to `data/fulltext/`. It was previously coded from the Berriche seed abstract only.
- **2/2 existing EXPOSURE values CONFIRMED verbatim** (5% of news/information time; 0.16% of total
  connected time — one sentence, Key Findings p.05, restated §3.6 p.26).
- **+1 REACH row**: 39% of participants consulted ≥1 unreliable source over the 30-day window (N=2,372) —
  a genuine audience-reach prevalence we had not coded.
- **FIX**: cleared the now-stale `abstract_only` flag on the 2 EXPOSURE rows (full text held + read).
- **0 demographic**: report gives demographic patterns only as correlations / Hedges' g / risk-group
  composition (e.g. "63.2% men" among disinfo consumers) — all excluded by RULE DEMO.
- Changelog `qa/cordonnier_changelog.csv`.

---

# FROZEN DATASET v1.3.2 (2026-07-15) — SUPERSEDED by v1.3.3, snapshot preserved
- File: data/extract_v2/estimates_v1.3.2_frozen.csv  (immutable; tag `dataset-frozen-v1.3.2`)
- Rows: 697 estimates / 326 studies
- MD5: 9d0d5cb6f1e417ad9dc9cfe8ef4779da
- Built by: scripts/apply_found.py (Phase A step 2c — 7 user-found high-value PDFs)

## v1.3.1 → v1.3.2 — Phase A step 2c: user-found high-value PDFs
Sacha located 7 of the 9 remaining high-value studies (PDFs in Desktop/New; copied to
`data/fulltext/pdf/` + extracted to v2txt). Matches verified by title page. 2 agents verified
existing values + extracted demographics.
- **23/24 existing values CONFIRM** (Pierri, Dahlke, Bandy, Caliandro, Fringe, Fletcher, Nigeria).
- **1 DROP**: Nigeria OA-W7125772788 EXPOSURE 40 ("40% higher than…" = relative comparison, not prevalence).
- **4 RELABEL**: Fletcher OA-W2992531903 EXPOSURE→REACH (France/Italy 3.1%/1.0% = avg monthly reach %).
- **+4 demographic** (Bandy 85114317455 political): junk-news exposures/day by leaning (left 1.1/right 5.8
  chronological, 0.3/4.3 algorithmic; intensity). Fletcher France/Italy "region" splits skipped (= existing country rows).
- Changelog `qa/found_changelog.csv`. Still missing: "Does Vinegar Kill Coronavirus" (OA-W3113799821);
  Cordonnier is data-complete (Fondation Descartes report, values from Berriche seed).

---

# FROZEN DATASET v1.3.1 (2026-07-15) — SUPERSEDED by v1.3.2, snapshot preserved
- File: data/extract_v2/estimates_v1.3.1_frozen.csv  (immutable; tag `dataset-frozen-v1.3.1`)
- Rows: 694 estimates / 326 studies
- MD5: e7d062d9587a354a6defe530f8f3e9d8
- Built by: scripts/apply_hv.py (Phase A step 2b — high-value canonical papers)

## v1.3 → v1.3.1 — Phase A step 2b: high-value canonical papers (coverage gap)
The demographic pass (step 2) only grepped `data/fulltext/`, so it MISSED 20 high-value
(exposure/sharing/reach/concentration) studies never extracted to text — incl. the canonical
Guess 2016/2020, Allcott, Supersharers, deplatforming. 11 were in the PDF library; 3 agents read them
and (1) VERIFIED existing values, (2) extracted demographic breakdowns. All 11 PDFs also extracted to
`data/fulltext/v2txt/` so the gap can't recur.
- **33/33 existing values CONFIRM** (0 CORRECT/DROP) — the canonical papers' frozen values validated.
- **+27 demographic rows** (political 17, age 9, gender 1; 23 per_subgroup_rate + 4 subgroup_composition).
  Canonical adds: Guess/Nyhan/Reifler political gradients (Trump 56.7% vs Clinton 27.7% reach among
  conservatives; media-diet-decile up to 84% reach / 20.9% diet-share), Moore 2020 (Trump 36.2/Biden 17.8;
  65+ 37.4), Lyons age gradient (website reach 4.8→20.9% by age). Supersharers 59% women / 64% Republican
  (composition). Dropped Moore's 3 "(2016)" rows = Moore citing Guess (coded natively). `qa/demographic_added_hv.csv`.
- 9 high-value studies remain unresolved (OA preprints/title-only) → still on missing-full-text sheet.

---

# FROZEN DATASET v1.3 (2026-07-15) — SUPERSEDED by v1.3.1, snapshot preserved
- File: data/extract_v2/estimates_v1.3_frozen.csv  (immutable; tag `dataset-frozen-v1.3`)
- Rows: 667 estimates / 326 studies
- MD5: 312b296629afeb57aaaddec2c1874ba5
- Built by: scripts/build_v1.3.py (Phase A step 2 — demographic-breakdown rows)

## v1.2.1 → v1.3 — Phase A step 2: demographic corpus pass (RULE DEMO)
Systematic corpus-wide extraction of demographic subgroup breakdowns of the misinfo estimate
(7 agents over 125 demographic-signal candidate texts; strict inclusion = a per-subgroup VALUE
anchored to a verbatim quote, NOT regressions/odds-ratios/sample-composition).
- **+54 demographic rows** (`demographic_group="dim=label"`, new cols demographic_dimension +
  demographic_subtype): political 38, age 9, gender 4, education 3. Subtype: 48 per_subgroup_rate,
  6 subgroup_composition (Trump/conservative share OF sharers — W4281770633, W3033912864,
  85194023903, 85188806397; flagged distinct from per-subgroup RATES). No new studies (all breakdowns
  are on already-frozen studies) → 326 studies unchanged.
- Canonical adds: Guess/Nagler/Tucker (18.1% Rep vs 3.5% Dem shared fake news; 65+ ~7×), Grinberg
  (11%/21% right vs <5% left shared), Lazer (political×age), Hjorth (6.5% liberal→45.2% conservative
  exposure), QAnon/pink-slime by ideology, multi-party sharing. Review sheet `qa/demographic_added.csv`.
- **REGION/country breakdowns SET ASIDE** (24 values, `qa/demographic_region_setaside.csv`) — geographic,
  already the country_norm axis; not coded as demographic_group. For Sacha's review.
- SUBGROUP rows: Phase B headline analysis MUST exclude `demographic_group != ''` (subgroup rows are
  not general-public one-per-cell estimates). One intensity row (Guess 65+ mean-count) blanked value_pct
  per R5 (value in value_raw, flag intensity_not_proportion).

---

# FROZEN DATASET v1.2.1 (2026-07-15) — SUPERSEDED by v1.3, snapshot preserved
- File: data/extract_v2/estimates_v1.2.1_frozen.csv  (immutable; tag `dataset-frozen-v1.2.1`)
- Rows: 613 estimates / 326 studies
- MD5: 2e46254a4c412ff16338e62c16d966b0
- Built by: scripts/apply_phaseA.py (Phase A second-reader verification of v1.2 new rows)

## v1.2 → v1.2.1 — Phase A: close the "no two-tier evidence standard" gate
Independent second-reader quote-verification of all 86 new/changed v1.2 rows (8 agents; protocol
`docs/value_verification_protocol.md`) + RoB appraisal of the 4 new studies + moderator gap-fill.
- **79/86 CONFIRM verbatim, 0 CORRECT, 6 DROP** (+1 KEEP-override). All headline numbers hold
  (Lyons conc 37%/77%, QAnon 3.7%, Eady 98%, Altay 8 rows, Oswald diet-share, Figeac 12 party rows).
- **Hybrid keep/drop rule (Sacha 2026-07-15):** keep verbatim values + exact PART/WHOLE prevalences
  from verbatim same-denominator counts; drop cross-category sums/complements. Dropped: Web Centipede
  within-news 23.9/11.3/20.2 (news-total denom not verbatim — re-checked), Mourão 11.8 (sum) & 43.5
  (complement), TikTok-nutrition 37 (sum). Kept-override: bladder-cancer 29.3 (44/150 part/whole).
  Full reasons: `data/extract_v2/qa/phaseA_changelog.csv`.
- **RoB** (companion `data/extract_v2/qa/rob_appraisals.csv`, 5 dims per `docs/rob_checklist.txt`):
  Lyons LOW; Web Centipede / Figeac / arXiv MODERATE. 148 moderator gap cells filled on new rows.
- No whole study departed → PRISMA id-set unchanged (326 studies), gate stays green.

---

# FROZEN DATASET v1.2 (2026-07-15) — SUPERSEDED by v1.2.1, snapshot preserved
- File: data/extract_v2/estimates_v1.2_frozen.csv  (immutable; tag `dataset-frozen-v1.2`)
- Rows: 619 estimates / 326 studies
- MD5: 17237c74cb46ed8e4d3db05f53d8eb0f
- Git tag: dataset-frozen-v1.2 (superseded by v1.2.1 after Phase A verification)
- Built by: scripts/build_frozen_v1.2.py (materializes LIVE rows of estimates_v1.2_A.csv; 57 dropped rows excluded)
- Gates at freeze: validate_frozen 0 FAIL / 0 WARN (19 X-of-Y reconciled, all constructs valid);
  validate_prisma 0 orphans (frozen=v1.2 → 326 INCLUDED_FROZEN; every advanced record maps to a terminal state).
- Construct mix: CONTENT 328 · SHARING 73 · RECALL 70 · QUALITY 46 · EXPOSURE 43 · CONCENTRATION 32 · REACH 21 · OTHER 6.
  (QUALITY + OTHER = 52 rows are documentary/excluded from prevalence analysis per the analysis rule.)

## What v1.2 folds in (all v1.1 errata below now RESOLVED)
- **RA-verification + re-audit content decisions** (Phase 3a, v1.2a): 7 ratified coding rules R1–R7 (+R4a/R4b);
  16 studies dropped with reasons; construct recodes; elite-population + source_level tags.
- **Denominator-sets-construct recodes** (Phase 3b, RULE D / C-TYPE / DEMO / DUAL-DENOM;
  `docs/construct_and_concentration_rules.md`): concentration typed by conc_unit × conc_dimension
  (bots dropped); FB/engagement → SHARING; dual-denominator content/news pairs; 6 fulltext re-extractions.
- **Corpus-wide moderator tagging** (6 judgment dims, 0 enum violations).
- **New rows / studies** (+53 rows / +16 studies): enrichment 2nd-reader+RoB, Lyons+arXiv, truncation-missed adds.
- **PRISMA reconciliation to 0 orphans** (`data/extract_v2/qa/prisma_dispositions.csv` +
  `data/extract_v2/qa/v1.2_drops_ledger.csv`; hard gate F).

## Deferred to v1.3 (not in this freeze)
- **Demographic systematic corpus pass** (age / political orientation / party breakdowns via `demographic_group`) —
  Sacha's call 2026-07-15: freeze v1.2 now as a certified milestone; demographic pass becomes an additive v1.3 freeze.
- **RA answer key vs v1.2**: 10 RA-sampled items are `our_keep=Y` but dropped in v1.2 (RA-verification + re-audit
  drops). NOT flipped here — retroactively changing the key alters the reliability κ Laura was scored against.
  Pending Sacha's decision (separate from the dataset freeze).

## v1.1 errata — ALL RESOLVED in v1.2 (kept here for the audit trail)
- **Cordonnier double-spelling** → RESOLVED: `SEED-cordonier2021` (one-n) merged into canonical
  `SEED-cordonnier2021` (two-n); ledgered DEDUP_COLLAPSED in `qa/v1.2_drops_ledger.csv`.
- **19 PRISMA recoveries (silent data loss)** → RESOLVED: 14 recovered into v1.2 (incl. Grinberg primary,
  web-centipede, QAnon, Eady/IRA); 6 out-of-scope recoveries dropped with reasons; all in
  `qa/prisma_dispositions.csv`. 44 INCLUDED_NO_DATA + 48 EXCLUDE + 14 title-screen dispositioned.
- **Truncation sensitivity adds** → RESOLVED: same-kind estimates added (QAnon, Eady, Altay); Allgaier
  `W2953415400` chemtrail/consensus-opposing label reconciled, then study dropped (stance not falsity, re-audit).
- **`W4306964957` units** → no change needed (was a false alarm; values already correct percentages).
- **Fletcher/RISJ cross-track dup** → academic `OA-W2992531903` kept (published-version-wins);
  canonical RISJ factsheet still deferred (couldn't source; OA copy retained).
- **DeVerna `2-s2.0-85194023903` concentration 73-78 → 81** → RESOLVED in build_v1.2 (oracle optimal 81%;
  73-78% noted as the predictor-based range).

---

# FROZEN DATASET v1.1 (2026-06-29) — SUPERSEDED by v1.2, snapshot preserved
- File: data/extract_v2/estimates_reextracted.csv  (immutable; tag `dataset-frozen-v1.1`)
- Rows: 584 estimates / 328 studies  (de-duplicated true totals were 582 / 327 — see Cordonnier erratum)
- MD5: 1a8f881a11f8e31df536862d76c314cd
- Certification: construct kappa 0.78; adversarial 0/40 false-drops; headline EXPOSURE 21/24 hold; blind 10%
  reproduction 90% (construct 94%); outlier audit 0 errors; 184 studies dropped with reasons; abstract-only 46
  (sensitivity-only). Dropped W7160643177 (conspiracy-curated Telegram archive, circular sample).
- The v1.1 errata that drove v1.2 are documented in the RESOLVED list above (and in git history of this file).
