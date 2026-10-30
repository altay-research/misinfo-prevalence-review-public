/**
 * Submission proxy for the misinformation prevalence review.
 *
 * A static site cannot receive a POST, and a browser cannot hold a GitHub token. This Worker sits
 * between them: it takes what a reader types on the public site, checks it is not a bot, and files
 * it as an issue in a PRIVATE triage repository that only Sacha sees. Nothing public is written,
 * so a spam run cannot deface the review's own repository, and submissions stay what they are —
 * recommendations for the author, not public claims about the review.
 *
 * GET /health reports whether the submission path actually works. See health() below for why.
 *
 * Deploy:  wrangler deploy
 * Secrets: wrangler secret put GITHUB_TOKEN      (fine-grained PAT, Issues: read+write, on the
 *                                                 submissions repo ONLY)
 *          wrangler secret put TURNSTILE_SECRET  (Cloudflare Turnstile secret key)
 */

const MAX = { submission: 8000, contact: 200, estimate: 40, issue: 4000 };

const cors = origin => ({
  'access-control-allow-origin': origin,
  'access-control-allow-headers': 'content-type',
  'access-control-allow-methods': 'GET, POST, OPTIONS',
  'access-control-max-age': '86400',
});

const json = (obj, status = 200, origin = '*') => new Response(JSON.stringify(obj), {
  status,
  headers: { 'content-type': 'application/json', ...cors(origin) },
});

// A 204 must carry no body; json() would give it one and the Response constructor rejects that.
const noContent = origin => new Response(null, { status: 204, headers: cors(origin) });

const clean = (v, n) => String(v ?? '').replace(/[\x00-\x08\x0b\x0c\x0e-\x1f]/g, '').trim().slice(0, n);

async function verifyTurnstile(token, secret, ip) {
  if (!secret) return true;                       // unset only while testing locally
  const body = new FormData();
  body.append('secret', secret);
  body.append('response', token || '');
  if (ip) body.append('remoteip', ip);
  const r = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify',
                        { method: 'POST', body });
  const out = await r.json();
  return out.success === true;
}

/* Is the submission path actually working?
 *
 * It is otherwise unobservable. The form sits behind Turnstile, which is designed to stop exactly
 * the automated request that would test it, so neither the author nor an agent can exercise the
 * path end to end. A GitHub token that has expired therefore shows up only as a stranger's failed
 * submission, and nobody is told. That happened here: the token was issued on 2026-09-18 with
 * GitHub's 30-day default, and the first chance to notice would have been a message that never
 * arrived.
 *
 * This asks GitHub whether the token still works and reports the expiry date GitHub returns
 * alongside it, so the token can be replaced before it lapses rather than after. It reveals only
 * whether the backend is configured: never the token, the repository's contents, or any
 * submission.
 */
let healthMemo = { at: 0, body: null, status: 0 };

async function health(env, origin) {
  const ttl = Number(env.HEALTH_CACHE_SECONDS ?? 60) * 1000;
  // Only a healthy result is memoised, and only briefly. A failure is always re-checked, so the
  // answer to "is it broken right now" is never a stale yes or a stale no; the memo exists so that
  // hammering this route cannot burn the GitHub rate limit the submissions themselves depend on.
  if (healthMemo.body && Date.now() - healthMemo.at < ttl) {
    return json({ ...healthMemo.body, cached: true }, healthMemo.status, origin);
  }

  const out = {
    ok: false,
    github: 'unknown',
    token_expires: null,
    turnstile: env.TURNSTILE_SECRET ? 'configured' : 'missing',
    repo: env.SUBMISSIONS_REPO || null,
    checked: new Date().toISOString(),
  };
  if (!env.GITHUB_TOKEN) {
    out.github = 'missing';
    return json(out, 503, origin);
  }

  let r;
  try {
    r = await fetch(`https://api.github.com/repos/${env.SUBMISSIONS_REPO}`, {
      headers: {
        authorization: `Bearer ${env.GITHUB_TOKEN}`,
        accept: 'application/vnd.github+json',
        'user-agent': 'misinfo-prevalence-submissions',
      },
    });
  } catch {
    out.github = 'unreachable';
    return json(out, 503, origin);
  }

  // Fine-grained tokens carry their own expiry on every authenticated response, which is the
  // number worth watching: it turns "it broke twelve days ago" into "it expires in three weeks".
  out.token_expires = r.headers.get('github-authentication-token-expiration');
  if (r.status === 401) out.github = 'unauthorized';          // expired or revoked
  else if (r.status === 403) out.github = 'forbidden';        // lacks Issues access
  else if (r.status === 404) out.github = 'no-such-repo';     // wrong name, or invisible to it
  else if (!r.ok) out.github = `error-${r.status}`;
  else out.github = 'ok';

  out.ok = out.github === 'ok' && out.turnstile === 'configured';
  const status = out.ok ? 200 : 503;
  if (out.ok) healthMemo = { at: Date.now(), body: out, status };
  return json(out, status, origin);
}

