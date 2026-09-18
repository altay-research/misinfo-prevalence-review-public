# RA keep/drop reliability — report BOTH figures (Sacha's decision 2026-07-15)

The independent double-coding answer key (`_ANSWER_KEY.csv`) is **NOT edited**. It stays the
gold standard Laura (RA1) was blind-scored against. But 10 of its `our_keep=Y` items were later
**dropped in the frozen v1.2 dataset** (via the RA-verification adjudication + the 20-study
re-audit). So we report two agreement figures against the *same* Laura codes, computed by
`scripts/ra_kappa_dual.py` (→ `ra_kappa_dual.json`):

| figure | comparison | raw | Cohen κ | Gwet AC1 |
|---|---|---|---|---|
| **PRIMARY (headline)** | Laura vs frozen-at-scoring key | 0.68 | **0.328** | 0.426 |
| SECONDARY (sensitivity) | Laura vs final v1.2 dataset | 0.74 | **0.463** | 0.508 |

- **PRIMARY** is the methodologically standard number: blind, independent, key never touched.
  It reproduces `reliability_reconciled.json` exactly (0.68 / 0.328 / 0.426).
- **SECONDARY** re-scores the same Laura codes against final v1.2 membership (kept iff the study
  id is in `estimates_v1.2_frozen.csv`). It is **not blind** — it folds in RA-driven post-hoc
  drops the key predates — so it is a sensitivity line, not the headline.

**Why SECONDARY is higher:** of the 10 items where the key said keep but v1.2 dropped, Laura
had independently voted *drop* on 8 of them — so those move from disagreement (FN) to agreement
(TN). Confusion vs reference: PRIMARY TP51/FP3/FN29/TN17 → SECONDARY TP49/FP5/FN21/TN25. In other
words, much of Laura's apparent "over-exclusion" against the key was **vindicated** once the
dataset incorporated the same scrutiny; only 2 of her keeps were dropped in v1.2 against her.

**The 10 divergent items (key=Y, v1.2 dropped)** — reasons in `data/extract_v2/qa/v1.2_drops_ledger.csv`:
2-s2.0-105011696813, 2-s2.0-105014962937, 2-s2.0-105031695645, 2-s2.0-105041276064,
2-s2.0-84869090226, 2-s2.0-85056602344, 2-s2.0-85105969129, 2-s2.0-85151055175,
OA-W4401812299, W2953415400.

**Manuscript wording (suggested):** "Blind independent keep/drop agreement between the LLM key and
the human coder was κ = 0.33 (raw 68%); scored against the final adjudicated dataset the same coder's
agreement rose to κ = 0.46 (raw 74%), reflecting that most apparent over-exclusions were upheld on
full-text re-audit." Also relabel every κ as inter-LLM where the *key itself* is the reference
(the key was LLM-generated, quote-anchored) — see planned-analyses P4.
