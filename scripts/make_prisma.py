#!/usr/bin/env python3
"""PRISMA 2020 flow diagram, GENERATED from the reconciliation, never hardcoded.

Every count on the figure is derived: from data/synth/prisma_counts.json (written by
scripts/validate_prisma.py), from the freeze named in docs/FROZEN.md, or from the screening and
arm ledgers themselves. A flow diagram is the one figure a reader checks with a calculator, so the
script asserts its own arithmetic before it writes anything:

  * the four terminal outcomes partition the assessed set (PRISMA's bottom-up reconciliation);
  * the per-stream contributions to the retrieval box sum to that same assessed set, so the reader
    can add the boxes down the page and land on the retrieval total;
  * the Scopus spine closes at the title stage, and the abstract/stage-5 coverage of the
    title-advanced records accounts for every one of them;
  * no text line overflows its box, and the canvas fits everything drawn on it.

WHAT THE LEDGER CANNOT SUPPORT, THE FIGURE NAMES. Two arms ran full-text screens whose per-record
outcomes live in the arm reports rather than in the record ledger validate_prisma.py reconciles:
citation snowballing (331 advanced to retrieval, only its retained studies carry a terminal state)
and the corpus repair (335 screened at full text, likewise). Those residuals are drawn as a note
instead of being absorbed into a box. The same is true of the title-advanced records that never
reached a second screen; they get their own box rather than disappearing between two totals.

PRISMA 2020 structure: databases/registers and "other methods" (citation searching) appear as
separate identification arms, per the 2020 template.

Inputs : data/synth/prisma_counts.json  (run scripts/validate_prisma.py first)
Outputs: docs/prisma_flow.svg (+ .png if rsvg-convert or cairosvg is available)

Run: python3 scripts/validate_prisma.py && python3 scripts/make_prisma.py
"""

import csv
import glob
import json
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COUNTS = os.path.join(ROOT, "data/synth/prisma_counts.json")

P = lambda *a: os.path.join(ROOT, *a)


# --- text metrics -----------------------------------------------------------------------------
# Helvetica advance widths (AFM, per 1000 em). Box heights and line breaks are computed from these,
# so a bad width estimate surfaces as an overflowing line, which the final assertion refuses to
# write. Box text used to be wrapped at a fixed character count, which silently ran past the border
# whenever a line happened to be full of wide glyphs.
_W = {" ": 278, "!": 278, '"': 355, "%": 889, "&": 667, "'": 191, "(": 333, ")": 333,
      "*": 389, "+": 584, ",": 278, "-": 333, ".": 278, "/": 278, ":": 278, ";": 278,
      "<": 584, "=": 584, ">": 584, "?": 556, "·": 333, "’": 222, "–": 556}
for _c in "0123456789":
    _W[_c] = 556
for _c, _w in zip("abcdefghijklmnopqrstuvwxyz",
                  [556, 556, 500, 556, 556, 278, 556, 556, 222, 222, 500, 222, 833,
                   556, 556, 556, 556, 333, 500, 278, 556, 500, 722, 500, 500, 500]):
    _W[_c] = _w
for _c, _w in zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                  [667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667, 556, 833,
                   722, 778, 667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611]):
    _W[_c] = _w

OVERFLOW = []          # (text, pixels over its box) for every line drawn; asserted at the end
PAD, LH, TOP, BOT = 12, 16, 20, 12


def tw(s, fs, bold=False):
    return sum(_W.get(c, 600) for c in s) / 1000.0 * fs * (1.06 if bold else 1.0)


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def wrap(text, maxw, fs, bold=False, indent="   "):
    """Greedy wrap to a pixel width; continuation lines are indented."""
    out, cur = [], ""
    for word in text.split(" "):
        cand = f"{cur} {word}".strip() if cur else word
        if cur and tw((indent if out else "") + cand, fs, bold) > maxw:
            out.append(cur)
            cur = word
        else:
            cur = cand
    out.append(cur)
    return [out[0]] + [indent + ln for ln in out[1:]]


