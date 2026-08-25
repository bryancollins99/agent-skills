Lists merged + stale local branches, deletes safe ones, flags the rest. Never main/master/release. Optionally cleans corresponding remote branches.

## Purpose

Keep local + remote branches tidy after shipping. Verifies merge state externally via `gh pr list` so it works in repos that squash-merge (where `git branch -d` refuses even though the PR is closed and merged).

## When to use

- After merging 3+ PRs in a week
- When `git branch` output spills past one screen
- As monthly hygiene
- Whenever automatic branch deletion has not been catching everything, for example branches whose PRs squash-merged before auto-delete-on-merge was switched on

Skip when: mid-feature with unpushed work on sibling branches, or shared repos where collaborators may still be using stale-looking branches.

## Steps

1. **Prerequisite checks.** If no remote configured, stop. If `gh auth status` fails, stop (the skill needs gh to verify PR state).
2. **Fetch + prune.** `git fetch --prune origin --quiet`. If this fails (network/auth), stop.
3. **Pull PR data.** `gh pr list --state all --json number,headRefName,state --limit 500` - get every PR with its head branch + state. Repos with >500 PRs need `--limit` raised.
4. **Classify every local branch:**
 - **Protected** (skip always): `main`, `master`, `develop`, `staging`, branches matching `release/*`
 - **No upstream** (skip, surface): never pushed; might be local-only WIP - manual review
 - **Open PR**: branch's PR is OPEN - preserve
 - **Merged PR + `[gone]` upstream**: PR merged AND remote already auto-deleted - safest deletion target
 - **Merged PR + live upstream**: PR squash-merged but remote-delete didn't happen (auto-delete-on-merge was off, or PR predates the setting) - also safe to delete locally; offer to delete remote too
 - **No PR record**: branch was pushed but no PR was opened - surface for manual review
 - **Unusual states** (closed-not-merged, etc.): surface for manual review
5. **Worktree map.** `git worktree list --porcelain` to find worktrees holding to-delete branches. Parse the lock-pid from any `locked …pid N` reason. If pid is alive (`os.kill(pid, 0)`), the worktree belongs to another live session - skip those branches and report them. If the pid is dead (or no lock), the worktree is reapable.
6. **Sanity check gate.** If `>10` branches would be deleted, present the full list grouped by category and **stop for explicit confirmation** before any destructive action. Below 10, present the list and ask once.
7. **Execute (after confirmation):**
 - For each safe-to-delete branch: `git worktree remove -f -f <path>` first if a reapable worktree holds it, then `git branch -D <name>`. Use `-D` (force) intentionally - gh's MERGED state is the safety check, not git's local merge-base check, because squash-merge defeats the latter.
 - `git worktree prune` at the end (cleans orphan metadata).
8. **Optional remote cleanup.** If any deleted branches still have live remote tracking refs, ask: "Delete N corresponding remote branches?" If yes: `cat <list> | xargs git push origin --delete` (one round trip). Also offer to enable repo-level auto-delete-on-merge: `gh repo edit <owner>/<repo> --delete-branch-on-merge`.
9. **Report.** Counts before/after for local + remote branches and worktrees. Surface any branches skipped (open PR, no PR, no upstream, alive lock pid) so the user knows what they need to look at.

## Output format

```
Pre-classification (94 local branches):
 DELETE-SAFE - gone + merged: 12
 DELETE-SAFE - live remote + merged (squash orphans): 8
 PRESERVE - open PR: 6
 SKIP - no PR record (manual review): 4
 SKIP - no upstream (never pushed): 3
 SKIP - alive worktree lock (other session): 2
 PROTECTED: main

20 branches to delete. Confirm? [y/N]
```

## Failure modes

- **Use `-D` (force) only for gh-verified MERGED branches.** Never force-delete a branch the gh check didn't confirm. The whole safety contract is gh's MERGED state - without that, fall back to `-d` (safe) and report refusals.
- If `gh` is unavailable, fall back to the legacy `-d`-only mode and report that you can't verify squash-merged branches - the user gets a partial cleanup.
- If `gh pr list` returns fewer PRs than expected (the `--limit 500` cap), retry with a higher limit. The skill MUST cover every PR in the repo or its classification is unsafe.
- If `>10` branches qualify for deletion, ALWAYS pause for confirmation. Even if the user said "go ahead" earlier in the session, re-confirm at this gate - bulk deletion is irreversible from CLI.
- If a branch is checked out by another live process (lock pid alive), do NOT force-unlock the worktree. Skip it and tell the user to re-run after that session ends.
- Never touch branches matching `release/*`, even if they appear merged.
- If the repo has no remote, report and stop - the verify pattern doesn't apply.

## Notes on the squash-merge default

Most modern repos squash-merge. `git branch -d` checks whether the branch tip's commit appears in HEAD's history; squash creates a new commit on main with a different SHA, so `-d` refuses even though the work is merged. The legacy "use `-d`, stop on refuse" pattern is wrong for squash-merge repos - it leaves ~95% of stale branches uncleaned. This skill defaults to gh-verify + `-D` precisely to handle that.

If you're in a merge-commit-only repo (rare these days), the gh check will still confirm MERGED and `-D` will still do the right thing - just slightly more aggressive than `-d` would be in that environment, but with the same end state since the branch IS in main's history.
