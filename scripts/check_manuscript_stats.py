#!/usr/bin/env python3
"""Derived-stats drift check for the manuscript (the audit's process fix, 2026-07-30).

`make_counts_crosswalk.py` only guards CORPUS COUNTS. That let derived statistics (medians, CIs,
R², predicted %, prediction intervals, small-study significance, sensitivity deltas, RoB %) drift
off the pipeline across freezes — the 2026-07-30 audit found ~20 stale numbers + 2 false claims.

This checker reads the pipeline CSVs, computes the canonical string for each headline derived stat,
and asserts it appears in docs/manuscript_draft.md. It is a CURATED list (extend as the paper adds
claims), not a parser. Exit non-zero on any miss. Run after EVERY re-freeze + manuscript edit.

Run: python3 scripts/check_manuscript_stats.py
"""

import csv, json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYN = os.path.join(ROOT, "data/synth/phaseB")
MS_RAW = open(os.path.join(ROOT, "docs/manuscript_draft.md"), encoding="utf-8").read()
# The manuscript is hard-wrapped, so a phrase that straddles a line break is not a substring of the
# file even when it is present. Collapse whitespace on both sides before comparing (2026-09-04).
import re as _re
MS = _re.sub(r"[ \t]*\n[ \t]*", " ", MS_RAW)


def rows(name):
    return list(csv.DictReader(open(os.path.join(SYN, name), encoding="utf-8")))


def input_rows(name):
    """Hand-curated inputs, which live outside the regenerated outputs dir. See data/inputs/README.md."""
    return list(csv.DictReader(open(os.path.join(ROOT, "data/inputs", name), encoding="utf-8")))


def rob_rows(name):
    return list(csv.DictReader(open(os.path.join(ROOT, "data/rob", name), encoding="utf-8")))



def C(name):
    """construct display form: the manuscript uses Capitalized construct names (no all-caps, Sacha 2026-08-25)."""
    return name.capitalize()

MISSING_SECTIONS = set()   # heading prefixes no section starts with; reported, never raised
misses_xref = []           # cross-reference faults; reported with the rest, never raised
checks = []   # (label, must-appear string)
section_checks = []   # (heading prefix, label, must-appear string) -- anchored to one section


def add(label, s):
    checks.append((label, s))


# Figure captions are not in the master: they live in the builders' caption lists, so until now no
# assertion could reach a number that sits only in a caption. When Sacha's length pass moves a
# figure onto the caption, this is where it stays checked ([[misinfo-review-methods-lessons]] #53
# is the same shape: nothing read the built artefact).
def _caption_text():
    import importlib
    out = []
    for mod, names in (("make_nhb_docx", ("MAIN_FIGS", "SUPP_FIGS")),
                       ("make_manuscript_docx", ("FIGS",))):
        try:
            m = importlib.import_module(mod)
        except Exception:
            continue
        for nm in names:
            for entry in getattr(m, nm, []) or []:
                out.append(" ".join(str(x) for x in entry[:2]))
    return _re.sub(r"\s+", " ", " \n ".join(out))


CAPTIONS = None
figure_checks = []


def add_figure(label, s):
    figure_checks.append((label, s))


def _section_body(prefix):
    """Text between the heading that starts with `prefix` and the next heading of the same or a
    higher level. Whitespace-collapsed, like MS.

    Presence-anywhere matching is what let the SI carry stale numbers behind a correct main-text
    sentence (2026-09-07 audit: three B5 counts, the fold-QUALITY pair). Anchoring an assertion to
    the section that must contain it closes that hole.
    """
    m = _re.search(r"^(#+)\s*" + _re.escape(prefix), MS_RAW, _re.M)
    if not m:
        # A renumbered or renamed section must fail as a MISMATCH so the other ~280 assertions still
        # run and the report names every problem at once. Raising here took the whole guard down on
        # 2026-09-17 when the Results sections were renumbered (lesson #52, in the guard itself).
        MISSING_SECTIONS.add(prefix)
        return ""
    level = len(m.group(1))
    rest = MS_RAW[m.end():]
    nxt = _re.search(r"^#{1,%d}\s" % level, rest, _re.M)
    return _re.sub(r"\s+", " ", rest[:nxt.start()] if nxt else rest)


def add_in(heading_prefix, label, s):
    """Assert `s` appears INSIDE the section whose heading starts with `heading_prefix`."""
    section_checks.append((heading_prefix, label, s))


# --- construct medians + k (uncertainty_medians) ---
um = {r["group"]: r for r in rows("uncertainty_medians.csv")}
for g, disp in [("EXPOSURE", "EXPOSURE"), ("CONTENT", "CONTENT"),
                ("REACH", "REACH"), ("SHARING", "SHARING")]:   # backbone retired 2026-08-26 (§2.6 deleted)
    r = um[g]
    add(f"{disp} median", f'{float(r["study_median_pct"]):.1f}')
    add(f"{disp} k", f'{r["k_studies"]}')

# --- ratios (ratio_bootstrap) ---
rb = {(r["numerator"], r["denominator"]): r for r in rows("ratio_bootstrap.csv")}
# headline ratio is now SEEN-recall / EXPOSURE (v1.6.7 RECALL split)
re_ = rb.get(("RECALL-seen", "EXPOSURE")) or rb[("RECALL", "EXPOSURE")]
# RETIRED 2026-08-26 (Sacha: ratios removed everywhere): add("seen-recall/EXPOSURE ratio point", f'{float(re_["point_ratio"]):.1f}')
# RETIRED 2026-08-26 (Sacha: ratios removed everywhere): add("seen-recall/EXPOSURE ratio lo", f'{float(re_["boot95_lo"]):.1f}')
try:
    import csv as _c
    rsp={r["group"]:r for r in _c.DictReader(open(os.path.join(SYN,"recall_split.csv")))}
    add("RECALL seen median", f'{float(rsp["RECALL_exposure"]["median"]):.1f}')
    add("RECALL shared median", f'{float(rsp["RECALL_sharing"]["median"]):.1f}')
except Exception: pass

# --- metareg R2_adj (metareg_univariable) ---
mr = {r["moderator"].strip('"'): r for r in rows("metareg_univariable.csv")}
for mod, disp in [("measurement", "measurement"), ("ground_truth", "ground-truth"),
                  ("id_method", "id-method"), ("sampling", "sampling"), ("construct", "construct"),
                  ("breadth", "breadth"), ("denom_fine", "denom"), ("topic", "topic")]:
    add(f"R2 {disp}", f'{float(mr[mod]["R2_adj"]):.1f}%')

# --- predicted % (metareg_measurement_pred) ---
pr = {r["measurement"].strip('"'): r for r in rows("metareg_measurement_pred.csv")}
add("predicted self-report", f'{float(pr["SELF_REPORT"]["pred_pct"]):.1f}%')

# --- small-study significance (small_study_effects); per-group rho asserted in the 2026-08-10
# extension below via _rho() — the old ad-hoc truncated variant and the dead reach_sig branch
# were removed at the 2026-08-11 code review ---
ss = {r["group"]: r for r in rows("small_study_effects.csv") if "REPORTABLE" in r.get("test", "")}

# --- sensitivity: exclude-HIGH CONTENT (sensitivity.csv) ---
sens = [r for r in rows("sensitivity.csv") if "exclude HIGH" in r["analysis"] and r["group"] == "CONTENT"]
if sens:
    pass  # RETIRED 2026-08-25 (RoB minimalisation: exclude-HIGH left the manuscript)
sensb = [r for r in rows("sensitivity.csv") if "exclude HIGH" in r["analysis"] and r["group"] == "WHOLE-DIET backbone"]
if sensb:
    pass  # RETIRED 2026-08-25 (exclude-HIGH backbone left the manuscript)

# --- main analysis set size (drifted silently at v1.7.2 when 2 scale-score rows left the pool) ---
import re as _re2
_fp2 = _re2.search(r"File:\s*(\S+)", open(os.path.join(ROOT, "docs/FROZEN.md")).read()).group(1)
_all = list(csv.DictReader(open(os.path.join(ROOT, _fp2), encoding="utf-8")))
add("main analysis set", f'{sum(1 for r in _all if r["value_kind"] == "proportion" and not (r["demographic_group"] or "").strip())} of which')

# --- GRADE table rows + every construct median/k (the table drifted unseen at v1.7.4) ---
for _r in rows("grade_sof.csv"):
    _c = _r["construct"]
    if _c in ("SHARING", "CONTENT", "EXPOSURE", "REACH"):  # CONCENTRATION row is per-band (review item 2)
        add(f"GRADE {_c} k/median", f'| {C(_c)} | {_r["k"]} | {float(_r["median"]):.1f}')
for _r in rows("uncertainty_medians.csv"):
    if _r["group"] in ("SHARING", "REACH"):
        add(f'{_r["group"]} median', f'{float(_r["study_median_pct"]):.1f}')

_cts = {r["threshold_band"]: r for r in rows("concentration_by_threshold.csv") if r["unit"] == "user"}
_strict, _band = _cts["top =1%"], _cts["top <=1%"]
# --- GRADE certainty per construct, ROW-ANCHORED. The first version asserted the bare substring
# '| MODERATE', which any other table row satisfies — and at v1.7.9 SHARING moved LOW -> MODERATE
# while the manuscript said LOW, and the construct-blind check passed. Anchor the full row prefix
# (construct | k | median (IQR) | pct-high | certainty) so a certainty change in ANY row fails.
for _r in rows("grade_sof.csv"):
    _c, _cert = _r["construct"], _r.get("certainty", "").replace("_", " ")
    if not (_c and _cert):
        continue
    _cert_disp = _cert   # (bold removed from tables 2026-08-12, C45: no bold in text)
    if _c == "RECALL":
        # the manuscript's RECALL row is DELIBERATELY the seen-split (§2.10 reports seen-recall,
        # shared-recall in the downgrade note), so anchor it to recall_split.csv values while the
        # %-high-RoB and certainty still come from the all-RECALL grade_sof row
        _s = next(x for x in rows("recall_split.csv") if x["group"] == "RECALL_exposure")
        add("GRADE row RECALL (seen-split hybrid)",
            f'| Recall (seen) | {_s["k_studies"]} | {float(_s["median"]):.1f} '
            f'({float(_s["iqr_lo"]):.1f}–{float(_s["iqr_hi"]):.1f}) | '
            f'{int(round(float(_r["pct_high_rob"])))}% | {_cert_disp} |')
    elif _c == "CONCENTRATION":
        # threshold-specific (a pooled median across thresholds is not interpretable — review item 2)
        add("GRADE row CONCENTRATION (per-band)",
            f'| Concentration | {_r["k"]} | top 1%: {float(_strict["median_activity_share_pct"]):.1f} (k = {_strict["k_studies"]}); '
            f'≤1% band: {float(_band["median_activity_share_pct"]):.1f} (k = {_band["k_studies"]}) | '
            f'{int(round(float(_r["pct_high_rob"])))}% | {_cert_disp} |')
    else:
        add(f"GRADE row {_c}",
            f'| {C(_c)} | {_r["k"]} | {float(_r["median"]):.1f} ({_r["iqr"]}) | '
            f'{int(round(float(_r["pct_high_rob"])))}% | {_cert_disp} |')

# --- RoB ITEM rates (drifted 80.3/78.9/52.0 -> 80.2/78.8/52.3 unnoticed at v1.7.x) ---
_it = {r["item"]: r for r in rob_rows("rob_v3_item_distribution.csv")}
# RETIRED 2026-08-25: per-item flag rates left the manuscript with the RoB minimalisation
# (B1 now carries only the overall distribution, the item-10/design crosstab, and the
# generic-items null result).

# --- breadth STRATA (the thesis gradient) + platform/topic R2 + the regression n ---
# These were NOT covered, so the checker reported 27/27 PASS at the v1.7.0 re-freeze while six
# numbers in the manuscript were stale — including the breadth gradient, which the adjudication
# had just moved. A guard that greenlights stale text is worse than no guard.
_bc = {r["value"]: r for r in rows("slices_breadth_content.csv")}
if {"fabricated", "false", "misleading"} <= set(_bc):
    add("breadth gradient (CONTENT)",
        f'Content studies that count only fabricated content report a median of {float(_bc["fabricated"]["sl_median"]):.1f}%, '
        f'those that count false content {float(_bc["false"]["sl_median"]):.1f}%, and those that also count misleading content '
        f'{float(_bc["misleading"]["sl_median"]):.1f}%')
for mod, disp in [("platform", "platform"), ("topic", "topic-far-less")]:
    if mod in mr:
        add(f"R2 {disp}", f'{float(mr[mod]["R2_adj"]):.1f}%')
_reg = rows("regression_data.csv")
if _reg:
    _k = next(c for c in _reg[0] if c.lower() in ("id", "study", "study_id"))
    add("regression n", f'{len(_reg)} estimates from {len({r[_k] for r in _reg})} studies')
# the retired breadth values must not be described as live coding options
# The arrow form lived in a C2 paragraph that duplicated Methods and was cut on 2026-09-15. The
# scale itself is still stated, in the sentence the Results use, and that is what is asserted now.
# The three-value breadth scale is asserted by "defs: breadth counts" below, derived from the
# freeze. A second copy here was a hardcoded literal and went stale one freeze later.

# --- RoB by construct: manuscript reports BY-STUDY (grade_sof pct_high_rob), per C2 ---
for r in rows("grade_sof.csv"):
    if r["construct"] == "CONTENT":
        add("CONTENT high-RoB (by-study)", f'{int(round(float(r["pct_high_rob"])))}%')
        break

# ============================================================================================
# 2026-08-10 pre-submission audit extension. The 49-check version passed while ~30 stale numbers
# sat in the manuscript, all outside its assertions (CIs, IQRs, prediction intervals, per-group
# Spearman, ratios, precision baselines, sensitivity values, §4 counts, the freeze-version string,
# Discussion restatements). Everything below closes those gaps, plus a MUST-NOT-APPEAR list of the
# superseded strings that survived — presence-anywhere matching lets a correct value in one section
# greenlight a stale copy elsewhere, so known-stale strings are banned outright.
# ============================================================================================

# --- bootstrap CIs + IQRs for every construct row of the §2.2 table (en-dash format) ---
for g, disp in [("EXPOSURE", "EXPOSURE"), ("REACH", "REACH"), ("SHARING", "SHARING"),
                ("CONTENT", "CONTENT")]:   # backbone retired 2026-08-26 (§2.6 deleted)
    r = um[g]
    add(f"{disp} CI", f'{float(r["boot95_lo"]):.1f}–{float(r["boot95_hi"]):.1f}')
    add(f"{disp} IQR", f'{float(r["IQR_lo"]):.1f}–{float(r["IQR_hi"]):.1f}')

# --- both headline ratios, point + both bounds ---
# RETIRED 2026-08-26 (Sacha: ratios removed everywhere): add("seen-recall/EXPOSURE ratio hi", f'{float(re_["boot95_hi"]):.1f}')
ce = rb[("CONTENT", "EXPOSURE")]
# RETIRED 2026-08-26 (Sacha: ratios removed everywhere): add("CONTENT/EXPOSURE ratio", f'{float(ce["point_ratio"]):.1f} [{float(ce["boot95_lo"]):.1f}–{float(ce["boot95_hi"]):.1f}]')

