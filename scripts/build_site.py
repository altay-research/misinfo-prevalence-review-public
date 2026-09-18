#!/usr/bin/env python3
"""build_site.py — generate the public companion site from the frozen dataset.

Reads the freeze named in docs/FROZEN.md plus the Phase B outputs, and writes site/ :
a static, dependency-free site served by GitHub Pages from the public replication repo.

  site/data/meta.json        freeze version, MD5, canonical counts, build date
  site/data/estimates.json   one record per estimate, with a stable content-hash id
  site/data/studies.json     study metadata, keyed by study_id
  site/data/slices.json      the published single-moderator tables, verbatim
  site/figures/*.svg         the article figures
  site/**/*.html             pages, copied from site_src/ with numbers injected

Sources of record:
  - estimate fields            data/synth/phaseB/estimates_full.json (phaseB_export_json.py)
  - study metadata + RoB       data/synth/phaseB/si_study_characteristics.csv   [443/443]
  - published slice tables     data/synth/phaseB/slices_*.csv
  - aggregation rule           scripts/lib_slices.py

Every number rendered into a page comes from these files. None is typed. check_site.py asserts it.
"""
import ast, csv, hashlib, json, re, shutil, sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib_slices import sl, el, iqr, group_by_study

# The public repo the "flag a coding error" links point at. Change here, nowhere else.
REPO = "altay-research/misinfo-prevalence-review-public"

# The preprint. Set this the day it goes up and rebuild; every link to it across the site comes
# from here. Until then the masthead link is absent and the citation says so rather than pointing
# at nothing. check_site.py asserts that a set URL actually reaches the pages.
PREPRINT_URL = None        # e.g. "https://osf.io/preprints/psyarxiv/XXXXX"

# The submission form. A static page cannot receive a POST, so the form posts to a Cloudflare
# Worker (worker/) which files the submission as an issue in a PRIVATE triage repository. Until
# both of these are set the site falls back to the GitHub issue links, which need an account.
# SETUP.md in worker/ has the two steps.
SUBMIT_ENDPOINT = "https://misinfo-prevalence-submit.sacha-altay.workers.dev"
TURNSTILE_SITEKEY = "0x4AAAAAAE76FRJFyjbY2FJl"   # public half; the secret lives in the Worker

ROOT = Path(__file__).resolve().parents[1]
SRC  = ROOT / "site_src"
OUT  = ROOT / "site"
PHB  = ROOT / "data/synth/phaseB"

# ---------------------------------------------------------------- freeze identity
FROZEN = (ROOT / "docs/FROZEN.md").read_text()
FREEZE_VERSION = re.search(r"# FROZEN DATASET (v[\d.]+)", FROZEN).group(1)
FREEZE_FILE    = re.search(r"File:\s*(\S+)", FROZEN).group(1)
FREEZE_MD5     = re.search(r"MD5:\s*([0-9a-f]{32})", FROZEN).group(1)

# ---------------------------------------------------------------- field policy
# Dropped from the site entirely, with reasons:
#   within_misinfo  — 0% filled in the freeze; a dead column.
#   row             — the freeze's row index; internal, and not stable across freezes.
#   n               — the parsed integer; n_raw carries the same fact in the study's own words.
#   denom2          — a two-way collapse of denom_class; used for analysis, redundant on a record.
DROP = {"within_misinfo", "row", "n", "denom2"}

# Explorer controls and codebook entries: fields coded on effectively the whole corpus, with the
# redundant ones removed. Measured on the corpus rather than judged by eye:
#   ground_truth <-> id_method      97.1% mutually determined, same five levels, different wording
#   sampling_frame -> sampling     100% determined; `sampling` is a strict collapse of it
#   platform -> platform_norm      100% determined; platform_norm is the tidied spelling
# The finer or better-worded member of each pair is kept. Blank is a level with its own meaning,
# never hidden.
# `measurement` rejoined the list on 2026-09-18, when phaseB_prep_regression.py stopped joining it
# from the 317-study appraisal file and derived it from construct instead. It is now coded for every
# study in the six prevalence constructs and NA for QUALITY and OTHER, which are never pooled.
CONTROLS = ["construct", "measurement", "ground_truth", "classification_level", "breadth",
            "denom_class", "sampling_frame", "platform_norm", "topic", "country_scope"]

