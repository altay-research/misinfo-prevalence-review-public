#!/usr/bin/env python3
"""Box 1 — the CCDH-vs-Meta denominator contrast, as a print figure (SVG).

The same twelve anti-vaccine accounts ("Disinformation Dozen"): 65% of a CURATED sample of shared
anti-vaccine content (CCDH) vs 0.05% of what users ACTUALLY SAW (Meta). One numerator, two
denominators, ~1,300x = three orders of magnitude. This is the paper's thesis in one exhibit.

Design (dataviz skill): form = hero contrast (two numbers + their denominators), not a series
chart; two independent 0-100% tracks so BOTH percentages are readable (a shared linear axis would
render 0.05% invisible; a log axis would muddy "a share of what"). Colour = the project's CVD-safe
pair, validated: vermillion #D55E00 (alarming/curated) vs blue #0072B2 (reassuring/diet), ΔE 21.9
CVD / 31.2 normal. Direct value labels (identity never colour-alone); recessive tracks; 4px rounded
data-ends. Static SVG (a print box, not an interactive dashboard).

Run: python3 scripts/make_box1.py  ->  docs/box1_ccdh_meta.svg
"""

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs/box1_ccdh_meta.svg")

VERM, BLUE = "#D55E00", "#0072B2"
INK, MUTE, LINE, SURF, TRACK = "#2c2a26", "#6b655c", "#e0d7c4", "#fcfcfb", "#ece7db"
W, H = 760, 400
PADX = 44
TRACK_X, TRACK_W = PADX, W - 2 * PADX          # full-width track
BAR_H = 34
R = 4


def bar(y, frac, colour, label_left, value, denom, note=""):
    filled = max(TRACK_W * frac, 3)            # min 3px so 0.05% is a visible sliver
    s = []
    # label above the track
    s.append(f'<text x="{TRACK_X}" y="{y-12}" font-size="13" fill="{MUTE}" '
             f'font-family="Georgia,serif" letter-spacing="0.3">{label_left}</text>')
    # recessive full track
    s.append(f'<rect x="{TRACK_X}" y="{y}" width="{TRACK_W}" height="{BAR_H}" rx="{R}" '
             f'fill="{TRACK}"/>')
    # filled bar, rounded data-end
    s.append(f'<rect x="{TRACK_X}" y="{y}" width="{filled:.1f}" height="{BAR_H}" rx="{R}" '
             f'fill="{colour}"/>')
    # value label — inside the bar if wide enough, else just right of the sliver
    if filled > 90:
        s.append(f'<text x="{TRACK_X+filled-12:.1f}" y="{y+BAR_H/2+6}" font-size="22" '
                 f'font-weight="bold" fill="#fff" text-anchor="end" '
                 f'font-family="Georgia,serif">{value}</text>')
    else:
        s.append(f'<text x="{TRACK_X+filled+10:.1f}" y="{y+BAR_H/2+7}" font-size="22" '
                 f'font-weight="bold" fill="{colour}" font-family="Georgia,serif">{value}</text>')
        if note:
            s.append(f'<text x="{TRACK_X+filled+74:.1f}" y="{y+BAR_H/2+6}" font-size="12.5" '
                     f'fill="{MUTE}" font-style="italic" font-family="Georgia,serif">{note}</text>')
    # denominator (what 100% means), under the track, right-aligned
    s.append(f'<text x="{TRACK_X+TRACK_W}" y="{y+BAR_H+18}" font-size="12.5" fill="{MUTE}" '
             f'text-anchor="end" font-family="Georgia,serif">100% = {denom}</text>')
    return "\n".join(s)


def main():
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" font-family="Georgia,serif">',
         f'<rect width="{W}" height="{H}" fill="{SURF}"/>',
         f'<rect x="0" y="0" width="{W}" height="6" fill="{INK}"/>']
    # title
    p.append(f'<text x="{PADX}" y="46" font-size="21" font-weight="bold" fill="{INK}">'
             f'Box 1 · One numerator, two denominators</text>')
    p.append(f'<text x="{PADX}" y="70" font-size="14.5" fill="{MUTE}">The same twelve anti-vaccine '
             f'accounts (the &#8220;Disinformation Dozen&#8221;), measured two ways:</text>')

    p.append(bar(126, 0.65, VERM,
                 "CCDH (advocacy) &#183; share of a CURATED sample of shared anti-vaccine content",
                 "65%", "anti-vaccine posts hand-collected for the report"))
    p.append(bar(224, 0.0005, BLUE,
                 "Meta (platform) &#183; share of what users ACTUALLY SAW in their feeds",
                 "0.05%", "all content shown to Facebook/Instagram users",
                 note="&#8592; essentially invisible at true scale"))

    # ratio callout
    p.append(f'<line x1="{PADX}" y1="292" x2="{W-PADX}" y2="292" stroke="{LINE}" stroke-width="1"/>')
    p.append(f'<text x="{PADX}" y="322" font-size="16" fill="{INK}">'
             f'<tspan font-weight="bold" font-size="20">&#215;1,300</tspan>'
             f'<tspan fill="{MUTE}">  &#8212; three orders of magnitude, from the denominator alone.'
             f'</tspan></text>')
    p.append(f'<text x="{PADX}" y="350" font-size="13" fill="{MUTE}" font-style="italic">'
             f'Both figures are arithmetically correct. The numerator (the twelve accounts) is '
             f'identical;</text>')
    p.append(f'<text x="{PADX}" y="368" font-size="13" fill="{MUTE}" font-style="italic">'
             f'only the denominator &#8212; a share of <tspan font-style="normal" '
             f'font-weight="bold">what?</tspan> &#8212; changed.</text>')
    p.append("</svg>")
    open(OUT, "w", encoding="utf-8").write("\n".join(p))
    print("wrote", os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main()
