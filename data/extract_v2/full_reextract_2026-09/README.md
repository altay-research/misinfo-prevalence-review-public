# Full blind re-extraction, September 2026

A second, independent extraction of every study in the frozen corpus by fresh agents that never
see our coding, to catch what agreement checks cannot: estimates we missed, studies we should not
hold, and moderator codes that do not reproduce. Same model family as the original extractor
(Opus), so the paper reports it as a curation check, not as a reliability tier.

| file / folder | what it is | made by |
|---|---|---|
| `INSTRUCTIONS.md` | the repair extraction rules and schema, verbatim, with a blind preamble | `scripts/build_full_reextraction.py` |
| `batches/batch_NN.json` | 57 manifests of 8 studies: id, title, text path only | same |
| `extractions/<id>.json` | one blind extraction per study (screen, rows, moderators, notes) | one Opus agent per batch |
| `batch_reports/batch_NN.md` | the extractor's own per-paper report and judgement calls | main session, from the agent's report |
| `PROVENANCE.md` | model and status per batch | main session |
| `scores/` | screen disputes, omission queue, moderator disputes, per-study match rates, field kappas, SUMMARY.md | `scripts/score_full_reextract.py` |
| `scores/claude_suggestions.json` | Claude's call and reason on every item Sacha had not ruled | main session |
| `rulings_sacha_<date><x>.csv` | Sacha's downloads from the Desktop adjudication page (later files win) | Sacha |
| `rulings_claude_default_<date>.csv` | Sacha-approved defaults for the extractor-flagged group | main session |
| `merge_plan.py`, `merge_plan.md` | the rulings as freeze operations (removals, additions, corrections, manual items) | `scripts/plan_reextract_merge.py` |

Workflow: build -> extract (one agent per batch, resumable per paper) -> validate
(`validate_repair_extractions.py --dir ... --batch N`) -> score -> Sacha adjudicates on
`~/Desktop/reextract_adjudication.html` (`scripts/build_reextract_adjudication.py`; rulings persist
by stable key) -> archive the download here -> plan the merge -> apply in the next freeze script.
