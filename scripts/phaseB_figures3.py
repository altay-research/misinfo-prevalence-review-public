#!/usr/bin/env python3
"""phaseB_figures3.py — (1) prevalence/sharing by political orientation & by age (demographic breakdowns),
(2) an intuitive 'minority accounts for most' concentration flow figure (misinfo vs general news),
(3) the same comparison held within panel (figQ), which is the defensible form of (2).
Dependency-free SVG. Reads the freeze + data/synth/phaseB/concentration_by_threshold.csv
+ data/synth/phaseB/review_matched_concentration.csv + data/inputs/nonmisinfo_concentration.csv."""
import csv, re, html, statistics as st
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1]
CSV=ROOT/re.search(r'File:\s*(\S+)',(ROOT/"docs/FROZEN.md").read_text()).group(1)
rows=list(csv.DictReader(open(CSV)))
def g(r,k): return (r.get(k) or "").strip()
def esc(s): return html.escape(str(s))
def pv(r):
    try: return float(g(r,"value_pct"))
    except: return None
def med(a): a=[x for x in a if x is not None];return st.median(a) if a else None
def S(w,h): return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" font-family="-apple-system,Segoe UI,Roboto,sans-serif">',f'<rect width="{w}" height="{h}" fill="#fff"/>']
def txt(x,y,s,sz=12,a="start",f="#222",w="normal"): return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{sz}" text-anchor="{a}" fill="{f}" font-weight="{w}">{esc(s)}</text>'
def ln(x1,y1,x2,y2,c="#ddd",w=1): return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c}" stroke-width="{w}"/>'
def cir(x,y,r,f,o=0.8): return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{f}" fill-opacity="{o}" stroke="#fff" stroke-width="0.5"/>'
def diamond(x,y,f="#111",s=6): return f'<path d="M{x:.1f},{y-s} L{x+s:.1f},{y} L{x:.1f},{y+s} L{x-s:.1f},{y} Z" fill="{f}"/>'
def save(name,P): (ROOT/"docs"/name).write_text("\n".join(P)+"\n</svg>")

# ============ FIG: by political orientation — DOTS with clear row bands; mixed separated ============
def fig_political():
    spectrum=["far_left","left","center","right","far_right"]   # ordered L-R
    extra=["mixed"]                                              # NOT on the L-R axis -> shown separately
    order=spectrum+extra
    BRCOL={"unreliable_source":"#E69F00","false":"#D55E00","fabricated":"#8b0000","misleading":"#d2691e","":"#888"}
    cons=[("SHARING","% of the group's shared links that are misinfo/unreliable (within-group sharing RATE — not concentration)"),
          ("REACH","% of the group exposed to ≥1 misinfo source (within-group reach RATE)")]
    W=800; L=118; rh=26; panelH=len(order)*rh+40
    H=110+len(cons)*panelH
    P=S(W,H); P.append(txt(18,24,"Misinformation RATES by political orientation — every estimate shown",14,"start","#111","bold"))
    P.append(txt(18,40,"Each dot = one per-subgroup RATE (share of the group's OWN activity that is misinfo). Diamond = median. Colour = definition. NOT concentration.",9.5,"start","#D55E00"))
    P.append(txt(18,53,"Party placements follow conventional left-right classification (Chapel-Hill-Expert-Survey / ParlGov consensus: FN/AfD/FdI=far-right, LFI/Die-Linke=far-left, LR/Lega/CDU=right, PS/Labour=left, REM=center).",9,"start","#888"))
    P.append(txt(18,65,"'mixed' = independents / mixed groups / non-partisan — NOT a point on the left-right axis, so shown separately below the line.",9,"start","#888"))
    ytop=80
    for c,subt in cons:
        P.append(txt(18,ytop+11,c,12,"start","#333","bold")); P.append(txt(80,ytop+11,subt,8.5,"start","#999"))
        rowsc={o:[] for o in order}
        for r in rows:
            if g(r,"construct")==c and g(r,"political_orientation") in order and g(r,"demographic_subtype")=="per_subgroup_rate" and pv(r) is not None:
                rowsc[g(r,"political_orientation")].append((pv(r),g(r,"breadth")))
        xmax=max([v[0] for o in order for v in rowsc[o]]+[10])*1.12
        def X(v): return L+(min(v,xmax)/xmax)*(W-L-46)
        y0=ytop+22
        # gridlines
        for gx in range(0,int(xmax)+1,10):
            P.append(ln(X(gx),y0-2,X(gx),y0+len(order)*rh,"#eee")); P.append(txt(X(gx),y0+len(order)*rh+12,f"{gx}%",9,"middle","#bbb"))
        for i,o in enumerate(order):
            yc=y0+i*rh+rh/2
            # alternating row band
            if i%2==0: P.append(f'<rect x="{L-2}" y="{y0+i*rh}" width="{W-L-44}" height="{rh}" fill="#f8f9fb"/>')
            if o=="mixed": P.append(ln(L-100,y0+i*rh,W-46,y0+i*rh,"#ccc",1))  # divider before mixed
            dots=rowsc[o]
            lab=("mixed/indep." if o=="mixed" else o.replace("_"," "))
            P.append(txt(L-8,yc+3,lab,10,"end","#333" if o!="mixed" else "#999"))
            for j,(v,br) in enumerate(dots):
                jit=((j*37)%3-1)*3.5
                P.append(cir(X(v),yc+jit,4.5,BRCOL.get(br,"#888"),0.82))
            if dots:
                m=st.median([d[0] for d in dots])
                P.append(diamond(X(m),yc,"#111",5)); P.append(txt(X(m),yc-8,f"{m:.1f}%",9,"middle","#111","bold"))
                P.append(txt(W-42,yc+3,f"n{len(dots)}",8,"start","#bbb"))
            else:
                P.append(txt(X(0)+6,yc+3,"(no estimates)",9,"start","#ccc"))
        ytop+=panelH
    lx=L
    for br,lab in [("unreliable_source","unreliable-source"),("false","false/misinfo"),("misleading","misleading")]:
        P.append(cir(lx,H-12,4.5,BRCOL[br],0.9)); P.append(txt(lx+8,H-9,lab,9,"start","#666")); lx+=150
    save("figI_by_political.svg",P)

