#!/usr/bin/env python3
"""phaseB_grade.py — GRADE certainty (prevalence adaptation) per construct, applied deterministically to
the live freeze (docs/FROZEN.md pointer) + RoB appraisals + precision-weighting output. Starts at HIGH; downgrades on 5 domains by
explicit rules (docs/grade_certainty_framework.md). Writes a Summary-of-Findings table (CSV + HTML fragment).
No hand-assignment in prose — the table regenerates from data."""
import csv, re, statistics as st
from pathlib import Path
from collections import defaultdict, Counter
ROOT=Path(__file__).resolve().parents[1]
CSV=ROOT/re.search(r'File:\s*(\S+)',(ROOT/"docs/FROZEN.md").read_text()).group(1)
rows=list(csv.DictReader(open(CSV)))
def g(r,k): return (r.get(k) or "").strip()
# RoB v3 master (Hoy-adapted, full-text, 317/317 studies). Use the RULING-CORRECTED column:
# shards 00-19 were appraised before the source-level-list ruling, so `overall` mixes two
# instruments; `overall_ruling_corrected` applies the ruling uniformly.
rob={r["study_id"]:g(r,"overall_ruling_corrected") for r in csv.DictReader(open(ROOT/"data/rob/risk_of_bias_v3_master.csv"))}
prec={r["group"]:r for r in csv.DictReader(open(ROOT/"data/synth/phaseB/precision_weighting.csv"))}
# Bootstrap 95% CIs on the study-level medians (scripts/phaseB_uncertainty.py). Used for the
# imprecision domain: a CI spanning a decision-relevant range is direct evidence of imprecision,
# whereas a bare study count (k<10) is an arbitrary proxy for it.
try:
    unc={r["group"]:r for r in csv.DictReader(open(ROOT/"data/synth/phaseB/uncertainty_medians.csv"))}
except FileNotFoundError:
    unc={}
def pct(r):
    v=g(r,"value_pct")
    try: return float(v) if v else None
    except: return None
for r in rows:
    r["_p"]=pct(r); r["_denom"]=g(r,"denom_class")
    # value_kind was missing from this predicate, so 10 non-proportion rows (6 per-capita intensity
    # counts, 4 ranges) entered the GRADE medians and inflated REACH and SHARING k against every
    # other table in the pipeline. Same main-set definition as phaseB_descriptives and the invariants.
    r["_main"]=(g(r,"demographic_group")=="" and g(r,"within_misinfo_content")!="TRUE"
                and (g(r,"value_kind") or "proportion")=="proportion" and r["_p"] is not None)

CONSTRUCTS=["EXPOSURE","REACH","RECALL","SHARING","CONTENT","CONCENTRATION"]
# indirectness: does the construct DIRECTLY measure audience-level exposure/consumption of misinformation?
INDIRECT={"EXPOSURE":0,"REACH":0,           # direct behavioural audience exposure
          "RECALL":1,                        # self-reported perception, not measured exposure
          "SHARING":1,                       # sharing as an exposure/consumption proxy
          "CONTENT":1,                       # share of items, not audience exposure (denominator is content)
          "CONCENTRATION":1}                 # distributional property, indirect for "how much exposure"
LADDER=["HIGH","MODERATE","LOW","VERY_LOW"]
def downgrade(level_idx,n): return min(len(LADDER)-1, level_idx+n)

