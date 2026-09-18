#!/usr/bin/env python3
"""make_manuscript_docx.py — render docs/manuscript_draft.md to a reviewable Word document.

SUPERSEDED for submission builds: use scripts/make_nhb_docx.py, which emits the Nature Human
Behaviour pair (docs/nhb_main.docx + docs/nhb_supplementary.docx) and the figure numbering the
manuscript actually uses -- PRISMA is "Supplementary Fig. 1" there and "Figure 6" here, so a doc
built by this script contradicts docs/manuscript_draft.md on every figure cross-reference after
Figure 5. Kept for the single-file review copy only. Its last output is archived at
docs/Old/manuscript_draft_2026-08-27.docx; re-running writes a fresh docs/manuscript_draft.docx.

One-command assembly: parses the markdown (headings, bold/italic/code runs, pipe tables), inserts
the five figures (SVG -> PNG via rsvg-convert at build time), and writes docs/manuscript_draft.docx.
Tables are APA-styled (horizontal rules only, via OxmlElement). The docx is a REVIEW COPY generated
from the markdown master — edits/comments made in Word are merged back into the .md by hand; the
.md stays the single source of truth for the guards.

Run: python3 scripts/make_manuscript_docx.py
"""

import os
import re
import subprocess
import tempfile

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "docs/manuscript_draft.md")
DST = os.path.join(ROOT, "docs/manuscript_draft.docx")
FIGS = [("Figure 1.", "PRISMA flow diagram. Records identified, screened, retrieved and included, with the corpus repair shown as its own identification stream.", "docs/prisma_flow.svg"),
        ("Figure 2.", "Platforms studied, by construct. Bars are the share of that construct's studies that cover the platform, against a track showing all of them; study counts are in brackets and the eight most covered platforms are shown per construct. A study counts once in every platform it names, so bars within a panel sum to more than k. The full breakdown, including self-reported recall, is in Supplementary Note A5.", "docs/figN_platform_panels.svg"),
        ("Figure 3.", "Topics studied, by construct. Bars are the share of that construct's studies on each topic, with study counts in brackets.", "docs/figP_topic_panels.svg"),
        ("Figure 4.", "Prevalence estimates by construct. Study-level medians with 95% confidence intervals from a study-cluster bootstrap (2,000 resamples).", "docs/fig5_forest_constructs.svg"),
        ("Figure 5.", "What drives the estimate. Study-level median prevalence by measurement type, sampling frame, ground-truth source, construct, and identification level; n = studies at that level.", "docs/fig2_method_drivers.svg"),
        ("Figure 6.", "Concentration of misinformation versus news in general. Left: study-level median share of misinformation activity accounted for by the top 1% of users, across the 5 studies reporting exactly that threshold. Right: median of 6 comparison estimates of general news activity, from 4 panels that report both quantities.", "docs/figK_concentration_flow.svg"),
        ("Figure 7.", "Ground truth by construct: who decided what counted as misinformation. Same form as Figure 2.", "docs/figP_ground_truth_panels.svg"),
        ("Figure 8.", "Countries studied, by construct. Same form as Figure 2; a study counts once in every country label it carries.", "docs/figP_country_norm_panels.svg")]

TOKEN = re.compile(r"(\*\*.+?\*\*|\*[^*\n]+?\*|`[^`\n]+?`)")


def add_runs(par, text):
    for tok in TOKEN.split(text):
        if not tok:
            continue
        if tok.startswith("**") and tok.endswith("**"):
            par.add_run(tok[2:-2]).bold = True
        elif tok.startswith("*") and tok.endswith("*") and len(tok) > 2:
            par.add_run(tok[1:-1]).italic = True
        elif tok.startswith("`") and tok.endswith("`"):
            # one typeface throughout (Sacha 2026-08-11: homogenize the font, no code face)
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
    png = os.path.join(tempfile.gettempdir(), os.path.basename(svg) + ".png")
    subprocess.run(["rsvg-convert", "-w", "1800", svg, "-o", png], check=True)
    doc.add_picture(png, width=Inches(6))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap = doc.add_paragraph()
    r = cap.add_run(label + " ")
    r.bold = True
    r.font.size = Pt(10)
    r2 = cap.add_run(caption)
    r2.font.size = Pt(10)


def main():
    lines = open(SRC, encoding="utf-8").read().split("\n")
    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = "Times New Roman"
    st.font.size = Pt(11)

    i, para_buf = 0, []

    def flush():
        nonlocal para_buf
        if para_buf:
            add_runs(doc.add_paragraph(), " ".join(para_buf))
            para_buf = []

    inserted = set()

    def maybe_figure(text):
        # place each figure inline, right after the paragraph that first cites it
        for n, (label, caption, svg) in enumerate(FIGS, 1):
            if n not in inserted and f"Figure {n}" in text:
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
            add_runs(doc.add_heading("", level=min(level, 3)), ln.lstrip("# "))
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

    for n, (label, caption, svg) in enumerate(FIGS, 1):
        if n not in inserted:
            add_figure(doc, label, caption, svg)

    doc.save(DST)
    print(f"wrote {DST}")


if __name__ == "__main__":
    main()
