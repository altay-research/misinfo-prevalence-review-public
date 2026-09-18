#!/usr/bin/env python3
"""phaseB_figures2.py — expanded figure gallery (many more figures). Dependency-free SVG.
Reads data/synth/phaseB/estimates_full.json. Produces a set of
publication figures (EXPOSURE/REACH split by estimate, by identification method, breadth gradient,
by topic/platform/ground-truth, RoB×construct, misinfo-vs-general concentration) + docs/phaseB_figure_gallery.html."""
import json, csv, html, statistics as st
from pathlib import Path
from collections import defaultdict
from fig_labels import pretty, warn_missing
ROOT=Path(__file__).resolve().parents[1]
D=json.load(open(ROOT/"data/synth/phaseB/estimates_full.json"))
MAIN=[d for d in D if d["main"] and d["value"] is not None]
def esc(s): return html.escape(str(s))
def med(a): a=[x for x in a if x is not None];return st.median(a) if a else None
def q(a,p): a=sorted(x for x in a if x is not None);return (st.quantiles(a,n=4)[int(p)] if len(a)>=4 else (a[0] if a else None))

# ---- SVG primitives ----
def S(w,h): return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" font-family="-apple-system,Segoe UI,Roboto,sans-serif" width="{w}" height="{h}">',f'<rect width="{w}" height="{h}" fill="#fff"/>']
def txt(x,y,s,sz=12,a="start",f="#222",w="normal"): return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{sz}" text-anchor="{a}" fill="{f}" font-weight="{w}">{esc(s)}</text>'
def ln(x1,y1,x2,y2,c="#ddd",w=1,d=""): return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c}" stroke-width="{w}"{" stroke-dasharray=\'"+d+"\'" if d else ""}/>'
def cir(x,y,r,f,o=0.72): return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{f}" fill-opacity="{o}" stroke="#fff" stroke-width="0.5"/>'
def rect(x,y,w,h,f): return f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w,0):.1f}" height="{h:.1f}" fill="{f}"/>'
def diamond(x,y,f="#111",s=7): return f'<path d="M{x:.1f},{y-s} L{x+s:.1f},{y} L{x:.1f},{y+s} L{x-s:.1f},{y} Z" fill="{f}"/>'
def save(name,parts): (ROOT/"docs"/name).write_text("\n".join(parts)+"\n</svg>")
# CVD-SAFE PALETTES. The previous green/amber/red traffic light was unreadable for
# deuteranopes -- and it carried the paper's central comparison, so the figure failed for
# ~8% of male readers. Replaced with cool->warm ramps that avoid the green/red pair and were
# verified with the dataviz validator (lightness band, chroma floor, CVD separation,
# normal-vision floor all PASS). Colour is never the only encoding: every mark carries a
# direct label or a written LOW/MODERATE/HIGH tag, which also discharges the orange
# contrast warning.
ROBCOL={'LOW':'#56B4E9','MODERATE':'#E69F00','HIGH':'#D55E00','':'#bbb'}
CONCOL={'BEHAVIOURAL':'#0072B2','CONTENT_CODING':'#E69F00','SELF_REPORT':'#D55E00','NA':'#999'}

def strip(name, title, groups, colorf=None, xmax=100, sub="", W=820):
    """groups = list of (label, [records]) ; each record dict with 'value'. colorf(d)->hex."""
    rowH=max(30,min(60,460/max(len(groups),1))); H=54+len(groups)*rowH+30; L,Rp=200,40
    def X(v): return L+(min(v,xmax)/xmax)*(W-L-Rp)
    P=S(W,H); P.append(txt(18,24,title,14,"start","#111","bold"))
    if sub: P.append(txt(18,40,sub,11,"start","#888"))
    for gx in range(0,int(xmax)+1,20): P.append(ln(X(gx),46,X(gx),H-26,"#f0f0f0"));P.append(txt(X(gx),H-12,f"{gx}%",10,"middle","#aaa"))
    y=52
    for lab,recs in groups:
        yc=y+rowH/2-4; vals=[r["value"] for r in recs]
        m,q1,q3=med(vals),q(vals,0),q(vals,2)
        P.append(txt(L-8,yc+4,f"{lab}",11.5,"end","#333"))
        P.append(txt(L-8,yc+16,f"n={len(recs)}",9,"end","#bbb"))
        if q1 is not None and len(vals)>=4: P.append(ln(X(q1),yc,X(q3),yc,"#cbd8e8",7))
        for i,r in enumerate(recs):
            j=((i*2654435761)%1000/1000-0.5)*(rowH-14)
            rad=2.6 if not r.get("n") else max(2.2,min(6.5,1.6+ (len(str(int(r["n"])))-1)*0.8))
            P.append(cir(X(r["value"]),yc+j,rad,(colorf(r) if colorf else "#0072B2")))
        if m is not None: P.append(diamond(X(m),yc));P.append(txt(X(m),yc-10,f"{m:.1f}%",10.5,"middle","#111","bold"))
        y+=rowH
    save(name,P); return name

