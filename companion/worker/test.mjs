/**
 * worker/test.mjs — exercise the submission Worker without deploying it.
 *
 *   node worker/test.mjs
 *
 * GitHub and Turnstile are stubbed, so this checks the parts that are ours: origin allow-listing,
 * required fields, the honeypot, field truncation, the shape of the issue that gets filed, that a
 * GitHub failure never leaks upstream detail to the page, and that /health reports the state of
 * the submission path without leaking the token.
 */
import worker from './index.js';

const ENV = {
  SUBMISSIONS_REPO: 'altay-research/misinfo-prevalence-submissions',
  ALLOWED_ORIGIN: 'https://altay-research.github.io',
  GITHUB_TOKEN: 'test-token',
  TURNSTILE_SECRET: '',            // unset -> verification skipped, as in local testing
};

let filed = [];
let githubStatus = 201;
let repoStatus = 200;                 // what GET /repos/<repo> returns, for the health route
let repoExpiry = '2026-11-18 00:00:00 UTC';
const realFetch = globalThis.fetch;
globalThis.fetch = async (url, opts) => {
  if (String(url).includes('api.github.com')) {
    // the health route reads the repo; a submission posts an issue
    if (!opts || opts.method !== 'POST') {
      const h = repoExpiry ? { 'github-authentication-token-expiration': repoExpiry } : {};
      return new Response(repoStatus === 200 ? '{}' : 'nope', { status: repoStatus, headers: h });
    }
    filed.push({ auth: opts.headers.authorization, ...JSON.parse(opts.body) });
    return new Response(githubStatus === 201 ? '{}' : 'boom', { status: githubStatus });
  }
  return realFetch(url, opts);
};

const post = (body, origin = ENV.ALLOWED_ORIGIN) =>
  worker.fetch(new Request('https://x/', {
    method: 'POST',
    headers: { 'content-type': 'application/json', origin },
    body: JSON.stringify(body),
  }), ENV);

let pass = 0, fail = 0;
const check = (name, ok, detail = '') => {
  if (ok) { pass++; } else { fail++; console.log(`  FAIL  ${name}${detail ? ' — ' + detail : ''}`); }
};

const GOOD = { kind: 'feedback',
               submission: 'Grinberg et al. 2019, Science, 10.1126/science.aau2706\n' +
                           'fake news was 6.7% of political links shared, out of all political ' +
                           'links shared by the panel (Table 2). US, Twitter, 2016.',
               contact: 'someone@example.edu' };

// --- a good submission
filed = [];
let r = await post(GOOD);
let out = await r.json();
check('good submission returns ok', r.status === 200 && out.ok === true, JSON.stringify(out));
check('one issue filed', filed.length === 1);
check('title is the first line', filed[0]?.title === 'Grinberg et al. 2019, Science, 10.1126/science.aau2706');
check('labels are kind + unverified',
      JSON.stringify(filed[0]?.labels) === JSON.stringify(['feedback', 'unverified']));
check('body carries the text verbatim',
      ['10.1126', '6.7%', 'all political links', 'Table 2', 'US, Twitter'].every(t => filed[0]?.body.includes(t)));
check('contact is recorded', filed[0]?.body.includes('someone@example.edu'));
check('token is sent as a bearer', filed[0]?.auth === 'Bearer test-token');

// --- missing required fields
filed = [];
r = await post({ kind: 'feedback', submission: '' });
check('an empty submission is rejected', r.status === 400 && filed.length === 0);
r = await post({ kind: 'feedback', submission: '   \n  ' });
check('whitespace only is rejected', r.status === 400 && filed.length === 0);

// --- coding queries
filed = [];
r = await post({ kind: 'coding', estimate: 'edd2e76', issue: 'the denominator is the news diet, not all media' });
check('coding query files', (await r.json()).ok === true && filed.length === 1);
check('coding title carries the id', filed[0]?.title === 'Coding query: edd2e76');
check('coding labels', JSON.stringify(filed[0]?.labels) === JSON.stringify(['coding', 'unverified']));
filed = [];
r = await post({ kind: 'coding', estimate: '', issue: 'x' });
check('coding without an id is rejected', r.status === 400 && filed.length === 0);

// --- honeypot: accepted, silently discarded
filed = [];
r = await post({ ...GOOD, website: 'http://spam.example' });
check('honeypot looks successful', (await r.json()).ok === true);
check('honeypot files nothing', filed.length === 0);

