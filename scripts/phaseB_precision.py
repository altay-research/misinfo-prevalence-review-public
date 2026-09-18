#!/usr/bin/env python3
"""phaseB_precision.py — precision-weighting sensitivity: does weighting estimates by sample size
change the prevalence picture? For each construct (and the whole-diet backbone), compare the
UNWEIGHTED study-level median with the SAMPLE-SIZE-WEIGHTED median, each with a study-cluster
bootstrap 95% CI. Thesis: larger samples find less misinformation, so weighting pulls the estimate down.
Deterministic (fixed seed). Reads data/synth/phaseB/regression_data.csv (has p, n, construct per estimate)."""
import csv, random, statistics as st
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1]
random.seed(20260722)
rows=list(csv.DictReader(open(ROOT/"data/synth/phaseB/regression_data.csv")))
for r in rows: r["value_pct"]=float(r["value_pct"]); r["n"]=int(r["n"])

def study_points(subset):
    """collapse to one (value, n) per study: median value, max n (the study's headline sample)."""
    by=defaultdict(list)
    for r in subset: by[r["study_id"]].append(r)
    pts=[]
    for sid,rs in by.items():
        pts.append((st.median([r["value_pct"] for r in rs]), max(r["n"] for r in rs), sid))
    return pts
def wmedian(pairs):
    """weighted median of (value,weight)."""
    s=sorted(pairs); tot=sum(w for _,w in s); cum=0
    for v,w in s:
        cum+=w
        if cum>=tot/2: return v
    return s[-1][0]
def boot_ci(pts, weighted, B=2000):
    # resampling frame must be insertion-ordered: building it from a set made iteration order
    # depend on PYTHONHASHSEED, so the published CIs were not reproducible despite the fixed seed
    # (caught at the 2026-08-11 code review — the one script of six with this defect)
    by=defaultdict(list)
    for p in pts: by[p[2]].append(p)
    sids=list(by)
    ests=[]
    for _ in range(B):
        samp=[]
        for _ in range(len(sids)): samp+=by[random.choice(sids)]
        if weighted: ests.append(wmedian([(v,n) for v,n,_ in samp]))
        else: ests.append(st.median([v for v,_,_ in samp]))
    ests.sort()
    return round(ests[int(.025*B)],1), round(ests[int(.975*B)],1)

def block(name, subset):
    pts=study_points(subset)
    if len(pts)<3: return None
    uw=st.median([v for v,_,_ in pts]); w=wmedian([(v,n) for v,n,_ in pts])
    uwlo,uwhi=boot_ci(pts,False); wlo,whi=boot_ci(pts,True)
    return dict(group=name, n_studies=len(pts),
        unweighted_median=round(uw,1), unweighted_CI=f"{uwlo}–{uwhi}",
        weighted_median=round(w,1), weighted_CI=f"{wlo}–{whi}",
        shift=round(w-uw,1))

CON=["EXPOSURE","REACH","RECALL","SHARING","CONTENT"]
res=[]
for c in CON:
    b=block(c,[r for r in rows if r["construct"]==c])
    if b: res.append(b)
# whole-diet backbone (need denom info -> recompute from frozen; approximate via construct EXPOSURE/REACH + representative)
# use regression_data has no denom col directly usable; reload denom from frozen for whole-diet subset
import re
CSV=ROOT/re.search(r'File:\s*(\S+)',(ROOT/"docs/FROZEN.md").read_text()).group(1)
fr={ (str(i)):row for i,row in enumerate(csv.DictReader(open(CSV))) }
def g(r,k): return (r.get(k) or "").strip()
WD={"all_media","news_diet","population","political_news"}
wd=[r for r in rows if fr.get(r["estimate_id"]) and g(fr[r["estimate_id"]],"denom_class") in WD
    and r["construct"] in ("EXPOSURE","REACH")]
b=block("WHOLE-DIET backbone",wd)
if b: res.append(b)

out=ROOT/"data/synth/phaseB/precision_weighting.csv"
with open(out,"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(res[0].keys())); w.writeheader(); w.writerows(res)
print(f"{'group':22} {'n':>3}  {'unweighted (95% CI)':>22}   {'weighted (95% CI)':>22}   shift")
for x in res:
    print(f"{x['group']:22} {x['n_studies']:>3}  {x['unweighted_median']:>6}% ({x['unweighted_CI']:>11})   "
          f"{x['weighted_median']:>6}% ({x['weighted_CI']:>11})   {x['shift']:+.1f}")
print(f"\nwrote {out}")