# ============ FIG A: EXPOSURE vs REACH split, BY ESTIMATE ============
WD={"all_media","news_diet","population","political_news"}
expo=[d for d in MAIN if d["construct"]=="EXPOSURE" and d["denom_class"] in WD]
reach=[d for d in MAIN if d["construct"]=="REACH" and d["denom_class"] in WD]
strip("figA_exposure_reach_split.svg","Whole-diet backbone, split by quantity (every estimate)",
      [("EXPOSURE\n(diet-share)",expo),("REACH\n(% reached ≥1)",reach)],
      colorf=lambda d:"#009E73" if d["construct"]=="EXPOSURE" else "#0072B2",
      sub="The two quantities the pooled 'backbone' was mixing: diet-share ~1-3% vs % reached-ever ~9-40%.")

# ============ FIG B: by identification method ============
methods=["domain/source list","fact-check (claim/URL)","researcher content-coding","classifier/LLM","self-report"]
gB=[(m,[d for d in MAIN if d["id_method"]==m and d["construct"] in ("EXPOSURE","REACH","RECALL","SHARING","CONTENT")]) for m in methods]
strip("figB_by_id_method.svg","Prevalence by how misinformation was identified",
      [(l,r) for l,r in gB if r], colorf=lambda d:CONCOL.get(d["measurement"],"#999"),
      sub="Domain/source lists vs claim-level fact-check vs researcher-coding vs classifier vs self-report. Colour = measurement type.")

# ============ FIG C: definitional breadth gradient (within CONTENT) ============
border=["fabricated","false","misleading","unreliable_source","low_quality"]
gC=[(pretty(b),[d for d in MAIN if d["construct"]=="CONTENT" and d["breadth"]==b]) for b in border]
strip("figC_breadth_gradient.svg","Definitional breadth drives content prevalence (within CONTENT)",
      [(l,r) for l,r in gC if r], colorf=lambda d:"#D55E00",
      sub="Strict → loose. Looser definitions yield higher 'prevalence' — a property of the definition.")

# ============ FIG D: by topic ============
# Ties break on the name, not on the set's iteration order: a set of strings iterates in hash order,
# which changes per process, so two builds of the same figure put tied rows in different places.
topics=sorted({d["topic"] for d in MAIN if d["topic"]},
              key=lambda t:(-(med([d["value"] for d in MAIN if d["topic"]==t]) or 0), t))
gD=[(pretty(t),[d for d in MAIN if d["topic"]==t]) for t in topics]
strip("figD_by_topic.svg","Prevalence by topic",[(l,r) for l,r in gD if r],
      colorf=lambda d:CONCOL.get(d["measurement"],"#999"),sub="Health/COVID-heavy corpus. Colour = measurement type.")

# ============ FIG E: by platform ============
plats=sorted({d["platform"] for d in MAIN if d["platform"]},
             key=lambda p:(-len([d for d in MAIN if d["platform"]==p]), p))[:10]
gE=[(pretty(p),[d for d in MAIN if d["platform"]==p]) for p in plats]
strip("figE_by_platform.svg","Prevalence by platform (top 10)",[(l,r) for l,r in gE if r],
      colorf=lambda d:CONCOL.get(d["measurement"],"#999"))

# ============ FIG F: RoB composition by construct (stacked bars) ============
def figF():
    cons=["EXPOSURE","REACH","RECALL","SHARING","CONTENT","CONCENTRATION"]
    W,H=780,60+42*len(cons); L=160
    P=S(W,H); P.append(txt(18,24,"Risk of bias by construct — bias tracks the number inversely",14,"start","#111","bold"))
    P.append(txt(18,40,"Share of each construct's studies at LOW / MODERATE / HIGH risk of bias.",11,"start","#888"))
    y=54
    for c in cons:
        studies={d["id"] for d in D if d["construct"]==c and d["main"]}
        robs=[next((d["rob"] for d in D if d["id"]==sid and d["rob"]),"") for sid in studies]
        robs=[r for r in robs if r]; nn=len(robs) or 1
        P.append(txt(L-8,y+16,c,11.5,"end","#333"))
        x=L
        for lvl in ["LOW","MODERATE","HIGH"]:
            w=(robs.count(lvl)/nn)*(W-L-40)
            if w>0: P.append(rect(x,y+4,w,22,ROBCOL[lvl]))
            if w>26: P.append(txt(x+w/2,y+19,f"{round(robs.count(lvl)/nn*100)}%",10,"middle","#fff","bold"))
            x+=w
        P.append(txt(W-34,y+19,f"n{len(robs)}",9,"start","#aaa"))
        y+=42
    # legend
    lx=L
    for lvl in ["LOW","MODERATE","HIGH"]:
        P.append(rect(lx,H-20,12,12,ROBCOL[lvl]));P.append(txt(lx+16,H-10,lvl,10,"start","#666"));lx+=95
    save("figF_rob_by_construct.svg",P)
figF()

