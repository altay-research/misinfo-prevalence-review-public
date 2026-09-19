/**
 * stress_site.mjs — exhaustive checks on the site's data and its pure logic.
 *
 *   node scripts/stress_site.mjs
 *
 * check_site.py proves the published slices reproduce. This goes after everything else: every
 * field, every level, every single-filter slice, the aggregation's edge cases, the URL codec, and
 * the data's internal consistency. It runs in a second and is meant to be run before any release.
 *
 * It is deliberately paranoid about the things that would be invisible on a page: a level that
 * matches nothing, a record that cannot render, an id that collides, a number that disagrees with
 * itself depending on which way you compute it.
 */
import { readFileSync, existsSync } from 'node:fs';
// the working repository keeps the site at the root; the public package publishes it under companion/
const SITE = existsSync(new URL('../site/', import.meta.url)) ? '../site/' : '../companion/site/';
const { summarise, sl, el, pyRound, median, quartiles, iqrText, groupByStudy, fmt } =
  await import(new URL(`${SITE}assets/agg.js`, import.meta.url));

const S = p => JSON.parse(readFileSync(new URL(`${SITE}${p}`, import.meta.url), 'utf8'));
const meta = S('data/meta.json');
const est = S('data/estimates.json');
const studies = S('data/studies.json');
const slices = S('data/slices.json');
const MAIN = est.filter(e => e.main && e.value !== null && e.value !== undefined);

let pass = 0, fail = 0;
const failures = [];
const check = (name, ok, detail = '') => {
  if (ok) pass++;
  else { fail++; failures.push(name + (detail ? ` — ${detail}` : '')); }
};
const section = n => console.log(`\n── ${n}`);

/* ═══ 1. identity and referential integrity ═══ */
section('identity');
check('every estimate has an id', est.every(e => e.eid && /^[0-9a-f]{7,}$/.test(e.eid)));
check('ids are unique', new Set(est.map(e => e.eid)).size === est.length,
      `${est.length - new Set(est.map(e => e.eid)).size} collisions`);
check('every estimate resolves to a study', est.every(e => studies[e.id]));
check('every study is reachable from an estimate',
      Object.keys(studies).every(id => est.some(e => e.id === id)));
check('corpus counts agree with meta',
      est.length === meta.n_estimates && Object.keys(studies).length === meta.n_studies);
check('main-set counts agree with meta',
      MAIN.length === meta.n_main_estimates &&
      new Set(MAIN.map(e => e.id)).size === meta.n_main_studies,
      `${MAIN.length} vs ${meta.n_main_estimates}`);
check('every study carries a risk-of-bias rating',
      Object.values(studies).every(s => ['LOW', 'MODERATE', 'HIGH'].includes(s.rob)));
check('no estimate carries a value outside 0-100',
      MAIN.every(e => e.value >= 0 && e.value <= 100),
      MAIN.filter(e => e.value < 0 || e.value > 100).map(e => `${e.eid}=${e.value}`).join(' '));

/* ═══ 2. every control, every level ═══ */
section('controls and levels');
for (const f of meta.controls) {
  const levels = [...new Set(est.map(e => e[f]).filter(Boolean))];
  check(`${f}: has levels`, levels.length > 0);
  check(`${f}: every level matches at least one estimate`,
        levels.every(v => est.some(e => e[f] === v)));
  // a level that matches nothing in the MAIN set still renders a chip that yields an empty view;
  // that is allowed, but it must not throw
  for (const v of levels) {
    const rows = MAIN.filter(e => e[f] === v);
    let s;
    try { s = summarise(rows); } catch (err) { s = null; }
    check(`${f}=${v}: summarises without throwing`, s !== null);
    if (s && s.k >= 4) {
      check(`${f}=${v}: median within its own range`,
            s.median >= s.min && s.median <= s.max, `${s.median} vs [${s.min}, ${s.max}]`);
      check(`${f}=${v}: IQR inside the range`,
            s.q1 >= s.min && s.q3 <= s.max, `[${s.q1}, ${s.q3}] vs [${s.min}, ${s.max}]`);
      check(`${f}=${v}: q1 <= median <= q3`, s.q1 <= s.median && s.median <= s.q3,
            `${s.q1} / ${s.median} / ${s.q3}`);
    }
    if (s && s.k < 4) check(`${f}=${v}: no IQR below four studies`, s.iqr === 'n<4');
  }
}

