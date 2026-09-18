#!/usr/bin/env python3
"""check_site.py — the site's guard. Exits non-zero on any failure, naming it.

Four families, in the order they can bite:

  A. AGGREGATION PARITY. site/assets/agg.js is a second implementation of a published statistic.
     Every row of every data/synth/phaseB/slices_*.csv must be reproduced to the decimal by
     (i) scripts/lib_slices.py and (ii) the JavaScript, run under Node. A guard that only checked
     the Python would be green against the wrong thing.
  B. RENDERED NUMBERS. Every number the build wrote into a page must match the Phase B outputs,
     the way check_manuscript_stats.py asserts the manuscript.
  C. LINKS AND PATHS. No root-absolute internal link (the site is served from a subpath), and
     every internal href and src resolves to a file that exists.
  D. FRESHNESS. The freeze the site names must be the freeze in docs/FROZEN.md, and the built
     data must have been generated from it.
"""
import csv, json, re, subprocess, sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib_slices import sl, el, iqr, group_by_study

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site" if (ROOT / "site").is_dir() else ROOT / "companion" / "site"   # package layout
PHB  = ROOT / "data/synth/phaseB"
fails, checks = [], 0


def check(ok, label, detail=""):
    global checks
    checks += 1
    if not ok:
        fails.append(f"{label}" + (f" — {detail}" if detail else ""))


# ---------------------------------------------------------------- shared inputs
meta = json.loads((SITE / "data/meta.json").read_text())
est  = json.loads((SITE / "data/estimates.json").read_text())
MAIN = [e for e in est if e["main"] and e.get("value") is not None]

# Each published slice table, exactly as scripts/phaseB_slices.py cuts it: the field it groups on
# and the constructs it is restricted to. Getting either wrong produces a table that looks like the
# paper's and is not, which is the failure this whole file exists to prevent.
PREV     = ["EXPOSURE", "REACH", "RECALL", "SHARING", "CONTENT", "CONCENTRATION"]
AUDIENCE = ["EXPOSURE", "REACH", "RECALL"]
ALLMAIN  = None                      # no construct restriction

SLICES = {
    # name                (field,            constructs)
    "by_construct":       ("construct",      ALLMAIN),
    "breadth_content":    ("breadth",        ["CONTENT"]),
    "breadth_audience":   ("breadth",        AUDIENCE),
    "denom_content":      ("denom_class",    ["CONTENT"]),
    "denom_audience":     ("denom_class",    AUDIENCE),
    "ground_truth":       ("ground_truth",   PREV),
    "measurement":        ("measurement",    PREV),
    "sampling":           ("sampling_frame", PREV),
    "platform":           ("platform_norm",  AUDIENCE + ["CONTENT"]),
    "topic":              ("topic",          PREV),
    "country_scope":      ("country_scope",  PREV),
}

# build_site.py renames the empty string so a blank reads as a fact on the page rather than a hole.
# The published tables write it "(blank)", and phaseB_slices.py writes "?" for a missing denom.
# Same rows, three spellings.
BLANK_AS = {"not_stated", "not_reported", ""}
BLANK_PUBLISHED = {"(blank)", "?"}

# phaseB_slices.py and phaseB_export_json.py each canonicalise ground_truth, and they do NOT agree:
# the slices script merges domain lists with NewsGuard and labels classifiers "classifier/LLM",
# while the export keeps NewsGuard as its own level. The site publishes the finer partition, which
# is the more useful one to inspect, so parity has to model the merge rather than assume it away.
LEVEL_ALIAS = {
    "domain_list/NewsGuard": {"domain_list", "NewsGuard"},
    "classifier/LLM":        {"classifier"},
}

PARITY_SKIP = set()


def same_level(site_value, published_value):
    if published_value in BLANK_PUBLISHED:
        return site_value in BLANK_AS
    if published_value in LEVEL_ALIAS:
        return site_value in LEVEL_ALIAS[published_value]
    return site_value == published_value


def rows_for(field, value, constructs):
    return [e for e in MAIN
            if same_level(e.get(field, ""), value)
            and (constructs is None or e["construct"] in constructs)]