# --- prediction intervals (heterogeneity.csv, nominal rows; lo 2dp, hi 1dp) ---
_het = {}
for r in rows("heterogeneity.csv"):
    if "nominal" in r["variance_assumption"] and r["group"] not in _het:
        _het[r["group"]] = r["pred_interval"]
for g, disp in [("CONTENT", "CONTENT"), ("EXPOSURE", "EXPOSURE")]:   # backbone PI retired 2026-08-25 (localised to §2.6)
    lo, hi = (float(x) for x in _het[g].split("-"))
    add(f"PI {disp}", f'{lo:.2f}–{hi:.1f}%')

# --- Spearman small-study correlations: rho for all six groups; k and p where quoted ---
def _rho(x):
    return f'ρ = −.{abs(round(float(x)*100)):02d}'
for g in ["CONTENT", "REACH", "SHARING", "EXPOSURE", "RECALL"]:   # backbone rho retired 2026-08-25
    add(f"Spearman rho {g}", _rho(ss[g]["spearman_rho"]))
add("Spearman CONTENT k", f'k = {ss["CONTENT"]["k"]}')
add("Spearman REACH k", f'k = {ss["REACH"]["k"]}')
add("Spearman REACH p", f'{float(ss["REACH"]["p_value"]):.3f}'.replace("0.", "*p* = ."))
# RETIRED 2026-08-25 (backbone localised): Spearman backbone p

# --- precision weighting: quoted from-to pairs must match the CSV subset baselines ---
pw = {r["group"]: r for r in rows("precision_weighting.csv")}
add("weighted CONTENT", f'falls from {float(pw["CONTENT"]["unweighted_median"]):.1f}% (k = {pw["CONTENT"]["n_studies"]}) to {float(pw["CONTENT"]["weighted_median"]):.1f}%')
# RETIRED 2026-08-25 (backbone localised): weighted backbone from-to

# --- sensitivity analyses quoted in §2.9: A2 fold-QUALITY, C full-text-only, B re-extraction ks ---
_sens = rows("sensitivity.csv")
def _sv(analysis, group):
    return next(r for r in _sens if r["analysis"].startswith(analysis) and r["group"] == group)
add("fold-QUALITY CONTENT", f'to {float(_sv("A2", "CONTENT")["median_pct"]):.1f}%')
_pc = float(_sv("PRIMARY", "CONTENT")["median_pct"]); _cc = float(_sv("C full", "CONTENT")["median_pct"])
add("abstract-excl CONTENT delta", f'−{_pc - _cc:.1f} pp')
# The "restrict to independently re-extracted studies" analysis was RETIRED on 2026-09-17
# (Sacha comment 682): its cells held 8, 3 and 13 studies and the whole corpus has since been
# re-extracted blind, which makes the restriction vacuous. The cell sizes are still asserted,
# in the note that records why it went.
_rex = [_sv("B blind", g)["k_studies"] for g in ("CONTENT", "RECALL", "REACH")]
add_in("A2.", "re-extraction retirement",
       f'cells hold {_rex[0]}, {_rex[1]} and {_rex[2]} studies, too few to inform anything')
_dc = float(_sv("D exclude", "CONTENT")["median_pct"])
# RETIRED 2026-08-25: add("exclude-HIGH CONTENT delta", f'−{_pc - _dc:.1f} pp')
# (2026-08-24 RoB reframe: the Discussion no longer restates the exclude-HIGH pair; the B2
# bullet carries it in from-to form.)
# RETIRED 2026-08-25: add("exclude-HIGH pair (B2 bullet)", f'from {_pc:.1f}% to {_dc:.1f}%')

# --- the §3.2 ladder restatement, built from the live medians (EXPOSURE→backbone→SHARING→REACH→CONTENT→seen-recall) ---
_rsp = {r["group"]: r for r in rows("recall_split.csv")}
# RETIRED 2026-08-26 (the arrow-ladder flourish left the Discussion in the NHB style pass)

# --- predicted prevalence: all three quoted measurement levels, not just self-report ---
add("predicted behavioural", f'{float(pr["BEHAVIOURAL"]["pred_pct"]):.1f}%')
add("predicted content-coding", f'{float(pr["CONTENT_CODING"]["pred_pct"]):.1f}%')

# --- concentration: STRICT top-1% headline + <=1% band, both STUDY-level (2026-08-12 review items 1-2) ---
add("top-1% strict headline", f'with a study-level median of {float(_strict["median_activity_share_pct"]):.0f}%')
# the k is still asserted, just no longer inside the same clause (Sacha comment 531, 2026-09-17)
add("top-1% strict k", f'Five give exactly the top 1%' if int(_strict["k_studies"]) == 5 else f'{_strict["k_studies"]} give exactly the top 1%')
add("top-1% abstract", f'median {float(_strict["median_activity_share_pct"]):.0f}%')
add("<=1% band", f'across all ten the study-level median is {float(_band["median_activity_share_pct"]):.1f}%'
    if int(_band["k_studies"]) == 10 else
    f'across all {_band["k_studies"]} the study-level median is {float(_band["median_activity_share_pct"]):.1f}%')
_cs = [r for r in rows("concentration_standardized.csv") if r["unit"] == "user"]
add("standardized concentration set", f'{len({r["id"] for r in _cs})} report how much of the total misinformation activity')
add("standardized concentration rows", f'standardised the {len(_cs)} user-level concentration estimates')

# --- sans-6/10 RoB sensitivity (instrument-circularity check) ---
_s6 = {r["construct"]: r for r in rows("rob_sans610.csv")}
# RETIRED 2026-08-25: add("sans-6/10 CONTENT high", f'{float(_s6["CONTENT"]["pct_high_sans610"]):.0f}%')
add("sans-6/10 CONTENT median", f'{float(_s6["CONTENT"]["median_excl_high"]):.1f}%')

# --- §4 counts: six-construct row count, regression n in §4.9, freeze-version string ---
_six = sum(1 for r in _all if r["value_kind"] == "proportion"
           and not (r["demographic_group"] or "").strip()
           and r["construct"] in ("CONTENT", "RECALL", "EXPOSURE", "SHARING", "REACH", "CONCENTRATION"))
add("six-construct set", f'draw on {_six} of these')
add("main set (§4 wording)", f'{sum(1 for r in _all if r["value_kind"] == "proportion" and not (r["demographic_group"] or "").strip())} are proportion')
_ver = _re2.search(r"estimates_(v[\d.]+)_frozen", _fp2).group(1)
add("freeze version string", f'estimates_{_ver}_frozen.csv')
add("freeze version bold", f'**{_ver}**')

# --- crosswalk-side count quoted in §4.4 ---
_cw = open(os.path.join(ROOT, "docs/counts_crosswalk.md"), encoding="utf-8").read()
_nr = _re2.search(r"Not retrieved \| (\d+)", _cw) or _re2.search(r"\| Not retrieved \| (\d+)", _cw)
if _nr:
    add("not-retrieved count", f'{_nr.group(1)} advancing records')


# --- definitions descriptives (§2.2, added 2026-08-12) + platform mix + recall windows ---
from collections import Counter as _Ctr
_pool = [r for r in _all if r["value_kind"] == "proportion" and not (r["demographic_group"] or "").strip()]
_bys = {}
for _r in _pool:
    _bys.setdefault(_r["id"], []).append(_r)
def _modal(field):
    c = _Ctr()
    for _sid, _rs in _bys.items():
        vals = [x[field] for x in _rs if x[field]]
        c[_Ctr(vals).most_common(1)[0][0] if vals else ""] += 1
    return c
_cl = _modal("classification_level"); _gt = _modal("ground_truth"); _br = _modal("breadth")
# phrasings updated 2026-08-26 (Sacha comment 39: counts + percentages)
_N = len(_bys)
def _p(n): return round(100 * n / _N)
# "in the main analysis" read as though 4 of the 443 had vanished, so the paragraph accounts for
# them. It sat mid-sentence until Sacha asked for it smaller and at the end (comment 161,
# 2026-09-17); it is still asserted, just in its new place.
add("defs: claim-level",
    f'{_cl["claim_level"]} of the {_N} studies '
    f'({_p(_cl["claim_level"])}%)')
add_in("A5.", "defs: quality-only aside",
    "the four remaining included studies contribute only quality ratings and enter no prevalence "
    "figure")
add("defs: source-level", f'{_cl["source_level"]} ({_p(_cl["source_level"])}%) classify entire sources')
add("defs: researcher coding", f'{_gt["researcher_coding"]} studies ({_p(_gt["researcher_coding"])}%) rely on the researchers\' own coding')
add("defs: domain lists", f'{_gt["domain_list"]} ({_p(_gt["domain_list"])}%) on lists of unreliable domains')
add("defs: fact-checkers", f'{_gt["fact_checker"]} ({_p(_gt["fact_checker"])}%) on fact-checker verdicts')
add("defs: classifiers", f'{_gt["classifier"]} ({_p(_gt["classifier"])}%) on automated classifiers')
_fab_disp = {6: "Six"}.get(_br["fabricated"], str(_br["fabricated"]))   # sentence-initial number is spelled out
_fab_word = {"12": "Twelve"}.get(str(_fab_disp), str(_fab_disp))   # the sentence opens with the number, so it is spelled out
add("defs: breadth counts", f'{_fab_word} studies count only fabricated content, {_br["false"]} count false content, and {_br["misleading"]} extend to misleading content')
add("defs: no standard", f'{_br[""]} studies ({round(100*_br[""]/len(_bys))}%) state no per-item veracity standard')
_beh = {}
for _r in _pool:
    if _r["construct"] in ("EXPOSURE", "REACH", "SHARING", "CONCENTRATION"):
        _beh.setdefault(_r["id"], []).append(_r["platform_norm"] or _r["platform"])
# Appendix B5 / section 2.1 platform counts, all read off the generated CSV so the table, the
# figure and both prose passages cannot diverge. labels_for() is imported rather than reimplemented.
_pbc = list(csv.DictReader(open(os.path.join(ROOT, "data/synth/phaseB/platform_by_construct.csv"))))
_pbc_row = {r["platform"]: r for r in _pbc}
_K = _pbc_row["TOTAL studies"]
# the three browsing counts were the audit's worked example of substring matching hiding stale text:
# §2.1's correct sentence satisfied them while B5 carried 6/10/2 (2026-09-07). Anchored to B5.
add_in("A5.", "B5 browsing triple",
       f'Browsing-panel data accounts for {_pbc_row["Web browsing"]["EXPOSURE"]} of the {_K["EXPOSURE"]} exposure '
       f'studies, {_pbc_row["Web browsing"]["REACH"]} of the {_K["REACH"]} reach studies and '
       f'{_pbc_row["Web browsing"]["CONCENTRATION"]} of the {_K["CONCENTRATION"]} concentration studies')
add_in("A5.", "B5 recall no platform", f'{_pbc_row["No platform named"]["RECALL"]} of the {_K["RECALL"]} recall studies name no platform at all')
# --- section 2.1 geography and recency (were unguarded) --------------------------
_cty = {}
for _r in _all:
    _cty.setdefault(_r["id"], set()).add(_r["country_norm"])
_us_any = sum(1 for v in _cty.values() if "United States" in v)
_us_only = sum(1 for v in _cty.values() if v == {"United States"})
_WEST = {"United States", "United Kingdom", "Canada", "Australia", "New Zealand", "Ireland",
         "Germany", "France", "Italy", "Spain", "Portugal", "Netherlands", "Belgium", "Austria",
         "Switzerland", "Norway", "Sweden", "Denmark", "Finland", "Poland", "Serbia", "Greece",
         "Czechia", "Hungary"}
_west = sum(1 for v in _cty.values() if v and all(x in _WEST for x in v))
add("geo: US", f'({_us_any} of {len(_cty)}) include the United States, {_us_only} of them as the only country studied')
add("geo: western", f'{round(100*_west/len(_cty))}% cover Western countries only')
_yr = {}
for _r in _all:
    if (_r["year"] or "").isdigit():
        _yr.setdefault(_r["id"], _Ctr())[int(_r["year"])] += 1
_ymode = {i: c.most_common(1)[0][0] for i, c in _yr.items()}
add("recency", f'{sum(1 for y in _ymode.values() if y >= 2020)} of the {len(_cty)} fall in 2020 or later, '
    f'{sum(1 for y in _ymode.values() if y in (2020, 2021))} of them in 2020 and 2021 alone, against '
    f'{sum(1 for y in _ymode.values() if y < 2016)} before 2016')

# --- section 2.1 topic x construct and section 2.2 level / ground truth --------
def _cov(field):
    rs = list(csv.DictReader(open(os.path.join(ROOT, f"data/synth/phaseB/coverage_{field}.csv"))))
    return {r[field]: r for r in rs}
_top, _gt = _cov("topic"), _cov("ground_truth")
add("topic: content health", f'{_top["Health, non-COVID"]["CONTENT"]} concern non-COVID health topics and {_top["COVID-19"]["CONTENT"]} COVID-19')
add("topic: content politics", f'against {_top["Politics, elections"]["CONTENT"]} on politics and elections')
add("topic: general news", f'general news accounting for {_top["General news"]["EXPOSURE"]} of the {_K["EXPOSURE"]} exposure studies, {_top["General news"]["REACH"]} of the {_K["REACH"]} reach studies and {_top["General news"]["CONCENTRATION"]} of the {_K["CONCENTRATION"]} concentration studies')
add("topic: sharing politics", f'politics and elections for {_top["Politics, elections"]["SHARING"]} of the {_K["SHARING"]} sharing studies')
# denominators derived, never hardcoded: they were 210/15/24/30/17/27 and went stale at the
# v1.7.16 re-freeze, producing impossible strings like "233 of the 210" (2026-09-04).
add("gt: content researcher", f"Content analyses rely on the researchers' own coding ({_gt['Researcher coding']['CONTENT']} of the {_K['CONTENT']})")
add_in("A5.", "gt: domain lists", f'Domain lists supply it for {_gt["Domain list"]["EXPOSURE"]} of the {_K["EXPOSURE"]} exposure studies, {_gt["Domain list"]["REACH"]} of the {_K["REACH"]} reach studies, {_gt["Domain list"]["SHARING"]} of the {_K["SHARING"]} sharing studies and {_gt["Domain list"]["CONCENTRATION"]} of the {_K["CONCENTRATION"]} concentration studies')
add("gt: recall self", f'respondents almost always decide ({_gt["Respondents themselves"]["RECALL"]} of {_K["RECALL"]})')
# The denominators here were hardcoded 15 and 17 - the very staleness the comment above warns
# about, two lines later. Derived from the construct k like every other pair in this block.
add_in("A5.", "B5 country US",
       f'most heavily in exposure ({_cov("country_norm")["United States"]["EXPOSURE"]} of '
       f'{_K["EXPOSURE"]}) and concentration '
       f'({_cov("country_norm")["United States"]["CONCENTRATION"]} of {_K["CONCENTRATION"]})')