def box(x, y, w, lines, fill="#ffffff", stroke="#334155", fs=12.5, bold0=True):
    """Draw a box sized to its wrapped text. Returns (svg, height)."""
    maxw = w - 2 * PAD
    flat = []
    for i, ln in enumerate(lines):
        b = bold0 and i == 0
        flat += [(sub, b) for sub in wrap(ln, maxw, fs, b)]
    h = TOP + LH * (len(flat) - 1) + BOT
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" '
         f'fill="{fill}" stroke="{stroke}"/>']
    ty = y + TOP
    for txt, b in flat:
        OVERFLOW.append((txt, tw(txt, fs, b) - maxw))
        bb = ' font-weight="700"' if b else ""
        o.append(f'<text x="{x+PAD}" y="{ty}" font-size="{fs}"{bb} '
                 f'fill="#0f172a">{esc(txt)}</text>')
        ty += LH
    return "\n".join(o), h


def arrow(x1, y1, x2, y2):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#334155" '
            f'stroke-width="1.3" marker-end="url(#a)"/>')


def line(x1, y1, x2, y2):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="#334155" stroke-width="1.3"/>')


# --- data -------------------------------------------------------------------------------------
def canon(x):
    """Normalise the six ID schemes, exactly as validate_prisma.py does."""
    x = str(x or "").strip().replace("https://openalex.org/", "")
    if x.startswith("OA-"):
        x = x[3:]
    if x.startswith("PMID-"):
        return x
    if re.fullmatch(r"\d+", x):
        return "PMID-" + x
    return x


def rc(path):
    return list(csv.DictReader(open(P(path), encoding="utf-8", errors="replace"))) \
        if os.path.exists(P(path)) else []


def rj(path):
    out = []
    for ln in open(P(path), encoding="utf-8", errors="replace"):
        ln = ln.strip()
        if ln:
            try:
                out.append(json.loads(ln))
            except ValueError:
                pass
    return out


def ids(rows, field):
    return {canon(r.get(field)) for r in rows if r.get(field)} - {""}


# The reason each terminal state prints on the figure, in the order the excluded box lists them.
# Module-level because scripts/make_si_lists.py imports it: the supplementary exclusion list and the
# figure have to group records under the same labels or the two documents disagree about why a
# quarter of the corpus left the funnel. It used to match these labels by string prefix, which made
# two labels that start alike a silent mis-filing.
#
# PRISMA item 17 wants an ELIGIBILITY CRITERION, not the stage that applied it. Five labels used to
# end "(review of pending records)" or "(September behavioural query)" — the name of a pipeline
# pass, which tells a reader nothing about why the record was ineligible — and the
# DROPPED_V2_UNLEDGERED label announced that no reason was logged. The per-record reasons behind
# that state were recovered from the campaign ledgers on 2026-09-15 (see
# data/extract_v2/qa/exclusion_reasons_2026-09-15_REPORT.md), so the label now says what the
# records have in common instead.
EXCL_LABELS = [
    ("DROPPED", "No qualifying estimate at full text: no denominator, curated sample, wrong construct, or secondary source"),
    ("VERIFY_REJECTED", "Not eligible on full-text re-reading: wrong construct, no denominator, or not empirical"),
    ("DROPPED_V2_UNLEDGERED", "No qualifying estimate at the second full-text extraction, or a duplicate of a counted record"),
    ("DISP_EXCLUDED", "Not a prevalence or exposure estimate"),
    ("DEDUP_COLLAPSED", "Duplicate of an included record"),
    ("DISP_EXCLUDED_TITLE_SCREEN", "Off-topic on the title, with no retrievable full text"),
    ("DISP_EXCLUDED_OUT_OF_SCOPE", "Out of scope: producer-side, curated or secondary, not audience consumption"),
    ("DISP_EXCLUDED_FULL_TEXT", "Not eligible on full-text reading: no qualifying estimate"),
    ("DISP_DUPLICATE_RECORD", "Duplicate publication of an included record"),
    ("ARM_EXCLUDED_FULL_TEXT", "Not eligible on full-text reading: no falsity coding, stance not falsity, or no numeric estimate"),
    ("ARM_EXCLUDED_AT_RULING", "Extracted, then excluded: quality-only, value not printed by the study, or unreliable tables"),
]


