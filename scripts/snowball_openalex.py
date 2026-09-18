#!/usr/bin/env python3
"""
Citation snowball + non-Scopus venue catch via OpenAlex (free, broader than Scopus).
Backward (references) + forward (citing works) from the 224 core audience-side included
studies, plus a targeted Journal of Quantitative Description venue sweep. Topic-filtered
and de-duplicated against the frozen Scopus corpus. Output: data/snowball/candidates.jsonl
(new, not-in-corpus, topic-relevant works to screen). Reproducible; OpenAlex polite pool.
"""
import json, re, time, urllib.parse, urllib.request, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
MAIL = "sachayesilaltay@gmail.com"
TOPIC = re.compile(r"misinfo|disinfo|fake news|false news|false information|fact.?check|"
                   r"untrustworthy|unreliable|low.?quality news|junk news|news diet|"
                   r"rumor|rumour|conspirac|hoax|falsehood|dubious|pseudoscien|"
                   r"information disorder|media diet|news exposure", re.I)

def api(url, tries=4):
    for t in range(tries):
        try:
            req = urllib.request.Request(url + ("&" if "?" in url else "?") + "mailto=" + MAIL,
                                         headers={"User-Agent": "misinfo-review/1.0 " + MAIL})
            return json.load(urllib.request.urlopen(req, timeout=60))
        except Exception as e:
            if t == tries - 1: return {"_err": str(e)}
            time.sleep(2 * (t + 1))

def deinvert(inv):
    if not inv: return ""
    pos = {}
    for w, ix in inv.items():
        for i in ix: pos[i] = w
    return " ".join(pos[i] for i in sorted(pos))[:1500]

corpus = json.load(open(os.path.join(ROOT, "data/snowball/corpus_keys.json")))
seen_doi = set(corpus["doi"]); seen_title = set(corpus["title"])
def norm(t): return re.sub(r"[^a-z0-9]", "", (t or "").lower())[:60]

dois = [d.strip() for d in open(os.path.join(ROOT, "data/snowball/core_dois.txt")) if d.strip()]
log = open(os.path.join(ROOT, "data/snowball/snowball.log"), "w")
def say(m):
    print(m); log.write(m + "\n"); log.flush()

# ---- Phase A: fetch core works (batched by DOI) -> OA ids + backward refs ----
core_ids, backward = [], set()
B = 40
for i in range(0, len(dois), B):
    chunk = "|".join(dois[i:i+B])
    r = api("https://api.openalex.org/works?filter=doi:" + urllib.parse.quote(chunk) + "&per-page=" + str(B) + "&select=id,referenced_works,doi")
    for w in (r or {}).get("results", []):
        core_ids.append(w["id"].split("/")[-1])
        for ref in (w.get("referenced_works") or []): backward.add(ref.split("/")[-1])
    say("backward: core %d/%d, refs so far %d" % (min(i+B, len(dois)), len(dois), len(backward)))
    time.sleep(0.3)

# ---- Phase B: forward citations (topic-filtered, capped) ----
forward = {}
for j, cid in enumerate(core_ids):
    r = api("https://api.openalex.org/works?filter=cites:" + cid + ",from_publication_date:2015-01-01&per-page=200&select=id,display_name,publication_year,doi,primary_location,abstract_inverted_index")
    for w in (r or {}).get("results", []):
        if TOPIC.search(w.get("display_name") or ""):
            forward[w["id"].split("/")[-1]] = w
    if j % 25 == 0: say("forward: core %d/%d, topic-citing collected %d" % (j, len(core_ids), len(forward)))
    time.sleep(0.25)

# ---- Phase C: JQD venue catch ----
venue_hits = {}
src = api("https://api.openalex.org/sources?search=journal of quantitative description")
jqd = next((s["id"].split("/")[-1] for s in (src or {}).get("results", []) if "quantitative description" in s["display_name"].lower()), None)
say("JQD source id: %s" % jqd)
if jqd:
    page = 1
    while True:
        r = api("https://api.openalex.org/works?filter=primary_location.source.id:%s&per-page=200&page=%d&select=id,display_name,publication_year,doi,primary_location,abstract_inverted_index" % (jqd, page))
        res = (r or {}).get("results", [])
        if not res: break
        for w in res:
            if TOPIC.search((w.get("display_name") or "") + " " + deinvert(w.get("abstract_inverted_index"))):
                venue_hits[w["id"].split("/")[-1]] = w
        if len(res) < 200: break
        page += 1; time.sleep(0.3)
say("JQD topic works: %d" % len(venue_hits))

# ---- Phase D: fetch backward metadata, merge, dedupe, topic-filter, output ----
have_meta = dict(forward); have_meta.update(venue_hits)
backward = [b for b in backward if b not in have_meta]
ids = list(backward)
for i in range(0, len(ids), 50):
    chunk = "|".join(ids[i:i+50])
    r = api("https://api.openalex.org/works?filter=openalex_id:" + chunk + "&per-page=50&select=id,display_name,publication_year,doi,primary_location,abstract_inverted_index")
    for w in (r or {}).get("results", []):
        have_meta[w["id"].split("/")[-1]] = w
    if i % 500 == 0: say("backward meta: %d/%d" % (i, len(ids)))
    time.sleep(0.25)

out = open(os.path.join(ROOT, "data/snowball/candidates.jsonl"), "w")
kept = 0
for oaid, w in have_meta.items():
    title = w.get("display_name") or ""
    abs = deinvert(w.get("abstract_inverted_index"))
    if not TOPIC.search(title + " " + abs): continue
    doi = (w.get("doi") or "").lower().replace("https://doi.org/", "")
    if doi and doi in seen_doi: continue
    if norm(title) in seen_title: continue
    ven = (((w.get("primary_location") or {}).get("source") or {}) or {}).get("display_name", "")
    out.write(json.dumps({"oaid": oaid, "title": title, "year": w.get("publication_year"),
                          "doi": doi, "venue": ven, "abstract": abs}, ensure_ascii=False) + "\n")
    kept += 1
out.close()
say("CANDIDATES (new, topic-relevant, not in corpus): %d" % kept)
say("  sources: backward=%d forward=%d venue=%d" % (len(backward), len(forward), len(venue_hits)))
