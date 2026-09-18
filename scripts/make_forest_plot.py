#!/usr/bin/env python3
"""fig5 — forest plot of the headline medians with bootstrap confidence intervals.

WHY. The review's flagship figures showed medians and IQRs but no intervals, so the central claim
("these quantities differ by an order of magnitude") was presented without any expression of
uncertainty about the medians themselves. An IQR is spread ACROSS studies, not uncertainty about the
summary — a conflation this genre makes constantly. This is the exhibit that shows the claim survives
its own uncertainty: EXPOSURE's interval and RECALL's interval do not approach each other.

FORM. The data's job is magnitude-with-uncertainty for a handful of named groups, so: a dot-and-
interval (forest) plot, one row per group, sorted by value. Not a bar chart — bars imply a count
from zero and would bury the interval, which is the point of the figure.

DESIGN NOTES (per the dataviz method):
  * Log x-axis, because the values span 2.6% to 69.7% and a linear axis would compress everything
    below 10% into an unreadable smear — which is precisely the region the paper's argument lives in.
  * One series, so no legend; the groups are direct-labelled at the left and every point carries its
    value. Identity is never colour-alone.
  * Colour is NOT used to encode the value (position already does that). A single hue carries the
    marks; the whole-diet backbone is distinguished by a second validated hue because it is a
    different KIND of row (a composite of two constructs, not a construct).
  * Palette #0072B2 / #E69F00 validated with scripts/validate_palette.js -- all checks PASS.
  * Recessive grid, 2px intervals, 9px markers, 2px surface ring on the marker so it stays legible
    where it overlaps its own interval.

Inputs : data/synth/phaseB/uncertainty_medians.csv
Outputs: docs/fig5_forest_constructs.svg

Run: python3 scripts/phaseB_uncertainty.py && python3 scripts/make_forest_plot.py
"""

import csv
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data/synth/phaseB/uncertainty_medians.csv")
DST = os.path.join(ROOT, "docs/fig5_forest_constructs.svg")

INK, MUTED, GRID = "#1f2933", "#6b7280", "#e8eaed"
HUE, HUE2 = "#0072B2", "#E69F00"          # validated pair
SURFACE = "#ffffff"

LABELS = {
    "EXPOSURE": ("Audience exposure", "share of a person's information diet"),
    "REACH": ("Reach", "% of people encountering it at least once"),
    "SHARING": ("Sharing", "share of sharing acts that carried misinformation"),
    "CONTENT": ("Content prevalence", "share of items in a corpus that are false"),
    "RECALL-seen": ("Self-reported recall (seen)", "% who say they have seen it"),
    "RECALL-shared": ("Self-reported recall (shared)", "% who say they have shared it"),
}


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    rows = [r for r in csv.DictReader(open(SRC, encoding="utf-8")) if r["boot95_lo"] != ""
            and r["group"] != "WHOLE-DIET backbone"]   # backbone has its own section + figure (Sacha, v6 round)
    # RECALL is reported split (seen vs shared), matching the text and tables — the merged
    # RECALL row is replaced by the two rows of recall_split.csv (Sacha, docx comments 2026-08-11)
    rows = [r for r in rows if r["group"] != "RECALL"]
    rsp = os.path.join(ROOT, "data/synth/phaseB/recall_split.csv")
    SPLIT = {"RECALL_exposure": "RECALL-seen", "RECALL_sharing": "RECALL-shared"}
    for s in csv.DictReader(open(rsp, encoding="utf-8")):
        if s["group"] not in SPLIT:
            continue
        rows.append({"group": SPLIT[s["group"]], "k_studies": s["k_studies"],
                     "study_median_pct": s["median"],
                     "boot95_lo": s["ci_lo"], "boot95_hi": s["ci_hi"]})
    rows.sort(key=lambda r: float(r["study_median_pct"]))

    W, H = 940, 40 + 52 * len(rows) + 56
    L, R = 300, 90                      # generous left gutter for two-line direct labels
    TOP = 34
    lo_x, hi_x = 0.0, 100.0             # LINEAR scale (log understated the gaps — Sacha, v6 round)

    def X(v):
        return L + (v - lo_x) / (hi_x - lo_x) * (W - L - R)

    # no title inside the figure: the caption lives in the document (Sacha, v6 round)
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'font-family="Helvetica,Arial,sans-serif">',
         f'<rect width="{W}" height="{H}" fill="{SURFACE}"/>']

    for gx in (0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100):
        p.append(f'<line x1="{X(gx):.1f}" y1="{TOP-14}" x2="{X(gx):.1f}" y2="{H-52}" '
                 f'stroke="{GRID}" stroke-width="1"/>')
        p.append(f'<text x="{X(gx):.1f}" y="{H-34}" font-size="10.5" text-anchor="middle" '
                 f'fill="{MUTED}">{gx:g}%</text>')

    for i, r in enumerate(rows):
        y = TOP + 26 + i * 52
        med = float(r["study_median_pct"])
        lo, hi = float(r["boot95_lo"]), float(r["boot95_hi"])
        col = HUE2 if r["group"] == "WHOLE-DIET backbone" else HUE
        name, sub = LABELS.get(r["group"], (r["group"], ""))

        p.append(f'<text x="{L-22}" y="{y+1}" font-size="13.5" text-anchor="end" '
                 f'font-weight="600" fill="{INK}">{esc(name)}</text>')
        p.append(f'<text x="{L-22}" y="{y+17}" font-size="10.5" text-anchor="end" '
                 f'fill="{MUTED}">{esc(sub)}</text>')
        p.append(f'<text x="{L-22}" y="{y-15}" font-size="10" text-anchor="end" '
                 f'fill="{MUTED}">k = {r["k_studies"]}</text>')

        # interval, then a ringed marker so it reads where it overlaps the line
        p.append(f'<line x1="{X(lo):.1f}" y1="{y}" x2="{X(hi):.1f}" y2="{y}" '
                 f'stroke="{col}" stroke-width="2" stroke-linecap="round"/>')
        for v in (lo, hi):
            p.append(f'<line x1="{X(v):.1f}" y1="{y-5}" x2="{X(v):.1f}" y2="{y+5}" '
                     f'stroke="{col}" stroke-width="2"/>')
        p.append(f'<circle cx="{X(med):.1f}" cy="{y}" r="6" fill="{col}" '
                 f'stroke="{SURFACE}" stroke-width="2"/>')
        p.append(f'<text x="{X(med):.1f}" y="{y-13}" font-size="12" text-anchor="middle" '
                 f'font-weight="700" fill="{INK}">{med:.1f}%</text>')
        # no numeric CI labels: the error bars carry the interval (Sacha, docx comments 2026-08-11)

    # (no footer note: provenance/interpretation notes never ship inside figures — Sacha 2026-08-11)
    p.append("</svg>")

    open(DST, "w", encoding="utf-8").write("\n".join(p))
    print(f"wrote {os.path.relpath(DST, ROOT)}  ({len(rows)} rows)")
    for r in rows:
        print(f"  {r['group']:22} k={r['k_studies']:>3}  {r['study_median_pct']:>5}%  "
              f"[{r['boot95_lo']}–{r['boot95_hi']}]")


if __name__ == "__main__":
    main()
