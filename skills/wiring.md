Compare the secrets and env vars your code declares against what is actually set on GitHub Actions and Netlify. Catches the green-workflow, green-deploy, variable-simply-absent defect that no status page shows.

# /wiring - is the plumbing actually connected?

## Purpose

A site could not send email for months. The mail API key was set and valid, so every surface-level check passed. But three other variables the send function needed were never added, so three scheduled digests never went out and the unsubscribe check failed open. Ten form submissions got silence.

Nothing in a workflow-failure audit, a deploy-status check or an uptime monitor can see that class of defect: the workflow runs, the deploy is green, the variable is simply absent. This skill is the check for it. Run it after any launch, and before saying a flow is live.

## When to use

- After adding any integration that reads a secret or env var (email, payments, analytics, an API key).
- Before telling anyone a scheduled job or serverless function is live.
- When a function "works locally" and silently does nothing in production.

## Steps

1. From the repo checkout, run the helper. It needs the `gh` CLI (authed) for the GitHub side and the `netlify` CLI (authed) for the Netlify side; either side degrades to UNKNOWN rather than guessing.

   ```bash
   python3 scripts/wiring.py .                       # repo from `gh repo view`, site from .netlify/state.json
   python3 scripts/wiring.py . --repo owner/name --netlify-site <site_id>
   ```

   It derives the required set from the code every run. There is deliberately no hand-maintained registry of required vars, because those drift:

   | Side | Declared | Actually set |
   |---|---|---|
   | GitHub Actions | `secrets.X` in `.github/workflows/*` | repo secrets plus org secrets |
   | Netlify runtime | `process.env.X` / `import.meta.env.X` in `netlify/`, `src/`, `functions/`, `edge-functions/` | `getEnvVars`, production context only |

2. Report. Lead with **GH SECRET MISSING** and **NETLIFY ENV MISSING**; those are live defects. Then **NETLIFY ENV NOT ON PRODUCTION**, then **UNKNOWN**. Give one clickable line per side:

   - GitHub secrets: `https://github.com/{repo}/settings/secrets/actions`
   - Netlify env: `https://app.netlify.com/sites/{site name}/settings/env`

3. For every missing var, say **what breaks**. Trace it to the workflow or function that references it. "NETLIFY_ACCESS_TOKEN missing" is not actionable; "the three scheduled digests in `send-digest.yml` cannot authenticate, so they have never sent" is.

4. Anything not verified against the API gets an `UNVERIFIED:` prefix.

## Failure modes

These are encoded in the script. Do not work around them.

- **Never read `netlify env:list --plain` as truth.** It prints secret-scoped vars as `KEY=` with an empty value. That is redaction, not absence, and reading it as absence is how a valid key got wrongly called empty. The script uses the `getEnvVars` API, which reports real value presence.
- **A var set only on deploy-preview or branch-deploy is not wired.** It reads as present in the dashboard and fails in production. Only `all` and `production` contexts count; anything else lands in NOT ON PRODUCTION.
- **`gh secret list --org` returns 403 without org-admin.** Org secrets are still visible per repo via `repos/{repo}/actions/organization-secrets`, which needs only repo read. Skipping that reports every org-inherited secret as missing.
- **If either lookup fails, no diff is run for that side.** A partial "available" set makes every unseen secret look missing. UNKNOWN is the honest answer.
- **Some absences are correct.** Add them to `INTENTIONAL` in the script with a written reason. Example: when a platform AI gateway is in use, a user-set provider key switches the gateway off, so its absence is the wired state. An unexplained suppression is worse than a false positive.
- **`scripts/` is excluded from the Netlify scan.** Those run in GitHub Actions; including them reported every cron key as a missing Netlify var.
- **A guarded reference is not a defect.** `process.env.X || 'default'`, `?? y`, a ternary, or `=== 'true'` all work when unset. Those land in the "probably fine" line, not in MISSING.
