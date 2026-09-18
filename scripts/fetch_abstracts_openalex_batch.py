#!/usr/bin/env python3
"""
Stage-2 prep (BATCHED): fetch abstracts from OpenAlex using the DOI filter, up to 50
works per request (filter=doi:d1|d2|...). ~55 calls for the whole advancing set instead
of one call per record -> avoids per-record rate limiting. Resumable: skips eids already
in data/abstracts/abstracts.jsonl. Records with no DOI are written with source=null.
"""
import csv, json, os, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
OUT = os.path.join(ROOT, "data", "abstracts", "abstracts.jsonl")
MAILTO = "sachayesilaltay@gmail.com"
BATCH = 50


def reconstruct(inv):
    if not inv:
        return ""
    pos = {}
    for w, ps in inv.items():
        for p in ps:
            pos[p] = w
    return " ".join(pos[i] for i in sorted(pos))


def norm(doi):
    return (doi or "").lower().replace("https://doi.org/", "").strip()


def fetch_batch(dois):
    filt = "doi:" + "|".join("https://doi.org/" + d for d in dois)
    url = ("https://api.openalex.org/works?per-page=%d&mailto=%s&select=doi,abstract_inverted_index,title&filter=%s"
           % (BATCH, MAILTO, urllib.parse.quote(filt)))
    req = urllib.request.Request(url, headers={"User-Agent": "misinfo-review/1.0"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r).get("results", [])
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 503) and attempt < 4:
                time.sleep(4 * (attempt + 1)); continue
            print("  HTTP", e.code, e.read().decode()[:150]); return []
        except Exception as e:
            if attempt < 4:
                time.sleep(3); continue
            print("  ERR", e); return []
    return []


def main():
    adv = {r["eid"] for r in csv.DictReader(open(os.path.join(ROOT, "data", "screen_title_2026-06-20.csv")))
           if r["label"].strip().upper() in ("INCLUDE", "MAYBE")}
    meta = {}
    for l in open(os.path.join(ROOT, "data", "corpus_strict_v2_2026-06-20.jsonl")):
        d = json.loads(l)
        if d["eid"] in adv:
            meta[d["eid"]] = (d.get("doi"), d.get("title"))
    done = set()
    if os.path.exists(OUT):
        done = {json.loads(l)["eid"] for l in open(OUT)}

    todo = [e for e in adv if e not in done]
    with_doi = [(e, meta[e][0]) for e in todo if meta.get(e, (None,))[0]]
    no_doi = [e for e in todo if not meta.get(e, (None,))[0]]
    print("advancing=%d done=%d todo=%d (with_doi=%d no_doi=%d)"
          % (len(adv), len(done), len(todo), len(with_doi), len(no_doi)))

    # doi(normalized) -> eid  (a doi could map to >1 eid in theory; keep first)
    doi2eid = {}
    for e, doi in with_doi:
        doi2eid.setdefault(norm(doi), e)

    got = wa = 0
    with open(OUT, "a") as out:
        # no-doi records: write immediately (title-only at Stage-2)
        for e in no_doi:
            out.write(json.dumps({"eid": e, "doi": None, "title": meta[e][1],
                                  "abstract": "", "source": None}, ensure_ascii=False) + "\n")
            got += 1
        out.flush()
        # batched DOI fetch
        dois = [norm(doi) for _, doi in with_doi]
        for i in range(0, len(dois), BATCH):
            chunk = dois[i:i + BATCH]
            results = fetch_batch(chunk)
            found = {}
            for w in results:
                dn = norm(w.get("doi"))
                if dn in doi2eid:
                    found[dn] = reconstruct(w.get("abstract_inverted_index"))
            for dn in chunk:
                e = doi2eid[dn]
                ab = found.get(dn, "")
                if ab:
                    wa += 1
                out.write(json.dumps({"eid": e, "doi": dn, "title": meta[e][1],
                                      "abstract": ab, "source": "openalex" if ab else None},
                                     ensure_ascii=False) + "\n")
                got += 1
            out.flush()
            print("  batch %d-%d: +%d (with_abstract running=%d)" % (i, i + len(chunk), len(chunk), wa))
            time.sleep(0.3)
    print("DONE: wrote %d new (%d with abstract this run)" % (got, wa))


if __name__ == "__main__":
    main()
