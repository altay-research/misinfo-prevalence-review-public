#!/usr/bin/env python3
"""
phaseB_figures.py — Phase B figures + concentration deep-dive. Dependency-free vector SVG
(deterministic, prints crisp, embeds in HTML). Reads frozen v1.4.6 (spec from FROZEN.md).
Figures:
  fig1_prevalence_by_construct.svg  — study-level median + range per construct
  fig2_method_drivers.svg           — the core result: behavioural vs content vs self-report, + sampling, + ground-truth
  fig3_whole_diet_backbone.svg      — 31 whole-diet studies, each at its median, sorted, RoB-coloured, pooled line
  fig4_concentration_curve.svg      — top X% of people -> Y% of misinfo activity (exposure vs sharing)
Plus data/synth/phaseB/concentration_standardized.csv and docs/phaseB_figures.html.
"""
import csv, os, re, html, math, statistics as st
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1]
CSV=ROOT/re.search(r'File:\s*(\S+)',(ROOT/"docs/FROZEN.md").read_text()).group(1)
rows=list(csv.DictReader(open(CSV)))
def g(r,k): return (r.get(k) or "").strip()
def esc(s): return html.escape(str(s))
# (the 22 July rob_appraisals_v145.csv load was removed on 2026-09-18: it covered 317 of 443
#  studies and everything that read it now reads a complete source)
MEASUREMENT_BY_CONSTRUCT = {"CONTENT": "CONTENT_CODING", "RECALL": "SELF_REPORT",
    "EXPOSURE": "BEHAVIOURAL", "REACH": "BEHAVIOURAL", "SHARING": "BEHAVIOURAL",
    "CONCENTRATION": "BEHAVIOURAL"}   # see phaseB_prep_regression.py for why this is not a join

def pct(r):
    v=g(r,"value_pct")
    try: return float(v.replace("%","")) if v else None
    except: return None
for r in rows:
    r["_p"]=pct(r); r["_denom"]=g(r,"denom_class") or "?"
    # Same main-set definition as the invariants, descriptives and GRADE.
    r["_main"]=(g(r,"demographic_group")=="" and (g(r,"value_kind") or "proportion")=="proportion"
                and r["_p"] is not None)
MAIN=[r for r in rows if r["_main"]]
def studymeds(subset):
    by=defaultdict(list)
    for r in subset:
        if r["_p"] is not None: by[g(r,"id")].append(r["_p"])
    return sorted(st.median(v) for v in by.values() if v)
def summ(meds):
    if not meds: return None
    return dict(n=len(meds),med=st.median(meds),mn=min(meds),mx=max(meds),
        q1=st.quantiles(meds,n=4)[0] if len(meds)>=4 else min(meds),
        q3=st.quantiles(meds,n=4)[2] if len(meds)>=4 else max(meds))

# ---------- tiny SVG helpers ----------
def svg_open(w,h): return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" font-family="-apple-system,Segoe UI,Roboto,sans-serif">']
def esc_t(s): return html.escape(str(s))
def txt(x,y,s,size=12,anchor="start",fill="#222",weight="normal"):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{fill}" font-weight="{weight}">{esc_t(s)}</text>'
def rect(x,y,w,h,fill,rx=2): return f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w,0):.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}"/>'
def line(x1,y1,x2,y2,stroke="#bbb",w=1,dash=""):
    d=f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{w}"{d}/>'
def circ(cx,cy,r,fill,stroke="none"): return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}" stroke="{stroke}"/>'

# CVD-SAFE PALETTES. The previous green/amber/red traffic light was unreadable for
# deuteranopes -- and it carried the paper's central comparison, so the figure failed for
# ~8% of male readers. Replaced with cool->warm ramps that avoid the green/red pair and were
# verified with the dataviz validator (lightness band, chroma floor, CVD separation,
# normal-vision floor all PASS). Colour is never the only encoding: every mark carries a
# direct label or a written LOW/MODERATE/HIGH tag, which also discharges the orange
# contrast warning.
ROBCOL={'LOW':'#56B4E9','MODERATE':'#E69F00','HIGH':'#D55E00','':'#999'}
def write(name,parts): (ROOT/"docs"/name).write_text("\n".join(parts)+"\n</svg>")