# Which figures belong on the overview; the rest go in the Methods gallery. Declared once so no
# figure can appear in both places or in neither, which check_site.py asserts.
OVERVIEW_FIGURES = {("main", 4), ("main", 5)}

# Figures the site does not carry at all. PRISMA is a reporting-standard diagram for a reader of the
# article, not a descriptive of the corpus, and Sacha cut it on 2026-09-18. Recorded here rather
# than simply left out, so check_site.py can tell "deliberately absent" from "silently lost".
OMITTED_FIGURES = {("main", 6)}

# The overview's tiles ARE Figure 3, which is why that figure moved to Methods: the same six
# study-level medians, each with the denominator named in the phrase rather than in an axis label.
# Colour encodes the kind of evidence, never the size of the number — position already encodes
# value, and the article's figures deliberately avoid that double encoding.
TILES = [
    ("EXPOSURE",      "behavioural", "of what people consume online is misinformation"),
    ("REACH",         "behavioural", "of people encounter it at least once"),
    ("SHARING",       "behavioural", "of sharing acts carry misinformation"),
    ("RECALL_shared", "surveys",     "say they have shared it"),
    ("CONTENT",       "coded content", "of items in a sampled corpus are misinformation"),
    ("RECALL_seen",   "surveys",     "say they have seen it"),
    ("CONCENTRATION", "behavioural", "of misinformation activity comes from the top 1% of users"),
]
EVIDENCE_COLOUR = {"behavioural": "t-beh", "surveys": "t-self", "coded content": "t-content"}

LABEL = {
    "construct": "What is measured",        "ground_truth": "Who decided",
    "id_method": "How identified",          "classification_level": "Judged at",
    "breadth": "Definitional breadth",      "denom_class": "Denominator",
    "sampling": "Sampling",                 "sampling_frame": "Sampling frame",
    "measurement": "Kind of evidence",      "platform_norm": "Platform",
    "platform": "Platform",
    "topic": "Topic",
    "country_scope": "Country scope",       "country": "Country",
    "unit": "Unit counted",                       "rob": "Risk of bias",
    "date": "Data collected",               "n_raw": "Sample",
}

CONSTRUCT_NAME = {
    "EXPOSURE": "audience exposure", "REACH": "reach", "RECALL": "self-reported recall",
    "SHARING": "sharing", "CONTENT": "content prevalence", "CONCENTRATION": "concentration",
    "QUALITY": "quality score", "OTHER": "other",
}
PREV = ["EXPOSURE", "REACH", "RECALL", "SHARING", "CONTENT", "CONCENTRATION"]

# Values that read as jargon on a public page. Display only; the underlying code is unchanged.
VALUE_LABEL = {
    "domain_list": "domain list",          "fact_checker": "fact-checkers",
    "researcher_coding": "researchers",    "self_report": "respondents themselves",
    "classifier": "automated classifier",  "NewsGuard": "NewsGuard",
    "source_level": "whole sources",       "claim_level": "individual claims",
    "post_level": "individual posts",      "self_perceived": "respondent's own judgement",
    "topic_level": "topics",               "mixed": "mixed levels",
    "news_diet": "a news diet",            "all_media": "a whole media diet",
    "political_news": "political news",    "population": "a population",
    "topical": "one topic",                "curated_sample": "a curated sample",
    "single_source": "a single source",    "n/a": "not applicable",
    "whole_diet": "whole diet",            "narrow": "narrow",
    "fabricated": "fabricated only",       "false": "false content",
    "misleading": "false or misleading",   "not_stated": "no per-item standard stated",
    "single": "one country",               "multi": "several countries",
    "global": "global or cross-national",  "not_reported": "not reported",
    "representative": "representative",
    "topical/curated": "topical or curated", "other": "other",
}

