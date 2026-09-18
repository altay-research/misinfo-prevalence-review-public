#!/usr/bin/env python3
"""RECALL split: self-report EXPOSURE ('seen') vs self-report SHARING ('shared'), reported
separately (v1.6.6+ recall_subtype). Study-level medians + study-cluster bootstrap 95% CI (2000
resamples, fixed seed), matching the paper's primary statistic. Also the RECALL(seen)/EXPOSURE
ratio. Output: data/synth/phaseB/recall_split.csv.
Run: python3 scripts/phaseB_recall_split.py
"""
import csv, os, re, random, statistics as st
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fp=re.search(r"File:\s*(\S+)",open(os.path.join(ROOT,"docs/FROZEN.md")).read()).group(1)
rows=[r for r in csv.DictReader(open(os.path.join(ROOT,fp),encoding="utf-8"))
      if r['value_kind']=='proportion' and not r['demographic_group'].strip()
      and r['value_pct'].strip()]
def studymed(subset):
    bys={}
    for r in subset: bys.setdefault(r['id'],[]).append(float(r['value_pct']))
    per=[st.median(v) for v in bys.values()]
    return per, len(bys)
def boot(subset, seed):
    bys={}
    for r in subset: bys.setdefault(r['id'],[]).append(float(r['value_pct']))
    keys=list(bys); rng=random.Random(seed); meds=[]
    for _ in range(2000):
        samp=[st.median(bys[rng.choice(keys)]) for _ in keys]
        meds.append(st.median(samp))
    meds.sort(); return meds[50], meds[-51]
out=[]
groups={
 'RECALL_exposure':[r for r in rows if r['construct']=='RECALL' and r['recall_subtype']=='exposure'],
 'RECALL_sharing':[r for r in rows if r['construct']=='RECALL' and r['recall_subtype']=='sharing'],
 'RECALL_combined':[r for r in rows if r['construct']=='RECALL'],
 'EXPOSURE':[r for r in rows if r['construct']=='EXPOSURE'],
}
for g,sub in groups.items():
    per,k=studymed(sub)
    if not per: continue
    lo,hi=boot(sub, 42)
    m=st.median(per)
    iqr=(st.quantiles(per,n=4)[0], st.quantiles(per,n=4)[2]) if len(per)>=4 else (min(per),max(per))
    out.append({'group':g,'k_studies':k,'median':round(m,1),'ci_lo':round(lo,1),'ci_hi':round(hi,1),
                'iqr_lo':round(iqr[0],1),'iqr_hi':round(iqr[1],1)})
    print(f"{g:18} k={k:3d} median={m:.1f}% CI[{lo:.1f},{hi:.1f}] IQR[{iqr[0]:.1f},{iqr[1]:.1f}]")
# ratio RECALL_exposure / EXPOSURE
re_exp=st.median(studymed(groups['RECALL_exposure'])[0]); exp=st.median(studymed(groups['EXPOSURE'])[0])
print(f"\nRECALL(seen)/EXPOSURE ratio = {re_exp/exp:.1f}")
with open(os.path.join(ROOT,"data/synth/phaseB/recall_split.csv"),"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
print("wrote data/synth/phaseB/recall_split.csv")
