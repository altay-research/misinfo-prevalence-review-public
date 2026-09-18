#!/usr/bin/env python3
"""venue_sensitivity.py — corpus composition by publication type, and a headline sensitivity.

WHY. Appraisers reading full texts flagged that several included studies come from very
low-visibility venues and contain internal contradictions (one claims a 2021-2026 longitudinal span
in a 2025 issue; another conflates a 282-respondent survey with 7,234 NLP data points). That is a
concern about the evidence base that is INDEPENDENT of risk of bias: a study can be internally
well-designed and still be published somewhere with little or no editorial scrutiny.

Rather than make a subjective "venue quality" judgement — which would be indefensible and is not
ours to make — this classifies each study by OBJECTIVE publication type from OpenAlex (journal
article, preprint, conference paper, repository record, unknown) and re-runs the headline medians
excluding non-journal sources. The point is to show whether the conclusions depend on the
grey-ish tail, not to rank venues.

Resolution: OpenAlex id where present, else DOI lookup. The DOI fallback is essential -- resolving
by OpenAlex id alone left 277 of 317 studies "unknown" and produced arms of k=3 swinging 26 points,
i.e. an uninterpretable analysis. With the fallback, 85% resolve as journal articles and 5% remain
unknown; unknowns are reported as their own stratum rather than folded silently into either arm.

Inputs : current freeze (docs/FROZEN.md pointer); OpenAlex API (no key; polite pool)
Outputs: data/synth/venue_types.csv
         data/synth/phaseB/venue_sensitivity.csv

Run: python3 scripts/venue_sensitivity.py
"""

import csv
import json
import os
import re
import statistics as st
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAILTO = "sachayesilaltay@gmail.com"
CONSTRUCTS = ["EXPOSURE", "REACH", "SHARING", "CONTENT", "RECALL"]
WHOLE_DIET = {"all_media", "news_diet", "population", "political_news"}


def frozen():
    spec = open(os.path.join(ROOT, "docs/FROZEN.md"), encoding="utf-8").read()
    fp = re.search(r"File:\s*(\S+)", spec).group(1)
    return list(csv.DictReader(open(os.path.join(ROOT, fp), encoding="utf-8")))


def openalex_id(sid):
    m = re.search(r"(W\d+)", sid)
    return m.group(1) if m else None


def doi_index():
    """study_id -> DOI, harvested from the cached search dumps.

    Necessary because 87% of the corpus is Scopus-sourced and carries no OpenAlex id in its
    identifier; resolving by OpenAlex id alone left 277 of 317 studies "unknown", which made the
    sensitivity uninterpretable (arms of k=3 swinging 26 points). DOI lookup recovers 84%.
    """
    idx = {}
    for f in ("data/abstracts/abstracts.jsonl", "data/abstracts/advancing_with_abstracts.jsonl",
              "data/openalex_netnew.jsonl", "data/pubmed_netnew.jsonl",
              "data/corpus_strict_v2_2026-06-20.jsonl"):
        path = os.path.join(ROOT, f)
        if not os.path.exists(path):
            continue
        for line in open(path, encoding="utf-8", errors="ignore"):
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            k = d.get("eid") or d.get("id") or d.get("oaid") or d.get("pmid")
            v = d.get("doi") or d.get("prism:doi")
            if k and v:
                idx.setdefault(str(k), str(v).replace("https://doi.org/", ""))
    return idx


def fetch_by_doi(dois, batch=40):
    out = {}
    dois = [d for d in dois if d]
    for k in range(0, len(dois), batch):
        chunk = dois[k:k + batch]
        url = ("https://api.openalex.org/works?filter=doi:"
               + urllib.parse.quote("|".join(chunk), safe="|")
               + f"&per-page={batch}&select=id,doi,type,primary_location&mailto={MAILTO}")
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                data = json.load(r)
        except Exception as e:
            print(f"  ! doi batch {k} failed: {e}")
            continue
        for w in data.get("results", []):
            dv = (w.get("doi") or "").replace("https://doi.org/", "").lower()
            loc = w.get("primary_location") or {}
            src = loc.get("source") or {}
            out[dv] = {"type": w.get("type") or "", "venue": src.get("display_name") or "",
                       "src_type": (src.get("type") or "")}
        time.sleep(0.3)
    return out


def fetch_types(ids, batch=40):
    out = {}
    ids = [i for i in ids if i]
    for k in range(0, len(ids), batch):
        chunk = ids[k:k + batch]
        url = ("https://api.openalex.org/works?filter=ids.openalex:"
               + urllib.parse.quote("|".join(chunk), safe="|")
               + f"&per-page={batch}&select=id,type,primary_location&mailto={MAILTO}")
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                data = json.load(r)
        except Exception as e:
            print(f"  ! batch {k} failed: {e}")
            continue
        for w in data.get("results", []):
            wid = (w.get("id") or "").rsplit("/", 1)[-1]
            loc = w.get("primary_location") or {}
            src = loc.get("source") or {}
            out[wid] = {"type": w.get("type") or "", "venue": src.get("display_name") or "",
                        "src_type": (src.get("type") or "")}
        time.sleep(0.3)
    return out


