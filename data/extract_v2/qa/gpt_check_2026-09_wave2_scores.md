# Independent cross-check of the corpus-repair extractions — scores

A different model family (OpenAI gpt-5.6-luna, run in Codex) re-coded 155 estimate rows from 78 studies, one file per fresh session, blind file before verify file.

## Fact-check pass (our value, denominator and construct were shown)

155 rows checked against the papers. **Confirmed outright: 139 (89.7%).**

| verdict | rows | share |
|---|---|---|
| correct | 139 | 89.7% |
| wrong construct | 11 | 7.1% |
| paper not eligible | 2 | 1.3% |
| wrong value | 2 | 1.3% |
| not in paper | 1 | 0.6% |

This is an error rate, not an agreement statistic: the second coder saw our answer, so it cannot be turned into a kappa. Every non-CORRECT row is a dispute to adjudicate against the paper.

### Confirmation rate by the construct we assigned

| construct | rows | confirmed |
|---|---|---|
| RECALL | 74 | 95% |
| CONTENT | 67 | 87% |
| SHARING | 14 | 79% |

### Confirmation rate by our own borderline flag

| our flag | rows | confirmed |
|---|---|---|
| not borderline | 114 | 95% |
| borderline | 41 | 76% |

## Blind pass (our construct was hidden)

155 rows coded from the reported quantity, the denominator sentence and the paper's own definition of misinformation, with our code withheld.

- percent agreement **91.6%**
- Cohen's kappa **0.859**

This is the reliability figure for the repair's construct coding, and it is comparable to the kappa .802 the frozen corpus carries from its own independent-model check.

### Where the blind coder differed

| ours | theirs | rows |
|---|---|---|
| CONTENT | QUALITY | 6 |
| SHARING | CONTENT | 3 |
| CONTENT | OTHER | 1 |
| SHARING | QUALITY | 1 |
| CONTENT | SHARING | 1 |
| RECALL | SHARING | 1 |

## Adjudication queue

23 rows to adjudicate against the papers: 16 flagged by the fact-check pass, plus 7 the fact-check confirmed but the blind coder typed differently. -> `data/extract_v2/qa/gpt_check_2026-09_disputes.csv`

No verdict is applied automatically. Each row is read against its paper and ruled ours, theirs, or a third reading, with the reason recorded — the same rule used for every earlier cross-check.

