#!/usr/bin/env python3
"""
Stage-2 prep: fetch abstracts for the advancing (INCLUDE+MAYBE) records.

Scopus Abstract Retrieval is not entitled on this key (richer views -> 401, basic ->
empty abstracts), so we use OpenAlex (free, by DOI, high coverage, polite pool with
mailto). Abstracts come as an inverted index which we reconstruct to plain text.

Input : data/screen_title_2026-06-20.csv (advancing = label INCLUDE/MAYBE)
        data/corpus_strict_v2_2026-06-20.jsonl (eid -> doi, title)
Output: data/abstracts/abstracts.jsonl  (one JSON/line: eid, doi, title, abstract, source)
Resumable: skips eids already written.
"""
import csv, json, os, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
OUTDIR = os.path.join(ROOT, "data", "abstracts")
OUT = os.path.join(OUTDIR, "abstracts.jsonl")
MAILTO = "sachayesilaltay@gmail.com"


def reconstruct(inv):
    if not inv:
        return ""
    pos = {}
    for w, ps in inv.items():
        for p in ps:
            pos[p] = w
    return " ".join(pos[i] for i in sorted(pos))


def openalex_by_doi(doi):
    url = ("https://api.openalex.org/works/https://doi.org/"
           + urllib.parse.quote(doi) + "?mailto=" + MAILTO)
    req = urllib.request.Request(url, headers={"User-Agent": "misinfo-review/1.0"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                d = json.load(r)
            return reconstruct(d.get("abstract_inverted_index")), d.get("title")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None, None
            if e.code in (429, 500, 503) and attempt < 3:
                time.sleep(5 * (attempt + 1)); continue
            return None, None
        except Exception:
            if attempt < 3:
                time.sleep(2); continue
            return None, None
    return None, None


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    # advancing eids
    adv = {r["eid"] for r in csv.DictReader(open(os.path.join(ROOT, "data", "screen_title_2026-06-20.csv")))
           if r["label"].strip().upper() in ("INCLUDE", "MAYBE")}
    # eid -> (doi, title)
    meta = {}
    for l in open(os.path.join(ROOT, "data", "corpus_strict_v2_2026-06-20.jsonl")):
        d = json.loads(l)
        if d["eid"] in adv:
            meta[d["eid"]] = (d.get("doi"), d.get("title"))
    done = set()
    if os.path.exists(OUT):
        done = {json.loads(l)["eid"] for l in open(OUT)}
    todo = [e for e in adv if e not in done]
    print("advancing=%d  already=%d  todo=%d" % (len(adv), len(done), len(todo)))

    got = with_abs = no_doi = no_abs = 0
    with open(OUT, "a") as out:
        for eid in todo:
            doi, title = meta.get(eid, (None, None))
            ab, source = "", None
            if doi:
                ab, oa_title = openalex_by_doi(doi)
                if ab:
                    source = "openalex"; with_abs += 1
                elif ab is None:
                    ab = ""; no_abs += 1
                else:
                    no_abs += 1
                time.sleep(0.2)
            else:
                no_doi += 1
            out.write(json.dumps({"eid": eid, "doi": doi, "title": title,
                                  "abstract": ab or "", "source": source},
                                 ensure_ascii=False) + "\n")
            got += 1
            if got % 100 == 0:
                out.flush()
                print("  %d/%d (with_abstract=%d no_doi=%d no_abs=%d)"
                      % (got, len(todo), with_abs, no_doi, no_abs))
    print("DONE: wrote %d (with_abstract=%d, no_doi=%d, no_abstract=%d)"
          % (got, with_abs, no_doi, no_abs))


if __name__ == "__main__":
    main()
