#!/usr/bin/env python3
"""Reproducible OpenAlex PRIMARY keyword search: topic-in-title AND measure-in-title/abstract.
(OpenAlex OR explodes, so we run topic x measure combos and union.)"""
import urllib.request, urllib.parse, json, time, os
EMAIL="sachayesilaltay@gmail.com"
TOPICS=["misinformation","disinformation","fake news","false news","unreliable news","junk news","low-quality news"]
MEAS=["prevalence","exposure","consumption","circulation","sharing","diffusion","dissemination","audience","reach","news diet","engagement","spread"]
def get(url):
    for _ in range(4):
        try: return json.loads(urllib.request.urlopen(url,timeout=60).read())
        except Exception: time.sleep(1.5)
    return {}
def inv2ab(inv):
    if not inv: return ""
    w={}
    for wd,ps in inv.items():
        for p in ps: w[p]=wd
    return " ".join(w[i] for i in sorted(w))
seen={}; combo_counts={}
for t in TOPICS:
    for m in MEAS:
        flt="title.search:%s,abstract.search:%s,from_publication_date:2010-01-01,type:article"%(t,m)
        cur="*"; got=0
        while cur:
            url="https://api.openalex.org/works?filter=%s&per-page=200&cursor=%s&mailto=%s"%(urllib.parse.quote(flt,safe=':,'),cur,EMAIL)
            d=get(url)
            for w in d.get("results",[]):
                e=w["id"].split("/")[-1]
                if e in seen: continue
                seen[e]={"oaid":e,"doi":(w.get("doi") or "").replace("https://doi.org/","").lower(),
                    "title":w.get("display_name","") or "","year":w.get("publication_year",""),
                    "abstract":inv2ab(w.get("abstract_inverted_index"))}
                got+=1
            cur=(d.get("meta") or {}).get("next_cursor")
            if not d.get("results"): break
            time.sleep(0.12)
        combo_counts["%s|%s"%(t,m)]=got
os.makedirs("searches",exist_ok=True)
open("searches/openalex_keyword_20260624.jsonl","w").write("\n".join(json.dumps(v,ensure_ascii=False) for v in seen.values()))
print("OpenAlex keyword union (unique works):",len(seen))
