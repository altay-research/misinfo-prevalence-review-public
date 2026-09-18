> **PARTLY SUPERSEDED (banner added 2026-08-11).** These rules were ratified 2026-07-15 and remain
> the historical record. Since then: `conc_unit` was renamed to {user|source} (bots dropped); the
> denominator field split into `denom_scope` × `denom_selection` (v1.6.0); and the CONTENT-vs-SHARING
> boundary gained the actor rule refined at v1.7.7–v1.7.8 (single named actor's output = CONTENT, a
> class of actors measured by what they share = SHARING). The LIVE rules are
> `docs/moderator_codebook.md` (read its end-of-file refinements) + `docs/DECISIONS_REGISTER.md`.

# Construct & concentration coding rules (ratified from Sacha's new-adds review, 2026-07-15)

Extends the RA rules (`RA_package/round1_2026-07/verification_implications_and_rules.md`) and the moderator
codebook. Governs v1.2 recoding and all future coding. Source: Sacha's per-study notes on the
53 new v1.2 rows (`data/extract_v2/qa/v1.2_newrows_manifest.csv`).

---

## RULE D — THE DENOMINATOR SETS THE CONSTRUCT (governing principle)
The numerator is always "the misinfo subset." The **construct is defined by the universe the %
is a share OF** (the denominator), NOT by the numerator or the topic. This IS the review's thesis
(methodological choices, esp. the denominator, drive divergent estimates).

| Denominator (universe) | Construct | Question |
|---|---|---|
| All content that **exists** (items posted/produced) | **CONTENT** | how much false stuff is out there? |
| Content people **consumed** — views, visits, **clicks**, impressions, diet-share | **EXPOSURE** | how much did people see/consume? |
| People who **encountered ≥1** (population reached) | **REACH** | what share of the population was touched? |
| Content people **shared / engaged with** — reshares, likes, FB engagement | **SHARING** | how much did people spread/endorse? |
| Respondents' **self-report** of seeing/remembering | **RECALL** | what do people *say* they saw? |

Shortcut when unsure: **"a share of *what*?"** — all content → CONTENT; things seen/clicked/visited
→ EXPOSURE; population reached → REACH; things shared/engaged → SHARING; self-report → RECALL.

Consequences (recodes applied at v1.2):
- **Facebook/Twitter engagement (likes+comments+shares)** → **SHARING** (`content_share`), consistent
  with Sacha's JQD paper. NOT `OTHER`. (Fraxanet #105017599346 recoded OTHER→SHARING.)
- **"% of shared links that are unreliable"** → **SHARING** `content_share` (denominator = shared
  links). Calling it CONTENT would erase the supply-vs-behaviour distinction the review exposes.
- **Link-clicks / visits / diet-share** → **EXPOSURE**. (Lyons #105029413645: 3%/10% diet-share = EXPOSURE.)
- **"% who saw ≥1 in a window"** → **REACH** (not EXPOSURE). (Lyons 13%/9%; Cha handled below.)
- **Self-report** → **RECALL**. (Cha #85101871838 "had seen the claim" recoded EXPOSURE→RECALL.)

## RULE C-TYPE — CONCENTRATION must be typed by unit × dimension
Every CONCENTRATION row carries:
- **`conc_unit`** = `individuals` | `news_source` | `bots`
- **`conc_dimension`** = `exposure` | `sharing`
- and (still mandatory, R1) **`conc_group_pct`** + **`conc_share_pct`**.

Keep/drop:
- **`individuals`** (people/users) → **KEEP** — the primary concentration of interest.
- **`news_source`** (top domains/sources) → **KEEP but labelled** `conc_unit=news_source`; reported
  **separately**, never pooled with individuals-concentration (Sacha 2026-07-15).
- **`bots`** → **DROP** (out of scope; supply/producer side). (Shao #85056802427 dropped.)

Never merge concentration across different denominators/units — a "top 1% of users → 80% of exposure"
is not comparable to a "top 10 sources → 95% of tweets". Cross-study concentration comparison needs a
common denominator (open methods question flagged by Sacha — for the analysis stage).

## RULE DEMO — code demographic breakdowns (age, political orientation)
When a study reports estimates broken down by **age** or **political orientation/party** (and other
demographics where clean), **keep each breakdown as a co-equal row** with a new field
**`demographic_group`** (e.g. `party=Front National`, `age=65+`). Report separately from the overall.
Scope: **systematic corpus-wide pass** (Sacha 2026-07-15) — a dedicated re-read to pull every reported
demographic breakdown (expected to be sparse but valuable). Figeac #85096862559 (per-party Table 3a) is
the template.

## RULE DUAL-DENOM — report both broad and news denominators when available
When a study reports misinfo prevalence against BOTH "all content" and "news content" denominators
(or these are computable), **keep both** as `definition_variant` pairs, tagged `denom_class`
= `all_media` vs `political_news`. (Web Centipede #85038621544: alt-news % of all posts AND
alt/(alt+main) within news.) This is the same "denominator drives the number" demonstration as breadth.

---

## Per-study actions from this review (applied at v1.2)
| id | action |
|---|---|
| 85086772538 (Guo rumors) | **DROP the paper** (Sacha) |
| 85056802427 (Shao) | **DROP** — concentration among **bots** |
| 105017599346 (Fraxanet) | recode **OTHER → SHARING** (content_share); FB engagement = sharing |
| 85101871838 (Cha) | recode **EXPOSURE → RECALL** (self-report) |
| 85095575703 (Figeac FB) | **SHARING (content_share)** — was CONTENT; denominator = shared links |
| 105029413645 (Lyons) | 13%/9% → **REACH**; 3%/10% → **EXPOSURE**; 37/77 → 2 CONCENTRATION rows (individuals, exposure); **fix wrong DOI**, verify identity |
| W4293124965 (Altay) | replace w/ **8 estimates** — 4 countries × 2 platforms (web=EXPOSURE, FB=SHARING), Table 2, 2017–2021 |
| W7146985142 (Oswald) | **ADD the <1% media-diet EXPOSURE** measure (abstract); keep reach 17/8 + top-3 concentration (news_source) |
| 85038621544 (Web Centipede) | add **dual-denominator** rows (all-content + within-news), per platform |
| 85105454127 (Osmundsen) | code **both** concentration points (1%→75%, 11%→100%), individuals-sharing |
| 85215303159 (Brugnoli) | label **pre-pandemic vs during** cleanly; consider adding Tab3 interactions |
| 85199110625 (Gravino) | relabel the 4 rows clearly: supply FB/TW = CONTENT; diffusion FB/TW = SHARING |
| 85213958624 (Gonzalez-Bailon) | **check supplement** — is 0.94% clean? repair/keep/drop concentration |
| 2603.11058 (arXiv) | keep only the **6 per-platform** P_restricted rows; **drop the 6 P_total** variants |
| 85096862559 (Figeac) | add **all-party** breakdown (Table 3a) → demographic_group |
| 85043684270 | ensure the specific misinfo **definition is encoded** |

## Already in the dataset (looked missing because the HTML showed only NEW rows)
- QAnon 39.1% misinfo-site exposure — **frozen v1.1**.
- Grinberg 1%→80% (exposure) & 0.1%→80% (sharing) **individuals-concentration** — **frozen v1.1**.
Fix: the review HTML must show ALL rows per study (frozen + new), not just new.
