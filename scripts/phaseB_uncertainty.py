#!/usr/bin/env python3
"""phaseB_uncertainty.py -- the uncertainty layer the review was missing.

Four additions, each closing a gap a methods reviewer would otherwise raise:

 (1) BOOTSTRAP CIs ON THE HEADLINE MEDIANS. The primary construct table reported
     median + IQR + range but no interval. IQR describes spread across studies; it is
     NOT uncertainty about the median. Study-cluster bootstrap (resample studies, not
     estimates, so within-study dependence is respected).

 (2) HETEROGENEITY AND PREDICTION INTERVALS. The paper's central claim is that these
     constructs do not pool. The honest way to demonstrate that is a large I^2 and a wide
     prediction interval -- not merely declining to pool. Random-effects DerSimonian-Laird
     on logit-transformed proportions, per construct. The prediction interval answers
     "what would the next study find?", which is the quantity a reader actually wants and
     which no confidence interval provides.

 (3) SMALL-STUDY EFFECTS (Egger). The review's own thesis is that larger samples find
     less misinformation. That is a testable claim about funnel asymmetry, and testing it
     converts a descriptive observation into evidence. NOTE: docs/fig_funnel.svg is a
     CONCEPTUAL schematic of the misinformation funnel, NOT a statistical funnel plot --
     the two are unrelated and the naming is unfortunate.

 (4) LEAVE-ONE-OUT on the whole-diet backbone. A handful of very large studies dominate;
     this shows no single study drives the headline.

Statistical notes / honest limitations:
 - Logit (PLO) sampling variance 1/(n*p*(1-p)) assumes n independent Bernoulli draws.
   For the large behavioural studies n is user-days, tweets or URL impressions, which are
   heavily clustered, so these variances are UNDERSTATED and those studies are
   over-weighted. This affects the random-effects pooled value (reported here mainly to
   derive tau^2/I^2) far more than the medians, which are the paper's primary statistic.
   A variance-inflation sensitivity is included to show how much it matters.
 - p = 0 or 1 is handled by the standard continuity correction (+0.5 events, +1 trial).
 - Implemented in the standard library only (no numpy/scipy available in this
   environment); the t-distribution tail uses a continued-fraction incomplete beta.

Inputs : data/synth/phaseB/regression_data.csv (built by phaseB_prep_regression.py)
Outputs: data/synth/phaseB/uncertainty_medians.csv     (1)
         data/synth/phaseB/heterogeneity.csv           (2)
         data/synth/phaseB/small_study_effects.csv     (3)
         data/synth/phaseB/leave_one_out_wholediet.csv (4)

Run: python3 scripts/phaseB_uncertainty.py
"""

import csv
import math
import random
import re
import statistics as st
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/synth/phaseB"
SEED = 20260723
BOOT = 2000
random.seed(SEED)

CONSTRUCTS = ["EXPOSURE", "REACH", "SHARING", "CONTENT", "RECALL"]
WHOLE_DIET_DENOM = {"all_media", "news_diet", "population", "political_news"}


