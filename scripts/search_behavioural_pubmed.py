#!/usr/bin/env python3
"""Behavioural-design arm, PubMed side (see search_behavioural_arm.py for why this arm exists).

Same logic as the OpenAlex arm: cross the topic terms with METHOD terms rather than outcome terms,
because trace/panel studies describe themselves by their data, not their subject. PubMed is included
for symmetry with the main search, which ran Scopus (primary), OpenAlex and PubMed; an arm that ran
on fewer sources than the search it supplements would be weaker than the thing it is checking.
Run: python3 scripts/search_behavioural_pubmed.py
"""
import datetime, json, os, time, urllib.parse, urllib.request, xml.etree.ElementTree as ET
EMAIL = "sachayesilaltay@gmail.com"; KEY = os.environ.get("NCBI_API_KEY", "")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOPIC = ('(misinformation[tiab] OR disinformation[tiab] OR "fake news"[tiab] OR "false news"[tiab] '
         'OR "unreliable news"[tiab] OR "junk news"[tiab] OR "low-quality news"[tiab] '
         'OR "news quality"[tiab] OR untrustworthy[tiab])')
METHOD = ('("web tracking"[tiab] OR "browsing data"[tiab] OR "browsing history"[tiab] OR clickstream[tiab] '
          'OR "digital trace"[tiab] OR "trace data"[tiab] OR "donated data"[tiab] OR "data donation"[tiab] '
          'OR "web panel"[tiab] OR "passive metering"[tiab] OR "browser extension"[tiab] '
          'OR "server log"[tiab] OR "media diet"[tiab] OR "URL-level"[tiab] OR "platform data"[tiab])')
TERM = f"({TOPIC} AND {METHOD})"

def call(url, params):
    if KEY: params["api_key"] = KEY
    params.update({"email": EMAIL, "tool": "misinfo-prevalence-review"})
    for _ in range(4):
        try:
            return urllib.request.urlopen(url + "?" + urllib.parse.urlencode(params), timeout=60).read()
        except Exception:
            time.sleep(1.5)
    return b""

ids = []
r = call("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
         {"db": "pubmed", "term": TERM, "retmode": "json", "retmax": "1000"})
if r: ids = json.loads(r).get("esearchresult", {}).get("idlist", [])
recs = []
for i in range(0, len(ids), 200):
    x = call("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
             {"db": "pubmed", "id": ",".join(ids[i:i+200]), "retmode": "xml"})
    if not x: continue
    for art in ET.fromstring(x).iter("PubmedArticle"):
        t = art.find(".//ArticleTitle"); ab = " ".join(e.text or "" for e in art.iter("AbstractText"))
        doi = next((e.text for e in art.iter("ArticleId") if e.get("IdType") == "doi"), "")
        yr = art.find(".//PubDate/Year")
        recs.append({"pmid": (art.find(".//PMID").text if art.find(".//PMID") is not None else ""),
                     "doi": (doi or "").lower(), "title": "".join(t.itertext()) if t is not None else "",
                     "year": yr.text if yr is not None else "", "abstract": ab, "found_by": "pubmed_behavioural"})
    time.sleep(0.2)
date = datetime.date.today().isoformat().replace("-", "")
out = os.path.join(ROOT, f"searches/behavioural_arm_pubmed_{date}.jsonl")
open(out, "w", encoding="utf-8").write("\n".join(json.dumps(r, ensure_ascii=False) for r in recs))
open(os.path.join(ROOT, "searches/query_log.md"), "a", encoding="utf-8").write(
    f"\n## {datetime.date.today()} — behavioural-design arm (PubMed)\nTERM: {TERM}\nHits: {len(recs)} -> {os.path.basename(out)}\n")
print(f"PubMed behavioural arm: {len(recs)} records -> {out}")
