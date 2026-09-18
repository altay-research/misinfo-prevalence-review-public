#!/usr/bin/env python3
"""
phaseB_descriptives.py — Phase B, component 1: descriptive backbone + DIAGNOSTIC pass.
Reads the FROZEN dataset (spec from docs/FROZEN.md), computes corpus counts and
prevalence distributions (estimate-level AND study-level) per construct x denominator,
enumerates the whole-diet backbone + concentration arm, and — crucially — flags data/coding
anomalies the analysis surfaces (out-of-range values, within-construct outliers, thin cells,
construct/denominator mismatches, missing fields, near-duplicate rows).

Read-only on the frozen data. Writes:
  data/synth/phaseB/{corpus_counts,construct_distributions,whole_diet,concentration,diagnostics}.csv
  docs/phaseB_descriptives.html
This is a REVIEW artifact (like the audit sheets), not a headline result — no re-freeze.
"""
import csv, os, re, html, statistics as st, sys
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]

def frozen_csv():
    """Read the File: line from docs/FROZEN.md so we always analyse the current freeze.

    Both failure paths RAISE. They used to fall back to estimates_v1.4.5_frozen.csv, which is still
    on disk, so a missing or unparseable pointer did not stop the run: it silently analysed a
    dataset seventeen versions old and every downstream number inherited that. validate_prisma.py
    carries a comment recording that the same fallback shipped once before and reported PASS on 329
    studies while the freeze held 317. A stage that analyses the wrong file is worse than one that
    fails, because only the failure is visible.
    """
    spec = (ROOT / "docs/FROZEN.md").read_text()
    m = re.search(r"File:\s*(\S+)", spec)
    if not m:
        raise SystemExit("phaseB_descriptives: cannot read the 'File:' line from docs/FROZEN.md")
    p = ROOT / m.group(1).strip("`")
    if not p.exists():
        raise SystemExit("phaseB_descriptives: FROZEN.md points at %s, which does not exist" % p)
    return p

CSV = frozen_csv()
rows = list(csv.DictReader(open(CSV)))
def g(r,k): return (r.get(k) or "").strip()
# One frozen row reads "single_country" where 788 read "single" (2-s2.0-85145196122, the study
# restored at v1.7.21). It is a spelling variant, not a different scope, and left alone it makes a
# one-study category of its own in every table grouped by this field. Normalised on read; the cell
# itself is a freeze edit and is logged for the next one.
def country_scope(r):
    v = (r.get("country_scope") or "").strip()
    return "single" if v == "single_country" else v
def esc(s): return html.escape(str(s))

# ---- value parsing -------------------------------------------------------
def parse_pct(r):
    """Return float percent in [0,100] or None. Prefer value_pct; else try value_raw a/b."""
    v = g(r,"value_pct")
    if v:
        try:
            f = float(v.replace("%","").strip())
            return f
        except ValueError:
            pass
    return None

for r in rows:
    r["_pct"] = parse_pct(r)
    r["_denom"] = g(r,"denom_class") or g(r,"denom_type") or "?"

def in_main_set(r):
    """The review's main-analysis set: proportions, not demographic subgroups.

    This filter was MISSING, and the construct table it feeds is the one FROZEN.md quotes as the
    HEADLINE MEDIANS. Without it, 104 demographic-subgroup rows and 10 non-proportion rows entered
    the study medians, which moved three constructs: REACH 11.1 -> 12.5 (k30 -> k28), EXPOSURE
    1.0 -> 1.3, SHARING k47 -> k45. The codebook and the main-set definition both say demographic
    rows never inflate a headline median; this is where that promise was being broken.
    Found by an audit on 2026-09-14, after the v1.7.19 freeze.
    """
    return (not g(r, "demographic_group")) and (g(r, "value_kind") or "proportion") == "proportion"

MAIN = [r for r in rows if in_main_set(r)]

STUDIES = {g(r,"id") for r in rows}
PREV_CONSTRUCTS = ["EXPOSURE","REACH","RECALL","SHARING","CONTENT","CONCENTRATION"]  # QUALITY/OTHER excluded from prevalence
WHOLE_DIET_DENOM = {"all_media","news_diet","political_news","population"}                       # clean audience-diet designs