export default {
  async fetch(request, env) {
    const allowed = (env.ALLOWED_ORIGIN || '').split(',').map(s => s.trim()).filter(Boolean);
    const origin = request.headers.get('origin') || '';
    const allowOrigin = allowed.length === 0 ? '*' : (allowed.includes(origin) ? origin : null);

    if (request.method === 'OPTIONS') return noContent(allowOrigin || 'null');
    // Readable from anywhere, deliberately: its whole purpose is to be checkable from a terminal,
    // and it says nothing a visitor to the public repository cannot already read.
    if (request.method === 'GET' && new URL(request.url).pathname === '/health') {
      return health(env, '*');
    }
    if (request.method !== 'POST') return json({ error: 'POST only' }, 405, allowOrigin || 'null');
    if (allowOrigin === null) return json({ error: 'origin not allowed' }, 403, 'null');

    let f;
    try {
      f = await request.json();
    } catch {
      return json({ error: 'expected JSON' }, 400, allowOrigin);
    }

    // Honeypot: a field hidden from people and irresistible to bots. Accept and discard, so the
    // bot sees success and does not retry with a different shape.
    if (clean(f.website, 100)) return json({ ok: true }, 200, allowOrigin);

    const ip = request.headers.get('cf-connecting-ip');
    if (!await verifyTurnstile(f.turnstile, env.TURNSTILE_SECRET, ip)) {
      return json({ error: 'could not verify that you are a person — please try again' }, 400, allowOrigin);
    }

    const kind = f.kind === 'coding' ? 'coding' : 'feedback';
    let title, body;

    if (kind === 'coding') {
      const estimate = clean(f.estimate, MAX.estimate);
      const issue = clean(f.issue, MAX.issue);
      if (!estimate || !issue) {
        return json({ error: 'the estimate id and what looks wrong are both needed' }, 400, allowOrigin);
      }
      title = `Coding query: ${estimate}`;
      body = [`**Estimate**: ${estimate}`, '', '**What looks wrong**', issue].join('\n');
    } else {
      // One open box: a missed study, a correction, or any other comment. The label says where it
      // came from; the title is simply the first line, so the queue reads like what people wrote.
      const submission = clean(f.submission, MAX.submission);
      if (!submission) {
        return json({ error: 'please write something' }, 400, allowOrigin);
      }
      const firstLine = submission.split('\n').find(l => l.trim()) || submission;
      title = firstLine.trim().slice(0, 80);
      body = submission;
    }

    const contact = clean(f.contact, MAX.contact);
    body += `\n\n---\n_Submitted through the public form${contact ? `, contact: ${contact}` : ', no contact given'}._`;

    const r = await fetch(`https://api.github.com/repos/${env.SUBMISSIONS_REPO}/issues`, {
      method: 'POST',
      headers: {
        authorization: `Bearer ${env.GITHUB_TOKEN}`,
        accept: 'application/vnd.github+json',
        'user-agent': 'misinfo-prevalence-submissions',
        'content-type': 'application/json',
      },
      body: JSON.stringify({ title, body, labels: [kind, 'unverified'] }),
    });

    if (!r.ok) {
      // Never leak the token or GitHub's error to the page; log it for `wrangler tail` instead.
      console.error('github error', r.status, await r.text());
      return json({ error: 'could not file the submission — please try again later' }, 502, allowOrigin);
    }
    return json({ ok: true }, 200, allowOrigin);
  },
};