sof=[]
for c in CONSTRUCTS:
    main=[r for r in rows if r["_main"] and g(r,"construct")==c] if c!="CONCENTRATION" \
         else [r for r in rows if g(r,"construct")=="CONCENTRATION" and r["_p"] is not None]
    by=defaultdict(list)
    for r in main: by[g(r,"id")].append(r["_p"])
    meds=sorted(st.median(v) for v in by.values() if v)
    if not meds: continue
    k=len(meds); med=st.median(meds)
    q1=st.quantiles(meds,n=4)[0] if k>=4 else min(meds)
    q3=st.quantiles(meds,n=4)[2] if k>=4 else max(meds)
    # RoB distribution over contributing studies
    robs=[rob.get(sid,"") for sid in by]; nrob=[x for x in robs if x]
    pHIGH=100*sum(x=="HIGH" for x in nrob)/len(nrob) if nrob else 0
    # topical/curated denominator share
    dl=[g(r,"_denom") for r in main]
    pTOPICAL=100*sum(d in ("topical","curated_sample","single_source","curated") for d in dl)/len(dl) if dl else 0
    # precision fragility from the weighting shift
    pw=prec.get(c,{}); shift=abs(float(pw["shift"])) if pw.get("shift") else 0
    unw=float(pw["unweighted_median"]) if pw.get("unweighted_median") else 0

    reasons=[]; dn=0; idx=0
    # 1 Risk of bias
    if pHIGH>=85: dn+=2; reasons.append(f"RoB −2 ({pHIGH:.0f}% HIGH-RoB studies)")
    elif pHIGH>50: dn+=1; reasons.append(f"RoB −1 ({pHIGH:.0f}% HIGH-RoB)")
    # 2 Inconsistency — wide spread (order of magnitude) NOT explained by the denom moderator
    ratio=(q3/q1) if q1>0 else 99
    # THRESHOLDS (pre-specified, documented in docs/grade_certainty_framework.md):
    #   ratio>=10  = the IQR spans an order of magnitude
    #   MIXED_DENOM 15-85% = a genuine within-construct mix of denominator types
    # The framework's rule is "do not penalise as inconsistency what a moderator already
    # explains". Previously BOTH branches below downgraded by 1, so the pTOPICAL condition was
    # inert and the rule was stated but never implemented. Now a wide spread that coexists with
    # a real denominator mix is recorded as EXPLAINED and does NOT downgrade; only unexplained
    # spread does.
    MIXED_DENOM = 15 <= pTOPICAL <= 85
    if ratio>=10 and MIXED_DENOM:
        reasons.append(f"Inconsistency not downgraded (IQR spans ~{ratio:.0f}× but {pTOPICAL:.0f}% "
                       f"topical/curated — the denominator moderator explains the spread)")
    elif ratio>=10:
        dn+=1; reasons.append(f"Inconsistency −1 (IQR spans ~{ratio:.0f}×, unexplained: "
                              f"denominator type is homogeneous at {pTOPICAL:.0f}% topical)")
    # 3 Indirectness
    if INDIRECT[c]:
        # heavier for topical CONTENT / perception RECALL
        idr=1; reasons.append({"RECALL":"Indirectness −1 (self-reported perception, not measured exposure)",
                               "SHARING":"Indirectness −1 (sharing proxies exposure)",
                               "CONTENT":"Indirectness −1 (content-share, not audience exposure)",
                               "CONCENTRATION":"Indirectness −1 (distributional, not an exposure magnitude)"}[c])
        dn+=idr
    # 4 Imprecision — few studies or precision-fragile under weighting
    # THRESHOLDS: k<10 studies; OR a bootstrap 95% CI whose upper bound is >=5x its lower bound
    # (i.e. the interval spans a decision-relevant range -- 2% and 10% imply different policy);
    # OR a weighted median that differs from the unweighted one by at least half (precision-fragile).
    # The weighting criterion was ABSOLUTE (>=10pp) until 2026-09-15, which made it a function of
    # the construct's scale rather than of its fragility: EXPOSURE's median falls 2.0 -> 0.6 under
    # weighting, a 70% collapse, but only 1.4pp, so it escaped a downgrade that REACH took for the
    # same behaviour at a larger base (12.0 -> 0.3). A pre-submission audit caught the supplement
    # justifying EXPOSURE's HIGH on the ground that its "median is stable under sample-size
    # weighting", which the weighting table refutes. Relative is scale-free and is what the
    # sentence was always claiming.
    # The CI criterion was added because k<10 alone is an arbitrary proxy: EXPOSURE has k=15 and
    # so escaped every imprecision downgrade while its CI runs 0.6-5.1% (an 8.5x span), which is
    # not a precise estimate by any reading. Certainty of HIGH on that basis was the single most
    # attackable rating in the review.
    u=unc.get(c,{}); ci_lo=float(u.get("boot95_lo") or 0); ci_hi=float(u.get("boot95_hi") or 0)
    ci_ratio=(ci_hi/ci_lo) if ci_lo>0 else 0
    if k<10:
        dn+=1; reasons.append(f"Imprecision −1 (only k={k} studies)")
    elif ci_ratio>=5:
        dn+=1; reasons.append(f"Imprecision −1 (95% CI {ci_lo:.1f}–{ci_hi:.1f}% spans {ci_ratio:.1f}×)")
    elif unw and abs(shift) / unw >= 0.5:
        dn += 1
        reasons.append(f"Imprecision −1 (weighted median {unw:.1f} → {float(pw['weighted_median']):.1f}%, "
                       f"a {abs(shift) / unw * 100:.0f}% shift — precision-fragile)")
    # 5 Publication/selection bias — dominated by curated/topical (already-contentious) corpora
    if pTOPICAL>=70: dn+=1; reasons.append(f"Selection bias −1 ({pTOPICAL:.0f}% topical/curated corpora)")

    cert=LADDER[downgrade(0,dn)]
    sof.append(dict(construct=c,k=k,median=round(med,1),iqr=f"{round(q1,1)}–{round(q3,1)}",
        pct_high_rob=round(pHIGH),pct_topical=round(pTOPICAL),weight_shift=round(shift,1),
        downgrades=dn,certainty=cert,reasons="; ".join(reasons) or "no serious concerns"))

out=ROOT/"data/synth/phaseB/grade_sof.csv"
with open(out,"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(sof[0].keys())); w.writeheader(); w.writerows(sof)
print(f"{'construct':14}{'k':>4}{'median':>9}{'IQR':>14}{'%HIGH':>7}{'%topcl':>8}  certainty")
for s in sof:
    print(f"{s['construct']:14}{s['k']:>4}{s['median']:>8}%{s['iqr']:>14}{s['pct_high_rob']:>6}%{s['pct_topical']:>7}%  {s['certainty']}")
print(f"\nwrote {out}")
for s in sof: print(f"  {s['construct']}: {s['reasons']}")
