# Wave 5 — the studies no cross-family check had read

38 estimates across 22 studies, the residual of the released corpus
(444 studies) once every earlier independent pass is
counted. Same instrument as the sweep that produced construct κ = 0.80, so these rows
join that statistic rather than sitting beside it.

| study | rows | construct |
|---|---:|---|
| `2-s2.0-105011756924` | 1 | RECALL |
| `2-s2.0-85145196122` | 2 | CONTENT |
| `W3171657220` | 1 | RECALL |
| `W4210350805` | 5 | RECALL |
| `W4306960737` | 3 | CONTENT |
| `W4313324568` | 2 | RECALL |
| `W4318617911` | 1 | CONTENT |
| `W4383851554` | 1 | CONTENT |
| `W4385325063` | 1 | EXPOSURE |
| `W4389633384` | 1 | CONTENT |
| `W4400887711` | 1 | CONTENT |
| `W4409319996` | 1 | CONTENT |
| `W4414259328` | 1 | REACH |
| `W4414351820` | 1 | RECALL |
| `W4417119300` | 1 | CONTENT |
| `W7117302408` | 1 | RECALL |
| `W7162938155` | 1 | CONTENT |
| `W7163821603` | 1 | RECALL |
| `W7166447493` | 1 | CONTENT |
| `W7168027278` | 2 | RECALL |
| `W7170181457` | 8 | CONTENT, QUALITY |
| `W7171843315` | 1 | CONTENT |

## How to run

ONE fresh session in a different model family. Paste `WAVE5_INSTRUCTIONS.md`, give
it `wave5_worklist.csv`, and have it code the four fields for every row blind. Do
not open the answer key (it is not in the Desktop copy).

**It saves its answers as a JSON file in the `returned/` folder of this package:**
`returned/wave5_codes.json`, one object keyed by `item_id`. The instructions spell
out the shape. Nothing else comes back: the worklist is not edited.

Then: `python3 scripts/score_codex_full.py --dir docs/codex_check_wave5 --key WAVE5_ANSWER_KEY.csv returned/wave5_codes.json`.