def classify(meta):
    if not meta:
        return "unknown"
    t, stype = (meta.get("type") or "").lower(), (meta.get("src_type") or "").lower()
    venue = (meta.get("venue") or "").lower()
    if t in ("preprint",) or "arxiv" in venue or "ssrn" in venue or "osf" in venue:
        return "preprint"
    if stype == "repository" or "university" in venue or "forskningsportal" in venue \
            or "scholarshare" in venue or "istituzionale" in venue:
        return "repository_record"
    if t in ("article",) and stype in ("journal",):
        return "journal_article"
    if t in ("proceedings-article", "proceedings") or "proceedings" in venue \
            or "conference" in venue:
        return "conference_paper"
    if t:
        return f"other:{t}"
    return "unknown"


def study_median(rows):
    by = defaultdict(list)
    for r in rows:
        by[r["id"]].append(float(r["value_pct"]))
    pts = [st.median(v) for v in by.values()]
    return (round(st.median(pts), 1), len(pts)) if pts else ("", 0)


def main():
    rows = frozen()
    studies = sorted({r["id"] for r in rows})
    idmap = {s: openalex_id(s) for s in studies}
    meta = fetch_types([v for v in idmap.values() if v])
    # fall back to DOI resolution for the Scopus-sourced majority
    di = doi_index()
    need = [s for s in studies if not meta.get(idmap.get(s) or "")]
    dmap = {s: (di.get(s) or di.get(s.replace("2-s2.0-", "")) or "").lower() for s in need}
    dmeta = fetch_by_doi(sorted({d for d in dmap.values() if d}))
    vt = {}
    for s in studies:
        m = meta.get(idmap.get(s) or "") or dmeta.get(dmap.get(s, ""), None)
        vt[s] = classify(m)
        if m:
            meta.setdefault(idmap.get(s) or s, m)

    with open(os.path.join(ROOT, "data/synth/venue_types.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["study_id", "venue_type", "venue"])
        for s in studies:
            m = meta.get(idmap.get(s) or "", {}) or dmeta.get(dmap.get(s, ""), {})
            w.writerow([s, vt[s], m.get("venue", "")])

    c = Counter(vt.values())
    print(f"corpus composition by publication type (n={len(studies)} studies)")
    for k, v in c.most_common():
        print(f"  {k:20s} {v:4d}  ({v/len(studies):5.1%})")

    main_set = [r for r in rows if r["value_kind"] == "proportion"
                and not r["demographic_group"].strip() and r["value_pct"].strip()]
    JOURNAL = {"journal_article"}

    res = []
    for label, keep in (("ALL studies", None),
                        ("journal articles only", JOURNAL),
                        ("excluding repository/unknown-venue records",
                         {k for k in c if k not in ("repository_record", "unknown")})):
        sub = main_set if keep is None else [r for r in main_set if vt.get(r["id"]) in keep]
        for con in CONSTRUCTS:
            m, k = study_median([r for r in sub if r["construct"] == con])
            if k >= 3:
                res.append({"analysis": label, "group": con, "k_studies": k, "median_pct": m})
        wd = [r for r in sub if r["denom_class"] in WHOLE_DIET
              and r["construct"] in ("EXPOSURE", "REACH")]
        m, k = study_median(wd)
        if k >= 3:
            res.append({"analysis": label, "group": "WHOLE-DIET backbone",
                        "k_studies": k, "median_pct": m})

    out = os.path.join(ROOT, "data/synth/phaseB/venue_sensitivity.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["analysis", "group", "k_studies", "median_pct"])
        w.writeheader()
        w.writerows(res)

    base = {r["group"]: r for r in res if r["analysis"] == "ALL studies"}
    print(f"\n{'analysis':44} {'group':21} {'k':>4} {'median':>8} {'vs all':>9}")
    print("-" * 90)
    for r in res:
        d = ""
        if r["analysis"] != "ALL studies" and r["group"] in base:
            d = f"{r['median_pct']-base[r['group']]['median_pct']:+.1f} pp"
        print(f"{r['analysis']:44} {r['group']:21} {r['k_studies']:>4} {r['median_pct']:>7}% {d:>9}")
    print(f"\nwrote {os.path.relpath(out, ROOT)} and data/synth/venue_types.csv")


if __name__ == "__main__":
    main()
