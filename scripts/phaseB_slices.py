#!/usr/bin/env python3
"""
phaseB_slices.py — Phase B component 2: the MEANINGFUL SLICES.
Study-level prevalence medians stratified by the choices that drive divergent estimates:
construct, denominator class, definitional breadth (the thesis), ground-truth source, sampling frame,
measurement type (behavioural/self-report/content-coding, from the RoB appraisal), platform, topic, country scope.
Plus the enumerated whole-diet backbone and the concentration arm.

Primary statistic = STUDY-LEVEL median (median-per-study, then median across studies) so multi-estimate
studies don't over-weight a cell; estimate-level shown alongside. Read-only on the current freeze (see docs/FROZEN.md).
Writes data/synth/phaseB/slices_*.csv + docs/phaseB_slices.html.
"""
import csv, os, re, html, statistics as st
from pathlib import Path
from collections import defaultdict, Counter
ROOT=Path(__file__).resolve().parents[1]

def frozen_csv():
    m=re.search(r'File:\s*(\S+)',(ROOT/"docs/FROZEN.md").read_text())
    return ROOT/m.group(1)
CSV=frozen_csv()
rows=list(csv.DictReader(open(CSV)))
def g(r,k): return (r.get(k) or "").strip()
# One frozen row reads "single_country" where 788 read "single" (2-s2.0-85145196122, the study
# restored at v1.7.21). It is a spelling variant, not a different scope, and left alone it makes a
# one-study category of its own in every table grouped by this field. Normalised on read; the cell
# itself is a freeze edit and is logged for the next one.
def country_scope(r):
    v = (r.get("country_scope") or "").strip()
    return "single" if v == "single_country" else v
def esc(s): return html.escape(str(s))

# RoB appraisal join (measurement + overall risk)
# (the 22 July rob_appraisals_v145.csv load was removed on 2026-09-18: it covered 317 of 443
#  studies and everything that read it now reads a complete source)
# Risk of bias comes from the v3 master, which covers all 443 studies. It used to come from the
# 22 July appraisal above, which covers 317 and filled only 63.4% of the corpus here (found
# 2026-09-18, alongside the measurement join that had the same cause).
rob_v3={r["study_id"]:(r.get("overall_ruling_corrected") or r.get("overall") or "").strip()
        for r in csv.DictReader(open(ROOT/"data/rob/risk_of_bias_v3_master.csv"))}
MEASUREMENT_BY_CONSTRUCT = {"CONTENT": "CONTENT_CODING", "RECALL": "SELF_REPORT",
    "EXPOSURE": "BEHAVIOURAL", "REACH": "BEHAVIOURAL", "SHARING": "BEHAVIOURAL",
    "CONCENTRATION": "BEHAVIOURAL"}   # see phaseB_prep_regression.py for why this is not a join


# ---- value parse + canonicalisation ----
def pct(r):
    v=g(r,"value_pct")
    try: return float(v.replace("%","")) if v else None
    except ValueError: return None
def canon_gt(r):
    x=g(r,"ground_truth").lower()
    if not x: return "(unspecified)"
    if "newsguard" in x or "domain_list" in x or "low-credibility" in x or "low credibility" in x or "domain" in x: return "domain_list/NewsGuard"
    if "fact" in x and "check" in x: return "fact_checker"
    if "self_report" in x or "self-report" in x or "perceived" in x: return "self_report"
    if "classifier" in x or "gpt" in x or "auto" in x or "hybrid" in x: return "classifier/LLM"
    if "researcher" in x or "hand" in x or "human" in x or "coder" in x or "coded" in x: return "researcher_coding"
    return "researcher_coding"
def measurement(r):
    m=MEASUREMENT_BY_CONSTRUCT.get(g(r,"construct").upper(), "")
    return m or "(unappraised)"

