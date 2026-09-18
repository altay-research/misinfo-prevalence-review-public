#!/usr/bin/env python3
"""phaseB_review_response.py — analyses answering the 2026-08-24 external AI review of v11.

Outputs (data/synth/phaseB/):
  review_matched_concentration.csv  — top-1% misinfo vs news concentration on the SAME panels,
                                      per-panel matched ratios (answers "the 2x is unmatched")
  review_weight_shares.csv          — share of total sample-size weight held by the top 1 / top 3
                                      studies per construct (answers "weighted medians are one
                                      mega-study in disguise")
  review_correction_symmetry.csv    — freeze-to-freeze movement of the six construct medians,
                                      v1.5.0 -> v1.7.13 (answers the circularity/direction attack:
                                      did corrections push estimates down, toward the thesis?)
  review_human_verified_subset.csv  — construct medians restricted to studies any human
                                      (author or RA) verified at any stage, vs full corpus
  review_cramers_v.csv              — pairwise Cramér's V among the four "one family" moderators

Reads the freeze via docs/FROZEN.md like the rest of the pipeline. Deterministic (seeded).
"""
import csv, re, glob, random, statistics as st
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
random.seed(20260824)
OUT = ROOT / "data/synth/phaseB"
INPUTS = ROOT / "data/inputs"          # hand-curated inputs; see data/inputs/README.md

frozen_path = None
for line in open(ROOT / "docs/FROZEN.md"):
    m = re.match(r"- File:\s*(\S+)", line)
    if m:
        frozen_path = ROOT / m.group(1)
        break
assert frozen_path and frozen_path.exists(), "cannot resolve freeze from docs/FROZEN.md"

SIX = {"CONTENT", "RECALL", "EXPOSURE", "SHARING", "REACH", "CONCENTRATION"}

def read_frozen(path):
    return list(csv.DictReader(open(path, encoding="utf8", errors="replace")))

frozen = read_frozen(frozen_path)

# ---------------------------------------------------------------- 1. matched concentration
# The four panels that report BOTH a top-1% general-news/activity figure and a top-1%
# misinfo figure, user-level. General side from nonmisinfo_concentration.csv (topX_share,
# top_pct==1); misinfo side from the frozen concentration rows of the same studies.
nonmis = list(csv.DictReader(open(INPUTS / "nonmisinfo_concentration.csv", encoding="utf8")))
gen = defaultdict(list)
for r in nonmis:
    if r["measure"] == "topX_share" and r["top_pct"] == "1" and r["share"]:
        # exclude rows explicitly flagged as the misinfo side quoted for comparison
        if "misinfo side" in r["detail"].lower() or "MISINFO" in r["detail"]:
            continue
        gen[r["id"]].append(float(r["share"]))

mis = defaultdict(list)
for r in frozen:
    if r["construct"] != "CONCENTRATION" or (r.get("conc_unit") or "") == "source":
        continue
    gp, sh = (r.get("conc_group_pct") or "").strip(), (r.get("conc_share_pct") or "").strip()
    try:
        if gp and sh and abs(float(gp) - 1.0) < 1e-9:
            mis[r["id"]].append(float(sh))
    except ValueError:
        pass
# Zhou's 65.3 misinfo figure lives in the nonmisinfo file (side-by-side quote), keep it too
for r in nonmis:
    if r["measure"] == "topX_share" and r["top_pct"] == "1" and r["share"] and (
            "misinfo side" in r["detail"].lower() or "MISINFO" in r["detail"]):
        mis[r["id"]].append(float(r["share"]))

rows = []
for sid in sorted(set(gen) & set(mis)):
    g_med, m_med = st.median(gen[sid]), st.median(mis[sid])
    rows.append(dict(study=sid, news_top1_median=g_med, misinfo_top1_median=m_med,
                     matched_ratio=round(m_med / g_med, 2),
                     news_estimates=len(gen[sid]), misinfo_estimates=len(mis[sid])))
ratios = [r["matched_ratio"] for r in rows]
rows.append(dict(study="MEDIAN (matched panels)",
                 news_top1_median=st.median(r["news_top1_median"] for r in rows),
                 misinfo_top1_median=st.median(r["misinfo_top1_median"] for r in rows),
                 matched_ratio=round(st.median(ratios), 2),
                 news_estimates=sum(r["news_estimates"] for r in rows),
                 misinfo_estimates=sum(r["misinfo_estimates"] for r in rows)))
