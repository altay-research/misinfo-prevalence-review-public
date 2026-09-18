/* site.js — shared data loading, labelling, and the estimate record.
 * The record is the unit the whole site is organised around: /explore/, /estimates/ and /studies/
 * all render this same component, so an estimate never appears one way in one place and another
 * way somewhere else. */

const BASE = (() => {
  // resolve site root from this module's own URL, so every page works at any subpath
  const u = new URL(import.meta.url);
  return u.href.replace(/assets\/site\.js.*$/, '');
})();

const j = async n => (await fetch(BASE + 'data/' + n)).json();

/* meta.json is 7 KB; estimates.json is 2 MB. The overview and the data page need only the first,
 * so the estimate payload is fetched on request rather than on every page load. */
let _meta = null;
export async function meta() {
  return (_meta = _meta || j('meta.json').then(m => (setMeta(m), m)));
}

let _data = null;
export async function data() {
  if (_data) return _data;
  const [m, estimates, studies, slices] = await Promise.all(
    [meta(), j('estimates.json'), j('studies.json'), j('slices.json')]);
  const byEid = new Map(estimates.map(e => [e.eid, e]));
  const byStudy = new Map();
  for (const e of estimates) {
    let a = byStudy.get(e.id); if (!a) byStudy.set(e.id, a = []); a.push(e);
  }
  return (_data = { meta: m, estimates, studies, slices, byEid, byStudy, base: BASE });
}

export const num = n => Number(n).toLocaleString('en-US');
export const esc = s => String(s == null ? '' : s)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

let META = null;
export function setMeta(m) { META = m; }
export function fieldLabel(f) { return (META && META.labels[f]) || f.replace(/_/g, ' '); }
export function valueLabel(v, field) {
  if (v === '' || v == null) return '—';
  const byField = field && META && META.field_value_labels[field];
  return (byField && byField[v]) || (META && META.value_labels[v]) || humanise(v);
}
// Coded levels are snake_case in the data. Anything without an explicit label still has to read
// as English on a public page, so underscores become spaces rather than shipping `web_cross_platform`.
export const humanise = v => {
  const t = String(v ?? '').replace(/_/g, ' ').trim();
  return t === 'NR' ? 'not reported' : t;          // the extraction's marker for a missing value
};

/* Truncate on a word boundary, with an ellipsis, so a table cell never ends mid-word. */
export function clip(s, n) {
  const t = String(s ?? '');
  if (t.length <= n) return t;
  const cut = t.slice(0, n);
  const sp = cut.lastIndexOf(' ');
  return (sp > n * 0.6 ? cut.slice(0, sp) : cut).replace(/[,;:]$/, '') + '…';
}
export function constructName(c) {
  return (META && META.construct_names[c]) || String(c || '').toLowerCase();
}

export function mountChrome(current) {
  const pages = [['', 'Overview'], ['explore/', 'Explore'], ['estimates/', 'Estimates'],
                 ['studies/', 'Studies'], ['descriptives/', 'Descriptives'], ['data/', 'Data']];
  const nav = pages.map(([href, name]) =>
    `<a href="${BASE}${href}"${href === current ? ' aria-current="page"' : ''}>${name}</a>`).join('');
  document.body.insertAdjacentHTML('afterbegin',
    `<header class="top"><div class="wrap">
       <a class="brand" href="${BASE}">Misinformation prevalence</a>
       <nav class="main">${nav}</nav>
     </div></header>`);
}

export function mountFooter(meta) {
  document.body.insertAdjacentHTML('beforeend',
    `<footer class="site"><div class="wrap">
      <p>Systematic review of misinformation prevalence, exposure and concentration ·
         ${num(meta.n_estimates)} estimates from ${meta.n_studies} studies ·
         frozen dataset <code>${esc(meta.freeze)}</code> (MD5 <code>${esc(meta.freeze_md5.slice(0, 12))}…</code>) ·
         built ${esc(meta.built)}</p>
      <p>Every number on this site is generated from the frozen dataset by
         <code>scripts/build_site.py</code> and checked by <code>scripts/check_site.py</code>.
         <a href="${BASE}data/">Download the data</a> ·
         <a href="${submitStudyURL(meta.repo)}" target="_blank" rel="noopener">Submit a study we missed</a></p>
    </div></footer>`);
}