PREV=["EXPOSURE","REACH","RECALL","SHARING","CONTENT","CONCENTRATION"]
AUDIENCE=["EXPOSURE","REACH","RECALL"]   # what a real audience saw/consumed/recalls
BREADTH_ORDER=["fabricated","false","misleading","unreliable_source","low_quality","misinfo_broad"]

for r in rows:
    r["_p"]=pct(r); r["_gt"]=canon_gt(r); r["_meas"]=measurement(r)
    r["_denom"]=g(r,"denom_class") or "?"
    # Main set = the invariants' definition: proportions, no demographic subgroups. The old predicate
    # tested within_misinfo_content, a column the freeze does not have, and never filtered
    # value_kind, so 10 range and per-capita rows sat in these slices and in the abstract's
    # headline numbers while Table 1 and GRADE excluded them (REACH k28/12.2 against k27/12.0).
    r["_main"]= (g(r,"demographic_group")=="" and (g(r,"value_kind") or "proportion")=="proportion"
                 and r["_p"] is not None)

# ---- study-level + estimate-level median helpers ----
def sl(subset):
    """study-level: median-per-study then across studies. returns (n_studies, median, q1, q3, min, max)."""
    by=defaultdict(list)
    for r in subset:
        if r["_p"] is not None: by[g(r,"id")].append(r["_p"])
    meds=sorted(st.median(v) for v in by.values() if v)
    if not meds: return (0,None,None,None,None,None)
    mn,mx=min(meds),max(meds)
    if len(meds)>=4:
        q=st.quantiles(meds,n=4)
        q1,q3=max(q[0],mn),min(q[2],mx)          # clamp: exclusive method can extrapolate past the data at small n
    else:
        q1=q3=None                                # too few studies for a stable IQR
    return (len(meds),round(st.median(meds),1),
            round(q1,1) if q1 is not None else None,round(q3,1) if q3 is not None else None,
            round(mn,1),round(mx,1))
def iqr(q1,q3): return f"{q1}–{q3}" if q1 is not None else "n<4"
def el(subset):
    vals=[r["_p"] for r in subset if r["_p"] is not None]
    return (len(vals), round(st.median(vals),1) if vals else None)

MAIN=[r for r in rows if r["_main"]]

# ================= build slice tables =================
def slice_by(subset, field, order=None, label=None):
    """Return list of dicts: value, n_studies, sl_median, sl_iqr, sl_range, n_est, el_median — sorted."""
    keys=sorted({field(r) for r in subset}, key=lambda k:(order.index(k) if order and k in order else 99, k))
    out=[]
    for k in keys:
        sub=[r for r in subset if field(r)==k]
        ns,med,q1,q3,mn,mx=sl(sub); ne,emed=el(sub)
        if ns==0: continue
        out.append(dict(value=k, n_studies=ns, sl_median=med, sl_iqr=iqr(q1,q3), sl_range=f"{mn}–{mx}",
                        n_est=ne, el_median=emed))
    return out

