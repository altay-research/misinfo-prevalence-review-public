# RA verification — implications & new coding rules (from Sacha's 29-paper review, 2026-07-14)

> **RATIFICATION STATUS (Sacha, 2026-07-14):** R1, R2, R3, R5, R7 ratified as written.
> R4 REVISED (no one-per-paper rule; keep clear country/platform breakdowns, collapse
> time-series/subgroups; quality over quantity). R6 confirmed: no structured field exists — the
> actor-vs-content distinction lives only in `measure_type` prose → make it a tag + audit.
> **#95 → SHARING (content_share subtype) + source_level** (resolved 2026-07-14 after re-reading
> Altay/Nielsen/Fletcher 2022: FB engagement = likes/emojis/shares/comments = behavioural engagement
> share, denominator is engagement acts not content items; paper explicitly says "source level, not
> content level"; it is the platform-twin of the Comscore web-traffic EXPOSURE measure. NOT CONTENT.)
> **#51 → DROP** (his lean).
> **#55 → keep, recode CONTENT→SHARING(content_share) + source_level, one value** (was blank; default).
> Phase 0 complete — cleared to start Phase 1.

Source: `docs/RA_package/round1_2026-07/ra29_verification_SACHA.csv` (20 agree, 5 disagree, 3 unsure, 1 blank).
Grounding checks run against `data/extract_v2/estimates_reextracted.csv` (frozen v1.1).

**Headline:** most of the "disagrees" are NOT us being wrong under the old rules — they are the
protocol *evolving*. Sacha's comments imply **7 coding rules** (some new, some clarifications),
**3 process fixes**, and a set of **per-paper actions**. Several new fields must be added to the
dataset before v1.2.

---

## A. NEW / REVISED CODING RULES

### R1 — CONCENTRATION is exempt from the "within-misinfo" exclusion
Audience/user/sharer **concentration** (top X% of users → Y% of exposure/sharing) is a VALID
`CONCENTRATION` estimate **even when computed within a misinfo-only sample**. The "composition
/ concentration within an already-misinfo set = DROP" rule was over-broad; it applies to *content
prevalence*, not to concentration.
- **Mandatory format:** every concentration estimate must carry BOTH (a) the group size as a
  share of the population/users (e.g. "1% of users"), AND (b) the share of content/exposure they
  account for (e.g. "→ 70% of exposures"). A bare count ("top 35 accounts = 28.6%") without the
  population denominator is **unusable** → re-extract the denominator or drop.
- Triggers: #16 ("for concentration it's ok — we should have been clearer"), #25 (disagree: keep
  "20% of community → 90% of tweets"), #94 (disagree: keep, but "35 out of how many?").
- **Grounding:** 25 CONCENTRATION rows exist; most already follow (group%→share%), but a few
  (e.g. `W4281770633` #94 = 28.6% with no group size; `2-s2.0-105007777349` empty value) are
  malformed and must be fixed.

### R2 — Population scope is a TAG, not a drop reason
Estimates for **specific populations** (politicians/elites, professionals, defined survey panels)
are **KEPT** and reported separately, not dropped for being non-general-public.
- **Add field `population_scope`**: `general_public | elite_politician | professional | other`.
- Triggers: #96 (disagree: keep politicians' estimates, tag them distinctly), #48 (unsure: elite
  sharing is "informative", keep w/ tag).
- **Grounding:** ~14 studies carry elite/professional signals (politicians `W4306964957`,
  pharmacists `2-s2.0-105031695645`, HCPs, candidate-content studies) — a whole class, not 2 papers.
- **Note:** #11 (pharmacist "% who encountered") stays a DROP for a *different* reason (perception
  survey, not a content/exposure share) — population scope alone would not have saved it.

### R3 — Within-misinfo CONTENT falsity → appendix bucket, not deletion
When a study reports content-level falsity **within a sample defined by misinfo source**
(low-quality/misinfo sites), **exclude from the main prevalence but RETAIN** in a secondary
"within-misinfo content" bucket for a brief appendix analysis.
- Trigger: #19 ("I feel bad dropping… keep them somewhere for an extra analysis, report briefly
  in appendix… only when it's misinfo content within a misinfo-source sample").