# ================= FIG 1 — prevalence by construct =================
def fig1():
    order=["EXPOSURE","REACH","SHARING","CONTENT","RECALL","CONCENTRATION"]
    data=[]
    for c in order:
        if c=="CONCENTRATION":
            m=studymeds([r for r in rows if g(r,"construct")=="CONCENTRATION"])
        else:
            m=studymeds([r for r in MAIN if g(r,"construct")==c])
        s=summ(m)
        if s: data.append((c,s))
    W,H=760,60+46*len(data); L,Rp=210,60; xmax=100
    def X(v): return L+(v/xmax)*(W-L-Rp)
    P=svg_open(W,H); P.append(rect(0,0,W,H,"#fff",0))
    P.append(txt(L,26,"Prevalence by construct — study-level medians (main-analysis set)",13,"start","#111","bold"))
    for gx in range(0,101,20):
        P.append(line(X(gx),44,X(gx),H-16,"#eee",1)); P.append(txt(X(gx),H-4,f"{gx}%",10,"middle","#999"))
    y=58
    for c,s in data:
        yc=y+18
        P.append(txt(L-10,yc+4,c,12,"end","#333","bold"))
        P.append(line(X(s['mn']),yc,X(s['mx']),yc,"#cbd5e1",6))         # range
        P.append(line(X(s['q1']),yc,X(s['q3']),yc,"#7aa0c4",10))        # IQR
        P.append(circ(X(s['med']),yc,6,"#0a4"))                          # median
        P.append(txt(X(s['med']),yc-9,f"{s['med']:.1f}%",11,"middle","#0a4","bold"))
        P.append(txt(W-8,yc+4,f"n={s['n']}",10,"end","#999"))
        y+=46
    write("fig1_prevalence_by_construct.svg",P)