# Some codes mean different things in different columns: `survey` is a sampling frame in one and a
# medium in another, so a single flat map mislabels one of them. Field-specific labels win.
FIELD_VALUE_LABEL = {
    "sampling":        {"survey": "survey sample"},
    "sampling_frame":  {"survey_sample": "survey sample", "panel_trace": "behavioural panel",
                        "full_census": "full census", "keyword_topical": "keyword or topical",
                        "curated_seed": "curated seed", "random_platform": "random platform",
                        "convenience_snowball": "convenience snowball",
                        "curated_business_pages": "curated business pages"},
    "platform":        {"survey": "survey", "web_cross_platform": "web, cross-platform",
                        "multi_platform": "several platforms", "other": "other platform"},
    "platform_norm":   {"survey": "survey", "web_cross_platform": "web, cross-platform",
                        "multi_platform": "several platforms", "other": "other platform"},
    "topic":           {"covid19": "COVID-19", "crime_society": "crime and society",
                        "economy_finance": "economy and finance", "general_news": "general news",
                        "health_other": "health (other)", "politics_elections": "politics and elections",
                        "science_other": "science (other)", "vaccines": "vaccines (non-COVID)",
                        "war_geopolitics": "war and geopolitics", "other": "other topic"},
    "country_scope":   {"multi": "several countries"},
    "measurement":     {"BEHAVIOURAL": "behavioural traces", "CONTENT_CODING": "coded content",
                        "SELF_REPORT": "self-report", "NA": "not one of the six constructs"},
    "unit":            {"exposure": "exposures", "reach": "people reached", "item": "items",
                        "post": "posts", "claim": "claims", "source": "sources",
                        "account": "accounts", "person": "people", "user": "users"},
}


def norm(rec):
    """Display-side normalisations. Each one is a coding artefact, not a judgement change."""
    # One row carries `single_country` where 788 carry `single`. Same level, one late-arriving
    # study (2-s2.0-85145196122, restored at v1.7.21). Touches no published number: country_scope
    # appears in no manuscript statistic. Normalised here rather than re-freezing for one cell.
    if rec.get("country_scope") == "single_country":
        rec["country_scope"] = "single"
    # A blank breadth is a finding, not a gap: 20% of studies state no per-item veracity standard,
    # and they are almost all the studies that classify whole sources (manuscript 2.2).
    if not rec.get("breadth"):
        rec["breadth"] = "not_stated"
    for f in ("country_scope", "denom_class", "classification_level", "sampling_frame",
              "unit", "country", "platform", "date"):
        if not rec.get(f):
            rec[f] = "not_reported"
    return rec


def stable_id(rec, taken):
    """Content-addressed estimate id: survives re-ordering across freezes, changes only when the
    estimate's own content changes. `row` would break every permalink on the next re-freeze."""
    seed = "|".join(str(rec.get(k, "")) for k in ("id", "construct", "value_raw", "quote", "denominator"))
    for width in range(7, 33):
        h = hashlib.blake2s(seed.encode("utf-8"), digest_size=16).hexdigest()[:width]
        if h not in taken:
            taken.add(h)
            return h
    raise RuntimeError("could not allocate a unique estimate id")


# Columns taken straight from the freeze and joined by row index. estimates_full.json is built by
# enumerating the same CSV in the same order (phaseB_export_json.py), so position is the join key;
# build_estimates asserts study-id alignment on every row rather than trusting that.
FREEZE_EXTRA = [
    "recall_subtype",       # seen vs shared: the split behind the paper's 57.7 / 19.8 contrast
    "moderator_quote",      # the sentence justifying the CODING, distinct from the value's quote
    "moderator_coder",      # who or what coded it
    "confidence",           # the extraction's own confidence in the row
    "question_type",        # for surveys, what the question asked
    "value_kind",           # proportion / range_not_point / per_capita_intensity
    "source",               # where in the paper the number was read from
    "ground_truth_detail",  # free text on how ground truth was established
    "denom_scope", "denom_selection",
    "conc_group_pct", "conc_share_pct", "conc_unit", "conc_dimension",
    "year", "era", "country_norm", "platform_norm",
    "demographic_group", "political_orientation", "data_provenance",
]


def build_estimates():
    raw = json.load(open(PHB / "estimates_full.json"))
    freeze = list(csv.DictReader(open(ROOT / FREEZE_FILE)))
    if len(freeze) != len(raw):
        raise SystemExit(f"freeze has {len(freeze)} rows, estimates_full.json has {len(raw)}; "
                         "re-run phaseB_export_json.py")
    taken, out = set(), []
    for i, rec in enumerate(raw):
        fz = freeze[i]
        if (fz.get("id") or "").strip() != rec["id"]:
            raise SystemExit(f"row {i}: freeze id {fz.get('id')!r} != export id {rec['id']!r}")
        rec = dict(rec)
        for f in FREEZE_EXTRA:
            rec[f] = (fz.get(f) or "").strip()
        rec = norm(rec)
        e = {k: v for k, v in rec.items() if k not in DROP}
        # Trim the long free-text fields; the full values ship in the CSV download.
        for f in ("quote", "definition", "measure_type", "denominator", "n_raw", "title",
                  "moderator_quote", "ground_truth_detail", "data_provenance"):
            if e.get(f):
                e[f] = e[f][:600]
        e["eid"] = stable_id(rec, taken)
        out.append(e)
    return out