# ---------------------------------------------------------------- t distribution
def _betacf(a, b, x, itmax=200, eps=3e-12):
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    if abs(d) < 1e-30:
        d = 1e-30
    d = 1.0 / d
    h = d
    for m in range(1, itmax + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < 1e-30:
            d = 1e-30
        c = 1.0 + aa / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < 1e-30:
            d = 1e-30
        c = 1.0 + aa / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return h


def betainc(a, b, x):
    """Regularised incomplete beta I_x(a,b)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbeta = (math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
             + a * math.log(x) + b * math.log(1 - x))
    if x < (a + 1) / (a + b + 2):
        return math.exp(lbeta) * _betacf(a, b, x) / a
    return 1 - math.exp(lbeta) * _betacf(b, a, 1 - x) / b


def t_sf2(t, df):
    """Two-sided p-value for a t statistic."""
    if df <= 0:
        return float("nan")
    return betainc(df / 2.0, 0.5, df / (df + t * t))


def t_crit(df, p=0.975):
    """Inverse t by bisection (no scipy)."""
    lo, hi = 0.0, 100.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if 1 - t_sf2(mid, df) / 2 < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# ---------------------------------------------------------------- data
def load_main_set():
    """The PRIMARY analysis set: the full frozen main set, NOT restricted to studies with an
    extractable sample size.

    phaseB_uncertainty previously computed the headline medians from regression_data.csv, which
    drops any estimate without a usable n (~13% of the main set). That produced a SECOND set of
    primary numbers differing from every other script (EXPOSURE k=15 vs 16, CONTENT k=205 vs 211,
    backbone 7.5% vs 7.2%) -- precisely the kind of split the counts crosswalk exists to prevent.
    The medians and leave-one-out now use the full main set; only the parts that mathematically
    REQUIRE n (heterogeneity, Spearman) use the n-restricted subset, and they say so.
    """
    frozen_path = re.search(r"File:\s*(\S+)", (ROOT / "docs/FROZEN.md").read_text()).group(1)
    fr = list(csv.DictReader(open(ROOT / frozen_path, encoding="utf-8")))
    out = []
    for r in fr:
        if r["value_kind"] != "proportion" or r["demographic_group"].strip() or not r["value_pct"].strip():
            continue
        out.append({"study_id": r["id"], "construct": r["construct"],
                    "denom_class": r["denom_class"], "value_pct": float(r["value_pct"]),
                    "n": int(r["n"]) if str(r.get("n", "")).strip().isdigit() else 0})
    return out


def load():
    rows = list(csv.DictReader(open(OUT / "regression_data.csv", encoding="utf-8")))
    frozen_path = re.search(r"File:\s*(\S+)", (ROOT / "docs/FROZEN.md").read_text()).group(1)
    frozen = list(csv.DictReader(open(ROOT / frozen_path, encoding="utf-8")))
    denom = {str(i): (r.get("denom_class") or "").strip() for i, r in enumerate(frozen)}
    for r in rows:
        r["value_pct"] = float(r["value_pct"])
        r["n"] = int(r["n"])
        r["denom_class"] = denom.get(r["estimate_id"], "")
    return rows


def study_points(subset):
    """One point per study: median value, and the n of the estimate AT that median.

    The previous precision script paired a study's MEDIAN value with its MAX n, so the
    value and the weight could come from different estimates. Here the weight is the n of
    the estimate actually contributing the median (lower of the two for an even count),
    which keeps value and weight coherent.
    """
    by = defaultdict(list)
    for r in subset:
        by[r["study_id"]].append(r)
    pts = []
    for sid, rs in by.items():
        rs_sorted = sorted(rs, key=lambda r: r["value_pct"])
        mid = rs_sorted[(len(rs_sorted) - 1) // 2]
        pts.append((st.median([r["value_pct"] for r in rs]), mid["n"], sid))
    return pts


# ---------------------------------------------------------------- (1) bootstrap CI
def boot_median_ci(pts, B=BOOT):
    by = defaultdict(list)
    for p in pts:
        by[p[2]].append(p)
    sids = list(by)
    ests = []
    for _ in range(B):
        samp = []
        for _ in range(len(sids)):
            samp += by[random.choice(sids)]
        ests.append(st.median([v for v, _, _ in samp]))
    ests.sort()
    return ests[int(0.025 * B)], ests[int(0.975 * B)]


# ---------------------------------------------------------------- (2) DL meta-analysis
def logit_points(pts):
    out = []
    for v, n, sid in pts:
        p = v / 100.0
        e = p * n
        # continuity correction for boundary proportions
        if p <= 0 or p >= 1:
            e, n2 = e + 0.5, n + 1
            p = e / n2
        else:
            n2 = n
        if p <= 0 or p >= 1 or n2 <= 1:
            continue
        y = math.log(p / (1 - p))
        var = 1.0 / (n2 * p * (1 - p))
        if var <= 0 or not math.isfinite(var):
            continue
        out.append((y, var, sid))
    return out


def dersimonian_laird(lp, var_inflation=1.0):
    """Returns dict with tau2, I2, Q, pooled proportion, CI and prediction interval."""
    k = len(lp)
    if k < 3:
        return None
    ys = [y for y, _, _ in lp]
    vs = [v * var_inflation for _, v, _ in lp]
    w = [1 / v for v in vs]
    ybar_f = sum(wi * y for wi, y in zip(w, ys)) / sum(w)
    Q = sum(wi * (y - ybar_f) ** 2 for wi, y in zip(w, ys))
    df = k - 1
    C = sum(w) - sum(wi ** 2 for wi in w) / sum(w)
    tau2 = max(0.0, (Q - df) / C) if C > 0 else 0.0
    I2 = max(0.0, (Q - df) / Q) * 100 if Q > 0 else 0.0
    wr = [1 / (v + tau2) for v in vs]
    mu = sum(wi * y for wi, y in zip(wr, ys)) / sum(wr)
    se = math.sqrt(1 / sum(wr))
    ci = (mu - 1.96 * se, mu + 1.96 * se)
    # prediction interval: where would the NEXT study land? t on k-2 df per the Higgins/IntHout
    # convention (was k-1, which is slightly narrower — i.e. the correction WIDENS our PIs)
    tc = t_crit(max(df - 1, 1))
    pi_half = tc * math.sqrt(tau2 + se ** 2)
    pi = (mu - pi_half, mu + pi_half)
    inv = lambda z: 100 / (1 + math.exp(-z))
    return {
        "k": k, "Q": round(Q, 1), "df": df,
        "Q_p": "",
        "tau2": round(tau2, 3), "I2_pct": round(I2, 1),
        "pooled_pct": round(inv(mu), 2),
        "pooled_CI": f"{inv(ci[0]):.2f}-{inv(ci[1]):.2f}",
        "pred_interval": f"{inv(pi[0]):.2f}-{inv(pi[1]):.2f}",
        "pred_width_pp": round(inv(pi[1]) - inv(pi[0]), 1),
    }


# ---------------------------------------------------------------- (3) Egger
def spearman(pts):
    """Rank correlation between study sample size and study prevalence.

    THIS, not Egger, is the defensible small-study test for these data. Egger regresses the
    standard normal deviate on precision; when precisions span ~6 orders of magnitude (as here:
    n ranges from dozens to hundreds of millions) the design matrix is pathologically scaled and
    the fitted intercept stops being interpretable -- our run produced intercepts of 203-916 on
    the logit scale, which is not a plausible effect size. A rank correlation is invariant to that
    scaling, uses no variance assumption at all, and answers the review's actual claim directly:
    do larger studies report lower prevalence?

    Negative rho => bigger samples find less misinformation.
    """
    k = len(pts)
    if k < 5:
        return None
    vals = [v for v, _, _ in pts]
    ns = [n for _, n, _ in pts]

    def rank(xs):
        order = sorted(range(len(xs)), key=lambda i: xs[i])
        r = [0.0] * len(xs)
        i = 0
        while i < len(order):            # average ranks within ties
            j = i
            while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for t in range(i, j + 1):
                r[order[t]] = avg
            i = j + 1
        return r

    rv, rn = rank(vals), rank(ns)
    mv, mn = sum(rv) / k, sum(rn) / k
    num = sum((a - mv) * (b - mn) for a, b in zip(rv, rn))
    den = math.sqrt(sum((a - mv) ** 2 for a in rv) * sum((b - mn) ** 2 for b in rn))
    if den == 0:
        return None
    rho = num / den
    df = k - 2
    t = rho * math.sqrt(df / (1 - rho ** 2)) if abs(rho) < 1 else float("inf")
    p = t_sf2(t, df) if math.isfinite(t) else 0.0
    # 95% CI on rho by the Fisher z transform with the Bonett-Wright standard error for a rank
    # correlation, sqrt(1.06 / (k - 3)). Nature's statistics checklist asks for the test statistic,
    # its degrees of freedom, an effect size and an interval together, not a p-value alone.
    if k > 3 and abs(rho) < 1:
        z = 0.5 * math.log((1 + rho) / (1 - rho))
        se = math.sqrt(1.06 / (k - 3))
        lo, hi = (math.tanh(z - 1.96 * se), math.tanh(z + 1.96 * se))
        ci_lo, ci_hi = round(lo, 3), round(hi, 3)
    else:
        ci_lo = ci_hi = ""
    return {"k": k, "spearman_rho": round(rho, 3), "rho_ci_lo": ci_lo, "rho_ci_hi": ci_hi,
            "t": round(t, 2), "df": df,
            "p_value": round(p, 4),
            "direction": ("larger samples find LESS" if rho < 0 else
                          "larger samples find MORE" if rho > 0 else "none"),
            "significant": "yes" if p < 0.05 else "no"}


def egger(lp):
    """Egger regression: SND = a + b*precision. Intercept a != 0 => funnel asymmetry.

    RETAINED AS A DIAGNOSTIC ONLY -- do not report. See spearman() for why: with precisions
    spanning six orders of magnitude the intercept is not interpretable here.
    """
    k = len(lp)
    if k < 4:
        return None
    x = [1 / math.sqrt(v) for _, v, _ in lp]          # precision
    y = [yy / math.sqrt(v) for yy, v, _ in lp]        # standard normal deviate
    xb, yb = sum(x) / k, sum(y) / k
    sxx = sum((xi - xb) ** 2 for xi in x)
    if sxx == 0:
        return None
    b = sum((xi - xb) * (yi - yb) for xi, yi in zip(x, y)) / sxx
    a = yb - b * xb
    resid = [yi - (a + b * xi) for xi, yi in zip(x, y)]
    df = k - 2
    s2 = sum(r ** 2 for r in resid) / df
    se_a = math.sqrt(s2 * (1 / k + xb ** 2 / sxx))
    t = a / se_a if se_a > 0 else float("nan")
    return {"k": k, "egger_intercept": round(a, 3), "se": round(se_a, 3),
            "t": round(t, 2), "df": df, "p_value": round(t_sf2(t, df), 4),
            "asymmetry": "yes" if t_sf2(t, df) < 0.05 else "no"}


# ---------------------------------------------------------------- main
def main():
    rows = load_main_set()            # PRIMARY: full main analysis set
    rows_n = load()                   # n-restricted subset, for statistics that require n

    def subset(c):
        return [r for r in rows if r["construct"] == c]

    whole_diet = [r for r in rows
                  if r["denom_class"] in WHOLE_DIET_DENOM
                  and r["construct"] in ("EXPOSURE", "REACH")]

    groups = [(c, subset(c)) for c in CONSTRUCTS] + [("WHOLE-DIET backbone", whole_diet)]

    # (1) medians with bootstrap CI
    med_rows = []
    for name, sub in groups:
        pts = study_points(sub)
        if len(pts) < 3:
            continue
        vals = sorted(v for v, _, _ in pts)
        lo, hi = boot_median_ci(pts)
        q1 = st.quantiles(vals, n=4)[0] if len(vals) >= 4 else ""
        q3 = st.quantiles(vals, n=4)[2] if len(vals) >= 4 else ""
        med_rows.append({
            "group": name, "k_studies": len(pts),
            "study_median_pct": round(st.median(vals), 1),
            "boot95_lo": round(lo, 1), "boot95_hi": round(hi, 1),
            "IQR_lo": round(q1, 1) if q1 != "" else "",
            "IQR_hi": round(q3, 1) if q3 != "" else "",
            "min": round(min(vals), 1), "max": round(max(vals), 1),
        })

    # (2)-(3) require a sample size, so they run on the n-restricted subset (stated in the output)
    def subset_n(c):
        return [r for r in rows_n if r["construct"] == c]
    groups_n = [(c, subset_n(c)) for c in CONSTRUCTS] + [("WHOLE-DIET backbone",
                [r for r in rows_n if r["denom_class"] in WHOLE_DIET_DENOM
                 and r["construct"] in ("EXPOSURE", "REACH")])]

    het_rows = []
    for name, sub in groups_n:
        lp = logit_points(study_points(sub))
        base = dersimonian_laird(lp)
        if not base:
            continue
        base["group"] = name
        base["variance_assumption"] = "nominal (binomial independence)"
        het_rows.append(base)
        infl = dersimonian_laird(lp, var_inflation=10.0)
        if infl:
            infl["group"] = name
            infl["variance_assumption"] = "x10 inflation (clustering sensitivity)"
            het_rows.append(infl)

    # (3) small-study effects -- Spearman is the reportable test; Egger is diagnostic only
    egg_rows = []
    for name, sub in groups_n:
        pts = study_points(sub)
        s = spearman(pts)
        if s:
            s["group"] = name
            s["test"] = "spearman(n, value) [REPORTABLE]"
            egg_rows.append(s)
        e = egger(logit_points(pts))
        if e:
            e["group"] = name
            e["test"] = "egger [DIAGNOSTIC ONLY - do not report]"
            e["spearman_rho"] = ""
            e["direction"] = ""
            e["significant"] = e.pop("asymmetry", "")
            egg_rows.append(e)

    # (4) leave-one-out on the whole-diet backbone
    loo_rows = []
    wd_pts = study_points(whole_diet)
    full = st.median([v for v, _, _ in wd_pts])
    for _, _, drop in wd_pts:
        keep = [p for p in wd_pts if p[2] != drop]
        if len(keep) < 3:
            continue
        m = st.median([v for v, _, _ in keep])
        loo_rows.append({"study_dropped": drop, "k_remaining": len(keep),
                         "median_without": round(m, 2),
                         "delta_from_full": round(m - full, 2)})
    loo_rows.sort(key=lambda r: -abs(r["delta_from_full"]))

    def write(fn, data):
        if not data:
            return
        cols = list(data[0].keys())
        cols = [c for c in cols if c != "group"]
        cols = (["group"] + cols) if "group" in data[0] else cols
        with open(OUT / fn, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(data)

    write("uncertainty_medians.csv", med_rows)
    write("heterogeneity.csv", het_rows)
    write("small_study_effects.csv", egg_rows)
    write("leave_one_out_wholediet.csv", loo_rows)

    print(f"(1) STUDY-LEVEL MEDIANS WITH BOOTSTRAP 95% CI  (study-cluster, B={BOOT}, seed {SEED})")
    print(f"{'group':22} {'k':>3}  {'median':>7}  {'95% CI':>15}  {'IQR':>13}")
    for r in med_rows:
        print(f"{r['group']:22} {r['k_studies']:>3}  {r['study_median_pct']:>6}%  "
              f"{str(r['boot95_lo'])+'-'+str(r['boot95_hi']):>15}  "
              f"{str(r['IQR_lo'])+'-'+str(r['IQR_hi']):>13}")

    print("\n(2) HETEROGENEITY AND PREDICTION INTERVALS (DerSimonian-Laird, logit scale)")
    print(f"{'group':22} {'assumption':34} {'k':>3} {'I2%':>6} {'tau2':>7}  {'prediction interval':>22}")
    for r in het_rows:
        print(f"{r['group']:22} {r['variance_assumption']:34} {r['k']:>3} "
              f"{r['I2_pct']:>6} {r['tau2']:>7}  {r['pred_interval']:>22}")

    print("\n(3) SMALL-STUDY EFFECTS")
    print("    Spearman rank correlation of study n against study prevalence.")
    print("    Negative rho = larger samples find LESS misinformation (the review's thesis).")
    print(f"\n{'group':22} {'k':>3} {'rho':>7} {'p':>8}  direction")
    for r in egg_rows:
        if r.get("spearman_rho") == "":
            continue
        print(f"{r['group']:22} {r['k']:>3} {r['spearman_rho']:>7} {r['p_value']:>8}  "
              f"{r['direction']}{'  *' if r['significant']=='yes' else ''}")

    print(f"\n(4) LEAVE-ONE-OUT, whole-diet backbone (full median {full:.2f}%)")
    print("    largest 5 shifts:")
    for r in loo_rows[:5]:
        print(f"      drop {r['study_dropped']:24} -> {r['median_without']:>6}%  "
              f"({r['delta_from_full']:+.2f} pp)")
    print(f"    max absolute shift: {max(abs(r['delta_from_full']) for r in loo_rows):.2f} pp")
    print(f"\nwrote 4 files to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
