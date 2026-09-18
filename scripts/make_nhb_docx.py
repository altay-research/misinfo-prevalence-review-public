#!/usr/bin/env python3
"""make_nhb_docx.py — render the manuscript in Nature Human Behaviour submission format.

Two documents from the one markdown master:
  docs/nhb_main.docx          — title page, abstract, main text + Methods, NUMBERED references
                                (superscript, order of first appearance), Table 1, Figures 1-5
  docs/nhb_supplementary.docx — Supplementary Notes A-E, Supplementary Tables, Supplementary
                                Figs 1-4 (citations numbered against the main list)

The md master stays author-year (the working format the guards read); numbering happens here
at build time. Every citation instance is converted through an explicit curated map, and the
build FAILS if any author-year pattern survives, so a new citation added to the md without a
map entry cannot slip through silently.

Run: python3 scripts/make_nhb_docx.py
"""
import os
import re
import subprocess
import sys
import tempfile

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "docs/manuscript_draft.md")

MAIN_FIGS = [
    ("Figure 1.", "Platforms studied, by construct. Bars are the share of that construct's studies that cover the platform, against a track showing all of them; study counts are in brackets and the eight most covered platforms are shown per construct. A study counts once in every platform it names, so bars within a panel sum to more than k. Supplementary Note A5 gives the counting rule and the ground-truth and country breakdowns.", "docs/figN_platform_panels.svg"),
    ("Figure 2.", "Topics studied, by construct. Bars are the share of that construct's studies on each topic, with study counts in brackets.", "docs/figP_topic_panels.svg"),
    ("Figure 3.", "Prevalence estimates by construct. Study-level medians with 95% confidence intervals from a study-cluster bootstrap (2,000 resamples).", "docs/fig5_forest_constructs.svg"),
    ("Figure 4.", "What drives the estimate. Study-level median prevalence by measurement type, sampling frame, ground-truth source, construct, and identification level, over the studies in the main analysis set that contribute to the six prevalence constructs. n = studies at that level, and the figure beside each band heading is that band's total. The bands rest on different totals because a study whose value for a moderator is not coded is omitted from that band only.", "docs/fig2_method_drivers.svg"),
    ("Figure 5.", "Concentration of misinformation versus news in general. In each pair the left column is the user population and the right column all of the activity, with the share accounted for by the top 1% of users filled in. Both columns are drawn to scale: the top 1% band is 1% of the height of the people column. Left: the study-level median share of misinformation activity accounted for by the top 1% of users, across the 5 studies reporting exactly that threshold (range 37-80%). Right: the median of 6 comparison estimates of general-news activity, from the 4 panels that report both quantities (range 30-43%). The two medians come from different sets of studies.", "docs/figK_concentration_flow.svg"),
    ("Figure 6.", "PRISMA flow diagram. Records identified, screened, retrieved and included, with the corpus repair shown as its own identification stream.", "docs/prisma_flow.svg"),
]
SUPP_FIGS = [
    ("Supplementary Fig. 1.", "Ground truth by construct: who decided what counted as misinformation. Same form as Figure 1.", "docs/figP_ground_truth_panels.svg"),
    ("Supplementary Fig. 2.", "Countries studied, by construct. Same form as Figure 1; a study counts once in every country label it carries.", "docs/figP_country_norm_panels.svg"),
]