# ============ FIG: by age — within-study slope lines (no cross-study pooling) ============
def fig_age():
    def midpt(grp):
        nums=[int(x) for x in re.findall(r'\d+',grp)]
        if not nums: return 45
        return (nums[0]+nums[1])/2 if len(nums)>=2 and nums[1]<100 else nums[0]+5
    # build one series per (study, construct, sub-scope) with >=2 age points (or singletons shown as dots)
    CON={"SHARING":"#D55E00","REACH":"#0072B2","RECALL":"#009E73","EXPOSURE":"#009E73"}
    series=defaultdict(list)  # key -> list of (age_mid, value)
    labels={}
    for r in rows:
        if g(r,"demographic_dimension")=="age" and pv(r) is not None and g(r,"construct")!="RECALL":
            c=g(r,"construct"); sid=g(r,"id")
            scope=""
            mt=g(r,"measure_type").lower()
            if "youtube" in mt: scope=" · YouTube health"
            elif "health" in mt or "low-cred health" in mt: scope=" · health website"
            elif "untrustworthy website" in mt: scope=" · untrustworthy sites"
            elif "who" in mt or "recall" in mt: scope=" · WHO recall"
            elif "fake" in mt or "fake-news" in mt: scope=" · fake-news URLs (indep.)"
            key=(sid,c,scope)
            series[key].append((midpt(g(r,"demographic_group")),pv(r)))
            labels[key]=f"{c}{scope}"
    W,H=780,430; L,B,Tp,Rp=54,70,60,240
    amin,amax=18,75; ymax=max(v for s in series.values() for _,v in s)*1.1
    def X(a): return L+(a-amin)/(amax-amin)*(W-L-Rp)
    def Y(v): return H-B-(v/ymax)*(H-B-Tp)
    P=S(W,H); P.append(txt(18,26,"Misinformation by age — each study's own gradient (no pooling across studies)",14,"start","#111","bold"))
    P.append(txt(18,43,"Merging incomparable studies into age bands would hide that they disagree. So each line is ONE study's within-study age slope.",10,"start","#888"))
    for a in range(20,71,10): P.append(ln(X(a),Tp,X(a),H-B,"#f3f3f3")); P.append(txt(X(a),H-B+16,f"{a}",9,"middle","#aaa"))
    P.append(txt((L+W-Rp)/2,H-B+30,"age (bin midpoint)",10,"middle","#888"))
    for gy in range(0,int(ymax)+1,20): P.append(ln(L,Y(gy),W-Rp,Y(gy),"#f3f3f3")); P.append(txt(L-6,Y(gy)+3,f"{gy}%",9,"end","#aaa"))
    # draw lines
    keys=sorted(series, key=lambda k:-max(v for _,v in series[k]))
    ly=Tp+4
    for key in keys:
        pts=sorted(series[key]); col=CON.get(key[1],"#888")
        if len(pts)>=2:
            d="M"+" L".join(f"{X(a):.1f},{Y(v):.1f}" for a,v in pts)
            P.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="2" stroke-opacity="0.85"/>')
        for a,v in pts: P.append(cir(X(a),Y(v),3.5,col,0.9))
        # right-side label
        la,lv=pts[-1]
        P.append(txt(W-Rp+8,ly,labels[key],9,"start",col,"bold"))
        P.append(txt(W-Rp+8,ly+11,f"({len(pts)} pt{'s' if len(pts)>1 else ''})",8,"start","#aaa"))
        ly+=26
    P.append(txt(W-Rp+8,ly+6,"Older users share/visit MORE in",8.5,"start","#555"))
    P.append(txt(W-Rp+8,ly+17,"most studies; YouTube-health flat.",8.5,"start","#555"))
    save("figJ_by_age.svg",P)