def build_studies():
    studies = {}
    for r in csv.DictReader(open(PHB / "si_study_characteristics.csv")):
        studies[r["study_id"]] = {
            "author": r["first_author"], "year": r["year"], "title": r["title"],
            "venue": r["venue"], "doi": r["doi"], "country": r["country"],
            "platform": r["platform"], "constructs": r["constructs"],
            "n_estimates": int(r["n_estimates"] or 0),
            # RoB from the 443/443 characteristics table, NOT from the estimate rows: the estimate
            # field is joined from a v1.4.5 file and is blank on 371 of 1,048 rows.
            "rob": r["risk_of_bias"],
            "read_from": r.get("read_from", ""),
        }
    return studies


# The six prevalence constructs. phaseB_slices.py restricts most of its tables to these, so QUALITY
# and OTHER rows are in the main analysis set but not in the published slices.
PREV_ONLY = PREV


def build_slices(est):
    """Ship the published tables verbatim. One exclusion, and one recomputation, both documented."""
    out, notes = {}, {}
    for p in sorted(PHB.glob("slices_*.csv")):
        name = p.stem.replace("slices_", "")
        rows = list(csv.DictReader(open(p)))
        out[name] = rows
    return out, notes


def headline(est):
    """The overview's tiles, computed rather than typed. Every value here is a published statistic:
    the six construct medians from slices_by_construct.csv, the recall split from recall_split.csv,
    and the concentration figure from the studies reporting exactly the top 1%."""
    by_con = {r["value"]: r for r in csv.DictReader(open(PHB / "slices_by_construct.csv"))}
    split  = {r["group"]: r for r in csv.DictReader(open(PHB / "recall_split.csv"))}

    def from_construct(c):
        r = by_con[c]
        return {"median": float(r["sl_median"]), "k": int(r["n_studies"]), "iqr": r["sl_iqr"]}

    def from_split(g):
        r = split[g]
        return {"median": float(r["median"]), "k": int(r["k_studies"]),
                "iqr": f"{r['iqr_lo']}–{r['iqr_hi']}", "ci": f"{r['ci_lo']}–{r['ci_hi']}"}

    conc = list(csv.DictReader(open(PHB / "concentration_standardized.csv")))

    def thresholds(keep):
        by = {}
        for r in conc:
            try:
                t = float(r["top_pct_people"])
            except ValueError:
                continue                      # a status-defined group, not a volume percentile
            if keep(t):
                by.setdefault(r["id"], []).append(float(r["activity_share_pct"]))
        return by

    n1, m1, *_ = sl(thresholds(lambda t: t == 1.0))
    nb, mb, *_ = sl(thresholds(lambda t: t <= 1.0))
    if m1 is None or mb is None:
        raise SystemExit("concentration_standardized.csv: no rows at the top-1% threshold")

    out = {
        "EXPOSURE": from_construct("EXPOSURE"), "REACH": from_construct("REACH"),
        "SHARING": from_construct("SHARING"), "CONTENT": from_construct("CONTENT"),
        "RECALL_seen": from_split("RECALL_exposure"), "RECALL_shared": from_split("RECALL_sharing"),
        "CONCENTRATION": {"median": m1, "k": n1, "band_median": mb, "band_k": nb},
    }
    # kept under their old names so nothing downstream has to change
    out["exposure"], out["reach"] = out["EXPOSURE"], out["REACH"]
    out["recall_seen"], out["recall_shared"] = out["RECALL_seen"], out["RECALL_shared"]
    out["concentration"] = out["CONCENTRATION"]
    out["contrast"] = round(out["RECALL_seen"]["median"] / out["REACH"]["median"], 1)
    return out