/* A researcher who knows of a study the search missed needs somewhere to put it. Same mechanism as
 * flagging a coding error: a pre-filled public issue, dated, screenable, and not an inbox. */
export function submitStudyURL(repo) {
  const body = [
    '**Reference** (DOI or full citation):', '',
    '**What it reports** — the quantity in the paper\'s own words, and the number:', '',
    '**Out of what** — the denominator that number is a share of:', '',
    '**Where in the paper** (table, figure or page):', '',
    '**Anything else** (country, platform, when the data were collected):', '',
  ].join('\n');
  return `https://github.com/${repo}/issues/new?labels=missing-study&title=` +
    encodeURIComponent('Missing study: ') + '&body=' + encodeURIComponent(body);
}

/* The invitation to contribute. One component so it reads and behaves the same everywhere, and so
 * it is a button people can see rather than a link in a footer. */
export function mountContributeCTA(meta, target) {
  const host = target || document.querySelector('main.wrap');
  if (!host) return;
  host.insertAdjacentHTML('beforeend', `
    <section class="cta">
      <div class="t"><h2>Know a study we missed?</h2></div>
      <a class="cta-btn" href="${submitStudyURL(meta.repo)}" target="_blank" rel="noopener">
        Submit a study <span class="arw">&rarr;</span></a>
    </section>`);
}

/* ---------- the estimate record ---------- */

// value_raw sometimes carries the underlying counts ("1,304,827 of 3,619,091"). When it does,
// showing them is worth more than showing the percentage twice.
const COUNTS = /^\s*[\d,]+(\.\d+)?\s+of\s+[\d,]+/i;

const CODING_ORDER = [
  ['construct', e => constructName(e.construct)],
  ['measurement', e => valueLabel(e.measurement, 'measurement')],
  ['classification_level', e => valueLabel(e.classification_level, 'classification_level')],
  ['ground_truth', e => valueLabel(e.ground_truth, 'ground_truth')],
  ['breadth', e => valueLabel(e.breadth, 'breadth')],
  ['denom_class', e => valueLabel(e.denom_class, 'denom_class')],
  ['sampling_frame', e => valueLabel(e.sampling_frame, 'sampling_frame')],
  ['platform', e => valueLabel(e.platform_norm || e.platform, 'platform')],
  ['country', e => humanise(e.country)],
  ['country_scope', e => valueLabel(e.country_scope, 'country_scope')],
  ['unit', e => valueLabel(e.unit, 'unit')],
  ['date', e => e.date],
  ['n_raw', e => e.n_raw],
];

