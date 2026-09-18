#!/usr/bin/env python3
"""Reproducible PubMed (E-utilities) primary keyword search — strict_v2-equivalent.
Saves dated dump to searches/. Read NCBI key from env NCBI_API_KEY if present."""
import urllib.request, urllib.parse, json, time, os, sys, re, xml.etree.ElementTree as ET
EMAIL="sachayesilaltay@gmail.com"; KEY=os.environ.get("NCBI_API_KEY","")
TERM=('((misinformation[tiab] OR disinformation[tiab] OR "fake news"[tiab] OR "false news"[tiab] '
 'OR "unreliable news"[tiab] OR "junk news"[tiab] OR "low-quality news"[tiab]) AND '
 '(exposure[tiab] OR consumption[tiab] OR prevalence[tiab] OR circulation[tiab] OR reach[tiab] '
 'OR audience[tiab] OR "news diet"[tiab] OR sharing[tiab] OR shared[tiab] OR spread[tiab] OR diffusion[tiab] '
 'OR dissemination[tiab] OR quantif*[tiab] OR supersharer*[tiab] OR traffic[tiab] OR visits[tiab] '
 'OR engagement[tiab] OR scale[tiab]) NOT (detection[ti] OR classifier[ti] OR classification[ti] '
 'OR "deep learning"[ti] OR "neural network"[ti] OR transformer[ti]))')
def call(url,params):
    if KEY: params["api_key"]=KEY
    params["email"]=EMAIL
    for _ in range(4):
        try: return urllib.request.urlopen(url+"?"+urllib.parse.urlencode(params),timeout=60).read()
        except Exception as e: time.sleep(2)
    return b""
# esearch with history
r=call("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
    {"db":"pubmed","term":TERM,"retmax":0,"usehistory":"y"})
root=ET.fromstring(r); count=int(root.findtext("Count")); webenv=root.findtext("WebEnv"); qk=root.findtext("QueryKey")
print("PubMed count:",count)
out=[]
step=200
for start in range(0,count,step):
    x=call("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
        {"db":"pubmed","WebEnv":webenv,"query_key":qk,"retstart":start,"retmax":step,"retmode":"xml"})
    try: rt=ET.fromstring(x)
    except: time.sleep(1); continue
    for art in rt.findall(".//PubmedArticle"):
        pmid=art.findtext(".//PMID")
        ti=" ".join((art.findtext(".//ArticleTitle") or "").split())
        ab=" ".join((" ".join(e.text or "" for e in art.findall(".//Abstract/AbstractText"))).split())
        yr=art.findtext(".//PubDate/Year") or ""
        doi=""
        for idn in art.findall(".//ArticleId"):
            if idn.get("IdType")=="doi": doi=(idn.text or "").lower()
        out.append({"pmid":pmid,"doi":doi,"title":ti,"abstract":ab,"year":yr})
    time.sleep(0.34 if not KEY else 0.11)
    if start % 1000==0: print("  fetched",start+step,"/",count)
os.makedirs("searches",exist_ok=True)
fn="searches/pubmed_strict_v2_20260624.jsonl"
open(fn,"w").write("\n".join(json.dumps(r,ensure_ascii=False) for r in out))
print("wrote",fn,len(out),"records")
