#!/usr/bin/env python3
"""phaseB_prep_regression.py — build the estimate-level analysis dataset for the meta-regression
and precision-weighting. Reads frozen v1.4.6; parses numeric n; collapses moderators to modelling
levels. Writes data/synth/phaseB/regression_data.csv (one row per estimate with usable p and n)."""
import csv, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CSV=ROOT/re.search(r'File:\s*(\S+)',(ROOT/"docs/FROZEN.md").read_text()).group(1)
rows=list(csv.DictReader(open(CSV)))
def g(r,k): return (r.get(k) or "").strip()
# MEASUREMENT TYPE is derived from the construct taxonomy, not joined from the risk-of-bias file.
# Until 2026-09-18 it came from data/extract_v2/qa/rob_appraisals_v145.csv, a 22 July appraisal
# covering 317 of the 443 studies. When the corpus grew past that file on 2026-09-04 the join
# started returning nothing for the new studies: 337 of 837 regression rows (40%) carried NA, which
# phaseB_metareg.R folded into an "unspecified" level. That level was not a measurement type, it was
# "not appraised by 22 July", and it was not random — 182 of the 244 RECALL rows landed in it, so
# SELF_REPORT was fitted on 61 rows while 182 genuinely self-reported rows sat in a bucket of their
# own. The taxonomy already fixes measurement type per construct (Table 1, 2.3): content analyses
# code content, recall surveys are self-report, and the four audience constructs read behavioural
# records. That rule reproduces the July appraisal on 90.6% of the rows where both exist, and it
# covers every study rather than the 317 that happened to be appraised first.
MEASUREMENT_BY_CONSTRUCT = {
    "CONTENT": "CONTENT_CODING",
    "RECALL": "SELF_REPORT",
    "EXPOSURE": "BEHAVIOURAL", "REACH": "BEHAVIOURAL",
    "SHARING": "BEHAVIOURAL", "CONCENTRATION": "BEHAVIOURAL",
}

def parse_n(s):
    # 2026-08-11 code review: the K/M suffix must be a whole token — the old r'\s*([KkMm])?' let
    # "64 media articles" parse as 64M (six rows inflated x1e6). The FIRST number in the n string
    # is the sampling base by convention; the exceptions, where the string leads with a numerator
    # or a unit other than the measure's denominator, are hand-audited in N_OVERRIDES below (a
    # blanket "take the segment after '/'" rule was tried and OVER-corrected — the strings follow
    # no single convention).
    s=s.replace(",","")
    m=re.search(r'(\d+\.?\d*)\s?([KkMm])?(?![A-Za-z])',s)
    if not m: return None
    v=float(m.group(1)); suf=(m.group(2) or "").lower()
    v*= {"k":1e3,"m":1e6}.get(suf,1)
    return int(v) if v>=1 else None

# (study_id, value_pct) -> denominator n, hand-audited against the n string + measure_type on
# 2026-08-11 (each row's measure names its base; the first number in these strings is not it).
N_OVERRIDES = {
    ("2-s2.0-85137779722", "0.88"): 1443871621,   # % of COVID tweets; string leads with numerator
    ("2-s2.0-85085201199", "24.1"): 257804146,    # view-weighted share; base = views
    ("2-s2.0-85095594211", "36"): 4904160,        # share-weighted share; base = shares
    ("2-s2.0-85142886759", "2.7"): 3960000,       # % of URL-bearing message base
    ("2-s2.0-85100218180", "2.7"): 7275642,       # % of URL links; 67.6M is all tweets
    ("2-s2.0-105009619554", "52"): 411,           # % of characteristics, not of 100 videos
    ("2-s2.0-105009619554", "27"): 411,
    ("2-s2.0-85160248068", "2.05"): 102114,       # % of SERPs, not of participants
    ("2-s2.0-85160248068", "0.72"): 226035,
    ("2-s2.0-85105511315", "32"): 3817494,        # low+high cred Twitter items rated
    ("2-s2.0-85105511315", "21"): 120375761,      # low+high cred Facebook items rated
}
def pct(r):
    v=g(r,"value_pct")
    try: return float(v) if v else None
    except: return None

def samp3(r):
    s=g(r,"sampling_frame")
    if s in ("panel_trace","full_census","random_platform"): return "representative"
    if s in ("survey_sample",): return "survey"
    if s in ("keyword_topical","curated_seed","purposive","convenience","convenience_snowball","curated_business_pages"): return "topical/curated"
    return "other"
def denom2(r):
    d=g(r,"denom_class")
    if d in ("all_media","news_diet","population","political_news"): return "whole_diet"
    if d in ("topical","curated_sample","single_source","curated"): return "narrow"
    return "other"
def id_method(r):
    gtx=g(r,"ground_truth").lower(); cl=g(r,"classification_level")
    if ("self" in gtx and "report" in gtx) or "perceived" in gtx: return "self_report"
    if "classifier" in gtx or "gpt" in gtx or "hybrid" in gtx or "auto" in gtx: return "classifier"
    if cl=="source_level" or "newsguard" in gtx or "domain" in gtx: return "domain_list"
    if "fact" in gtx and "check" in gtx: return "factcheck_claim"
    return "researcher_claim"
def gt(r):
    x=g(r,"ground_truth").lower()
    if "newsguard" in x or "domain" in x or "low-cred" in x or "low credibility" in x: return "domain_list"
    if "fact" in x and "check" in x: return "fact_checker"
    if "self" in x and "report" in x or "perceived" in x: return "self_report"
    if "classifier" in x or "gpt" in x or "hybrid" in x or "auto" in x: return "classifier"
    return "researcher_coding"

PREV=("EXPOSURE","REACH","RECALL","SHARING","CONTENT")
out=[]
for i,r in enumerate(rows):
    if g(r,"demographic_group") or (g(r,"value_kind") or "proportion")!="proportion": continue
    p=pct(r); n=N_OVERRIDES.get((g(r,"id"), g(r,"value_pct"))) or parse_n(g(r,"n"))
    if p is None or n is None or g(r,"construct") not in PREV: continue
    p=min(max(p,0.0),100.0)/100.0
    events=round(p*n)
    out.append(dict(estimate_id=i, study_id=g(r,"id"), construct=g(r,"construct"),
        measurement=MEASUREMENT_BY_CONSTRUCT.get(g(r,"construct").upper(), "NA"),
        sampling=samp3(r), denom=denom2(r),
        # Fine-grained denominator (v1.5.2, post-adjudication). The coarse denom2() collapses to
        # whole_diet/narrow/other, which understates the very variable this review is about --
        # it explained only 1.0% of variance while the paper argues the denominator drives the
        # number. Both are emitted so the coarse and fine readings can be compared.
        denom_fine=(g(r,"denom_class") or "unspecified"),
        breadth=g(r,"breadth") or "NA",
        ground_truth=gt(r), id_method=id_method(r), topic=g(r,"topic") or "NA", platform=g(r,"platform_norm") or "NA",
        p=round(p,6), n=n, events=events, value_pct=round(p*100,3)))
outp=ROOT/"data/synth/phaseB/regression_data.csv"
with open(outp,"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
print(f"wrote {outp}: {len(out)} estimates / {len({r['study_id'] for r in out})} studies")
from collections import Counter
for c in ["construct","measurement","sampling","denom","breadth"]:
    print(f"  {c}: {dict(Counter(r[c] for r in out))}")