export function recordHTML(e, studies, opts = {}) {
  const st = studies[e.id] || {};
  const flags = [];
  if (!e.main) {
    flags.push(e.demographic_group
      ? `demographic subgroup — excluded from the pooled statistics`
      : `not in the main analysis set (${valueLabel(e.value_kind)})`);
  }
  if (e.demographic_group) flags.push(esc(e.demographic_group));
  if (e.confidence && e.confidence !== 'high') flags.push(`extraction confidence: ${esc(e.confidence)}`);

  const val = e.value != null ? `${e.value}%` : esc(e.value_raw || '—');
  // 441 of the frozen misinfo_def values are exactly 200 characters, cut at extraction and usually
  // mid-word. Saying so beats rendering a half-sentence as if it were the study's whole definition.
  const defTrunc = e.definition && e.definition.length >= 200 && !/[.!?"'\)]\s*$/.test(e.definition);
  // Some rows repeat the definition in the moderator quote; showing it twice is noise.
  const modQuote = e.moderator_quote &&
    !(e.definition || '').startsWith(e.moderator_quote.slice(0, 60)) &&
    !(e.moderator_quote || '').startsWith((e.definition || '').slice(0, 60))
    ? e.moderator_quote : null;
  const counts = e.value_raw && COUNTS.test(e.value_raw) && e.value != null ? e.value_raw : null;

  const coding = CODING_ORDER.map(([f, get]) => {
    const v = get(e);
    if (!v || v === 'not_reported' || v === '—') return '';
    return `<div><dt>${esc(fieldLabel(f))}</dt><dd>${esc(v)}</dd></div>`;
  }).join('');

  const conc = e.conc_share_pct
    ? `<div class="rout"><span class="lab">Concentration</span><span class="d">the top
         <strong>${esc(e.conc_group_pct)}%</strong> of ${esc(e.conc_unit || 'users')} account for
         <strong>${esc(e.conc_share_pct)}%</strong> of ${esc(e.conc_dimension || 'activity')}</span></div>`
    : '';

  const others = (opts.siblings || 0) - 1;
  const issue = opts.repo ? `https://github.com/${opts.repo}/issues/new?labels=coding&title=` +
    encodeURIComponent(`Coding query: ${e.eid} (${e.id})`) + '&body=' + encodeURIComponent(
      `Estimate: ${e.eid}\nStudy: ${st.author || e.id} ${st.year || ''} — ${st.title || e.title || ''}\n` +
      `Value: ${val}\nConstruct: ${e.construct}\nGround truth: ${e.ground_truth}\n` +
      `Judged at: ${e.classification_level}\nBreadth: ${e.breadth}\nDenominator: ${e.denominator || ''}\n\n` +
      `What looks wrong, and what the paper actually says:\n\n`) : null;

  return `<article class="record" id="${esc(e.eid)}">
    <div class="rhead">
      <span class="rval">${esc(val)}</span>
      <span class="rcon">${esc(constructName(e.construct))}</span>
      <span class="rid">${esc(e.eid)}</span>
    </div>
    ${flags.length ? `<div class="flags">${flags.map(f =>
        `<span class="badge flag">${f}</span>`).join('')}</div>` : ''}
    <div class="rout">
      <span class="lab">Out of</span>
      <span class="d">${esc(e.denominator || valueLabel(e.denom_scope))}</span>
      ${counts ? `<div class="small muted" style="margin-top:6px">counts as reported: <span class="num">${esc(counts)}</span></div>` : ''}
    </div>
    ${conc}
    ${e.quote ? `<blockquote class="q"><span class="lab">Quoted from the paper</span>${esc(e.quote)}</blockquote>` : ''}
    ${modQuote ? `<blockquote class="q mod"><span class="lab">Why it is coded this way</span>${esc(modQuote)}</blockquote>` : ''}
    ${e.definition ? `<div class="rout" style="padding-top:16px"><span class="lab">Misinformation defined as</span><span class="d small">${esc(e.definition)}${defTrunc ? '<span class="trunc"> … (truncated in the extraction)</span>' : ''}</span></div>` : ''}
    <div class="rstudy">
      <div class="t">${esc(st.title || e.title || e.id)}</div>
      <div class="m">${esc([st.author, st.year, st.venue].filter(Boolean).join(' · '))}
        ${st.doi ? ` · <a href="https://doi.org/${esc(st.doi)}" target="_blank" rel="noopener">doi.org/${esc(st.doi)}</a>` : ''}
        ${st.rob ? ` · <span class="badge ${esc(st.rob)}">risk of bias: ${esc(st.rob.toLowerCase())}</span>` : ''}
      </div>
    </div>
    <dl class="coding">${coding}</dl>
    <div class="rfoot">
      <button class="btn" data-copy="${esc(e.eid)}">copy link to this estimate</button>
      ${others > 0 ? `<a href="${BASE}studies/#${esc(e.id)}">${others} other estimate${others > 1 ? 's' : ''} from this study</a>` : ''}
      ${issue ? `<a href="${esc(issue)}" target="_blank" rel="noopener" class="warn">⚠︎ flag a coding error</a>` : ''}
    </div>
  </article>`;
}

/* Delegated handler for every "copy link" button on a page. */
export function wireCopy(root = document) {
  root.addEventListener('click', ev => {
    const b = ev.target.closest('[data-copy]');
    if (!b) return;
    const url = location.origin + location.pathname + '#' + b.dataset.copy;
    navigator.clipboard?.writeText(url);
    const was = b.textContent; b.textContent = 'copied';
    setTimeout(() => { b.textContent = was; }, 1200);
  });
}
