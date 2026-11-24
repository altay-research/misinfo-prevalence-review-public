#!/usr/bin/env python3
"""PRISMA 2020 items 16b and 17: the record-level lists the review ships.

Generated from the record ledger (data/synth/prisma_terminal_states.csv, written by
scripts/validate_prisma.py from scripts/prisma_ledger.py), so the lists and the flow diagram are the
same records by construction; each writer asserts its row count against data/synth/prisma_counts.json.

Outputs
  data/synth/phaseB/si_included_studies.csv     item 16b: one row per included study
  data/synth/phaseB/si_fulltext_exclusions.csv  item 17 / Supplementary Data 2: every report excluded at
                                                full text, across all sources and passes, one row per
                                                report, with the stage that decided it, the reason
                                                category drawn on the figure and the verbatim reason
  data/synth/phaseB/si_not_retrieved.csv        every report sought and not retrieved
  data/synth/phaseB/si_other_reports.csv        second reports of included studies
  data/synth/phaseB/si_rescreen_exclusions.csv  records excluded at the second-reader title/abstract
                                                re-screen of the June abstract includes
  docs/SI_lists_README.md

Bibliography: cached search dumps first, then the hand-verified overlay data/inputs/si_biblio_manual.csv,
then a DOI content-negotiation cache (data/synth/si_biblio_cache.json; --fetch refreshes it, with the
contact address taken from the SI_LISTS_MAILTO environment variable). Nothing is inferred; a field with
no source is written "unknown".

Run: python3 scripts/validate_prisma.py && python3 scripts/make_si_lists.py [--fetch]
"""

import csv
import glob
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

P = lambda *a: os.path.join(ROOT, *a)
# Contact for the polite pools of doi.org and OpenAlex, used only with --fetch; set it in the
# environment rather than in the repository.
MAILTO = os.environ.get("SI_LISTS_MAILTO", "")
CACHE = P("data/synth/si_biblio_cache.json")
UNKNOWN = "unknown"

# Project-internal display labels, not bibliography. `titles.json` and the QA worklists hold a
# short label for a study ("Moreno et al. — dermatology misinformation on social media"), which is
# the right thing on a coding page and the wrong thing in a reference list. A registered record
# overrides these; it never overrides the hand-verified overlay or a publisher dump.
WEAK_SOURCES = {"titles_json", "staged_candidates", "abstract_only_list", "drop_ledger",
                "not_retrieved_ledger", "dedup_ledger", "screening_sheet"}


# === IO HELPERS ===

def canon(x):
    """Normalize any of the six ID schemes to one key. Copied from validate_prisma.canon."""
    if x is None:
        return ""
    x = str(x).strip().replace("https://openalex.org/", "")
    if x.startswith("OA-"):
        x = x[3:]
    if x.startswith("PMID-"):
        return x
    if re.fullmatch(r"\d+", x):
        return "PMID-" + x
    return x


def read_csv(path):
    p = P(path)
    return list(csv.DictReader(open(p, encoding="utf-8", errors="replace"))) if os.path.exists(p) else []


def read_jsonl(path):
    out = []
    p = P(path)
    if not os.path.exists(p):
        return out
    for line in open(p, encoding="utf-8", errors="replace"):
        line = line.strip()
        if line.startswith("{"):
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def ids_from(rows, field):
    return {canon(r.get(field)) for r in rows if r.get(field)}


def frozen_path():
    spec = open(P("docs/FROZEN.md"), encoding="utf-8").read()
    return re.search(r"File:\s*(\S+)", spec).group(1)


# === BIBLIOGRAPHY ===