# ---------------------------------------------------------------- citation map
# in-text form (exact string as it appears inside a citation group) -> reference-list prefix
CITE_MAP = {
    "Allcott & Gentzkow 2017": "Allcott, H., & Gentzkow, M. (2017)",
    "Shao et al. 2018": "Shao, C., Hui, P. M.",
    "Allen et al. 2020": "Allen, J., Howland, B.",
    "Allen, Watts & Rand 2024": "Allen, J., Watts, D. J.",
    "Altay 2026": "Altay, S. (2026)",
    "Aslett et al. 2024a": "Aslett, K., Guess",
    "Aslett et al. 2024b": "Aslett, K., Sanderson",
    "Godel et al. 2021": "Godel, W.",
    "Altay & Acerbi 2024": "Altay, S., & Acerbi, A. (2024)",
    "Altay, Berriche & Acerbi 2023": "Altay, S., Berriche, M., & Acerbi, A. (2023)",
    "Altay, Berriche, Heuer et al. 2023": "Altay, S., Berriche, M., Heuer, H.",
    "Altay & Mercier 2026": "Altay, S., & Mercier, H. (2026)",
    "Baribi-Bartov, Swire-Thompson & Grinberg 2024": "Baribi-Bartov, S.",
    "Barendregt et al. 2013": "Barendregt, J. J.",
    "Begg & Mazumdar 1994": "Begg, C. B.",
    "Bergeron-Boutin, Nyhan et al. 2026": "Bergeron-Boutin, O.",
    "Berriche & Altay 2020": "Berriche, M., & Altay, S. (2020)",
    "Boulianne & Humprecht 2023": "Boulianne, S.",
    "Budak et al. 2024": "Budak, C.",
    "Carlson 2020": "Carlson, M. (2020)",
    "Cordonier & Brest 2021": "Cordonier, L.",
    "Ecker et al. 2025": "Ecker, U. K. H.",
    "Grinberg et al. 2019": "Grinberg, N.",
    "Neely et al. 2022": "Neely, S. R.",
    "Oswald & Munzert 2026": "Oswald, L.",
    "Pierri, Artoni & Ceri 2020": "Pierri, F., Artoni",
    "Pierri et al. 2023": "Pierri, F., DeVerna",
    "Guess, Nagler & Tucker 2019": "Guess, A., Nagler, J.",
    "Guess, Nyhan & Reifler 2020": "Guess, A., Nyhan, B.",
    "Moore, Dahlke & Hancock 2023": "Moore, R. C., Dahlke",
    "Parry et al. 2021": "Parry, D. A., Davidson",
    "Kreps et al. 2022": "Kreps, S., George",
    "Mourão & Robertson 2019": "Mourão, R. R., & Robertson",
    "Wirtschafter et al. 2024": "Wirtschafter, V., Batista",
    "Tai, Lin & Desmarais 2026": "Tai, Y. C., Lin",
    "Pierri et al. 2023": "Pierri, F., DeVerna",
    "Guyatt et al. 2008": "Guyatt, G. H.",
    "Hameleers 2025": "Hameleers, M. (2025)",
    "Hoes et al. 2025": "Hoes, E.",
    "Hoy et al. 2012": "Hoy, D.",
    "Kim et al. 2023": "Kim, J., Bak",
    "Matthes et al. 2023": "Matthes, J.",
    "Mercier 2020": "Mercier, H. (2020)",
    "Munn et al. 2015": "Munn, Z.",
    "Nickl et al. 2025": "Nickl, P. L.",
    "Page et al. 2021": "Page, M. J.",
    "Pennycook & Rand 2026": "Pennycook, G.",
    "Rogers 2020": "Rogers, R. (2020)",
    "Stecula 2025": "Stecula, D.",
    "Suarez-Lledo & Alvarez-Galvez 2021": "Suarez-Lledo, V.",
    "Tay, Hurlstone et al. 2024": "Tay, L. Q., Hurlstone",
    "Tay, Lewandowsky et al. 2024": "Tay, L. Q., Lewandowsky",
    "Van Doorn 2023": "Van Doorn, M.",
    "van der Meer & Hameleers 2025": "van der Meer, T. G. L. A.",
    "Viechtbauer 2010": "Viechtbauer, W.",
    "Vincent et al. 2025": "Vincent, E. M.",
    "Wardle & Derakhshan 2017": "Wardle, C.",
    "Watts, Rothschild & Mobius 2021": "Watts, D. J.",
    "Williams 2026": "Williams, D. (2026)",
}
SUP = "⁙SUP⁙"   # internal marker: ⁘SUP⁘12,13⁘END⁘
END = "⁙END⁙"