with open(OUT / "review_matched_concentration.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
print("matched concentration:")
for r in rows:
    print(f"  {r['study']:28} news {r['news_top1_median']:>5} misinfo {r['misinfo_top1_median']:>5} ratio {r['matched_ratio']}")

# ---------------------------------------------------------------- 2. weight shares
reg = list(csv.DictReader(open(OUT / "regression_data.csv")))
for r in reg:
    r["value_pct"] = float(r["value_pct"]); r["n"] = int(r["n"])
wrows = []
for c in sorted(SIX - {"CONCENTRATION"}):
    by = defaultdict(list)
    for r in reg:
        if r["construct"] == c:
            by[r["study_id"]].append(r)
    pts = sorted((max(x["n"] for x in rs) for rs in by.values()), reverse=True)
    tot = sum(pts)
    wrows.append(dict(construct=c, k=len(pts),
                      top1_weight_share=round(pts[0] / tot, 3),
                      top3_weight_share=round(sum(pts[:3]) / tot, 3)))
    print(f"weight share {c:9} k={len(pts):>3} top1={pts[0]/tot:.1%} top3={sum(pts[:3])/tot:.1%}")
with open(OUT / "review_weight_shares.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=wrows[0].keys()); w.writeheader(); w.writerows(wrows)

# ---------------------------------------------------------------- 3. correction symmetry
def vkey(p):
    m = re.search(r"v1\.(\d+)(?:\.(\d+))?_", p)
    return (int(m.group(1)), int(m.group(2) or 0))

def medians(path):
    out = {}
    rows = read_frozen(path)
    by = defaultdict(lambda: defaultdict(list))
    for r in rows:
        c = (r.get("construct") or "").strip()
        v = (r.get("value_pct") or "").strip()
        if c not in SIX or c == "CONCENTRATION" or not v:
            continue
        if (r.get("demographic_group") or "").strip():
            continue
        if (r.get("value_kind") or "proportion").strip() != "proportion":
            continue          # main set = proportions only, as in the invariants and descriptives
        try:
            by[c][r["id"]].append(float(v))
        except ValueError:
            continue
    for c, studies in by.items():
        out[c] = st.median(st.median(vs) for vs in studies.values())
    return out

# Single source of truth: scripts/phaseB_correction_direction.py recomputes every freeze's medians
# on the canonical main set, over the WHOLE released history, and separates corpus expansions from
# corrections. This block used to redo that computation on its own, from v1.5.0 only, without the
# main-set filter and without the expansion split, and the two disagreed. It now reads that file.
_cd_path = OUT / "correction_direction.csv"
if not _cd_path.exists():
    raise SystemExit("run scripts/phaseB_correction_direction.py first: " + str(_cd_path))
srows, updown = [], defaultdict(lambda: [0, 0])
for r in csv.DictReader(open(_cd_path)):
    if r["transition"] != "correction":
        continue
    d = float(r["delta_pp"])
    updown[r["construct"]][0 if d > 0 else 1] += 1
    srows.append(dict(from_v=r["from_version"], to_v=r["to_version"], construct=r["construct"],
                      before=r["from_median"], after=r["to_median"], delta=d))
with open(OUT / "review_correction_symmetry.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["from_v", "to_v", "construct", "before", "after", "delta"])
    w.writeheader(); w.writerows(srows)
tot_up = sum(v[0] for v in updown.values()); tot_dn = sum(v[1] for v in updown.values())
print(f"correction symmetry (corrections only, whole release history): "
      f"{tot_up} moves UP (against thesis), {tot_dn} moves DOWN (toward thesis)")
for c, (u, d) in sorted(updown.items()):
    print(f"  {c:9} up {u:>2} down {d:>2}")

# ---------------------------------------------------------------- 4. human-verified subset
ID_RE = re.compile(r"(2-s2\.0-\d+|OA-W\d+|W\d{8,}|SEED-[A-Za-z0-9_]+)")
sources = [
    "docs/RA_package/irr_v2/ANSWER_KEY.csv",
    "docs/RA_package/irr_v2/ANSWER_KEY_batch2.csv",
    "docs/RA_package/round1_2026-07/adjudication_29_resolved.csv",
    "docs/RA_package/round1_2026-07/ra29_verification_SACHA.csv",
    "docs/RA_package/round1_2026-07/phase1_readjudication.csv",
    "data/extract_v2/qa/curation_adjudication.csv",
    "data/extract_v2/qa/cordonnier_changelog.csv",
    "data/extract_v2/qa/gonzalez_changelog.csv",
]
human_ids = set()
for s in sources:
    p = ROOT / s
    if p.exists():
        human_ids |= set(ID_RE.findall(p.read_text(encoding="utf8", errors="replace")))
frozen_ids = {r["id"] for r in frozen}
human_ids &= frozen_ids
print(f"human-verified studies in freeze: {len(human_ids)} of {len(frozen_ids)}")

hrows = []
by_full = defaultdict(lambda: defaultdict(list))
for r in frozen:
    c, v = (r["construct"] or "").strip(), (r["value_pct"] or "").strip()
    if (c in SIX and c != "CONCENTRATION" and v and not (r.get("demographic_group") or "").strip()
            and (r.get("value_kind") or "proportion").strip() == "proportion"):
        try:
            by_full[c][r["id"]].append(float(v))
        except ValueError:
            pass
for c in sorted(SIX - {"CONCENTRATION"}):
    full = {sid: st.median(vs) for sid, vs in by_full[c].items()}
    sub = {sid: v for sid, v in full.items() if sid in human_ids}
    hrows.append(dict(construct=c, k_full=len(full), median_full=round(st.median(full.values()), 1),
                      k_human=len(sub),
                      median_human=round(st.median(sub.values()), 1) if sub else ""))
    print(f"  {c:9} full {hrows[-1]['median_full']:>5} (k={len(full):>3})  "
          f"human-verified {hrows[-1]['median_human']:>5} (k={len(sub)})")
hrows.append(dict(construct="TOTAL_HUMAN_VERIFIED_STUDIES", k_full=len(frozen_ids),
                  median_full="", k_human=len(human_ids), median_human=""))
with open(OUT / "review_human_verified_subset.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=hrows[0].keys()); w.writeheader(); w.writerows(hrows)

# ---------------------------------------------------------------- 5. Cramér's V matrix
def cramers_v(xs, ys):
    pairs = [(x, y) for x, y in zip(xs, ys) if x and y]
    xs2, ys2 = [p[0] for p in pairs], [p[1] for p in pairs]
    xcats, ycats = sorted(set(xs2)), sorted(set(ys2))
    n = len(pairs)
    obs = defaultdict(int)
    for x, y in pairs:
        obs[(x, y)] += 1
    xm = {x: sum(obs[(x, y)] for y in ycats) for x in xcats}
    ym = {y: sum(obs[(x, y)] for x in xcats) for y in ycats}
    chi2 = sum((obs[(x, y)] - xm[x] * ym[y] / n) ** 2 / (xm[x] * ym[y] / n)
               for x in xcats for y in ycats if xm[x] and ym[y])
    k = min(len(xcats), len(ycats)) - 1
    return (chi2 / (n * k)) ** 0.5 if k else 0.0, n

MODS = ["id_method", "ground_truth", "measurement", "sampling"]
crows = []
for i, a in enumerate(MODS):
    for b in MODS[i + 1:]:
        v, n = cramers_v([r[a] for r in reg], [r[b] for r in reg])
        crows.append(dict(mod_a=a, mod_b=b, cramers_v=round(v, 2), n_estimates=n))
        print(f"Cramér's V {a:12} x {b:12} = {v:.2f} (n={n})")
with open(OUT / "review_cramers_v.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=crows[0].keys()); w.writeheader(); w.writerows(crows)
print("done.")

# ---------------------------------------------------------------- 6. item10 x design (2026-08-24)
# Sacha's observation: item 10 as applied is largely determined by the sampling design.
# This table is the evidence, and the manuscript's B1 now reports RoB descriptively on it.
rob_master = {r["study_id"]: r for r in csv.DictReader(
    open(ROOT / "data/rob/risk_of_bias_v3_master.csv", encoding="utf8", errors="replace"))}
dn = defaultdict(list)
for r in frozen:
    if (r.get("denom_class") or "").strip():
        dn[r["id"]].append(r["denom_class"].strip())
rows10 = []
tab = defaultdict(lambda: [0, 0])
for sid, ds in dn.items():
    rm = rob_master.get(sid)
    if rm and (rm.get("item10") or "").upper() in ("LOW", "HIGH"):
        d = sorted(ds, key=ds.count)[-1]
        tab[d][0 if rm["item10"].upper() == "HIGH" else 1] += 1
for d, (hi, lo) in sorted(tab.items()):
    rows10.append(dict(denom_class=d, item10_high=hi, item10_low=lo,
                       pct_high=round(100 * hi / (hi + lo)) if hi + lo else ""))
with open(OUT / "review_item10_design.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows10[0].keys()); w.writeheader(); w.writerows(rows10)
print("item10 x denom_class:")
for r in rows10:
    print(f"  {r['denom_class']:16} HIGH {r['item10_high']:>3} LOW {r['item10_low']:>3}  ({r['pct_high']}%)")