def load():
    d = json.load(open(COUNTS, encoding="utf-8"))
    ident, ts = d["identified"], d["terminal_states"]

    # Ruling P1 (2026-09-14) folded the September behavioural arm into the identified total as a
    # fifth database stream. The Google Scholar recall check stays out: it is a probe of the primary
    # query's recall, not a search arm, and is reported the way the supplementary concentration
    # query already is.
    db = (ident["scopus_corpus"] + ident["openalex_netnew"] + ident["pubmed_netnew"]
          + ident["behavioural_arm_netnew"])
    arm = d["behavioural_arm"]

    title_excl = d["title_screen"].get("EXCLUDE", 0)
    title_adv = d["title_screen"].get("INCLUDE", 0) + d["title_screen"].get("MAYBE", 0)
    abs_excl = d["abstract_screen"].get("EXCLUDE", 0)
    st5_excl = d["stage5_screen"].get("EXCLUDE", 0)

    # The behavioural arm's records reach terminal states at four different stages, and only the
    # ones that reached FULL TEXT belong in the retrieval column. Its abstract-stage exclusions are
    # a screening outcome of its own stream, reported in the arm's box, so they come out of the
    # sought-for-retrieval total rather than inflating it.
    arm_abs_excl = ts.get("ARM_EXCLUDED_ABSTRACT", 0)
    assessed_total = d["included_or_staged_to_reconcile"] - arm_abs_excl
    included = ts.get("INCLUDED_FROZEN", 0)
    not_retrieved = ts.get("INCLUDED_NOT_RETRIEVED", 0) + ts.get("ARM_NOT_RETRIEVED", 0)
    no_data = (ts.get("DISP_INCLUDED_NO_DATA", 0) + ts.get("DISP_INCLUDED_RECOVERED", 0)
               + ts.get("ARM_INCLUDED_NO_DATA", 0))

    # Substantive reasons, in PRISMA's sense; the pipeline stage that produced each is in the
    # research log, not on the figure. Keyed by terminal state (see EXCL_LABELS above) so that
    # KNOWN below can check the mapping is total.
    excl_reasons = [(lab, ts.get(st, 0)) for st, lab in EXCL_LABELS]
    excl_total = sum(n for _, n in excl_reasons)

    # A terminal state this script does not know about would silently shrink the excluded box and
    # break the reconciliation with a bare arithmetic message. Two such states were added to the
    # ledger after this script was written, and the figure then sat unregenerated for several
    # freezes. Name the offender instead.
    KNOWN = ({st for st, _ in EXCL_LABELS}
             | {"INCLUDED_FROZEN", "INCLUDED_NOT_RETRIEVED",
                "DISP_INCLUDED_NO_DATA", "DISP_INCLUDED_RECOVERED",
                "ARM_NOT_RETRIEVED", "ARM_INCLUDED_NO_DATA", "ARM_EXCLUDED_ABSTRACT"})
    unknown = {k: v for k, v in ts.items() if k not in KNOWN and v}
    assert not unknown, (
        f"PRISMA: terminal state(s) not mapped to a flow box: {unknown}. "
        f"Give each one a box or an exclusion reason in make_prisma.py.")

    # ASSERTION 1 (bottom-up): the four outcomes must partition the assessed set exactly.
    lhs = included + not_retrieved + no_data + excl_total
    assert lhs == assessed_total, (
        f"PRISMA does not reconcile: {included}+{not_retrieved}+{no_data}+{excl_total}"
        f" = {lhs} but assessed = {assessed_total}. Fix the ledger, do not fudge the figure.")

    # ---- the freeze ---------------------------------------------------------------------------
    spec = open(P("docs/FROZEN.md"), encoding="utf-8").read()
    fp = re.search(r"File:\s*(\S+)", spec).group(1).strip("`")
    rows = list(csv.DictReader(open(P(fp), encoding="utf-8")))
    ver = re.search(r"v([\d.]+)", os.path.basename(fp)).group(1)
    frozen = ids(rows, "id")

    # ---- the Scopus spine ---------------------------------------------------------------------
    title_rows = rc("data/screen_title_2026-06-20.csv")
    abs_rows = rc("data/screen_abstract_2026-06-21.csv")
    st5_rows = rc("data/screen_stage5_2026-06-21.csv")
    tadv = {canon(r["eid"]) for r in title_rows if r.get("label") in ("INCLUDE", "MAYBE")}
    A, S5 = ids(abs_rows, "eid"), ids(st5_rows, "eid")

    # Stage 2 could only screen the records for which an abstract was retrievable; the rest were
    # routed to the stage-5 full-text gate, which did not reach all of them. That remainder is a
    # real hole in the spine, so it is counted here and drawn, not left between two totals.
    title_dups = ident["scopus_corpus"] - (title_excl + title_adv)
    n_abs_screened = len(A & tadv)
    n_st5_new = len(S5 - A)
    n_st5_reread = len(S5 & A)
    n_no_second_screen = len(tadv - (A | S5))

    # 165 records carry BOTH an abstract-stage and a stage-5 label, so the per-file label counts
    # cannot be subtracted from 2,759 without double-counting. Resolve one outcome per record
    # (include beats exclude beats maybe) and report that partition, which does subtract.
    inc_abs = {canon(r["eid"]) for r in abs_rows if r.get("label") == "INCLUDE"}
    inc_st5 = {canon(r["eid"]) for r in st5_rows if r.get("label") == "INCLUDE"}
    exc_scr = ({canon(r["eid"]) for r in abs_rows if r.get("label") == "EXCLUDE"}
               | {canon(r["eid"]) for r in st5_rows if r.get("label") == "EXCLUDE"})
    tagged = ids(rc("data/extract/include635_tagged.csv"), "eid")
    spine_inc = tadv & (inc_abs | inc_st5 | tagged)
    spine_exc = (tadv - spine_inc) & exc_scr
    spine_maybe = (tadv - spine_inc - spine_exc) & (A | S5)

    # ASSERTION 2 (spine, top-down): identification and the title stage must close, and the four
    # resolved outcomes must partition the title-advanced records exactly.
    assert title_excl + title_adv + title_dups == ident["scopus_corpus"], (
        f"PRISMA spine: {title_excl}+{title_adv}+{title_dups} != {ident['scopus_corpus']}")
    assert (len(spine_inc) + len(spine_exc) + len(spine_maybe) + n_no_second_screen
            == title_adv == len(tadv)), (
        f"PRISMA spine: {len(spine_inc)}+{len(spine_exc)}+{len(spine_maybe)}"
        f"+{n_no_second_screen} != {title_adv}")
    assert n_abs_screened + n_st5_new + n_no_second_screen == title_adv, (
        f"PRISMA spine coverage: {n_abs_screened}+{n_st5_new}+{n_no_second_screen} != {title_adv}")

    # ---- who reaches the retrieval box, and from which stream -----------------------------------
    # The retrieval total is defined bottom-up by validate_prisma.py's partition. Without this
    # decomposition the figure showed a box whose number could not be reached by adding anything
    # above it. The sets below are the SAME ledgers validate_prisma.py unions into `advanced`; the
    # assertion at the end of this block is what keeps the two from drifting apart -- this file
    # re-derives stream ATTRIBUTION only, never terminal states.
    staged = ids(rc("data/extract_v2/qa/openalex_candidates_STAGED.csv"), "id")
    oa_rows, pm_rows = rj("data/openalex_adjudicate.jsonl"), rj("data/pubmed_adjudicate.jsonl")
    inc_oa = {canon(r["oaid"]) for r in oa_rows if r.get("label") == "INCLUDE"}
    inc_pm = {canon(r["pmid"]) for r in pm_rows if r.get("label") == "INCLUDE"}
    arm_disp = {canon(r["id"]): r["disposition"]
                for r in rc("data/extract_v2/qa/behavioural_arm_dispositions.csv") if r.get("id")}
    arm_abs_ids = {k for k, v in arm_disp.items() if v == "ARM_EXCLUDED_ABSTRACT"}
    repair_rows = rc("data/extract_v2/repair_2026-09/repair_screen.csv")
    repair_ids = ids(repair_rows, "item_id")
    snow_rows = rj("data/snowball/advancing.jsonl")
    snow_ids = {canon(r["oaid"]) for r in snow_rows}
    scholar_ids = {canon(r["id"]) for r in rows if r.get("source") == "scholar_arm_2026-09"}

    assessed_ids = ((inc_abs | inc_st5 | tagged | inc_oa | inc_pm | staged
                     | set(arm_disp) | frozen) - {""}) - arm_abs_ids
    scopus = (inc_abs | inc_st5 | tagged) & assessed_ids
    oapm = ((inc_oa | staged | inc_pm) - scopus) & assessed_ids
    behav = ((set(arm_disp) - arm_abs_ids) - scopus - oapm) & assessed_ids
    repair = (repair_ids - scopus - oapm - behav) & assessed_ids
    snow = (snow_ids - scopus - oapm - behav - repair) & assessed_ids
    scholar = (scholar_ids - scopus - oapm - behav - repair - snow) & assessed_ids
    direct = assessed_ids - scopus - oapm - behav - repair - snow - scholar
    streams = [("Scopus", len(scopus)), ("OpenAlex keyword and PubMed", len(oapm)),
               ("September behavioural query", len(behav)), ("corpus repair", len(repair)),
               ("citation snowballing", len(snow)), ("Google Scholar recall check", len(scholar)),
               ("seed and hand-added records", len(direct))]

    # ASSERTION 3 (top-down): the streams drawn above the retrieval box must sum to it.
    assert len(assessed_ids) == assessed_total, (
        f"PRISMA: stream union is {len(assessed_ids)} but the ledger's assessed set is "
        f"{assessed_total}; the two derivations have drifted.")
    assert sum(n for _, n in streams) == assessed_total, (
        f"PRISMA: streams sum to {sum(n for _, n in streams)}, assessed = {assessed_total}")

    # ---- the arms' own funnels ------------------------------------------------------------------
    netnew_total = ident["openalex_netnew"] + ident["pubmed_netnew"]
    netnew_adj = len(oa_rows) + len(pm_rows)
    netnew_inc = len(inc_oa) + len(inc_pm)

    snow_screen = [r for f in sorted(glob.glob(P("data/snowball/screen/*.csv")))
                   for r in csv.DictReader(open(f, encoding="utf-8", errors="replace"))]
    snow = dict(core=sum(1 for _ in open(P("data/snowball/core_dois.txt"), encoding="utf-8")),
                candidates=len(rj("data/snowball/candidates.jsonl")),
                screened=len(snow_screen),
                excluded=sum(1 for r in snow_screen if r.get("label") == "EXCLUDE"),
                advancing=len(snow_rows),
                ledgered=len(snow_ids & assessed_ids))

    rep_est = rc("data/extract_v2/repair_2026-09/repair_estimates_final.csv")
    repair_stats = dict(pool=title_excl + abs_excl,
                        fulltext=len(repair_rows),
                        eligible=sum(1 for r in repair_rows if r.get("screen") == "INCLUDE"),
                        excluded=sum(1 for r in repair_rows if r.get("screen") == "EXCLUDE"),
                        main_pool=len({r["id"] for r in rep_est if r.get("pool") == "main"}),
                        ledgered=len(repair_ids & assessed_ids))

    return dict(ident=ident, db=db, arm=arm, ver=ver, n_est=len(rows),
                title_excl=title_excl, title_adv=title_adv, title_dups=title_dups,
                abs_excl=abs_excl, st5_excl=st5_excl,
                maybe_not_selected=d.get("maybe_not_selected", 0),
                n_abs_screened=n_abs_screened,
                n_st5_new=n_st5_new, n_st5_reread=n_st5_reread,
                n_no_second_screen=n_no_second_screen,
                spine_inc=len(spine_inc), spine_exc=len(spine_exc),
                spine_exc_abs=len(spine_exc & {canon(r["eid"]) for r in abs_rows
                                               if r.get("label") == "EXCLUDE"}),
                spine_maybe=len(spine_maybe),
                scopus_adv=len(scopus), scopus_tagged=len(scopus - tadv),
                netnew_total=netnew_total, netnew_adj=netnew_adj, netnew_inc=netnew_inc,
                netnew_staged=len(oapm) - netnew_inc, netnew_adv=len(oapm),
                snow=snow, repair=repair_stats, streams=streams,
                assessed=assessed_total, included=included, not_retrieved=not_retrieved,
                nr_main=ts.get("INCLUDED_NOT_RETRIEVED", 0), nr_arm=ts.get("ARM_NOT_RETRIEVED", 0),
                no_data=no_data, excl_reasons=excl_reasons, excl_total=excl_total,
                n_behav=len({r["id"] for r in rows if r["source"] == "behavioural_arm_2026-09"}),
                n_scholar=len(scholar), n_repair=repair_stats["ledgered"])