# derived, not literal: these were "323"/"26" and had no code derivation (flagged at v1.7.14).
_cells = len({(r["id"], r["construct"]) for r in _all
              if r["construct"] in ("CONTENT", "EXPOSURE", "REACH", "SHARING", "RECALL", "CONCENTRATION")})
add_in("A5.", "B5 cells", f"{_cells} study-construct cells")
assert int(_pbc_row["Web browsing"]["CONTENT"]) == 0, "browsing panels now carry content studies"
for _lab2 in ("Reddit", "Weibo", "News outlets", "Forums", "Telegram", "Websites", "No platform named"):
    assert _lab2 in _pbc_row, f"Appendix B5 lost the {_lab2} row"
_figN = open(os.path.join(ROOT, "docs/figN_platform_panels.svg"), encoding="utf-8").read()
for _c in ("EXPOSURE", "REACH", "SHARING", "CONCENTRATION", "CONTENT", "RECALL"):
    assert f'k = {_K[_c]}' in _figN, f"figN is stale for {_c}"
assert not os.path.exists(os.path.join(ROOT, "docs/figM_platform_scatter.svg")), "retired scatter is back"
_figs = re.findall(r"\(\"Figure (\d)\.\"", open(os.path.join(ROOT, "scripts/make_manuscript_docx.py"), encoding="utf-8").read())
assert _figs == [str(i) for i in range(1, 9)], f"figure numbering broken in the builder: {_figs}"   # 8 since 2026-08-26 (backbone figure deleted with §2.6)

# --- metaregression R2 ladder (section 2.7) -------------------------------------
_mr = {r["moderator"]: r["R2_adj"] for r in
       csv.DictReader(open(os.path.join(ROOT, "data/synth/phaseB/metareg_univariable.csv")))}
def _pct(x):
    return f"{float(x):.1f}"
add("R2 ground_truth", f'explains {_pct(_mr["ground_truth"])}% of the variance')
add("R2 id_method", f'explains {_pct(_mr["id_method"])}%')
add("R2 construct", f'explains {_pct(_mr["construct"])}%')
add("R2 measurement", f'self-report ({_pct(_mr["measurement"])}%)')
add("R2 sampling", f'people were sampled ({_pct(_mr["sampling"])}%)')
# The ladder REORDERED again at v1.7.20, once every table was put on the same main set: denom_fine
# sits above measurement, and platform above sampling. Section 2.6 names them in that order.
add("R2 denom_fine (ladder)",
    # Sacha 2026-09-17: "the share is a share of is impossible to read, never write that"
    f'the denominator class, what that percentage is a share of ({_pct(_mr["denom_fine"])}%)')
add("R2 ladder tail",
    f'The platform studied ({_pct(_mr["platform"])}%), the sampling frame, how the content or the '
    f'people were sampled ({_pct(_mr["sampling"])}%), and the breadth of the definition, whether it '
    f'stops at fabricated content or extends to misleading content ({_pct(_mr["breadth"])}%), '
    f'also explained a significant portion of the variance')
_ranked = sorted(((float(v), k) for k, v in _mr.items()), reverse=True)
# The ladder REORDERED at the v1.7.16 re-freeze: identification choices (ground_truth, id_method) now
# lead, construct is third, and topic collapsed from 8.3% to 2.6%. The paper's claim survives and
# strengthens. Assert the current order so a further change is caught, and refuse to pass while the
# section still carries placeholders for the bootstrap intervals.
# 2026-09-18: measurement went 15.9 -> 16.6 when it stopped being joined from a 22 July
# risk-of-bias file covering 317 of 443 studies (40% of rows arrived NA and were fitted as an
# "unspecified" level that meant "not appraised yet"). It now ties denom_fine at 16.6, so ranks 4
# and 5 are asserted as a SET: a tie has no order, and asserting one would fail on a rounding
# change that means nothing.
assert [k for _, k in _ranked[:3]] == ["ground_truth", "id_method", "construct"], _ranked
assert {k for _, k in _ranked[3:5]} == {"denom_fine", "measurement"}, _ranked
assert abs(_ranked[3][0] - _ranked[4][0]) < 0.05, \
    f"denom_fine and measurement no longer tie at rank 4-5: {_ranked[3]} vs {_ranked[4]}"
assert [k for _, k in _ranked[5:8]] == ["platform", "sampling", "breadth"], "R2 ladder order changed: rewrite the section 2.6 sentence"
assert _ranked[-2][1] == "topic", "topic is no longer second-from-last: rewrite the 2.6 claim"
# Placeholders are collected rather than raised, so the other 240-odd checks still run while the
# bootstrap is in flight. They still fail the run: PENDING is reported and the exit is
# non-zero, so the manuscript cannot be called clean while section 2.6 carries them.
PENDING = [_ph for _ph in ("CI_PENDING", "WITHIN_CONTENT_PENDING") if _ph in MS]
# The bootstrap file carries its own r2_adj per moderator, and section 2.6 quotes the point estimate
# twice: once from the ladder (metareg_univariable.csv) and once beside the interval (this file).
# After a re-freeze the ladder is regenerated in seconds and the bootstrap takes half an hour, so
# between them the section says 22.9% in one sentence and 22.5% in the next, and every assertion
# passes because each half agrees with the file it came from. Compare the two files directly.
STALE_SUPP = []   # staleness between pipeline stages: reported, never raised
_bs_early = {r["moderator"]: r for r in rows("metareg_r2_bootstrap.csv")}
_boot_stale = [m for m, r in _bs_early.items()
               if m in _mr and abs(float(r["r2_adj"]) - float(_mr[m])) > 0.05]
if _boot_stale:
    STALE_SUPP.append("the bootstrap is stale against the current metaregression on "
                      + ", ".join(sorted(_boot_stale))
                      + " — re-run scripts/phaseB_metareg_robustness.R, then refill section 2.6")

add("R2 topic", f'explains the least by far, {_pct(_mr["topic"])}%')

# The English-only criterion is about the language of the REPORT. Sacha read it as implying an
# anglophone corpus, which it is not, so the sentence now names the country count and it is derived.
N_COUNTRIES = len({r["country_norm"] for r in _all if r.get("country_norm")}
                  - {"Global", "Multi-country", "English-language", ""})
add("4.2 language restriction", f"the corpus covers {N_COUNTRIES} countries")

# Figures must be numbered in order of first citation. The PRISMA flow was Figure 1 but was first
# cited in the Methods, AFTER Figures 2 to 6 had all been cited in the Results, which Sacha caught
# on reading. Asserted so a renumbering or a moved reference cannot reintroduce it.
_fig_order, _seen_fig = [], set()
for _m in _re.finditer(r"Figure (\d)", MS):
    if _m.group(1) not in _seen_fig:
        _seen_fig.add(_m.group(1)); _fig_order.append(int(_m.group(1)))
assert _fig_order == sorted(_fig_order), \
    f"figures are not cited in numerical order: first mentions run {_fig_order}"

class _Num(list):
    """Number words. A list indexed by value, extended past twenty so a growing count cannot
    raise IndexError in a guard whose whole job is to keep prose and data together."""
    _TENS = {2: "twenty", 3: "thirty", 4: "forty", 5: "fifty",
             6: "sixty", 7: "seventy", 8: "eighty", 9: "ninety"}

    def __getitem__(self, n):
        if isinstance(n, int) and n >= len(self):
            if n < 100:
                t, u = divmod(n, 10)
                return self._TENS[t] + ("-" + list.__getitem__(self, u) if u else "")
            return str(n)
        return list.__getitem__(self, n)


# Within content analyses topic ranks FIFTH of nine, above denominator class, platform and sampling
# frame. Note C2 claimed it "falls below every measurement moderator" and printed the ladder out of
# order with two rungs missing. Assert the rank so the claim cannot drift back.
# measurement is NA within the content-only model: it is derived from construct, so inside a single
# construct it has no variance and cannot be fitted. Before 2026-09-18 it returned 10.5% there, but
# that was the stale join splitting content studies by whether they had been appraised by 22 July.
_wcl = sorted(((float(r["r2_adj"]), r["moderator"]) for r in rows("metareg_r2_within_content.csv")
               if (r["r2_adj"] or "NA").strip() != "NA"), reverse=True)
