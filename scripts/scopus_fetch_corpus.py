#!/usr/bin/env python3
"""
Download the FULL Scopus result set for a preset.

This key's entitlement DISALLOWS the cursor parameter, and start/count paging caps at
5,000 records (total ~20k). Workaround: slice the query by publication YEAR so each
slice is < 5,000 records, then page each slice with start/count and union (dedupe by
eid). The base query MUST be parenthesised before AND-ing the year filter, else Scopus
mis-parses precedence and the year clause is ignored.

Saves a frozen snapshot to ../data/corpus_<preset>_<date>.jsonl (one record/line:
eid, doi, title, first author, year, source, type, citedby) — the title-screening input.
Abstracts are NOT in the STANDARD view; fetch them later only for survivors.

Key read from $SCOPUS_KEY. Resumable: skips eids already in the output file.
"""
import json, os, sys, time, urllib.parse, urllib.request, datetime

BASE = "https://api.elsevier.com/content/search/scopus"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from scopus_search import QUERIES  # reuse the exact preset strings  # noqa: E402

PRESET = sys.argv[1] if len(sys.argv) > 1 else "strict_v2"
COUNT = 25       # service level caps page size at 25
MAX_START = 5000  # start/count hard cap
YEARS = list(range(2015, 2027))  # year slices; pre-2015 handled as one "< 2015" slice


def api(query, start, headers):
    params = {"query": query, "count": COUNT, "start": start, "view": "STANDARD"}
    url = BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=headers)
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and attempt < 4:
                time.sleep(10 * (attempt + 1)); continue
            sys.exit("HTTP %s: %s" % (e.code, e.read().decode()[:300]))


def fetch():
    key = os.environ.get("SCOPUS_KEY") or sys.exit("set SCOPUS_KEY")
    headers = {"X-ELS-APIKey": key, "Accept": "application/json"}
    base = "( %s )" % QUERIES[PRESET]   # parenthesise before AND-ing year filter
    today = datetime.date.today().isoformat()
    outp = os.path.join(HERE, "..", "data", "corpus_%s_%s.jsonl" % (PRESET, today))

    seen = set()
    if os.path.exists(outp):
        with open(outp) as f:
            for line in f:
                try:
                    seen.add(json.loads(line)["eid"])
                except Exception:
                    pass
        print("resuming: %d records already saved" % len(seen))

    slices = ["%s AND PUBYEAR < 2015" % base] + \
             ["%s AND PUBYEAR IS %d" % (base, y) for y in YEARS]

    got = len(seen)
    with open(outp, "a") as out:
        for sl in slices:
            first_sr = api(sl, 0, headers)["search-results"]
            stotal = int(first_sr.get("opensearch:totalResults", 0))
            label = sl.split("AND PUBYEAR")[-1].strip()
            if stotal > MAX_START:
                print("!! slice '%s' has %d > %d — needs sub-splitting; SKIPPED"
                      % (label, stotal, MAX_START))
                continue
            print("slice PUBYEAR %s: %d records" % (label, stotal))
            start = 0
            while start < stotal and start < MAX_START:
                sr = first_sr if start == 0 else api(sl, start, headers)["search-results"]
                for e in sr.get("entry", []):
                    eid = e.get("eid")
                    if not eid or eid in seen:
                        continue
                    seen.add(eid)
                    out.write(json.dumps({
                        "eid": eid, "doi": e.get("prism:doi"),
                        "title": e.get("dc:title"),
                        "first_author": e.get("dc:creator"),
                        "year": (e.get("prism:coverDate") or "")[:4],
                        "source": e.get("prism:publicationName"),
                        "type": e.get("subtypeDescription"),
                        "citedby": e.get("citedby-count")}, ensure_ascii=False) + "\n")
                    got += 1
                out.flush()
                start += COUNT
                time.sleep(0.35)
            print("  running total: %d" % got)

    print("DONE: %d unique records -> %s" % (got, os.path.relpath(outp, HERE)))


if __name__ == "__main__":
    fetch()