/* ═══ 3. cross-filters: every pair of levels across every pair of fields ═══ */
section('cross-filters');
let pairs = 0, empties = 0;
for (let i = 0; i < meta.controls.length; i++) {
  for (let j = i + 1; j < meta.controls.length; j++) {
    const fa = meta.controls[i], fb = meta.controls[j];
    const la = [...new Set(MAIN.map(e => e[fa]).filter(Boolean))];
    const lb = [...new Set(MAIN.map(e => e[fb]).filter(Boolean))];
    for (const va of la) for (const vb of lb) {
      const rows = MAIN.filter(e => e[fa] === va && e[fb] === vb);
      pairs++;
      if (!rows.length) { empties++; continue; }
      const s = summarise(rows);
      if (s.k === 0 || s.median === null) { check(`${fa}=${va} x ${fb}=${vb}`, false, 'null median on non-empty rows'); continue; }
      if (s.k >= 4 && !(s.q1 <= s.median && s.median <= s.q3)) {
        check(`${fa}=${va} x ${fb}=${vb}`, false, `IQR straddle: ${s.q1}/${s.median}/${s.q3}`);
      }
    }
  }
}
check(`all ${pairs} two-field combinations summarise correctly`, true);
console.log(`   ${pairs} combinations tested, ${empties} empty (a legitimate "no studies match")`);

/* ═══ 4. the aggregation's own edge cases ═══ */
section('aggregation edge cases');
check('empty input', summarise([]).k === 0 && summarise([]).median === null);
check('single study', (() => { const s = sl({ a: [5] }); return s.k === 1 && s.median === 5 && s.q1 === null; })());
check('three studies still refuse an IQR', sl({ a: [1], b: [2], c: [3] }).q1 === null);
check('four studies produce one', sl({ a: [1], b: [2], c: [3], d: [4] }).q1 !== null);
check('a study with many estimates counts once',
      sl({ a: [1, 1, 1, 1, 1, 1], b: [9] }).k === 2);
check('within-study median, not mean', sl({ a: [0, 0, 100] }).median === 0);
check('IQR is clamped to the data', (() => {
  const s = sl({ a: [10], b: [20], c: [30], d: [40] });
  return s.q1 >= s.min && s.q3 <= s.max;
})());
check('median of an even count interpolates', median([1, 2, 3, 4]) === 2.5);
check('quartiles use the exclusive method',
      JSON.stringify(quartiles([1, 2, 3, 4]).map(x => +x.toFixed(4))) === JSON.stringify([1.25, 2.5, 3.75]));
// Python's round() is half-to-even on the exact binary value
for (const [x, want] of [[0.35, 0.3], [0.25, 0.2], [0.15, 0.1], [7.45, 7.5], [3.35, 3.4],
                         [0.125, 0.1], [2.675, 2.7], [1.05, 1.1], [0.05, 0.1], [18.5, 18.5],
                         [0, 0], [100, 100],
                         // the double nearest 99.95 is 99.95000000000000284, so it rounds UP
                         [99.95, 100], [99.94, 99.9], [0.449, 0.4]]) {
  check(`pyRound(${x})`, pyRound(x, 1) === want, `got ${pyRound(x, 1)}, python gives ${want}`);
}
check('fmt prints one decimal like Python', fmt(12) === '12.0' && fmt(0) === '0.0');
check('iqrText below four studies', iqrText(null, null) === 'n<4');

/* ═══ 5. the published slices, once more from the shipped data ═══ */
section('published slices');
const PREV = meta.construct_order;
const AUD = ['EXPOSURE', 'REACH', 'RECALL'];
const SPEC = {
  by_construct: ['construct', null], ground_truth: ['ground_truth', PREV],
  measurement: ['measurement', PREV], topic: ['topic', PREV],
  sampling: ['sampling_frame', PREV], platform: ['platform_norm', AUD.concat('CONTENT')],
  country_scope: ['country_scope', PREV],
  breadth_content: ['breadth', ['CONTENT']], breadth_audience: ['breadth', AUD],
  denom_content: ['denom_class', ['CONTENT']], denom_audience: ['denom_class', AUD],
};
const BLANK = new Set(['not_stated', 'not_reported', '']);
const ALIAS = { 'domain_list/NewsGuard': ['domain_list', 'NewsGuard'], 'classifier/LLM': ['classifier'] };
const same = (site, pub) => ['(blank)', '?'].includes(pub) ? BLANK.has(site ?? '')
  : (ALIAS[pub] ? ALIAS[pub].includes(site) : (site ?? '') === pub);

let rowsChecked = 0;
for (const [name, rows] of Object.entries(slices)) {
  const spec = SPEC[name];
  if (!spec) continue;
  const [field, constructs] = spec;
  for (const row of rows) {
    const sub = MAIN.filter(e => same(e[field], row.value) &&
                                 (!constructs || constructs.includes(e.construct)));
    const s = summarise(sub);
    check(`${name}[${row.value}] k`, String(s.k) === String(row.n_studies), `${s.k} vs ${row.n_studies}`);
    check(`${name}[${row.value}] median`, fmt(s.median) === String(row.sl_median),
          `${fmt(s.median)} vs ${row.sl_median}`);
    check(`${name}[${row.value}] iqr`, s.iqr === row.sl_iqr, `${s.iqr} vs ${row.sl_iqr}`);
    rowsChecked++;
  }
}
console.log(`   ${rowsChecked} published rows reproduced from the shipped JSON`);