YEAR_GROUP = re.compile(r"\(([^()]*?(?:19|20)\d\d[a-z]?(?:[^()]*?)?)\)")
NARRATIVE = re.compile(r"\b(Hameleers|Hoy et al\.)\s+\((\d{4})\)")


def load():
    s = open(SRC, encoding="utf-8").read()
    refs_start = s.index("## References")
    # Note A was removed on 2026-09-18 (Sacha). The remaining notes keep their letters, B to F,
    # rather than shifting up, because renaming them would move every cross-reference in the paper.
    supp_start = s.index("## Supplementary Note A")
    refs_end = supp_start
    main = s[:refs_start]
    refs_block = s[refs_start:refs_end]
    supp = s[supp_start:]
    entries = [ln.strip() for ln in refs_block.split("\n")
               if ln.strip() and not ln.startswith("#") and not ln.startswith("---")]
    return main, entries, supp


def build_numbering(main, supp, entries):
    """assign numbers by first appearance in main-then-supp; return (num_for_intext, ordered_entries)."""
    def entry_for(intext):
        pref = CITE_MAP[intext]
        cands = [e for e in entries if e.startswith(pref)]
        assert len(cands) == 1, f"reference match not unique for {intext!r}: {len(cands)}"
        return cands[0]

    order, num = [], {}
    def note(intext):
        e = entry_for(intext)
        if e not in order:
            order.append(e)
        return order.index(e) + 1

    # scan in reading order: both literal in-text forms and narrative "Name (YYYY)" forms,
    # merged by position so numbering follows first appearance
    text = main + supp
    hits = []
    for m in re.finditer("|".join(re.escape(k) for k in sorted(CITE_MAP, key=len, reverse=True)), text):
        hits.append((m.start(), m.group(0)))
    for m in NARRATIVE.finditer(text):
        k = f"{m.group(1).rstrip('.')} {m.group(2)}" if not m.group(1).endswith("al.") else f"{m.group(1)} {m.group(2)}"
        assert k in CITE_MAP, f"narrative form unmapped: {k}"
        hits.append((m.start(), k))
    for _, k in sorted(hits):
        num.setdefault(k, note(k))
    return num, order


