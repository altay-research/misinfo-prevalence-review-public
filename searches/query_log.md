
## 2026-09-04 — behavioural-design arm (PubMed)
TERM: ((misinformation[tiab] OR disinformation[tiab] OR "fake news"[tiab] OR "false news"[tiab] OR "unreliable news"[tiab] OR "junk news"[tiab] OR "low-quality news"[tiab] OR "news quality"[tiab] OR untrustworthy[tiab]) AND ("web tracking"[tiab] OR "browsing data"[tiab] OR "browsing history"[tiab] OR clickstream[tiab] OR "digital trace"[tiab] OR "trace data"[tiab] OR "donated data"[tiab] OR "data donation"[tiab] OR "web panel"[tiab] OR "passive metering"[tiab] OR "browser extension"[tiab] OR "server log"[tiab] OR "media diet"[tiab] OR "URL-level"[tiab] OR "platform data"[tiab]))
Hits: 23 -> behavioural_arm_pubmed_20260904.jsonl

## 2026-09-04 — behavioural-design arm (OpenAlex)
9 topic terms x 18 method terms (arm A) plus 18 method-in-title sweeps filtered on topic (arm B). Unique works 0; new to us 0. -> behavioural_arm_20260904.jsonl

> **CORRECTION, 2026-09-07.** The "0 unique works" above is not a result and must not be cited as
> one: the run lost requests to exhausted rate-limit retries, and no `behavioural_arm_20260904.jsonl`
> was ever written (the script now refuses to write a dump it cannot vouch for). A hardened repeat on
> 2026-09-07 also hit rate limits (278 calls, 504 backoffs, 82 requests lost) and correctly refused to
> write, even though it had collected 5,367 works. The arm was resumed from
> `searches/.behavioural_arm_checkpoint.json` (75 of 180 sweeps) on 2026-09-07 with a longer pause
> and is still running; its counts will be logged as a new dated entry when it completes. Nothing in
> the review depends on this arm — it is a supplementary recall check on the June searches.

## 2026-09-07 — behavioural-design arm (OpenAlex)
9 topic terms x 18 method terms (arm A) plus 18 method-in-title sweeps filtered on topic (arm B). Unique works 6972; new to us 5382. -> behavioural_arm_20260907.jsonl