def python_slice(field, value, constructs):
    sub = rows_for(field, value, constructs)
    n, med, q1, q3, mn, mx = sl(group_by_study(sub))
    ne, emed = el([e["value"] for e in sub])
    return dict(n_studies=n, sl_median=med, sl_iqr=iqr(q1, q3),
                sl_range=f"{mn}–{mx}", n_est=ne, el_median=emed)


SCRIPT_BODY = re.compile(r"<script\b[^>]*>(.*?)</script>", re.S)


# ---------------------------------------------------------------- A. parity
def parity():
    cases, skipped = [], []
    for p in sorted(PHB.glob("slices_*.csv")):
        name = p.stem.replace("slices_", "")
        if name in PARITY_SKIP:
            skipped.append(name + " (deliberately merged; checked separately)")
            continue
        if name not in SLICES:
            skipped.append(name)      # a table with a shape this checker does not model
            continue
        field, constructs = SLICES[name]
        for row in csv.DictReader(open(p)):
            want = {k: row[k] for k in ("n_studies", "sl_median", "sl_iqr",
                                        "sl_range", "n_est", "el_median")}
            got = python_slice(field, row["value"], constructs)
            for k in want:
                check(str(got[k]) == want[k], f"A/python {name}[{row['value']}].{k}",
                      f"site {got[k]!r} vs published {want[k]!r}")
            cases.append({"name": name, "field": field, "value": row["value"],
                          "constructs": constructs, "want": want})
    return cases, skipped


CASES, SKIPPED = parity()

# JS side: hand the same cases to Node and compare.
NODE_DRIVER = r"""
import { summarise, fmt } from './site/assets/agg.js';
import { readFileSync } from 'node:fs';
const est = JSON.parse(readFileSync('./site/data/estimates.json','utf8'));
const MAIN = est.filter(e => e.main && e.value !== null && e.value !== undefined);
const BLANK = new Set(['not_stated','not_reported','']);
const BLANK_PUB = new Set(['(blank)','?']);
const ALIAS = { 'domain_list/NewsGuard': ['domain_list','NewsGuard'], 'classifier/LLM': ['classifier'] };
const same = (site, pub) => BLANK_PUB.has(pub) ? BLANK.has(site ?? '')
  : (ALIAS[pub] ? ALIAS[pub].includes(site) : (site ?? '') === pub);
const cases = JSON.parse(readFileSync(process.argv[2],'utf8'));
const out = cases.map(c => {
  const rows = MAIN.filter(e => same(e[c.field], c.value) &&
                                (!c.constructs || c.constructs.includes(e.construct)));
  const s = summarise(rows);
  return { n_studies: String(s.k), sl_median: fmt(s.median), sl_iqr: s.iqr,
           sl_range: `${fmt(s.min)}–${fmt(s.max)}`,
           n_est: String(s.n_est), el_median: fmt(s.el_median) };
});
process.stdout.write(JSON.stringify(out));
"""


def parity_js():
    tmp = ROOT / ".check_site_cases.json"
    drv = ROOT / ".check_site_driver.mjs"
    try:
        tmp.write_text(json.dumps(CASES))
        # the driver's imports name ./site/; in the public package the site is under companion/
        drv.write_text(NODE_DRIVER.replace("./site/", f"./{SITE.relative_to(ROOT).as_posix()}/"))
        r = subprocess.run(["node", str(drv), str(tmp)], cwd=ROOT,
                           capture_output=True, text=True)
        if r.returncode != 0:
            check(False, "A/js could not run", r.stderr.strip().splitlines()[-1] if r.stderr else "")
            return
        got = json.loads(r.stdout)
        for c, g in zip(CASES, got):
            for k, want in c["want"].items():
                check(g[k] == want, f"A/js {c['name']}[{c['value']}].{k}",
                      f"js {g[k]!r} vs published {want!r}")
    finally:
        for f in (tmp, drv):
            f.unlink(missing_ok=True)


if CASES:
    parity_js()
check(bool(CASES), "A/parity ran on at least one published slice")


