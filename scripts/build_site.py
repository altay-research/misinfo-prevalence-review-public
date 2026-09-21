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
PAPER_PDF = "docs/preprint/Altay_Systematic_Review_Misinfo.pdf"

# The preprint. Set this the day it goes up and rebuild; every link to it across the site comes
# from here. Until then the masthead link is absent and the citation says so rather than pointing
# at nothing. check_site.py asserts that a set URL actually reaches the pages.
PREPRINT_URL = "https://osf.io/preprints/psyarxiv/sgvr8"   # versionless: follows the latest version

# The submission form. A static page cannot receive a POST, so the form posts to a Cloudflare
# Worker (worker/) which files the submission as an issue in a PRIVATE triage repository. Until
# both of these are set the site falls back to the GitHub issue links, which need an account.
# SETUP.md in worker/ has the two steps.
SUBMIT_ENDPOINT = "https://misinfo-prevalence-submit.sacha-altay.workers.dev"
TURNSTILE_SITEKEY = "0x4AAAAAAE76FRJFyjbY2FJl"   # public half; the secret lives in the Worker

AUTHOR = {"name": "Sacha Altay",
          "affiliation": "Department of Political Science, University of Zurich"}
LICENCE = {"data": "CC BY 4.0", "code": "MIT"}          # as LICENSE in the public package
# The site's path on its host. Only 404.html needs it: GitHub Pages serves that page at whatever
# address was missing, so its own links cannot be relative.
SITE_PATH = "/misinfo-prevalence-review-public/"
# Cloudflare Web Analytics: no cookies, no personal data, one script tag. Create the site under
# Cloudflare -> Web Analytics -> Add a site (hostname altay-research.github.io), paste the token
# here and rebuild. None ships no script at all.
ANALYTICS_TOKEN = None
ANALYTICS_SNIPPET = ('<script defer src="https://static.cloudflareinsights.com/beacon.min.js" '
                     'data-cf-beacon=\'{"token": "%s"}\'></script>')

