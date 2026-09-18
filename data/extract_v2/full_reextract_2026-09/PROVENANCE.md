# Full blind re-extraction 2026-09 — provenance

Built 2026-09-07 by `scripts/build_full_reextraction.py` from FROZEN v1.7.16 (456 studies): 57
batches of 8, seeded shuffle (seed 20260907), 428 full texts + 28 archived abstracts. Manifests carry
id, title and text path only; no frozen value, construct or hint reaches the extractor.

Extractor: Claude Opus (Claude Code subagent, one fresh session per batch, `model: opus`), on
Sacha's instruction of 2026-09-07 (GPT credit exhausted; "a good Claude model like Opus 5 or Fable").
Same base family as the pipeline coder, so this is reported as a curation check (omissions and
moderator errors caught), NOT as an independent-family reliability tier. Batch-level log below.

| batch | model | date | status |
|---|---|---|---|
| 01 | opus | 2026-09-07 | done, validator clean, 8/8 INCLUDE, 11 rows |
| 03 | opus | 2026-09-07 | done, validator clean, 7/8 INCLUDE (1 QUALITY-only dispute), 21 rows |
| 02 | opus | 2026-09-07 | done, validator clean, 8/8 INCLUDE, 31 rows |
| 05 | opus | 2026-09-07 | done, validator clean, 8/8 INCLUDE, 13 rows |
| 04 | opus | 2026-09-07 | done, validator clean, 8/8 INCLUDE, 17 rows |
| 07 | opus | 2026-09-07 | done, validator clean, 8/8 INCLUDE, 11 rows |
| 09 | opus | 2026-09-07 | done, validator clean, 6/8 INCLUDE (news feature + quality-only excluded), 11 rows |
| 06 | opus | 2026-09-07 | done, validator clean, 8/8 INCLUDE, 17 rows |
| 10 | opus | 2026-09-07 | done, validator clean, 8/8 INCLUDE, 18 rows |
| 08 | opus | 2026-09-07 | done, validator clean, 8/8 INCLUDE, 21 rows |
| 13 | opus | 2026-09-07 | done in two sessions (limit kill), validator clean, 7/8 INCLUDE |
| 11 | opus | 2026-09-07 | done (quotes repaired in a second session), validator clean, 8/8 INCLUDE, 14 rows |
| 12 | opus | 2026-09-07 | done in two sessions (limit kill), validator clean |
| 16 | opus | 2026-09-08 | done, validator clean, 8/8 INCLUDE, 14 rows |
| 15 | opus | 2026-09-08 | done, validator clean, 7/8 INCLUDE, 11 rows |
| 14 | opus | 2026-09-08 | done in two sessions (limit kill), validator clean |
| 19 | opus | 2026-09-08 | done (repaired in a second session), validator clean, 8/8 INCLUDE, 17 rows |
| 20 | opus | 2026-09-08 | done in two sessions (limit kill), validator clean |
| 22 | opus | 2026-09-08 | done in two sessions (limit kill), validator clean |
| 21 | opus | 2026-09-08 | done in two sessions (limit kill), validator clean |
| 17 | opus | 2026-09-08 | done in two sessions (limit kill), validator clean |
| 18 | opus | 2026-09-08 | done (repaired in a second session), validator clean |
| 23 | opus | 2026-09-08 | done, validator clean, 8/8 INCLUDE, 24 rows |
| 24 | opus | 2026-09-08 | done (validated in a second session), validator clean, 8/8 INCLUDE, 19 rows |
| 26 | opus | 2026-09-08 | done (quotes repaired in a second session), validator clean, 8/8 INCLUDE, 14 rows |
| 25 | opus | 2026-09-08 | done in two sessions, validator clean, 7/8 INCLUDE (84929523850 wrong_paper) |
| 27 | opus | 2026-09-08 | done in two sessions, validator clean |
| 28 | opus | 2026-09-08 | done in two sessions, validator clean, 8/8 INCLUDE, 31 rows |
| 29 | opus | 2026-09-08 | done, validator clean, 8/8 INCLUDE, 28 rows |
| 31 | opus | 2026-09-08 | done, validator clean, 7/8 INCLUDE, 14 rows |
| 30 | opus | 2026-09-08 | done, validator clean, 8/8 INCLUDE, 19 rows |
| 32 | opus | 2026-09-08 | done, validator clean, 7/8 INCLUDE, 17 rows |
| 33 | opus | 2026-09-08 | done, validator clean, 8/8 INCLUDE, 21 rows |
| 34 | opus | 2026-09-08 | done, validator clean, 8/8 INCLUDE, 32 rows |
| 35 | opus | 2026-09-08 | done, validator clean, 8/8 INCLUDE, 16 rows |
| 36 | opus | 2026-09-08 | done, validator clean, 8/8 INCLUDE, 14 rows |
| 38 | opus | 2026-09-08 | done, validator clean, 8/8 INCLUDE, 12 rows |
| 37 | opus | 2026-09-08 | done, validator clean, 7/8 INCLUDE, 12 rows |
| 41 | opus | 2026-09-09 | done in two sessions, validator clean |
| 42 | opus | 2026-09-09 | done in two sessions, validator clean |
| 39 | opus | 2026-09-09 | done (validated in a second session), validator clean, 7/8 INCLUDE |
| 40 | opus | 2026-09-09 | done (validated in a second session), validator clean, 6/8 INCLUDE |
| 44 | opus | 2026-09-09 | done, validator clean, 8/8 INCLUDE, 23 rows |
| 43 | opus | 2026-09-09 | done, validator clean, 8/8 INCLUDE, 26 rows |
| 45 | opus | 2026-09-09 | done, validator clean, 7/8 INCLUDE, 14 rows |
| 46 | opus | 2026-09-09 | done, validator clean, 6/8 INCLUDE (85147303661 wrong_paper) |
| 47 | opus | 2026-09-09 | done, validator clean, 8/8 INCLUDE, 30 rows |
| 48 | opus | 2026-09-09 | done, validator clean, 7/8 INCLUDE, 13 rows |
| 49 | opus | 2026-09-09 | done, validator clean, 8/8 INCLUDE, 31 rows |
| 50 | opus | 2026-09-09 | done, validator clean, 8/8 INCLUDE, 15 rows |
| 52 | opus | 2026-09-09 | done in two sessions, validator clean |
| 53 | opus | 2026-09-09 | done in two sessions, validator clean |
| 51 | opus | 2026-09-09 | done (validated in a second session), validator clean, 7/8 INCLUDE |
| 54 | opus | 2026-09-09 | done, validator clean, 8/8 INCLUDE, 26 rows |
| 55 | opus | 2026-09-09 | done, validator clean after quote repairs, 8/8 INCLUDE, 16 rows |
| 56 | opus | 2026-09-09 | done, validator clean after quote repairs, 8/8 INCLUDE, 17 rows |
| 57 | opus | 2026-09-09 | done, validator clean, 7/8 INCLUDE (fluoride/Instagram EXCLUDE, quality-only), 11 rows — CAMPAIGN COMPLETE |
