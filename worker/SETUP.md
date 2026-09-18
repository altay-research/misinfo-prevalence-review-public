# Turning on the submission form

Right now the site falls back to GitHub issue links, which work but require the visitor to have a
GitHub account. These steps replace that with a form anyone can use. Submissions land as issues in
the **private** repo `altay-research/misinfo-prevalence-submissions`, which only you can see —
they are recommendations for you, not public claims about the review.

Everything is written and tested (`node worker/test.mjs`, 23 checks). What remains needs your
accounts, which is why it is not already done.

---

## 1. A GitHub token for the Worker  (~2 minutes)

github.com → Settings → Developer settings → **Fine-grained personal access tokens** → Generate new.

- **Resource owner**: `altay-research`
- **Repository access**: Only select repositories → `misinfo-prevalence-submissions`
- **Permissions**: Repository permissions → **Issues: Read and write**. Nothing else.
- **Expiration**: a year is reasonable; the form stops working silently when it lapses, so put a
  reminder somewhere.

Copy the token. It is shown once.

Scoped this narrowly, the worst a leak can do is file issues in a private repo that exists to
receive them. It cannot touch the review's own repository.

## 2. Turnstile, so the endpoint is not a spam faucet  (~2 minutes)

dash.cloudflare.com → **Turnstile** → Add site.

- **Domain**: `altay-research.github.io` (add your own domain too when it exists)
- **Widget mode**: Managed

You get a **site key** (public, goes in the page) and a **secret key** (goes in the Worker).

## 3. Deploy the Worker  (~3 minutes)

```bash
cd worker
npx wrangler login                    # opens a browser
npx wrangler deploy                   # prints the endpoint URL
npx wrangler secret put GITHUB_TOKEN       # paste the token from step 1
npx wrangler secret put TURNSTILE_SECRET   # paste the secret key from step 2
```

`wrangler deploy` prints something like
`https://misinfo-prevalence-submit.<your-subdomain>.workers.dev`. Keep it for the next step.

## 4. Point the site at it  (~1 minute)

In `scripts/build_site.py`:

```python
SUBMIT_ENDPOINT   = "https://misinfo-prevalence-submit.<your-subdomain>.workers.dev"
TURNSTILE_SITEKEY = "0x4AAAAAAA..."          # the site key from step 2
```

Then:

```bash
python3 scripts/build_site.py
python3 scripts/check_site.py
python3 scripts/build_public_package.py --force
cd ~/Desktop/Claude/Random/misinfo-prevalence-review-public && git add -A && git commit -m "Turn on the submission form" && git push
```

The form appears on every page in place of the GitHub button. The GitHub route stays available as
a link under the form for people who prefer it.

## 5. Check it once, from a logged-out browser

Open the site in a private window, submit something, and confirm it arrives:

```bash
gh issue list -R altay-research/misinfo-prevalence-submissions
```

Then delete the test: `gh issue delete 1 -R altay-research/misinfo-prevalence-submissions --yes`

---

## What arrives, and what to do with it

Every submission is an issue labelled `unverified`, plus `missing-study` or `coding`. The body
carries exactly what was typed, and the submitter's email if they gave one. Nothing is published
and nothing enters the dataset automatically — a submission is a lead, and it goes through the
same eligibility criteria as everything else, or it does not.

Triage by closing what does not qualify and keeping what does. If a submission does change the
corpus, that is a re-freeze, with its own entry in `FROZEN.md` and `research_log.md`, like any
other change.

## If it stops working

- `npx wrangler tail` streams the Worker's logs live. A GitHub failure is logged there and never
  shown to the submitter.
- The commonest cause is the token expiring. Re-issue it and `wrangler secret put GITHUB_TOKEN`
  again; no redeploy needed.
- Set `SUBMIT_ENDPOINT = None` and rebuild to fall back to GitHub links at any time.

## Cost

Cloudflare Workers' free tier is 100,000 requests a day. A form on an academic companion site will
not approach it.