def stats(vals):
    vals = [v for v in vals if v is not None]
    if not vals: return dict(n=0,median=None,q1=None,q3=None,min=None,max=None)
    vals = sorted(vals)
    q = st.quantiles(vals, n=4) if len(vals) >= 2 else [vals[0],vals[0],vals[0]]
    return dict(n=len(vals), median=round(st.median(vals),2),
                q1=round(q[0],2), q3=round(q[2],2), min=round(min(vals),2), max=round(max(vals),2))

# ============================ 1. CORPUS COUNTS ============================
def counts_by(field, norm=None):
    pick = norm if norm else (lambda r: g(r, field))
    return Counter(pick(r) or "(blank)" for r in rows)
corpus = {
    "construct": counts_by("construct"),
    "denom_class": Counter(r["_denom"] for r in rows),
    "platform_norm": counts_by("platform_norm"),
    "country_scope": counts_by("country_scope", norm=country_scope),
    "ground_truth": counts_by("ground_truth"),
    "unit": counts_by("unit"),
    "measure(question_type)": counts_by("question_type"),
}

# ============================ 2. DISTRIBUTIONS ============================
# estimate-level: all parsed pct rows per construct; study-level: median-per-study then across studies
def dist_for(subset):
    est = [r["_pct"] for r in subset]
    by_study = defaultdict(list)
    for r in subset:
        if r["_pct"] is not None: by_study[g(r,"id")].append(r["_pct"])
    study_meds = [st.median(v) for v in by_study.values() if v]
    return stats(est), stats(study_meds), len({g(r,'id') for r in subset})

construct_rows = []
for c in PREV_CONSTRUCTS:
    sub = [r for r in MAIN if g(r,"construct")==c]
    e,s,nst = dist_for(sub)
    construct_rows.append(dict(construct=c, level="ALL denominators", n_studies=nst,
        est_n=e["n"], est_median=e["median"], est_iqr=f'{e["q1"]}–{e["q3"]}', est_range=f'{e["min"]}–{e["max"]}',
        study_n=s["n"], study_median=s["median"], study_iqr=f'{s["q1"]}–{s["q3"]}'))
    # stratify by denom_class
    for dn in sorted({r["_denom"] for r in sub}):
        subd=[r for r in sub if r["_denom"]==dn]
        e,s,nst=dist_for(subd)
        if e["n"]==0: continue
        construct_rows.append(dict(construct=c, level=f"  └ {dn}", n_studies=nst,
            est_n=e["n"], est_median=e["median"], est_iqr=f'{e["q1"]}–{e["q3"]}', est_range=f'{e["min"]}–{e["max"]}',
            study_n=s["n"], study_median=s["median"], study_iqr=f'{s["q1"]}–{s["q3"]}'))

# ============================ 3. WHOLE-DIET BACKBONE =====================
whole = [r for r in rows if g(r,"construct") in ("EXPOSURE","REACH")
         and r["_denom"] in WHOLE_DIET_DENOM and g(r,"demographic_group")=="" ]
whole_tbl = [dict(id=g(r,"id"), construct=g(r,"construct"), denom=r["_denom"], country=g(r,"country_norm") or g(r,"country"),
                  platform=g(r,"platform_norm") or g(r,"platform"), value=r["_pct"], n=g(r,"n"),
                  measure=g(r,"measure_type")[:80]) for r in whole]
whole_tbl.sort(key=lambda x:(x["construct"], -(x["value"] or 0)))

# ============================ 4. CONCENTRATION ==========================
conc = [r for r in rows if g(r,"construct")=="CONCENTRATION"]
conc_tbl=[dict(id=g(r,"id"), country=g(r,"country_norm") or g(r,"country"), platform=g(r,"platform_norm") or g(r,"platform"),
               group=g(r,"conc_group_label") or g(r,"conc_group_pct"), share=g(r,"conc_share_pct") or (r["_pct"] and f'{r["_pct"]}%'),
               dim=g(r,"conc_dimension"), unit=g(r,"conc_unit"), quote=g(r,"source_quote")[:90]) for r in conc]

