# Independent cross-check of a systematic review's extractions — one batch per session

You are the SECOND coder for a systematic review of the prevalence, exposure, sharing and
concentration of misinformation. Another model extracted these estimates from the full texts. Your
job is to check that work against the papers, independently. Being right matters more than agreeing.

Paper texts are in `texts/<item_id>.txt`, for the verify task only. Do not use the web, and do not
read any file outside this folder.

## ONE FILE PER SESSION — code the file you were given, save it, and stop
You are given ONE csv, either a `blind_NN.csv` or a `verify_NN.csv`. Fill that file only, save it in
place, and stop. Do not open the other file of the same batch, and do not start another batch. Long sessions degrade:
in an earlier campaign a coder reproduced only 45% of its own codes late in a 647-row session.

## The two file types
A batch is two files over the same rows, run in SEPARATE sessions. `blind_NN.csv` is coded from the
worksheet fields alone and never opens a paper. `verify_NN.csv` is checked against the full texts.
The blind file must be done before the verify file of the same batch is opened in any session,
because the verify file shows our own construct codes and seeing them would void the blind coding.

---

## Task 1 — `blind_NN.csv` (our construct is NOT shown; code it yourself)

Each row gives the quantity as reported, the denominator sentence and how the paper defined
misinformation. Code the construct FROM THOSE FIELDS ALONE: do not open the paper, do not open any
other file. Fill `YOUR_construct` and `YOUR_confidence` (1-5). If the fields genuinely do not settle
it, code your best reading and give it confidence 1 or 2 rather than leaving it blank.

## Task 2 (do this SECOND) — `verify_NN.csv` (our extraction is shown; check it)

Each row is one estimate we recorded, with `our_value_pct`, `our_denominator`, `our_construct`,
`our_measure_type` and `our_source_quote` (the sentence we took the number from).

Fill four columns:

`YOUR_verdict` — one of:
- `CORRECT` — the value, its denominator and the construct are all right.
- `WRONG_VALUE` — the number is not what the paper reports (wrong figure, wrong rounding,
  transposed, or computed when the paper never states it).
- `WRONG_DENOMINATOR` — the number is right but it is a share of something else than we say
  (e.g. we say "of respondents" and it is "of those who saw any"; we say 100 answers and the
  paper's base is 100 answers x 4 raters).
- `WRONG_CONSTRUCT` — see the construct rules below.
- `NOT_IN_PAPER` — you cannot find this figure anywhere in the text.
- `PAPER_NOT_ELIGIBLE` — the paper reports no quantitative misinformation share at all, or is an
  excluded design (detection/classifier work, an intervention or correction experiment, belief or
  discernment only, hypothetical sharing intentions, review/commentary, qualitative only).

`YOUR_value_pct` — the number you believe is correct (plain, e.g. `23.4`). Copy ours if you agree.
`YOUR_quote` — the VERBATIM sentence or table cell in the text that carries your number. Mandatory
whenever you give a value. Copy exactly, do not translate or tidy.
`YOUR_note` — one short line: what is wrong, or what you checked. For `PAPER_NOT_ELIGIBLE`, the ground.

Rules that govern what counts as a correct value:
- A value is acceptable if the paper states it VERBATIM, or if it is an exact part/whole from
  verbatim counts with the same denominator (44/150 = 29.3%). A cross-category SUM, a COMPLEMENT
  (100 - 56.5), a rounding or a figure the paper cites from another study is NOT acceptable —
  flag those `WRONG_VALUE` even if the arithmetic is right.
- A percentage of a MEAN is never a share. If the paper reports only a scale mean ("exposure
  M = 2.4 on 1-5"), no share exists: `NOT_IN_PAPER`.

## The construct rules (they govern both tasks)

THE DENOMINATOR SETS THE CONSTRUCT. Ask: this percentage is a share OF WHAT?
- all items that EXIST (a platform's, outlet's or person's posts, videos, websites, search
  results, chatbot answers) -> `CONTENT`
- what people CONSUMED (views, visits, clicks, share of diet) -> `EXPOSURE`
- PEOPLE who encountered it at least once, measured behaviourally -> `REACH`
- a stream of SHARING acts (shares, retweets, engagement), or the share of users who shared
  -> `SHARING`
- what respondents SAY they saw or shared (any survey self-report; "perceived amount of
  misinformation around me" counts) -> `RECALL`
- a top group of users or sources accounting for a share of activity -> `CONCENTRATION`
- a usefulness, completeness, reliability or "quality" rating rather than a truth judgement
  (DISCERN, GQS, JAMA, guideline-coverage checklists) -> `QUALITY`
- none of these -> `OTHER`

Two boundaries that decide most disputes:
- "% of shared links that were unreliable" is `SHARING`, not `CONTENT`: the denominator is the
  shared links. One named actor's own output is `CONTENT`; a class of actors measured by what they
  share follows the paper's own framing, usually `SHARING`.
- `CONTENT` requires a truth judgement against an external standard (fact-checks, expert
  verification, an explicit accurate/inaccurate coding, a source-reliability list). If a wholly
  TRUE item could receive the label — "misleading" meaning it covered fewer than four screener
  items, or a low DISCERN score — it is `QUALITY`, whatever the paper calls it.

Return the CSV with every row filled, `item_id` and row order unchanged, and nothing else edited.
