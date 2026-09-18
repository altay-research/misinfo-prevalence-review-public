#!/usr/bin/env python3
"""
Reproducible Scopus search for the misinformation prevalence/concentration review.

Reads the API key from the environment variable SCOPUS_KEY (never hard-coded).
Every run writes a timestamped JSON dump to ../searches/ AND appends a one-line
record (query, count, date) to ../searches/scopus_query_log.tsv so the search
history is auditable and reproducible.

Usage:
    export SCOPUS_KEY="...your key..."          # do NOT commit this
    python3 scopus_search.py --name strict_v1 --query 'TITLE-ABS-KEY ( ... )'
    python3 scopus_search.py --preset strict    # run a named preset from QUERIES

Notes on reproducibility:
    * Scopus is a live database; a hit count is only reproducible *as of the run
      date*. The run date (UTC) is recorded in every output file and in the log.
    * --count controls how many entries are saved per call; --max paginates to
      retrieve the full result set (cursor-based) when you need the actual records,
      not just the total.
"""
import argparse, json, os, sys, time, urllib.parse, urllib.request, datetime

BASE = "https://api.elsevier.com/content/search/scopus"
HERE = os.path.dirname(os.path.abspath(__file__))
SEARCH_DIR = os.path.join(HERE, "..", "searches")

# ---- Named query presets (edit here; every change is tracked in git) -----------
TOPIC = ('( misinformation OR disinformation OR "fake news" OR "false news" '
         'OR "unreliable news" OR "untrustworthy websites" OR "low-quality news" '
         'OR "junk news" )')
EXPOSURE = ('( exposure OR consumption OR reach OR audience OR "news diet" '
            'OR prevalence OR circulation )')
NOTCS = (' AND NOT TITLE-ABS-KEY ( detection OR classifier OR classification '
         'OR "deep learning" OR "neural network" OR "machine learning" OR blockchain '
         'OR algorithm OR transformer OR dataset )')

# v2 (recommended after recall validation 2026-06-20): broadened measurement family
# (exposure AND sharing/spread/scale/quantification) + TITLE-only CS exclusion.
# Recall vs Berriche seed set: 14/16 indexed studies (vs 8/16 for v1 "strict").
MEASURE_V2 = ('( exposure OR consumption OR consume* OR reach OR audience OR "news diet" '
              'OR "information diet" OR prevalence OR circulation OR sharing OR shared '
              'OR spread OR diffusion OR dissemination OR quantif* OR "how much" '
              'OR supersharer* OR "super-sharer*" OR traffic OR visits OR engagement OR scale )')
NOTCS_TITLE = (' AND NOT TITLE ( detection OR classifier OR classification '
               'OR "deep learning" OR "neural network" OR transformer )')

# Concentration-targeted SUPPLEMENTARY search (robustness, 2026-06-21): strict_v2's
# MEASURE block under-targets concentration (has supersharer* but not concentration/Gini/
# skew/top-X%/inequality/superspreader). Run when the Scopus key resets; merge NEW eids
# into the corpus; report as a sensitivity analysis. `concentration_missed` finds those
# NOT already caught by the MEASURE_V2 block.
CONC = ('( concentration OR Gini OR skewed OR "long tail" OR inequality OR "top 1%" '
        'OR "top 10%" OR superspreader* OR superconsumer* OR "small minority" '
        'OR "small number of" OR disproportionate OR "heavy users" )')

QUERIES = {
    "strict": "TITLE-ABS-KEY ( %s AND %s )%s" % (TOPIC, EXPOSURE, NOTCS),
    "strict_v2": "TITLE-ABS-KEY ( %s AND %s )%s" % (TOPIC, MEASURE_V2, NOTCS_TITLE),
    "concentration_supp": "TITLE-ABS-KEY ( %s AND %s )%s" % (TOPIC, CONC, NOTCS_TITLE),
    "concentration_missed": "TITLE-ABS-KEY ( %s AND %s AND NOT %s )%s" % (TOPIC, CONC, MEASURE_V2, NOTCS_TITLE),
    "broad":  "TITLE-ABS-KEY ( %s AND %s )" % (TOPIC, EXPOSURE),
    "reviews_title": ('TITLE ( ( misinformation OR disinformation OR "fake news" ) '
                      'AND ( prevalence OR exposure OR consumption ) ) AND DOCTYPE ( re )'),
}


def get_key():
    key = os.environ.get("SCOPUS_KEY")
    if not key:
        sys.exit("ERROR: set the SCOPUS_KEY environment variable (see README.md).")
    return key


def run(query, name, count=25, max_records=0):
    key = get_key()
    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    headers = {"X-ELS-APIKey": key, "Accept": "application/json"}
    start, fetched, entries, total = 0, 0, [], None
    while True:
        url = "%s?query=%s&count=%d&start=%d" % (
            BASE, urllib.parse.quote(query), count, start)
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.load(r)
        sr = d["search-results"]
        if total is None:
            total = int(sr.get("opensearch:totalResults", 0))
        batch = sr.get("entry", [])
        entries.extend(batch)
        fetched += len(batch)
        start += count
        if max_records == 0 or fetched >= min(max_records, total) or not batch:
            break
        time.sleep(1)  # be polite to the API

    os.makedirs(SEARCH_DIR, exist_ok=True)
    stamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out = os.path.join(SEARCH_DIR, "scopus_%s_%s.json" % (name, stamp))
    with open(out, "w") as f:
        json.dump({"run_utc": now, "name": name, "query": query,
                   "total_results": total, "n_saved": len(entries),
                   "entries": entries}, f, indent=2, ensure_ascii=False)
    # append to the auditable query log
    logp = os.path.join(SEARCH_DIR, "scopus_query_log.tsv")
    newfile = not os.path.exists(logp)
    with open(logp, "a") as f:
        if newfile:
            f.write("run_utc\tname\ttotal_results\tn_saved\tquery\n")
        f.write("%s\t%s\t%s\t%d\t%s\n" % (now, name, total, len(entries), query))

    print("[%s] name=%s  TOTAL=%s  saved=%d -> %s"
          % (now, name, total, len(entries), os.path.relpath(out, HERE)))
    for e in entries[:8]:
        print("   -", (e.get("prism:coverDate", "?")[:4]), "|",
              (e.get("dc:title") or "")[:90])
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preset", choices=sorted(QUERIES))
    ap.add_argument("--query")
    ap.add_argument("--name", default="adhoc")
    ap.add_argument("--count", type=int, default=25)
    ap.add_argument("--max", type=int, default=0,
                    help="0 = count only (one page); >0 = paginate up to N records")
    a = ap.parse_args()
    if a.preset:
        run(QUERIES[a.preset], a.name if a.name != "adhoc" else a.preset,
            a.count, a.max)
    elif a.query:
        run(a.query, a.name, a.count, a.max)
    else:
        ap.error("provide --preset or --query")


if __name__ == "__main__":
    main()
