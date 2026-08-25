---
description: Independent QA review of a working-tree diff before commit. Spawns a read-only reviewer agent to find correctness bugs the test suite can't catch - magnitude heuristics, pagination-then-filter, off-by-one, edge cases, coupling to retired code. Verdict-only - never edits.
---

# /pre-commit-review - second pair of eyes before commit

Catches the bugs your own tests miss because you wrote both the code and the tests against the same mental model. High ROI on dense numerical, data-transformation, parser, and schema-migration code. Low ROI on UI changes or trivial edits.

## When to use

**Trigger phrases worth running this on (Claude: if you wrote any of these, suggest `/pre-commit-review` before `/commit` even if you were not asked):**
- New parser / extractor / column mapper (CSV, JSON, scraped HTML)
- Numerical pipeline (EMA, rolling windows, financial math, training-load math, statistics)
- SQL refactor or new query that filters / orders / paginates
- Schema migration or model field rename
- Anywhere you wrote a magnitude-based heuristic (`if x > N: treat as A else B`)
- Anywhere you filter in Python after a SQL `LIMIT`
- Anywhere you removed an integration but left the column names

**Skip for:** copy edits, UI styling, README/docs, dependency bumps with no code changes, one-line fixes.

## How to invoke

- `/pre-commit-review` - review the entire working-tree diff (staged + unstaged)
- `/pre-commit-review <paths>` - narrow to specific files (`/pre-commit-review norwegian/tools/pmc.py`)
- `/pre-commit-review HEAD` - review the last commit instead of the working tree (for "I already committed, second-guess me")

## Steps

### 1. Identify the diff

```bash
git status -sb
git diff --stat # working tree
git diff --stat --cached # staged
git diff HEAD~1 # if reviewing last commit
```

If the diff is empty, stop with "nothing to review."

### 2. Classify the change

Skim the diff. Decide one of:
- **Numerical / data**: math, parsers, queries, schema. → Full review.
- **UI / cosmetic**: styles, copy, layout. → Reply "low-ROI for this skill - `/commit` directly."
- **Mixed**: review only the numerical/data files; skip the cosmetic ones.

State the classification in one line before proceeding.

### 3. Spawn the reviewer

Use the **Agent** tool with `subagent_type: general-purpose`, `isolation: "worktree"` is NOT needed (read-only). Brief it with:

- The exact file paths changed.
- A one-paragraph summary of what the change is supposed to do (synthesise from the diff, don't ask the user).
- The five specific things to look for:
 1. **Correctness bugs**: off-by-one, magnitude heuristics, sign errors, EWMA constants, threshold values
 2. **Pagination-then-filter**: any SQL `LIMIT` followed by Python filtering on a column that should be in the `WHERE` clause
 3. **Coupling to retired code**: vestigial column names, dead branches, dispatcher entries that no longer route anywhere
 4. **Test coverage gaps**: which edge cases the new tests don't exercise
 5. **CLI-PRD alignment** (if the change touches `chat.py` or tool dispatch): tool descriptions clear enough for the agent to pick correctly without disambiguation help?

- Cap the response under 600 words.
- Ask for a **verdict** at the end: "ship-ready" / "ship after these N fixes" / "needs rework".

### 4. Surface the verdict

Show the user the reviewer's full report (under 600 words so it fits one screen). Then:

- **Ship-ready** → "Reviewer says ship. Want me to run `/commit`?"
- **Ship after fixes** → list each fix as a one-line action. Ask: "Fix these and re-review, or accept and commit anyway?"
- **Needs rework** → name the structural issue. Don't push toward commit.

### 5. Loop if the user accepts the fixes

If the user says "fix them," apply the fixes, re-run `pytest`, **do not re-spawn the reviewer** (one round is enough - second-guessing the second-guesser is procedural waste). Move to `/commit`.

If the user says "commit anyway," proceed to `/commit` and note in the commit body that the reviewer flagged N issues that are accepted as-is.

## Do not

- Do not edit code as part of this skill - verdict-only.
- Do not use `worktree` isolation - wastes a checkout for a read-only step.
- Do not re-run if you ran it ≤1 commit ago on the same files.
- Do not block on the reviewer for trivial diffs - be honest about ROI.
- Do not write the reviewer's output to a file unless the user asks - it's chat-only output.

## Anchor (why this exists)

Two real bugs caught on 2026-05-11 Norwegian Agent PRD layer that the author's own tests missed:
1. Zone parser: `if secs > 1: seconds else hours` - would fabricate 48 minutes of phantom Z3 from a 0.8-second reading.
2. `get_latest_lactate_test`: SQL `LIMIT 10` then Python filter on `time_of_day` - AM tests fall off the back once 11+ PM tests accumulate.

Both authors-can't-see-them bugs. Both caught by a 60-second agent run. The skill exists to make that 60-second run the default before any commit that touches code where this class of bug is plausible.