# ============================ 5. DIAGNOSTICS ============================
diag=[]  # dict(sev, kind, id, construct, detail)
def add(sev,kind,r,detail): diag.append(dict(sev=sev,kind=kind,id=g(r,"id") if r else "",
                                             construct=g(r,"construct") if r else "", detail=detail))

# (a) value_pct present but unparseable / out of range
for r in rows:
    v=g(r,"value_pct")
    if v and r["_pct"] is None:
        add("high","unparseable_value",r,f"value_pct={v!r} not numeric")
    if r["_pct"] is not None and not (0<=r["_pct"]<=100):
        add("high","value_out_of_range",r,f"value_pct={r['_pct']} outside [0,100]")

# (b) within-construct outliers (Tukey fence on estimate-level, prevalence constructs)
for c in PREV_CONSTRUCTS:
    vals=[r["_pct"] for r in rows if g(r,"construct")==c and r["_pct"] is not None]
    if len(vals)<8: continue
    q=st.quantiles(sorted(vals),n=4); iqr=q[2]-q[0]
    lo,hi=q[0]-1.5*iqr, q[2]+1.5*iqr
    for r in rows:
        if g(r,"construct")==c and r["_pct"] is not None and not(lo<=r["_pct"]<=hi):
            add("info","within_construct_outlier",r,f"{r['_pct']} vs {c} fence [{round(lo,1)},{round(hi,1)}] (denom={r['_denom']})")

# (c) construct x denom_class unusual combos
UNUSUAL={("CONTENT","population"),("CONTENT","all_media"),("EXPOSURE","topical"),
         ("EXPOSURE","single_source"),("REACH","topical"),("CONCENTRATION","topical")}
for r in rows:
    key=(g(r,"construct"), r["_denom"])
    if key in UNUSUAL:
        add("med","construct_denom_mismatch",r,f"{key[0]} coded with denom_class={key[1]} — verify")

# (d) thin cells that nonetheless produce a stratified median (construct x denom, n_est<3)
cell=defaultdict(list)
for r in rows:
    if g(r,"construct") in PREV_CONSTRUCTS and r["_pct"] is not None:
        cell[(g(r,"construct"),r["_denom"])].append(g(r,"id"))
for (c,dn),ids in sorted(cell.items()):
    if len(ids)<3:
        diag.append(dict(sev="info",kind="thin_cell",id=",".join(sorted(set(ids))),construct=c,
                         detail=f"{c}×{dn}: only {len(ids)} estimate(s) from {len(set(ids))} study(ies) — median unstable"))

# (e) FIELD COMPLETENESS — report as coverage stats, not per-row spam
def coverage(field):
    have=sum(1 for r in rows if g(r,field)); return have,len(rows)
for fld,sev in [("measure_type","med"),("misinfo_def","med"),("topic","info"),("n","info")]:
    have,tot=coverage(fld)
    if have<tot:
        # which studies are affected (for measure_type — a real backfill target)
        studs=sorted({g(r,'id') for r in rows if not g(r,fld)})
        ex=f" — {len(studs)} studies affected" + (f" (e.g. {', '.join(studs[:4])})" if fld=="measure_type" else "")
        diag.append(dict(sev=sev,kind="field_completeness",id="",construct="",
            detail=f"{fld}: populated on {have}/{tot} rows ({have/tot*100:.0f}%){ex}"))
# missing misinfo definition on a PREVALENCE row is still a per-row concern
for r in rows:
    if g(r,"construct") in PREV_CONSTRUCTS and not (g(r,"misinfo_def") or g(r,"definition")):
        add("med","missing_definition",r,"no misinfo definition on a prevalence row")

# (f) near-duplicate rows (same id+construct+value_pct+denom)
seen=defaultdict(list)
for i,r in enumerate(rows):
    if r["_pct"] is not None:
        seen[(g(r,"id"),g(r,"construct"),r["_pct"],r["_denom"])].append(i)
