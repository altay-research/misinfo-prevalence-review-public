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

/* Search is all-terms, not whole-string: the field order is author-then-title, so a substring
 * match on "Guess 2020" finds nothing even though both terms are there. Split and require each. */
export function matchesQuery(hay, q) {
  if (!q) return true;
  const h = hay.toLowerCase();
  return q.toLowerCase().split(/\s+/).filter(Boolean).every(t => h.includes(t));
}

export const plural = (n, one, many) => `${num(n)} ${n === 1 ? one : (many || one + 's')}`;

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

/* An estimate id in the hash of a page that does not handle estimate links. Older copied links
 * look like this; send them to the page that does rather than dropping them. */
export function rescueEstimateLink() {
  const h = location.hash.slice(1);
  if (!/^[0-9a-f]{7,}$/.test(h)) return false;
  location.replace(BASE + 'estimates/#' + h);
  return true;
}

export function mountChrome(current, meta) {
  const pages = [['', 'Overview'], ['explore/', 'Explore'], ['estimates/', 'Estimates'],
                 ['studies/', 'Studies'], ['descriptives/', 'Descriptives'], ['data/', 'Data']];
  const nav = pages.map(([href, name]) =>
    `<a href="${BASE}${href}"${href === current ? ' aria-current="page"' : ''}>${name}</a>`).join('');
  const main = document.querySelector('main.wrap');
  if (main && !main.id) main.id = 'main';
  document.body.insertAdjacentHTML('afterbegin',
    `<a class="skip" href="#main">Skip to content</a>
     <header class="top"><div class="wrap">
       <a class="brand" href="${BASE}">Misinformation prevalence</a>
       <nav class="main">${nav}</nav>
     </div></header>`);
  // the paper itself, added to the masthead once it exists
  if (meta && meta.preprint) {
    document.querySelector('nav.main').insertAdjacentHTML('beforeend',
      `<a class="paper" href="${meta.preprint}" target="_blank" rel="noopener">Read the paper &rarr;</a>`);
  }
}

/* Called once meta has loaded, for pages that mount their chrome before fetching. */
export function addPaperLink(meta) {
  const nav = document.querySelector('nav.main');
  if (!nav || !meta || !meta.preprint || nav.querySelector('.paper')) return;
  nav.insertAdjacentHTML('beforeend',
    `<a class="paper" href="${meta.preprint}" target="_blank" rel="noopener">Read the paper &rarr;</a>`);
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
         <a href="${submitStudyURL(meta.repo)}" target="_blank" rel="noopener">Send a comment</a></p>
    </div></footer>`);
}

/* A researcher who knows of a study the search missed needs somewhere to put it. Same mechanism as
 * flagging a coding error: a pre-filled public issue, dated, screenable, and not an inbox. */
export function submitStudyURL(repo) {
  const body = 'A study I missed, something coded wrongly, or any other comment:\n\n';
  return `https://github.com/${repo}/issues/new?labels=feedback&title=` +
    encodeURIComponent('') + '&body=' + encodeURIComponent(body);
}

/* The invitation to contribute. One component so it reads and behaves the same everywhere, and so
 * it is a button people can see rather than a link in a footer. */
export function mountContributeCTA(meta, target) {
  const host = target || document.querySelector('main.wrap');
  if (!host) return;
  host.insertAdjacentHTML('beforeend', `
    <section class="cta">
      <div class="t"><h2>If I've missed a study, or you have a comment</h2></div>
      ${meta.submit_endpoint
        ? `<button class="cta-btn" type="button" data-open-form>Tell me <span class="arw">&rarr;</span></button>`
        : `<a class="cta-btn" href="${submitStudyURL(meta.repo)}" target="_blank" rel="noopener">
             Tell me <span class="arw">&rarr;</span></a>`}
      <div class="cta-form" hidden></div>
    </section>`);

  const cta = host.querySelector('.cta:last-of-type');
  const opener = cta && cta.querySelector('[data-open-form]');
  if (opener) {
    opener.addEventListener('click', () => {
      const box = cta.querySelector('.cta-form');
      box.hidden = false;
      opener.hidden = true;
      box.innerHTML = submissionFormHTML(meta, 'missing-study');
      wireSubmissionForm(box, meta);
      box.querySelector('input, textarea')?.focus();
    });
  }
}


/* ---------- filter state in the URL ----------
 * A slice someone finds interesting should be something they can send to a colleague or cite.
 * The state is a plain query string in the hash: #construct=EXPOSURE&ground_truth=domain_list,
 * fact_checker. Unknown keys are ignored, so an old link never throws.
 */

