# Wave 4 — the two studies the cross-family sweep never reached

The sweep covered 306 of the 315 studies the corpus then held. Of the nine it missed,
six carry no proportion at all, one reports a range rather than a point, and these two
entered the corpus in the repair after the sweep had run. Running them makes the
cross-family check complete over every study carrying a codeable estimate.

| study | what we hold | text |
|---|---|---|
| `2-s2.0-105026630069` | CONTENT 6% — share of videos coded inaccurate | `data/fulltext/v2txt/2-s2.0-105026630069.txt` |
| `2-s2.0-85136545530` | RECALL 9.9% — UK social media users who shared exaggerated or false news | `data/fulltext/v2txt/2-s2.0-85136545530.txt` |

## How to run

One fresh session per paper, in a different model family from the pipeline (the
earlier waves used GPT-5.6). Paste the whole of `batches/<id>.md`. Save the returned
JSON as `returned/<id>.json`. The instructions are wave 3's verbatim, so these two are
coded under exactly the rules the other 306 were.

## Outcome (2026-09-16)

Both returns are in `returned/`, scored by `scripts/score_gpt_wave4.py` against
`data/extract_v2/estimates_v1.7.21_frozen.csv`:
`data/extract_v2/qa/gpt_check_2026-09_wave4_scores.md`.

Seven estimates matched on value, seven agreed on construct, seven agreed on the denominator base.
No omission (nothing the second coder found that the freeze does not hold) and no extra (nothing
the freeze holds that the second coder missed); the figures it did not code, it listed with a
reason. Nothing went to adjudication.

With these two, the cross-family check covers every study in the corpus that carries a codeable
proportion — 308 of 315 at the sweep's baseline, the remaining seven carrying only quality scores
or a range.