# ================= FIG 2 — method drivers (the core figure) =================
def fig2():
    def meas(r): return MEASUREMENT_BY_CONSTRUCT.get(g(r,"construct").upper(), "")
    # All five bands are computed over the same set, the six prevalence constructs. The
    # measurement band used to be restricted to the audience constructs, which left content
    # coding at n = 5 while the text quoted its median as the content-coding figure (caught by
    # the 2026-09-02 pre-submission review).
    PREV=["EXPOSURE","REACH","RECALL","SHARING","CONTENT","CONCENTRATION"]
    groups=[]  # (band_label, [(label,summary)])
    m1=[("Behavioural trace",summ(studymeds([r for r in MAIN if g(r,"construct") in PREV and meas(r)=="BEHAVIOURAL"]))),
        ("Content coding",   summ(studymeds([r for r in MAIN if g(r,"construct") in PREV and meas(r)=="CONTENT_CODING"]))),
        ("Self-report",      summ(studymeds([r for r in MAIN if g(r,"construct") in PREV and meas(r)=="SELF_REPORT"])))]
    def samp(v): return summ(studymeds([r for r in MAIN if g(r,"construct") in PREV and g(r,"sampling_frame")==v]))
    m2=[("Behavioural panel",samp("panel_trace")),("Full census",samp("full_census")),
        ("Keyword-topical",samp("keyword_topical")),("Survey self-report",samp("survey_sample"))]
    def gt(canon,preds):
        sub=[r for r in MAIN if g(r,"construct") in PREV and preds(g(r,"ground_truth").lower())]
        return summ(studymeds(sub))
    m3=[("Domain list",gt("dl",lambda x:("domain" in x or "newsguard" in x or "low-cred" in x))),
        ("Fact-checker",gt("fc",lambda x:("fact" in x and "check" in x))),
        ("Researcher coding",gt("rc",lambda x:("researcher" in x or "hand" in x or (("coded" in x or "coder" in x) and "domain" not in x)))),
        ("Self-report",gt("sr",lambda x:("self" in x and "report" in x) or "perceived" in x))]
    # bands 4-5 added 2026-08-25 (Sacha comment 45): construct + identification level,
    # same presentation as the other bands
    m4=[(lab, summ(studymeds([r for r in MAIN if g(r,"construct")==c])))
        for c,lab in [("EXPOSURE","Exposure"),("REACH","Reach"),("SHARING","Sharing"),("CONTENT","Content")]]
    # recall is shown split, as everywhere else in the paper (seen vs shared), never pooled
    m4+=[("Recall (seen)", summ(studymeds([r for r in MAIN if g(r,"construct")=="RECALL" and g(r,"recall_subtype")!="sharing"]))),
         ("Recall (shared)", summ(studymeds([r for r in MAIN if g(r,"construct")=="RECALL" and g(r,"recall_subtype")=="sharing"])))]
    def idm(v): return summ(studymeds([r for r in MAIN if g(r,"construct") in PREV and g(r,"classification_level")==v]))
    m5=[("Claim level",idm("claim_level")),("Source level",idm("source_level"))]
    # within-band ordering: smallest to largest median (Sacha comment 53, 2026-08-26)
    def _bysize(items): return sorted(items, key=lambda t: (t[1] is None, t[1]['med'] if t[1] else 0))
    bands=[("By measurement",_bysize(m1)),("By sampling frame",_bysize(m2)),
           ("By ground-truth source",_bysize(m3)),("By construct",_bysize(m4)),
           ("By identification level",_bysize(m5))]
    rowsN=sum(1+len(b[1]) for b in bands)
    # +22px of height over the old 70 to carry an axis title under the tick labels: the bars were
    # unlabelled percentages of nothing in particular unless the reader had the caption to hand.
    W,H=780,92+30*rowsN; L,Rp=250,60; xmax=65   # axis cut at 65%: the largest median is 57% (Sacha, 2026-09-11)
    def X(v): return L+(min(v,xmax)/xmax)*(W-L-Rp)
    P=svg_open(W,H); P.append(rect(0,0,W,H,"#fff",0))  # caption lives in the document, not the figure
    for gx in range(0,66,15):
        P.append(line(X(gx),40,X(gx),H-38,"#eee",1)); P.append(txt(X(gx),H-26,f"{gx}%",12,"middle","#999"))
    P.append(txt(L+(W-L-Rp)/2,H-6,"Prevalence of misinformation",12.5,"middle","#666"))
    y=52
    for band,items in bands:
        # Each band is computed over a different number of studies: a study whose value for that
        # moderator is uncoded drops out of that band only. The band total is on the figure because
        # the bands are read side by side and the bases range from 270 to 471 studies.
        tot=sum(s['n'] for _,s in items if s)
        P.append(txt(20,y+13,band,13,"start","#888","bold"))
        # Right-aligned on the same edge as the row labels below it. Placing these after the band
        # label, at 20 + len(band) * 7.3, put every band's count at a different x — four ragged
        # numbers down the left of the figure, since the labels differ in length by half a word.
        P.append(txt(L-10,y+13,f"{tot} studies",11,"end","#aaa")); y+=26
        for label,s in items:
            if not s:
                P.append(txt(L-10,y+13,label,13,"end","#333")); P.append(txt(L+4,y+13,"(no data)",11,"start","#bbb")); y+=30; continue
            yc=y+9
            P.append(txt(L-10,yc+4,label,13,"end","#333"))
            # position already encodes the value, so colouring BY value was redundant double-encoding
            col="#0072B2"
            P.append(rect(X(0),yc-6,X(s['med'])-X(0),12,col))
            # One decimal, like the forest plot and the text. Rounding to whole percent printed two
            # visibly different bars as the same "9%", and turned the exposure median of 1.3% into
            # "1%" -- a quarter of the value, on the smallest number in the paper.
            P.append(txt(X(s['med'])+6,yc+4,f"{s['med']:.1f}%",13,"start",col,"bold"))
            P.append(txt(W-8,yc+4,f"n = {s['n']}",11,"end","#777"))
            y+=30
    write("fig2_method_drivers.svg",P)