# What each coded field and each of its levels means, in one line, from docs/CODEBOOK_estimates.md
# and docs/moderator_codebook.md. Rendered on the Descriptives page under each chart, which is
# where every record's field label links. A level absent from the data is simply not shown.
FIELD_DEFS = {
    "construct": {
        "def": "What the percentage is a share of. The denominator sets the construct, never the "
               "topic or what is counted in the numerator.",
        "levels": {
            "EXPOSURE": "the share of a person's actual information diet (visits, views, time) that is misinformation, from behavioural records",
            "REACH": "the share of people who encountered misinformation at least once, from behavioural records",
            "RECALL": "the share of people who say they have seen or shared misinformation, from surveys",
            "SHARING": "the share of shares, posts or links that carry misinformation, from behavioural records",
            "CONTENT": "the share of items in a sampled corpus (posts, videos, articles) classified as misinformation",
            "CONCENTRATION": "the share of all misinformation activity accounted for by the most active users or sources",
            "QUALITY": "a source or content quality rating that is not a veracity judgement; never pooled with prevalence",
            "OTHER": "a composition or other quantity outside the six constructs; never pooled",
        }},
    "measurement": {
        "def": "The kind of evidence, derived from the construct.",
        "levels": {
            "CONTENT_CODING": "researchers, fact-checkers or classifiers judged sampled items",
            "SELF_REPORT": "respondents answered a survey question",
            "BEHAVIOURAL": "records of what people actually saw, visited or shared",
            "NA": "quality scores and other quantities outside the six constructs",
        }},
    "ground_truth": {
        "def": "Who decided what counted as misinformation.",
        "levels": {
            "researcher_coding": "the authors or trained coders, following a codebook",
            "domain_list": "a list of unreliable sources such as NewsGuard or the Grinberg lists; everything from a listed source counts",
            "self_report": "the respondents' own judgement of what they saw",
            "fact_checker": "verdicts of professional fact-checkers or an expert panel, claim by claim",
            "classifier": "an automated classifier or suspicion score",
        }},
    "classification_level": {
        "def": "Whether misinformation was judged per source or per item. Claim-level judgement "
               "finds several times more than source-level.",
        "levels": {
            "claim_level": "each item, post or claim was classified on its own content",
            "source_level": "whole outlets or accounts were classified and everything they published counts; a lower bound on false items",
            "mixed": "both levels were used",
            "post_level": "each post was classified",
            "topic_level": "whole topics were classified",
            "self_perceived": "the respondent judged for themselves",
            "not_reported": "the paper does not say",
        }},
    "breadth": {
        "def": "How wide the veracity net is, where the definition sets a per-item standard.",
        "levels": {
            "fabricated": "invented or hoax content only",
            "false": "verifiably false against a ground truth",
            "misleading": "false or misleading, including manipulated or missing-context content",
            "not_stated": "no per-item veracity standard: typically source lists and quality ratings",
        }},
    "denom_class": {
        "def": "The universe the percentage is a share of. If the percentage were 100%, what would "
               "that mean?",
        "levels": {
            "population": "a defined group of people: respondents, panellists, users",
            "all_media": "everything a person consumed, news and non-news",
            "news_diet": "all the news a person consumed, on any topic",
            "political_news": "political or election news only",
            "topical": "content on one issue, typically a keyword or hashtag corpus",
            "curated_sample": "a hand-picked set with no natural total, such as the most-shared posts or fact-check-seeded items",
            "single_source": "one account, channel, outlet or platform feature",
            "n/a": "no denominator by construction: concentration estimates",
            "not_reported": "the fused class was not filled on this row; its scope is coded separately",
        }},
    "sampling_frame": {
        "def": "How the data were drawn.",
        "levels": {
            "keyword_topical": "a keyword or hashtag search",
            "survey_sample": "survey respondents",
            "convenience": "a convenience or non-representative sample",
            "panel_trace": "a behavioural panel: web tracking, browsing or voter-file panels",
            "full_census": "a full platform census or firehose",
            "curated_seed": "a set seeded from fact-checks or a known-misinformation list",
            "purposive": "a purposive selection by the researchers",
            "random_platform": "a random or representative sample of the platform",
            "convenience_snowball": "convenience plus snowball recruitment",
            "curated_business_pages": "a curated set of business pages",
            "not_reported": "the paper does not say",
        }},
    "platform_norm": {
        "def": "The platform or medium, with the papers' 274 spellings collapsed. For surveys it is "
               "the frame of the question, not a measured source.",
        "levels": {
            "survey": "a survey question, not a measured platform",
            "web_cross_platform": "browsing or tracking data across the web",
            "multi_platform": "several platforms measured together",
            "other": "a platform outside the named list",
        }},
    "topic": {
        "def": "The subject of the misinformation studied, one code per study. COVID vaccines count "
               "as COVID-19; a whole-diet or domain-list study is general news.",
        "levels": {
            "health_other": "health topics other than COVID-19",
            "general_news": "no single subject: whole diets, domain lists, general news",
            "covid19": "COVID-19, including its vaccines",
            "vaccines": "vaccines other than COVID-19",
            "other": "a subject outside the list",
        }},
    "country_scope": {
        "def": "How many countries the estimate covers.",
        "levels": {
            "single": "one country",
            "multi": "several named countries",
            "global": "worldwide or unspecified",
            "not_reported": "the paper does not say",
        }},
    "rob": {
        "def": "Risk of bias on the Hoy prevalence instrument, adapted for this review (Methods 4.7). "
               "LOW: 0 to 2 items at high risk with the two design items low. MODERATE: 3 to 5, or "
               "one design item high. HIGH: 6 or more, or both design items high.",
        "levels": {}},
}

ROOT = Path(__file__).resolve().parents[1]
# In the working repository the site lives at the root; the public package publishes it under
# companion/ (build_public_package.py remaps it). Resolve whichever layout this checkout has.
SRC  = ROOT / "site_src" if (ROOT / "site_src").is_dir() else ROOT / "companion" / "site_src"
OUT  = ROOT / "site" if (ROOT / "site_src").is_dir() else ROOT / "companion" / "site"
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
        # Each tile opens the slice it summarises. The five constructs open the Build tab with
        # that construct chosen; the two recall tiles are the seen/shared split, which the Build
        # tab does not make, so they open the estimate list filtered to recall instead.
        href = (f"estimates/#construct=RECALL" if key.startswith("RECALL")
                else f"explore/#construct={key}&tab=build")
        out.append(f'<a class="tile {cls}" href="{href}"><b>{val}%</b><p>{phrase}</p>'
                   f'<span class="k">{h["k"]} studies · {evidence}</span>{extra}</a>')
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
        # the paper itself, so a reader can take it away without leaving for OSF
        "Altay_Systematic_Review_Misinfo.pdf": ROOT / PAPER_PDF,
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