- **Action:** create `data/extract_v2/within_misinfo_content/` + an `estimate_role` value for it.

### R4 — Keep every high-confidence distinct estimate; collapse the rest (REVISED per Sacha 2026-07-14)
There is **no in-principle one-estimate-per-paper rule.** The governing principle is quality:
**one estimate we are 100% sure of beats ten uncertain ones.** Concretely:
- **Clear country / platform breakdowns** that are cleanly reported → **keep them all** (4 countries
  clearly reported = 4 estimates; #95 per-country; #65 platform/topic where clean).
- **Time series** → pick ONE representative point, not every time slice.
- **Main estimate + demographic/other subgroups** → keep just the main headline (e.g. the 5%),
  drop the subgroup splits (#56 keep 0.1461, not the news-desert subgroup).
- Decision test: is this breakdown a *distinct, clearly-reported, high-confidence* quantity, or a
  redundant/uncertain slice of the same thing? Keep the former, collapse the latter.
- **No primary/secondary hierarchy** (revised per Sacha 2026-07-14): most studies contribute several
  **co-equal** estimates that all matter equally (e.g. JQD = 4 countries × 2 constructs = 8 co-equal).
  The pooled median de-duplicates to one estimate per (study × construct × country × platform) cell;
  co-equal estimates sit in different cells and all enter.
- **R4a — Only definition/severity variants need flagging** (from #4). When two estimates in the SAME
  cell differ only by definition strictness (e.g. "contains any" 79% vs "entirely false" 27%; source vs
  content level), set **`definition_variant=TRUE`**. All variants are KEPT and central to the breadth
  analysis (R4b); the single pooled median uses one per cell (fixed reference breadth) to avoid
  double-counting. No "primary/secondary" ranking.
- **R4b — Definitional strictness is a PRIMARY analytical target, not a nuisance** (Sacha, 2026-07-14).
  Because this is a review of misinformation *prevalence*, **how much the estimate changes with a
  stricter vs broader definition is one of the headline findings.** Therefore:
  - When a study reports the SAME quantity under multiple definitions/strictness levels (fabricated-only
    vs false vs misleading; content-level vs source-level; entirely-false vs contains-any), **keep them
    all**, each tagged with its `breadth` code — do NOT collapse to one. These are "interesting distinct
    estimates" in the same class as country/platform breakdowns.
  - The headline analysis reports prevalence **stratified by `breadth`** (and by `classification_level`
    source vs content), so the review can show the definition-driven spread explicitly. The single
    pooled median uses one estimate per study at a fixed reference breadth to avoid double-counting; the
    breadth-stratified view uses all of them.
  - This is the operational payoff of the project's thesis ("methodological/definitional choices drive
    divergent estimates") — so capturing definitional variants is a feature, not overhead.

### R5 — EXPOSURE must be a PROPORTION (%), not a mean/median count
Intensity measures (mean sites visited, mean stories read, mean impressions) are **not** prevalence
proportions and must not sit in the %-based headline.
- Trigger: #40 ("EXPOSURE=1.19 is a mean number of sites, not a %; not sure we do that").
- **Grounding:** 5 EXPOSURE rows are intensity-flavoured, 2 with EMPTY `value_pct`
  (`SEED-allcott2017` mean stories/impressions; `2-s2.0-85111545521` #40 mean visits).
- **Action:** `exposure_type = proportion | intensity`; intensity → side-bucket, out of headline.

### R6 — SHARING must separate actor-share vs content-share
"% of users who shared misinfo" ≠ "% of shared content that is misinfo" — a first-order distinction.
- Trigger: #54 ("3.2% is 3.2% of users *have shared* misinfo, not users share 3.2% of misinfo —
  important distinction, that we already make I think, right?").
- **Grounding:** the distinction currently lives ONLY in free-text `measure_type` (56 SHARING rows,
  ~8 actor-share, ~9 content-share, rest implicit). Promote it to a structured field.
- **Add field `sharing_subtype`**: `actor_share | content_share`.

### R7 — QUALITY / DISCERN confirmed NOT misinformation (reinforced)
mDISCERN/DISCERN reliability (source attribution, uncertainty, clarity) ≠ misinformation.
- Trigger: #7 ("'absence of source attribution / lack of reference to uncertainty' are not enough
  to be misinformation… I agree we drop"). No change; add this as an explicit example in the rubric.

---

## B. PROCESS FIXES

- **P1 — Always read the PDF when it exists.** Do NOT defer as "needs PDF". Trigger: #81 ("you
  wrote needs PDF but you HAVE the PDF — read it! applies to all such articles"). All 29 PDFs are
  now in `PDFs/`. Re-adjudicate #4, #65, #81 from the actual PDFs.
- **P2 — Update the RA rubric** (`docs/RA_package/round1_2026-07/RA_INSTRUCTIONS.md` + `ADJ_RUBRIC`) to encode
  R1–R6, so RA2 / any re-coding apply them. #16 shows the current rubric caused avoidable confusion.
- **P3 — Two construct re-code checks to resolve:**
  - #95 `W4293124965`: Comscore web-traffic = EXPOSURE (agree). Facebook-engagement share is
    currently coded **SHARING**; Sacha asks if it should be **CONTENT**. (My read: engagement =
    audience behaviour, closer to SHARING/REACH than CONTENT — but his call. **Needs decision.**)
  - #51 `2-s2.0-85151055175`: numerator = mentions of a fixed misinfo-topic dictionary
    (stance-agnostic), denominator = all candidate content. Sacha leans DROP. **Needs decision.**

---

## C. PER-PAPER ACTIONS (the 9 non-agreements)

| # | id | Sacha | Action |
|---|---|---|---|
| 13 | 2-s2.0-105041276064 | disagree | No clean "9.6%" estimate + tiny n → **re-verify; likely DROP** |
| 24 | 2-s2.0-85066894147 | unsure | Denominator of the 20% unclear → **careful re-read (triple-check)** |
| 25 | 2-s2.0-85078014559 | disagree | **Reclassify DROP→CONCENTRATION-keep** (R1): "20% of community → 90% of tweets" |
| 48 | 2-s2.0-85142396682 | unsure | **Keep, tag `population_scope=elite_politician`** (R2) |
| 51 | 2-s2.0-85151055175 | unsure→drop | Misinfo-topic-dictionary numerator → **decision (P3), lean DROP** |
| 55 | 2-s2.0-85188806397 | BLANK | No decision recorded → **needs decision** (source-level share of sharing; default keep+tag) |
| 94 | W4281770633 | disagree | **Reclassify DROP→CONCENTRATION-keep** (R1) BUT re-extract proper group-size denominators |
| 95 | W4293124965 | disagree | Per-country (already have); **resolve FB=SHARING vs CONTENT** (P3); keep source_level |
| 96 | W4306964957 | disagree | **Keep, tag `population_scope=elite_politician`** (R2) |

Provisional (re-read from PDF, P1): #4 (agree — "52% partial, 27% entirely misleading"), #65
(agree + **add topic breakdowns** per R4), #81 (re-adjudicate from PDF).

---

## D. NEW DATASET FIELDS (add before v1.2)
`population_scope` · `estimate_role` · `exposure_type` · `sharing_subtype` · `within_misinfo_content` (bool)

## E. RELIABILITY NOTE
Of the 5 disagreements: 3 (#25, #94, #96) are **rule changes, not errors**; 1 (#95) is a
granularity/construct refinement; 1 (#13) is a genuine weak-estimate drop. So under the *old* rules
our adjudication was largely defensible — the value of the exercise is the **protocol evolution**,
not an error rate. Recompute agreement AFTER applying R1–R7 to a re-adjudicated gold.