def convert(text, num):
    """replace citation groups and narrative citations with superscript markers."""
    keys = sorted(CITE_MAP, key=len, reverse=True)
    # Announce key containment rather than let it pass silently: the span-claiming below handles it,
    # but a new key that sits inside another is worth a human look, since it means two references
    # share a surname and year and the shorter one can only ever be matched outside the longer.
    nested = [(a, b) for a in keys for b in keys if a != b and b in a]
    for a, b in nested:
        print(f"  note: citation key {b!r} is contained in {a!r}; longest match wins")

    def conv_group(m):
        inner = m.group(1)
        # Find the mapped citations in this parenthetical, claiming character spans so that a key
        # contained inside a longer one is not counted twice. "(van der Meer & Hameleers 2025)"
        # contains "Hameleers 2025", and without this it rendered as two references, "1,18"
        # (Sacha spotted it in the built PDF, 2026-09-17). keys is sorted longest-first, so the
        # longest match claims its span before any substring of it is tried.
        found, claimed = [], []
        for k in keys:
            start = 0
            while True:
                i = inner.find(k, start)
                if i < 0:
                    break
                if not any(a < i + len(k) and i < b for a, b in claimed):
                    found.append((i, k))
                    claimed.append((i, i + len(k)))
                    break
                start = i + 1
        if not found:
            return m.group(0)   # not a citation parenthetical (e.g. a date or stat)
        found.sort()
        nums = sorted({num[k] for _, k in found})
        rest = inner
        for _, k in found:
            rest = rest.replace(k, "")
        rest = re.sub(r"^(e\.g\.,?|see also|;|,|\s)+|(;|,|\s)+$", "", rest.strip())
        rest = re.sub(r"\s*;\s*$", "", rest)
        # An UNMAPPED citation sharing a parenthetical with mapped ones used to survive here as
        # plain text and render beside the numbers: "(Allcott & Gentzkow 201722,28)", which is what
        # Sacha read in the built file on 2026-09-18. The whole-parenthetical check below cannot
        # see it, because by then the superscript sits between the year and the closing bracket.
        # This is the only place the leftover is still visible, so it fails here.
        # A bare year fragment is an unmapped citation too: "(Aslett et al. 2024a, 2024b; Godel et
        # al. 2021)" left ", 2024b;" behind and shipped as "(2024b52,53)", with Aslett 2024b in the
        # reference list and cited nowhere. The name-plus-year pattern below cannot see that form.
        stray = (re.search(r"[A-Z][A-Za-z.\u2019' ]+ (?:19|20)\d\d[a-z]?", rest)
                 or re.search(r"\b(?:19|20)\d\d[a-z]?\b", rest))
        assert not stray, (
            f"unmapped citation {stray.group(0)!r} inside {m.group(0)[:90]!r} — add it to CITE_MAP "
            "and to the reference list")
        sup = SUP + ",".join(str(n) for n in nums) + END
        if rest:
            return f"({rest}{sup})"
        return sup

    def conv_narr(m):
        name = m.group(0)
        for k in keys:
            surname = k.rsplit(" ", 1)[0]
            if name.startswith(surname.split(" (")[0]) and m.group(2) in k:
                return name.split(" (")[0] + SUP + str(num[k]) + END
        raise AssertionError(f"narrative citation unmapped: {name}")

    text = NARRATIVE.sub(conv_narr, text)
    text = YEAR_GROUP.sub(conv_group, text)
    # Nature style: no space before the superscript, and the number sits after punctuation
    text = re.sub(r" +(" + SUP + r"[0-9,]+" + END + r")", r"\1", text)
    text = re.sub(r"(" + SUP + r"[0-9,]+" + END + r")([.,;:])", r"\2\1", text)
    # nothing author-year may survive outside methods dates
    leftovers = [m.group(0) for m in re.finditer(r"\([A-Z][a-z]+[^()]{0,60}(?:19|20)\d\d\)", text)]
    assert not leftovers, f"unconverted citations: {leftovers[:5]}"
    return text


# The single-asterisk branch is markdown italics, but Supplementary Note C prints Boolean queries
# whose truncation operators are also asterisks, so `consume* ... quantif*` was being read as one
# italic span and FOUR wildcards were silently deleted from the published query. A reviewer
# re-running the printed string would get a different record set, which is the one thing this note
# exists to prevent. Italics are skipped inside a query line; the query is the only place in the
# manuscript where a bare asterisk is content rather than markup.
TOKEN = re.compile(r"(\*\*.+?\*\*|\*[^*\n]+?\*|`[^`\n]+?`|" + SUP + r"[0-9,]+" + END + r")")
TOKEN_NO_ITALIC = re.compile(r"(\*\*.+?\*\*|`[^`\n]+?`|" + SUP + r"[0-9,]+" + END + r")")


def _is_query_line(text):
    return "TITLE-ABS-KEY" in text or "title_and_abstract.search" in text or "title.search" in text


def add_runs(par, text):
    tokeniser = TOKEN_NO_ITALIC if _is_query_line(text) else TOKEN
    for tok in tokeniser.split(text):
        if not tok:
            continue
        if tok.startswith(SUP):
            r = par.add_run(tok[len(SUP):-len(END)])
            r.font.superscript = True
        elif tok.startswith("**") and tok.endswith("**"):
            par.add_run(tok[2:-2]).bold = True
        elif tok.startswith("*") and tok.endswith("*") and len(tok) > 2:
            par.add_run(tok[1:-1]).italic = True
        elif tok.startswith("`") and tok.endswith("`"):
            par.add_run(tok[1:-1])
        else:
            par.add_run(tok)


def set_apa_borders(table):
    tbl = table._tbl
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "bottom", "insideH"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "6" if edge != "insideH" else "2")
        el.set(qn("w:color"), "000000")
        borders.append(el)
    for edge in ("left", "right", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "none")
        borders.append(el)
    tbl.tblPr.append(borders)


