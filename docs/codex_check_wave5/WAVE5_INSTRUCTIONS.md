# Codex blind re-code — batch campaign (COMPLETE 2026-08-10; retained verbatim as the instrument of record)

Code BLIND from each row's two text fields only. Do NOT open WAVE5_ANSWER_KEY.csv, the frozen
dataset, docs/moderator_codebook.md, or any other project file — the definitions you need are all
below.

## ⛔ CODE EXACTLY ONE FILE IN THIS SESSION, THEN STOP

You were pointed at ONE worklist — normally a batch file, `wave5_worklist.csv`. Code that file and only
that file. When it is saved, **STOP and report back. Do not start another batch, do not offer to
continue, and do not open any other batch file** — even if you have capacity left, and even if you
are asked to "keep going" later in this same session. The correct response to that request is:
start a new session.

This is not housekeeping. An earlier attempt coded 647 rows in one continuous session and degraded
badly: on rows it had already coded under identical instructions it reproduced only 45% of its own
denominator codes, and it collapsed seven denominator categories into two defaults. That whole run
was discarded. Batches of ~72 rows each in a FRESH session held up (kappa .83 and .75). The failure
is per-session, so a second batch in this session re-creates it.

Read `wave5_worklist.csv`. Do NOT edit it and do NOT hand back a CSV.

## How to hand the answers back: ONE JSON FILE, SAVED IN THE `returned/` FOLDER

When every row is coded, write a single JSON file and save it, inside this package, as

    returned/wave5_codes.json

The `returned/` folder sits beside `wave5_worklist.csv` and is already there. Save the file INTO
it — not next to the worklist, not in a batches folder, not wherever the tool defaults to.

One object, keyed by the worklist's `item_id`, one entry per row, every row present:

    {
      "W50001": {"construct": "RECALL",  "breadth": "false", "denom_class": "population", "confidence": 4},
      "W50002": {"construct": "CONTENT", "breadth": "",      "denom_class": "topical",    "confidence": 3}
    }

`item_id` strings exactly as the worklist spells them. `construct` is never blank. `breadth` and
`denom_class` may be an empty string when the row genuinely carries none. `confidence` is 1 to 5.
Nothing else in the file: no prose, no commentary, no markdown fence around it.

These definitions ARE the project codebook (v1.6.0 taxonomy, the current one). Round 1 of this sweep
shipped bare label names with no definitions and produced systematic mismatches — a coder using
reasonable but DIFFERENT senses of the same words, especially across EXPOSURE / REACH / RECALL and
across CONTENT / SHARING. Apply the senses defined here, not the plain-English ones.

## `YOUR_construct` — ask: "this is a share of *what*?" (never blank)
| code | the % is a share of | tell |
|---|---|---|
| `CONTENT` | all content that EXISTS (items posted/produced) | how much false stuff is out there |
| `EXPOSURE` | content people CONSUMED — views, visits, clicks, impressions, diet-share | a share of a consumption stream |
| `REACH` | PEOPLE who encountered >=1, measured BEHAVIOURALLY (tracking/log data) | "% who visited/were exposed to at least one" |
| `SHARING` | content people SHARED or engaged with — reshares, likes, FB engagement | the denominator is a stream of SHARING ACTS (shares, retweets, link-bearing posts) |
| `RECALL` | PEOPLE, measured by SELF-REPORT — what they say they saw/shared/remember | "respondents reported", survey question |
| `CONCENTRATION` | a top-X% of units accounting for Y% of the volume | inequality / Lorenz-type statement |
| `QUALITY` | a quality / usefulness / reliability RATING, not falsity | DISCERN, "quality", "reliability" |
| `OTHER` | none of the above — e.g. conditional probabilities, engagement rates per post | |

The three boundaries that decide most rows:
- **EXPOSURE vs REACH.** EXPOSURE is a share of CONTENT consumed; REACH is a share of PEOPLE. If the
  denominator is persons, it is never EXPOSURE, however much the sentence says "exposure".
- **REACH vs RECALL.** Both have a PEOPLE denominator; they differ ONLY by measurement — behavioural
  (tracking, logs, platform data) is REACH, asking respondents is RECALL. Anything measured by
  ASKING is RECALL even when the question is about exposure or about sharing; self-report never
  becomes EXPOSURE/REACH/SHARING. (This distinction is the review's central exposure-perception gap,
  so it must not be collapsed.)
- **CONTENT vs SHARING.** Decide on the DENOMINATOR, not on the numerator's verb. If the corpus is a
  stream of sharing ACTS (shares, retweets, link-bearing posts), it is SHARING; if it is a corpus of
  items that EXIST (an outlet's or a person's own posts, articles, videos, search results), it is
  CONTENT — including when those items happen to contain links. An ACTOR'S OWN OUTPUT is CONTENT:
  what matters is the content that exists to be seen, not who posted it.
  *(Post-campaign note, 2026-08-10: the dataset's actor rule was REFINED at v1.7.8 after this
  campaign ran — a single named actor's own output stays CONTENT, but a CLASS of actors measured by
  what they share is SHARING. This file keeps the wording coders actually received.)*

