#!/usr/bin/env python3
"""fig_coverage_panels.py — "what each construct is made of" panels, one figure per moderator.

Writes, for each moderator, docs/figP_<field>_panels.svg plus
data/synth/phaseB/coverage_<field>.csv:

  platform      (docs/figN_platform_panels.svg — manuscript Figure 1, name kept for the builder)
  topic         ground_truth      denom_scope      country
  sampling_frame                  breadth          classification_level

One drawing routine for all of them, so the panels stay comparable and cannot drift apart.

Counting rule, same as the platform figure: STUDIES, not estimates, and a study counts once in
every value it carries for that construct, so a study whose rows cover two topics appears under
both and the bars within a panel can sum to more than the panel's k. A modal-value-per-study rule
was rejected because it is tie-dependent. A study contributing two constructs is counted in both.

Run: python3 scripts/fig_coverage_panels.py
"""

import collections
import csv
import importlib.util
import os
import re

from fig_labels import pretty, warn_missing

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLUE, INK, MUTED, TRACK = "#0072B2", "#333333", "#8a8f98", "#eef1f4"
PANELS = [("Audience exposure", "EXPOSURE"), ("Reach", "REACH"), ("Sharing", "SHARING"),
          ("Concentration", "CONCENTRATION"), ("Content prevalence", "CONTENT"),
          ("Self-reported recall", "RECALL")]


def load():
    spec = importlib.util.spec_from_file_location(
        "pbc", os.path.join(ROOT, "scripts/phaseB_platform_construct.py"))
    pbc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pbc)
    block = open(os.path.join(ROOT, "docs/FROZEN.md"), encoding="utf-8").read()
    path = os.path.join(ROOT, re.search(r"^- File: (.+)$", block, re.M).group(1).strip())
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    pool = [r for r in rows
            if r["value_kind"] == "proportion" and not (r["demographic_group"] or "").strip()]
    return pool, pbc


def gather(pool, values_of):
    """-> {construct: (k, Counter(value -> studies))}"""
    out = {}
    for _, key in PANELS:
        per_study = collections.defaultdict(set)
        for r in pool:
            if r["construct"] == key:
                per_study[r["id"]] |= values_of(r)
        counts = collections.Counter(v for s in per_study.values() for v in s)
        out[key] = (len(per_study), counts)
    return out


def plain(value, empty="Not stated"):
    """Identity label, for the fields whose values are already prose (platform, country)."""
    return value or empty


def draw(name, data, label, nrow=8):
    COLS, PW, LEFT, W, RH = 2, 340, 142, 132, 18
    shown = [(t, *data[k]) for t, k in PANELS]
    # ties sorted by label so equal bars keep a fixed order across runs (most_common follows dict order)
    shown = [(t, k, sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[:nrow]) for t, k, c in shown]
    rows_n = (len(shown) + COLS - 1) // COLS
    tallest = [max(len(shown[i][2]) for i in range(r * COLS, min((r + 1) * COLS, len(shown))))
               for r in range(rows_n)]
    tops, y = [], 40
    for mx in tallest:
        tops.append(y)
        y += 20 + mx * RH + 26

    b = []
    for i, (title, k, entries) in enumerate(shown):
        px, py = 20 + (i % COLS) * PW, tops[i // COLS]
        b += [f'<text x="{px}" y="{py}" font-size="12" font-weight="bold" fill="{INK}">{title}</text>',
              f'<text x="{px+len(title)*6.8+8}" y="{py}" font-size="10" fill="{MUTED}">k = {k}</text>']
        for j, (val, n) in enumerate(entries):
            yy, pct = py + 18 + j * RH, n / k
            lab = label(val)
            b += [f'<text x="{px+LEFT-8}" y="{yy+4}" font-size="10.5" text-anchor="end" '
                  f'fill="{INK}">{lab}</text>',
                  f'<rect x="{px+LEFT}" y="{yy-6}" width="{W}" height="12" fill="{TRACK}" rx="2"/>',
                  f'<rect x="{px+LEFT}" y="{yy-6}" width="{pct*W:.1f}" height="12" fill="{BLUE}" '
                  f'rx="2" fill-opacity="{1 if j == 0 else 0.75}"/>',
                  f'<text x="{px+LEFT+W+8}" y="{yy+4}" font-size="9.5" fill="{MUTED}">'
                  f'{pct*100:.0f}% ({n})</text>']
    w, h = 20 + COLS * PW + 20, y
    out = os.path.join(ROOT, "docs", name)
    open(out, "w", encoding="utf-8").write(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'font-family="Helvetica,Arial,sans-serif"><rect width="{w}" height="{h}" fill="#fff"/>'
        + "\n".join(b) + "</svg>\n")
    print("wrote", out)


def dump(field, data, label):
    # Tie-break on the label: the comprehension builds a SET, whose order follows the per-process
    # hash seed, so tied labels swapped places between builds of the same figure.
    labels = sorted({v for _, (_, c) in data.items() for v in c},
                    key=lambda v: (-sum(data[k][1][v] for _, k in PANELS), v))
    path = os.path.join(ROOT, "data/synth/phaseB", f"coverage_{field}.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([field] + [k for _, k in PANELS])
        for lab in labels:
            w.writerow([label(lab, "not stated")] + [data[k][1][lab] for _, k in PANELS])
        w.writerow(["TOTAL studies"] + [data[k][0] for _, k in PANELS])


def main():
    pool, pbc = load()
    # `label` differs by field: codebook levels go through the shared prose map, while platform
    # and country already carry display strings and must not be looked up.
    jobs = [("platform", "figN_platform_panels.svg",
             lambda r: pbc.labels_for(r["platform"], r["platform_norm"], r.get("construct", "")),
             plain)]
    for field in ("topic", "ground_truth", "denom_scope", "country_norm", "sampling_frame",
                  "breadth", "classification_level"):
        jobs.append((field, f"figP_{field}_panels.svg",
                     (lambda fld: (lambda r: {r[fld]} if r[fld] else set()))(field),
                     plain if field == "country_norm" else pretty))
    for field, name, values_of, label in jobs:
        data = gather(pool, values_of)
        draw(name, data, label)
        dump(field, data, label)
    warn_missing("coverage panels")


if __name__ == "__main__":
    main()