def biblio_index():
    """study key -> {title, first_author, year, doi, venue, src}.

    Sources are consulted in descending order of trust and the first non-empty value for each field
    wins, so the Scopus corpus (the only dump carrying an author) sets the author and a later dump
    can still supply a venue it lacks. `src` records which source filled which field.
    """
    meta = {}

    def put(key, source, **fields):
        k = canon(key)
        if not k:
            return
        d = meta.setdefault(k, {"src": {}})
        for f, v in fields.items():
            v = str(v).strip() if v is not None else ""
            if v and not d.get(f):
                d[f] = v
                d["src"][f] = source

    for d in read_jsonl("data/corpus_strict_v2_2026-06-20.jsonl"):
        put(d.get("eid"), "scopus_corpus", title=d.get("title"), first_author=d.get("first_author"),
            year=d.get("year"), doi=d.get("doi"), venue=d.get("source"))
    for p in sorted(glob.glob(P("searches/scopus_*.json"))):
        for e in (json.load(open(p, encoding="utf-8")).get("entries") or []):
            put(e.get("eid"), "scopus_arm_dump", title=e.get("dc:title"),
                first_author=e.get("dc:creator"), year=(e.get("prism:coverDate") or "")[:4],
                doi=e.get("prism:doi"), venue=e.get("prism:publicationName"))
    for d in read_jsonl("data/abstracts/abstracts.jsonl"):
        put(d.get("eid"), "abstract_dump", title=d.get("title"), doi=d.get("doi"),
            venue=d.get("source"))
    for f in ("searches/openalex_keyword_20260624.jsonl", "data/openalex_netnew.jsonl",
              "data/snowball/candidates.jsonl", "data/snowball/advancing.jsonl"):
        for d in read_jsonl(f):
            put(d.get("oaid"), "openalex_dump", title=d.get("title"), year=d.get("year"),
                doi=d.get("doi"), venue=d.get("venue"))
    for f in ("searches/pubmed_strict_v2_20260624.jsonl", "data/pubmed_netnew.jsonl",
              "searches/behavioural_arm_pubmed_20260904.jsonl"):
        for d in read_jsonl(f):
            put(d.get("pmid"), "pubmed_dump", title=d.get("title"), year=d.get("year"),
                doi=d.get("doi"))
    for r in read_csv("data/extract/extraction_master.csv"):
        put(r.get("eid"), "extraction_master", title=r.get("title"),
            first_author=r.get("first_author"), year=r.get("year"), doi=r.get("doi"))

    # Title-only fallbacks, for records that left the funnel before any dump carried them.
    for r in read_csv("data/extract_v2/qa/dropped_studies.csv"):
        put(r.get("id"), "drop_ledger", title=r.get("title"))
    for f in ("data/extract_v2/qa/included_not_retrieved.csv",
              "data/extract_v2/qa/openalex_not_retrieved.csv"):
        for r in read_csv(f):
            put(r.get("id"), "not_retrieved_ledger", title=r.get("title"), doi=r.get("doi"))
    for r in read_csv("data/extract_v2/qa/oa_dups_dropped.csv"):
        put(r.get("oaid"), "dedup_ledger", title=r.get("oa_title"))
    for r in read_csv("data/extract_v2/qa/openalex_candidates_STAGED.csv"):
        put(r.get("id"), "staged_candidates", title=r.get("title"))
    for d in json.load(open(P("data/extract_v2/qa/abstract_only_list.json"), encoding="utf-8")):
        put(d.get("id"), "abstract_only_list", title=d.get("title"))
    for f in ("data/screen_title_2026-06-20.csv", "data/screen_abstract_2026-06-21.csv",
              "data/screen_stage5_2026-06-21.csv"):
        for r in read_csv(f):
            put(r.get("eid"), "screening_sheet", title=r.get("title"), year=r.get("year"))
    for k, v in json.load(open(P("data/synth/phaseB/titles.json"), encoding="utf-8")).items():
        put(k, "titles_json", title=v)

    # venue_types.csv is the OpenAlex-resolved venue for every frozen study; it fills the venues the
    # OpenAlex and PubMed dumps never carried.
    for r in read_csv("data/synth/venue_types.csv"):
        put(r.get("study_id"), "venue_types", venue=r.get("venue"))

    return meta