# --- drawing ----------------------------------------------------------------------------------
W = 1300
LX, LW = 70, 440            # the spine
MX, MW = 525, 360           # side outcomes (exclusions, records not retrieved)
RX, RW = 910, 360           # the parallel identification streams
BUS = RX - 15               # vertical bus carrying the parallel streams down into the spine
GAP = 34


def main():
    d = load()
    s = []

    def put(x, y, w, lines, **kw):
        svg, h = box(x, y, w, lines, **kw)
        s.append(svg)
        return y + h

    i, a, sn, rp = d["ident"], d["arm"], d["snow"], d["repair"]

    # ---- identification -------------------------------------------------------------------------
    y0 = 74
    yl = put(LX, y0, LW, [
        f'Records identified from databases (n = {d["db"]:,})',
        f'Scopus {i["scopus_corpus"]:,} · OpenAlex keyword {i["openalex_netnew"]:,} · '
        f'PubMed {i["pubmed_netnew"]:,} · OpenAlex behavioural and preprint-venue query '
        f'{i["behavioural_arm_netnew"]:,} (September 2026)'], fill="#f1f5f9")

    # Each stream that joins the funnel between the abstract screen and the retrieval box gets its
    # own box, ending in the number it contributes. The two arms whose full-text decisions are not
    # in the record ledger say so on the face of the figure.
    arms = [
        (["Databases: OpenAlex keyword and PubMed, screened in their own stream "
          f'(n = {d["netnew_total"]:,})',
          f'{d["netnew_total"]-d["netnew_adj"]:,} excluded at screening, {d["netnew_adj"]} '
          f'adjudicated, {d["netnew_inc"]} included; {d["netnew_staged"]} further OpenAlex '
          f'records staged for retrieval.',
          f'{d["netnew_adv"]} advance to retrieval'], "#f1f5f9"),
        ([f'Databases: September behavioural and preprint-venue query, screened in its own stream '
          f'(n = {i["behavioural_arm_netnew"]:,})',
          f'{a["duplicates_collapsed"]} duplicates removed, {a["records_screened_unique"]:,} '
          f'unique; {a["title_screen"].get("EXCLUDE", 0):,} excluded at title; '
          f'{a["sought_for_retrieval"]} sought; {a["terminal_states"].get("ARM_EXCLUDED_ABSTRACT", 0)} '
          f'excluded at abstract adjudication.',
          f'{a["sought_at_full_text"]} advance to retrieval ({a["assessed_at_full_text"]} assessed '
          f'at full text, {a["not_retrieved"]} not retrieved); {d["n_behav"]} studies held'],
         "#f1f5f9"),
        ([f'Other methods: OpenAlex citation snowballing (n = {sn["candidates"]:,})',
          f'backward and forward citations of {sn["core"]} core studies; {sn["screened"]:,} '
          f'candidates screened, {sn["excluded"]:,} excluded.',
          f'{sn["advancing"]} advance to full-text retrieval, of which {sn["ledgered"]} carry a '
          f'terminal state in the record ledger and {sn["advancing"]-sn["ledgered"]} do not '
          f'(see the note below)'], "#fff7ed"),
        ([f'Other methods: corpus repair (n = {rp["pool"]:,})',
          f'this review’s own {d["title_excl"]:,} title-stage and {d["abs_excl"]:,} '
          "abstract-stage exclusions, re-screened under corrected criteria by two independent "
          "model families; "
          f'{rp["fulltext"]} papers retrieved and screened at full text, {rp["eligible"]} eligible, '
          f'{rp["excluded"]} excluded.',
          f'{rp["main_pool"]} of the {rp["eligible"]} carried a main-pool estimate at the repair’s '
          f'own freeze; {rp["ledgered"]} survive in the current freeze and carry a terminal state, '
          f'{rp["fulltext"]-rp["ledgered"]} do not (see the note below)'], "#fff7ed"),
        (["Other methods: Google Scholar recall check",
          "a hand-run probe of the primary query’s recall rather than a search arm; "
          f'{d["n_scholar"]} studies held'], "#fff7ed"),
    ]
    yr, mids = y0, []
    for lines, fill in arms:
        top = yr
        yr = put(RX, yr, RW, lines, fill=fill, fs=11.5)
        mids.append((top + yr) / 2)
        yr += 12
    yr -= 12

    # ---- the Scopus spine ------------------------------------------------------------------------
    y = yl + GAP
    s.append(arrow(LX + LW // 2, yl, LX + LW // 2, y))
    top = y
    y = put(LX, y, LW, [f'Scopus records screened at title (n = {d["title_excl"]+d["title_adv"]:,})',
                        f'{d["title_dups"]} duplicate records removed before screening'])
    mid = (top + y) / 2
    put(MX, top, MW, [f'Excluded at title screen (n = {d["title_excl"]:,})',
                      "not a study of misinformation prevalence or exposure"],
        fill="#fef2f2", fs=11.5)
    s.append(arrow(LX + LW, mid, MX, mid))

    y += GAP
    s.append(arrow(LX + LW // 2, y - GAP, LX + LW // 2, y))
    top = y
    y = put(LX, y, LW, [
        f'Records advancing from the title screen (n = {d["title_adv"]:,})',
        f'{d["n_abs_screened"]:,} screened at abstract and {d["n_st5_new"]} more at the stage-5 '
        f'full-text gate (records with no retrievable abstract); {d["n_st5_reread"]} of the '
        f'abstract-screened records were re-read at that gate'])
    mid = (top + y) / 2
    ymr = put(MX, top, MW, [
        f'Excluded at the abstract or stage-5 screen (n = {d["spine_exc"]:,})',
        f'{d["spine_exc_abs"]:,} at the abstract screen, {d["st5_excl"]} at the stage-5 screen',
        f'Rated "maybe" and not advanced (n = {d["spine_maybe"]})'],
        fill="#fef2f2", fs=11.5)
    s.append(arrow(LX + LW, mid, MX, mid))
    ymr += 12
    put(MX, ymr, MW, [
        f'No further decision recorded (n = {d["n_no_second_screen"]:,})',
        "title-advanced records with no retrievable abstract that the stage-5 gate did not reach"],
        fill="#fffbeb", fs=11.5)
    s.append(arrow(LX + LW, mid + 8, MX, ymr + 14))

    y += GAP
    s.append(arrow(LX + LW // 2, y - GAP, LX + LW // 2, y))
    y = put(LX, y, LW, [
        f'Scopus records advancing to retrieval (n = {d["scopus_adv"]:,})',
        f'{d["spine_inc"]} of the {d["title_adv"]:,} title-advanced records '
        f'({d["title_adv"]:,} less {d["spine_exc"]:,} excluded, {d["spine_maybe"]} left at '
        f'"maybe" and {d["n_no_second_screen"]} undecided), plus {d["scopus_tagged"]} record '
        f'from the tagged include list that predates the title screen'])

    # ---- the merge --------------------------------------------------------------------------------
    y4 = max(y, yr) + 46
    s.append(arrow(LX + LW // 2, y, LX + LW // 2, y4))
    yjoin = y4 - 24
    for m in mids:                                  # each stream onto the bus
        s.append(line(RX, m, BUS, m))
    s.append(line(BUS, mids[0], BUS, yjoin))
    s.append(line(BUS, yjoin, LX + LW - 60, yjoin))
    s.append(arrow(LX + LW - 60, yjoin, LX + LW - 60, y4 - 2))

    top = y4
    y = put(LX, y4, LW, [
        f'Reports sought for retrieval (n = {d["assessed"]:,})',
        " · ".join(f"{lab} {n}" for lab, n in d["streams"]) + f' = {d["assessed"]:,}'])
    mid = (top + y) / 2
    put(MX, top, MW, [f'Not retrieved (n = {d["not_retrieved"]:,})',
                      f'{d["nr_main"]} from the main streams, {d["nr_arm"]} from the September '
                      f'behavioural query'], fill="#fffbeb", fs=11.5)
    s.append(arrow(LX + LW, mid, MX, mid))

    y += GAP
    s.append(arrow(LX + LW // 2, y - GAP, LX + LW // 2, y))
    top = y
    y = put(LX, y, LW, [f'Reports assessed for eligibility '
                        f'(n = {d["assessed"]-d["not_retrieved"]:,})'])
    rl = [f'Reports excluded (n = {d["excl_total"]:,})']
    rl += [f"· {lab} (n = {n})" for lab, n in d["excl_reasons"] if n]
    ybot = put(MX, top, RX + RW - MX, rl, fill="#fef2f2", fs=11.5)
    s.append(arrow(LX + LW, top + 14, MX, top + 14))

    y = max(y, ybot) - 42 + 20
    s.append(arrow(LX + LW // 2, top + 42, LX + LW // 2, y))
    y = put(LX, y, LW,
            [f'Included, but contributed no codeable estimate (n = {d["no_data"]:,})'],
            fill="#fffbeb")

    y += GAP
    s.append(arrow(LX + LW // 2, y - GAP, LX + LW // 2, y))
    y = put(LX, y, LW, [f'Studies included in the review (n = {d["included"]:,})',
                        f'contributing {d["n_est"]:,} estimates'],
            fill="#ecfdf5", stroke="#047857")

    # ---- band labels and notes --------------------------------------------------------------------
    for ly, lab in [(y0 + 90, "Identification"), (y4 - 120, "Screening"), (y - 40, "Included")]:
        s.append(f'<text x="26" y="{ly:.0f}" font-size="11" font-weight="700" fill="#94a3b8" '
                 f'transform="rotate(-90 26 {ly:.0f})">{lab}</text>')

    ny = y + 30
    notes = [
        f'Reports sought for retrieval = {d["included"]} included + {d["not_retrieved"]} not '
        f'retrieved + {d["no_data"]} without a codeable estimate + {d["excl_total"]} excluded '
        f'= {d["assessed"]:,}.',
        f'Note. The citation-snowballing and corpus-repair arms ran their own full-text screens, '
        f'and their per-record outcomes are held in the arm ledgers rather than in the record '
        f'ledger reconciled here; only their retained studies carry a terminal state. '
        f'{sn["advancing"]-sn["ledgered"]} snowballed records and {rp["fulltext"]-rp["ledgered"]} '
        f'repaired records therefore sit outside every total below the retrieval box. The repair’s '
        f'{rp["eligible"]} eligible papers and the {d["no_data"]} reports without a codeable '
        f'estimate are different quantities and do not subtract: the repair’s non-pooled papers '
        f'yielded estimates that the author’s class-level rulings sent to the appendix pool.',
        f'The abstract-stage screen file records {d["abs_excl"]:,} exclusions and the stage-5 file '
        f'{d["st5_excl"]}. {d["abs_excl"]-d["spine_exc_abs"]} of the {d["abs_excl"]:,} are records '
        f'the title screen did not advance, so the spine\u2019s resolved exclusion count is '
        f'{d["spine_exc"]:,} rather than {d["abs_excl"]+d["st5_excl"]:,}.']
    for txt in notes:
        for ln in wrap(txt, W - 320, 10.5, indent=""):
            s.append(f'<text x="36" y="{ny:.0f}" font-size="10.5" fill="#64748b">{esc(ln)}</text>')
            ny += 14
        ny += 4

    # ASSERTION 4: nothing drawn may overrun its box. The wrap above sizes every box to its text,
    # so a failure here means a single unbreakable token is wider than the column.
    worst = max(OVERFLOW, key=lambda t: t[1])
    assert worst[1] <= 0, f"PRISMA: line overflows its box by {worst[1]:.0f}px: {worst[0]!r}"

    # ASSERTION 5: the canvas is measured from what was actually drawn, and the white ground is
    # painted to that same height. A literal canvas height cut the last box in half; painting the
    # ground at the old literal then left a transparent strip that renders as a black band.
    body = "\n".join(s)
    drawn = [float(yy) + float(hh) for yy, hh in
             re.findall(r'<rect[^>]*y="([0-9.]+)"[^>]*height="([0-9.]+)"', body)]
    drawn += [float(yy) + 6 for yy in re.findall(r'<text[^>]*y="([0-9.]+)"', body)]
    drawn += [float(yy) for yy in re.findall(r'<line[^>]*y2="([0-9.]+)"', body)]
    H = int(max(drawn)) + 24
    assert max(drawn) <= H, f"PRISMA content reaches y={max(drawn):.0f} on a {H}-high canvas"

    head = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'font-family="Helvetica,Arial,sans-serif">',
            '<defs><marker id="a" markerWidth="9" markerHeight="9" refX="7" refY="3" '
            'orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#334155"/></marker></defs>',
            f'<rect width="{W}" height="{H}" fill="white"/>',
            '<text x="36" y="32" font-size="17" font-weight="700" fill="#0f172a">'
            'PRISMA 2020 flow: prevalence, exposure and concentration of misinformation</text>',
            '<text x="36" y="52" font-size="11.5" fill="#64748b">Counts from the released '
            'dataset; primary searches run 20 to 24 June 2026, top-up searches September 2026'
            '</text>']

    out = P("docs/prisma_flow.svg")
    open(out, "w", encoding="utf-8").write("\n".join(head + [body, "</svg>"]))
    print(f"reconciliation OK: {d['included']} + {d['not_retrieved']} + {d['no_data']} + "
          f"{d['excl_total']} = {d['assessed']}")
    print("streams OK: " + " + ".join(str(n) for _, n in d["streams"]) + f" = {d['assessed']}")
    print(f"included {d['included']} studies / {d['n_est']} estimates (frozen v{d['ver']})")
    print(f"wrote {os.path.relpath(out, ROOT)} ({W}x{H})")
    png = out.replace(".svg", ".png")
    for cmd in (["rsvg-convert", out, "-o", png], ["cairosvg", out, "-o", png]):
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"wrote {os.path.relpath(png, ROOT)}")
            break
        except Exception:
            continue


if __name__ == "__main__":
    main()