# ================= FIG 3 — whole-diet backbone =================
def fig3():
    # ratings from the v3 master (the v145 file predates the later-added studies and left them grey)
    rob3={r["study_id"]:(r["overall_ruling_corrected"] or r["overall"])
          for r in csv.DictReader(open(ROOT/"data/rob/risk_of_bias_v3_master.csv"))}
    WD={"all_media","news_diet","political_news","population"}
    sub=[r for r in MAIN if g(r,"construct") in ("EXPOSURE","REACH") and r["_denom"] in WD]
    by=defaultdict(list)
    for r in sub: by[g(r,"id")].append(r)
    items=[]
    for sid,rs in by.items():
        vals=[x["_p"] for x in rs if x["_p"] is not None]
        if vals: items.append((sid,st.median(vals),rob3.get(sid,""),
                               g(rs[0],"construct"), g(rs[0],"country_norm") or g(rs[0],"country")))
    items.sort(key=lambda t:(0 if t[3]=="EXPOSURE" else 1, t[1]))   # exposure block first, then reach
    meds=[t[1] for t in items]; pooled=st.median(meds)
    W=780; H=76+18*len(items)+44+34; L,Rp=250,60; xmax=max(70,math.ceil(max(meds)/10)*10)
    def X(v): return L+(v/xmax)*(W-L-Rp)
    P=svg_open(W,H); P.append(rect(0,0,W,H,"#fff",0))  # caption lives in the document
    # RoB colouring removed 2026-08-24 (appraisal reported descriptively; figure lives in the appendix)
    TOPY=46
    for gx in range(0,xmax+1,10):
        P.append(line(X(gx),TOPY,X(gx),H-30,"#f0f0f0",1)); P.append(txt(X(gx),H-16,f"{gx}%",9.5,"middle","#999"))
    P.append(line(X(pooled),TOPY-4,X(pooled),H-30,"#0a4",1.5,"4 3"))
    P.append(txt(min(X(pooled)+4,W-Rp-90),TOPY+6,f"median {pooled:.1f}%",10,"start","#0a4","bold"))
    y=TOPY+12; lastcon=None
    for n,(sid,med,rb,con,ctry) in enumerate(items):
        if con!=lastcon:
            gl=("Exposure: share of the diet that is misinformation" if con=="EXPOSURE"
                else "Reach: % of people encountering misinformation at least once")
            P.append(txt(24,y+13,gl,10,"start","#333","bold")); y+=22; lastcon=con
        yc=y+8
        if n%2==0: P.append(rect(20,y,W-20-Rp+30,18,"#fafafa"))
        P.append(txt(L-8,yc+3,ctry[:22],9.5,"end","#666"))
        P.append(line(L,yc,X(med)-7,yc,"#e8e8e8",1))
        P.append(circ(X(med),yc,5,'#0072B2'))
        P.append(txt(X(med)+8,yc+3,f"{med:.1f}",9,"start","#888"))
        y+=18
    write("fig3_whole_diet_backbone.svg",P)

