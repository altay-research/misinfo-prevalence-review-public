# Round-3 scoring report

## Task A — sacha vs pipeline (n = 200)

### ALL rows (n = 200)
| pipeline \ human | INCLUDE | MAYBE | EXCLUDE |
|---|---:|---:|---:|
| INCLUDE | 8 | 12 | 5 |
| MAYBE | 3 | 10 | 12 |
| EXCLUDE | 0 | 7 | 143 |

- Pipeline-EXCLUDE rows the human would ADVANCE (candidate pipeline misses): **7/150** (one-sided 95% upper bound on the miss rate 8.6%)
- Pipeline-ADVANCE rows the human also advances: 33/50 (66%)
- Binary advance-vs-exclude agreement 88%, Cohen κ = 0.66

### without the 14 flagged leaky-shard rows (n = 186)
| pipeline \ human | INCLUDE | MAYBE | EXCLUDE |
|---|---:|---:|---:|
| INCLUDE | 7 | 12 | 5 |
| MAYBE | 3 | 9 | 11 |
| EXCLUDE | 0 | 7 | 132 |

- Pipeline-EXCLUDE rows the human would ADVANCE (candidate pipeline misses): **7/139** (one-sided 95% upper bound on the miss rate 9.3%)
- Pipeline-ADVANCE rows the human also advances: 31/47 (66%)
- Binary advance-vs-exclude agreement 88%, Cohen κ = 0.65

Disagreement queue (24 rows) -> data/extract_v2/qa/round3_keys/disagreements_A_sacha.csv

## Task A — laura vs pipeline (n = 200)

### ALL rows (n = 200)
| pipeline \ human | INCLUDE | MAYBE | EXCLUDE |
|---|---:|---:|---:|
| INCLUDE | 14 | 5 | 6 |
| MAYBE | 6 | 8 | 11 |
| EXCLUDE | 0 | 13 | 137 |

- Pipeline-EXCLUDE rows the human would ADVANCE (candidate pipeline misses): **13/150** (one-sided 95% upper bound on the miss rate 13.4%)
- Pipeline-ADVANCE rows the human also advances: 33/50 (66%)
- Binary advance-vs-exclude agreement 85%, Cohen κ = 0.59

### without the 14 flagged leaky-shard rows (n = 186)
| pipeline \ human | INCLUDE | MAYBE | EXCLUDE |
|---|---:|---:|---:|
| INCLUDE | 13 | 5 | 6 |
| MAYBE | 6 | 7 | 10 |
| EXCLUDE | 0 | 13 | 126 |

- Pipeline-EXCLUDE rows the human would ADVANCE (candidate pipeline misses): **13/139** (one-sided 95% upper bound on the miss rate 14.5%)
- Pipeline-ADVANCE rows the human also advances: 31/47 (66%)
- Binary advance-vs-exclude agreement 84%, Cohen κ = 0.58

Disagreement queue (30 rows) -> data/extract_v2/qa/round3_keys/disagreements_A_laura.csv

## Task A — coder vs coder (n = 200)
- 3-way agreement 80%, Cohen κ = 0.46
- Binary advance-vs-exclude agreement 85%, κ = 0.56

## Task C — sacha vs pipeline (coded 50 of 50)
| pipeline \ human | INCLUDE | EXCLUDE |
|---|---:|---:|
| INCLUDED | 23 | 2 |
| DROPPED | 4 | 21 |
- Included studies the human would EXCLUDE (candidate over-inclusions): 2/25
- Dropped studies the human would INCLUDE (candidate over-exclusions): 4/25
- Agreement with pipeline 88%, κ = 0.76
- Disagreement queue (6 rows) -> data/extract_v2/qa/round3_keys/disagreements_C_sacha.csv

## Task C — laura vs pipeline (coded 50 of 50)
| pipeline \ human | INCLUDE | EXCLUDE |
|---|---:|---:|
| INCLUDED | 19 | 6 |
| DROPPED | 11 | 14 |
- Included studies the human would EXCLUDE (candidate over-inclusions): 6/25
- Dropped studies the human would INCLUDE (candidate over-exclusions): 11/25
- Agreement with pipeline 66%, κ = 0.32
- Disagreement queue (17 rows) -> data/extract_v2/qa/round3_keys/disagreements_C_laura.csv

## Task C — coder vs coder (n = 50 jointly coded)
- Agreement 66%, Cohen κ = 0.31

## Task B — sacha vs pipeline (coded 60 of 60)
| pipeline \ human | INCLUDE | MAYBE | EXCLUDE |
|---|---:|---:|---:|
| INCLUDE | 4 | 2 | 4 |
| MAYBE | 1 | 2 | 7 |
| EXCLUDE | 5 | 2 | 33 |
- Pipeline-EXCLUDE abstracts the human would ADVANCE: **7/40** (one-sided 95% UB 30.4%)
- Binary agreement 70%, κ = 0.29

## Task B — laura vs pipeline (coded 60 of 60)
| pipeline \ human | INCLUDE | MAYBE | EXCLUDE |
|---|---:|---:|---:|
| INCLUDE | 3 | 2 | 5 |
| MAYBE | 1 | 2 | 7 |
| EXCLUDE | 3 | 2 | 35 |
- Pipeline-EXCLUDE abstracts the human would ADVANCE: **5/40** (one-sided 95% UB 24.5%)
- Binary agreement 72%, κ = 0.30

## Task D — grey claims, sacha vs our coding (coded 30; 21 in the current key)
- NOTE: 9 coded claims are not in the current key (screener predates a Task-D regeneration) and are not scored.
- Category agreement 7/21 (33%), Cohen κ = 0.29
- Binary usable-estimate vs excluded: 13/21 (62%), κ = 0.28
- Disagreement queue (14) -> data/extract_v2/qa/round3_keys/disagreements_D_sacha.csv

