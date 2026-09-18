/**
 * worker/test.mjs — exercise the submission Worker without deploying it.
 *
 *   node worker/test.mjs
 *
 * GitHub and Turnstile are stubbed, so this checks the parts that are ours: origin allow-listing,
 * required fields, the honeypot, field truncation, the shape of the issue that gets filed, and
 * that a GitHub failure never leaks upstream detail to the page.
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
const realFetch = globalThis.fetch;
globalThis.fetch = async (url, opts) => {
  if (String(url).includes('api.github.com')) {
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

console.log(`\nworker: ${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