# ============ FIG: intuitive concentration flow (misinfo vs general) ============
def fig_flow():
    # top-1% activity share, both sides DERIVED from the pipeline (a hardcoded 70 went stale here
    # when the freeze moved — methods-lessons #2/#18):
    # misinfo = the headline top-<=1% user-band median; general = median of the user-level
    # non-misinfo comparators (denom != 'other' i.e. not the misinfo side, and user-level only).
    import statistics as _st
    _bt = list(csv.DictReader(open(ROOT/"data/synth/phaseB/concentration_by_threshold.csv")))
    misinfo = round(float(next(r for r in _bt if r["unit"]=="user" and "1%" in r["threshold_band"])
                          ["median_activity_share_pct"]))
    _nmrows = [r for r in csv.DictReader(open(ROOT/"data/inputs/nonmisinfo_concentration.csv"))
           if r["top_pct"]=="1" and (r["share"] or "").strip()
           and r["denom"]!="other" and "DOMAIN" not in r["detail"]
           and "MISINFO" not in r["detail"].upper()[:30]]
    _mis_row = next(r for r in _bt if r["unit"]=="user" and "1%" in r["threshold_band"])
    mis_k, mis_lo, mis_hi = int(_mis_row["k_studies"]), float(_mis_row["min"]), float(_mis_row["max"])
    _bysd={}
    for r in _nmrows: _bysd.setdefault(r["id"],[]).append(float(r["share"]))
    # STUDY-level median (one point per panel), matching the paper's primary statistic
    _gen_meds=[_st.median(v) for v in _bysd.values()]
    general = int(_st.median(_gen_meds)+0.5)
    gen_k, gen_n = len(_bysd), sum(len(v) for v in _bysd.values())
    gen_lo, gen_hi = min(_gen_meds), max(_gen_meds)
    W,H=820,368
    P=S(W,H)  # caption lives in the document
    def panel(x0,label,basis,share,lo,hi,col):
        pop_x=x0+30; act_x=x0+250; barW=34; top=104; barH=210
        P.append(txt(x0+150,top-38,label,12,"middle","#333","bold"))
        P.append(txt(x0+150,top-24,basis,9.5,"middle","#888"))
        # Population bar, drawn TO SCALE: the sliver is exactly 1% of the column's height. It was
        # padded by 4px to make it easier to see, which drew the top 1% of people at three times
        # its size -- in the one figure whose whole argument is how small that group is.
        sliver=barH*0.01
        P.append(f'<rect x="{pop_x}" y="{top}" width="{barW}" height="{sliver}" fill="{col}"/>')
        P.append(f'<rect x="{pop_x}" y="{top+sliver}" width="{barW}" height="{barH-sliver}" fill="#e5e7eb"/>')
        # leader line to the sliver, since a 2-pixel band cannot carry a label of its own
        P.append(ln(pop_x-30,top+sliver/2,pop_x-3,top+sliver/2,col,1))
        P.append(txt(pop_x-34,top+sliver/2+3,"top 1%",8.5,"end",col,"bold"))
        P.append(txt(pop_x+barW/2,top+barH+14,"people",10,"middle","#888"))
        # activity bar: share on top
        sh=barH*share/100
        P.append(f'<rect x="{act_x}" y="{top}" width="{barW}" height="{sh}" fill="{col}"/>')
        P.append(f'<rect x="{act_x}" y="{top+sh}" width="{barW}" height="{barH-sh}" fill="#e5e7eb"/>')
        P.append(txt(act_x+barW/2,top+sh/2+4,f"{share}%",13,"middle","#fff","bold"))
        P.append(txt(act_x+barW/2,top+barH+14,"activity",10,"middle","#888"))
        # observed spread across the contributing studies, so the median is not read as a constant
        wx=act_x+barW+16
        P.append(ln(wx,top+barH*lo/100,wx,top+barH*hi/100,col,1.2))
        for v in (lo,hi):
            P.append(ln(wx-4,top+barH*v/100,wx+4,top+barH*v/100,col,1.2))
            P.append(txt(wx+8,top+barH*v/100+3,f"{v:.0f}%",8.5,"start","#888"))
        P.append(txt(wx,top+barH*hi/100+17,"range",9,"middle","#aaa"))
        # ribbon from sliver to share block
        P.append(f'<path d="M{pop_x+barW},{top} C{(pop_x+act_x)/2},{top} {(pop_x+act_x)/2},{top} {act_x},{top} '
                 f'L{act_x},{top+sh} C{(pop_x+act_x)/2},{top+sh} {(pop_x+act_x)/2},{top+sliver} {pop_x+barW},{top+sliver} Z" '
                 f'fill="{col}" fill-opacity="0.28"/>')
    panel(60,"MISINFORMATION",f"{mis_k} studies reporting the top 1%",misinfo,mis_lo,mis_hi,"#D55E00")
    panel(440,"NEWS IN GENERAL",f"{gen_k} panels, {gen_n} estimates",general,gen_lo,gen_hi,"#0072B2")
    save("figK_concentration_flow.svg",P)