OUT=ROOT/"data/synth/phaseB"; OUT.mkdir(parents=True,exist_ok=True)
def dump(name,tbl):
    if not tbl: return
    with open(OUT/name,"w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(tbl[0].keys())); w.writeheader(); w.writerows(tbl)

# A. headline by construct (main set)
by_construct=[]
for c in PREV:
    sub=[r for r in MAIN if g(r,"construct")==c]
    ns,med,q1,q3,mn,mx=sl(sub); ne,emed=el(sub)
    if ns: by_construct.append(dict(value=c,n_studies=ns,sl_median=med,sl_iqr=iqr(q1,q3),sl_range=f"{mn}–{mx}",n_est=ne,el_median=emed))
dump("slices_by_construct.csv",by_construct)

# helper: slice a construct-group by a field
def group_slice(constructs, field, order=None):
    sub=[r for r in MAIN if g(r,"construct") in constructs]
    return slice_by(sub, field, order)

# B. THESIS: breadth (within CONTENT, and within AUDIENCE)
breadth_content=group_slice(["CONTENT"], lambda r:g(r,"breadth") or "(blank)", BREADTH_ORDER)
breadth_aud=group_slice(AUDIENCE, lambda r:g(r,"breadth") or "(blank)", BREADTH_ORDER)
dump("slices_breadth_content.csv",breadth_content); dump("slices_breadth_audience.csv",breadth_aud)

# C. denom class (within CONTENT and AUDIENCE)
denom_content=group_slice(["CONTENT"], lambda r:r["_denom"])
denom_aud=group_slice(AUDIENCE, lambda r:r["_denom"])
dump("slices_denom_content.csv",denom_content); dump("slices_denom_audience.csv",denom_aud)

# D. ground-truth source (all prevalence)
gt=slice_by([r for r in MAIN if g(r,"construct") in PREV], lambda r:r["_gt"])
dump("slices_ground_truth.csv",gt)

# E. sampling frame (all prevalence)
samp=slice_by([r for r in MAIN if g(r,"construct") in PREV], lambda r:g(r,"sampling_frame") or "(blank)")
dump("slices_sampling.csv",samp)

# F. measurement (behavioural vs self-report vs content-coding), all six prevalence constructs
# (was audience-only until 2026-09-02, which left content coding at n = 5)
meas=group_slice(PREV, lambda r:r["_meas"])
dump("slices_measurement.csv",meas)

# G. platform (audience)
plat=group_slice(AUDIENCE+["CONTENT"], lambda r:g(r,"platform_norm") or "(blank)")
dump("slices_platform.csv",plat)

# H. topic (all prevalence)
topic=slice_by([r for r in MAIN if g(r,"construct") in PREV], lambda r:g(r,"topic") or "(blank)")
dump("slices_topic.csv",topic)

# I. country scope
cscope=slice_by([r for r in MAIN if g(r,"construct") in PREV], lambda r:country_scope(r) or "(blank)")
dump("slices_country_scope.csv",cscope)

# J. whole-diet backbone (EXPOSURE/REACH, population/all_media/political_news, main set)
WD={"all_media","news_diet","political_news","population"}
whole=[r for r in MAIN if g(r,"construct") in ("EXPOSURE","REACH") and r["_denom"] in WD]
wd_by=defaultdict(list)
for r in whole: wd_by[g(r,"id")].append(r)
wd_tbl=[]
for sid,rs in wd_by.items():
    vals=[x["_p"] for x in rs if x["_p"] is not None]
    wd_tbl.append(dict(id=sid, construct="/".join(sorted({g(x,'construct') for x in rs})),
        denom="/".join(sorted({x["_denom"] for x in rs})), country=g(rs[0],"country_norm") or g(rs[0],"country"),
        platform=g(rs[0],"platform_norm") or g(rs[0],"platform"), topic=g(rs[0],"topic"),
        study_median=round(st.median(vals),2) if vals else None, n_est=len(vals),
        rob=rob_v3.get(sid,"")))
wd_tbl.sort(key=lambda x:(x["study_median"] if x["study_median"] is not None else 0))
dump("slices_whole_diet.csv",wd_tbl)
wd_meds=sorted(x["study_median"] for x in wd_tbl if x["study_median"] is not None)
wd_summary=dict(n_studies=len(wd_meds),
    median=round(st.median(wd_meds),2) if wd_meds else None,
    q1=round(st.quantiles(wd_meds,n=4)[0],2) if len(wd_meds)>=2 else None,
    q3=round(st.quantiles(wd_meds,n=4)[2],2) if len(wd_meds)>=2 else None,
    min=min(wd_meds) if wd_meds else None, max=max(wd_meds) if wd_meds else None)

# K. concentration arm
conc=[r for r in rows if g(r,"construct")=="CONCENTRATION"]
conc_tbl=[dict(id=g(r,"id"), country=g(r,"country_norm") or g(r,"country"), platform=g(r,"platform_norm") or g(r,"platform"),
    group=g(r,"conc_group_label") or g(r,"conc_group_pct"), share=g(r,"conc_share_pct") or (r["_p"] and f'{r["_p"]}%'),
    measure=g(r,"measure_type")[:70], topic=g(r,"topic")) for r in conc]
dump("slices_concentration.csv",conc_tbl)

# ================= HTML =================
def T(headers, tbl, keys, note="", hi=None):
    if not tbl: return f"<p class=sub>(no rows)</p>"
    th="".join(f"<th>{esc(h)}</th>" for h in headers)
    body=""
    for x in tbl:
        cls=' class="hl"' if hi and hi(x) else ""
        body+=f"<tr{cls}>"+"".join(f"<td>{esc(x.get(k,'') if x.get(k,'') is not None else '')}</td>" for k in keys)+"</tr>"
    return (f"<p class=sub>{esc(note)}</p>" if note else "")+f"<table><tr>{th}</tr>{body}</table>"

SL_H=["value","#studies","study median %","study IQR","study range","#est","est median %"]
SL_K=["value","n_studies","sl_median","sl_iqr","sl_range","n_est","el_median"]

wd_rows_html=T(["study","construct","denom","country","platform","topic","study median %","#est","RoB"],
    wd_tbl,["id","construct","denom","country","platform","topic","study_median","n_est","rob"],
    hi=lambda x:(x["study_median"] or 0)>=25)

HTML=f"""<meta charset=utf-8><title>Phase B — meaningful slices</title>
<style>
 body{{font:14px/1.55 -apple-system,Segoe UI,Roboto,sans-serif;max-width:1120px;margin:22px auto;padding:0 16px;color:#181818}}
 h1{{font-size:23px}} h2{{margin-top:30px;border-bottom:2px solid #222;padding-bottom:4px}} h3{{margin:20px 0 4px;font-size:15px}}
 .sub{{color:#666;margin:2px 0 8px}}
 table{{border-collapse:collapse;width:100%;font-size:12.5px;margin:6px 0 14px}} th,td{{border:1px solid #e3e3e3;padding:4px 8px;text-align:left}}
 th{{background:#f4f4f4}} td:first-child{{white-space:nowrap}}
 td:nth-child(3){{font-weight:700;color:#036}}
 .hl td{{background:#fff3ee}} .sid{{font-family:ui-monospace,monospace}}
 .box{{border:1px solid #cbd8e6;background:#eef4fb;border-radius:6px;padding:10px 14px;margin:10px 0}}
 .big{{font-size:26px;font-weight:800;color:#0a4}} .two{{display:flex;gap:22px;flex-wrap:wrap}} .two>div{{flex:1;min-width:330px}}
.starthere{{background:#eef4fb;border:1px solid #cbd8e6;border-radius:6px;padding:10px 14px;margin:0 0 16px;font-size:14px}}
</style>
<h1>Phase B · Component 2 — the meaningful slices</h1>
<div class="starthere"><b>Start here:</b> this is a component view. The narrative dashboard is <a href="phaseB_dashboard.html">phaseB_dashboard.html</a>; the interactive explorer is <a href="companion_dashboard.html">companion_dashboard.html</a>.</div>
<p class=sub>Source <span class=sid>{esc(CSV.name)}</span>. <b>Main-analysis set</b> = general-public rows (no demographic
subgroup), a real proportion, not within-misinfo composition → {len(MAIN)} estimate rows. Primary statistic =
<b>study-level median</b> (median-per-study, then across studies); estimate-level shown alongside. Prevalence excludes QUALITY/OTHER.</p>

<div class=box>
<b>Read this first — the estimand matters more than any single number.</b> "Prevalence of misinformation" is not one quantity.
<b>Audience exposure</b> (EXPOSURE = share of a real information diet; REACH = % of people who saw ≥1; RECALL = % who report seeing it)
answers "how much misinfo do people actually encounter?" — the review's core question. <b>CONTENT</b> (% of items in a sample that are
misinfo) answers a different question and is usually measured on topic-curated samples, so it runs much higher. Slice within these, never pool across them.
</div>

<h2>A · Headline prevalence by construct</h2>
{T(SL_H,by_construct,SL_K,"Study-level medians on the main set. EXPOSURE is the diet-share estimand; CONTENT is content-level and topical.")}

<h2>B · The thesis — definitional breadth drives the estimate</h2>
<p class=sub>Breadth runs fabricated → false → misleading → unreliable_source → low_quality (strict → loose). If looser definitions yield higher prevalence, the number is an artefact of the definition.</p>
<div class=two>
 <div><h3>within CONTENT</h3>{T(SL_H,breadth_content,SL_K)}</div>
 <div><h3>within AUDIENCE exposure (EXPOSURE/REACH/RECALL)</h3>{T(SL_H,breadth_aud,SL_K)}</div>
</div>

<h2>C · Denominator class — "% of WHAT?"</h2>
<div class=two>
 <div><h3>within CONTENT</h3>{T(SL_H,denom_content,SL_K,"topical/curated/single_source inflate; all_media/population are clean.")}</div>
 <div><h3>within AUDIENCE</h3>{T(SL_H,denom_aud,SL_K)}</div>
</div>

<h2>D · Ground-truth source</h2>
{T(SL_H,gt,SL_K,"How 'misinfo' was determined. Domain-list/NewsGuard = source-level; fact-checker/researcher = claim-level.")}

<h2>E · Sampling frame</h2>
{T(SL_H,samp,SL_K,"panel_trace / full_census = behavioural whole-diet; keyword_topical = topic-seeded (inflates); survey_sample = self-report.")}

<h2>F · Measurement type <span style="font-weight:400;color:#888">(from the RoB appraisal)</span></h2>
{T(SL_H,meas,SL_K,"Behavioural trace vs self-report vs content-coding, over AUDIENCE + SHARING constructs.")}

<h2>G · Platform</h2>
{T(SL_H,plat,SL_K,"Over AUDIENCE + CONTENT constructs.")}

<h2>H · Topic</h2>
{T(SL_H,topic,SL_K,"The new moderator. Note the corpus is health/COVID-heavy.")}

<h2>I · Country scope</h2>
{T(SL_H,cscope,SL_K)}

<h2>J · Whole-diet backbone — the paper's core <span style="font-weight:400;color:#888">({wd_summary['n_studies']} studies)</span></h2>
<div class=box>
 The clean audience-diet designs (EXPOSURE/REACH over a population / all-media / political-news denominator).
 <span class=big>{wd_summary['median']}%</span> &nbsp;study-level median &nbsp;·&nbsp; IQR {wd_summary['q1']}–{wd_summary['q3']}% &nbsp;·&nbsp; range {wd_summary['min']}–{wd_summary['max']}%.
 <br>This is the honest answer to "what share of a real information diet is misinformation?" — low single digits, with a small high-denominator/topical tail (highlighted).
</div>
{wd_rows_html}

<h2>K · Concentration arm <span style="font-weight:400;color:#888">({len(conc_tbl)} estimates)</span></h2>
{T(["study","country","platform","group","share","measure","topic"],conc_tbl,
   ["id","country","platform","group","share","measure","topic"],"Who accounts for the exposure/sharing — the concentration story (top X% → Y%).")}
"""
(ROOT/"docs/phaseB_slices.html").write_text(HTML)
print(f"read {CSV.name}: main-set {len(MAIN)} rows")
print(f"by construct (study-level median):", {x['value']:x['sl_median'] for x in by_construct})
print(f"whole-diet backbone: {wd_summary['n_studies']} studies, median {wd_summary['median']}% (IQR {wd_summary['q1']}-{wd_summary['q3']})")
print(f"breadth within CONTENT:", {x['value']:x['sl_median'] for x in breadth_content})
print("wrote docs/phaseB_slices.html + data/synth/phaseB/slices_*.csv")