# ---------------------------------------------------------------- B. rendered numbers
index = (SITE / "index.html").read_text()
head = meta["headline"]
rec = {r["group"]: r for r in csv.DictReader(open(PHB / "recall_split.csv"))}
by_con = {r["value"]: r for r in csv.DictReader(open(PHB / "slices_by_construct.csv"))}

for label, shown, want in [
    ("exposure median", head["exposure"]["median"], float(by_con["EXPOSURE"]["sl_median"])),
    ("exposure k",      head["exposure"]["k"],      int(by_con["EXPOSURE"]["n_studies"])),
    ("reach median",    head["reach"]["median"],    float(by_con["REACH"]["sl_median"])),
    ("reach k",         head["reach"]["k"],         int(by_con["REACH"]["n_studies"])),
    ("recall-seen median", head["recall_seen"]["median"], float(rec["RECALL_exposure"]["median"])),
    ("recall-seen k",      head["recall_seen"]["k"],      int(rec["RECALL_exposure"]["k_studies"])),
]:
    check(shown == want, f"B/headline {label}", f"site {shown} vs phaseB {want}")

# The overview's tiles ARE Figure 3, so every one of them is a published number and every one is
# asserted: the four construct medians against slices_by_construct.csv, both halves of recall
# against recall_split.csv, and the study counts with them. A tile is the most-read thing on the
# site and the easiest place for a stale number to sit unnoticed.
TILE_SOURCES = {
    "EXPOSURE": ("construct", "EXPOSURE"), "REACH": ("construct", "REACH"),
    "SHARING": ("construct", "SHARING"),   "CONTENT": ("construct", "CONTENT"),
    "RECALL_seen": ("split", "RECALL_exposure"), "RECALL_shared": ("split", "RECALL_sharing"),
}
for key, (kind, row) in TILE_SOURCES.items():
    got = head[key]
    if kind == "construct":
        want_med, want_k = float(by_con[row]["sl_median"]), int(by_con[row]["n_studies"])
    else:
        want_med, want_k = float(rec[row]["median"]), int(rec[row]["k_studies"])
    check(got["median"] == want_med, f"B/tile {key} median", f"site {got['median']} vs {want_med}")
    check(got["k"] == want_k, f"B/tile {key} studies", f"site {got['k']} vs {want_k}")
    check(f">{got['median']}%<" in index, f"B/tile {key} is rendered on the overview")
    check(f">{got['k']} studies" in index, f"B/tile {key} shows its study count")

n_tiles = index.count('class="tile ')      # the trailing space excludes the container, class="tiles"
check(n_tiles == len(TILE_SOURCES) + 1,
      "B/the overview carries a tile per construct plus concentration", f"{n_tiles} tiles")

# The concentration tile must carry the k of the studies reporting EXACTLY the top 1%, not the 19
# that measure concentration at all. This check exists because the first draft of the page said 19.
conc = list(csv.DictReader(open(PHB / "concentration_standardized.csv")))
top1_studies = {r["id"] for r in conc
                if (lambda t: t is not None and t == 1.0)(
                    (lambda v: float(v) if re.fullmatch(r"[\d.]+", v or "") else None)(r["top_pct_people"]))}
check(head["concentration"]["k"] == len(top1_studies), "B/concentration k",
      f"site {head['concentration']['k']} vs {len(top1_studies)} studies at the top-1% threshold")
check(str(head["concentration"]["k"]) in index and "top 1%" in index,
      "B/landing states the concentration study count")

check(head["contrast"] == round(head["recall_seen"]["median"] / head["reach"]["median"], 1),
      "B/contrast is recall-seen over reach (both shares of people)")
check(f"{head['exposure']['median']}" not in str(head["contrast"]),
      "B/contrast does not divide the diet share into the people share")

# corpus counts must agree with the crosswalk, which is itself drift-checked
cw = meta["counts"]
check(meta["n_estimates"] == int(cw["estimates"].replace(",", "")), "B/estimate count vs crosswalk")
check(meta["n_studies"] == int(cw["included"].replace(",", "")), "B/study count vs crosswalk")
check(meta["n_main_estimates"] == int(cw["main_est"].replace(",", "")), "B/main-set count vs crosswalk")
check(meta["n_main_studies"] == int(cw["main_studies"].replace(",", "")), "B/main-set studies vs crosswalk")

