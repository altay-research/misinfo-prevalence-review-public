#!/usr/bin/env python3
"""Targeted recall search for BEHAVIOURAL-DESIGN prevalence studies (2026-09).

WHY THIS ARM EXISTS. The corpus is saturated on the constructs measured by coding content or asking
people (CONTENT k=275, RECALL k=94) and thin on the constructs measured from what people actually
did (EXPOSURE k=15, REACH k=24, CONCENTRATION k=17) — which are the strongest designs and carry the
review's central comparison. The likeliest reason is that the original search matched on the TOPIC
(misinformation and its synonyms) crossed with outcome words. Studies built on browsing panels,
clickstreams and donated data describe themselves by their METHOD, and often frame the topic as news
quality or exposure rather than misinformation, so a topic-first string under-catches them.

So this arm crosses the same topic terms with METHOD terms instead of outcome terms, and adds a
method-only sweep whose hits are filtered on the topic afterwards. It is a targeted recall check on
the sparse constructs, not a general top-up, and the methods section says so.

Output: searches/behavioural_arm_<date>.jsonl + a dated log line. Records already in the corpus or
already screened are marked, so the new-to-us set is explicit.
Run: python3 scripts/search_behavioural_arm.py
"""
import re, json, os, time, urllib.parse, urllib.request, urllib.error, datetime, csv
EMAIL = "sachayesilaltay@gmail.com"
# OpenAlex throttles keyless callers hard (one sweep took ~35 min on 2026-09-07). A key, read from the
# environment only and never written to disk, lifts the rate limit; the query is unchanged either way.
API_KEY = os.environ.get("OPENALEX_API_KEY", "")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOPICS = ["misinformation", "disinformation", "fake news", "false news", "unreliable news",
          "junk news", "low-quality news", "news quality", "untrustworthy"]
# how these studies describe their DATA, not their subject
METHODS = ["web tracking", "browsing data", "browsing history", "clickstream", "digital trace",
           "trace data", "donated data", "data donation", "web panel", "online panel tracking",
           "passive metering", "url-level", "desktop and mobile tracking", "browser extension",
           "platform data", "server log", "exposure log", "media diet"]
FAIL = {"http": 0, "429": 0, "calls": 0, "backoff": 0}
def get(url):
    """OpenAlex answers 429 under load. A swallowed 429 returns {} and the sweep then looks like a
    clean empty result -- which is how the 2026-09-04 run reported 0 works and was mistaken for
    evidence of absence. Back off properly, and COUNT every failure so the caller can refuse to
    treat a rate-limited run as a finished one."""
    FAIL["calls"] += 1
    for attempt in range(8):
        try:
            return json.loads(urllib.request.urlopen(
                urllib.request.Request(url, headers={"User-Agent": "research; mailto:" + EMAIL}), timeout=60).read())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                FAIL["backoff"] += 1          # a backoff that later succeeds is normal, not a failure
                if attempt == 7:
                    FAIL["429"] += 1          # only an EXHAUSTED retry is a lost request
                    return {}
                # OpenAlex tells us how long to wait when it feels like it; believe it over a guess.
                ra = e.headers.get("Retry-After") if e.headers else None
                try: wait = float(ra)
                except (TypeError, ValueError): wait = 30 * (attempt + 1)
                time.sleep(min(wait, 300)); continue
            FAIL["http"] += 1
            if attempt == 5: return {}
            time.sleep(3 * (attempt + 1))
        except Exception:
            if attempt == 5:
                FAIL["http"] += 1; return {}
            time.sleep(3 * (attempt + 1))
    FAIL["http"] += 1
    return {}
def inv2ab(inv):
    if not inv: return ""
    w = {}
    for wd, ps in inv.items():
        for p in ps: w[p] = wd
    return " ".join(w[i] for i in sorted(w))

# A sweep is minutes of work and there are 180 of them, so a throttled or interrupted run used to
# throw away everything it had. Checkpoint after every sweep and skip completed tags on resume; the
# run can then be restarted as often as the daily budget requires and still converge.
PAUSE = float(os.environ.get("PAUSE", "1.0"))
CKPT = os.path.join(ROOT, "searches/.behavioural_arm_checkpoint.json")
seen, combo, done_tags = {}, {}, set()
if os.path.exists(CKPT) and os.environ.get("FRESH", "") != "1":
    _cp = json.load(open(CKPT, encoding="utf-8"))
    seen = _cp["seen"]; combo = _cp["combo"]; done_tags = set(_cp["done_tags"])
    print(f"resuming: {len(done_tags)} sweeps already done, {len(seen)} works held")

def _save():
    json.dump({"seen": seen, "combo": combo, "done_tags": sorted(done_tags)},
              open(CKPT, "w", encoding="utf-8"), ensure_ascii=False)

def sweep(flt, tag):
    if tag in done_tags:
        return
    cur, got = "*", 0
    while cur:
        url = ("https://api.openalex.org/works?filter=%s&per-page=200&cursor=%s&mailto=%s"
               % (urllib.parse.quote(flt, safe=':,'), cur, EMAIL)) + ("&api_key=" + API_KEY if API_KEY else "")
        d = get(url)
        for w in d.get("results", []):
            e = w["id"].split("/")[-1]
            if e in seen: continue
            seen[e] = {"oaid": e, "doi": (w.get("doi") or "").replace("https://doi.org/", "").lower(),
                       "title": w.get("display_name", "") or "", "year": w.get("publication_year", ""),
                       "abstract": inv2ab(w.get("abstract_inverted_index")), "found_by": tag}
            got += 1
        cur = (d.get("meta") or {}).get("next_cursor")
        if not d.get("results"): break
        time.sleep(PAUSE)
    combo[tag] = got
    done_tags.add(tag); _save()

