Turns a doc's open decisions into one question at a time, then writes the locked answers back into the doc. Args: a file path, a PR/issue number, or nothing (harvest from the current conversation).

## Purpose

Decision tables rot as "leans". A plan says `Lean: probably Postgres` and six weeks later nobody knows whether that was decided or just muttered. This skill forces each open decision to a lock, then persists the answer where the question lived, so the doc stops lying about its own state.

## When to use

- A PRD, plan or design doc with an "Open questions" section you keep scrolling past.
- After a review that returned a list of "needs a human call" items.
- End of a long conversation where you deferred four things with "later".

## Steps

### 1. Resolve the source

- **File path** (any `.md` or text doc) - harvest decisions from that file.
- **`#N` or a bare number** - `gh pr view N --json body,title`, falling back to `gh issue view N`. Harvest from the body.
- **No argument** - harvest from the current conversation: questions you asked that were never answered, `Lean:` statements, anything deferred with "later" or "TBD".

### 2. Harvest the decisions

Scan for, in priority order:

1. An explicit section - headings matching `Open decisions|Open questions|Decisions|TBD|Unresolved`, case-insensitive.
2. Inline markers - lines containing `Lean:`, `TBD`, `TODO(decide)`, `open question`, or an `(a)/(b)/(c)` option list.
3. Review output - `needs a human` / `blocking` / `for ratification` blocks.

For each decision extract: the question, the enumerated options if any, and the stated lean if any.

Skip anything marked mandatory or already locked - there is nothing to decide. Report those separately as "already locked".

**If nothing harvests, say so and stop. Never invent decisions to ask about.**

### 3. Ask, one at a time

- One question per decision. Highest-stakes first.
- The stated lean becomes the first option, marked **(Recommended)**. No lean means you order by your own judgment and still mark a recommendation.
- 2-4 options per question. Each option's description states the trade-off in one sentence: what it costs, what it buys.
- Do not batch. A wall of nineteen questions is unanswerable; one question with its context attached is.
- Wait for the answer before moving to the next.
- If a decision has no enumerable options and is genuinely free-text, offer the lean against "something else" and let the freeform answer carry it.

In Claude Code this is the one place an interactive picker earns its keep - `AskUserQuestion` with previews is the delivery mechanism. In any other agent, ask in plain text and wait.

### 4. Write the resolutions back

- **File source:** rewrite the open-decisions section in place. Retitle it `Decisions (resolved YYYY-MM-DD)` and give each decision one row: the bolded resolution, plus a one-line consequence note where the answer overrode the lean (mark it "overrides the lean" - future you will want to know the recommendation lost). If an answer creates a new follow-on question, add it as a clearly marked open item rather than silently resolving it.
- **PR or issue source:** append a `## Decisions (YYYY-MM-DD)` section via `gh pr edit --body` or `gh issue comment`.
- **Conversation source:** there is no doc to edit. Print the resolved table and offer exactly one save target, only if an obvious home exists.

Never touch any other part of the doc. Preserve its formatting conventions: tables stay tables, prose stays prose.

### 5. Report

One line: `N decisions resolved (M overrode the lean) -> written to <target>`. Then the resolved table. Flag any follow-on questions the answers created. Nothing else.

## Failure modes

- Do not answer on the human's behalf, even when the lean is obvious. The point of the skill is the lock, and a lock you applied yourself is worth nothing.
- Do not rewrite surrounding prose while editing the decisions section.
- Do not batch questions to save round-trips.
- If the doc is under version control and dirty, say so before writing - the human may want the edit isolated.