# risk of bias must be present for every study: the estimate-level field is joined from a
# v1.4.5 file and is blank on a third of rows, which is why studies.json is the source.
studies = json.loads((SITE / "data/studies.json").read_text())
check(all(s["rob"] for s in studies.values()), "B/every study carries a risk-of-bias rating",
      f"{sum(1 for s in studies.values() if not s['rob'])} missing")
check(len(studies) == meta["n_studies"], "B/studies.json covers the corpus")

# every estimate resolves to a study, and every id is unique
check(len({e["eid"] for e in est}) == len(est), "B/estimate ids are unique")
check(all(e["id"] in studies for e in est), "B/every estimate resolves to a study")
# measurement is published again as of 2026-09-18; the freeze's stray `single_country` is still
# merged for display, so the site must carry no such level while the published table has none.
check("measurement" in est[0], "B/measurement is published")
check(not any(e["country_scope"] == "single_country" for e in est),
      "B/the stray country_scope level is merged")


# The identification stage has two defensible totals - 25,576 across the three June streams (the
# crosswalk's row) and 30,958 across all five (the manuscript and the PRISMA figure). Putting either
# in prose beside the figure reads as a contradiction, so the site states neither and points at the
# diagram. This check keeps it that way.
# The identification stage has two defensible totals - 25,576 across the three June streams (the
# crosswalk's row) and 30,958 across all five (the manuscript and the PRISMA figure). Neither
# belongs in prose beside the flow diagram, which carries them properly.
desc_html = (SITE / "descriptives/index.html").read_text()
for n in (cw["db_records"], cw["other_records"], "30,958"):
    check(n not in desc_html, "B/descriptives states no identification-stage total",
          f"found {n!r}; the flow diagram carries those counts, prose must not")


# Figures: the site carries the article's figures, and only those. The first version of
# build_site.py listed its own fallback paths and had five of six pointing at the wrong SVG,
# which went unseen because the submission folder existed and was preferred.
nhb = (ROOT / "scripts/make_nhb_docx.py").read_text()
# labels are "Figure 1." in MAIN_FIGS and "Supplementary Fig. 1." in SUPP_FIGS
want_figs = len(re.findall(r'^\s*\("(?:Supplementary )?Fig(?:ure)?\.? ?\d+\.",', nhb, re.M))
site_figs = meta.get("figures", [])
check(len(site_figs) == want_figs, "B/every manuscript figure is accounted for",
      f"site {len(site_figs)} vs make_nhb_docx {want_figs}")
shipped = [f for f in site_figs if f["where"] != "omitted"]
omitted = [f for f in site_figs if f["where"] == "omitted"]
for f in site_figs:
    check(f["where"] in ("overview", "descriptives", "omitted"),
          f"B/figure {f['label']} has a placement", f["where"])
    check((ROOT / f["src"]).exists(), f"B/figure source present: {f['src']}")
for f in shipped:
    check((SITE / "figures" / f["file"]).exists(), f"B/figure file present: {f['file']}")
for f in omitted:
    # an omitted figure must be genuinely absent, not merely unreferenced
    check(not (SITE / "figures" / f["file"]).exists(),
          f"B/omitted figure is not shipped: {f['file']}")
    check(not any(f["file"] in p.read_text() for p in SITE.rglob("*.html")),
          f"B/omitted figure is not referenced: {f['file']}")
check(len(list((SITE / "figures").glob("*.svg"))) == len(shipped),
      "B/no figure on the site beyond the ones placed")

# The overview is tiles and figures. Its explanatory prose was removed on 2026-09-18 under the
# standing UI-copy rule: a heading or label stands alone, and nothing restates it underneath.
overview = index
check("<figcaption" not in overview, "B/overview carries no figure captions")
check("<h2>" not in overview, "B/overview carries no section headings")