def apply_overlays(meta, ids, fetch):
    """Fill remaining gaps from the hand-entered overlay, then from OpenAlex.

    The overlay exists because eight included studies entered the corpus as user-supplied PDFs or
    seed studies under a hand-assigned key (NEW-…, SEED-…, an arXiv number) and carry no identifier
    any API can resolve. Their bibliography has to be typed once; data/inputs/ is where this project
    keeps hand-curated inputs.
    """
    for r in read_csv("data/inputs/si_biblio_manual.csv"):
        k = canon(r.get("study_id") or r.get("id"))
        if not k:
            continue
        d = meta.setdefault(k, {"src": {}})
        for f in ("title", "first_author", "year", "doi", "venue"):
            v = (r.get(f) or "").strip()
            if v:
                d[f], d["src"][f] = v, "manual_overlay"

    cache = json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}
    if fetch:
        cache.update(fetch_biblio(meta, ids, cache))
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        json.dump(cache, open(CACHE, "w", encoding="utf-8"), indent=1, sort_keys=True)

    for k, rec in cache.items():
        d = meta.setdefault(canon(k), {"src": {}})
        for f in ("title", "first_author", "year", "doi", "venue"):
            v = (rec.get(f) or "").strip()
            if v and (not d.get(f) or d["src"].get(f) in WEAK_SOURCES):
                d[f], d["src"][f] = v, rec.get("api", "api")
    return meta


def _initialled(family, given):
    """"Unlu A." — the Scopus corpus's author format, so both halves of the column read alike."""
    ini = "".join(f"{t[0]}." for t in re.split(r"[\s\-]+", given or "") if t[:1].isalpha())
    return f"{family} {ini}".strip()


def fetch_biblio(meta, ids, cache):
    """Fill the gaps the local dumps leave, for included studies only.

    DOI content negotiation (doi.org, asking for CSL JSON) is the primary lookup. It is free,
    unmetered, and reaches every registration agency behind one request, so Crossref journal
    articles, DataCite arXiv postings and OSF preprints all resolve through the same call — and it
    carries the author list the OpenAlex and PubMed dumps never stored. OpenAlex by work id is the
    fallback for the handful of records that have an OpenAlex id but no DOI. Title search is
    deliberately NOT used: a fuzzy title match is how a wrong author ends up in a reference list.
    """
    by_doi, by_oaid = {}, {}
    for i in ids:
        k = canon(i)
        d = meta.get(k, {})
        if k in cache or all(d.get(f) for f in ("first_author", "year", "venue", "doi")):
            continue
        if d.get("doi"):
            by_doi[d["doi"].lower().replace("https://doi.org/", "")] = k
        elif re.fullmatch(r"W\d+", k):
            by_oaid[k] = k

    out = {}

    def get(url, accept=None):
        headers = {"User-Agent": f"mailto:{MAILTO}"}
        if accept:
            headers["Accept"] = accept
        for attempt in range(4):
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=60) as r:
                    return json.load(r)
            except Exception as e:                               # noqa: BLE001 — report, don't die
                if attempt == 3:
                    print(f"  ! {url.split('?')[0]} failed: {e}")
                    return None
                time.sleep(2 ** attempt)
        return None

    def one_of(v):
        """CSL fields arrive as a string from some agencies and a one-item list from others."""
        if isinstance(v, list):
            v = v[0] if v else ""
        return html.unescape(str(v or "")).strip()

    for doi, key in sorted(by_doi.items()):
        m = get("https://doi.org/" + urllib.parse.quote(doi),
                accept="application/vnd.citationstyles.csl+json")
        if not m:
            continue
        auth = m.get("author") or []
        first = next((a for a in auth if a.get("sequence") == "first"), auth[0] if auth else None)
        parts = (m.get("issued") or {}).get("date-parts") or [[]]
        out[key] = {
            "api": "doi_csl",
            "title": one_of(m.get("title")),
            # A corporate author has no given/family pair, only a literal name.
            "first_author": (_initialled(first.get("family", ""), first.get("given", ""))
                             or one_of(first.get("literal"))) if first else "",
            "year": str(parts[0][0]) if parts and parts[0] else "",
            "doi": m.get("DOI", doi),
            # Preprints and reports carry no container title; the publisher is the venue there.
            "venue": one_of(m.get("container-title")) or one_of(m.get("publisher")),
        }
        time.sleep(0.2)

    oaids = sorted(by_oaid)
    SELECT = "id,doi,display_name,publication_year,authorships,primary_location"
    for k in range(0, len(oaids), 40):
        chunk = oaids[k:k + 40]
        url = ("https://api.openalex.org/works?filter=ids.openalex:"
               + urllib.parse.quote("|".join(chunk), safe="|")
               + f"&per-page={len(chunk)}&select={SELECT}&mailto={MAILTO}")
        for w in (get(url) or {}).get("results", []):
            wid = (w.get("id") or "").rsplit("/", 1)[-1]
            if wid not in by_oaid:
                continue
            src = ((w.get("primary_location") or {}).get("source") or {})
            first = next((a for a in (w.get("authorships") or [])
                          if a.get("author_position") == "first"), None)
            out[by_oaid[wid]] = {
                "api": "openalex_api",
                "title": w.get("display_name") or "",
                "first_author": ((first or {}).get("author") or {}).get("display_name", ""),
                "year": str(w.get("publication_year") or ""),
                "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
                "venue": src.get("display_name") or "",
            }
        time.sleep(1.0)

    print(f"fetched {len(out)} of {len(by_doi) + len(by_oaid)} requested record(s) "
          f"({len(by_doi)} by DOI content negotiation, {len(by_oaid)} by OpenAlex work id)")
    return out



