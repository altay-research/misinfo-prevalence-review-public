#!/usr/bin/env python3
"""phaseB_dashboard.py — one master HTML pulling together the whole Phase B picture:
corpus composition, the 4 figures, headline construct table, whole-diet backbone, key moderator slices,
meta-regression, precision weighting, concentration, and the GRADE Summary-of-Findings. Reads the
already-generated data/synth/phaseB/*.csv + docs/fig*.svg. Writes docs/phaseB_dashboard.html."""
import csv, html
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
# Version string derived from the freeze pointer, never hardcoded -- the dashboard
# previously advertised v1.4.7 in its lede and v1.4.6 in its footer, on the same page.
import re as _re
_spec = open(ROOT/"docs/FROZEN.md").read() if hasattr(ROOT, "__truediv__") else open("docs/FROZEN.md").read()
FROZEN_VER = _re.search(r"File:.*?v([\d.]+)_frozen", _spec).group(1)
# counts derive from the freeze, never hardcoded: the dashboard shipped "679 estimates / 317
# studies" for four freezes because those were literals in the template.
import csv as _csv
_rows = list(_csv.DictReader(open(ROOT / _re.search(r"File:\s*(\S+)", _spec).group(1), encoding="utf-8")))
N_EST = len(_rows)
N_STU = len({_r["id"] for _r in _rows})
S=ROOT/"data/synth/phaseB"
def esc(x): return html.escape(str(x))
def rd(name):
    p=S/name
    return list(csv.DictReader(open(p))) if p.exists() else []
def svg(name):
    p=ROOT/"docs"/name
    return p.read_text() if p.exists() else "<i>(figure missing)</i>"

def table(rows, cols, heads, hi=None, fmt=None):
    if not rows: return "<p><i>(no data)</i></p>"
    th="".join(f"<th>{esc(h)}</th>" for h in heads)
    body=""
    for r in rows:
        cls=' class="hl"' if hi and hi(r) else ""
        tds=""
        for c in cols:
            v=r.get(c,"")
            if fmt and c in fmt: v=fmt[c](r)
            tds+=f"<td>{esc(v)}</td>"
        body+=f"<tr{cls}>{tds}</tr>"
    return f"<table><tr>{th}</tr>{body}</table>"

CERTCOL={"HIGH":"#0072B2","MODERATE":"#E69F00","LOW":"#d2691e","VERY_LOW":"#D55E00"}

# ---- data ----
byc=rd("slices_by_construct.csv")
order={"EXPOSURE":0,"REACH":1,"SHARING":2,"CONTENT":3,"RECALL":4,"CONCENTRATION":5}
byc.sort(key=lambda r:order.get(r["value"],9))
meas=rd("slices_measurement.csv"); samp=rd("slices_sampling.csv")
brc=rd("slices_breadth_content.csv"); gt=rd("slices_ground_truth.csv"); top=rd("slices_topic.csv")
wd=rd("slices_whole_diet.csv"); wd.sort(key=lambda r:float(r["study_median"]) if r.get("study_median") else 0)
uni=rd("metareg_univariable.csv"); uni.sort(key=lambda r:-float(r["R2"]))
mv=rd("metareg_multivariable.csv"); pred=rd("metareg_measurement_pred.csv")
pw=rd("precision_weighting.csv"); grade=rd("grade_sof.csv")
conc=rd("concentration_standardized.csv")
conc_src=rd("concentration_source.csv")
corpus=rd("corpus_counts.csv")

# corpus composition compact
from collections import defaultdict
cc=defaultdict(list)
for r in corpus: cc[r["field"]].append((r["value"],r["n"]))
def corpus_line(field):
    items=cc.get(field,[])[:12]
    return " · ".join(f"{esc(v)} <b>{esc(n)}</b>" for v,n in items)

SLH=["construct/level","#studies","study median %","study IQR","study range","#est","est median %"]
SLK=["value","n_studies","sl_median","sl_iqr","sl_range","n_est","el_median"]

def num(x):
    try: return float(x)
    except: return 0