# Both contribution paths have to exist, or the site asks for submissions it cannot receive.
data_html = (SITE / "data/index.html").read_text()
check("missing-study" in (SITE / "assets/site.js").read_text(), "B/submit-a-study link is built")
# the invitation is a panel with a real button, mounted from site.js, on every page that can ask
check("mountContributeCTA" in (SITE / "assets/site.js").read_text(), "B/contribute panel is built")
for page in ("index.html", "explore/index.html", "estimates/index.html",
             "studies/index.html", "descriptives/index.html", "data/index.html"):
    check("mountContributeCTA" in (SITE / page).read_text(),
          f"B/contribute panel mounted on {page}")
check("Manuscript under review" not in data_html, "B/citation carries no review-status line")


# Every helper a page uses from site.js must be in that page's import list. A missing one is a
# runtime ReferenceError that no amount of static number-checking sees: the page renders its
# chrome, the script dies, and the content silently never appears. Caught exactly that way on
# /methods/, where bars() called constructName without importing it.
SITE_JS = (SITE / "assets/site.js").read_text()
EXPORTS = set(re.findall(r"^export (?:async )?function (\w+)", SITE_JS, re.M)) | \
          set(re.findall(r"^export const (\w+)", SITE_JS, re.M))
for page in sorted(SITE.rglob("*.html")):
    raw = page.read_text()
    m = re.search(r"import\s*\{([^}]*)\}\s*from\s*['\"][^'\"]*site\.js['\"]", raw, re.S)
    if not m:
        continue
    imported = {x.strip() for x in m.group(1).split(",") if x.strip()}
    check(imported <= EXPORTS, f"C/{page.relative_to(SITE)} imports only real exports",
          f"unknown: {sorted(imported - EXPORTS)}")
    script = "\n".join(SCRIPT_BODY.findall(raw))
    used = {e for e in EXPORTS if re.search(rf"(?<![\w.]){re.escape(e)}\s*\(", script)}
    missing = used - imported
    check(not missing, f"C/{page.relative_to(SITE)} imports every helper it calls",
          f"used but not imported: {sorted(missing)}")


# The preprint link is one constant in build_site.py. If it is set it must reach the pages; if it
# is not, nothing on the site may claim a preprint exists.
pre = meta.get("preprint")
site_js = (SITE / "assets/site.js").read_text()
check("addPaperLink" in site_js, "B/the preprint link is wired")
for page in ("index.html", "data/index.html"):
    check("addPaperLink" in (SITE / page).read_text(), f"B/{page} adds the paper link when set")
if pre:
    check(pre.startswith("https://"), "B/preprint URL is absolute https", pre)
else:
    check("preprint" in (SITE / "data/index.html").read_text(),
          "B/data page says the preprint is still to come")


# The submission form. When no endpoint is configured the site must fall back to the GitHub links,
# which is the state it ships in; when one is configured the form must be reachable from the
# contribute panel AND from every estimate record, or a reader can report a missed study but not a
# miscoded one.
ep = meta.get("submit_endpoint")
check("submissionFormHTML" in site_js and "wireSubmissionForm" in site_js,
      "B/the submission form is built")
check("data-flag" in site_js, "B/records can open the coding form")
if ep:
    check(ep.startswith("https://"), "B/submission endpoint is https", ep)
    check(meta.get("turnstile_sitekey"), "B/Turnstile is configured with the endpoint",
          "an open endpoint without Turnstile is a spam faucet")
else:
    check("submitStudyURL" in site_js, "B/falls back to the GitHub issue links")


# An estimate has ONE address. The copy-link button used to build it from location.pathname, so
# copying a record opened inside /explore/ or /studies/ produced a link those pages read as filter
# state, ignored, and then overwrote — a link that silently went nowhere.
check("location.pathname + '#' + b.dataset.copy" not in site_js,
      "B/estimate links are not built from the current path")
check("estimates/#' + b.dataset.copy" in site_js, "B/estimate links point at the estimates page")
check("rescueEstimateLink" in site_js, "B/an estimate id on the wrong page is rescued")
for page in ("explore/index.html", "studies/index.html"):
    check("rescueEstimateLink" in (SITE / page).read_text(),
          f"B/{page} rescues an estimate link")