# === WRITERS ===

STAGES = (("screening_pass_2026-11", "November 2026 third-model re-screen: full-text check and extraction"),
          ("changelog_v1725", "November 2026 third-model re-screen: full-text check and extraction"),
          ("changelog_v1724", "v1.7.24 freeze (November 2026 full-text re-read)"),
          ("rules_pass_2026-11", "November 2026 full-text re-read of earlier exclusions"),
          ("repair_2026-09", "September 2026 corpus repair: full-text screen"),
          ("behavioural_arm", "September 2026 behavioural-design queries: full-text screen"),
          ("full_reextract_2026-09", "September 2026 blind full-text re-extraction"),
          ("changelog_v1718", "v1.7.18 freeze (September 2026 pre-merge rulings)"),
          ("removal_reasons", "removed at a freeze (see reason)"),
          ("fulltext_decisions", "full-text decision recorded in the research log"),
          ("screen_stage5", "June 2026 stage-5 full-text screen (two readers)"),
          ("worklist.jsonl", "June 2026 full-text extraction"),
          ("estimates_master_final", "June-July 2026 second full-text extraction"),
          ("freeze history", "removed at a freeze (see reason)"),
          ("merged_outcomes", "November 2026 screening of undecided records"))


def stage_of(row):
    """The pass that took the decisive full-text decision, named from the ledger's reason source."""
    for key, lab in STAGES:
        if key in row["reason_source"]:
            return lab
    return "July-August 2026 full-text verification and dispositioning"


def ledger():
    path = P("data/synth/prisma_terminal_states.csv")
    if not os.path.exists(path):
        raise SystemExit("run scripts/validate_prisma.py first: " + path)
    return (read_csv("data/synth/prisma_terminal_states.csv"),
            json.load(open(P("data/synth/prisma_counts.json"), encoding="utf-8")))