for k,idx in seen.items():
    if len(idx)>1:
        diag.append(dict(sev="med",kind="possible_duplicate",id=k[0],construct=k[1],
                         detail=f"{len(idx)} rows share value={k[2]} denom={k[3]} (rows {idx}) — verify not double-counted"))

diag.sort(key=lambda d:{"high":0,"med":1,"info":2}[d["sev"]])

# ============================ WRITE CSVs ===============================
OUT=ROOT/"data/synth/phaseB"; OUT.mkdir(parents=True, exist_ok=True)
def wcsv(name,rows_,cols):
    with open(OUT/name,"w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=cols); w.writeheader()
        for x in rows_: w.writerow({c:x.get(c,"") for c in cols})
wcsv("construct_distributions.csv",construct_rows,list(construct_rows[0].keys()))
wcsv("whole_diet.csv",whole_tbl,list(whole_tbl[0].keys()) if whole_tbl else ["id"])
wcsv("concentration.csv",conc_tbl,list(conc_tbl[0].keys()) if conc_tbl else ["id"])
wcsv("diagnostics.csv",diag,["sev","kind","id","construct","detail"])
with open(OUT/"corpus_counts.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["field","value","n"])
    for fld,cnt in corpus.items():
        for val,n in cnt.most_common(): w.writerow([fld,val,n])

# ============================ WRITE HTML ===============================
def tbl(headers, rowdicts, keys, rowclass=None):
    th="".join(f"<th>{esc(h)}</th>" for h in headers)
    body=""
    for x in rowdicts:
        cls=f' class="{rowclass(x)}"' if rowclass else ""
        body+=f"<tr{cls}>"+"".join(f"<td>{esc(x.get(k,'') if x.get(k,'') is not None else '')}</td>" for k in keys)+"</tr>"
    return f"<table><tr>{th}</tr>{body}</table>"

sevcount=Counter(d["sev"] for d in diag)
corpus_html=""
for fld,cnt in corpus.items():
    items=" · ".join(f"{esc(v)} <b>{n}</b>" for v,n in cnt.most_common())
    corpus_html+=f"<p class=cc><span class=k>{esc(fld)}</span> {items}</p>"

HTML=f"""<meta charset=utf-8><title>Phase B — descriptives & diagnostics</title>
<style>
 body{{font:14px/1.55 -apple-system,Segoe UI,Roboto,sans-serif;max-width:1150px;margin:22px auto;padding:0 16px;color:#181818}}
 h1{{font-size:23px}} h2{{margin-top:30px;border-bottom:2px solid #222;padding-bottom:4px}}
 h3{{margin:18px 0 6px;font-size:15px;color:#333}}
 .sub{{color:#666;margin:2px 0 12px}} .cc{{margin:3px 0}} .cc .k{{display:inline-block;min-width:150px;color:#036;font-weight:700}}
 table{{border-collapse:collapse;width:100%;font-size:12.5px;margin:8px 0}} th,td{{border:1px solid #e2e2e2;padding:5px 8px;text-align:left;vertical-align:top}}
 th{{background:#f4f4f4}} tr.strat td{{color:#555;background:#fafafa}} td:first-child{{white-space:nowrap}}
 .mono{{font-family:ui-monospace,Menlo,monospace}} .sid{{font-family:ui-monospace,monospace;font-weight:700}}
 .box{{border:1px solid #cbe0bd;background:#eef7ee;border-radius:6px;padding:8px 12px;margin:8px 0}}
 .warn{{border-color:#f0ccc0;background:#fff3f0}}
 tr.high td{{background:#fff0ee}} tr.med td{{background:#fff8ee}} tr.info td{{background:#fafafa}}
 .pill{{font-size:10px;font-weight:700;padding:1px 6px;border-radius:3px;color:#fff}}
 .p-high{{background:#c33}} .p-med{{background:#e08a00}} .p-info{{background:#888}}
.starthere{{background:#eef4fb;border:1px solid #cbd8e6;border-radius:6px;padding:10px 14px;margin:0 0 16px;font-size:14px}}
</style>
<h1>Phase B · Component 1 — descriptive backbone &amp; diagnostics</h1>
<div class="starthere"><b>Start here:</b> this is a component view. The narrative dashboard is <a href="phaseB_dashboard.html">phaseB_dashboard.html</a>; the interactive explorer is <a href="companion_dashboard.html">companion_dashboard.html</a>.</div>
<p class=sub>Source: <span class=mono>{esc(CSV.name)}</span> · {len(rows)} estimate rows · {len(STUDIES)} studies.
Read-only analysis of the frozen dataset — a Results foundation AND a QA lens. Nothing here changes the dataset.</p>
<div class="box {'warn' if sevcount['high'] else ''}">
 <b>Diagnostics summary:</b>
 <span class="pill p-high">{sevcount['high']} high</span>
 <span class="pill p-med">{sevcount['med']} medium</span>
 <span class="pill p-info">{sevcount['info']} info</span>
 — see the Diagnostics section at the bottom. "High" = must-check before headline; "info" = expected/benign, listed for transparency.
</div>

<h2>1 · Corpus composition</h2>
{corpus_html}

<h2>2 · Prevalence distributions by construct</h2>
<p class=sub>QUALITY &amp; OTHER excluded from prevalence. <b>Estimate-level</b> = every parsed % row; <b>study-level</b> = median-per-study
first, then across studies (avoids multi-estimate studies over-weighting a cell). "└ denom" rows stratify by denominator class —
the load-bearing moderator (topical/curated/single_source inflate; population/all_media are clean audience-diet designs).</p>
{tbl(["construct / denom","#studies","est n","est median","est IQR","est range","study n","study median","study IQR"],
     construct_rows,
     ["construct" if False else "level","n_studies","est_n","est_median","est_iqr","est_range","study_n","study_median","study_iqr"],
     rowclass=lambda x:"strat" if x["level"].startswith("  ") else "")}
<p class=sub>(first column shows construct on its "ALL denominators" line, then indented denominator strata)</p>

<h2>3 · Whole-diet backbone <span style="font-weight:400;color:#888">({len(whole_tbl)} estimates)</span></h2>
<p class=sub>The clean audience-diet-share designs: EXPOSURE/REACH with a population / all-media / political-news denominator
(not topical or curated). This small set is what actually measures "% of a real audience's information diet that was misinformation."</p>
{tbl(["study","construct","denom","country","platform","value %","n","measure"],whole_tbl,
     ["id","construct","denom","country","platform","value","n","measure"])}

<h2>4 · Concentration arm <span style="font-weight:400;color:#888">({len(conc_tbl)} estimates)</span></h2>
{tbl(["study","country","platform","group","share","dimension","unit","quote"],conc_tbl,
     ["id","country","platform","group","share","dim","unit","quote"])}

<h2>5 · Diagnostics <span style="font-weight:400;color:#888">({len(diag)} flags)</span></h2>
<p class=sub>Anomalies the analysis surfaces. Most are benign (info) and listed for transparency; check <b>high</b> and <b>medium</b> first.</p>
{tbl(["sev","kind","study","construct","detail"],
     [dict(sev=f'<span class="pill p-{d["sev"]}">{d["sev"]}</span>' if False else d["sev"],**{k:d[k] for k in ("kind","id","construct","detail")}) for d in diag],
     ["sev","kind","id","construct","detail"],
     rowclass=lambda x:x["sev"])}
"""
(ROOT/"docs/phaseB_descriptives.html").write_text(HTML)

print(f"read {CSV.name}: {len(rows)} rows / {len(STUDIES)} studies")
print(f"diagnostics: {sevcount['high']} high / {sevcount['med']} med / {sevcount['info']} info")
print(f"whole-diet backbone estimates: {len(whole_tbl)} | concentration: {len(conc_tbl)}")
print(f"wrote docs/phaseB_descriptives.html + data/synth/phaseB/*.csv")
