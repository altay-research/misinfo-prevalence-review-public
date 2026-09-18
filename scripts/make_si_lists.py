#!/usr/bin/env python3
"""PRISMA 2020 items 16b and 17 — the two record-level lists the review has to ship.

Item 16b asks for the studies that meet the inclusion criteria, cited. Item 17 asks for the records
excluded at full-text assessment, each with its reason. Both were reconciled internally (the
terminal-state ledger behind Supplementary Fig. 1) but neither existed as a table a reader could
open, so a referee could see the funnel's arithmetic and not the records behind it.

WHAT THIS GUARANTEES. The exclusion list is not written independently of the flow figure: the reason
labels are imported from make_prisma.EXCL_LABELS, the table the figure draws, and the script ASSERTS
that its own per-reason row counts equal the figure's numbers before writing anything. If the two
ever diverge the script fails instead of shipping a table that contradicts the figure.

EVERY ROW CARRIES A REASON. PRISMA item 17 asks for the reason a record was excluded, which means an
eligibility criterion and not the name of the pass that applied it. exclusion_reasons() below reads
every ledger, campaign output and ruling file that recorded one, in a documented precedence. Where
nothing recorded a reason the row says that in words instead of leaving the cell blank, so a bounded
gap is visible to a reader rather than looking like an omission.

The terminal-state assignment is replicated from validate_prisma.py rather than imported, because
that script's logic lives inside a main() that writes files and exits. The replication is guarded:
its histogram is asserted equal to data/synth/prisma_counts.json, which validate_prisma.py itself
writes, so any drift between the two copies fires on the next run.

BIBLIOGRAPHY. Fields come from the cached search-arm dumps first (Scopus carries first author and
venue; the OpenAlex, PubMed and snowball dumps carry title, year and DOI, but no author). Whatever
those cannot supply is filled with --fetch, by DOI content negotiation (which reaches Crossref,
DataCite and the rest behind one request) and by OpenAlex work id for the few records with no DOI,
then cached to data/synth/si_biblio_cache.json so every later run is offline and deterministic.
Nothing is inferred: a field with no source is written "unknown", and every row records where its
fields came from.

Inputs : docs/FROZEN.md (freeze pointer) and the freeze it names
         data/synth/prisma_counts.json  (run scripts/validate_prisma.py first)
         data/rob/risk_of_bias_v3_master.csv          (source_read -> text basis)
         the search-arm dumps in data/ and searches/; data/synth/venue_types.csv
         data/inputs/si_biblio_manual.csv             (hand-entered overlay, source-noted per row)
         data/synth/si_biblio_cache.json              (DOI/OpenAlex cache; --fetch refreshes)
         the drop ledgers, campaign outputs and ruling files read by exclusion_reasons(),
         including data/extract_v2/qa/exclusion_reasons_recovered_2026-09-15.csv
Outputs: data/synth/phaseB/si_included_studies.csv
         data/synth/phaseB/si_fulltext_exclusions.csv
         docs/SI_lists_README.md

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
import make_prisma  # noqa: E402  — the flow figure's own loader; source of the reason labels

P = lambda *a: os.path.join(ROOT, *a)
MAILTO = "sachayesilaltay@gmail.com"
CACHE = P("data/synth/si_biblio_cache.json")
UNKNOWN = "unknown"

# Project-internal display labels, not bibliography. `titles.json` and the QA worklists hold a
# short label for a study ("Moreno et al. — dermatology misinformation on social media"), which is
# the right thing on a coding page and the wrong thing in a reference list. A registered record
# overrides these; it never overrides the hand-verified overlay or a publisher dump.
WEAK_SOURCES = {"titles_json", "staged_candidates", "abstract_only_list", "drop_ledger",
                "not_retrieved_ledger", "dedup_ledger", "screening_sheet"}

# The exclusion reason each terminal state is filed under. Imported whole from make_prisma, which
# is also what the figure draws, so the list and the figure cannot disagree about a label. This
# used to be a local table of string PREFIXES matched against the figure's labels, which meant two
# labels beginning alike filed one state under the other's reason; the prefixes had to carry a
# disambiguating parenthetical, and the parenthetical was the pipeline stage PRISMA item 17 says
# not to report. One shared mapping removes both problems.
STATE_TO_REASON = dict(make_prisma.EXCL_LABELS)

# What a row says when no ledger, campaign file or ruling records why the record left. A stated,
# bounded gap is defensible in a PRISMA list; an empty cell reads as an oversight and an invented
# reason is worse than either. Keyed by terminal state so the sentence is true of the record it
# describes.
NO_REASON = "No per-record reason was recorded."
NO_REASON_BY_STATE = {
    "DROPPED_V2_UNLEDGERED": "No qualifying estimate was identified at the second full-text "
                             "extraction, and no per-record reason was recorded.",
}


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


# === TERMINAL STATES (replicated from validate_prisma.py, asserted against its output) ===

def terminal_states():
    """The per-record terminal states, as validate_prisma.py computed them.

    This used to be a second copy of that script's fifteen-source precedence chain, with an
    assertion that the two agreed. The assertion did its job when the September behavioural arm was
    folded into the funnel (ruling P1) and only one copy learned about it, which is the argument for
    not having two. validate_prisma.py now writes data/synth/prisma_terminal_states.csv and this
    reads it.
    """
    path = P("data/synth/prisma_terminal_states.csv")
    if not os.path.exists(path):
        raise SystemExit("run scripts/validate_prisma.py first: " + path)
    state = {canon(r["id"]): r["terminal_state"] for r in read_csv(path)}
    ref = json.load(open(P("data/synth/prisma_counts.json"), encoding="utf-8"))["terminal_states"]
    got = dict(Counter(state.values()))
    assert got == ref, ("prisma_terminal_states.csv disagrees with prisma_counts.json:\n"
                        f"  states {got}\n  counts {ref}\nBoth come from validate_prisma.py; "
                        "re-run it.")
    return state


def exclusion_reasons():
    """record key -> (free-text reason, the ledger it came from). Empty where none was logged.

    Sources are consulted in order and the FIRST reason wins, so the order is a precedence: a
    hand-verified per-record ruling before a campaign's batch verdict, and a campaign verdict before
    a generic fallback.

    The second half of this list was added on 2026-09-15. A pre-submission audit found 139 excluded
    records whose reason named a pipeline stage rather than an eligibility criterion, and 102 with
    no per-record reason at all. Most of those reasons did exist — in the campaign files that
    produced the drop rather than in a drop ledger — so the campaigns are read here directly:
    the blind re-extraction's screen, the Step-B / re-exam / rev2 / processing passes, the
    pre-extraction triage, and the v1.7.18 merge changelog. What survived that sweep with no
    recorded reason is listed in data/extract_v2/qa/exclusion_reasons_2026-09-15_REPORT.md and is
    left empty here rather than filled with a guess.
    """
    detail = {}

    def put(key, reason, source):
        k, reason = canon(key), (reason or "").strip()
        if k and reason and k not in detail:
            detail[k] = (reason, source)

    # The dedup ledger first, and only it, for the records it collapsed: those rows are filed under
    # "Duplicate of an included record", so any other file's reading of the same record would
    # contradict the category the row prints.
    for r in read_csv("data/extract_v2/qa/oa_dups_dropped.csv"):
        if r.get("matched_existing"):
            put(r.get("oaid"), f"duplicate of {r['matched_existing']}", "oa_dups_dropped.csv")
    # Then the September blind re-extraction, which screened every study independently, wrote a
    # paragraph per disputed study, and was ruled EXCLUDE_STUDY by the author
    # (full_reextract_2026-09/rulings_sacha_2026-09-10a.csv). It outranks the earlier ledgers: it is
    # the project's latest full-text assessment, and where both speak the earlier entry tends to
    # point at the ruling ("excluded on the blind pass's eligibility finding") while this one states
    # the finding.
    for r in read_csv("data/extract_v2/full_reextract_2026-09/scores/screen_disputes.csv"):
        if (r.get("blind_screen") or "").strip() == "EXCLUDE":
            put(r.get("id"), r.get("reason"), "full_reextract_2026-09/scores/screen_disputes.csv")

    for f in ("data/extract_v2/qa/stepb_drops_queue.csv", "data/extract_v2/qa/decided_drops.csv",
              "data/extract_v2/qa/review_pooled_drops.csv",
              "data/extract_v2/qa/v1.2_drops_ledger.csv",
              "data/extract_v2/qa/prisma_dispositions.csv"):
        for r in read_csv(f):
            put(r.get("id"), r.get("reason"), os.path.basename(f))
    for d in json.load(open(P("data/extract_v2/qa/drop_audit.json"), encoding="utf-8")):
        put(d.get("id"), d.get("drop_reason"), "drop_audit.json")
    for f in (glob.glob(P("data/verify/v_*.csv")) + glob.glob(P("data/verify/adj_*.csv"))
              + glob.glob(P("data/extract_v2/qa/triage_*.csv"))):
        for r in csv.DictReader(open(f, encoding="utf-8", errors="replace")):
            if (r.get("verdict") or "").strip() in ("REJECT", "EXCLUDE"):
                put(r.get("eid") or r.get("id"), r.get("reason"), os.path.basename(f))
    # The September behavioural arm (folded into the funnel by ruling P1). Its full-text screen
    # recorded a reason per record.
    ARM = "data/extract_v2/qa/behavioural_arm/openalex_2026-09"
    for r in read_csv(f"{ARM}/fulltext/screen/screened_all.csv"):
        if (r.get("ruling") or "").strip() in ("EXCLUDE", "UNCERTAIN"):
            put(r.get("oaid"), r.get("reason") or r.get("notes"),
                "behavioural_arm/fulltext/screen/screened_all.csv")

    # --- reasons recovered 2026-09-15 -----------------------------------------------------------
    # Hand-verified, one row per record, for reasons that exist only inside a freeze-application
    # script, a rule file that names the study, or the diff of the commit that removed it. Each row
    # carries the file or commit it was read from, so none of it is this script's invention.
    for r in read_csv("data/extract_v2/qa/exclusion_reasons_recovered_2026-09-15.csv"):
        put(r.get("id"), r.get("reason"), "exclusion_reasons_recovered_2026-09-15.csv")
    # Whole-study exclusions applied at the v1.4.3 freeze, each with the author's reason.
    for r in read_csv("data/extract_v2/qa/v143_exclusions.csv"):
        put(r.get("id"), r.get("reason"), "v143_exclusions.csv")
    # The v1.7.18 merge changelog. `remove` and `skip` rows carry the ruling's own `why`, which is
    # the reason four behavioural-arm studies were dropped after extraction.
    for r in read_csv("data/extract_v2/qa/changelog_v1718.csv"):
        if (r.get("op") or "").strip() in ("remove", "skip"):
            put(r.get("id"), r.get("why"), "changelog_v1718.csv")
    # The full-text passes that rebuilt the corpus between the first and second extraction: Step-B
    # (58 batches over the full-text studies), the rev2 strict re-exam of the low-confidence
    # studies, the 39-study re-exam, the processing pass over the abstract-only tier, and the
    # six-paper full-text upgrade. Each wrote one verdict per study; DROP_STUDY is an exclusion and
    # its `answer`/`notes` field is the reason.
    for f in sorted(glob.glob(P("data/extract_v2/qa/stepb/out_*.json"))
                    + glob.glob(P("data/extract_v2/qa/rev2/r2_out_*.json"))
                    + glob.glob(P("data/extract_v2/qa/reexam/reexam_out_*.json"))
                    + glob.glob(P("data/extract_v2/qa/proc/proc_out_*.json"))
                    + [P("data/extract_v2/qa/upgrade6_out.json")]):
        if not os.path.exists(f):
            continue
        try:
            obj = json.load(open(f, encoding="utf-8", errors="replace"))
        except ValueError:
            continue
        if not isinstance(obj, dict):
            continue
        for k, v in obj.items():
            if isinstance(v, dict) and v.get("verdict") == "DROP_STUDY":
                put(k, v.get("answer") or v.get("notes"),
                    os.path.relpath(f, P("data/extract_v2/qa")))
    # The pre-extraction triage that produced data/extract_v2/qa/dropped_studies.csv, which recorded
    # the id and title but not the call behind it. The call and its rule are here.
    for r in read_csv("data/extract_v2/qa/proposals.csv"):
        if (r.get("proposed_call") or "").strip().upper() in ("DROP", "DISCUSS"):
            note, rule = (r.get("proposed_note") or "").strip(), (r.get("rule") or "").strip()
            put(r.get("id"), f"{note} [rule {rule}]" if rule else note, "proposals.csv")

    # Fallback for any behavioural-arm study removed after extraction that the changelog above did
    # not name.
    for r in read_csv("data/extract_v2/qa/behavioural_arm_dispositions.csv"):
        if r.get("disposition") == "ARM_EXCLUDED_AT_RULING":
            put(r.get("id"), "removed by the author's pre-merge ruling on the behavioural arm",
                "behavioural_arm_dispositions.csv")
    return detail


# === WRITERS ===

def write_included(meta, flow):
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
        rec = {"study_id": sid,
               "first_author": d.get("first_author") or UNKNOWN,
               "year": d.get("year") or UNKNOWN,
               "title": d.get("title") or UNKNOWN,
               "venue": d.get("venue") or UNKNOWN,
               "doi": d.get("doi") or UNKNOWN,
               "constructs": ";".join(sorted(constructs[sid])),
               "n_estimates": n_est[sid],
               "text_basis": basis.get(sid, UNKNOWN),
               "biblio_source": ";".join(sorted(set(d.get("src", {}).values()))) or "none"}
        for f in ("first_author", "year", "title", "venue", "doi"):
            if rec[f] == UNKNOWN:
                gaps[f] += 1
        out.append(rec)

    assert len(out) == flow["included"], \
        f"{len(out)} rows but the flow's included box says {flow['included']}"

    # Alphabetical by first author reads as a reference list; the unresolved ones sort last.
    out.sort(key=lambda r: ((r["first_author"] == UNKNOWN), r["first_author"].lower(),
                            str(r["year"]), r["study_id"]))
    path = P("data/synth/phaseB/si_included_studies.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    return path, out, gaps


def write_exclusions(meta, state, flow):
    # The figure and the list must print the same label set. They share one mapping, so the only
    # way they can differ is if the figure prints a label for a state the mapping does not hold.
    assert {lab for lab, _ in flow["excl_reasons"]} == set(STATE_TO_REASON.values()), \
        ("the flow figure's reason labels differ from make_prisma.EXCL_LABELS:\n"
         f"  figure {sorted(lab for lab, _ in flow['excl_reasons'])}\n"
         f"  mapping {sorted(STATE_TO_REASON.values())}")

    detail = exclusion_reasons()
    out = []
    for k, st in state.items():
        if st not in STATE_TO_REASON:
            continue
        d = meta.get(k, {})
        reason, source = detail.get(
            k, (NO_REASON_BY_STATE.get(st, NO_REASON), "none recorded"))
        out.append({"record_id": k,
                    "title": d.get("title") or "",
                    "exclusion_reason": STATE_TO_REASON[st],
                    "terminal_state": st,
                    "reason_detail": reason,
                    "reason_source": source})

    # THE RECONCILIATION. Per-reason counts must equal the flow figure's, exactly.
    got = Counter(r["exclusion_reason"] for r in out)
    table = []
    for lab, n_flow in flow["excl_reasons"]:
        if n_flow:
            table.append((lab, got.get(lab, 0), n_flow))
            assert got.get(lab, 0) == n_flow, \
                f"reason '{lab}': {got.get(lab, 0)} rows in the list, {n_flow} in the flow"
    assert len(out) == flow["excl_total"], \
        f"{len(out)} exclusion rows but the flow's excluded box says {flow['excl_total']}"

    order = {lab: i for i, (lab, _) in enumerate(flow["excl_reasons"])}
    out.sort(key=lambda r: (order[r["exclusion_reason"]], r["record_id"]))
    path = P("data/synth/phaseB/si_fulltext_exclusions.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    return path, out, table


def write_readme(flow, inc_path, exc_path, included, exclusions, table, gaps):
    ver = flow["ver"]
    no_detail = sum(1 for r in exclusions if r["reason_source"] == "none recorded")
    n_sources = len({r["reason_source"] for r in exclusions} - {"none recorded"})
    rows = "\n".join(f"| {lab} | {a} | {b} |" for lab, a, b in table)
    fields = ("first_author", "year", "venue", "doi")
    unresolved = [r for r in included if any(r[f] == UNKNOWN for f in fields)]
    ul = "\n".join(f"- `{r['study_id']}` — missing "
                   + ", ".join(f.replace("_", " ") for f in fields if r[f] == UNKNOWN)
                   + " — " + (r["title"][:78] + "…" if len(r["title"]) > 79 else r["title"])
                   for r in unresolved) or "- none"

    text = f"""# Supplementary lists — PRISMA 2020 items 16b and 17