/* ═══ 6. the headline tiles ═══ */
section('headline');
const h = meta.headline;
for (const [key, construct] of [['EXPOSURE', 'EXPOSURE'], ['REACH', 'REACH'],
                                ['SHARING', 'SHARING'], ['CONTENT', 'CONTENT']]) {
  const s = summarise(MAIN.filter(e => e.construct === construct));
  check(`tile ${key} median`, h[key].median === s.median, `${h[key].median} vs ${s.median}`);
  check(`tile ${key} k`, h[key].k === s.k, `${h[key].k} vs ${s.k}`);
}
check('the contrast divides like with like',
      h.contrast === pyRound(h.RECALL_seen.median / h.REACH.median, 1));
check('concentration k is the top-1% studies, not all concentration studies',
      h.CONCENTRATION.k < summarise(MAIN.filter(e => e.construct === 'CONCENTRATION')).k,
      `${h.CONCENTRATION.k} vs ${summarise(MAIN.filter(e => e.construct === 'CONCENTRATION')).k}`);

/* ═══ 6b. the study list must be able to reproduce the published k ═══ */
section('study list reproduces k');
// The studies page counts studies per construct from the estimates. With its main-set toggle on
// those counts must equal the published k, or the same quantity reads two ways on two pages —
// which it did until 2026-09-18 (20 exposure studies there, 18 in the tile).
const byConstruct = Object.fromEntries(slices.by_construct.map(r => [r.value, r]));
for (const c of meta.construct_order) {
  const k = new Set(MAIN.filter(e => e.construct === c).map(e => e.id)).size;
  check(`study-list k for ${c}`, String(k) === byConstruct[c].n_studies,
        `${k} vs published ${byConstruct[c].n_studies}`);
}
check('main-set totals match the crosswalk',
      MAIN.length === meta.n_main_estimates &&
      new Set(MAIN.map(e => e.id)).size === meta.n_main_studies);

/* ═══ 7. record renderability ═══ */
section('records');
const longest = {};
for (const e of est) {
  for (const f of ['quote', 'denominator', 'definition', 'measure_type', 'moderator_quote', 'n_raw']) {
    if (e[f] && e[f].length > (longest[f]?.len ?? 0)) longest[f] = { len: e[f].length, eid: e.eid };
  }
}
check('no free-text field exceeds its 600-char cap',
      Object.values(longest).every(x => x.len <= 600),
      Object.entries(longest).map(([f, x]) => `${f}:${x.len}`).join(' '));
check('every main estimate has a denominator or a denom_scope',
      MAIN.every(e => e.denominator || e.denom_scope));
check('every estimate has a quote', est.every(e => e.quote));
check('every estimate has a construct in the known set',
      est.every(e => meta.construct_names[e.construct]),
      [...new Set(est.filter(e => !meta.construct_names[e.construct]).map(e => e.construct))].join(' '));
const noValue = est.filter(e => e.value === null || e.value === undefined);
check('estimates without a parsed value carry the raw string',
      noValue.every(e => e.value_raw), `${noValue.length} rows without a value`);
check('estimates without a value are never in the main set', noValue.every(e => !e.main));

/* ═══ 8. the URL codec ═══ */
section('url codec');
const roundTrip = sel => {
  const p = new URLSearchParams();
  for (const [f, on] of Object.entries(sel)) if (on.size) p.set(f, [...on].join(','));
  const back = {};
  for (const [k, v] of new URLSearchParams(p.toString()).entries()) {
    back[k] = new Set(v.split(',').filter(Boolean));
  }
  return JSON.stringify(Object.entries(back).map(([k, v]) => [k, [...v].sort()]).sort()) ===
         JSON.stringify(Object.entries(sel).map(([k, v]) => [k, [...v].sort()]).sort());
};
check('single filter round-trips', roundTrip({ construct: new Set(['EXPOSURE']) }));
check('multi-value round-trips', roundTrip({ ground_truth: new Set(['domain_list', 'fact_checker']) }));
check('many fields round-trip', roundTrip({
  construct: new Set(['CONTENT']), topic: new Set(['covid19', 'vaccines']),
  platform_norm: new Set(['Twitter/X']), breadth: new Set(['false', 'misleading']),
}));
// values containing the separator would break the codec silently
const withComma = meta.controls.flatMap(f =>
  [...new Set(est.map(e => e[f]).filter(Boolean))].filter(v => String(v).includes(',')));
check('no level contains a comma', withComma.length === 0, withComma.join(' | '));
const withAmp = meta.controls.flatMap(f =>
  [...new Set(est.map(e => e[f]).filter(Boolean))].filter(v => /[&#=]/.test(String(v))));
check('no level contains a URL-significant character', withAmp.length === 0, withAmp.join(' | '));

/* ═══ report ═══ */
console.log(`\n${'═'.repeat(60)}`);
if (failures.length) {
  console.log(`STRESS: ${fail} FAILURE(S) of ${pass + fail} checks\n`);
  for (const f of failures.slice(0, 40)) console.log('  ✗ ' + f);
  if (failures.length > 40) console.log(`  … and ${failures.length - 40} more`);
  process.exit(1);
}
console.log(`STRESS: ${pass}/${pass} checks pass`);