def add_table(doc, block):
    rows = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in block]
    rows = [r for r in rows if not all(set(c) <= set(":- ") for c in r)]
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    for i, row in enumerate(rows):
        for j, cell in enumerate(row):
            par = t.cell(i, j).paragraphs[0]
            add_runs(par, cell)
            for r in par.runs:
                r.font.size = Pt(10)
                if i == 0:
                    r.bold = True
    set_apa_borders(t)


def add_figure(doc, label, caption, svg_rel):
    svg = os.path.join(ROOT, svg_rel)
    if not os.path.exists(svg):
        return
    png = os.path.join(tempfile.gettempdir(), os.path.basename(svg) + ".nhb.png")
    subprocess.run(["rsvg-convert", "-w", "1800", svg, "-o", png], check=True)
    doc.add_picture(png, width=Inches(6))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap = doc.add_paragraph()
    r = cap.add_run(label + " ")
    r.bold = True
    r.font.size = Pt(10)
    r2 = cap.add_run(caption)
    r2.font.size = Pt(10)


def render(text, dst, figs, fig_marker, title_page=False, ref_list=None):
    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = "Times New Roman"
    st.font.size = Pt(11)

    if title_page:
        t = doc.add_paragraph()
        r = t.add_run("Rare on screens but on everyone's mind: a systematic review of misinformation prevalence, exposure, and concentration")
        r.bold = True
        r.font.size = Pt(15)
        # Cut on 2026-09-18 when this was a journal submission, where the portal collects
        # authorship; restored the same day for the PREPRINT, which is posted publicly and must
        # carry its author (Sacha, 2026-09-18: "yes add back author, me").
        for line in ("", "Sacha Altay",
                     "Department of Political Science, University of Zurich, Zurich, Switzerland",
                     "Correspondence: sachayesilaltay@gmail.com", ""):
            doc.add_paragraph(line)

    lines = text.split("\n")
    i, para_buf = 0, []

    def flush():
        nonlocal para_buf
        if para_buf:
            add_runs(doc.add_paragraph(), " ".join(para_buf))
            para_buf = []

    inserted = set()

    def maybe_figure(t):
        for n, (label, caption, svg) in enumerate(figs, 1):
            if n not in inserted and f"{fig_marker}{n}" in t:
                inserted.add(n)
                add_figure(doc, label, caption, svg)

    while i < len(lines):
        ln = lines[i]
        if ln.lstrip().startswith("<!--"):
            while i < len(lines) and "-->" not in lines[i]:
                i += 1
            i += 1
            continue
        if ln.startswith("|"):
            flush()
            block = []
            while i < len(lines) and lines[i].startswith("|"):
                block.append(lines[i])
                i += 1
            add_table(doc, block)
            continue
        if ln.startswith("#"):
            flush()
            level = len(ln) - len(ln.lstrip("#"))
            head = ln.lstrip("# ")
            if head == "Rare on screens but on everyone's mind: a systematic review of misinformation prevalence, exposure, and concentration":
                i += 1
                continue   # title lives on the title page
            add_runs(doc.add_heading("", level=min(level, 3)), head)
        elif ln.strip() in ("---", ""):
            flush()
        elif re.match(r"^\d+\.\s|^- ", ln):
            flush()
            style = "List Number" if re.match(r"^\d+\.", ln) else "List Bullet"
            add_runs(doc.add_paragraph(style=style), re.sub(r"^(\d+\.|-)\s+", "", ln))
        else:
            para_buf.append(ln.strip())
            if para_buf and (i + 1 >= len(lines) or lines[i + 1].strip() in ("", "---")):
                joined = " ".join(para_buf)
                flush()
                maybe_figure(joined)
        i += 1
    flush()

    if ref_list:
        add_runs(doc.add_heading("", level=2), "References")
        for n, entry in enumerate(ref_list, 1):
            p = doc.add_paragraph()
            add_runs(p, f"{n}. {entry}")
            for r in p.runs:
                r.font.size = Pt(10)

    for n, (label, caption, svg) in enumerate(figs, 1):
        if n not in inserted:
            add_figure(doc, label, caption, svg)

    doc.save(dst)
    print(f"wrote {dst}")



