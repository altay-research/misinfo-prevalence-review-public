#!/usr/bin/env python3
"""PRISMA 2020 flow diagram (new review; databases and other methods), drawn from the record ledger.

Every number comes from data/synth/prisma_counts.json, which scripts/validate_prisma.py writes from
the record-level ledger (one row per identified record, data/synth/prisma_terminal_states.csv).
Nothing is typed here. Before writing, the script re-asserts every box identity it draws, per column
and for the whole flow, so the figure cannot show a box that does not close.

Layout, following the PRISMA 2020 template for new reviews that searched databases and other sources:
  Identification  records identified per source (with search dates); duplicates removed
  Screening       records screened -> excluded; excluded records re-screened later and recovered
                  (September corrected-criteria re-screen, November third-model re-screen) re-enter
                  the flow at "reports sought", so no record is counted twice and none sits outside
                  the totals; records awaiting a decision have their own box
                  reports sought -> not retrieved; reports assessed -> excluded with reasons
  Included        studies included in the review, and the reports of those studies

Inputs : data/synth/prisma_counts.json (run scripts/validate_prisma.py first)
Outputs: docs/prisma_flow.svg and docs/prisma_flow.png (rsvg-convert or cairosvg, if available)

Run: python3 scripts/validate_prisma.py && python3 scripts/make_prisma.py
"""

import json
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)

# --- text metrics -----------------------------------------------------------------------------
# Helvetica advance widths (AFM, per 1000 em). Box heights and line breaks are computed from these,
# and the final assertion refuses to write a figure with a line wider than its box.
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

OVERFLOW = []
PAD, TOP, BOT = 10, 18, 10
INK, LINE = "#0f172a", "#334155"


def tw(s, fs, bold=False):
    return sum(_W.get(c, 600) for c in s) / 1000.0 * fs * (1.06 if bold else 1.0)


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def wrap(text, maxw, fs, bold=False, indent="  "):
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


class Canvas:
    def __init__(self):
        self.s = []

    def box(self, x, y, w, lines, fill="#ffffff", stroke=LINE, fs=12, bold0=True, lh=None):
        """Draw a box sized to its wrapped text; returns its bottom y."""
        lh = lh or round(fs * 1.32)
        maxw = w - 2 * PAD
        flat = []
        for i, ln in enumerate(lines):
            b = bold0 and i == 0
            flat += [(sub, b) for sub in wrap(ln, maxw, fs, b)]
        h = TOP + lh * (len(flat) - 1) + BOT
        self.s.append(f'<rect x="{x}" y="{y:.0f}" width="{w}" height="{h:.0f}" rx="4" fill="{fill}" stroke="{stroke}"/>')
        ty = y + TOP
        for txt, b in flat:
            OVERFLOW.append((txt, tw(txt, fs, b) - maxw))
            bb = ' font-weight="700"' if b else ""
            self.s.append(f'<text x="{x + PAD}" y="{ty:.0f}" font-size="{fs}"{bb} fill="{INK}">{esc(txt)}</text>')
            ty += lh
        return y + h

    def arrow(self, x1, y1, x2, y2):
        self.s.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{LINE}" '
                      f'stroke-width="1.3" marker-end="url(#a)"/>')

    def line(self, x1, y1, x2, y2):
        self.s.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{LINE}" stroke-width="1.3"/>')

    def band(self, x, y0, y1, label, fill="#dbeafe"):
        self.s.append(f'<rect x="{x}" y="{y0:.0f}" width="22" height="{y1 - y0:.0f}" rx="4" fill="{fill}" stroke="#93c5fd"/>')
        cy = (y0 + y1) / 2
        self.s.append(f'<text x="{x + 15}" y="{cy:.0f}" font-size="12" font-weight="700" fill="{INK}" '
                      f'text-anchor="middle" transform="rotate(-90 {x + 15} {cy:.0f})">{label}</text>')


def n(x):
    return f"{x:,}"


def date(d):
    if not d:
        return ""
    y, m, dd = d.split("-")
    return f"{int(dd)} {['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][int(m) - 1]} {y}"


def reassert(b, name):
    """The identities validate_prisma.py checked, re-asserted on exactly the numbers drawn."""
    assert b["identified"] == b["dup_at_search"] + b["dup_rebuild"] + b["screened"] + b["awaiting_screening"], name
    assert b["screened"] == b["first_pass_excluded"] + b["advanced"], name
    assert b["excluded_screening"] == b["first_pass_excluded"] - b["recovered"], name
    assert b["sought"] == b["advanced"] + b["recovered"], name
    assert b["sought"] == b["not_retrieved"] + b["awaiting_ft"] + b["assessed"], name
    assert b["assessed"] == b["excluded_ft"] + b["included"] + b["other_reports"], name
    assert sum(b["excluded_ft_by_reason"].values()) == b["excluded_ft"], name
    assert sum(b["recovered_by"].values()) == b["recovered"], name
    assert sum(b["excluded_screening_by_stage"].values()) == b["excluded_screening"], name