def tiles_html(head):
    """Ordered smallest to largest, the way Figure 3 orders them, with concentration last because
    it is a different quantity from the six."""
    rows = sorted(TILES[:-1], key=lambda t: head[t[0]]["median"]) + [TILES[-1]]
    out = []
    for key, evidence, phrase in rows:
        h = head[key]
        val = f"{h['median']:.0f}" if key == "CONCENTRATION" else f"{h['median']}"
        cls = "t-conc" if key == "CONCENTRATION" else EVIDENCE_COLOUR[evidence]
        extra = (f'<span class="k2">{head["CONCENTRATION"]["band_median"]:.1f}% across the '
                 f'{head["CONCENTRATION"]["band_k"]} studies reporting the top 1% or less</span>'
                 if key == "CONCENTRATION" else "")
        out.append(f'<div class="tile {cls}"><b>{val}%</b><p>{phrase}</p>'
                   f'<span class="k">{h["k"]} studies · {evidence}</span>{extra}</div>')
    return "\n    ".join(out)


def crosswalk_counts():
    """Read the canonical counts from docs/counts_crosswalk.md. That file is generated by
    make_counts_crosswalk.py and its drift check fails if any current doc contradicts it, so it is
    the right place to take a corpus count from."""
    text = (ROOT / "docs/counts_crosswalk.md").read_text()
    want = {
        "db_records":   r"Records identified — databases \| ([\d,]+)",
        "other_records": r"Records identified — other methods \| ([\d,]+)",
        "sought":       r"Reports sought for retrieval \| ([\d,]+)",
        "not_retrieved": r"Not retrieved \| ([\d,]+)",
        "included":     r"\*\*Included studies\*\* \| \*\*([\d,]+)\*\*",
        "estimates":    r"\*\*Estimates \(all\)\*\* \| \*\*([\d,]+)\*\*",
        "main_est":     r"Estimates in the main analysis set \| ([\d,]+)",
        "main_studies": r"Studies in the main analysis set \| ([\d,]+)",
        "rob":          r"Studies with a risk-of-bias appraisal \| ([\d,]+)",
    }
    out = {}
    for k, pat in want.items():
        m = re.search(pat, text)
        if not m:
            raise SystemExit(f"counts_crosswalk.md: could not read {k}")
        out[k] = m.group(1)
    return out


def copy_downloads():
    """The files offered on /data/. The frozen dataset itself is the primary one."""
    dl = OUT / "downloads"
    dl.mkdir(parents=True, exist_ok=True)
    sources = {
        "misinfo_prevalence_estimates.csv": ROOT / FREEZE_FILE,
        "included_studies.csv":             PHB / "si_included_studies.csv",
        "study_characteristics.csv":        PHB / "si_study_characteristics.csv",
        "fulltext_exclusions.csv":          PHB / "si_fulltext_exclusions.csv",
    }
    out = {}
    for name, src in sources.items():
        if src.exists():
            shutil.copy(src, dl / name)
            out[name] = (dl / name).stat().st_size
    return out


def figures_from_manuscript():
    """The site's figures ARE the manuscript's, read out of scripts/make_nhb_docx.py rather than
    listed again here. A second list would drift: the first version of this script hard-coded
    fallback paths and had five of the six main figures pointing at the wrong SVG, which went
    unnoticed because the submission folder happened to exist and was preferred."""
    src = (ROOT / "scripts/make_nhb_docx.py").read_text()
    out = []
    for name, kind in (("MAIN_FIGS", "main"), ("SUPP_FIGS", "supplementary")):
        m = re.search(rf"^{name} = (\[.*?^\])", src, re.S | re.M)
        if not m:
            raise SystemExit(f"could not read {name} from make_nhb_docx.py")
        for label, caption, path in ast.literal_eval(m.group(1)):
            num = re.search(r"(\d+)", label).group(1)
            slug = "supplementary_figure_" if kind == "supplementary" else "figure_"
            ref = (kind, int(num))
            where = ("omitted" if ref in OMITTED_FIGURES
                     else "overview" if ref in OVERVIEW_FIGURES else "descriptives")
            out.append({"kind": kind, "label": label.rstrip("."), "n": int(num), "where": where,
                        "caption": caption, "src": path, "file": f"{slug}{num}.svg"})
    return out