# ================= CONCENTRATION deep-dive + FIG 4 =================
def concentration():
    conc=[r for r in rows if g(r,"construct")=="CONCENTRATION" and g(r,"conc_unit")=="user"]  # USER concentration only (headline)
    # source concentration written separately (not pooled into the 'top X% of people' story)
    srcc=[r for r in rows if g(r,"construct")=="CONCENTRATION" and g(r,"conc_unit")=="source"]
    with open(ROOT/"data/synth/phaseB/concentration_source.csv","w",newline="") as sf:
        sw=csv.writer(sf); sw.writerow(["id","top_group","activity_share_pct","country","quote"])
        for r in srcc: sw.writerow([g(r,"id"),g(r,"conc_group_pct") or "top-N sources",g(r,"value_pct"),g(r,"country_norm") or g(r,"country"),g(r,"source_quote")[:120]])
    # Hard-mapped (top % of people, activity share %) per row, read from source quotes (regex mis-parses
    # "1% of panel consumed 80%"). Ordered to match the 23 frozen CONCENTRATION rows; id-guarded below.
    # top=None where the study gives an absolute group (e.g. "~800 superspreaders") with no % of the base.
    # derive from the corrected frozen data (v1.4.7: value_pct=activity share, conc_group_pct=population fraction)
    std=[]
    for r in conc:
        def num(x):
            try: return float(x)
            except: return None
        std.append(dict(id=g(r,"id"),dimension=g(r,"conc_dimension") or "sharing",
                        top_pct_people=num(g(r,"conc_group_pct")),
                        activity_share_pct=num(g(r,"value_pct")) or num(g(r,"conc_share_pct")),
                        unit=g(r,"conc_unit"),country=g(r,"country_norm") or g(r,"country"),
                        platform=g(r,"platform_norm"),quote=g(r,"source_quote")[:140]))
    # write standardized table
    with open(ROOT/"data/synth/phaseB/concentration_standardized.csv","w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(std[0].keys())); w.writeheader(); w.writerows(std)
    # summary: top-1% subset (0.8<=top<=1.2)
    def shares_where(lo,hi):
        return [s["activity_share_pct"] for s in std if s["top_pct_people"] is not None
                and lo<=s["top_pct_people"]<=hi and s["activity_share_pct"] is not None]
    top1=shares_where(0.8,1.2); top10=shares_where(8,12); top20=shares_where(18,25)
    summ_c=dict(top1=(len(top1),round(st.median(top1),1) if top1 else None,f"{min(top1):.0f}-{max(top1):.0f}" if top1 else ""),
                top10=(len(top10),round(st.median(top10),1) if top10 else None),
                top20=(len(top20),round(st.median(top20),1) if top20 else None))
    # FIG 4: scatter top% (log x) vs share%
    pts=[s for s in std if s["top_pct_people"] and s["activity_share_pct"] and s["top_pct_people"]>0]
    W,H=720,430; L,B,Tp,Rp=60,60,50,30
    xs=[math.log10(p["top_pct_people"]) for p in pts]
    xmin,xmax=math.floor(min(xs)),math.ceil(max(xs))  # decades
    def X(lp): return L+(lp-xmin)/(xmax-xmin)*(W-L-Rp)
    def Y(sh): return H-B-(sh/100)*(H-B-Tp)
    P=svg_open(W,H); P.append(rect(0,0,W,H,"#fff",0))
    P.append(txt(20,26,"Concentration — a tiny fraction of people drive most misinfo activity",13,"start","#111","bold"))
    P.append(txt(20,42,"x: top % of people (log)   y: % of all misinfo exposure/sharing they account for",10,"start","#888"))
    for d in range(xmin,xmax+1):
        P.append(line(X(d),Tp,X(d),H-B,"#f0f0f0",1))
        lab={ -3:"0.001%", -2:"0.01%", -1:"0.1%",0:"1%",1:"10%",2:"100%"}.get(d,f"1e{d}%")
        P.append(txt(X(d),H-B+16,lab,10,"middle","#999"))
    for sh in range(0,101,25):
        P.append(line(L,Y(sh),W-Rp,Y(sh),"#f0f0f0",1)); P.append(txt(L-8,Y(sh)+4,f"{sh}%",10,"end","#999"))
    DIMC={"exposure":"#0072B2","sharing":"#D55E00"}
    for p in pts:
        P.append(circ(X(math.log10(p["top_pct_people"])),Y(p["activity_share_pct"]),5,DIMC.get(p["dimension"],"#888")+"cc","#fff"))
    # legend
    P.append(circ(W-150,Tp+4,5,DIMC["exposure"])); P.append(txt(W-140,Tp+8,"exposure",10,"start","#555"))
    P.append(circ(W-150,Tp+22,5,DIMC["sharing"])); P.append(txt(W-140,Tp+26,"sharing",10,"start","#555"))
    write("fig4_concentration_curve.svg",P)
    return std,summ_c

PREV=["EXPOSURE","REACH","RECALL","SHARING","CONTENT","CONCENTRATION"]
fig1(); fig2(); fig3(); std,summ_c=concentration()

# ---------- assemble HTML ----------
def embed(name): return (ROOT/"docs"/name).read_text()
def pctcell(v): return "" if v is None else f"{v:g}%"
def conc_row(s):
    return ("<tr><td class=sid>"+esc(s['id'])+"</td><td>"+esc(s['dimension'])+"</td><td>"
        +pctcell(s['top_pct_people'])+"</td><td>"+pctcell(s['activity_share_pct'])+"</td><td>"
        +esc(s['country'])+"</td><td style='font-size:11px;color:#777'>"+esc(s['quote'])+"</td></tr>")
conc_rows="".join(conc_row(s) for s in std)
t1=summ_c['top1']
HTML=f"""<meta charset=utf-8><title>Phase B — figures & concentration</title>
<style>
 body{{font:14px/1.55 -apple-system,Segoe UI,Roboto,sans-serif;max-width:900px;margin:22px auto;padding:0 16px;color:#181818}}
 h1{{font-size:23px}} h2{{margin-top:30px;border-bottom:2px solid #222;padding-bottom:4px}}
 .sub{{color:#666;margin:2px 0 10px}} svg{{max-width:100%;height:auto;border:1px solid #eee;border-radius:6px;background:#fff;margin:6px 0}}
 .box{{border:1px solid #cbd8e6;background:#eef4fb;border-radius:6px;padding:10px 14px;margin:10px 0}}
 .big{{font-size:24px;font-weight:800;color:#D55E00}}
 table{{border-collapse:collapse;width:100%;font-size:12px;margin-top:8px}} th,td{{border:1px solid #e3e3e3;padding:4px 7px;text-align:left}} th{{background:#f4f4f4}} .sid{{font-family:ui-monospace,monospace}}
</style>
<h1>Phase B · figures &amp; concentration deep-dive</h1>
<p class=sub>Source <span class=sid>{esc(CSV.name)}</span>. Vector SVG (dependency-free, deterministic).</p>

<h2>Figure 1 — prevalence is not one number</h2>
{embed('fig1_prevalence_by_construct.svg')}

<h2>Figure 2 — what drives the estimate <span style='font-weight:400;color:#888'>(the core result)</span></h2>
<p class=sub>The same underlying question — how much misinfo do people encounter — answered by different methods.</p>
{embed('fig2_method_drivers.svg')}

<h2>Figure 3 — the whole-diet backbone</h2>
{embed('fig3_whole_diet_backbone.svg')}

<h2>Figure 4 — concentration</h2>
{embed('fig4_concentration_curve.svg')}
<div class=box>
 <b>Across {t1[0]} studies reporting a "top 1%" figure, that 1% of people accounts for a median
 <span class=big>{t1[1]}%</span> of all misinfo exposure/sharing</b> (range {t1[2]}%).
 Top 10% → {summ_c['top10'][1]}% (n={summ_c['top10'][0]}). Misinformation activity is extremely concentrated in a tiny minority.
</div>
<h3 style="font-size:14px">Standardized concentration estimates ({len(std)} rows / {len({s['id'] for s in std})} studies)</h3>
<table><tr><th>study</th><th>dimension</th><th>top % of people</th><th>→ % of activity</th><th>country</th><th>quote</th></tr>{conc_rows}</table>
"""
(ROOT/"docs/phaseB_figures.html").write_text(HTML)
print("figures written: fig1-4 + docs/phaseB_figures.html")
print(f"concentration: top-1% -> median {t1[1]}% of activity across {t1[0]} studies (range {t1[2]})")
print(f"  top-10% -> {summ_c['top10'][1]}% (n={summ_c['top10'][0]}); top-20% -> {summ_c['top20'][1]}% (n={summ_c['top20'][0]})")