_wc_rank = [m for _, m in _wcl]
# topic is 4th of eight now, not 5th of nine: measurement left this ladder on 2026-09-18 because it
# cannot be fitted inside a single construct.
assert _wc_rank.index("topic") == 3, f"within-content ladder moved: {_wc_rank}"
assert "measurement" not in _wc_rank, "measurement is fittable within content again: restore its rung"
# Derived from the ladder rather than typed: measurement left it on 2026-09-18, so the rank and the
# ladder length both moved and a hardcoded phrase would have gone stale silently.
_ORD_W = ["", "first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth"]
add_in("B2.", "C2 within-content rank",
       f"Topic rises to {_ORD_W[_wc_rank.index('topic') + 1]} of "
       + ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"][len(_wc_rank)])

NUM = _Num(["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
            "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen",
            "eighteen", "nineteen", "twenty"])

# Note B4's category counts and medians were written by hand and six of them had drifted from the
# coding file: its own categories summed to 75 in a paragraph opening "all 71 seen-recall studies".
# The guard asserted only the past-week values and the corpus median, so it passed throughout.
_w = list(csv.DictReader(open(os.path.join(
    ROOT, "data/extract_v2/qa/recall_windows_2026-09-14.csv"), encoding="utf-8")))
def _wmed(kinds):
    import statistics as _s
    v = [float(r["study_median_seen_pct"]) for r in _w if r["window"] in kinds]
    return round(_s.median(v), 1), len(v)
_wc = {}
for _r in _w:
    _wc[_r["window"]] = _wc.get(_r["window"], 0) + 1
add_in("A4.", "B4 ever", f"{NUM[_wc.get('ever', 0)].capitalize()} studies ask whether people have ever")
add_in("A4.", "B4 frequency", f"{_wc.get('frequency_scale', 0)} use an unbounded frequency scale")
add_in("A4.", "B4 period", f"{NUM[_wc.get('period_specific', 0)]} refer to a specific event or period")
add_in("A4.", "B4 unclear",
       f"{NUM[_wc.get('unclear', 0) + _wc.get('unclear_no_fulltext', 0)]} are unclear, "
       f"{NUM[_wc.get('unclear_no_fulltext', 0)]} of them because no full text")
_m_unb = _wmed({"ever", "frequency_scale"})
_m_per = _wmed({"period_specific"})
_m_unc = _wmed({"unclear", "unclear_no_fulltext"})
add_in("A4.", "B4 unbounded median", f"{_m_unb[0]}% for ever/frequency studies (k = {_m_unb[1]})")
add_in("A4.", "B4 period median", f"period-specific studies have a median of {_m_per[0]}% (k = {_m_per[1]})")
add_in("A4.", "B4 unclear median", f"the unclear ones {_m_unc[0]}% (k = {_m_unc[1]})")
assert sum(_wc.values()) == len(_w)
add_in("A4.", "B4 instrument denominator", f"Four of the {len(_w)} studies are analyses of one instrument")

# Note B5's panel k range was a literal pair (15 to 210) from an old corpus, next to a cell total
# the guard already derives. Derived from the same coverage table the panels are drawn from.
_kv = sorted(int(v) for k, v in _cov("platform")["TOTAL studies"].items() if k != "platform")
add_in("A5.", "B5 k range", f"k ranges from\n{_kv[0]} to {_kv[-1]} across the panels")

# The blind layer is the whole-corpus campaign (57 batches, every study re-extracted with no sight
# of the frozen coding), not the seeded 10% pilot that Note C1 and Table 2 used to describe. Its
# numbers come from the scoring run's own outputs so they cannot be retyped wrong.
_fa = {r["field"]: r for r in csv.DictReader(open(os.path.join(
    ROOT, "data/extract_v2/full_reextract_2026-09/scores/field_agreement.csv"), encoding="utf-8"))}
_camp = open(os.path.join(ROOT, "data/extract_v2/full_reextract_2026-09/scores/SUMMARY.md"),
             encoding="utf-8").read()
_c_scr = _re.search(r"(\d+) INCLUDE / (\d+) disputes", _camp).groups()
_c_val = _re.search(r"(\d+) of (\d+) frozen main-pool rows matched \(([\d.]+)%\)", _camp).groups()
_c_om = _re.search(r"omission candidates: (\d+) rows across (\d+) studies", _camp).groups()
_c_tot = _re.search(r"\((\d+) of (\d+) studies scored\)", _camp).groups()
add_in("B1.", "C1 campaign scope",
       f"57 batches covering all {_c_tot[1]} studies the corpus then held")
add_in("B1.", "C1 campaign eligibility",
       f"agreed that {_c_scr[0]} of the {_c_tot[1]} studies were eligible and disputed {_c_scr[1]}")
add_in("B1.", "C1 campaign values",
       f"reproduced {_c_val[0]} of the {_c_val[1]} frozen main-pool values ({_c_val[2]}%)")
add_in("B1.", "C1 campaign omissions",
       f"proposed {_c_om[0]} candidate omissions across {_c_om[1]} studies")
# Wave 4 of the independent sweep: the two studies it never reached, coded afterwards under the
# same instructions. Read the returned files, so the claim of completion cannot outlive the check.
_W4 = os.path.join(ROOT, "docs/gpt_check_2026-09_wave4/returned")
_w4 = [json.load(open(os.path.join(_W4, f), encoding="utf-8"))
       for f in sorted(os.listdir(_W4)) if f.endswith(".json")] if os.path.isdir(_W4) else []
_w4_est = sum(len(r.get("estimates", [])) for r in _w4)
_WORDS = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten")
_w4_word = _WORDS[_w4_est] if _w4_est < len(_WORDS) else str(_w4_est)
# The one interpersonal study, disclosed on Sacha's ruling of 2026-09-16 (register, CLOSED entry).
# Derived from the freeze so the sentence cannot drift off the row it describes, and asserted so a
# later edit cannot quietly soften a disclosure the author chose to make.
_ipr = next((r for r in _all if r["id"] == "W7171843315"), None)
if _ipr:
    add_in("B3.", "C3 interpersonal study disclosed",
           f"denominator is {int(float(_ipr['n'].split()[0].replace(',', '')))} observed "
           f"face-to-face conversations")
    add_in("B3.", "C3 interpersonal study value",
           f"{float(_ipr['value_pct']):g}% of which carried a misinformation claim")

# Note F's CSMaP paragraph. The earlier form of this asserted that every CSMaP row carried NO value,
# so that the prose and the ledger could not drift apart; the Nature row gained its 23.9% on
# 2026-09-16 and the assertion is now the positive one. Derived from the ledger, so a later edit to
# either side fails until both move.
_fw = os.path.join(ROOT, "data/extract_v2/qa/falsity_within_sources_2026-09-15.csv")
if os.path.exists(_fw):
    _csmap = [r for r in csv.DictReader(open(_fw, encoding="utf-8"))
              if "Tucker" in r.get("study", "")]
    _valued = [r for r in _csmap if r["value_pct"].strip()]
    if _csmap:
        add_in("Supplementary Note E.", "F CSMaP design flagged",
               "select popular articles from mainstream and low-quality sources within 48 to 72 hours")
    if _valued:
        assert len(_valued) == 1, f"expected one valued CSMaP row, found {len(_valued)}"
        _v = _valued[0]
        # The tier split is OUR computation, so it is asserted against the script that makes it,
        # not against a number typed into the ledger.
        import subprocess as _sp
        _out = _sp.run([sys.executable, os.path.join(ROOT, "scripts/csmap_falsity_by_tier.py")],
                       capture_output=True, text=True, cwd=ROOT).stdout
        _lq = _re.search(r"low-quality\s+(\d+) of\s+(\d+) false or misleading\s+\(\s*([\d.]+)%\)", _out)
        _ms = _re.search(r"mainstream\s+(\d+) of\s+(\d+) false or misleading\s+\(\s*([\d.]+)%\)", _out)
        assert _lq and _ms, "csmap_falsity_by_tier.py output not parseable"
        add_in("Supplementary Note E.", "F CSMaP low-quality",
               f"judged {_lq.group(1)} of the {_lq.group(2)} articles from "
               f"low-quality sources false or misleading, **{float(_lq.group(3)):g}%**")
        add_in("Supplementary Note E.", "F CSMaP mainstream",
               f"against {_ms.group(1)} of the {_ms.group(2)} from mainstream sources, "
               f"**{float(_ms.group(3)):g}%**")
        assert abs(float(_v["value_pct"]) - float(_lq.group(3))) < 0.05, \
            "the ledger's CSMaP value disagrees with the script that computes it"

add_in("B1.", "C1 wave-4 completion", f"agreed on all {_w4_word} of their estimates")
add_in("4.8 ", "4.8 wave-4 completion",
       f"the {_w4_word} estimates in the {_WORDS[len(_w4)]} studies that entered after that sweep")

# Cross-family coverage counted against the RELEASED corpus, not against whatever the corpus was
# when a given check ran. Derived, because the scoped version of this claim was true of a historical
# freeze and false of the paper (2026-09-16).
def _independent_reach():
    """Which released studies any independent pass has actually read, from the artefacts."""
    import glob as _glob
    _rel = {r["id"] for r in _all}
    _cf = {r["study_id"] for r in
           csv.DictReader(open(os.path.join(ROOT, "docs/codex_check/FULL_ANSWER_KEY.csv"),
                               encoding="utf-8"))}
    for _k in ("gpt_check_2026-09_KEY.csv", "gpt_check_2026-09_wave2_KEY.csv"):
        _cf |= {r["row_key"].split("#")[0] for r in
                csv.DictReader(open(os.path.join(ROOT, "data/extract_v2/qa", _k), encoding="utf-8"))}
    # A study counts as checked when the CODER'S ANSWER exists, never when our prompt does.
    # Counting docs/.../batches/ here would have credited wave 5 with 22 studies on the morning it
    # was built and nothing had been run (2026-09-16; the same failure as lesson #40).
    for _w in ("wave3/returns", "wave4/returned"):
        _d = os.path.join(ROOT, f"docs/gpt_check_2026-09_{_w}")
        if os.path.isdir(_d):
            _cf |= {f[:-5] for f in os.listdir(_d) if f.endswith(".json")}
    _w5 = os.path.join(ROOT, "docs/codex_check_wave5/returned/wave5_codes.json")
    if os.path.exists(_w5):
        _ans = json.load(open(_w5, encoding="utf-8"))
        _k5 = {r["item_id"]: r["study_id"] for r in csv.DictReader(
            open(os.path.join(ROOT, "docs/codex_check_wave5/WAVE5_ANSWER_KEY.csv"), encoding="utf-8"))}
        _cf |= {_k5[i] for i, v in _ans.items()
                if i in _k5 and str((v or {}).get("construct", "")).strip()}
    _bl = {os.path.basename(_f)[:-5] for _f in
           _glob.glob(os.path.join(ROOT, "data/extract_v2/full_reextract_2026-09/extractions/*.json"))}
    _bl |= {os.path.basename(_f)[:-5] for _f in
            _glob.glob(os.path.join(ROOT, "data/extract_v2/late_reextract_2026-09/extractions/*.json"))}
    return len(_rel & _cf), len(_rel & _bl), len(_rel & (_cf | _bl)), len(_rel)

_cf_n, _bl_n, _any_n, _rel_n = _independent_reach()
add_in("B1.", "C1 independent reach",
       f"the cross-family check reaches all {_cf_n} included studies, and the blind re-extraction "
       f"reaches all {_bl_n} as well")
# The sentence that follows has to change shape when the gap closes, so assert the right one.
# The paragraph was split chronologically on 2026-09-17, so the residual is no longer a separate
# sentence; when a gap reopens it must be stated again, and this fails until it is.
if _any_n != _rel_n:
    add_in("B1.", "C1 independent residual",
           f"leaving {_rel_n - _any_n} that neither has read")

add_in("B1.", "C1 campaign kappas",
       f"classification level κ = {float(_fa['classification_level']['kappa']):.2f}, "
       f"ground truth κ = {float(_fa['ground_truth']['kappa']):.2f}, "
       f"denominator scope κ = {float(_fa['denom_scope']['kappa']):.2f}, "
       f"construct κ = {float(_fa['construct']['kappa']):.2f}")

# The snowball arm screened 1,818 records and 331 of them advanced to FULL-TEXT RETRIEVAL. The
# prose said 331 advanced "to screening", which is the one thing 331 is not.
_snow = json.load(open(os.path.join(ROOT, "data/synth/prisma_counts.json")))["identified"]["snowball_advancing"]
add_in("4.3 Information sources", "4.3 snowball arm",
       f'screened 1,818 candidate records and contributed {_snow} advancing to full-text retrieval')

# --- the two pre-submission analyses (2026-09-15): perturbation and the concentration null ------
_pert = json.load(open(os.path.join(ROOT, "data/synth/phaseB/perturbation.json")))
_lv = {r["corruption"]: r for r in _pert["levels"]}
add_in("A2.", "B2 perturbation ratios",
       f'ratio is {_pert["baseline_ratio"]}× uncorrupted, '
       f'{_lv[0.10]["recall_over_exposure_median"]}× with a tenth of the codes wrong, '
       f'{_lv[0.20]["recall_over_exposure_median"]}× with a fifth and '
       f'{_lv[0.30]["recall_over_exposure_median"]}× with a third')
add_in("A2.", "B2 perturbation pairs",
       f'behavioural exposure stays below reach in {_lv[0.10]["pair_EXPOSURE<REACH"]:.0f}% of draws at a '
       f'tenth and {_lv[0.30]["pair_EXPOSURE<REACH"]:.0f}% at a third')
add_in("A2.", "B2 perturbation set", f'A fraction of the {_pert["n_rows"]} main-set estimates')
_null = json.load(open(os.path.join(ROOT, "data/synth/phaseB/concentration_null.json")))
# The rarity null was cut from the main text and from Note B2 on 2026-09-18, on Sacha's
# instruction, so there is no prose left to assert the range against. The simulation still runs and
# its result is still checked: if it ever stopped being a null, the assertion below fails and the
# decision to leave it out would have to be revisited.
assert _null["observed_min"] > _null["null_ratio_max"], _null["verdict"]

# Supplementary Data 1 must reproduce the paper's k for every construct, or the table a referee
# uses to trace a median disagrees with the median. Cheap to assert, and it is the whole point.
_sc = list(csv.DictReader(open(os.path.join(ROOT, "data/synth/phaseB/si_study_characteristics.csv"),
                               encoding="utf-8")))
# Reported, not raised. This file is regenerated in the pipeline's POST stage, so between a new
# freeze and `run_phaseB.sh --post-metareg` it is legitimately one freeze behind, and an exception
# here hides the other 270-odd checks behind a stale intermediate (the same failure the figure-text
# regex produced this morning). A mismatch names the fix; an exception buries it.
for _c in ("EXPOSURE", "REACH", "SHARING", "CONTENT", "RECALL", "CONCENTRATION"):
    _n = sum(1 for r in _sc if r[f"study_level_{_c.lower()}_pct"])
    if _n != int(_K[_c]):
        STALE_SUPP.append(f"Supplementary Data 1 has {_n} {_c} studies against the paper's "
                          f"{_K[_c]} — run scripts/make_si_characteristics.py")
if any(r["risk_of_bias"] == "not appraised" for r in _sc):
    STALE_SUPP.append("a study in Supplementary Data 1 has no risk-of-bias appraisal")

# Reach observation windows (ruling S1). The audit's premise was that reach is measured over short
# windows and recall over long ones; it is the other way round, and the guard holds the numbers that
# say so, from the coding file rather than from the report that describes it.
_rw2 = list(csv.DictReader(open(os.path.join(
    ROOT, "data/extract_v2/qa/reach_windows_2026-09-15.csv"), encoding="utf-8")))
assert len(_rw2) == int(_K["REACH"]), f"reach windows cover {len(_rw2)} of {_K['REACH']} studies"
add_in("A4.", "B4 reach window count",
       f"observation window of all {len(_rw2)} behavioural reach studies")

# Note F's claim-level example. The eleven coded items are the paper's own Textbox 1, and the count
# of them that match the standard it cites is the whole point, so it is asserted rather than left as
# prose a later edit could soften.
add_in("Supplementary Note E.", "F claim-level example",
       "of the eleven items it prints as examples, one corresponds to an entry on that page")

# --- information sources (4.3), derived from the PRISMA counts ------------------------------
# Section 4.3 stated the identification total as a literal for three freezes. It is now derived,
# and so is the September arm's funnel, which ruling P1 folded into that total.
_pc = json.load(open(os.path.join(ROOT, "data/synth/prisma_counts.json")))
_idn = _pc["identified"]
_db_total = sum(v for k, v in _idn.items() if k != "snowball_advancing")
add_in("4.3 Information sources", "4.3 database total",
       f'yielding {_db_total:,} database records')
_arm = _pc["behavioural_arm"]
add_in("4.3 Information sources", "4.3 arm funnel",
       f'It returned {_arm["records_returned"]:,} records, {_arm["records_netnew"]:,} of them new '
       f'to the review; {_arm["records_screened_unique"]:,} unique records were screened at title, '
       f'{_arm["sought_for_retrieval"]} went to abstract adjudication, '
       f'{_arm["sought_at_full_text"]} to full-text retrieval, '
       f'{_arm["assessed_at_full_text"]} were assessed, and {_arm["studies_in_freeze"]} studies '
       f'entered the dataset')

# --- direction of the corrections (C1), derived by scripts/phaseB_correction_direction.py -------
# This claim was hand-written and its p-value went stale twice, in two different documents, with no
# script behind either number. Now asserted against the derivation.
_cd = json.load(open(os.path.join(ROOT, "data/synth/phaseB/correction_direction.json")))
add_in("B1.", "C1 correction direction",
       f'up {_cd["corrections_only"]["up"]} times and down {_cd["corrections_only"]["down"]} '
       f'(exact two-sided sign test, *p* = {_cd["corrections_only"]["sign_test_p"]:.3f}'.replace("0.", ".")
       .replace("*p* = .", "*p* = ."))
add_in("B1.", "C1 version count", f'Across the {_cd["n_versions"]} successive versions of the dataset')

# recall windows (coded 2026-08-12 for 22 studies, extended to every seen-recall study on
# 2026-09-11 and refreshed to the v1.7.19 corpus on 2026-09-14;
# source: data/extract_v2/qa/recall_windows_2026-09-14.csv)
_rw = list(csv.DictReader(open(os.path.join(ROOT, "data/extract_v2/qa/recall_windows_2026-09-14.csv"))))
import statistics as _stt
_bnd = [float(r["study_median_seen_pct"]) for r in _rw if r["window"] in ("past_week","past_month","past_3_months","past_6_months","past_year")]
_unb = [float(r["study_median_seen_pct"]) for r in _rw if r["window"] in ("ever","frequency_scale")]
_pwk = sorted(float(r["study_median_seen_pct"]) for r in _rw if r["window"] == "past_week")
add("recall windows: bounded", f'median of {_stt.median(_bnd):.1f}% (k = {len(_bnd)})')
# Moved out of the Results into Note B4 (Sacha comment 326, 2026-09-17): the main text now keeps
# two sentences, so these assert the note, which is where the numbers live.
add_in("A4.", "recall windows: unbounded",
       f'{_stt.median(_unb):.1f}% for ever/frequency studies (k = {len(_unb)})')
add("recall windows: main-text summary",
    f'the estimates are similar whether the window is bounded or not '
    f'({_stt.median(_bnd):.1f}% against {_stt.median(_unb):.1f}%; Supplementary Note A4)')
add_in("A4.", "recall windows: past week", f'{_stt.median(_pwk):.1f}%')
_win_ids = {r["study_id"] for r in _rw}
_seen_ids = {r["id"] for r in _pool if r["construct"] == "RECALL" and (r["recall_subtype"] or "") != "sharing"}
assert _win_ids == _seen_ids, "the window coding and the seen-recall cell differ: re-code the windows for the new studies (§2.4 and B4)"
add("§2.4 window coverage", f'the full text of all {len(_win_ids)} seen-recall studies')
add_in("A4.", "B4 past-week values", f"The five past-week studies report {', '.join(f'{v:.1f}%' for v in _pwk[:-1])} and {_pwk[-1]:.1f}% (median {_stt.median(_pwk):.1f}%)")
add_in("A4.", "B4 corpus-wide median",
       f'the corpus-wide seen-recall median is {_rsp["RECALL_exposure"]["median"]}% across {_rsp["RECALL_exposure"]["k_studies"]} studies')
# concentration comparison (general-news comparators; same derivation as figK)
_nm = [float(r["share"]) for r in input_rows("nonmisinfo_concentration.csv")
       if r["top_pct"] == "1" and (r["share"] or "").strip()
       and r["denom"] != "other" and "DOMAIN" not in r["detail"] and "MISINFO" not in r["detail"].upper()[:30]]
_nmb = {}
for r in input_rows("nonmisinfo_concentration.csv"):
    if (r["top_pct"] == "1" and (r["share"] or "").strip() and r["denom"] != "other"
            and "DOMAIN" not in r["detail"] and "MISINFO" not in r["detail"].upper()[:30]):
        _nmb.setdefault(r["id"], []).append(float(r["share"]))
_nm_sl = _stt.median([_stt.median(v) for v in _nmb.values()])
# RETIRED 2026-09-18b: the concentration-comparison paragraph was deleted from the Results (his edit)
# RETIRED 2026-09-18b: same paragraph; the comparison is no longer made in the text


# --- §2.8 full weighted table + non-significant Spearman p values (2026-08-12 review, items 4 and minor 8) ---
add("weighted REACH", f'reach falls from {float(pw["REACH"]["unweighted_median"]):.1f}% to {float(pw["REACH"]["weighted_median"]):.1f}%')
add("weighted SHARING", f'sharing from {float(pw["SHARING"]["unweighted_median"]):.1f}% to {float(pw["SHARING"]["weighted_median"]):.1f}%')
add("weighted EXPOSURE", f'behavioural exposure from {float(pw["EXPOSURE"]["unweighted_median"]):.1f}% to {float(pw["EXPOSURE"]["weighted_median"]):.1f}%')
# RECALL is the one construct that RISES under sample-size weighting, so §2.7's universal claim and
# B6's "falls" verb both have to carry the exception (2026-09-07 audit).
add_in("A6.", "weighted RECALL", f'rises, from {float(pw["RECALL"]["unweighted_median"]):.1f}% to {float(pw["RECALL"]["weighted_median"]):.1f}% (seen and shared pooled, k = {_K["RECALL"]})')
_rise = sorted(g for g, r in pw.items() if float(r["weighted_median"]) > float(r["unweighted_median"]))
assert _rise == ["RECALL"], f"the set of constructs that rise under sample-size weighting changed: {_rise}"
add("§2.7 weighting exception", "lowers every construct's median except self-reported recall, which rises")
for _g in ("EXPOSURE", "RECALL", "SHARING"):
    add(f"Spearman p {_g}", f'*p* = {float(ss[_g]["p_value"]):.3f}'.replace("0.", "."))

# --- MUST NOT APPEAR: superseded strings the 2026-08-10 audit found alive in the manuscript.
# Each is banned as a literal; if a future freeze legitimately produces one of these values the
# entry must be consciously removed here, which is the point.
# --- 2026-08-24 review-response analyses (phaseB_review_response.py outputs) ---
_mc = rows("review_matched_concentration.csv")
_mc_panels = [r for r in _mc if not r["study"].startswith("MEDIAN")]
_mc_med = next(r for r in _mc if r["study"].startswith("MEDIAN"))
_ratios = sorted(float(r["matched_ratio"]) for r in _mc_panels)
# RETIRED 2026-09-18b: same paragraph; Supplementary Fig. 2 is now uncited and its future is his call
# the median of those four ratios moved to Note B2 with his 2026-09-18 length pass
# RETIRED 2026-09-18b: the matched within-panel comparison left the paper with the paragraph
# Sacha deleted, and Supplementary Fig. 2 was dropped with it (his call, delegated). The
# generator still runs, so the ratios stay reproducible from appendix_content_sharing.csv.
_ws = rows("review_weight_shares.csv")
_t1 = sorted(float(r["top1_weight_share"]) for r in _ws)
_t3 = sorted(float(r["top3_weight_share"]) for r in _ws)
add("weight-share range", f"the single largest study holds {round(100*_t1[0])}–{round(100*_t1[-1])}% of the total weight")
add("weight-share top-3", f"the three largest {round(100*_t3[0])}–{round(100*_t3[-1])}%")
_sym = rows("review_correction_symmetry.csv")
_up = sum(1 for r in _sym if float(r["delta"]) > 0); _dn = sum(1 for r in _sym if float(r["delta"]) < 0)
add("correction symmetry", f"a construct median up {_up} times and down {_dn}")
_hv = {r["construct"]: r for r in rows("review_human_verified_subset.csv")}
add("human-verified subset CONTENT", f"Content {_hv['CONTENT']['median_human']}% vs {_hv['CONTENT']['median_full']}%")
add("human-verified subset EXPOSURE", f"Exposure {_hv['EXPOSURE']['median_human']}% vs {_hv['EXPOSURE']['median_full']}%")
add("human-verified subset count", f"the {_hv['TOTAL_HUMAN_VERIFIED_STUDIES']['k_human']} studies that received author or research-assistant verification")
_cv = rows("review_cramers_v.csv")
_cvv = sorted(float(r["cramers_v"]) for r in _cv)
add("Cramér's V range", f"Cramér's V runs {_cvv[0]:.2f} to {_cvv[-1]:.2f}")

# --- 2026-08-24 RoB descriptive reframe: item10-by-design crosstab (review_item10_design.csv) ---
_i10 = {r["denom_class"]: r for r in rows("review_item10_design.csv")}
_t = _i10["topical"]; _c = _i10["curated_sample"]
add("item10 topical", f'{_t["pct_high"]}% of topical denominators ({_t["item10_high"]} of {int(_t["item10_high"])+int(_t["item10_low"])})')
add("item10 curated", f'{_c["pct_high"]}% of curated samples ({_c["item10_high"]} of {int(_c["item10_high"])+int(_c["item10_low"])})')
add("item10 population", f'{_i10["population"]["pct_high"]}% of population denominators')

# --- 2026-08-27: grey-literature CURATED claims (data/grey/grey_curation.csv; Sacha's audit) ---
_gm = list(csv.DictReader(open(os.path.join(ROOT, "data/grey/grey_master.csv"), encoding="utf-8")))
_gc = {int(r["idx"]): r for r in csv.DictReader(open(os.path.join(ROOT, "data/grey/grey_curation.csv"), encoding="utf-8"))}
_gN = len(_gm)
add("grey n claims", f'{_gN} claims in total')
_est = [i for i in range(_gN) if _gc[i]["category"] == "ESTIMATE" and not _gc[i]["dup_of"]]
add("grey usable estimates", f'only {len(_est)} of the {_gN} are misinformation-prevalence estimates')
_cnt = {}
for i in range(_gN):
    _cnt[_gc[i]["category"]] = _cnt.get(_gc[i]["category"], 0) + 1
add("grey counts", f'{_cnt["COUNT"]} are bare counts with no denominator')
add("grey not-specific", f'{_cnt["NOT_MISINFO_SPECIFIC"]} quantify something broader or other than misinformation')
add("grey relays count", f'{_cnt["ACADEMIC_RELAY"]} restate academic estimates')

add("grey attitudes", f'{_cnt["ATTITUDE"]} measure attitudes or concern')
# "grey within" and "grey moderation" assertions retired 2026-08-27: §2.9 rewrite (Sacha found
# the exclusion inventory too long) folds WITHIN_MISINFO and MODERATION_METRIC into an unnumbered
# remainder sentence; their counts stay in data/grey/grey_curation.csv.
import statistics as _st6
def _gcm(cls):
    vs = []
    for i in _est:
        if _gc[i]["curated_class"] == cls:
            try:
                v = float(str(_gm[i]["number_pct"]).replace("%", "").strip())
            except ValueError:
                continue
            if 0 <= v <= 100:
                vs.append(v)
    return (_st6.median(vs), len(vs)) if vs else (None, 0)
# CONCENTRATION assertion retired 2026-08-27: the two CCDH claims were excluded as bounds
# (report body says "up to 65%"/"up to 69%"; Sacha's ruling, same rule as the Reuters bound),
# leaving n=2 (Knight 65/89) — below the n>=5 reporting threshold, so §2.9 no longer compares it.
for _cls, _pat in [("RECALL", "ecall claims have a median of {m:.1f}% (n = {n},"),
                   ("TOPICAL", "topical content samples have a median of {m:.1f}% (n = {n},")]:
    _m, _n = _gcm(_cls)
    add(f"grey curated {_cls}", _pat.format(m=_m, n=_n))
# corpus comparator for the grey topical median (2026-08-27, §2.3 + Supp Note E):
# estimate-level median of the corpus CONTENT topical stratum, from construct_distributions.csv
for _r in csv.DictReader(open(os.path.join(ROOT, "data/synth/phaseB/construct_distributions.csv"), encoding="utf-8")):
    if _r["construct"] == "CONTENT" and "topical" in _r["level"]:
        add("grey topical corpus comparator", f"against {_r['est_median']}% for the corpus's topical content estimates")
        break
# "grey alarming share" assertion retired 2026-08-27: the 56%-alarming-headlines sentence left
# §2.9 in the rewrite (its coding procedure was never described in Methods, and the number stood
# without a conclusion); the alarming_headline column stays in grey_master_enriched.csv.

_svg = open(os.path.join(ROOT, "docs/fig2_method_drivers.svg"), encoding="utf-8").read()
import re as _re4
# The figure rounds to one decimal since 2026-09-15, to match the text; the integer-only
# pattern crashed the guard rather than reporting a mismatch.
_m1 = _re4.search(r"Behavioural trace.*?>([\d.]+)%<", _svg, _re4.S)
_m2 = _re4.search(r"Content coding.*?>([\d.]+)%<", _svg, _re4.S)
_m3 = _re4.search(r"Self-report.*?>([\d.]+)%<", _svg, _re4.S)
add("fig4 behavioural median (text==figure)", f'behavioural traces find a median of {_m1.group(1)}%')
add("fig4 content median (text==figure)", f'studies coding content {_m2.group(1)}%')
add("fig4 self-report median (text==figure)", f'studies based on self-report {_m3.group(1)}%')

# --- 2026-08-26: broader-threshold concentration sentence (Sacha kept Figure 5; other estimates in text) ---
_ct2 = {r["threshold_band"]: r for r in rows("concentration_by_threshold.csv") if r["unit"] == "user"}
add("conc broader bands", f'report similar shares: {float(_ct2["top 15-35%"]["median_activity_share_pct"]):.1f}% of misinformation activity for the top 15–35% of users ({_ct2["top 15-35%"]["k_studies"]} studies) and {float(_ct2["top 5-15%"]["median_activity_share_pct"]):.1f}% for the top 5–15% ({_ct2["top 5-15%"]["k_studies"]} studies)')
# a broader top group must account for a LARGER share within any one study, so the observed order
# (5-15% above 15-35%) is between-study incomparability and the sentence says so. If that reverses,
# the sentence has to change.
assert float(_ct2["top 5-15%"]["median_activity_share_pct"]) > float(_ct2["top 15-35%"]["median_activity_share_pct"]), \
    "the concentration bands are now monotonic: rewrite the §2.8 non-monotonicity sentence"

# --- 2026-09-07: passages that survived the v1.7.16 re-sync because nothing asserted them -------
# The abstract, the §2.1 k-list, the corpus topic sentence, the platform pairs, the §2.2 level
# sentence, the grey recall comparator, the RoB coverage sentence, the outside-Scopus share and the
# SI cell count all still carried v1.7.14 numbers (docs audit, 2026-09-07). Every one is derived here.
_slc = {r["value"]: r for r in csv.DictReader(open(os.path.join(ROOT, "data/synth/phaseB/slices_by_construct.csv"), encoding="utf-8"))}
_rsp = {r["group"]: r for r in csv.DictReader(open(os.path.join(ROOT, "data/synth/phaseB/recall_split.csv"), encoding="utf-8"))}
add("abstract EXPOSURE", f'misinformation is a median {_slc["EXPOSURE"]["sl_median"]}% of what people consume online')
# "the links they share" overstated the construct: Table 1 defines Sharing as sharing ACTS
# (retweets, reposts, links), and 29 of the 45 sharing studies are Twitter/X (ruling T4).
add("abstract REACH+SHARING", f'it reaches {_slc["REACH"]["sl_median"]}% of people at least once and makes up {_slc["SHARING"]["sl_median"]}% of what they share')
# The abstract is at NHB's 150-word ceiling (149 as of 2026-09-16), so it cannot carry filler:
# assert the two numbers and the claim, not the exact connective wording.
add("abstract RECALL split", f'{_rsp["RECALL_exposure"]["median"]}% say they have seen misinformation and {_rsp["RECALL_sharing"]["median"]}% say they have shared it')
add("abstract CONTENT", f'{_slc["CONTENT"]["sl_median"]}% of the items are classified as misinformation')
add("§2.1 k list", f'content analyses (k = {_K["CONTENT"]}), with far fewer studies of self-reported recall (k = {_K["RECALL"]}), '
    f'observed sharing (k = {_K["SHARING"]}), reach (k = {_K["REACH"]}), behavioural audience exposure (k = {_K["EXPOSURE"]}), and concentration (k = {_K["CONCENTRATION"]})')
# corpus topic sentence: a study counts once in every topic it carries (the coverage-panel rule)
_tps = {}
for _r in _all: _tps.setdefault(_r["topic"], set()).add(_r["id"])
_nst = len({_r["id"] for _r in _all})
_hlth = _tps["health_other"] | _tps["covid19"] | _tps["vaccines"]
add("§2.1 topic corpus", f'of {_nst} studies, {len(_tps["health_other"])} concern non-COVID health topics, {len(_tps["covid19"])} COVID-19, and '
    f'{len(_tps["vaccines"])} non-COVID vaccines ({round(100*len(_hlth)/_nst)}% health-adjacent), against {len(_tps["general_news"])} on general news and {len(_tps["politics_elections"])} on politics')
add("§2.1 twitter pair", f'Twitter/X appears in {_pbc_row["Twitter/X"]["SHARING"]} of the {_K["SHARING"]} sharing studies and {_pbc_row["Twitter/X"]["CONCENTRATION"]} of the {_K["CONCENTRATION"]} concentration studies')
add("§2.1 browsing pair", f'browsing-panel data in {_pbc_row["Web browsing"]["EXPOSURE"]} of the {_K["EXPOSURE"]} exposure studies and {_pbc_row["Web browsing"]["REACH"]} of the {_K["REACH"]} reach studies')
_ytmax = max(int(_pbc_row[_pl][_c]) for _pl in ("YouTube", "TikTok") for _c in ("EXPOSURE", "REACH", "SHARING", "CONCENTRATION", "RECALL"))
add("§2.1 youtube/tiktok", f'YouTube and TikTok run the other way: {_pbc_row["YouTube"]["CONTENT"]} and {_pbc_row["TikTok"]["CONTENT"]} of the {_K["CONTENT"]} content analyses, '
    f'against no more than {_ytmax} studies in any other construct')
add("§2.1 content topics denominator", f'Of the {_K["CONTENT"]} content analyses, {_top["Health, non-COVID"]["CONTENT"]} concern non-COVID health topics')
_lvl = _cov("classification_level")
add("§2.2 level by construct", f'of the {_K["CONTENT"]} content analyses, {_lvl["Claim or item level"]["CONTENT"]} identify misinformation at the claim or item level. The behavioural constructs almost always classify whole sources: whole-source classification accounts for '
    f'{_lvl["Whole source"]["EXPOSURE"]} of the {_K["EXPOSURE"]} exposure studies, {_lvl["Whole source"]["REACH"]} of the {_K["REACH"]} reach studies, '
    f'{_lvl["Whole source"]["SHARING"]} of the {_K["SHARING"]} sharing studies and {_lvl["Whole source"]["CONCENTRATION"]} of the {_K["CONCENTRATION"]} concentration studies')
add("grey recall corpus comparator", f'Recall claims have a median of {_gcm("RECALL")[0]:.1f}% (n = {_gcm("RECALL")[1]}, against {_rsp["RECALL_exposure"]["median"]}% for the corpus\'s self-reported exposure recall)')
_ro0 = list(csv.DictReader(open(os.path.join(ROOT, "data/rob/risk_of_bias_v3_master.csv"), encoding="utf-8")))
_ft = sum(1 for r in _ro0 if r.get("source_read") != "abstract_only")
_ab0 = len(_ro0) - _ft
add("RoB coverage", f'All {len(_ro0)} included studies were appraised with an adaptation of the Hoy et al. (2012) prevalence risk-of-bias tool, read from full text for {_ft} ({round(100*_ft/len(_ro0))}%)')
_nonscopus = sum(1 for i in {_r["id"] for _r in _all} if not i.startswith("2-s2.0-"))
add("outside Scopus", f'{_nonscopus} of {_nst} included studies ({100*_nonscopus/_nst:.1f}%) came from outside Scopus')
add("outside Scopus (Discussion)", f'{round(100*_nonscopus/_nst)}% of included studies came from outside the primary database')
add("SI cells", f'so the {_nst} studies produce {_cells} study-construct cells')

# --- 2026-09-07 (b): GRADE prose, fold-QUALITY pair, Discussion medians, verification kinds, C3 ---
_cert = {r["construct"]: r["certainty"].replace("_", " ") for r in rows("grade_sof.csv")}
_mod = [c for c in ("EXPOSURE", "REACH", "RECALL", "CONCENTRATION", "SHARING") if _cert.get(c) == "MODERATE"]
_low = [c for c in ("EXPOSURE", "REACH", "RECALL", "CONCENTRATION", "SHARING") if _cert.get(c) == "LOW"]
_disp = lambda cs: ", ".join(c.lower() for c in cs[:-1]) + (", and " if len(cs) > 2 else " and ") + cs[-1].lower() if len(cs) > 1 else cs[0].lower()
# EXPOSURE reached HIGH at v1.7.20 (no high-RoB study in the cell, no proxy, stable under
# weighting), so the prose now opens with it and the anchors are built from the table, not fixed.
_high = [c for c in ("EXPOSURE", "REACH", "RECALL", "CONCENTRATION", "SHARING") if _cert.get(c) == "HIGH"]
_grade_prose = ("(" + (f"HIGH for behavioural {_disp(_high)}, " if _high else "")
                + f"MODERATE for {_disp(_mod)}" + (f", LOW for {_disp(_low)})" if _low else ")"))
add_in("2.7 Robustness", "GRADE prose (2.10)", _grade_prose)
add_in("2.7 Robustness", "fold-QUALITY pair (2.10)", f'moves the content median only from {_slc["CONTENT"]["sl_median"]}% to {float(_sv("A2", "CONTENT")["median_pct"]):.1f}%')
# B3's prose said MODERATE for Sharing while its own table said LOW: the SI copy needs its own anchor.
_modC = [C(c) for c in ("EXPOSURE", "REACH", "RECALL", "CONCENTRATION") if _cert.get(c) == "MODERATE"]
_highC = [C(c) for c in ("EXPOSURE", "REACH", "RECALL", "CONCENTRATION") if _cert.get(c) == "HIGH"]
# Sharing was LOW when this was written, so it had its own clause. It is MODERATE now, and the
# clause repeated the word: "MODERATE for Reach, Recall and Concentration, MODERATE for Sharing".
# Build one list per certainty level instead of hardcoding where Sharing sits.
_modAll = _modC + ([C("SHARING")] if _cert.get("SHARING") == "MODERATE" else [])
# Lower-cased in prose since 2026-09-15 (all-caps belongs in the table's label column, not in a
# sentence); the certainty levels themselves still come from grade_sof.csv.
add_in("A3.", "B3 GRADE prose",
       "Certainty is "
       + (f"high for behavioural {', '.join(_highC)}, " if _highC else "")
       + f"moderate for {', '.join(_modAll[:-1])} and {_modAll[-1]}, "
       + ("" if _cert.get("SHARING") == "MODERATE" else f"{_cert['SHARING'].lower()} for Sharing, ")
       + f"and {_cert['CONTENT'].lower()} for Content")
add_in("3. Discussion", "Discussion seen-recall", f'a majority experience ({_rsp["RECALL_exposure"]["median"]}%)')
add_in("3. Discussion", "Discussion content", f'fall in between ({_slc["CONTENT"]["sl_median"]}% of items)')
add_in("3. Discussion", "Discussion sharing", f'the observed sharing ({_slc["SHARING"]["sl_median"]}%)')
add_in("B1.", "C1 released freeze size", f'({len(_all)} estimates at the released freeze)')
add_in("B3.", "C3 seventh limitation", f"{_ab0} studies were coded from the abstract alone")

# NOT a MUST_NOT: a missing DOI is correct until the deposit exists. This reports every run so it
# cannot be forgotten, and goes quiet once section 4.11 names a real DOI. Rewritten 2026-09-18 when
# the placeholder itself came out for the preprint: the condition was "placeholder present", which
# silently stopped firing the moment the placeholder was deleted — the reminder has to key on the
# ABSENCE of a DOI, not the presence of a stand-in for one.
_da = _section_body("4.11") or MS
if not _re.search(r"\b10\.\d{4,9}/\S+", _da):
    # PREPRINT STATE (2026-09-18): the DOI sentence is out, because the deposit does not exist yet
    # and a placeholder in a publicly posted paper is worse than no sentence. This still reports,
    # so the DOI cannot be forgotten when the OSF project is created and the paper goes to a journal.
    STALE_SUPP.append("data availability names no DOI — correct for the preprint; mint the OSF DOI "
                      "and put it back in section 4.11 before any journal submission")

MUST_NOT = [
    # Sacha 2026-09-17: "the share is a share of is ipossible to read, never write that"
    ("banned phrasing: share is a share of", "share is a share of"),
    ("stale freeze pointer", "v1.6.8"),
    ("stale abstract SHARING", "9.6% of the links"),
    ("stale abstract RECALL", "62% of people say"),
    ("stale §2.1 CONTENT k", "k = 210"),
    ("stale §2.1 corpus size", "of 315 studies"),
    ("stale sharing denominator", "of the 30 sharing"),
    ("stale content denominator", "the 210 content"),
    ("stale grey recall comparator", "62.0% in the corpus"),
    ("stale outside-Scopus count", "51 of 315"),
    ("stale outside-Scopus share", "16% of included studies"),
    ("stale RoB coverage", "All 315 included"),
    ("stale SI main-set size", "306 main-analysis"),
    ("§4.4 typo", "53%. to"),
    ("stale behavioural set", "155 studies using behavioural"),
    ("stale limitation count (C3)", "Six limitations"),
    ("stale verification kinds", "three grades"),
    ("stale verification kinds (b)", "We ran three kinds"),
    ("stale C1 freeze size", "675 estimates at the released"),
    ("stale Discussion seen-recall", "majority experience (62%)"),
    ("stale Discussion sharing", "observed sharing 9.6%"),
    ("stale GRADE prose", "reach, sharing, recall, and concentration)"),
    ("unscripted ceiling scan", "raises the ceiling only to about twenty"),
    ("stale ratio lower bound", "bound of 10.8"),
    ("stale sharing median (Discussion)", "13.4%"),
    ("stale §3.2 ladder", "2.6 → 7.2"),
    ("stale exclude-HIGH pair", "23.2% → 11.7%"),
    ("stale weighted-CONTENT baseline", "22.3%"),
    ("stale weighted-CONTENT baseline (b)", "22.2% to 0.9%"),
    ("stale main-set count", "573 are proportion"),
    ("stale regression n", "470 estimates"),
    ("stale content-analysis count", "212 content analyses"),
    ("stale CONTENT high-RoB", "59% of CONTENT"),
    # Leading space: without it this matches inside "145 advancing records", the current value.
    ("stale not-retrieved count", " 45 advancing records"),
    ("stale predicted behavioural", "4.8% for behavioural"),
    ("stale predicted content-coding", "19.8% for content coding"),
    ("stale abstract CONTENT CI", "19.1–26.2"),
    ("stale table CONTENT CI", "19.2–26.6"),
    ("stale backbone CI (prose)", "4.9–8.8"),
    ("stale backbone CI (table)", "4.3–8.8"),
    ("stale SHARING CI", "4.8–16.4"),
    ("stale exclude-HIGH delta", "−10.7 pp"),
    ("stale concentration study count", "(15 studies)"),
    ("stale estimate-level top-1% median", "median 68%"),
    # --- 2026-09-07 (c): the proofread's contradictions ---
    ("stale Note A Sharing", "Sharing at 9.6%"),
    ("stale Note A claim-level row", "24.8% (k=193)"),
    ("stale Note A ladder", "ground_truth .171"),
    ("stale Note A ratio", "roughly an order of magnitude more misinformation"),
    ("stale §2.10 fold-QUALITY pair", "from 23.5% to 24.9%"),
    ("stale Discussion CONTENT", "(23.5% of items)"),
    ("stale C1 recall baseline", "vs 53.3%"),
    ("stale C2 bootstrap B", "100 study-cluster bootstrap"),
    ("stale C2 regression set", "480 estimates (281 studies)"),
    ("stale C2 within-content set", "302 estimates from 204 studies"),
    ("stale C2 overlap claim", "overlaps their lower ends"),
    ("stale denom_fine", "categories explains 10.3%"),
    ("stale sign-test p", "sign test *p* = .38"),
    ("over-read null", "shows no directional drift"),
    ("stale full-paper item count", "35 full-paper items"),
    ("stale Table 2 human items", "36 items in two batches"),
    ("interim two-batch phrasing", "in the two completed batches"),
    ("false third family", "a third family recoded"),
    ("mislabelled confirmation rate", "That second figure is an error rate"),
    ("overclaimed omission rate", "effectively zero"),
    ("stale repair study count", "repair added 148 studies"),
    ("stale shared-recall k", "k = 8 shared-recall"),
    ("unsupported within-behavioural gradient", "the gradient also holds within the behavioural studies"),
    # the value verification is scored but not yet written up: the §4.8 sentence returns with the
    # C1 write-up, and until then this cross-reference must not point at a note that lacks it.
    ("unreported value verification", "is reported in Supplementary Note B1"),
    ("unblinded adjudication unqualified", "upper bound 11.3% each). Supplementary Note B1"),
]


# --- 2026-09-02: round-3 human screening validation (adjudicated ledgers in round3_keys/) ---
_r3 = os.path.join(ROOT, "data/extract_v2/qa/round3_keys")
_af = list(csv.DictReader(open(os.path.join(ROOT, "docs/RA_package/round3_2026-08/A_adjudication_sacha_FILLED.csv"), encoding="utf-8")))
_a_miss = sum(1 for r in _af if r["ruling"] == "MISS")
add("r3 title misses", f"none was a study the review should have included ({_a_miss} of 150" if _a_miss == 0 else f"{_a_miss} of 150")
_b = list(csv.DictReader(open(os.path.join(_r3, "adjudication_B_union.csv"), encoding="utf-8")))
_b_miss = sum(1 for r in _b if r["ruling"] == "MISS")
add("r3 abstract misses", f"both of those were genuine misses ({_b_miss} of 40" if _b_miss == 2 else f"{_b_miss} of 40")
_c = list(csv.DictReader(open(os.path.join(_r3, "adjudication_C_FINAL.csv"), encoding="utf-8")))
_c_up = sum(1 for r in _c if r["pipeline_upheld"] == "True")
add("r3 fulltext upheld", f"upheld the pipeline in all {len(_c)} contested cases" if _c_up == len(_c) else f"upheld the pipeline in {_c_up} of {len(_c)}")
_d = list(csv.DictReader(open(os.path.join(_r3, "adjudication_D_FINAL.csv"), encoding="utf-8")))
_d_up = sum(1 for r in _d if r["dataset_upheld"] == "True")
# phrased in Table 2 as "Curation upheld in 11 of 14 disagreements"; assert the numbers as the
# manuscript actually states them, not as an earlier draft did.
add("r3 grey upheld", f"Curation upheld in {_d_up} of {len(_d)} disagreements")
_c_del = sum(1 for r in _c if r["ruled_by"] != "sacha"); _d_del = sum(1 for r in _d if r["ruled_by"] != "sacha")
# 2026-09-07: this assertion was UNREACHABLE (the script aborted at the ladder assert), and the
# sentence it guards had never been written -- a human-provenance fact left unstated. Now asserted
# against the disclosure added to Section 4.8.
add("r3 delegated rulings", f"he ruled {len(_c)-_c_del} of the {len(_c)} full-text cases, {_d_del} of the {len(_d)} grey-claim cases were settled by re-reading the producer's own publication and {_c_del} of the {len(_c)} full-text cases by re-reading the source")


# --- 2026-09-02: R² bootstrap intervals + within-content ladder (phaseB_metareg_robustness.R) ---
_bs = {r["moderator"]: r for r in rows("metareg_r2_bootstrap.csv")}
_wc = {r["moderator"]: r for r in rows("metareg_r2_within_content.csv")}
# 2026-09-07: the ladder reordered at the v1.7.16 re-freeze, so the leader named here is now the
# GROUND-TRUTH SOURCE, not measurement type. The old assertions expected the pre-rewrite prose and
# were unreachable, because the script aborted at the ladder-order assert before reaching them.
# Moved out of the Results into Note C2 (Sacha comment 398, 2026-09-17), which already carried
# the full ladder; assert it where it now lives.
add_in("B2.", "R2 gt CI", f"ground-truth source {_bs['ground_truth']['r2_adj']}% [{_bs['ground_truth']['ci_lo']}\u2013{_bs['ground_truth']['ci_hi']}]")
add("R2 topic CI", f"topic {_bs['topic']['r2_adj']}% [{_bs['topic']['ci_lo']}\u2013{_bs['topic']['ci_hi']}]")
# Cut from the main text on 2026-09-18 for length; the same ladder is asserted in C2 below
# ("C2 within-content ladder"), so the numbers are still checked against the pipeline.
_retired_within_content = (f"the ground-truth source explains {_wc['ground_truth']['r2_adj']}%, the identification level {_wc['id_method']['r2_adj']}%, measurement type {_wc['measurement']['r2_adj']}% and topic {_wc['topic']['r2_adj']}%, which puts topic above the denominator class, the platform and the sampling frame but still below every identification and measurement moderator ({_wc['topic']['n_estimates']} estimates from {_wc['topic']['n_studies']} studies")
assert all(int(r["B"]) == 200 for r in _bs.values()), "bootstrap B is not 200: the manuscript says 200 resamples"
# The claim that survives the overlapping intervals: topic's upper bound sits below every
# measurement moderator's lower bound. If that stops being true, the 2.6 sentence must change.
assert all(float(_bs["topic"]["ci_hi"]) < float(_bs[m]["ci_lo"])
           for m in ("ground_truth", "id_method", "measurement", "sampling")), \
    "topic's interval now overlaps a measurement moderator's: rewrite the 2.6 claim about the gap at the bottom"

# --- 2.9 demographic subgroups (phaseB_subgroups.py) ---
_sg = json.load(open(os.path.join(ROOT, "data/synth/phaseB/subgroups_summary.json"), encoding="utf-8"))
add("2.9 coverage", f"Only {_sg['n_subgroup_studies']} of the {_sg['n_studies_total']} included")
add("2.9 rows", f"contributing {_sg['n_subgroup_rows']} estimates")
add("2.9 behavioural", f"{_sg['n_behavioural_studies']} studies whose measurement type is behavioural")
# the set is the RoB-derived MEASUREMENT field (2026-09-07); the old local definition let 93 recall surveys in
assert _sg["n_behavioural_studies"] < 100, "the behavioural set is back to including recall surveys"
add("2.9 beh with subgroups", f"only\n{_sg['n_behavioural_with_subgroups']} do".replace("\n", " "))
add("2.9 political", f"{_sg['by_dimension'].get('political',0)} split respondents by party")
add("2.9 ratio", f"a median {_sg['political_ratio_median']}\u00d7 the left-leaning")

# --- re-checkability limitation: studies with no archived text (scan_missed_concentration.py) ---
_nt = len(list(csv.DictReader(open(os.path.join(ROOT,
      "data/extract_v2/qa/missed_concentration/no_local_text.csv"), encoding="utf-8"))))
_ro = list(csv.DictReader(open(os.path.join(ROOT, "data/rob/risk_of_bias_v3_master.csv"), encoding="utf-8")))
_ab = sum(1 for r in _ro if r.get("source_read") == "abstract_only")
add("abstract-only limitation", f"{_ab} studies were coded from the abstract alone")
# Every abstract-only study now has its abstract archived (2026-09-07); assert that stays true.
# The archive is publisher abstract text, so it is the one input this script reads that the public
# replication package cannot carry (see scripts/build_public_package.py). Outside the working
# repository the check has nothing to look at, so it reports itself skipped instead of failing:
# a third party running the package must not see a red herring where an input was withheld on
# purpose. Every other assertion in this file runs on the package as shipped.
_ABSDIR = os.path.join(ROOT, "data/fulltext/abstract")
if os.path.isdir(_ABSDIR):
    _missing = [r["id"] for r in csv.DictReader(open(os.path.join(ROOT,
        "data/extract_v2/qa/missed_concentration/no_local_text.csv"), encoding="utf-8"))
        if not os.path.exists(os.path.join(_ABSDIR, r["id"] + ".txt"))]
    assert not _missing, f"studies with neither a full text nor an archived abstract: {_missing}"
else:
    print("SKIPPED: archived abstracts (data/fulltext/abstract/) are not redistributed, so the "
          "check that every abstract-only study has its abstract on disk cannot run here. The "
          "studies and their DOIs are in data/extract_v2/qa/abstract_only_list.json.")

# ============================================================================================
# 2026-09-07 (c): the proofread's remaining contradictions. Two structural fixes drive this block:
# the Supplementary Notes were never regenerated at the v1.7.15/v1.7.16 re-freeze, and every
# assertion that a SI passage carries is anchored to its own section with add_in().
# ============================================================================================

# --- §2.2: the five ground-truth levels partition the main set; the blanks decompose by level ---
_gtm = _modal("ground_truth")
assert sum(_gtm.values()) == _N and "" not in _gtm, "ground-truth levels no longer partition the main set"
add("defs: respondents", f'in {_gtm["self_report"]} studies ({_p(_gtm["self_report"])}%), all surveys, the respondents themselves decided')
_cl_by = {s: (_Ctr([x["classification_level"] for x in rs if x["classification_level"]]).most_common(1)[0][0]
              if any(x["classification_level"] for x in rs) else "") for s, rs in _bys.items()}
_br_by = {s: (_Ctr([x["breadth"] for x in rs if x["breadth"]]).most_common(1)[0][0]
              if any(x["breadth"] for x in rs) else "") for s, rs in _bys.items()}
_blank_by_level = _Ctr(_cl_by[s] for s in _bys if _br_by[s] == "")
assert sum(_blank_by_level.values()) == _br[""], "the blank-breadth decomposition no longer sums to the blank count"
add_in("A5.", "defs: blanks decomposed",
    f'{_blank_by_level["source_level"]} of the {_cl["source_level"]} state none, because a domain list rates outlets rather than claims, and so do {_blank_by_level["claim_level"]} of the {_cl["claim_level"]} claim-level studies')

# --- §2.6: the breadth gradient is a CONTENT finding, and the denominator pair ---
# --- abstract-disclosure test on curated-sample studies (2026-09-11; Sacha: "well test it then") ---
_cad = list(csv.DictReader(open(os.path.join(ROOT, "data/extract_v2/qa/curated_abstract_disclosure_2026-09-11.csv"), encoding="utf-8")))
_notcur = {l.strip() for l in open(os.path.join(ROOT, "data/extract_v2/qa/curated_abstract_disclosure_2026-09-11_notcurated.txt"), encoding="utf-8") if l.strip() and not l.startswith("#")}
_cad = [r for r in _cad if r["study_id"] not in _notcur and r["disclosure"] != "no_abstract"]
_cadc = _Ctr(r["disclosure"] for r in _cad)
_cadh = [r for r in _cad if r["headline_pct_in_abstract"].strip().lower() == "yes"]
_cadhn = [r for r in _cadh if r["disclosure"] in ("sample_size_only", "not_stated")]
add_in("A7.", "disclosure: base", f"Among the {len(_cad)} studies in this corpus whose estimate rests on a rank-truncated or hand-selected sample, {_cadc['stated']} name the selection in the abstract, {_cadc['sample_size_only']} give only a sample size, and {_cadc['not_stated']} give neither")
add_in("A7.", "disclosure: headline", f"of the {len(_cadh)} abstracts that headline the percentage, {len(_cadhn)} ({round(100*len(_cadhn)/len(_cadh))}%) do so without saying how the sample was selected")
add("§2.6 gradient scope", "Wider definitions produce higher estimates within the content analyses")
_ra = {r["value"]: r for r in rows("slices_breadth_audience.csv")}
assert not (float(_ra["fabricated"]["sl_median"]) < float(_ra["false"]["sl_median"])
            < float(_ra["misleading"]["sl_median"])), \
    "the breadth gradient is now monotonic outside CONTENT too: the §2.6 scope caveat can be dropped"
add("§2.6 denom binary", f'explains almost none of the variance ({float(mr["denom"]["R2_adj"]):.1f}%, '
    + f'*p* = {float(mr["denom"]["QMp"]):.3f}'.replace("0.", ".", 1) + ")")
add("§2.6 denom_fine (full set)", f'the full set of denominator categories explains {float(mr["denom_fine"]["R2_adj"]):.1f}%')

# --- §2.8: Figure 5's comparison is cited, and the matched panels are all American ---
# RETIRED 2026-09-18b: the sentence citing Figure 5 for the comparison went with that paragraph
_caps = dict(re.findall(r'\("Figure (\d)\.", "([^"]+)"',
                        open(os.path.join(ROOT, "scripts/make_manuscript_docx.py"), encoding="utf-8").read()))
assert _caps["6"].split(".")[0] in MS_RAW, "Figure 6's caption text is not in the manuscript's figure list"
_mc_ctry = {c for i in {r["study"] for r in _mc_panels} for c in {r["country_norm"] for r in _all if r["id"] == i}}
assert _mc_ctry == {"United States"}, f"the matched concentration panels are no longer all US: {_mc_ctry}"

# --- §2.9: no subgroup row is pooled anywhere; the dimension tally is exhaustive ---
assert not any((r["demographic_group"] or "").strip() for r in _pool), "a subgroup row entered the main analysis set"
# Sacha cut this sentence on 2026-09-15 when he shortened section 2.9. The rule it stated - that a
# demographic row never enters a median, an interval or the meta-regression - still holds and is
# still stated in Methods ("proportion, non-demographic-subgroup estimates"), so the guard now
# anchors it there instead of retiring it.
add_in("4.9 Synthesis", "main-set excludes subgroups",
       "proportion, non-demographic-subgroup estimates")
assert sum(_sg["by_dimension"].values()) == _sg["n_subgroup_rows"], \
    "the subgroup dimension tally no longer sums to the row count"
# The dimension counts must still sum to the total: his shortened sentence dropped the residual and
# left 71 + 21 + 7 + 3 against 104 estimates, which a reader can add up.
# Every dimension is asserted, not just the two that happened to be written down. The prose said
# 21 by age and 7 by gender against the data's 19 and 8, and omitted the community split entirely,
# and none of it was guarded: the sentence's numbers no longer summed to the total it quoted.
_DIM_WORD = {"age": "by age", "gender": "by gender", "education": "by education",
             "office_level": "by the office a politician holds", "community": "by community"}
for _d, _w in _DIM_WORD.items():
    add(f"2.9 dimension {_d}", f"{_sg['by_dimension'].get(_d, 0)} {_w}")
add("2.9 political contrast studies",
    f"{NUM[_sg['n_studies_with_subgroup_dimension']['political']].capitalize()} studies report a "
    f"partisan split, and {NUM[_sg['political_contrast_studies']]} of them give both sides")
add("2.9 age contrasts",
    f"{NUM[_sg['age_contrast_studies']].capitalize()} studies allow an age contrast between their "
    f"oldest and youngest groups, giving "
    f"{NUM[len(_sg['age_contrast_older_higher']) + len(_sg['age_contrast_older_lower'])]} contrasts")

# The blind re-extraction subsample used to be quoted as the one check the construct ordering did
# not survive. That analysis was retired on 2026-09-17 (Sacha comment 682), so nothing asserts its
# ordering any more; the note that records the retirement asserts the cell sizes instead.

# --- Discussion: the behavioural literature sets no per-item standard (the Ecker rebuttal) ---
_beh_ids = {r["id"] for r in _pool if r["construct"] in ("EXPOSURE", "REACH", "SHARING", "CONCENTRATION")}
_beh_src_blank = sum(1 for s in _beh_ids if _cl_by[s] == "source_level" and _br_by[s] == "")
# Re-anchored 2026-09-18b: his Discussion rewrite replaced the two counts with "few studies have
# reported clear demographic breakdown of misinformation exposure". The numbers are unchanged and
# still stated in 2.6, so the assertion follows them there.
add_in("2.6", "Discussion subgroup coverage",
       f"Only {_sg['n_subgroup_studies']} of the {_nst} included studies report estimates broken down by demographic group")
add_in("2.6", "subgroup coverage, behavioural",
       f"among the {_sg['n_behavioural_studies']} studies whose measurement type is behavioural, only {_sg['n_behavioural_with_subgroups']} do")
# the two limitation counts must move together (the Discussion promises what C3 delivers)
assert MS.count("limitations qualify the synthesis") == 2, "the two limitation counts have diverged again"
add_in("3. Discussion", "Discussion behavioural breadth",
       f"of the {len(_beh_ids)} studies contributing an estimate in a behavioural construct, {_beh_src_blank} classify whole sources")

# --- §4.4: the two-stage retrieval ladder, and the 208 -> 141 repair ladder ---
_rep_txt = open(os.path.join(ROOT, "docs/corpus_repair_2026-09/REPAIR_REPORT.md"), encoding="utf-8").read()
_s1 = int(re.search(r"(\d+) sent to retrieval", _rep_txt).group(1))
_s2 = int(re.search(r"corrected criteria: \*\*(\d+) eligible", _rep_txt).group(1))
_screened = int(re.search(r"Papers screened at full text \| (\d+)", _rep_txt).group(1))
_incl = int(re.search(r"\| Included \| (\d+)", _rep_txt).group(1))
_excl = int(re.search(r"\| Excluded \| (\d+)", _rep_txt).group(1))
add("§4.4 retrieval ladder", f"passed {_s1 + _s2} records to full-text retrieval, of which {_screened} texts were "
    f"obtained ({_s1 + _s2 - _screened} could not be retrieved)")
add("§4.4 full-text split", f"{_incl} were eligible and {_excl} were not")
add("§4.4 two numbers", f"{_s1 + _s2} records were judged eligible from their titles or abstracts, but only "
    f"{_incl} of the {_screened} retrieved survived full-text screening")
_rep_ids = {r["id"] for r in csv.DictReader(open(os.path.join(
    ROOT, "data/extract_v2/repair_2026-09/repair_estimates_final.csv"), encoding="utf-8"))}
_rep_in_freeze = len(_rep_ids & {r["id"] for r in _all})
_rep_poolable = len({r["id"] for r in csv.DictReader(open(os.path.join(
    ROOT, "data/extract_v2/repair_2026-09/repair_estimates_final.csv"), encoding="utf-8")) if r["pool"] == "main"})
add("§4.4 repair ladder", f"The repair confirmed {len(_rep_ids)} studies at full text, of which {_rep_poolable} "
    f"carry a poolable estimate; {_rep_poolable - _rep_in_freeze} of those were removed in the later dispute "
    f"adjudication, leaving {_rep_in_freeze} in the released dataset")
# The repair's size left the Discussion with the sentence Sacha cut on 2026-09-15; §4.4 and Note C1
# still carry it, and both are asserted below.
# Section 4.4 said 141 carry a poolable estimate while C1 and the crosswalk said 131, and no
# assertion covered the 4.4 copy, so the two sat contradicting each other across three freezes.
# RETIRED 2026-09-18b: his compression of the criteria-defect passage cut this sentence; the number is still asserted twice, in §4.8 and in Table 2
add("§4.8 repair coverage", f"468 rows across 148 studies, {_rep_in_freeze} of which are in the released dataset")
add("Table 2 repair coverage", f"{_rep_in_freeze} are in the released dataset")

# Wave 5, the second coverage-completion pass. It had no row in Table 2 until Sacha asked whether
# the table was exhaustive (comment [0], 2026-09-18); it is the pass that takes the cross-family
# check to every study in the corpus, and the table carried only the smaller wave-4 pass.
_w5 = open(os.path.join(ROOT, "data/extract_v2/qa/gpt_check_2026-09_wave5_adjudication.md"),
           encoding="utf-8").read()
_w5_k = _re.search(r"construct \|\s*(\d+)\s*\|[^|]*\|\s*\*\*([0-9.]+)\*\*", _w5)
assert _w5_k, "wave-5 adjudication no longer states the construct n and kappa in its table"
add("Table 2 wave-5 row",
       f"{_w5_k.group(1)} estimates in the 22 studies no earlier pass had read")
add("Table 2 wave-5 kappa",
       f"Construct \u03ba = {round(float(_w5_k.group(2)), 2)} (37 of {_w5_k.group(1)})")

# --- §4.8: the confirmation rate, the omission bound, and the human item counts ---
add("fact-check confirmation rate", "confirming 83.1% outright. That second figure is a confirmation rate")
def _zero_event_ub(n):
    """exact binomial one-sided 95% upper bound with 0 events in n (the paper's other zero-event bounds)."""
    return 100 * (1 - 0.05 ** (1 / n))
_irr = {p: len(list(csv.DictReader(open(os.path.join(ROOT, f"docs/RA_package/irr_v2/{p}_sacha.csv"), encoding="utf-8"))))
        for p in ("part1", "part2", "part2b")}
add_in("B1.", "C1 human item counts", f"{_irr['part1']} items classified from the reported-quantity sentence plus "
       f"the paper's definition, and {_irr['part2'] + _irr['part2b']} items coded from the full paper")
add_in("B1.", "C1 full-paper batches", f"({_irr['part2'] + _irr['part2b']} full-paper items in two batches")
add("Table 2 human items", f"| {sum(_irr.values())} items in three deliveries")

# --- C1: the completed nine-batch run, the sign test, the human-verified pairs ---
# §4.8 runs four kinds of check, so C1's grade list must name four, not three (2026-09-07 audit)
add_in("B1.", "C1 grade count", "we distinguish four grades of evidence about coding quality and report all four")
for _g in ("Model self-consistency.", "Independent model.", "Blind re-extraction.", "Human coding."):
    add_in("B1.", f"C1 grade heading {_g.strip('.')}", _g)
from math import comb as _comb
def _sign_p(k, n):
    lo = min(k, n - k)
    return min(1.0, 2 * sum(_comb(n, i) for i in range(lo + 1)) / 2 ** n)
add_in("B1.", "correction symmetry p",
       f"(exact two-sided sign test, *p* = {_sign_p(_up, _up + _dn):.3f}".replace("0.", ".", 1) + ")")
for _c2, _lab2 in [("REACH", "Reach"), ("SHARING", "Sharing")]:
    add_in("B1.", f"C1 human-verified {_c2} pair",
           f"{_lab2} {_hv[_c2]['median_human']}% vs {_hv[_c2]['median_full']}%, k = {_hv[_c2]['k_human']}")
add_in("B1.", "C1 human-verified RECALL pair",
       f"Recall is the exception ({_hv['RECALL']['median_human']}% vs {_hv['RECALL']['median_full']}%) on "
       f"{NUM[int(_hv['RECALL']['k_human'])]} verified studies, too few to compare")

# --- Supplementary Note A was REMOVED on 2026-09-18 (Sacha deleted the whole note and its table
# from the supplement). Nine assertions lived here, all derived from appendix_content_sharing.csv:
# the five stratified rows of Supplementary Table 2, the claim/source ratio, the marginal medians
# and gap, the claim-level difference, and the construct's rank in the eta-squared ladder. They are
# retired rather than re-anchored because the prose that carried them is gone, not moved. The
# generator still runs and the CSV is still released, so the numbers remain reproducible; if the
# note ever comes back, restore this block from git history at f3809e1.

# Derived, not literal: this ladder was hardcoded and went stale at v1.7.20 while its own rank
# assertions above were being computed from the same file two lines earlier.
_ETA_LABEL = {"ground_truth": "ground truth", "topic": "topic", "sampling_frame": "sampling frame",
              "platform_norm": "platform", "classification_level": "classification level",
              "breadth": "breadth", "denom_scope": "denominator scope", "construct": "construct",
              "unit": "unit", "denom_selection": "denominator selection"}

# B1 and B2 carried their own copies of numbers the main text also states, and both went stale
# while the main text was re-synced (B1 said 456 studies appraised, B2 said Content 23.2 -> 24.3).
# Anchor each copy to the section it lives in.
_rob_rows = list(csv.DictReader(open(os.path.join(ROOT, "data/rob/risk_of_bias_v3_master.csv"),
                                     encoding="utf-8")))
_rob_pct = {}
for _r in _rob_rows:
    _rob_pct[_r["overall_ruling_corrected"]] = _rob_pct.get(_r["overall_ruling_corrected"], 0) + 1
_rob_n = sum(_rob_pct.values())
add_in("A1.", "B1 appraisal coverage",
       f'All {_rob_n} studies were appraised with the Hoy prevalence instrument '
       f'({round(100 * _rob_pct.get("HIGH", 0) / _rob_n)}% high, '
       f'{round(100 * _rob_pct.get("MODERATE", 0) / _rob_n)}% moderate, '
       f'{round(100 * _rob_pct.get("LOW", 0) / _rob_n)}% low risk')
add_in("A2.", "B2 fold-QUALITY pair",
       f'moves Content only from {_slc["CONTENT"]["sl_median"]}% to '
       f'{float(_sv("A2", "CONTENT")["median_pct"]):.1f}%')

# --- B1's unweighted-vs-weighted contrast (the eight generic items against the two design items) ---
add_in("A1.", "B1 unweighted vs weighted",
       f'from {float(_s6["CONTENT"]["median_all"]):.1f}% to {float(_s6["CONTENT"]["median_excl_high"]):.1f}%, '
       f'against {float(_sv("D exclude", "CONTENT")["median_pct"]):.1f}% when the two design items are weighted in')

# --- C2, rewritten to the 200-resample run (it still carried the 100-resample one) ---
add_in("B2.", "C2 bootstrap B", f"re-estimated on {_bs['ground_truth']['B']} study-cluster bootstrap resamples")
# denom_fine was missing from this list, so Note C2's denominator-class interval sat at the v1.7.21
# values (16.5% [9.4-25.5]) while the pipeline said 16.6% [9.7-25.9]. Found 2026-09-17 by reading
# the note, not by a guard: an unasserted number in an asserted paragraph is the easiest kind to miss.
for _m, _lab in [("ground_truth", "ground-truth source"), ("id_method", "identification level"),
                 ("construct", "construct"), ("measurement", "measurement type"),
                 ("denom_fine", "denominator class"),
                 ("sampling", "sampling frame"), ("platform", "platform"),
                 ("breadth", "breadth"), ("topic", "topic")]:
    # one decimal throughout: R drops a trailing zero, so 12.0 reaches the CSV as "12" and the
    # guard would otherwise demand "breadth 12%" in a paragraph where every other rung has one
    add_in("B2.", f"C2 rung {_m}",
           f"{_lab} {float(_bs[_m]['r2_adj']):g}% [{float(_bs[_m]['ci_lo']):g}–{float(_bs[_m]['ci_hi']):g}]"
           if float(_bs[_m]['r2_adj']) % 1 else
           f"{_lab} {float(_bs[_m]['r2_adj']):.1f}% [{float(_bs[_m]['ci_lo']):g}–{float(_bs[_m]['ci_hi']):g}]")
add_in("B2.", "C2 within-content set", f"content analyses ({_wc['topic']['n_estimates']} estimates from {_wc['topic']['n_studies']} studies)")
# Built from the file in rank order, with every rung. The hand-written version printed the rungs
# out of order (3.2 after 2.8) and omitted the two denominator moderators entirely.
_WC_LABEL = {"ground_truth": "ground-truth source", "id_method": "identification level",
             "measurement": "measurement type", "breadth": "breadth", "topic": "topic",
             "denom_fine": "denominator class", "denom": "the binary denominator contrast",
             "platform": "platform", "sampling": "sampling frame"}
add_in("B2.", "C2 within-content ladder",
       ", ".join(f"{_WC_LABEL[m]} {v}%" for v, m in
                 sorted(((float(r["r2_adj"]), r["moderator"]) for r in
                         rows("metareg_r2_within_content.csv")
                         if (r["r2_adj"] or "NA").strip() != "NA"), reverse=True)))
add_in("B2.", "C2 regression set", f"restricted to the {len(_reg)} estimates ({len({r['study_id'] for r in _reg})} studies) with an extractable sample size")
add_in("B2.", "C2 breadth uncoded", f"uncoded for {sum(1 for r in _reg if r['breadth'] == 'NA')} of the {len(_reg)} estimates")

# MODERATOR COVERAGE. The measurement moderator was joined from a 22 July risk-of-bias file
# covering 317 of 443 studies. When the corpus grew past it on 2026-09-04 the join silently started
# returning nothing: 40% of rows arrived NA, the model fitted them as an "unspecified" level that
# meant "not appraised yet", and the reported R² was wrong for a fortnight. Nothing noticed, because
# every check here asks whether a NUMBER IS PRESENT in the prose, and an uncoded cell produces no
# number to check. A moderator's uncoded share is declared below and asserted, so a join that
# degrades has to be acknowledged rather than absorbed.
_MOD_UNCODED_MAX = {          # moderator: highest share of uncoded rows the paper accounts for
    "construct": 0.0, "measurement": 0.0, "sampling": 0.0, "denom": 0.0,
    "ground_truth": 0.0, "id_method": 0.0, "topic": 0.0,
    "platform": 0.02,         # a handful of estimates name no platform
    "denom_fine": 0.06,       # unspecified denominator class, disclosed in Note B2
    "breadth": 0.30,          # sources stating no veracity standard, 204 of 837, disclosed in B2
}
_reg_rows = list(csv.DictReader(open(os.path.join(ROOT, "data/synth/phaseB/regression_data.csv"),
                                    encoding="utf-8")))
for _m, _cap in _MOD_UNCODED_MAX.items():
    _bad = sum(1 for _r in _reg_rows if (_r.get(_m) or "").strip() in ("", "NA", "unspecified"))
    _share = _bad / len(_reg_rows)
    if _share > _cap:
        misses_xref.append(("moderator coverage",
                            f"{_m} is uncoded on {_bad} of {len(_reg_rows)} rows ({_share:.0%}), "
                            f"above the {_cap:.0%} this paper declares — a join has degraded, or "
                            f"the declared share needs updating with a reason"))

# --- display items must be cited in prose, and the SI tables numbered in order of first citation ---
assert len(re.findall(r"(?<!Supplementary )Table 2", MS)) >= 2, "Table 2 is never cited in the prose"
# What EXISTS: the supplementary notes that have a heading and the tables/figures that have a
# caption. Derived, never hardcoded — the old list named Note A, and a hardcoded list goes stale
# exactly when the document changes under it (Note A was removed on 2026-09-18).
_headings = set(_re.findall(r"## (Supplementary Note [A-F])\.", MS_RAW))
_labels = set(_re.findall(r"\*\*(Supplementary (?:Table|Fig\.) \d+)\.", MS_RAW))
_labels |= set(_caption_text and _re.findall(r"(Supplementary Fig\. \d+)\.", _caption_text()) or [])

# Two directions, both reported rather than raised, so neither can hide the other assertions.
# UNCITED: it exists and no prose points at it.
for _t in sorted(_headings | _labels):
    if MS.count(_t) < 2:
        misses_xref.append((f"uncited display item", f"{_t} exists but no prose cites it"))
# DANGLING: prose points at it and it does not exist. Removing Note A left the main text saying
# "Supplementary Note A compares the two constructs ...", and nothing caught it, because every
# other check asks whether a number is PRESENT, never whether a pointer RESOLVES.
for _m in sorted(set(_re.findall(r"Supplementary Note [A-F]\b", MS))
                 | set(_re.findall(r"Supplementary (?:Table|Fig\.) \d+", MS))):
    if _m not in _headings and _m not in _labels:
        misses_xref.append(("dangling cross-reference", f"{_m} is cited but does not exist"))
# Generalised when Supplementary Table 3 was added (2026-09-15): check EVERY supplementary table
# and figure, not just the first pair, so a new one cannot be introduced out of citation order.
for _kind in ("Supplementary Table", "Supplementary Fig."):
    _order, _seen_k = [], set()
    for _m in _re.finditer(_kind + r" (\d)", MS):
        if _m.group(1) not in _seen_k:
            _seen_k.add(_m.group(1)); _order.append(int(_m.group(1)))
    if _order != sorted(_order):
        # Reported, not raised: an ordering fault is a real defect but it must not hide the other
        # 270 assertions behind an exception, and it is usually the visible end of a decision the
        # author still has to make (here, whether a figure whose subject was cut still belongs).
        misses_xref.append(("display-item order",
                            f"{_kind}s are not cited in numerical order: first mentions run {_order}"))
# ORPHANED REFERENCES: an entry in the list that nothing cites. The builder drops it silently when
# it numbers by first appearance, so the shipped document looks right while the master carries a
# dead entry — which is how Baribi-Bartov et al. 2024 survived Sacha cutting the only sentence that
# cited it (2026-09-18b). Reported, with the CITE_MAP key that would have matched.
try:
    import importlib
    _nhb = importlib.import_module("make_nhb_docx")
    _refs_s, _supp_s = MS_RAW.index("## References"), MS_RAW.index("## Supplementary Note A")
    _body = MS_RAW[:_refs_s] + MS_RAW[_supp_s:]
    for _e in (ln.strip() for ln in MS_RAW[_refs_s:_supp_s].split("\n")):
        if not _re.match(r"^[A-Z\u00c0-\u00dd][^|]*\(\d{4}[a-z]?\)\.", _e):
            continue
        _keys = [k for k, pref in _nhb.CITE_MAP.items() if _e.startswith(pref)]
        if not _keys:
            misses_xref.append(("reference not in CITE_MAP", _e[:90]))
        elif not any(k in _body for k in _keys):
            misses_xref.append(("orphaned reference", f"{_e[:80]} ... is in the list, cited nowhere"))
except Exception as _exc:
    print(f"  note: orphaned-reference check could not run ({_exc})")

assert not _re.search(r"\b[Ss]ections?\s+\d", MS), "mixed cross-reference styles: the master uses §X.Y throughout"


def main():
    misses = []
    for label, s in checks:
        if _re.sub(r"\s+", " ", s) not in _re.sub(r"\s+", " ", MS):
            misses.append((label, s))
    for heading, label, s in section_checks:
        if _re.sub(r"\s+", " ", s) not in _section_body(heading):
            misses.append((f"{label} [in '{heading}']", s))
    misses.extend(misses_xref)
    caps = _caption_text()
    for label, st in figure_checks:
        if _re.sub(r"\s+", " ", st) not in caps:
            misses.append((f"{label} [in a figure caption]", st))
    n = len(checks) + len(section_checks) + len(figure_checks)
    stale = [(label, s) for label, s in MUST_NOT if _re.sub(r"\s+", " ", s) in _re.sub(r"\s+", " ", MS)]
    print(f"Derived-stats check: {n - len(misses)}/{n} present "
          f"({len(section_checks)} section-anchored, {len(figure_checks)} in captions), "
          f"{len(MUST_NOT) - len(stale)}/{len(MUST_NOT)} stale strings absent")
    if misses:
        print("\nMISMATCHES (pipeline value NOT found in manuscript):")
        for label, s in misses:
            print(f"  [{label}] expected to find '{s}'")
    if stale:
        print("\nSTALE STRINGS (superseded value still present in manuscript):")
        for label, s in stale:
            print(f"  [{label}] must not contain '{s}'")
    if MISSING_SECTIONS:
        print("\nMISSING SECTIONS (an assertion is anchored to a heading that does not exist):")
        for _p in sorted(MISSING_SECTIONS):
            print(f"  no heading starts with {_p!r} — renumbered or renamed? update the anchor")
    if STALE_SUPP:
        print("\nSTALE SUPPLEMENTARY DATA:")
        for _m in STALE_SUPP:
            print(f"  {_m}")
    if PENDING:
        print("\nPENDING (section 2.4 placeholders; fill from "
              "data/synth/phaseB/metareg_r2_bootstrap.csv when the bootstrap finishes):")
        for _ph in PENDING:
            print(f"  {_ph}")
    if misses or stale or PENDING or STALE_SUPP or MISSING_SECTIONS:
        sys.exit(1)
    print("PASS — all checked derived stats appear in the manuscript; no banned stale strings.")


if __name__ == "__main__":
    main()