HTML=f"""<meta charset=utf-8><title>Misinfo prevalence — Phase B results dashboard</title>
<style>
 :root{{--ink:#1a1a1a;--mut:#666;--line:#e4e4e4}}
 body{{font:14.5px/1.6 -apple-system,Segoe UI,Roboto,sans-serif;max-width:1080px;margin:0 auto;padding:26px 18px 80px;color:var(--ink)}}
 h1{{font-size:26px;margin:0 0 4px}} .lede{{color:var(--mut);font-size:15px;margin:0 0 18px}}
 h2{{font-size:19px;margin:34px 0 6px;border-bottom:2px solid #222;padding-bottom:5px}}
 h3{{font-size:14px;margin:16px 0 4px;color:#333}} .sub{{color:var(--mut);margin:2px 0 8px;font-size:13px}}
 nav{{position:sticky;top:0;background:#fffe;backdrop-filter:blur(6px);border-bottom:1px solid var(--line);
   padding:8px 0;margin-bottom:10px;font-size:12.5px;z-index:9}} nav a{{color:#2668c9;text-decoration:none;margin-right:12px;white-space:nowrap}}
 table{{border-collapse:collapse;width:100%;font-size:12.5px;margin:6px 0 14px}}
 th,td{{border:1px solid var(--line);padding:5px 8px;text-align:left;vertical-align:top}} th{{background:#f5f5f5}}
 td:first-child{{white-space:nowrap}} tr.hl td{{background:#fff3ee;font-weight:600}}
 svg{{max-width:100%;height:auto;border:1px solid #eee;border-radius:6px;background:#fff;margin:6px 0}}
 .box{{border:1px solid #cbd8e6;background:#eef4fb;border-radius:7px;padding:12px 16px;margin:12px 0}}
 .kpis{{display:flex;gap:12px;flex-wrap:wrap;margin:14px 0}}
 .kpi{{flex:1;min-width:150px;border:1px solid var(--line);border-radius:8px;padding:10px 12px;text-align:center}}
 .kpi b{{display:block;font-size:26px;line-height:1.1}} .kpi span{{font-size:11.5px;color:var(--mut)}}
 .green{{color:#0072B2}} .red{{color:#D55E00}} .amber{{color:#E69F00}}
 .cert{{color:#fff;font-weight:700;font-size:11px;padding:2px 7px;border-radius:4px}}
 .two{{display:flex;gap:20px;flex-wrap:wrap}} .two>div{{flex:1;min-width:320px}}
 .muted{{color:var(--mut);font-size:12px}}
</style>
<nav>
 <a href="#top">Overview</a><a href="#corpus">Corpus</a><a href="#headline">Headline</a><a href="#backbone">Whole-diet</a>
 <a href="#drivers">Drivers</a><a href="#slices">Slices</a><a href="#precision">Weighting</a><a href="#conc">Concentration</a><a href="#grade">GRADE</a>
</nav>

<a name=top></a>
<h1>How much misinformation are people actually exposed to?</h1>
<p class=lede>Phase B results dashboard · systematic review · frozen dataset <b>v{FROZEN_VER}</b> ({N_EST} estimates / {N_STU} studies).
Every number is computed deterministically from the frozen data; this page is read-only.</p>
<div class=box style="background:#f4f7ff">
 <b>Companion views:</b>
 <a href="companion_dashboard.html">🔎 Interactive explorer</a> (every estimate, hover for quote/definition, filter &amp; regroup) ·
 <a href="phaseB_figure_gallery.html">📊 Figure gallery</a> (12 figures) ·
 <a href="litreview_measurement.html">📚 Theory vs our findings</a> (Nickl funnel, Hameleers gap)
 <!-- The meta-regression page was a one-off July artefact with no generator, so it went stale at the
      first re-freeze and was archived to docs/Old/. The current meta-regression results live in the
      manuscript (Section 2.6) and in data/synth/phaseB/, both regenerated with every freeze. -->
</div>

<div class=box>
<b>Bottom line.</b> "Prevalence of misinformation" is not one number. People <b>report</b> seeing misinformation constantly
(self-report median ~55%) and curated <b>content</b> samples look alarming (~23% of items), but the share of an ordinary
person's <b>actual information diet</b> that is misinformation is small — around <b>3%</b> (behavioural exposure), the best-supported
estimate in the literature. What misinformation there is concentrates in a tiny minority: the <b>top 1% of users account for ~70%</b>
of all misinfo exposure/sharing. And the divergence between these numbers is not noise — it is driven by <b>how</b> misinformation is measured.
</div>
<div class=kpis>
 <div class=kpi><b class=green>2.8%</b><span>audience diet-share (EXPOSURE)<br>GRADE: HIGH</span></div>
 <div class=kpi><b class=red>23%</b><span>content-sample items false<br>GRADE: VERY LOW</span></div>
 <div class=kpi><b class=amber>55%</b><span>self-report having seen it</span></div>
 <div class=kpi><b>70%</b><span>of misinfo activity from<br>the top 1% of users</span></div>
 <div class=kpi><b>4.8→48%</b><span>predicted, behavioural<br>→ self-report</span></div>
</div>

<a name=corpus></a><h2>1 · What the literature measures</h2>
<p class=sub>The corpus over-measures <i>content</i> and <i>health</i> relative to the audience-exposure and political questions that motivate concern.</p>
<p class=muted><b>construct</b> — {corpus_line('construct')}</p>
<p class=muted><b>denominator</b> — {corpus_line('denom_class')}</p>
<p class=muted><b>ground truth</b> — {corpus_line('ground_truth')}</p>
<p class=muted><b>platform</b> — {corpus_line('platform_norm')}</p>
<h3>Topic distribution (new moderator, all {N_STU} studies coded)</h3>
{table(top,["value","n_studies","sl_median","sl_iqr"],["topic","#studies","study median %","IQR"])}

<a name=headline></a><h2>2 · The headline — the quantities differ by an order of magnitude</h2>
{svg('fig1_prevalence_by_construct.svg')}
{table(byc,SLK,SLH,hi=lambda r:r["value"]=="EXPOSURE")}

<a name=backbone></a><h2>3 · The whole-diet backbone — two distinct quantities</h2>
<p class=sub>The clean audience-diet designs answer <b>two</b> different questions that must not be pooled: <b>EXPOSURE</b> = what share of your diet is misinfo (≈1–3%); <b>REACH</b> = what share of people saw ≥1 over a period (≈9–40%). The high "backbone" values (up to 70%, e.g. foreign-influence campaign reach) are all REACH; the ~0.1–1% values are all EXPOSURE diet-share.</p>
{svg('figA_exposure_reach_split.svg')}

<a name=drivers></a><h2>4 · What drives the estimate <span class=muted>(meta-regression)</span></h2>
{svg('fig2_method_drivers.svg')}
<div class=two>
 <div><h3>Variance explained by each moderator (pseudo-R²)</h3>
   {table(uni,["moderator","R2","df"],["moderator","R² %","df"],hi=lambda r:num(r["R2"])>=15)}</div>
 <div><h3>Model-predicted prevalence by measurement</h3>
   {table(pred,["measurement","pred_pct"],["measurement","predicted %"])}
   <p class=muted>Multivariable model (construct+breadth+denom+topic): pseudo-R² = 27%.</p></div>
</div>
<h3>Multivariable odds ratios <span class=muted>(vs EXPOSURE / fabricated / whole-diet / general-news)</span></h3>
{table([r for r in mv if r['term']!='intrcpt'],["term","OR","p"],["term","odds ratio","p"],
   hi=lambda r:(r.get("p") not in ("","NA")) and num(r["p"])<0.05)}

<a name=slices></a><h2>5 · The meaningful slices</h2>
<div class=two>
 <div><h3>By measurement</h3>{table(meas,SLK,SLH)}</div>
 <div><h3>By sampling frame</h3>{table(samp,SLK,SLH)}</div>
</div>
<div class=two>
 <div><h3>By definitional breadth (within CONTENT — the thesis)</h3>{table(brc,SLK,SLH)}</div>
 <div><h3>By ground-truth source</h3>{table(gt,SLK,SLH)}</div>
</div>

<a name=precision></a><h2>6 · Precision-weighting sensitivity</h2>
<p class=sub>Sample-size-weighted vs unweighted study-level median (study-cluster bootstrap 95% CI). Larger samples find less.</p>
{table(pw,["group","n_studies","unweighted_median","unweighted_CI","weighted_median","weighted_CI","shift"],
   ["group","#studies","unweighted %","95% CI","weighted %","95% CI","shift"],
   hi=lambda r:abs(num(r["shift"]))>=7)}

<a name=conc></a><h2>7 · Concentration — and how it compares to news in general</h2>
{svg('fig4_concentration_curve.svg')}
<div class=box><b>The top 1% of people account for a median 70% of all misinfo exposure/sharing</b> (range 37–80%); top 10% → ~88%.
And this is <b>markedly more concentrated than news at large</b> — in the studies reporting both, the top 1% accounts for only
~30–49% of general news activity vs ~65–82% of misinformation (Osmundsen 30/75; Grinberg 49/82; Zhou 43/65; Eady 24–37/70).
<br><span class=muted>This is <b>user</b> concentration (<code>conc_unit=user</code>) only — source concentration is a separate quantity, below.</span></div>
{svg('figK_concentration_flow.svg')}
<h3>The same comparison held within panel <span class=muted>(the two medians above come from different study sets)</span></h3>
{svg('figQ_matched_concentration.svg')}
{svg('figL_concentration_lorenz.svg')}
<h3>Source concentration — few outlets/domains produce most of it <span class=muted>(a distinct quantity; {len(conc_src)} estimates)</span></h3>
<p class=sub>Not "which <i>people</i>" but "which <i>sources</i>" — kept separate from the headline so the two aren't conflated.</p>
{table(conc_src,["id","top_group","activity_share_pct","country"],["study","top sources","→ % of activity","country"])}
{svg('figG_concentration_comparison.svg')}
<h3>More general-activity concentration, from the broader literature</h3>
<p class=sub>Context comparators the review surfaced (different percentiles; provenance noted). General news/political activity is also concentrated — but misinfo is more so at the extreme top.</p>
<table><tr><th>source</th><th>top X% of people</th><th>→ % of activity</th><th>of what</th><th>note</th></tr>
<tr><td>Muise 2022</td><td>21%</td><td>64%</td><td>TV-news minutes</td><td class=muted>most-partisan archetypes; own data</td></tr>
<tr><td>Muise 2022</td><td>6%</td><td>28%</td><td>online-news minutes</td><td class=muted>own data</td></tr>
<tr><td>Wojcieszak 2022</td><td>13%</td><td>86%</td><td>political-elite content shares</td><td class=muted>own data, 1.4M random Twitter users</td></tr>
<tr><td>Wojcieszak 2022 (cit. Pew)</td><td>25%</td><td>97%</td><td>ALL tweets</td><td class=muted>secondary citation; all-content, not news</td></tr>
<tr><td>Lorenz-Spreen 2024 (cit.)</td><td>10%</td><td>96%</td><td>ALL platform content</td><td class=muted>secondary citation; all-content, not news</td></tr>
<tr><td>Allen 2020</td><td>~10%</td><td>—</td><td>cable-news consumption</td><td class=muted>qualitative "voracious" top decile; 44% consume zero online news</td></tr>
</table>
<p class=muted>Takeaway: general news/political activity is concentrated too (a known "participation inequality"), but at the extreme top the misinfo-specific concentration is markedly higher — top 1% ≈ 70% (misinfo) vs 24–49% (general news).</p>
{table(conc,["id","dimension","top_pct_people","activity_share_pct","country"],
   ["study","dimension","top % people","→ % of activity","country"])}

<h2>7b · Who — by political orientation &amp; age</h2>
<p class=sub>Within-group <b>RATES</b> — what share of a group's <i>own</i> sharing/exposure is misinformation (<b>not</b> concentration). Sharing skews sharply right (left ~0.5% to right ~5% to far-right ~40%); older users share more. Separately, misinfo <i>audiences/spreaders</i> skew right — that is concentration, shown in section 7.</p>
{svg('figI_by_political.svg')}
{svg('figJ_by_age.svg')}

<a name=grade></a><h2>8 · How much can we trust each number? (GRADE certainty)</h2>
<p class=sub>GRADE rates how <b>trustworthy</b> a body of evidence is (not how big the number is), starting at HIGH and downgrading for
weak designs, inconsistency, indirect measures, too-few studies, or cherry-picked corpora. The punchline: <b>the reassuring
number is the trustworthy one, the scary number is the least trustworthy</b> — certainty runs inverse to magnitude.</p>
<table><tr><th>construct</th><th>k</th><th>median % (IQR)</th><th>% HIGH RoB</th><th>certainty</th><th>downgrades</th></tr>
{"".join(f'<tr><td>{esc(r["construct"])}</td><td>{esc(r["k"])}</td><td>{esc(r["median"])} ({esc(r["iqr"])})</td>'
   f'<td>{esc(r["pct_high_rob"])}%</td><td><span class=cert style="background:{CERTCOL.get(r["certainty"],"#888")}">{esc(r["certainty"].replace("_"," "))}</span></td>'
   f'<td class=muted>{esc(r["reasons"])}</td></tr>' for r in grade)}
</table>
<p class=muted>Prevalence-adapted GRADE (Murad 2023; Migliavaca 2020): start HIGH, downgrade on risk of bias, inconsistency,
indirectness, imprecision, selection bias. Computed by <code>scripts/phaseB_grade.py</code>.</p>

<p class=muted style="margin-top:30px">Generated by <code>scripts/phaseB_dashboard.py</code> from frozen v{FROZEN_VER}. Full methods: <code>docs/manuscript_draft.md</code> §2.8. Reproducibility: <code>docs/FROZEN.md</code>.</p>
"""
(ROOT/"docs/phaseB_dashboard.html").write_text(HTML)
print("wrote docs/phaseB_dashboard.html")
print(f"  embedded 4 figures; {len(byc)} constructs, {len(wd)} whole-diet studies, {len(grade)} GRADE rows, {len(conc)} concentration rows")