# arm A: topic in title/abstract x method in title/abstract
for t in TOPICS:
    for m in METHODS:
        sweep(f"title_and_abstract.search:{t},abstract.search:{m},from_publication_date:2010-01-01,type:article", f"A|{t}|{m}")
# arm B: method in title, topic filtered afterwards (catches papers whose topic wording we do not anticipate)
TOPIC_WORDS = ("misinform", "disinform", "fake news", "false news", "unreliable", "junk news",
               "low-quality news", "untrustworthy", "news quality", "credibility")
for m in METHODS:
    sweep(f"title.search:{m},from_publication_date:2010-01-01,type:article", f"B|{m}")
for k, v in list(seen.items()):
    if v["found_by"].startswith("B|"):
        blob = (v["title"] + " " + v["abstract"]).lower()
        if not any(w in blob for w in TOPIC_WORDS): del seen[k]

# mark what we have already seen. EVERY arm's id space, not just the Scopus corpus: a check that
# looked only at corpus_strict_v2 once reported four studies as missing that the freeze already had,
# because the citation-snowball arm stores OpenAlex ids and was invisible to it.
def _norm_title(t):
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()
known_doi, known_oaid, known_title = set(), set(), set()
def _absorb(path, doi_field="doi", oaid_field="oaid", title_field="title"):
    if not os.path.exists(path): return 0
    n = 0
    for line in open(path, encoding="utf-8", errors="replace"):
        try: d = json.loads(line)
        except json.JSONDecodeError: continue
        if d.get(doi_field): known_doi.add(str(d[doi_field]).lower().replace("https://doi.org/", ""))
        if d.get(oaid_field): known_oaid.add(str(d[oaid_field]).split("/")[-1])
        if d.get(title_field): known_title.add(_norm_title(d[title_field]))
        n += 1
    return n
arms = {}
for name, path in [("scopus_corpus", "data/corpus_strict_v2_2026-06-20.jsonl"),
                   ("openalex_keyword", "searches/openalex_keyword_20260624.jsonl"),
                   ("pubmed", "searches/pubmed_strict_v2_20260624.jsonl"),
                   ("snowball_candidates", "data/snowball/candidates.jsonl"),
                   ("snowball_advancing", "data/snowball/advancing.jsonl"),
                   ("openalex_netnew", "data/openalex_netnew.jsonl")]:
    arms[name] = _absorb(os.path.join(ROOT, path))
print("known-id arms:", ", ".join(f"{k} {v}" for k, v in arms.items()))
print(f"  -> {len(known_doi)} dois, {len(known_oaid)} oaids, {len(known_title)} titles")

new = 0
for v in seen.values():
    v["already_known"] = bool((v["doi"] and v["doi"] in known_doi) or v["oaid"] in known_oaid
                              or _norm_title(v["title"]) in known_title)
    new += not v["already_known"]

# A run is FAILED if requests were LOST (retries exhausted) or the yield is implausibly small.
# Backoffs that recovered are normal under rate limiting and must not block a good run -- the earlier
# version counted them as failures and would have refused to write a perfectly complete sweep.
print(f"  {FAIL['calls']} calls, {FAIL['backoff']} rate-limit backoffs, "
      f"{FAIL['429']} lost to exhausted retries, {FAIL['http']} hard failures")
if len(seen) < 200 or FAIL["429"] or FAIL["http"]:
    _save()
    print(f"  checkpoint kept: {len(done_tags)} of {len(TOPICS)*len(METHODS)+len(METHODS)} sweeps done. "
          f"Re-run to resume where this stopped (PAUSE={PAUSE}s; raise it if throttling persists).")
    raise SystemExit(f"REFUSING TO WRITE: {len(seen)} unique works from {FAIL['calls']} calls, with "
                     f"{FAIL['429']} requests lost to exhausted retries and {FAIL['http']} hard failures. "
                     f"A search that returns little while requests are being dropped is a FAILED RUN, not "
                     f"evidence of absence. Re-run when the OpenAlex daily budget has reset.")

date = datetime.date.today().isoformat().replace("-", "")
out = os.path.join(ROOT, f"searches/behavioural_arm_{date}.jsonl")
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, "w", encoding="utf-8").write("\n".join(json.dumps(v, ensure_ascii=False) for v in seen.values()))
open(os.path.join(ROOT, "searches/query_log.md"), "a", encoding="utf-8").write(
    f"\n## {datetime.date.today()} — behavioural-design arm (OpenAlex)\n"
    f"{len(TOPICS)} topic terms x {len(METHODS)} method terms (arm A) plus {len(METHODS)} method-in-title "
    f"sweeps filtered on topic (arm B). Unique works {len(seen)}; new to us {new}. -> {os.path.basename(out)}\n")
print(f"behavioural arm: {len(seen)} unique works, {new} not already known -> {out}")
os.remove(CKPT) if os.path.exists(CKPT) else None   # a clean run retires its checkpoint