Two record-level tables, generated by `scripts/make_si_lists.py` from freeze v{ver} and the PRISMA
reconciliation in `data/synth/prisma_counts.json`. Both are regenerated per freeze; do not hand-edit
them.

## `{os.path.relpath(inc_path, ROOT)}` — item 16b, the included studies

One row per study in the frozen dataset: {flow['included']} studies contributing {flow['n_est']:,}
estimates.

| column | meaning |
|---|---|
| `study_id` | the review's record key (Scopus EID, OpenAlex id, PMID, or a hand-assigned key) |
| `first_author`, `year`, `title`, `venue`, `doi` | bibliography; `unknown` where no source carries it |
| `constructs` | the constructs the study contributes, semicolon-joined |
| `n_estimates` | rows the study contributes to the freeze |
| `text_basis` | `full text` or `abstract only`, from `source_read` in `data/rob/risk_of_bias_v3_master.csv` |
| `biblio_source` | which dumps or lookups supplied the bibliography, for audit |

Fields come from the cached search-arm dumps and `data/synth/venue_types.csv`; the hand-entered
overlay `data/inputs/si_biblio_manual.csv` overrides those, and whatever is still missing is filled
by a DOI content-negotiation lookup cached in `data/synth/si_biblio_cache.json`. Nothing is inferred:
an unsourced field is written `unknown`, and every row's `biblio_source` says which of these
supplied it.

