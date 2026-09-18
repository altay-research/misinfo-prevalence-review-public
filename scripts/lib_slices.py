#!/usr/bin/env python3
"""lib_slices.py — the canonical study-level aggregation used for every published median.

The paper's headline statistics are STUDY-level: median within each study, then median across
studies. This module is the single Python definition of that rule, extracted verbatim from
scripts/phaseB_slices.py so that build_site.py and check_site.py cannot drift from the analysis.

check_site.py asserts two things against it:
  1. sl() reproduces every row of every data/synth/phaseB/slices_*.csv (Python <-> Python);
  2. the JavaScript port in site/assets/site.js returns the same values (JS <-> Python).

phaseB_slices.py keeps its own copy for now; it is the pipeline and is not edited mid-submission.
check_site.py compares the two sources textually so the copies cannot silently diverge.
"""
import statistics as st
from collections import defaultdict

__all__ = ["sl", "el", "iqr"]


def sl(values_by_study):
    """Study-level: median-per-study, then across studies.

    Takes {study_id: [pct, ...]} and returns (n_studies, median, q1, q3, min, max).
    q1/q3 are None below four studies: the exclusive quartile method is unstable there and the
    published tables print 'n<4' rather than a number.
    """
    meds = sorted(st.median(v) for v in values_by_study.values() if v)
    if not meds:
        return (0, None, None, None, None, None)
    mn, mx = min(meds), max(meds)
    if len(meds) >= 4:
        q = st.quantiles(meds, n=4)
        # clamp: the exclusive method can extrapolate past the observed data at small n
        q1, q3 = max(q[0], mn), min(q[2], mx)
    else:
        q1 = q3 = None
    return (len(meds),
            round(st.median(meds), 1),
            round(q1, 1) if q1 is not None else None,
            round(q3, 1) if q3 is not None else None,
            round(mn, 1), round(mx, 1))


def el(values):
    """Estimate-level: (count, median) over every parsed percentage, ignoring study membership."""
    vals = [v for v in values if v is not None]
    return (len(vals), round(st.median(vals), 1) if vals else None)


def iqr(q1, q3):
    """The published IQR string. 'n<4' is a value, not a missing marker."""
    return f"{q1}–{q3}" if q1 is not None else "n<4"


def group_by_study(records, key=lambda r: r["id"], value=lambda r: r.get("value")):
    """Helper: {study_id: [values]} from a list of estimate records, dropping unparsed values."""
    by = defaultdict(list)
    for r in records:
        v = value(r)
        if v is not None:
            by[key(r)].append(v)
    return by
