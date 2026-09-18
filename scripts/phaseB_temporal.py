#!/usr/bin/env python3
"""Temporal trend: does measured misinformation prevalence change over data-collection year/era?
Reads the frozen `era`/`year` (v1.6.6+). Study-level medians per era, per construct + a Spearman of
study prevalence vs data year within each construct. Novel: probes whether 'prevalence' tracks the
moral-panic timeline. Output: data/synth/phaseB/temporal.csv + console.
Run: python3 scripts/phaseB_temporal.py
"""
import csv, os, re, statistics as st
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fp=re.search(r"File:\s*(\S+)",open(os.path.join(ROOT,"docs/FROZEN.md")).read()).group(1)
rows=[r for r in csv.DictReader(open(os.path.join(ROOT,fp),encoding="utf-8"))
      if r['value_kind']=='proportion' and not r['demographic_group'].strip()
      and r['population_scope']=='general_public' and r['value_pct'].strip()
      and r['construct'] in ('CONTENT','EXPOSURE','REACH','RECALL','SHARING') and r['year'].strip()]
ERAS=["<=2016","2017-2019","2020-2021",">=2022"]
def spearman(xs,ys):
    n=len(xs)
    if n<5: return None,None,n
    def rank(v):
        s=sorted(range(len(v)),key=lambda i:v[i]); r=[0]*len(v)
        i=0
        while i<len(v):
            j=i
            while j+1<len(v) and v[s[j+1]]==v[s[i]]: j+=1
            for k in range(i,j+1): r[s[k]]=(i+j)/2+1
            i=j+1
        return r
    rx,ry=rank(xs),rank(ys); mx=sum(rx)/n; my=sum(ry)/n
    num=sum((a-mx)*(b-my) for a,b in zip(rx,ry))
    den=(sum((a-mx)**2 for a in rx)*sum((b-my)**2 for b in ry))**.5
    if den==0: return None,None,n
    rho=num/den; t=rho*((n-2)/(1-rho**2))**.5 if abs(rho)<1 else float('inf')
    # two-tailed p via a normal approx (stdlib only)
    import math; p=2*(1-0.5*(1+math.erf(abs(t)/((2*(n-2))**.5))))  # rough
    return rho,p,n
out=[]
print("=== Study-level median prevalence by ERA (per construct) ===")
for c in ('CONTENT','EXPOSURE','REACH','RECALL','SHARING'):
    print(f"\n{c}:")
    for e in ERAS:
        sub=[r for r in rows if r['construct']==c and r['era']==e]
        # study-level: median per study then across studies
        bys={}
        for r in sub: bys.setdefault(r['id'],[]).append(float(r['value_pct']))
        if not bys: print(f"  {e:11} —"); continue
        sm=st.median([st.median(v) for v in bys.values()])
        print(f"  {e:11} k={len(bys):3d}  median={sm:.1f}%")
        out.append({'construct':c,'era':e,'k_studies':len(bys),'median_pct':round(sm,1)})
    # spearman: study prevalence vs year
    bysy={}
    for r in rows:
        if r['construct']==c: bysy.setdefault(r['id'],[]).append((int(r['year']),float(r['value_pct'])))
    yrs=[st.median([y for y,_ in v]) for v in bysy.values()]
    vals=[st.median([x for _,x in v]) for v in bysy.values()]
    rho,p,n=spearman(yrs,vals)
    if rho is not None: print(f"  Spearman(year, prevalence): rho={rho:+.2f} p~{p:.3f} (k={n} studies)")
with open(os.path.join(ROOT,"data/synth/phaseB/temporal.csv"),"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=['construct','era','k_studies','median_pct']); w.writeheader(); w.writerows(out)
print("\nwrote data/synth/phaseB/temporal.csv")