def write_included(meta, counts):
    rows = list(csv.DictReader(open(P(frozen_path()), encoding="utf-8")))
    n_est, constructs = Counter(), defaultdict(set)
    for r in rows:
        n_est[r["id"]] += 1
        constructs[r["id"]].add(r["construct"])
    basis = {r["study_id"]: {"full_text": "full text", "abstract_only": "abstract only"}
             .get(r["source_read"], r["source_read"] or UNKNOWN)
             for r in read_csv("data/rob/risk_of_bias_v3_master.csv")}
    out, gaps = [], Counter()
    for sid in sorted(n_est):
        d = meta.get(canon(sid), {})
        rec = {"study_id": sid, "first_author": d.get("first_author") or UNKNOWN,
               "year": d.get("year") or UNKNOWN, "title": d.get("title") or UNKNOWN,
               "venue": d.get("venue") or UNKNOWN, "doi": d.get("doi") or UNKNOWN,
               "constructs": ";".join(sorted(constructs[sid])), "n_estimates": n_est[sid],
               "text_basis": basis.get(sid, UNKNOWN),
               "biblio_source": ";".join(sorted(set(d.get("src", {}).values()))) or "none"}
        for f in ("first_author", "year", "title", "venue", "doi"):
            if rec[f] == UNKNOWN:
                gaps[f] += 1
        out.append(rec)
    assert len(out) == counts["total"]["included"], (len(out), counts["total"]["included"])
    out.sort(key=lambda r: ((r["first_author"] == UNKNOWN), r["first_author"].lower(), str(r["year"]), r["study_id"]))
    _write("data/synth/phaseB/si_included_studies.csv", out, list(out[0].keys()))
    return out, gaps