Remaining gaps: {gaps['first_author']} without a first author, {gaps['year']} without a year, {gaps['venue']} without
a venue, {gaps['doi']} without a DOI.

Studies whose bibliographic record is incomplete, of two kinds. Repository deposits (theses and
institutional records) carry an OpenAlex id but no DOI, so they resolve through the OpenAlex work-id
lookup rather than the DOI one. The rest entered as a user-supplied PDF or a seed under a
hand-assigned key: for those the overlay carries what the document's own title page states, and
there is no DOI to fetch anything further from.

{ul}

## `{os.path.relpath(exc_path, ROOT)}` — item 17, the full-text exclusions

One row per record that reached full-text assessment and was excluded ({flow['excl_total']}
records), with the reason category the flow figure groups it under, the terminal state behind that
category, and the free-text reason from the ledger that recorded it, named in `reason_source`.

{flow['excl_total'] - no_detail} of the {flow['excl_total']} rows carry a record-level reason, drawn
from {n_sources} ledgers and campaign files; `reason_source` names the file each came from. The
remaining {no_detail} ({'this row says' if no_detail == 1 else 'these rows say'} so in words rather
than leaving the cell blank) had no ledger, campaign file or ruling recording why the record left,
and nothing is invented to fill the gap. The recovery pass that produced this state, and what it
could and could not reach, is documented in
`data/extract_v2/qa/exclusion_reasons_2026-09-15_REPORT.md`.