# ============ FIG: the SAME panels, matched (the comparison figK makes across study sets) ============
def fig_matched():
    """Within-panel top-1% concentration, misinformation vs news in general.

    figK contrasts a median over the 5 studies that report a top-1% misinfo figure with a median
    over the 4 panels that also report the general-news figure: two different study sets. This
    figure holds the panel fixed, which is the comparison the Results treat as defensible.
    Reads review_matched_concentration.csv (phaseB_review_response.py), never its own arithmetic.
    """
    # Study names are not in the freeze (ids only), so they are curated here and guarded: a panel
    # entering or leaving the matched set fails the build rather than printing a bare Scopus id.
    NAMES={"2-s2.0-105002155467":"Zhou et al. 2025","2-s2.0-85060549676":"Grinberg et al. 2019",
           "2-s2.0-85105454127":"Osmundsen et al. 2021","2-s2.0-85145956359":"Eady et al. 2023"}
    rs=list(csv.DictReader(open(ROOT/"data/synth/phaseB/review_matched_concentration.csv")))
    panels=[r for r in rs if not r["study"].startswith("MEDIAN")]
    overall=next(r for r in rs if r["study"].startswith("MEDIAN"))
    unknown=[r["study"] for r in panels if r["study"] not in NAMES]
    assert not unknown, f"matched panel with no display name: {unknown} (add it to NAMES)"
    panels.sort(key=lambda r:(float(r["matched_ratio"]),NAMES[r["study"]]))
    items=[(NAMES[r["study"]],f'{r["news_estimates"]} news, {r["misinfo_estimates"]} misinfo estimates',r)
           for r in panels]
    items.append((f'Median of {len(panels)} panels',"",overall))
    W=780; L,Rp=196,104; H=96+34*len(items)+28
    def X(v): return L+(v/100)*(W-L-Rp)
    P=S(W,H)
    GEN,MIS="#0072B2","#D55E00"
    for gx in range(0,101,20):
        P.append(ln(X(gx),64,X(gx),H-34,"#f0f0f0")); P.append(txt(X(gx),H-18,f"{gx}%",10,"middle","#aaa"))
    P.append(txt((L+X(100))/2,H-4,"share of all activity accounted for by the top 1% of users",10,"middle","#888"))
    y=72
    for i,(lab,sub,r) in enumerate(items):
        gen,mis,ratio=float(r["news_top1_median"]),float(r["misinfo_top1_median"]),float(r["matched_ratio"])
        yc=y+9
        if lab.startswith("Median"):
            P.append(ln(L-186,y-4,W-24,y-4,"#ccc",1)); yc+=6
        P.append(txt(L-12,yc+(0 if sub else 3),lab,11.5,"end","#333","bold" if not sub else "normal"))
        if sub: P.append(txt(L-12,yc+12,sub,8.5,"end","#aaa"))
        P.append(ln(X(gen),yc,X(mis),yc,"#ddd",2))
        P.append(cir(X(gen),yc,6,GEN,1)); P.append(cir(X(mis),yc,6,MIS,1))
        P.append(txt(X(gen),yc-10,f"{gen:.1f}",9,"middle",GEN,"bold"))
        P.append(txt(X(mis),yc-10,f"{mis:.1f}",9,"middle",MIS,"bold"))
        P.append(txt(W-24,yc+4,f"×{ratio:.1f}",12,"end","#333","bold"))
        # direct labels on the first row, in the panel's whitespace, instead of a legend
        if i==0:
            P.append(txt(X(gen),yc-24,"news in general",9.5,"middle",GEN))
            P.append(txt(X(mis),yc-24,"misinformation",9.5,"middle",MIS))
        y+=34+(6 if lab.startswith("Median") else 0)
    P.append(txt(W-24,60,"ratio",9.5,"end","#aaa"))
    save("figQ_matched_concentration.svg",P)