STAGE_LABELS = [("title", "at the title screen"), ("abstract", "at the abstract screen"),
                ("title_abstract", "at a single title-and-abstract screen"),
                ("adjudication", "at adjudication of screener disagreements"),
                ("second_reader", "by the second-reader re-screen of abstract includes"),
                ("november_undecided_screen", "at the November 2026 screen of undecided records")]
SHORT_ROUTE = {"september_repair": "September 2026 re-screen under corrected criteria",
               "november_rescreen": "November 2026 re-screen by a third model family",
               "november_rules_pass": "November 2026 full-text re-read",
               "other_check": "other checks"}


def main():
    d = json.load(open(P("data/synth/prisma_counts.json"), encoding="utf-8"))
    S, Cc, T = d["streams"], d["columns"], d["total"]
    for name, b in list(Cc.items()) + [("total", T)]:
        reassert(b, name)
    assert Cc["db"]["included"] + Cc["other"]["included"] == T["included"] == d["studies"]
    labels = d["reason_labels"]

    W = 1500
    LX, LW = 52, 330          # databases column: main boxes
    LS, LSW = 400, 330        # databases column: side boxes
    RX, RW = 770, 320         # other methods: main boxes
    RS, RSW = 1108, 352       # other methods: side boxes
    G = 30
    cv = Canvas()
    db, ot = Cc["db"], Cc["other"]

    # ---- column headers -------------------------------------------------------------------------
    y = 70
    cv.s.append(f'<rect x="{LX}" y="{y}" width="{LS + LSW - LX}" height="30" rx="4" fill="#fde68a" stroke="#d97706"/>')
    cv.s.append(f'<text x="{(LX + LS + LSW) / 2:.0f}" y="{y + 20}" font-size="13" font-weight="700" fill="{INK}" '
                f'text-anchor="middle">Identification of studies via databases</text>')
    cv.s.append(f'<rect x="{RX}" y="{y}" width="{RS + RSW - RX}" height="30" rx="4" fill="#e5e7eb" stroke="#6b7280"/>')
    cv.s.append(f'<text x="{(RX + RS + RSW) / 2:.0f}" y="{y + 20}" font-size="13" font-weight="700" fill="{INK}" '
                f'text-anchor="middle">Identification of studies via other methods</text>')
    y0 = y + 30 + 16

    # ---- identification -------------------------------------------------------------------------
    dbs = [k for k, b in S.items() if b["column"] == "db"]
    ots = [k for k, b in S.items() if b["column"] == "other"]
    a = cv.box(LX, y0, LW, [f"Records identified from databases (n = {n(db['identified'])})"]
               + [f"{S[k]['label']}, {date(S[k]['date'])}: {n(S[k]['identified'])}" for k in dbs], fs=11.5)
    cv.box(LS, y0, LSW, [f"Records removed before screening (n = {n(db['dup_at_search'] + db['dup_rebuild'])})",
                         f"Duplicates removed when the searches were run: {n(db['dup_at_search'])}",
                         f"Duplicates found when the record ledger was rebuilt (same id, same DOI or same full "
                         f"title in two sources; the copy that went furthest is kept): {n(db['dup_rebuild'])}"],
           fs=11.5)
    b_ = cv.box(RX, y0, RW, [f"Records identified from other methods (n = {n(ot['identified'])})"]
                + [f"{S[k]['label']}{', ' + date(S[k]['date']) if S[k]['date'] else ''}: {n(S[k]['identified'])}"
                   for k in ots], fs=11.5)
    cv.box(RS, y0, RSW, [f"Records removed before screening (n = {n(ot['dup_at_search'] + ot['dup_rebuild'])})",
                         f"Already held when the source was searched: {n(ot['dup_at_search'])}",
                         f"Duplicates of records from another source, found when the ledger was rebuilt: "
                         f"{n(ot['dup_rebuild'])}"], fs=11.5)
    for x, w, sx in ((LX, LW, LS), (RX, RW, RS)):
        cv.arrow(x + w, y0 + 24, sx, y0 + 24)
    y1 = max(a, b_) + G

    # ---- screening --------------------------------------------------------------------------------
    def screening_row(x, w, sx, sw, b, ytop, yprev):
        cv.arrow(x + w / 2, yprev, x + w / 2, ytop)
        bot = cv.box(x, ytop, w, [f"Records screened (n = {n(b['screened'])})",
                                  "titles and abstracts; records with no abstract were sought in full text"], fs=11.5)
        st = b["excluded_screening_by_stage"]
        lines = [f"Records excluded (n = {n(b['excluded_screening'])})"]
        lines += [f"{lab}: {n(st[k])}" for k, lab in STAGE_LABELS if st.get(k)]
        sb = cv.box(sx, ytop, sw, lines, fill="#fef2f2", fs=11)
        cv.arrow(x + w, ytop + 22, sx, ytop + 22)
        if b["awaiting_screening"]:
            sb2 = cv.box(sx, sb + 10, sw, [f"Awaiting a screening decision (n = {n(b['awaiting_screening'])})",
                                           "never screened in June; being screened in November 2026"],
                         fill="#fffbeb", fs=11)
            cv.line(x + w, bot - 14, x + w + 9, bot - 14)
            cv.line(x + w + 9, bot - 14, x + w + 9, sb + 26)
            cv.arrow(x + w + 9, sb + 26, sx, sb + 26)
            sb = sb2
        return bot, sb

    yl, ys_l = screening_row(LX, LW, LS, LSW, db, y1, a)
    yr, ys_r = screening_row(RX, RW, RS, RSW, ot, y1, b_)

    # recovered box: excluded records re-screened later and sent to full text
    def recovered_box(sx, sw, b, ytop):
        rb = b["recovered_by"]
        lines = [f"Excluded records recovered by a later re-screen (n = {n(b['recovered'])})",
                 f"of the {n(b['first_pass_excluded'])} records the first screen excluded or missed"]
        lines += [f"{SHORT_ROUTE[k]}: {n(v)}" for k, v in rb.items() if v]
        return cv.box(sx, ytop, sw, lines, fill="#ecfeff", stroke="#0e7490", fs=11)

    yrec_l = ys_l + 14
    yrec_r = ys_r + 14
    rl = recovered_box(LS, LSW, db, yrec_l)
    rr = recovered_box(RS, RSW, ot, yrec_r)

    y2 = max(yl, yr, rl, rr) + G
    # ---- reports sought ---------------------------------------------------------------------------
    def sought_row(x, w, sx, sw, b, ytop, yprev, rec_top, rec_bot):
        cv.arrow(x + w / 2, yprev, x + w / 2, ytop)
        bot = cv.box(x, ytop, w, [f"Reports sought for retrieval (n = {n(b['sought'])})",
                                  f"{n(b['advanced'])} advanced at screening + {n(b['recovered'])} recovered"],
                     fs=11.5)
        # recovered -> sought
        mid = (rec_top + rec_bot) / 2
        cv.line(sx, mid, sx - 12, mid)
        cv.line(sx - 12, mid, sx - 12, ytop + 14)
        cv.arrow(sx - 12, ytop + 14, x + w, ytop + 14)
        lines = [f"Reports not retrieved (n = {n(b['not_retrieved'])})"]
        sb = cv.box(sx, ytop + 30, sw, lines, fill="#fffbeb", fs=11)
        cv.arrow(x + w, ytop + 38 + 6, sx, ytop + 38 + 6)
        if b["awaiting_ft"]:
            top2 = sb + 8
            sb = cv.box(sx, top2, sw, [f"Awaiting a full-text decision (n = {n(b['awaiting_ft'])})",
                                       "being assessed in November 2026"], fill="#fffbeb", fs=11)
            cv.line(x + w, bot - 8, x + w + 9, bot - 8)
            cv.line(x + w + 9, bot - 8, x + w + 9, top2 + 18)
            cv.arrow(x + w + 9, top2 + 18, sx, top2 + 18)
        return bot, sb

    yl, sl = sought_row(LX, LW, LS, LSW, db, y2, yl, yrec_l, rl)
    yr, sr = sought_row(RX, RW, RS, RSW, ot, y2, yr, yrec_r, rr)

    y3 = max(yl, yr, sl, sr) + G
    # ---- assessed ---------------------------------------------------------------------------------
    def assessed_row(x, w, sx, sw, b, ytop, yprev):
        cv.arrow(x + w / 2, yprev, x + w / 2, ytop)
        bot = cv.box(x, ytop, w, [f"Reports assessed for eligibility (n = {n(b['assessed'])})"], fs=11.5)
        lines = [f"Reports excluded (n = {n(b['excluded_ft'])})"]
        lines += [f"{labels[k]}: {n(v)}" for k, v in b["excluded_ft_by_reason"].items() if v]
        sb = cv.box(sx, ytop, sw, lines, fill="#fef2f2", fs=11)
        cv.arrow(x + w, ytop + 20, sx, ytop + 20)
        return bot, sb

    yl, sl = assessed_row(LX, LW, LS, LSW, db, y3, yl)
    yr, sr = assessed_row(RX, RW, RS, RSW, ot, y3, yr)

    # ---- included ---------------------------------------------------------------------------------
    y4 = max(sl, sr) + G
    IX, IW = 470, 560
    reports = T["included"] + T["other_reports"]
    yi = cv.box(IX, y4, IW, [f"Studies included in the review (n = {n(T['included'])}), contributing "
                             f"{n(d['estimates'])} estimates",
                             f"Reports of included studies (n = {n(reports)}), of which {n(T['other_reports'])} are "
                             f"additional reports (preprint or second copy) of an included study",
                             f"From databases: {n(db['included'])} studies; from other methods: "
                             f"{n(ot['included'])} studies. {d['studies_assessed_on_abstract_only']} studies were "
                             f"assessed on the abstract alone (no full text retrievable)"],
                fill="#ecfdf5", stroke="#047857", fs=12)
    for x, w, yb in ((LX, LW, yl), (RX, RW, yr)):
        cv.line(x + w / 2, yb, x + w / 2, y4 - 14)
        cv.line(x + w / 2, y4 - 14, IX + IW / 2 + (-60 if x == LX else 60), y4 - 14)
        cv.arrow(IX + IW / 2 + (-60 if x == LX else 60), y4 - 14, IX + IW / 2 + (-60 if x == LX else 60), y4)

    # ---- phase bands --------------------------------------------------------------------------------
    cv.band(16, y0, y1 - 8, "Identification")
    cv.band(16, y1, y4 - 20, "Screening")
    cv.band(16, y4, yi, "Included", fill="#dcfce7")

    # ---- note -------------------------------------------------------------------------------------
    note = (f"Each identified record ends in exactly one box. Excluded records recovered by a later re-screen are "
            f"counted once, in the box where they ended. Totals: {n(T['identified'])} records identified = "
            f"{n(T['dup_at_search'] + T['dup_rebuild'])} duplicates + {n(T['excluded_screening'])} excluded at "
            f"screening + {n(T['not_retrieved'])} not retrieved + "
            f"{n(T['excluded_ft'])} excluded at full text + "
            f"{n(reports)} reports of included studies.")
    ny = yi + 26
    for ln in wrap(note, W - 80, 11, indent=""):
        cv.s.append(f'<text x="40" y="{ny:.0f}" font-size="11" fill="#475569">{esc(ln)}</text>')
        ny += 15
    total_check = (T["dup_at_search"] + T["dup_rebuild"] + T["excluded_screening"] + T["awaiting_screening"]
                   + T["not_retrieved"] + T["awaiting_ft"] + T["excluded_ft"] + reports)
    assert total_check == T["identified"], f"terminal boxes sum to {total_check}, identified {T['identified']}"

    worst = max(OVERFLOW, key=lambda t: t[1])
    assert worst[1] <= 0, f"PRISMA: line overflows its box by {worst[1]:.0f}px: {worst[0]!r}"
    body = "\n".join(cv.s)
    drawn = [float(yy) + float(hh) for yy, hh in re.findall(r'<rect[^>]*y="([0-9.]+)"[^>]*height="([0-9.]+)"', body)]
    drawn += [float(yy) + 6 for yy in re.findall(r'<text[^>]*y="([0-9.]+)"', body)]
    H = int(max(drawn)) + 20
    head = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'font-family="Helvetica,Arial,sans-serif">',
            '<defs><marker id="a" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto">'
            f'<path d="M0,0 L7,3 L0,6 Z" fill="{LINE}"/></marker></defs>',
            f'<rect width="{W}" height="{H}" fill="white"/>',
            f'<text x="40" y="36" font-size="17" font-weight="700" fill="{INK}">PRISMA 2020 flow diagram: '
            'prevalence, exposure and concentration of misinformation</text>']
    out = P("docs/prisma_flow.svg")
    open(out, "w", encoding="utf-8").write("\n".join(head + [body, "</svg>"]))
    print(f"identified {n(T['identified'])} = duplicates {n(T['dup_at_search'] + T['dup_rebuild'])} + excluded at "
          f"screening {n(T['excluded_screening'])} + awaiting screening {T['awaiting_screening']} + not retrieved "
          f"{n(T['not_retrieved'])} + awaiting full text {T['awaiting_ft']} + excluded at full text "
          f"{n(T['excluded_ft'])} + reports of included studies {reports}")
    print(f"studies included {T['included']} (databases {db['included']}, other methods {ot['included']}); "
          f"{d['estimates']:,} estimates (freeze v{d['freeze']})")
    print(f"wrote {os.path.relpath(out, ROOT)} ({W}x{H})")
    png = out.replace(".svg", ".png")
    for cmd in (["rsvg-convert", "-z", "1.5", out, "-o", png], ["cairosvg", out, "-o", png]):
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"wrote {os.path.relpath(png, ROOT)}")
            break
        except Exception:
            continue


if __name__ == "__main__":
    main()
