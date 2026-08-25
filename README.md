# Claude Code skills

A small, growing set of [Claude Code](https://claude.com/claude-code) slash commands I actually use, taken from my own `~/.claude/commands/` and genericised so they work in any repo.

Every skill here earns its place by having caught something real. They are not demos.

**MIT licensed.** Copy them, fork them, change them, ship them in commercial work. No attribution required. (The largest community list, `awesome-claude-code`, is CC BY-NC-ND, which means you cannot legally reuse what is in it. That is the gap this fills.)

## Install

A skill is a markdown file. There is nothing to build and no dependencies.

```bash
git clone https://github.com/The-Flash-Report/claude-code-skills.git
cp claude-code-skills/skills/*.md ~/.claude/commands/
```

Then type `/pre-commit-review`, `/branch-cleanup` or `/explain` in Claude Code.

To take just one:

```bash
curl -o ~/.claude/commands/branch-cleanup.md \
  https://raw.githubusercontent.com/The-Flash-Report/claude-code-skills/main/skills/branch-cleanup.md
```

## The skills

### `/pre-commit-review`
A second pair of eyes before you commit. Spawns a read-only reviewer agent over your working-tree diff, looking for the bugs your own tests miss because you wrote the code and the tests against the same mental model: magnitude errors, pagination-then-filter, off-by-one, edge cases, coupling to code you already retired.

Verdict only. It never edits. High value on numerical code, data transformations, parsers and schema migrations. Low value on UI tweaks.

### `/branch-cleanup`
Lists merged and stale local branches, deletes the safe ones, flags the rest. Never touches `main`, `master` or `release`.

The reason it exists: **`git branch -d` does not know about squash merges.** If you squash-merge pull requests, git refuses to delete branches whose work is already in `main`, so they pile up for months. This checks merge state externally with `gh pr list` instead of trusting git, so squash-merged branches get correctly identified as safe.

I ran it on my own repos and it found 31 branches in that state.

### `/explain`
Re-tells whatever you just built or found as plain-language use cases from the point of view of the person who benefits, not the person who built it.

No file paths, no PR numbers, no "shipped" or "wired" or "implemented". Useful when you need to tell a client, a newsletter, or yourself-in-three-months what the work actually does for someone.

## What this is not

A framework, a package, or a product. Just files that work.

I add one when a skill has proved itself and is portable enough to be useful outside my own setup. Some of the ones I use most are too wired into my own infrastructure to publish honestly, and I would rather ship three that work than thirty that need explaining.

## Who wrote these

I'm Bryan Collins. I build and run data businesses with Claude Code and document the process on [YouTube](https://www.youtube.com/channel/UCglNILz3uBqPer5EMJ_pzVg).

If you want the reasoning behind these, and what I get wrong along the way, that goes out in my newsletter:

**[Join the newsletter](https://newsletter.bryancollins.com/?utm_source=github&utm_medium=readme&utm_campaign=skills)**
