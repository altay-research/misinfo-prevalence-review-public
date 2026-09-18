/* agg.js — the browser port of scripts/lib_slices.py.
 *
 * The paper's medians are STUDY-level: median within each study, then median across studies.
 * Cross-filtered slices cannot be precomputed, so this file does the arithmetic client-side,
 * which makes it a second implementation of a published statistic. scripts/check_site.py runs it
 * under Node against every data/synth/phaseB/slices_*.csv and fails the build on any mismatch.
 *
 * Three details carry that parity and are easy to get wrong:
 *   - Python's round() is round-half-to-EVEN applied to the exact binary value of the double.
 *     (0.35).toFixed(1) is "0.4" in JS; Python's round(0.35, 1) is 0.3, because the double nearest
 *     0.35 is 0.34999999999999997780. pyRound below reads that exact expansion via toFixed(20).
 *   - statistics.quantiles(n=4) defaults to the EXCLUSIVE method, which is not what most quantile
 *     helpers implement. quartiles() reproduces CPython's integer arithmetic exactly.
 *   - below four studies there is no IQR at all; the published tables print "n<4", which is a
 *     value and not a missing marker.
 */

export function pyRound(x, nd) {
  if (x === null || x === undefined || !isFinite(x)) return null;
  if (nd === undefined) nd = 1;
  const neg = x < 0, s = Math.abs(x).toFixed(20);  // exact decimal expansion of the double
  const dot = s.indexOf('.');
  const digits = s.slice(0, dot) + s.slice(dot + 1);
  const cut = dot + nd;                            // index of the first dropped digit
  let head = digits.slice(0, cut), tail = digits.slice(cut);
  let up;
  const first = tail.charCodeAt(0) - 48;
  if (first > 5) up = true;
  else if (first < 5) up = false;
  else up = /[1-9]/.test(tail.slice(1))            // anything beyond the 5 breaks the tie
            ? true
            : ((head.charCodeAt(head.length - 1) - 48) % 2 === 1);  // exact tie -> to even
  if (up) head = (BigInt(head) + 1n).toString().padStart(head.length, '0');
  const v = Number(head) / Math.pow(10, nd);
  return neg ? -v : v;
}

export function median(arr) {
  if (!arr.length) return null;
  const s = [...arr].sort((a, b) => a - b), m = s.length >> 1;
  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
}

/* CPython statistics.quantiles(data, n=4, method='exclusive') */
export function quartiles(data) {
  const d = [...data].sort((a, b) => a - b), ld = d.length, n = 4, m = ld + 1, out = [];
  for (let i = 1; i < n; i++) {
    let j = Math.floor((i * m) / n);
    j = j < 1 ? 1 : (j > ld - 1 ? ld - 1 : j);
    const delta = i * m - j * n;
    out.push((d[j - 1] * (n - delta) + d[j] * delta) / n);
  }
  return out;
}

/* Study-level aggregation. `byStudy` is a Map or object of studyId -> [pct, ...]. */
export function sl(byStudy) {
  const lists = byStudy instanceof Map ? [...byStudy.values()] : Object.values(byStudy);
  const meds = lists.filter(v => v && v.length).map(median).sort((a, b) => a - b);
  if (!meds.length) return { k: 0, median: null, q1: null, q3: null, min: null, max: null };
  const mn = meds[0], mx = meds[meds.length - 1];
  let q1 = null, q3 = null;
  if (meds.length >= 4) {
    const q = quartiles(meds);
    q1 = Math.max(q[0], mn);   // clamp: the exclusive method extrapolates past the data at small n
    q3 = Math.min(q[2], mx);
  }
  return {
    k: meds.length,
    median: pyRound(median(meds), 1),
    q1: q1 === null ? null : pyRound(q1, 1),
    q3: q3 === null ? null : pyRound(q3, 1),
    min: pyRound(mn, 1), max: pyRound(mx, 1),
  };
}

export function el(values) {
  const v = values.filter(x => x !== null && x !== undefined);
  return { n: v.length, median: v.length ? pyRound(median(v), 1) : null };
}

/* Python prints round(x,1) as "12.0", JavaScript's String(12.0) is "12". Every published string
 * goes through fmt so the two agree; check_site.py compares these strings, not the numbers. */
export const fmt = x => (x === null || x === undefined) ? 'None' : x.toFixed(1);

export function iqrText(q1, q3) { return q1 === null ? 'n<4' : `${fmt(q1)}–${fmt(q3)}`; }

export function groupByStudy(records, valueOf) {
  const by = new Map();
  for (const r of records) {
    const v = valueOf ? valueOf(r) : r.value;
    if (v === null || v === undefined) continue;
    let a = by.get(r.id);
    if (!a) by.set(r.id, a = []);
    a.push(v);
  }
  return by;
}

/* One call: filtered records -> the published statistic shape. */
export function summarise(records) {
  const s = sl(groupByStudy(records));
  const e = el(records.map(r => r.value));
  return { ...s, iqr: iqrText(s.q1, s.q3), n_est: e.n, el_median: e.median };
}