# ============ FIG: Lorenz/Pareto — all cutoffs on one plot, vs equality + general news ============
def fig_lorenz():
    def f(x):
        try: return float(x)
        except: return None
    # misinfo points from frozen concentration
    mis=defaultdict(list)
    for r in rows:
        if g(r,"construct")=="CONCENTRATION":
            if g(r,"conc_unit")!="user": continue  # user-concentration only for the Lorenz headline
            t=f(g(r,"conc_group_pct")); a=f(g(r,"value_pct"))
            if t is not None and a is not None: mis[g(r,"id")].append((t,a))
    # general-news comparators (from library mining + direct in-corpus comparators)
    gen={"Muise 2022":[(21,64),(6,28)],"Wojcieszak 2022":[(13,86)],
         "Osmundsen":[(1,30)],"Grinberg":[(1,49)],"Zhou":[(1,43.2)],"Eady":[(1,24),(1,37)]}
    W,H=760,500; L,B,Tp,Rp=58,60,54,40; xmax=35
    def X(v): return L+(min(v,xmax)/xmax)*(W-L-Rp)
    def Y(v): return H-B-(v/100)*(H-B-Tp)
    P=S(W,H)  # title/reading guide live in the document caption (house rule)
    for gx in range(0,xmax+1,5): P.append(ln(X(gx),Tp,X(gx),H-B,"#f2f2f2")); P.append(txt(X(gx),H-B+15,f"{gx}%",9,"middle","#aaa"))
    for gy in range(0,101,20): P.append(ln(L,Y(gy),W-Rp,Y(gy),"#f2f2f2")); P.append(txt(L-6,Y(gy)+3,f"{gy}%",9,"end","#aaa"))
    P.append(txt((L+W-Rp)/2,H-B+30,"top % of people",10,"middle","#888"))
    # equality diagonal (y=x up to xmax)
    P.append(f'<path d="M{X(0)},{Y(0)} L{X(xmax)},{Y(xmax)}" stroke="#bbb" stroke-width="1.5" stroke-dasharray="5 4"/>')
    P.append(txt(X(xmax),Y(xmax)-6,"equality",9,"end","#aaa"))
    # general lines/points (blue)
    for k,pts in gen.items():
        pts=sorted(pts)
        if len(pts)>=2: P.append(f'<path d="M'+" L".join(f"{X(a)},{Y(b)}" for a,b in pts)+f'" fill="none" stroke="#0072B2" stroke-width="1.5" stroke-opacity="0.5"/>')
        for a,b in pts: P.append(cir(X(a),Y(b),4,"#0072B2",0.85))
    # misinfo lines/points (red)
    for sid,pts in mis.items():
        pts=sorted(pts)
        if len(pts)>=2: P.append(f'<path d="M'+" L".join(f"{X(a)},{Y(b)}" for a,b in pts)+f'" fill="none" stroke="#D55E00" stroke-width="1.5" stroke-opacity="0.5"/>')
        for a,b in pts: P.append(cir(X(a),Y(b),4.5,"#D55E00",0.8))
    # annotation for the top-1% band
    P.append(ln(X(1),Tp+14,X(1),H-B,"#E69F00",1))
    P.append(txt(X(1)+6,Y(35),"at the top 1%:",8.5,"start","#888"))
    P.append(txt(X(1)+6,Y(30),"misinfo ~68%",8.5,"start","#D55E00","bold"))
    P.append(txt(X(1)+6,Y(25),"news ~30-49%",8.5,"start","#0072B2","bold"))
    # legend
    P.append(cir(L+10,H-16,4.5,"#D55E00")); P.append(txt(L+18,H-13,"misinformation",9,"start","#666"))
    P.append(cir(L+130,H-16,4,"#0072B2")); P.append(txt(L+138,H-13,"news in general",9,"start","#666"))
    save("figL_concentration_lorenz.svg",P)

fig_political(); fig_age(); fig_flow(); fig_matched(); fig_lorenz()
print("wrote figI_by_political, figJ_by_age, figK_concentration_flow, figQ_matched_concentration, figL_concentration_lorenz")
PY_END = True