// --- origin allow-listing
r = await post(GOOD, 'https://evil.example');
check('foreign origin is refused', r.status === 403);
r = await worker.fetch(new Request('https://x/', { method: 'GET', headers: { origin: ENV.ALLOWED_ORIGIN } }), ENV);
check('GET is refused', r.status === 405);
r = await worker.fetch(new Request('https://x/', { method: 'OPTIONS', headers: { origin: ENV.ALLOWED_ORIGIN } }), ENV);
check('preflight is allowed', r.status === 204 &&
      r.headers.get('access-control-allow-origin') === ENV.ALLOWED_ORIGIN);

// --- oversized input is truncated, not rejected or passed through
filed = [];
await post({ ...GOOD, submission: 'x'.repeat(50000) });
check('long fields are truncated', filed[0] && filed[0].body.length < 12000, `${filed[0]?.body.length} chars`);

// --- control characters are stripped
filed = [];
const NUL = String.fromCharCode(0), BEL = String.fromCharCode(7);
await post({ ...GOOD, submission: `a${NUL}b${BEL}c` });
check('control characters are stripped',
      filed[0] && filed[0].body.includes('abc') &&
      !filed[0].body.includes(NUL) && !filed[0].body.includes(BEL));

// --- a GitHub failure must not leak upstream detail
filed = []; githubStatus = 500;
r = await post(GOOD);
out = await r.json();
check('github failure returns 502', r.status === 502);
check('github failure leaks nothing', !JSON.stringify(out).includes('boom') && !JSON.stringify(out).includes('test-token'),
      JSON.stringify(out));
githubStatus = 201;

// --- malformed body
r = await worker.fetch(new Request('https://x/', {
  method: 'POST', headers: { 'content-type': 'application/json', origin: ENV.ALLOWED_ORIGIN },
  body: 'not json',
}), ENV);
check('malformed JSON is rejected', r.status === 400);

// --- /health: the submission path's only observable
// Turnstile is deliberately unset in ENV above (local testing), so health must report that and
// refuse to call itself ok, even when GitHub is fine.
const HENV = { ...ENV, HEALTH_CACHE_SECONDS: '0' };   // no memo, so each case is checked afresh
const getHealth = (env = HENV) =>
  worker.fetch(new Request('https://x/health', { method: 'GET' }), env);

repoStatus = 200;
r = await getHealth();
out = await r.json();
check('health reports github ok', out.github === 'ok', JSON.stringify(out));
check('health reports the token expiry', out.token_expires === repoExpiry);
check('health names the repo', out.repo === ENV.SUBMISSIONS_REPO);
check('health is not ok while turnstile is unset', out.ok === false && out.turnstile === 'missing');
check('an unhealthy path answers 503', r.status === 503);
check('health never leaks the token', !JSON.stringify(out).includes('test-token'));

// with Turnstile configured too, the whole path is healthy
r = await getHealth({ ...HENV, TURNSTILE_SECRET: 'sekrit' });
out = await r.json();
check('health is ok when both halves are configured', r.status === 200 && out.ok === true,
      JSON.stringify(out));
check('health never leaks the turnstile secret', !JSON.stringify(out).includes('sekrit'));

// an expired or revoked token is the case this route exists for
repoStatus = 401;
r = await getHealth({ ...HENV, TURNSTILE_SECRET: 'sekrit' });
out = await r.json();
check('an expired token reads as unauthorized', out.github === 'unauthorized' && out.ok === false);
check('an expired token answers 503', r.status === 503);
check('github error text does not reach the page', !JSON.stringify(out).includes('nope'));

repoStatus = 404;
out = await (await getHealth()).json();
check('a wrong repo name is named as such', out.github === 'no-such-repo');
repoStatus = 500;
out = await (await getHealth()).json();
check('an upstream fault is reported with its status', out.github === 'error-500');

// a missing token must not look healthy
out = await (await getHealth({ ...HENV, GITHUB_TOKEN: '' })).json();
check('a missing token reads as missing', out.github === 'missing' && out.ok === false);
repoStatus = 200;

// the memo: a healthy answer is reused briefly, so this route cannot burn the GitHub rate limit
const MENV = { ...ENV, TURNSTILE_SECRET: 'sekrit', HEALTH_CACHE_SECONDS: '60' };
await getHealth(MENV);                       // populate
out = await (await getHealth(MENV)).json();
check('a healthy answer is memoised', out.cached === true);

// health must not disturb the rest of the routing
r = await worker.fetch(new Request('https://x/', { method: 'GET', headers: { origin: ENV.ALLOWED_ORIGIN } }), ENV);
check('GET on any other path is still refused', r.status === 405);
filed = [];
r = await post(GOOD);
check('submissions still work after a health check', (await r.json()).ok === true && filed.length === 1);

console.log(`\nworker: ${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