export function encodeFilters(sel, extra = {}) {
  const p = new URLSearchParams();
  for (const [f, on] of Object.entries(sel)) {
    if (on && on.size) p.set(f, [...on].join(','));
  }
  for (const [k, v] of Object.entries(extra)) {
    if (v !== '' && v != null && v !== false) p.set(k, String(v));
  }
  return p.toString();
}

export function decodeFilters(fields) {
  const p = new URLSearchParams(location.hash.replace(/^#/, ''));
  const sel = {}, extra = {};
  for (const [k, v] of p.entries()) {
    if (fields.includes(k)) {
      const vals = v.split(',').filter(Boolean);
      if (vals.length) sel[k] = new Set(vals);
    } else {
      extra[k] = v;
    }
  }
  return { sel, extra };
}

/* Write without stacking history entries — a filter is not a page you go "back" from. */
export function writeFilters(sel, extra = {}) {
  const q = encodeFilters(sel, extra);
  history.replaceState(null, '', q ? '#' + q : location.pathname + location.search);
}

/* A button that copies the current address, with its filters, to the clipboard. */
export function wireShare(btn) {
  if (!btn) return;
  btn.addEventListener('click', () => {
    navigator.clipboard?.writeText(location.href);
    const was = btn.textContent;
    btn.textContent = 'link copied';
    setTimeout(() => { btn.textContent = was; }, 1400);
  });
}

/* ---------- the submission form ----------
 * Only shown when meta.submit_endpoint is set. Without it the site falls back to the GitHub issue
 * links, which work but need an account — which is the whole reason this exists. Submissions go to
 * a private triage repository: they are recommendations for the author, not public claims.
 */

const FIELDS = {
  'missing-study': [
    ['submission', 'Your message', 'textarea', true,
     "A study I missed, something coded wrongly, or any other comment. If it is a study, a DOI "
     + "and what it reports is enough."],
  ],
  coding: [
    ['estimate', 'Estimate identifier', 'input', true, 'The seven characters at the top right of the record'],
    ['issue', 'What looks wrong', 'textarea', true, 'Which field, and what the paper actually says'],
  ],
};

let turnstileLoaded = false;
function loadTurnstile(sitekey, host) {
  if (!sitekey) return;
  const render = () => window.turnstile && window.turnstile.render(host, { sitekey });
  if (turnstileLoaded) return render();
  turnstileLoaded = true;
  const sc = document.createElement('script');
  sc.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';
  sc.async = true;
  sc.onload = render;
  document.head.appendChild(sc);
}

export function submissionFormHTML(meta, kind = 'missing-study', prefill = {}) {
  const rows = FIELDS[kind].map(([name, label, tag, required, hint]) => {
    const attrs = `id="sf-${name}" name="${name}" placeholder="${esc(hint)}"${required ? ' required' : ''}`;
    const val = prefill[name] ? esc(prefill[name]) : '';
    const control = tag === 'textarea'
      ? `<textarea ${attrs} rows="${name === 'submission' ? 7 : 3}">${val}</textarea>`
      : `<input type="text" ${attrs} value="${val}">`;
    return `<label class="sf-row"><span>${esc(label)}${required ? ' <i>required</i>' : ''}</span>${control}</label>`;
  }).join('');
  return `<form class="sf" data-kind="${kind}" novalidate>
    ${rows}
    <label class="sf-row"><span>Your email <i>optional</i></span>
      <input type="email" id="sf-contact" name="contact" placeholder="Only so I can ask a follow-up"></label>
    <label class="sf-hp" aria-hidden="true"><span>Website</span><input type="text" name="website" tabindex="-1" autocomplete="off"></label>
    <div class="sf-row sf-check"><span>Confirm you are a person</span><div class="sf-turnstile"></div></div>
    <div class="sf-foot">
      <button type="submit" class="cta-btn">Send</button>
      <span class="sf-msg" role="status"></span>
    </div>
    <p class="sf-note">Goes to a private queue the author reads. Nothing is published.
      Prefer GitHub? <a href="${kind === 'coding' ? '#' : submitStudyURL(meta.repo)}" target="_blank" rel="noopener">Open an issue instead</a>.</p>
  </form>`;
}

export function wireSubmissionForm(root, meta, onDone) {
  const form = root.querySelector('form.sf');
  if (!form) return;
  loadTurnstile(meta.turnstile_sitekey, form.querySelector('.sf-turnstile'));
  form.addEventListener('submit', async ev => {
    ev.preventDefault();
    const msg = form.querySelector('.sf-msg');
    const btn = form.querySelector('button[type=submit]');
    const data = { kind: form.dataset.kind };
    for (const el of form.querySelectorAll('input, textarea')) {
      if (el.name) data[el.name] = el.value;
    }
    const missing = [...form.querySelectorAll('[required]')].filter(el => !el.value.trim());
    if (missing.length) {
      msg.textContent = 'Please fill the required fields.';
      msg.className = 'sf-msg bad';
      missing[0].focus();
      return;
    }
    const ts = form.querySelector('[name="cf-turnstile-response"]');
    data.turnstile = ts ? ts.value : '';
    // Turnstile escalates to a click-the-box challenge for anything it finds unusual. Posting
    // without a token just earns a rejection from the Worker, which reads as the form being
    // broken; point at the check instead.
    if (meta.turnstile_sitekey && !data.turnstile) {
      msg.textContent = form.querySelector('.sf-turnstile iframe')
        ? 'Please complete the check above.'
        : 'The bot check has not loaded. Use the GitHub link below instead.';
      msg.className = 'sf-msg bad';
      return;
    }
    btn.disabled = true;
    msg.className = 'sf-msg';
    msg.textContent = 'Sending…';
    try {
      const r = await fetch(meta.submit_endpoint, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(data),
      });
      const out = await r.json().catch(() => ({}));
      if (r.ok && out.ok) {
        form.innerHTML = '<p class="sf-done">Thank you — it has reached the author.</p>';
        if (onDone) onDone();
        return;
      }
      msg.textContent = out.error || 'Something went wrong. Please try again.';
      msg.className = 'sf-msg bad';
    } catch {
      msg.textContent = 'Could not reach the server. Please try again, or use the GitHub link.';
      msg.className = 'sf-msg bad';
    }
    btn.disabled = false;
    if (window.turnstile) window.turnstile.reset();
  });
}

/* ---------- the estimate record ---------- */

// value_raw sometimes carries the underlying counts ("1,304,827 of 3,619,091"). When it does,
// showing them is worth more than showing the percentage twice.
const COUNTS = /^\s*[\d,]+(\.\d+)?\s+of\s+[\d,]+/i;

const CODING_ORDER = [
  ['construct', e => constructName(e.construct), 'construct'],
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

  // Each coded field links to the chart that shows its levels, so a term the reader does not
  // know is one click from being defined rather than something to go hunting for.
  const coding = CODING_ORDER.map(([f, get]) => {
    const v = get(e);
    if (!v || v === 'not_reported' || v === '—') return '';
    const href = `${BASE}descriptives/#field-${f}`;
    return `<div><dt><a href="${href}">${esc(fieldLabel(f))}</a></dt><dd>${esc(v)}</dd></div>`;
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
      ${opts.endpoint
        ? `<button class="warn linky" type="button" data-flag="${esc(e.eid)}">⚠︎ flag a coding error</button>`
        : (issue ? `<a href="${esc(issue)}" target="_blank" rel="noopener" class="warn">⚠︎ flag a coding error</a>` : '')}
    </div>
  </article>`;
}

/* Delegated handler for the record's own buttons: copy-link, and flag-a-coding-error when the
 * submission endpoint exists (otherwise the flag is a plain link to GitHub). */
export function wireCopy(root = document, meta) {
  root.addEventListener('click', ev => {
    const flag = ev.target.closest('[data-flag]');
    if (flag && meta && meta.submit_endpoint) {
      const rec = flag.closest('.record');
      let box = rec.querySelector('.rec-form');
      if (!box) {
        rec.insertAdjacentHTML('beforeend', '<div class="rec-form"></div>');
        box = rec.querySelector('.rec-form');
        box.innerHTML = submissionFormHTML(meta, 'coding', { estimate: flag.dataset.flag });
        wireSubmissionForm(box, meta);
      }
      box.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      box.querySelector('textarea')?.focus();
      return;
    }
    const b = ev.target.closest('[data-copy]');
    if (!b) return;
    // Always the estimates page. Building this from location.pathname gave /explore/#<eid> or
    // /studies/#<eid> when the record was opened there, and those pages read a hash as filter
    // state, ignore an unknown key, then overwrite it — so the link silently went nowhere.
    const url = new URL(BASE + 'estimates/#' + b.dataset.copy, location.href).href;
    navigator.clipboard?.writeText(url);
    const was = b.textContent; b.textContent = 'copied';
    setTimeout(() => { b.textContent = was; }, 1200);
  });
}
