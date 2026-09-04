# Agent skills

Skills and workflows for AI coding agents, taken from my own setup and genericised so they work in any repo.

They ship as Claude Code slash commands because that is what I run daily, but nothing here is Claude-specific: each one is a plain markdown instruction file describing a repeatable job. The same text works as a Cursor rule, a custom prompt, or a spec you hand any capable agent.

Every skill here earns its place by having caught something real. They are not demos.

**MIT licensed.** Copy, fork, change, ship in commercial work. No attribution required. (The largest community list, `awesome-claude-code`, is CC BY-NC-ND, so nothing in it can legally be reused. That is the gap this fills.)

## Install

There is nothing to build and no dependencies.

**Claude Code:**

```bash
git clone https://github.com/bryancollins99/agent-skills.git
cp agent-skills/skills/*.md ~/.claude/commands/
```

Then type `/pre-commit-review`, `/fix-cluster`, `/decide` or any of the others.

**Any other agent:** open the file and paste it as your instruction. They are written as procedures, not as tool calls.

**Just one:**

```bash
curl -o ~/.claude/commands/branch-cleanup.md \
  https://raw.githubusercontent.com/bryancollins99/agent-skills/main/skills/branch-cleanup.md
```

## The skills

**Git hygiene**

### `/pre-commit-review`
A second pair of eyes before you commit. Runs a read-only reviewer over your working-tree diff, looking for the bugs your own tests miss because you wrote the code and the tests against the same mental model: magnitude errors, pagination-then-filter, off-by-one, edge cases, coupling to code you already retired.

Verdict only. It never edits. High value on numerical code, data transformations, parsers and schema migrations. Low value on UI tweaks.

### `/merge-conflict-walkthrough`
Reads both sides of every conflicted file and proposes a resolution with its reasoning.

It classifies each conflict first - additive, version bump, semantic clash, rename-plus-edit - because those need different treatment and only the first two are safe to resolve mechanically. Semantic clashes are reported and left alone. It never writes to disk and never runs `git add` or `git rebase --continue`.

### `/rebase-plan`
Drafts the pick / squash / reword todo list for `git rebase -i` before you open the editor.

Interactive rebase is the right tool for consolidating wip commits and the one most people get wrong on the first try. This prints exactly what your editor will show, so you walk in knowing what to do. Advisory only: it refuses on branches that track a shared remote, and it never runs the rebase itself.

### `/branch-cleanup`
Lists merged and stale local branches, deletes the safe ones, flags the rest. Never touches `main`, `master` or `release`.

The reason it exists: **`git branch -d` does not understand squash merges.** If you squash-merge pull requests, git refuses to delete branches whose work is already in `main`, so they pile up for months. This checks merge state externally with `gh pr list` instead of trusting git, so squash-merged branches are correctly identified as safe.

Run on my own repos, it found 31 branches in exactly that state.

**Issues to shipped code**

### `/log-issue`
Files the bug you just spotted as a GitHub issue on the current repo and then stops.

It dedupes against open issues first, so re-spotting a known bug adds a re-confirmed comment instead of a second ticket. The hard rule is that it never fixes, never investigates, never runs a build to "verify" what you saw. The moment a capture tool starts investigating, capture stops being cheap and you stop using it.

### `/fix-cluster`
Fixes a set of related issues as one pull request. Issue bodies are the spec.

Five small related bugs handled separately costs five context loads and five reviews, and each fix is made without sight of the other four. This plans the cluster, shows you the risks before touching code, branches once and opens one PR with a `Closes #N` line per issue. If the cluster is too big or spans more than one surface, it proposes a split instead of shipping a review-hostile PR.

**Keeping automation honest**

### `/cron-staleness`
Audits every scheduled GitHub Actions workflow for silent death: not the runs that failed, the runs that should have happened and did not.

`gh run list --status failure` cannot see a cron that stopped firing, because a workflow that never runs produces no failed run and no notification. The dashboard stays green on checks that are not executing. This derives each workflow's expected cadence from its own cron expression, compares it against the last successful run, and separately flags anything GitHub auto-disabled after 60 days of repository inactivity.

Run on my own portfolio it found a build check, a Core Web Vitals check and two link scrapers that had not fired in weeks, while a weekly monitoring email reported on them the entire time.

**Thinking and communicating**

### `/decide`
Takes the "Open questions" section that every plan grows and forces each item to a lock, one question at a time, then writes the answers back into the doc.

Decision tables rot as leans. A plan that says `Lean: probably Postgres` is not a decision, and six weeks later nobody can tell whether it was made or just muttered. This asks, waits, and persists - including a note when the answer overrides the lean, because future you will want to know the recommendation lost.

### `/explain`
Retells whatever you just built or found as plain-language use cases from the point of view of the person who benefits, not the person who built it.

No file paths, no PR numbers, no "shipped" or "wired" or "implemented". Useful when you need to tell a client, a newsletter, or yourself in three months what the work actually does for someone.

### `/notes-to-ideas`
Mines a folder of your own notes for things worth writing, weighted to recent material but forced to resurface older notes that connect to a current thread. Ideation only. It never drafts.

Pointing an agent at your notes to write for you produces an impression of you. The job it is actually better at than you are is retrieval: finding the note from two years ago that answers what you are stuck on this week, which no tagging system fixes because you did not know to make the connection at the time.

The rule that keeps it working past the third run is the distinction between an idea that has been *drafted* and one that was merely *surfaced*. Retiring surfaced-but-unwritten ideas feels like hygiene and degrades the list to the bottom of the barrel within a month.

## What this is not

A framework, a package, or a product. Just files that work.

I add one when it has proved itself and is portable enough to be useful outside my own setup. Some of the ones I lean on hardest are too wired into my own infrastructure to publish honestly, and I would rather ship eight that work than thirty that need explaining.

## Who wrote these

I'm Bryan Collins. I build and run data businesses with AI coding agents and document the process on [YouTube](https://www.youtube.com/channel/UCglNILz3uBqPer5EMJ_pzVg).

If you want the reasoning behind these, and what I get wrong along the way, that goes out in my newsletter:

**[Join the newsletter](https://newsletter.bryancollins.com/?utm_source=github&utm_medium=readme&utm_campaign=skills)**