## How it reconciles with Supplementary Fig. 1

The reason labels are imported from `make_prisma.EXCL_LABELS`, the table the figure itself draws, and
the script asserts every per-reason count before writing. As of this build:

| exclusion reason | rows in the list | box in the flow |
|---|---|---|
{rows}

The flow's two other non-inclusion outcomes are not exclusions and are not listed here:
{flow['not_retrieved']} reports were not retrieved and {flow['no_data']} were included but
contributed no codeable estimate. The full partition is {flow['included']} included +
{flow['not_retrieved']} not retrieved + {flow['no_data']} without a codeable estimate +
{flow['excl_total']} excluded = {flow['assessed']} reports sought for retrieval.

Regenerate with:

```bash
python3 scripts/validate_prisma.py    # refreshes data/synth/prisma_counts.json
python3 scripts/make_si_lists.py      # add --fetch to refill bibliography gaps from the registries
```
"""
    path = P("docs/SI_lists_README.md")
    open(path, "w", encoding="utf-8").write(text)
    return path


def main():
    fetch = "--fetch" in sys.argv
    flow = make_prisma.load()
    state = terminal_states()

    rows = list(csv.DictReader(open(P(frozen_path()), encoding="utf-8")))
    meta = apply_overlays(biblio_index(), sorted({r["id"] for r in rows}), fetch)

    inc_path, included, gaps = write_included(meta, flow)
    exc_path, exclusions, table = write_exclusions(meta, state, flow)
    readme = write_readme(flow, inc_path, exc_path, included, exclusions, table, gaps)

    print(f"included studies : {len(included):>4}  -> {os.path.relpath(inc_path, ROOT)}")
    print(f"  gaps: {gaps['first_author']} no author, {gaps['year']} no year, "
          f"{gaps['venue']} no venue, {gaps['doi']} no DOI, {gaps['title']} no title")
    print(f"exclusions       : {len(exclusions):>4}  -> {os.path.relpath(exc_path, ROOT)}")
    print(f"                   {os.path.relpath(readme, ROOT)}")
    print("-" * 78)
    print(f"{'exclusion reason':<62}{'list':>6}{'flow':>6}")
    for lab, a, b in table:
        print(f"{lab[:60]:<62}{a:>6}{b:>6}")
    print(f"{'TOTAL':<62}{sum(a for _, a, _ in table):>6}{flow['excl_total']:>6}")
    print("-" * 78)
    print(f"reconciles: {flow['included']} included + {flow['not_retrieved']} not retrieved + "
          f"{flow['no_data']} no codeable estimate + {flow['excl_total']} excluded "
          f"= {flow['assessed']}")


if __name__ == "__main__":
    main()
