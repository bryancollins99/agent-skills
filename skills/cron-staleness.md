Audits every scheduled GitHub Actions workflow in a repo or org for silent death: not just failures, but crons that stopped firing while reporting nothing at all.

## Purpose

`gh run list --status failure` tells you what broke. It cannot tell you what stopped.

A scheduled workflow that never fires produces no failed runs, no red X, no notification. The dashboard is green because the dashboard only knows about runs that happened. On my own portfolio this hid a Netlify build check, a Core Web Vitals check and two link scrapers that had not fired in weeks. A weekly monitoring email had been arriving the whole time, reporting on checks that were not running.

The signal is not the run that failed. It is the run that should have happened and did not. That requires comparing each workflow's last successful run against the cadence its own cron expression promises, which nothing in the GitHub UI does for you.

Three specific ways a cron dies quietly:

- **GitHub disables schedules after 60 days of repository inactivity.** No email to the org, no run history entry. A stable repo that needs no commits is exactly the repo whose crons get switched off.
- **A workflow file renamed or moved** keeps its old run history under the old name and starts fresh under the new one, so recent-runs views look empty.
- **A secret expired.** Depending on where it is read, the job can exit 0 having done nothing.

## When to use

- Weekly or monthly on any repo with scheduled workflows you rely on but do not watch.
- Before trusting any automated report, dashboard or digest that a cron produces. Audit the checks before you audit their output.
- After a quiet period on a repo, or after a rename or secrets rotation.
- Whenever a monitoring email has looked healthy for a suspiciously long time.

Not useful on repos with no `schedule:` triggers. Push-triggered workflows fail loudly and need no staleness check.

## Steps

1. **Enumerate the scheduled workflows.** Do not keep a hand-maintained registry; it drifts the moment someone adds a workflow. Read the repo's own workflow files and keep the ones with a `schedule:` trigger:

   ```bash
   gh api repos/{owner}/{repo}/actions/workflows --jq '.workflows[] | {name, path, state, id}'
   ```

   Note the `state` field. `disabled_inactivity` is the 60-day auto-disable and is the single most valuable row in the output. Report it as a finding, not as a footnote.

2. **Derive the expected cadence from each workflow's own cron.** Read the `schedule.cron` expression out of the workflow file rather than asking the user how often it should run. Convert it to an expected interval in hours: `0 6 * * *` is 24, `0 6 * * 1` is 168, `0 6 1 * *` is roughly 730. The tolerance window should be about 1.5x the interval, so one skipped run flags but ordinary jitter does not.

3. **Get the last successful run per workflow.**

   ```bash
   gh api "repos/{owner}/{repo}/actions/workflows/{id}/runs?status=success&per_page=1" \
     --jq '.workflow_runs[0].updated_at // "none"'
   ```

   Do this per workflow rather than pulling the whole run list and grouping. It is one cheap call each and it does not silently truncate on a busy repo.

4. **Classify every workflow into exactly one bucket**, and sort the report in this order:

   - **DISABLED** - `state` is not `active`. Nothing will fire. Say which flavour, since `disabled_inactivity` is fixed with a click and `disabled_manually` was somebody's decision.
   - **FAILING** - latest run errored. Include the age of the last success, because a job failing for six weeks is a different problem from one that failed this morning.
   - **STALE** - no successful run inside the tolerance window, or no runs on record at all. This is the bucket the whole skill exists for.
   - **UNKNOWN** - the API call errored or timed out. Never fold these into OK.
   - **OK** - one summary count. Do not list them.

5. **Report with full clickable URLs**, one per finding:

   `https://github.com/{owner}/{repo}/actions/workflows/{workflow file}`

   A workflow name alone means opening the Actions tab and hunting. The URL means one click.

6. **State what you did not check.** Name it explicitly rather than letting the green count imply full coverage. This audit does not verify that a workflow which ran actually did its job, and step 5 of the failure modes below explains why that gap matters more than it sounds.

## Failure modes

- **"No runs on record" is not always death.** GitHub retains run history for about 90 days. On a monthly or quarterly workflow, an empty history often means the runs expired, not that the cron stopped. Flag it for a manual check and say which of the two you think it is. Raising it as a dead cron when it fired fine last month costs you trust in the whole report.

- **A workflow that has never run may be deliberate.** Read the workflow's own header and trigger block before calling it dead. Manual-dispatch-only workflows, disaster-recovery scripts and one-shot migrations all correctly show zero scheduled runs. I found seven zero-run workflows in one sweep and every single one was intentional.

- **A green run does not mean the work happened.** This audit checks that a workflow ran and exited 0. A job whose API call returned an empty list, whose credentials silently expired, or whose script guarded on a directory that no longer exists will exit 0 having done nothing at all. If the workflow produces an artefact, a commit, a file or a row, assert on that artefact's freshness too. An empty result and a successful run look identical from the outside.

- **Do not stop at the checks and skip their output.** The inverse trap is just as expensive. If a monitoring workflow emails or files a report, read one and ask whether a human can act on it. A report nobody reads and a check that never fires produce the same outcome, and both of them feel fine from the inbox.

- **Retire a healthcheck together with the thing it watches.** A staleness checker pointed at a workflow that was deliberately deleted files false alarms forever, and false alarms are how you learn to ignore the real ones.

- **Do not fix inside the audit.** Report, then let the operator decide. A cron that stopped firing on purpose looks exactly like one that died, and only the person who turned it off knows which it was.
