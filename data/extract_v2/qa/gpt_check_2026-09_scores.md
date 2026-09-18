# Independent cross-check of the corpus-repair extractions — scores

A different model family (OpenAI gpt-5.6-luna, run in Codex) re-coded 313 estimate rows from 106 studies, one file per fresh session, blind file before verify file.

## Fact-check pass (our value, denominator and construct were shown)

313 rows checked against the papers. **Confirmed outright: 250 (79.9%).**

| verdict | rows | share |
|---|---|---|
| correct | 250 | 79.9% |
| not in paper | 16 | 5.1% |
| wrong value | 14 | 4.5% |
| paper not eligible | 14 | 4.5% |
| wrong construct | 13 | 4.2% |
| wrong denominator | 6 | 1.9% |

This is an error rate, not an agreement statistic: the second coder saw our answer, so it cannot be turned into a kappa. Every non-CORRECT row is a dispute to adjudicate against the paper.

### Confirmation rate by the construct we assigned

| construct | rows | confirmed |
|---|---|---|
| CONTENT | 133 | 83% |
| RECALL | 132 | 79% |
| QUALITY | 26 | 62% |
| SHARING | 14 | 79% |
| CONCENTRATION | 6 | 100% |
| EXPOSURE | 2 | 100% |

### Confirmation rate by our own borderline flag

| our flag | rows | confirmed |
|---|---|---|
| not borderline | 216 | 91% |
| borderline | 97 | 55% |

## Blind pass (our construct was hidden)

313 rows coded from the reported quantity, the denominator sentence and the paper's own definition of misinformation, with our code withheld.

- percent agreement **81.8%**
- Cohen's kappa **0.732**

This is the reliability figure for the repair's construct coding, and it is comparable to the kappa .802 the frozen corpus carries from its own independent-model check.

### Where the blind coder differed

| ours | theirs | rows |
|---|---|---|
| CONTENT | QUALITY | 23 |
| RECALL | SHARING | 18 |
| QUALITY | CONTENT | 6 |
| CONTENT | OTHER | 5 |
| QUALITY | SHARING | 2 |
| QUALITY | EXPOSURE | 1 |
| SHARING | CONTENT | 1 |
| RECALL | OTHER | 1 |

## Adjudication queue

104 rows to adjudicate against the papers: 63 flagged by the fact-check pass, plus 41 the fact-check confirmed but the blind coder typed differently. -> `data/extract_v2/qa/gpt_check_2026-09_disputes.csv`

No verdict is applied automatically. Each row is read against its paper and ruled ours, theirs, or a third reading, with the reason recorded — the same rule used for every earlier cross-check.