def site_figure_4(svg):
    """Two changes the site's copy of Figure 4 carries and the article's does not.

    The article's figure is fixed: it is in the posted preprint and in a hand-formatted docx that
    AUTHORITATIVE_FILES.txt forbids regenerating. The site is free to be clearer, so its copy gets
    an x-axis title, and the per-band study totals move into the `n =` column on the right, where
    they sit on the same edge as the counts they belong with. Applied to the rendered SVG so the
    article's figure is untouched.
    """
    m = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg)
    if not m:
        raise SystemExit("figure 4: no viewBox to extend for the axis title")
    W, H = int(m.group(1)), int(m.group(2))
    NEW_H = H + 22
    svg = svg.replace(f'viewBox="0 0 {W} {H}"', f'viewBox="0 0 {W} {NEW_H}"', 1)
    # the white backing rect has to grow with it, or the added strip renders transparent
    svg = svg.replace(f'height="{H}.0"', f'height="{NEW_H}.0"', 1)

    # The band totals ("446 studies") are placed just after their band label, so each lands at a
    # different x. Move them onto the right-hand edge the `n = ` values already use.
    mm = re.search(r'<text x="([\d.]+)"[^>]*>n = \d+</text>', svg)
    if mm:
        right = mm.group(1)
        svg = re.sub(r'<text x="[\d.]+"([^>]*?)text-anchor="start"([^>]*>\d+ studies</text>)',
                     lambda g: f'<text x="{right}"{g.group(1)}text-anchor="end"{g.group(2)}', svg)

    cx = 250 + (W - 250 - 60) / 2
    return svg.replace('</svg>',
                       f'<text x="{cx:.1f}" y="{NEW_H - 6}" font-size="12.5" text-anchor="middle" '
                       f'fill="#666">Prevalence of misinformation</text></svg>')


def site_figure_5(svg):
    """Drop the two panel subtitles from the site's copy of the concentration figure.

    "5 studies reporting the top 1%" and "4 panels, 6 estimates" are the kind of caption detail the
    article carries under its figure anyway; on the page they read as clutter under two short
    headings. The article's copy keeps them, since it is in the posted preprint.
    """
    out, dropped = svg, 0
    for label in ("5 studies reporting the top 1%", "4 panels, 6 estimates"):
        m = re.search(r"<text[^>]*>" + re.escape(label) + r"</text>", out)
        if not m:
            raise SystemExit(f"figure 5: subtitle not found, has the figure changed? {label!r}")
        out = out[:m.start()] + out[m.end():]
        dropped += 1
    if dropped != 2:
        raise SystemExit("figure 5: expected to drop exactly two subtitles")
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
        "author": AUTHOR, "licence": LICENCE, "field_defs": FIELD_DEFS, "site_path": SITE_PATH,
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
        transform = {"figure_4.svg": site_figure_4, "figure_5.svg": site_figure_5}.get(f["file"])
        if transform:
            (OUT / "figures" / f["file"]).write_text(transform(src.read_text()))
            continue
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
        "SITE_PATH": SITE_PATH,
        # baked in rather than read from meta.json at runtime: the two files cache independently,
        # and a page served with a stale meta rendered "PDF, NaN MB"
        "PAPER_MB": f"{(ROOT / PAPER_PDF).stat().st_size / 1048576:.1f}",
        # stamps every page and every data URL, so the two cannot be served from different builds
        "DATA_V": hashlib.blake2s(
            (FREEZE_MD5 + meta["built"] + str(PREPRINT_URL) + str(SUBMIT_ENDPOINT)).encode(),
            digest_size=6).hexdigest(),
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
            if p.suffix == ".html" and ANALYTICS_TOKEN:
                text = text.replace("</head>", ANALYTICS_SNIPPET % ANALYTICS_TOKEN + "\n</head>", 1)
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
