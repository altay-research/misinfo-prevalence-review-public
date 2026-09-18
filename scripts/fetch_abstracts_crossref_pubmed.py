#!/usr/bin/env python3
"""Third abstract source for the stage-2 title-only records (after OpenAlex and Semantic Scholar):
Crossref (works/{doi}, abstract field where the publisher deposited one) then PubMed (esearch by
DOI, efetch abstract). Input: FINAL_rulings.csv rows with abstract_source == none and a DOI.
Output: data/extract_v2/qa/title_rescreen/flagged_abstracts_cr.jsonl (eid, doi, abstract, source).
Resumable. Run: python3 scripts/fetch_abstracts_crossref_pubmed.py"""
import csv, html, json, os, re, time, urllib.parse, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data/extract_v2/qa/title_rescreen/flagged_abstracts_cr.jsonl")
MAILTO = "sachayesilaltay@gmail.com"; UA = {"User-Agent": "misinfo-review/1.0 (mailto:" + MAILTO + ")"}
rows = [r for r in csv.DictReader(open(os.path.join(ROOT, "data/extract_v2/qa/flagged_abstracts/FINAL_rulings.csv"), encoding="utf-8"))
        if r["abstract_source"] == "none" and r["doi"]]
done = {json.loads(l)["eid"] for l in open(OUT, encoding="utf-8")} if os.path.exists(OUT) else set()
def get(url, timeout=40):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read().decode("utf-8", "replace")
def clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()
def crossref(doi):
    try:
        w = json.loads(get("https://api.crossref.org/works/" + urllib.parse.quote(doi) + "?mailto=" + MAILTO))["message"]
        a = clean(w.get("abstract") or "")
        return a if len(a) > 80 else ""
    except Exception:
        return ""
def pubmed(doi):
    try:
        j = json.loads(get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=" + urllib.parse.quote(doi + "[doi]") + "&retmode=json"))
        ids = j.get("esearchresult", {}).get("idlist") or []
        if not ids: return ""
        time.sleep(0.4)
        x = get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=" + ids[0] + "&retmode=xml")
        parts = re.findall(r"<AbstractText[^>]*>(.*?)</AbstractText>", x, flags=re.S)
        a = clean(" ".join(parts))
        return a if len(a) > 80 else ""
    except Exception:
        return ""
found = 0
with open(OUT, "a", encoding="utf-8") as fh:
    for i, r in enumerate(rows, 1):
        if r["item_id"] in done: continue
        a, src = crossref(r["doi"]), "crossref"
        if not a:
            a, src = pubmed(r["doi"]), "pubmed"
        fh.write(json.dumps({"eid": r["item_id"], "doi": r["doi"], "abstract": a, "source": src if a else ""}, ensure_ascii=False) + "\n"); fh.flush()
        found += bool(a); time.sleep(0.4)
        if i % 50 == 0: print(f"  {i}/{len(rows)}, found {found}", flush=True)
print(f"{len(rows)} title-only records with DOI; abstracts found this run: {found}")