def main():
    est = build_estimates()
    studies = build_studies()
    slices, slice_notes = build_slices(est)
    head = headline(est)
    figures = figures_from_manuscript()

    main_set = [e for e in est if e["main"] and e.get("value") is not None]
    meta = {
        "freeze": FREEZE_VERSION, "freeze_file": FREEZE_FILE, "freeze_md5": FREEZE_MD5,
        "built": date.today().isoformat(),
        "n_estimates": len(est), "n_studies": len(studies),
        "n_main_estimates": len(main_set), "n_main_studies": len({e["id"] for e in main_set}),
        "controls": CONTROLS, "labels": LABEL, "value_labels": VALUE_LABEL,
        "construct_names": CONSTRUCT_NAME, "construct_order": PREV,
        "field_value_labels": FIELD_VALUE_LABEL,
        "headline": head, "slice_notes": slice_notes, "repo": REPO,
        "preprint": PREPRINT_URL, "submit_endpoint": SUBMIT_ENDPOINT,
        "turnstile_sitekey": TURNSTILE_SITEKEY,
        "counts": crosswalk_counts(),
        "figures": figures,
    }

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "data").mkdir(parents=True)
    (OUT / "figures").mkdir(parents=True)

    def dump(name, obj):
        p = OUT / "data" / name
        p.write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")))
        return p.stat().st_size

    downloads = copy_downloads()
    meta["downloads"] = {k: round(v / 1024) for k, v in downloads.items()}
    sizes = {
        "meta.json": dump("meta.json", meta),
        "estimates.json": dump("estimates.json", est),
        "studies.json": dump("studies.json", studies),
        "slices.json": dump("slices.json", slices),
    }

    for f in figures:
        if f["where"] == "omitted":
            continue
        src = ROOT / f["src"]
        if not src.exists():
            raise SystemExit(f"figure missing: {f['src']} (named by make_nhb_docx.py as {f['label']})")
        shutil.copy(src, OUT / "figures" / f["file"])

    # pages: copy site_src, substituting {{TOKENS}}
    tokens = {
        "FREEZE": FREEZE_VERSION, "BUILT": meta["built"],
        "N_EST": f"{meta['n_estimates']:,}", "N_STUDIES": str(meta["n_studies"]),
        "N_MAIN_EST": f"{meta['n_main_estimates']:,}", "N_MAIN_STUDIES": str(meta["n_main_studies"]),
        "EXPOSURE": f"{head['exposure']['median']}", "EXPOSURE_K": str(head["exposure"]["k"]),
        "REACH": f"{head['reach']['median']}", "REACH_K": str(head["reach"]["k"]),
        "RECALL": f"{head['recall_seen']['median']}", "RECALL_K": str(head["recall_seen"]["k"]),
        "CONC": f"{head['concentration']['median']:.0f}", "CONC_K": str(head["concentration"]["k"]),
        "CONC_BAND": f"{head['concentration']['band_median']:.1f}",
        "CONC_BAND_K": str(head["concentration"]["band_k"]),
        "CONTRAST": f"{head['contrast']}",
        "TILES": tiles_html(head),
    }
    for k, v in meta["counts"].items():
        tokens["C_" + k.upper()] = v
    for p in sorted(SRC.rglob("*")):
        if p.is_dir() or p.name.startswith("."):
            continue
        dst = OUT / p.relative_to(SRC)
        dst.parent.mkdir(parents=True, exist_ok=True)
        if p.suffix in (".html", ".css", ".js"):
            text = p.read_text()
            for k, v in tokens.items():
                text = text.replace("{{" + k + "}}", v)
            left = re.findall(r"\{\{([A-Z_]+)\}\}", text)
            if left:
                raise SystemExit(f"unsubstituted token(s) in {p.relative_to(ROOT)}: {sorted(set(left))}")
            dst.write_text(text)
        else:
            shutil.copy(p, dst)

    print(f"site built — freeze {FREEZE_VERSION}, {meta['n_estimates']:,} estimates / "
          f"{meta['n_studies']} studies")
    for k, v in sizes.items():
        print(f"  data/{k:16s} {v/1024:8.1f} KB")
    print(f"  headline: exposure {tokens['EXPOSURE']}% (k={tokens['EXPOSURE_K']}) · "
          f"reach {tokens['REACH']}% (k={tokens['REACH_K']}) · "
          f"recall-seen {tokens['RECALL']}% (k={tokens['RECALL_K']}) · "
          f"top-1% {tokens['CONC']}% (k={tokens['CONC_K']}) · contrast {tokens['CONTRAST']}x")


if __name__ == "__main__":
    main()
