#!/usr/bin/env python3
"""build_companion_dashboard.py — the interactive companion to the paper. Embeds every estimate
(data/synth/phaseB/estimates_full.json) into a self-contained HTML with a vanilla-JS explorer:
strip/beeswarm plot of all estimates, grouped/colored by any moderator, hover for provenance
(quote, definition, category, measure, RoB, n), and live filters by construct/definition/topic/etc.
No external libraries (CSP-safe). Writes docs/companion_dashboard.html."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=json.load(open(ROOT/"data/synth/phaseB/estimates_full.json"))
# keep payload lean: round + trim
for d in DATA:
    if d.get("quote"): d["quote"]=d["quote"][:400]
    if d.get("definition"): d["definition"]=d["definition"][:400]
    if d.get("measure_type"): d["measure_type"]=d["measure_type"][:200]
payload=json.dumps(DATA, ensure_ascii=False, separators=(",",":"))

HTML=r"""<meta charset="utf-8"><title>Misinformation prevalence — interactive companion</title>
<style>
:root{--ink:#1b1b1b;--mut:#6a6a6a;--line:#e5e5e5;--bg:#fff;--accent:#2563c9}
*{box-sizing:border-box}
body{margin:0;font:13.5px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;color:var(--ink);background:#fafafa}
header{padding:14px 20px;background:#fff;border-bottom:1px solid var(--line)}
header h1{margin:0;font-size:19px} header p{margin:3px 0 0;color:var(--mut);font-size:12.5px}
.wrap{display:flex;gap:0;align-items:stretch;min-height:calc(100vh - 58px)}
.side{width:250px;flex:none;background:#fff;border-right:1px solid var(--line);padding:12px 14px;overflow-y:auto;max-height:calc(100vh - 58px);position:sticky;top:0}
.main{flex:1;padding:14px 18px;overflow-x:auto}
.grp{margin-bottom:14px} .grp h4{margin:0 0 5px;font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:#888}
select,button{font:inherit;padding:4px 6px;border:1px solid var(--line);border-radius:5px;background:#fff;width:100%}
label.ck{display:flex;align-items:center;gap:5px;font-size:12px;padding:1px 0;cursor:pointer;color:#333}
label.ck input{margin:0}
.chipbar{display:flex;flex-wrap:wrap;gap:4px;margin-top:3px}
.pill{font-size:10.5px;padding:1px 6px;border-radius:9px;background:#eef;color:#224;cursor:pointer;border:1px solid #dde}
.pill.off{background:#f4f4f4;color:#aaa;border-color:#eee;text-decoration:line-through}
.kpis{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px}
.kpi{border:1px solid var(--line);border-radius:7px;padding:6px 11px;background:#fff}
.kpi b{font-size:19px} .kpi span{font-size:10.5px;color:var(--mut);display:block}
svg{background:#fff;border:1px solid var(--line);border-radius:8px;width:100%}
.row-lab{font-size:11.5px;fill:#333} .med{font-weight:700}
#tip{position:fixed;pointer-events:none;max-width:360px;background:#0f141b;color:#eef2f6;padding:11px 13px;border-radius:8px;
 font-size:12px;line-height:1.5;opacity:0;transition:opacity .08s;z-index:99;box-shadow:0 6px 22px #0007;border:1px solid #2a3542}
#tip b{color:#8fb8ff} #tip .q{color:#c7d0da;font-style:italic;margin-top:5px;display:block}
#tip .denom{color:#ffd08a;margin-top:4px;display:block;font-size:11.5px}
#tip .tag{display:inline-block;background:#243244;color:#d7e2ee;border-radius:4px;padding:1px 6px;margin:2px 3px 0 0;font-size:11px}
#tip .tag b{color:#fff}
.toolbar{display:flex;gap:10px;flex-wrap:wrap;align-items:end;margin-bottom:10px}
.toolbar .f{display:flex;flex-direction:column;gap:2px;font-size:11px;color:#888}
.toolbar select{width:auto;min-width:120px}
.cap{background:#f6f8fc;border:1px solid #e2e8f2;border-radius:7px;padding:8px 12px;margin:6px 0;font-size:13px;color:#333}
.cap b{color:#111}
.legend{display:flex;flex-wrap:wrap;gap:9px;margin:6px 0 2px;font-size:11px}
.legend span{display:inline-flex;align-items:center;gap:4px} .sw{width:11px;height:11px;border-radius:3px;display:inline-block}
small.note{color:var(--mut)} a{color:var(--accent)}
button.act{background:var(--accent);color:#fff;border-color:var(--accent);cursor:pointer;width:auto;padding:4px 10px}
</style>
<header>
 <h1>How much misinformation are people exposed to? — interactive companion</h1>
 <p>Every estimate in the review. <b>Hover a point</b> for its article, quote, definition &amp; coding; <b>use the left panel</b> to filter; <b>"group by" / "colour by"</b> to re-slice. <span id="count"></span></p>
 <p style="font-size:11.5px;color:#888;margin:4px 0 0">The six quantities the word "prevalence" conflates —
  <b>EXPOSURE</b>: % of a person's information diet that's misinfo ·
  <b>REACH</b>: % of people who saw ≥1 ·
  <b>RECALL</b>: % who <i>say</i> they saw it ·
  <b>SHARING</b>: observed sharing/engagement ·
  <b>CONTENT</b>: % of items in a sample that are false ·
  <b>CONCENTRATION</b>: % of activity from the top users. They differ ~10×, so slice within a construct, don't pool.</p>
</header>
<div class="wrap">
 <div class="side" id="filters"></div>
 <div class="main">
  <div class="toolbar">
   <div class="f">group rows by<select id="groupby"></select></div>
   <div class="f">colour by<select id="colorby"></select></div>
   <div class="f">x-axis<select id="xscale"><option value="lin">linear %</option><option value="log">log %</option></select></div>
   <div class="f">show<select id="mainonly"><option value="1">main-analysis set</option><option value="0">all estimates</option></select></div>
   <button class="act" id="reset">reset view</button>
   <button class="act" id="dl" style="background:#555;border-color:#555">⬇ CSV</button>
  </div>
  <div class="kpis" id="kpis"></div>
  <div class="cap" id="caption"></div>
  <div class="legend" id="legend"></div>
  <svg id="plot"></svg>
  <p><small class="note">Each dot = one estimate · horizontal position = the reported % · <b>diamond</b> = group median · bar = middle-50% (IQR) · dot size ∝ log(sample size). Hover for the article &amp; quote; click to pin. Main-analysis set = general public, a proportion, not within-misinfo composition.</small></p>
 </div>
</div>
<div id="tip"></div>
<script>
const DATA=__PAYLOAD__;
const CATFIELDS=["construct","topic","measurement","denom_class","denom2","breadth","ground_truth","id_method","sampling","platform","country_scope","rob"];
const LABEL={construct:"Construct",topic:"Topic",measurement:"Measurement",denom_class:"Denominator",denom2:"Denominator (2-way)",breadth:"Definitional breadth",ground_truth:"Ground truth",id_method:"Identification method",sampling:"Sampling frame",platform:"Platform",country_scope:"Country scope",rob:"Risk of bias"};
const PALETTE=["#2563c9","#c0392b","#178a3f","#e0902a","#7a3fc0","#0891b2","#be185d","#65a30d","#9a3412","#475569","#db2777","#0d9488","#a16207","#4f46e5"];
const CONSTRUCT_ORDER=["EXPOSURE","REACH","RECALL","SHARING","CONTENT","CONCENTRATION","QUALITY","OTHER"];
let state={groupby:"construct",colorby:"measurement",xscale:"lin",mainonly:"1",filters:{},pinned:null};

// ---- build filter UI ----
function uniq(f){return [...new Set(DATA.map(d=>d[f]).filter(x=>x!==""&&x!=null))].sort();}
function buildFilters(){
 const el=document.getElementById("filters"); el.innerHTML="";
 for(const f of CATFIELDS){
  const vals=uniq(f); if(vals.length<2)continue;
  state.filters[f]=state.filters[f]||new Set(vals);
  const g=document.createElement("div"); g.className="grp";
  g.innerHTML=`<h4>${LABEL[f]}</h4>`;
  const bar=document.createElement("div"); bar.className="chipbar";
  for(const v of vals){
   const p=document.createElement("span"); p.className="pill"+(state.filters[f].has(v)?"":" off");
   p.textContent=v; p.onclick=()=>{ state.filters[f].has(v)?state.filters[f].delete(v):state.filters[f].add(v); p.classList.toggle("off"); render(); };
   bar.appendChild(p);
  }
  g.appendChild(bar); el.appendChild(g);
 }
}
function fillSelect(id,sel){const s=document.getElementById(id);s.innerHTML="";for(const f of CATFIELDS){const o=document.createElement("option");o.value=f;o.textContent=LABEL[f];if(f===sel)o.selected=true;s.appendChild(o);}}

function activeData(){
 return DATA.filter(d=>{
  if(state.mainonly==="1"&&!d.main)return false;
  if(d.value==null)return false;
  for(const f of CATFIELDS){ if(state.filters[f]&&!state.filters[f].has(d[f])&&d[f]!=="") if(!state.filters[f].has(d[f]))return false; }
  return true;
 });
}
function median(a){if(!a.length)return null;const s=[...a].sort((x,y)=>x-y);const m=s.length>>1;return s.length%2?s[m]:(s[m-1]+s[m])/2;}
function quantile(a,q){if(a.length<4)return null;const s=[...a].sort((x,y)=>x-y);const p=(s.length-1)*q,b=Math.floor(p);return s[b]+(s[b+1]-s[b])*(p-b);}

let colorScale={};
function computeColors(cb){colorScale={};const vals=uniq(cb);vals.forEach((v,i)=>colorScale[v]=PALETTE[i%PALETTE.length]);}

function render(){
 const cb=state.colorby; computeColors(cb);
 const data=activeData();
 document.getElementById("count").textContent=`— ${data.length} estimates shown, ${new Set(data.map(d=>d.id)).size} studies`;
 // group
 const gb=state.groupby; const groups={};
 for(const d of data){(groups[d[gb]]=groups[d[gb]]||[]).push(d);}
 let gkeys=Object.keys(groups);
 gkeys.sort((a,b)=>{ if(gb==="construct"){return CONSTRUCT_ORDER.indexOf(a)-CONSTRUCT_ORDER.indexOf(b);}
   return (median(groups[b].map(d=>d.value))||0)-(median(groups[a].map(d=>d.value))||0);});
 // dynamic caption
 const topg=gkeys.slice(0,3).map(k=>`${k||"(blank)"} ${(median(groups[k].map(d=>d.value))||0).toFixed(1)}%`).join(" · ");
 const filt=CATFIELDS.filter(f=>state.filters[f]&&state.filters[f].size<uniq(f).length).map(f=>LABEL[f]);
 document.getElementById("caption").innerHTML=
   `Showing <b>${data.length}</b> estimates from <b>${new Set(data.map(d=>d.id)).size}</b> studies, grouped by <b>${LABEL[gb]}</b>, coloured by <b>${LABEL[cb]}</b>.`+
   ` Highest-median rows: <b>${topg}</b>.`+
   (filt.length?` <span style="color:#a30">Filtered by: ${filt.join(", ")}.</span>`:` No filters active.`);
 // kpis (overall + a couple constructs)
 const kpi=document.getElementById("kpis"); kpi.innerHTML="";
 const expo=data.filter(d=>d.construct==="EXPOSURE").map(d=>d.value);
 const cont=data.filter(d=>d.construct==="CONTENT").map(d=>d.value);
 const rec=data.filter(d=>d.construct==="RECALL").map(d=>d.value);
 const mk=(lab,v,c)=>`<div class="kpi"><b style="color:${c}">${v==null?"–":v.toFixed(1)+"%"}</b><span>${lab}</span></div>`;
 kpi.innerHTML=mk("EXPOSURE median",median(expo),"#178a3f")+mk("CONTENT median",median(cont),"#c0392b")+mk("RECALL median",median(rec),"#e0902a")+mk("all shown (median)",median(data.map(d=>d.value)),"#333");
 // legend
 const lg=document.getElementById("legend"); lg.innerHTML=`<b style="color:#888;font-weight:600">colour = ${LABEL[cb]}:</b> `+
   Object.entries(colorScale).map(([k,c])=>`<span><i class="sw" style="background:${c}"></i>${k||"(blank)"}</span>`).join("");
 // layout
 const svg=document.getElementById("plot");
 const W=svg.clientWidth||900, padL=150, padR=30, padT=14, rowH=Math.max(34,Math.min(64,(560/gkeys.length)));
 const H=padT+gkeys.length*rowH+34; svg.setAttribute("viewBox",`0 0 ${W} ${H}`); svg.setAttribute("height",H);
 const log=state.xscale==="log";
 const allv=data.map(d=>d.value);
 const xmaxRaw=Math.max(...allv,1); const xmin=log?0.01:0;
 const X=v=>{ if(log){const lv=Math.log10(Math.max(v,0.01)),l0=Math.log10(0.01),l1=Math.log10(Math.max(xmaxRaw,10));return padL+(lv-l0)/(l1-l0)*(W-padL-padR);}
   return padL+(v/Math.max(xmaxRaw,1))*(W-padL-padR);};
 let s=`<g font-family="inherit">`;
 // x gridlines
 const ticks=log?[0.01,0.1,1,10,100]:[0,20,40,60,80,100].filter(t=>t<=xmaxRaw+5);
 for(const t of ticks){const x=X(t);s+=`<line x1="${x}" y1="${padT}" x2="${x}" y2="${H-28}" stroke="#f0f0f0"/><text x="${x}" y="${H-14}" font-size="10" text-anchor="middle" fill="#aaa">${t}%</text>`;}
 s+=`<text x="${padL+(W-padL-padR)/2}" y="${H-1}" font-size="11" text-anchor="middle" fill="#888">reported prevalence / share (%)</text>`;
 gkeys.forEach((k,gi)=>{
  const yc=padT+gi*rowH+rowH/2; const arr=groups[k]; const vals=arr.map(d=>d.value);
  const med=median(vals),q1=quantile(vals,.25),q3=quantile(vals,.75);
  s+=`<text x="${padL-8}" y="${yc+4}" text-anchor="end" class="row-lab">${k||"(blank)"} <tspan fill="#bbb">n${arr.length}</tspan></text>`;
  s+=`<line x1="${padL}" y1="${yc}" x2="${W-padR}" y2="${yc}" stroke="#f7f7f7"/>`;
  if(q1!=null){s+=`<line x1="${X(q1)}" y1="${yc}" x2="${X(q3)}" y2="${yc}" stroke="#c9d6e8" stroke-width="7"/>`;}
  // points with vertical jitter
  arr.forEach((d,i)=>{
   const jitter=((i*2654435761)%1000/1000-0.5)*(rowH-14);
   const r=d.n?Math.max(2.2,Math.min(7,1.6+Math.log10(d.n)*0.9)):3;
   s+=`<circle cx="${X(d.value)}" cy="${yc+jitter}" r="${r}" fill="${colorScale[d[cb]]||'#999'}" fill-opacity="0.72" stroke="#fff" stroke-width="0.5" data-i="${DATA.indexOf(d)}" class="pt"/>`;
  });
  if(med!=null){s+=`<path d="M${X(med)},${yc-8} L${X(med)+7},${yc} L${X(med)},${yc+8} L${X(med)-7},${yc} Z" fill="#111"/>`;
   s+=`<text x="${X(med)}" y="${yc-11}" font-size="10.5" text-anchor="middle" class="med">${med.toFixed(1)}%</text>`;}
 });
 s+=`</g>`; svg.innerHTML=s;
 // events
 svg.querySelectorAll(".pt").forEach(c=>{
  c.addEventListener("mousemove",e=>showTip(e,DATA[+c.dataset.i]));
  c.addEventListener("mouseleave",()=>{if(!state.pinned)hideTip();});
  c.addEventListener("click",()=>{state.pinned=DATA[+c.dataset.i];showTipFixed(DATA[+c.dataset.i]);});
 });
 svg.addEventListener("click",e=>{if(e.target.tagName!=="circle"){state.pinned=null;hideTip();}});
}
function tipHTML(d){
 const tag=(l,v)=>v?`<span class="tag">${l} <b>${v}</b></span>`:"";
 return `<b style="color:#fff;font-size:13px">${d.title||d.id}</b>
  <div style="color:#8fb8ff;margin:3px 0 5px"><b style="font-size:17px">${d.value!=null?d.value+"%":d.value_raw}</b> · ${d.construct} · <span style="color:#7a8899">${d.id}</span></div>
  ${d.measure_type?`<div style="margin:0 0 4px;color:#bfe3d0">📏 <b style="color:#dff5e8">what it measures:</b> ${d.measure_type}</div>`:""}
  ${d.denominator?`<span class="denom">➗ out of (denominator): ${d.denominator}</span>`:""}
  <div style="margin-top:5px">${tag("topic",d.topic)}${tag("breadth",d.breadth)}${tag("how identified",d.id_method)}${tag("ground truth",d.ground_truth)}${tag("sampling",d.sampling)}${tag("measure",d.measurement)}${tag("platform",d.platform)}${tag("country",d.country)}${tag("n",d.n_raw)}${tag("RoB",d.rob)}</div>
  ${d.quote?`<span class="q">💬 "${d.quote}"</span>`:""}
  ${d.definition?`<span class="q" style="color:#a9b4c0">misinfo defined as: ${d.definition}</span>`:""}`;
}
const tip=document.getElementById("tip");
function showTip(e,d){tip.innerHTML=tipHTML(d);tip.style.opacity=1;let x=e.clientX+14,y=e.clientY+14;
 if(x+350>innerWidth)x=e.clientX-354;if(y+220>innerHeight)y=innerHeight-230;tip.style.left=x+"px";tip.style.top=y+"px";}
function showTipFixed(d){tip.innerHTML=tipHTML(d)+`<div style="margin-top:5px;color:#9ab"><i>pinned — click empty space to close</i></div>`;tip.style.opacity=1;}
function hideTip(){tip.style.opacity=0;}

document.getElementById("groupby").onchange=e=>{state.groupby=e.target.value;render();};
document.getElementById("colorby").onchange=e=>{state.colorby=e.target.value;render();};
document.getElementById("xscale").onchange=e=>{state.xscale=e.target.value;render();};
document.getElementById("mainonly").onchange=e=>{state.mainonly=e.target.value;render();};
document.getElementById("reset").onclick=()=>{state.filters={};state.groupby="construct";state.colorby="measurement";state.mainonly="1";state.xscale="lin";document.getElementById("groupby").value="construct";document.getElementById("colorby").value="measurement";document.getElementById("mainonly").value="1";document.getElementById("xscale").value="lin";buildFilters();render();};
document.getElementById("dl").onclick=()=>{
 const cols=["id","title","value","construct","topic","breadth","id_method","ground_truth","sampling","measurement","platform","country","n_raw","rob","quote"];
 const esc=v=>'"'+String(v==null?"":v).replace(/"/g,'""')+'"';
 const lines=[cols.join(",")].concat(activeData().map(d=>cols.map(c=>esc(d[c])).join(",")));
 const blob=new Blob([lines.join("\n")],{type:"text/csv"});const a=document.createElement("a");
 a.href=URL.createObjectURL(blob);a.download="misinfo_estimates_filtered.csv";a.click();};
fillSelect("groupby","construct");fillSelect("colorby","measurement");
buildFilters();render();
window.addEventListener("resize",render);
</script>
"""
html=HTML.replace("__PAYLOAD__",payload)
(ROOT/"docs/companion_dashboard.html").write_text(html)
print(f"wrote docs/companion_dashboard.html ({len(html)//1024} KB, {len(DATA)} estimates embedded)")