def _write(path, rows, fields):
    with open(P(path), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


# Working notes (rulings, task codes, names, quoted chat) stay in the repository ledgers; the published list carries the
# reason only. A reason that is nothing but working notes falls back to its category label (2026-11-24).
_STAFF = re.compile(r"sacha|claude|\bs\.a\.|in chat|\bchat\b(?!bot)|\bwiat\b|\bhmm|i think|\bno\? |\bruled\b|\bruling|browser value|\bcard\b|jc\d|excluded at extraction", re.I)


def public_reason(s, label):
    s = re.sub(r"; T\d(_[A-Z0-9_]+)?,?( filter \w+)?:.*$", "", s or "")
    s = re.sub(r"\s*\([^()]*(?:Sacha|S\.A\.|jc\d|pre-merge rulings?)[^()]*\)", "", s)
    s = re.sub(r"\b(R|L|A)\d+(/(R|L|A)?\d+)*: ", "", s)
    s = re.sub(r"^(DROP( both rows)?\.|dispute adjudication:)\s*", "", s)
    if not s.strip() or _STAFF.search(s):
        keep = [x.strip() for x in re.split(r"(?<=[.;])\s+", s) if x.strip() and not _STAFF.search(x)]
        s = " ".join(keep) if keep and "accepted" not in s.lower() and len(" ".join(keep)) > 40 and not re.search(r"no\?", s) else label
    return s.strip(" ;")


def record_rows(T, meta, labels, state, extra):
    out = []
    for r in T:
        if r["terminal_state"] != state:
            continue
        d = meta.get(canon(r["record_id"]), {})
        out.append(dict(record_id=r["record_id"], identified_by=labels.get(r["stream"], r["stream"]),
                        title=d.get("title") or r["title"] or UNKNOWN, year=d.get("year") or r["year"] or UNKNOWN,
                        doi=d.get("doi") or r["doi"] or "", **extra(r)))
    return out


def main():
    fetch = "--fetch" in sys.argv
    T, counts = ledger()
    src_label = {k: b["label"] for k, b in counts["streams"].items()}
    labels = counts["reason_labels"]
    rows = list(csv.DictReader(open(P(frozen_path()), encoding="utf-8")))
    meta = apply_overlays(biblio_index(), sorted({r["id"] for r in rows}), fetch)

    included, gaps = write_included(meta, counts)

    exc = record_rows(T, meta, src_label, "EXCLUDED_FT", lambda r: dict(
        stage=stage_of(r), recovered_by=r["recovered_by"], reason_category=labels[r["reason_category"]],
        reason_detail=public_reason(r["reason"], labels[r["reason_category"]]) or "No per-record reason was recorded.", reason_source=re.sub(r"\S*sacha\S*", "author rulings (repository)", r["reason_source"], flags=re.I)))
    order = {lab: i for i, lab in enumerate(labels.values())}
    exc.sort(key=lambda r: (order[r["reason_category"]], r["record_id"]))
    assert len(exc) == counts["total"]["excluded_ft"], (len(exc), counts["total"]["excluded_ft"])
    got = Counter(r["reason_category"] for r in exc)
    for cat, k in counts["total"]["excluded_ft_by_reason"].items():
        assert got.get(labels[cat], 0) == k, (cat, got.get(labels[cat], 0), k)
    _write("data/synth/phaseB/si_fulltext_exclusions.csv", exc, list(exc[0].keys()))

    nr = record_rows(T, meta, src_label, "NOT_RETRIEVED", lambda r: dict(
        recovered_by=r["recovered_by"], note=r["reason"], source=r["reason_source"]))
    assert len(nr) == counts["total"]["not_retrieved"]
    nr.sort(key=lambda r: r["record_id"])
    _write("data/synth/phaseB/si_not_retrieved.csv", nr, list(nr[0].keys()))

    rep = record_rows(T, meta, src_label, "OTHER_REPORT", lambda r: dict(report_of=r["dup_of"], note=r["reason"]))
    assert len(rep) == counts["total"]["other_reports"]
    _write("data/synth/phaseB/si_other_reports.csv", rep,
           ["record_id", "identified_by", "title", "year", "doi", "report_of", "note"])

    sr = [dict(record_id=r["record_id"], title=r["title"],
               exclusion_stage="second-reader title/abstract re-screen of the June abstract includes "
                               "(third reader on disagreement)",
               reason_detail=r["reason"], reason_source=r["reason_source"])
          for r in T if r["terminal_state"] == "EXCLUDED_SCREENING" and r["screen_stage"] == "second_reader"]
    assert len(sr) == counts["total"]["excluded_screening_by_stage"].get("second_reader", 0)
    _write("data/synth/phaseB/si_rescreen_exclusions.csv", sorted(sr, key=lambda r: r["record_id"]),
           ["record_id", "title", "exclusion_stage", "reason_detail", "reason_source"])

    no_detail = sum(1 for r in exc if r["reason_detail"].startswith("No per-record"))
    readme = f"""# Supplementary lists (PRISMA 2020 items 16b and 17)

Generated by `scripts/make_si_lists.py` from the record ledger (`data/synth/prisma_terminal_states.csv`,
one row per identified record, built by `scripts/prisma_ledger.py` and checked by
`scripts/validate_prisma.py`). Freeze v{counts['freeze']}. Do not hand-edit.

| file | rows | content |
|---|---|---|
| `si_included_studies.csv` | {len(included)} | included studies (item 16b) |
| `si_fulltext_exclusions.csv` | {len(exc)} | every report excluded at full text, all sources and passes (item 17; Supplementary Data 2) |
| `si_not_retrieved.csv` | {len(nr)} | every report sought and not retrieved |
| `si_other_reports.csv` | {len(rep)} | second reports (preprint or duplicate copy) of included studies |
| `si_rescreen_exclusions.csv` | {len(sr)} | records excluded at the second-reader title/abstract re-screen |

In `si_fulltext_exclusions.csv`, `stage` names the pass that took the decisive decision; `recovered_by` is
filled when the first screen had excluded the record and a later re-screen sent it to full text;
`reason_category` is the group drawn on the flow diagram, assigned by the ordered rules in
`prisma_ledger.REASON_CATEGORIES` from the recorded reason; `reason_detail` is the recorded reason,
verbatim; `reason_source` is the file it comes from. {no_detail} rows carry no recorded reason and say so.

Bibliography gaps among included studies: {gaps['first_author']} without a first author, {gaps['year']}
without a year, {gaps['venue']} without a venue, {gaps['doi']} without a DOI.
"""
    open(P("docs/SI_lists_README.md"), "w", encoding="utf-8").write(readme)
    print(f"included studies   {len(included):>5}")
    print(f"full-text excluded {len(exc):>5}  ({no_detail} without a recorded reason)")
    print(f"not retrieved      {len(nr):>5}")
    print(f"other reports      {len(rep):>5}")
    print(f"second-reader excl {len(sr):>5}")
    for lab, k in Counter(r["stage"] for r in exc).most_common():
        print(f"   {k:>5}  {lab}")


if __name__ == "__main__":
    main()
