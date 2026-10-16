Compare two AI agents' builds of the same spec, name what each did better, and write one brief that folds the loser's best ideas into the winner's branch. Args: the spec path plus two preview URLs or branch names.

## Purpose

When you run the same spec through two coding agents, the natural move is to pick a winner and delete the other branch. That throws away whatever the losing build got right.

It happened on a paid-placement leaderboard: the GPT build was the better page overall, but the Claude build handled empty categories far better, filling them with existing site content so the page never looked dead. Picking GPT outright would have shipped empty pages for every category with no paying vendor yet, which on launch day was all of them.

This skill makes the comparison explicit and turns it into a single, specific improvement brief instead of a vague "can you improve your version?".

## When to use

- You built the same feature twice, with two agents or two models, from one spec.
- Both builds are viewable: a preview deploy, a local branch, or screenshots.
- You prefer one overall but keep noticing things the other did better.

Not for choosing between two specs. Settle the spec first; this compares implementations of the same one.

## Steps

### 1. Load the spec and both builds

- Read the spec in full. Its sections (reader experience, states, money, boundaries, metrics) become the comparison rows.
- For each build, get something you can actually look at: a preview URL, or `git diff main...<branch> --stat` plus the rendered page. If a build only exists as code, run it locally before judging it. Do not compare from diffs alone.

### 2. Compare section by section

Write a table, one row per spec section:

| Spec section | Build A | Build B | Better | Why (one line) |

Rules:

- Judge against the spec, not against each other's style.
- Call out anything a build added that the spec never asked for (extra states, extra pages, extra settings). Over-building is a cost, not a feature, especially from high-effort runs.
- Check the empty, first-use and error cases explicitly. That is where builds differ most and where the losing build often wins.

### 3. Pick the base

Pick the build that wins on the most important rows as the base branch. Say why in one sentence. Everything else is a donor.

### 4. Write the merge brief

One brief for the agent that owns the base branch:

- **Keep:** the base build's winning sections, named, so it does not regress them.
- **Adopt:** each donor idea, described concretely (what it does, where on the page), with the donor's preview URL and a screenshot of that exact part.
- **Drop:** anything over-built that the spec did not ask for.
- **Do not:** copy code across branches. The donor build is a reference for behaviour, not a source to paste from; the base agent re-implements in its own structure.

Print the brief. Do not send it or run it.

### 5. After the merge

Re-open the merged preview and re-check every row the donor won. A donor idea that did not survive the merge is the most common failure here.

## Failure modes

- **"Improve your version" with no specifics.** The agent polishes what it already built and ignores the other build. Name each idea to adopt.
- **Judging from code instead of the rendered page.** Two builds can look equivalent in a diff and very different on screen, especially empty and error states.
- **Rewarding volume.** The build with more states, toggles and pages looks more complete. Check each extra against the spec before counting it as a win.
- **Cherry-picking commits between agents' branches.** Different file layouts and naming make this a conflict mess. Re-implement from the description instead.