## `YOUR_breadth` — veracity strictness ONLY (blank is a valid, common answer)
Exactly three values, narrowest -> widest:
| code | means | tell |
|---|---|---|
| `fabricated` | invented/hoax content only | "fabricated", "hoax", "made-up" |
| `false` | verifiably FALSE claims checked against ground truth | fact-check "false" verdicts, expert-judged incorrect |
| `misleading` | misleading / manipulated / missing-context, NOT outright false | "misleading", "manipulated", "lacks context" |

**Leave `YOUR_breadth` BLANK whenever the definition sets no per-item veracity standard** — i.e.
when misinformation is identified by SOURCE (domain/account reliability lists such as NewsGuard or
the Grinberg list) or by a QUALITY/reliability rating. Breadth measures veracity strictness only;
source-vs-claim and quality live in other fields. Blanking these is correct, not a gap — do not
reach for the nearest of the three to avoid an empty cell.
Do NOT code `unreliable_source` / `low_quality` (retired from this scale; they will not match).
Within the three: use `misleading` only when the definition genuinely reaches BEYOND falsity to
missing-context / manipulated material. A fact-check or expert "false" standard is `false`.

### Unit of coding (keeps you consistent across the file)
`breadth` is a property of the DEFINITION, not of the row: two rows sharing the same `how_defined`
text should get the SAME breadth. `construct` and `denom_class` are per-ROW — the same definition
often appears with different reported quantities (a content share in one row, a people share in the
next), so re-read each row's `reported_quantity` rather than copying the previous row's code.

## `YOUR_denom_class` — the denominator the % is a share OF (never blank; use `n/a` if none)
Ask: **if this percentage were 100%, what would that mean?** Code what the % is a share OF — never
the topic, never what the numerator counts. Decision tree, stop at the first match:
1. a share of PEOPLE -> `population` (this beats every rule below)
2. someone's own consumption stream -> non-news media genuinely included `all_media` / all news, any
   topic `news_diet` / political-election news only `political_news`
3. the set was assembled by searching ONE topic -> `topical`
4. the set was hand-picked, seeded from already-known misinformation, or rank-truncated
   ("the top-N most shared") -> `curated_sample`
5. ONE account / channel / outlet / subreddit / broadcaster -> `single_source`. NOTE: being drawn
   from a single PLATFORM does not make a set `single_source`. A topic search run on one platform
   ("COVID videos on YouTube", "#adhdtest TikToks", "all tweets mentioning X") is `topical` — the
   set was defined by the TOPIC, and the platform is recorded in a separate field. Reach for
   `single_source` only when the universe is one specific account/outlet, not one venue.
Use `n/a` when the quantity is not a share of a defined universe:
- **every CONCENTRATION row is `n/a`** — a "top-1% of users account for 70% of exposure" statement
  has no single denominator, and concentration is typed by other fields;
- quantities that are not a share at all (conditional probabilities, per-post engagement rates —
  typically the rows you coded `OTHER`) are also `n/a`.

Recurring hard cases:
- **Surveys and self-report -> `population`, ALWAYS.** The denominator is who was ASKED, not what
  they were asked about. "38% of respondents said they had seen false COVID claims" is `population`,
  NOT `topical` — the topic is captured by a separate moderator, so coding it here double-counts it.
  Same for behavioural REACH: the denominator is the people observed, however narrow the thing counted.
- `all_media` requires non-news media genuinely inside the denominator. "All news traffic" is
  `news_diet` however comprehensive it sounds — "all" there means all *news*, not all *media*.
- A platform-wide census is not `all_media`: "all tweets mentioning X" is `topical`; "all posts on
  one platform" is `single_source` unless that platform is genuinely someone's whole diet.
- **Numerator-building vs denominator-defining.** A topic-neutral search for all COVID-vaccine
  articles, with a misinfo classifier applied only to find the false ones, is `topical` (the
  denominator is all vaccine articles). "The 5,000 most-retweeted tweets" or "the top-100 links by
  engagement" is `curated_sample` (rank truncation defines the set itself).
- A retrieval instrument whose query list deliberately includes misinformation-associated terms is
  `curated_sample` however large the corpus; `topical` requires a topic-neutral query set on ONE issue.
- A keyword corpus spanning several unrelated issues is not `topical` (that means ONE issue) ->
  `curated_sample`.
- When two readings are defensible, prefer the NARROWER category.

## `YOUR_confidence`
1-5. Use the full range: 4-5 when the two text fields settle the code, 1-2 when the quote is a
fragment that does not identify the denominator or the measurement mode. Still give your best code
on low-confidence rows — do NOT leave `YOUR_construct` or `YOUR_denom_class` blank to avoid a hard
call. Blank is a substantive answer for `YOUR_breadth` only, under the rule above.

Scored by scripts/score_codex_full.py.