# ---------------------------------------------------------------- NHB structure
# Nature-format articles carry no section numbers and no Introduction heading, and the main text
# refers to sections by name ("Methods", or a quoted subsection title). The master keeps its numbers
# because the checker and every internal document cite them, so the change is made here, at build
# time: headings lose their numbers, the Introduction heading is dropped, and every "§2.6" /
# "section 2.2" / "Sections 2.3 to 2.8" becomes the quoted title of the section it points at, with
# "Methods" or "Results" added where the reader needs the part. Approved by Sacha, 2026-09-07.
_HEAD = re.compile(r"^(#{2,3}) (\d+(?:\.\d+)?)\.? (.+?)\s*$", re.M)

def section_titles(text):
    return {m.group(2): m.group(3).strip() for m in _HEAD.finditer(text)}

def _name(num, titles, with_part=True):
    """A cross-reference as Sacha wants it read: the section's own name, nothing else.

    This used to render "(Results, 'Who is exposed: demographic subgroups')". He struck it twice in
    the 2026-09-17 round — "remove any such parentheses, hate tehse" and "we never do (Results, xxx)"
    — so the part prefix is gone and the name carries the reference on its own.
    """
    if "." not in num:
        return titles.get(num, num)
    return "'" + titles.get(num, num) + "'"

def denumber(text, titles):
    # "Sections 2.3 to 2.8" -> "the sections from 'A' to 'B'"
    text = re.sub(r"\b[Ss]ections (\d+\.\d+) to (\d+\.\d+)",
                  lambda m: f"the sections from {_name(m.group(1), titles, False)} to {_name(m.group(2), titles, False)}", text)
    # "(§4.8)" and "(§4.4, §4.8)" style groups, and bare in-sentence "§4.8" / "section 2.2"
    text = re.sub(r"§(\d+(?:\.\d+)?)", lambda m: _name(m.group(1), titles), text)
    text = re.sub(r"\b[Ss]ection (\d+\.\d+)", lambda m: _name(m.group(1), titles), text)
    # headings: drop the number. The Introduction heading used to be dropped too, on the Nature
    # convention that an Article runs straight from the abstract into the introduction without one.
    # Sacha put it back by hand in the 2026-09-17 round, so it renders (his edit, his call).
    out = []
    for ln in text.split("\n"):
        m = _HEAD.match(ln)
        if m:
            ln = f"{m.group(1)} {m.group(3).strip()}"
        out.append(ln)
    return "\n".join(out)

def main():
    main_md, entries, supp_md = load()
    num, ordered = build_numbering(main_md, supp_md, entries)
    # strip the old References heading from main (rebuilt numbered at the end)
    titles = section_titles(main_md)
    # the trailing "Figures and tables" index is manuscript scaffolding (captions live in the FIGS lists)
    supp_md = supp_md.split("\n## Figures and tables")[0]
    main_conv = denumber(convert(main_md, num), titles)
    supp_conv = denumber(convert(supp_md, num), titles)
    supp_conv = ("# Supplementary Information\n\nRare on screens but on everyone's mind: a systematic "
                 "review of misinformation prevalence, exposure, and concentration.\n\n"
                 "Reference numbers follow the main-text reference list.\n\n" + supp_conv)
    render(main_conv, os.path.join(ROOT, "docs/nhb_main.docx"), MAIN_FIGS, "Figure ",
           title_page=True, ref_list=ordered)
    render(supp_conv, os.path.join(ROOT, "docs/nhb_supplementary.docx"), SUPP_FIGS,
           "Supplementary Fig. ", title_page=False, ref_list=None)
    print(f"{len(ordered)} references numbered by first appearance; "
          f"{len(num)} distinct in-text citation forms converted")


if __name__ == "__main__":
    main()
