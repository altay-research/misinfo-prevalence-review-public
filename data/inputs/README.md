# data/inputs/ — hand-curated analysis inputs

Files here are **inputs**, not outputs. Nothing in the Phase B pipeline regenerates them: each was
assembled by hand (or by a documented agent extraction round) from source papers, and each carries a
verbatim quote per row so it can be re-checked against the source. They live here rather than in
`data/synth/phaseB/` because that directory is regenerated wholesale on every re-freeze, and a
hand-made file sitting in it can be destroyed by a `rm -rf` + re-run without anyone noticing.

If you delete `data/synth/phaseB/` and re-run the pipeline, everything there comes back. Delete a
file here and it is gone.

| file | rows | provenance | read by |
|---|---:|---|---|
| `nonmisinfo_concentration.csv` | 25 | 2026-07-22 extraction round: 8 parallel quote-anchored agents over the 39 panel/concentration studies in the corpus, pulling **general-activity** (non-misinformation) concentration quantities so misinformation concentration has a comparator. 24 quantities from 14 studies. `docs/research_log.md`, entry "2026-07-22 — Phase B round 2". | `phaseB_figures3.py` (figK), `phaseB_review_response.py` (matched ratio), `check_manuscript_stats.py` |
| `nonmisinfo_concentration_extra.csv` | 5 | 2026-07-22, same day: a second agent pass mining the wider local PDF library (Muise, Wojcieszak, Pew, Lorenz-Spreen, Allen) for general news/activity concentration baselines outside the review corpus. `docs/research_log.md`, entry "2026-07-22 — more non-misinfo concentration comparators (library mining)". Context/caveat table only. | no script (context table; kept for the record) |
| `si_biblio_manual.csv` | 9 | Bibliography for the nine included studies that no machine-readable source resolves: six user-supplied PDFs, two Berriche-seed studies and one arXiv posting, all keyed by a hand-assigned id (`NEW-…`, `SEED-…`, `2603.11058`). Five rows carry only the DOI, verified against the archived text, so the fields themselves are fetched from the registry rather than typed; four have no DOI at all and carry fields read off the document's own title page. Every row's `source` column names where each field came from. | `make_si_lists.py` |
| `topic_input.jsonl` | 317 | The per-study packet handed to the 16 parallel topic-coding agents in the v1.4.6 `topic` moderator pass (one line per study in the v1.4.5 freeze: id, country, platform, denom_class, misinfo_def, quotes). Codes came back through `scripts/aggregate_topics.py` → `data/extract_v2/qa/topics_v146.csv`. `docs/research_log.md`, entry "v1.4.6 descriptive completeness". | no live script (round input; `aggregate_topics.py` is freeze history and needs `$CLAUDE_JOB_DIR`) |

## Columns

`nonmisinfo_concentration.csv` — `id` (study id, matching the freeze where the study is in the
corpus), `top_pct` (the top band as a % of users/sources), `share` (% of activity that band accounts
for), `denom` (what the activity is: `all_news`, `political`, `other` …; `other` marks a
misinformation-side figure quoted alongside for the side-by-side), `measure` (`topX_share`),
`detail` (plain-language statement of the quantity; consumers filter on `DOMAIN` and `MISINFO`
markers here), `quote` (verbatim source sentence), `note` (extraction note).

`nonmisinfo_concentration_extra.csv` — `cite`, `title`, `top_pct_people`, `share_pct`,
`denominator`, `measure`, `note`, `quote`.

`si_biblio_manual.csv` — `study_id` (matching the freeze), `first_author`, `year`, `title`, `venue`,
`doi`, `source`. A blank field means "not asserted here": `make_si_lists.py` falls through to the
DOI lookup for it. `source` plays the role `quote` plays in the other files — it states, per row,
which document or ledger line each asserted field was read from.

`topic_input.jsonl` — one JSON object per study: `id`, `existing_topic`, `country`, `platform`,
`denom_class`, `misinfo_def`, plus the quote fields the coders read.

## Rules

- Treat these as immutable once used in a freeze's analysis. A correction is a new dated row or a
  new file, logged in `docs/research_log.md`, never a silent edit.
- Every row must keep its verbatim `quote` (`source`, in `si_biblio_manual.csv`). A row without one
  cannot be re-checked and does not belong here.
- Do not move these back into `data/synth/phaseB/`.