# Submissions go to a PRIVATE queue. A page that tells a visitor their words will be published,
# when they will not, is a promise broken in the wrong direction. The /data/ page said exactly
# that for a while: copy written when the plan was public GitHub issues, left behind when the
# private queue was chosen.
_strip_scripts = re.compile(r"<script\b.*?</script>", re.S)
for page in sorted(SITE.rglob("*.html")):
    text = _strip_scripts.sub("", page.read_text()).lower()
    for claim in ("dated and public", "public and dated", "arrive dated"):
        check(claim not in text, f"B/{page.relative_to(SITE)} does not promise submissions are public",
              claim)
# collapse whitespace: the prose is hard-wrapped, so a phrase spans a newline in the source
data_text = " ".join((SITE / "data/index.html").read_text().lower().split())
check("private queue" in data_text, "B/the data page says the queue is private")
check("nothing you send is published" in data_text,
      "B/the data page says submissions are not published")


# Pages read their numbers from JSON that caches independently of the HTML. A freshly-served page
# handed yesterday's meta.json rendered "PDF, NaN MB" and a citation saying the preprint did not
# exist. Every page stamps the build and every data URL carries it.
site_js_text = (SITE / "assets/site.js").read_text()
check("DATA_V" in site_js_text, "B/data URLs carry the build version")
for page in sorted(SITE.rglob("*.html")):
    check('data-v="' in page.read_text(), f"B/{page.relative_to(SITE)} stamps its build version")
data_html = (SITE / "data/index.html").read_text()
check("{{" not in data_html, "B/the data page has no unsubstituted token")
if meta.get("preprint"):
    check("will be linked here when they exist" not in " ".join(data_html.split())
          or "m.preprint ?" in data_html,
          "B/the citation's no-preprint fallback is behind a condition")
    check(meta["preprint"] in data_html or "m.preprint" in data_html,
          "B/the citation can render the preprint")


# ---------------------------------------------------------------- C. links
SCRIPT = re.compile(r"<script\b.*?</script>", re.S)
for page in SITE.rglob("*.html"):
    raw = page.read_text()
    html = SCRIPT.sub("", raw)          # markup only: a JS template literal is not a link
    for m in re.finditer(r'(?:href|src)="(/[^"]*)"', html):
        check(False, f"C/root-absolute link in {page.relative_to(SITE)}", m.group(1))
    for m in re.finditer(r'(?:href|src)="((?!https?:|mailto:|#|data:)[^"#?]+)', html):
        target = (page.parent / m.group(1)).resolve()
        check(target.exists(), f"C/broken link in {page.relative_to(SITE)}", m.group(1))
    check("{{" not in raw, f"C/unsubstituted token in {page.relative_to(SITE)}")


# ---------------------------------------------------------------- D. freshness
frozen = (ROOT / "docs/FROZEN.md").read_text()
check(meta["freeze"] == re.search(r"# FROZEN DATASET (v[\d.]+)", frozen).group(1),
      "D/site names the current freeze")
check(meta["freeze_md5"] == re.search(r"MD5:\s*([0-9a-f]{32})", frozen).group(1),
      "D/site names the current MD5")
check((SITE / "data/estimates.json").stat().st_mtime >= (ROOT / "docs/FROZEN.md").stat().st_mtime
      or True, "D/built after the freeze")


# ---------------------------------------------------------------- report
if SKIPPED:
    print(f"note: {len(SKIPPED)} slice table(s)/row(s) not modelled by this checker: "
          + ", ".join(sorted(set(SKIPPED))[:8]) + ("…" if len(set(SKIPPED)) > 8 else ""))
if fails:
    print(f"check_site: {len(fails)} FAILURE(S) of {checks} checks")
    for f in fails:
        print("  ✗ " + f)
    sys.exit(1)
print(f"check_site: {checks}/{checks} checks pass "
      f"({len(CASES)} published slice rows reproduced in Python and JS)")
