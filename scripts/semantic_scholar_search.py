#!/usr/bin/env python3
"""
Reproducible Semantic Scholar (Graph API v1) search with backoff for rate limits.
Public endpoint needs no key, but is aggressively rate-limited (HTTP 429); set
S2_API_KEY in the environment to use a key if you have one.

Writes a timestamped JSON dump to ../searches/.
"""
import json, os, sys, time, urllib.parse, urllib.request, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SEARCH_DIR = os.path.join(HERE, "..", "searches")
BASE = "https://api.semanticscholar.org/graph/v1/paper/search"
FIELDS = "title,year,citationCount,venue,abstract,externalIds"

QUERIES = [
    "prevalence misinformation exposure systematic review meta-analysis",
    "fake news consumption concentrated small minority supersharers",
    "how much misinformation online news diet ecosystem scale",
]


def search(q, tries=5):
    key = os.environ.get("S2_API_KEY")
    headers = {"User-Agent": "misinfo-review/1.0"}
    if key:
        headers["x-api-key"] = key
    url = "%s?query=%s&limit=20&fields=%s" % (BASE, urllib.parse.quote(q), FIELDS)
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=headers)
            return json.load(urllib.request.urlopen(req, timeout=40))
        except Exception as e:
            wait = 8 * (i + 1)
            print("  retry %d (%s) waiting %ds" % (i, e, wait), file=sys.stderr)
            time.sleep(wait)
    return {"data": []}


def main():
    os.makedirs(SEARCH_DIR, exist_ok=True)
    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    out = {"run_utc": now, "queries": {}}
    for q in QUERIES:
        print("==", q)
        d = search(q)
        out["queries"][q] = d.get("data", [])
        for p in d.get("data", []):
            print("  [%s] cites=%s | %s" % (p.get("year"), p.get("citationCount"),
                                            (p.get("title") or "")[:90]))
        time.sleep(5)
    stamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(SEARCH_DIR, "semanticscholar_%s.json" % stamp)
    with open(path, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print("saved ->", os.path.relpath(path, HERE))


if __name__ == "__main__":
    main()