# ============ FIG G: misinfo vs general-news concentration (dumbbell) ============
def figG():
    # direct-comparison studies transcribed from data/inputs/nonmisinfo_concentration.csv
    # (top-1% general vs misinfo). figK in phaseB_figures3.py reads that file directly.
    pairs=[("Osmundsen 2021","real-news shares",30,75),
           ("Grinberg 2019","political-URL shares",49,82),
           ("Grinberg 2019","political-URL exposure",12,74),
           ("Zhou 2024","reliable vs unreliable pages",43.2,65.3),
           ("Eady 2023","domestic-news exposure",24,70),
           ("Eady 2023","politician exposure",37,70),
           ("van der Linden 2024","nonfake vs fake (by supersharers)",None,None)]
    pairs=[p for p in pairs if p[2] is not None]
    W,H=800,70+34*len(pairs); L,Rp=230,50
    def X(v): return L+(v/100)*(W-L-Rp)
    P=S(W,H); P.append(txt(18,24,"Is misinformation more concentrated than news in general? Yes.",14,"start","#111","bold"))
    P.append(txt(18,40,"Share of all activity from the TOP 1% of users — general news (blue) vs misinformation (red).",11,"start","#888"))
    for gx in range(0,101,20): P.append(ln(X(gx),48,X(gx),H-24,"#f0f0f0"));P.append(txt(X(gx),H-10,f"{gx}%",10,"middle","#aaa"))
    y=56
    for lab,what,gen,mis in pairs:
        yc=y+9
        P.append(txt(L-8,yc,lab,11,"end","#333"));P.append(txt(L-8,yc+12,what,9,"end","#aaa"))
        P.append(ln(X(gen),yc,X(mis),yc,"#ccc",2))
        P.append(cir(X(gen),yc,6,"#0072B2",1));P.append(cir(X(mis),yc,6,"#D55E00",1))
        P.append(txt(X(gen),yc-9,f"{gen:g}",9,"middle","#0072B2","bold"));P.append(txt(X(mis),yc-9,f"{mis:g}",9,"middle","#D55E00","bold"))
        y+=34
    P.append(cir(L,H-14,6,"#0072B2",1));P.append(txt(L+10,H-11,"general news",10,"start","#666"))
    P.append(cir(L+130,H-14,6,"#D55E00",1));P.append(txt(L+140,H-11,"misinformation",10,"start","#666"))
    save("figG_concentration_comparison.svg",P)
figG()

# ============ FIG H: ground-truth source ============
gts=["domain_list","NewsGuard","fact_checker","researcher_coding","classifier","self_report"]
gH=[(pretty(g),[d for d in MAIN if d["ground_truth"]==g]) for g in gts]
strip("figH_ground_truth.svg","Prevalence by ground-truth source",[(l,r) for l,r in gH if r],
      colorf=lambda d:CONCOL.get(d["measurement"],"#999"))

FIGS=[("figK_concentration_flow.svg","Concentration — the top 1% account for most (misinfo vs general news)"),
      ("figQ_matched_concentration.svg","Concentration — the same panels, matched (within-panel ratios)"),
      ("figL_concentration_lorenz.svg","Concentration — Lorenz view (all cutoffs, vs equality & general news)"),
      ("figI_by_political.svg","Misinformation by political orientation"),
      ("figJ_by_age.svg","Misinformation by age group"),
      ("figA_exposure_reach_split.svg","Whole-diet split: EXPOSURE (diet-share) vs REACH (% reached), by estimate"),
      ("figB_by_id_method.svg","By identification method (domain-list vs claim vs classifier vs self-report)"),
      ("figC_breadth_gradient.svg","Definitional breadth gradient (within CONTENT)"),
      ("figD_by_topic.svg","By topic"),("figE_by_platform.svg","By platform"),
      ("figF_rob_by_construct.svg","Risk of bias by construct"),
      ("figG_concentration_comparison.svg","Misinfo vs general-news concentration (top 1%)"),
      ("figH_ground_truth.svg","By ground-truth source"),
      ("fig1_prevalence_by_construct.svg","Prevalence by construct"),
      ("fig2_method_drivers.svg","What drives the estimate"),
      ("fig4_concentration_curve.svg","Concentration curve")]
body="".join(f'<section><h2>{esc(t)}</h2>{(ROOT/"docs"/f).read_text()}</section>' for f,t in FIGS if (ROOT/"docs"/f).exists())
HTML=f"""<meta charset=utf-8><title>Phase B — figure gallery</title>
<style>body{{font:14px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;max-width:900px;margin:20px auto;padding:0 16px;color:#181818}}
h1{{font-size:22px}} h2{{font-size:15px;margin:26px 0 6px;color:#333}} section{{margin-bottom:10px}} svg{{max-width:100%;height:auto;border:1px solid #eee;border-radius:8px}}
p.sub{{color:#666}}</style>
<h1>Phase B — figure gallery</h1>
<p class=sub>All static figures (frozen v1.4.6). Interactive version: <a href="companion_dashboard.html">companion_dashboard.html</a>.</p>
{body}"""
(ROOT/"docs/phaseB_figure_gallery.html").write_text(HTML)
warn_missing("figure gallery")
print(f"wrote {len(FIGS)} figures + docs/phaseB_figure_gallery.html")
print("EXPOSURE(diet) est-median:", round(med([d['value'] for d in expo]),2), "| REACH est-median:", round(med([d['value'] for d in reach]),2))
