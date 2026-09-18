#!/usr/bin/env python3
"""phaseB_export_json.py — export EVERY estimate as a clean JSON record for the interactive companion
dashboard: value, all moderators, the new misinfo-identification method, RoB, topic, and full provenance
(source quote, misinfo definition, measure). Reads frozen v1.4.6. Writes data/synth/phaseB/estimates_full.json."""
import csv, re, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CSV=ROOT/re.search(r'File:\s*(\S+)',(ROOT/"docs/FROZEN.md").read_text()).group(1)
rows=list(csv.DictReader(open(CSV)))
def g(r,k): return (r.get(k) or "").strip()
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
TITLES=json.load(open(ROOT/"data/synth/phaseB/titles.json")) if (ROOT/"data/synth/phaseB/titles.json").exists() else {}

def pctf(r):
    v=g(r,"value_pct")
    try: return round(float(v),3) if v else None
    except: return None
def parse_n(s):
    s=s.replace(",","")
    m=re.search(r'(\d+\.?\d*)\s*([KkMm])?',s)
    if not m: return None
    v=float(m.group(1))*{"k":1e3,"m":1e6}.get((m.group(2) or "").lower(),1)
    return int(v) if v>=1 else None

def id_method(r):
    """How misinfo was IDENTIFIED — the domain-list vs URL/claim vs classifier distinction."""
    gtx=g(r,"ground_truth").lower(); cl=g(r,"classification_level"); unit=g(r,"unit")
    if "self" in gtx and "report" in gtx or "perceived" in gtx or cl=="self_perceived": return "self-report"
    if "classifier" in gtx or "gpt" in gtx or "hybrid" in gtx or "auto" in gtx: return "classifier/LLM"
    if cl=="source_level" or "newsguard" in gtx or "domain" in gtx: return "domain/source list"
    if "fact" in gtx and "check" in gtx: return "fact-check (claim/URL)"
    if "researcher" in gtx or "hand" in gtx or "coder" in gtx or "coded" in gtx or "human" in gtx: return "researcher content-coding"
    return "other/unspecified"
def measurement(r): return MEASUREMENT_BY_CONSTRUCT.get(g(r,"construct").upper(), "NA")
def canon_gt(r):
    x=g(r,"ground_truth").lower()
    if not x: return "unspecified"
    if "newsguard" in x: return "NewsGuard"
    if "domain" in x or "low-cred" in x or "low credibility" in x: return "domain_list"
    if "fact" in x and "check" in x: return "fact_checker"
    if "self" in x and "report" in x or "perceived" in x: return "self_report"
    if "classifier" in x or "gpt" in x or "hybrid" in x: return "classifier"
    return "researcher_coding"
def samp3(r):
    s=g(r,"sampling_frame")
    if s in ("panel_trace","full_census","random_platform"): return "representative"
    if s=="survey_sample": return "survey"
    if s in ("keyword_topical","curated_seed","purposive","convenience","convenience_snowball","curated_business_pages"): return "topical/curated"
    return "other"
def denom2(r):
    d=g(r,"denom_class")
    return "whole_diet" if d in ("all_media","news_diet","population","political_news") else ("narrow" if d in ("topical","curated_sample","single_source","curated") else "other")

out=[]
for i,r in enumerate(rows):
    out.append(dict(
        row=i, id=g(r,"id"), title=TITLES.get(g(r,"id"),""),
        value=pctf(r), value_raw=g(r,"value_raw"),
        construct=g(r,"construct"),
        denom_class=g(r,"denom_class"), denom2=denom2(r),
        breadth=g(r,"breadth"),
        ground_truth=canon_gt(r), id_method=id_method(r),
        classification_level=g(r,"classification_level"), unit=g(r,"unit"),
        sampling=samp3(r), sampling_frame=g(r,"sampling_frame"),
        measurement=measurement(r),
        topic=g(r,"topic"),
        platform=g(r,"platform_norm") or g(r,"platform"),
        country=g(r,"country_norm") or g(r,"country"), country_scope=g(r,"country_scope"),
        reach_subtype=g(r,"reach_subtype"),
        n=parse_n(g(r,"n")), n_raw=g(r,"n"),
        rob=rob_v3.get(g(r,"id"),""),
        demographic=g(r,"demographic_group"),
        within_misinfo=g(r,"within_misinfo_content"),
        main=(g(r,"demographic_group")=="" and (g(r,"value_kind") or "proportion")=="proportion"
              and pctf(r) is not None),
        measure_type=g(r,"measure_type"), denominator=g(r,"denominator"),
        definition=g(r,"misinfo_def") or g(r,"definition"),
        quote=g(r,"source_quote"),
        date=g(r,"period_label") or g(r,"date"),
    ))
outp=ROOT/"data/synth/phaseB/estimates_full.json"
json.dump(out, open(outp,"w"), ensure_ascii=False)
print(f"wrote {outp}: {len(out)} estimates")
from collections import Counter
print("id_method:", dict(Counter(r["id_method"] for r in out)))
print("main-set with value:", sum(1 for r in out if r["main"] and r["value"] is not None))
