---
description: Re-explain the findings or work from this session as plain-language use cases told from the persona's point of view (the writer, the buyer, the bidder), not the developer's. No file paths, no PR numbers, no jargon. Use when a technical summary needs translating into "what does this actually do for someone".
---

# /explain - say it as the person who uses it, not the person who built it

Takes whatever was just found, built, audited or decided in this session and re-tells it as **concrete use cases from the point of view of the human who benefits**. Nothing new is investigated. No files are touched. This is a translation pass over work already done.

## Arguments
- `/explain` - translate the current session's findings/work.
- `/explain <thing>` - narrow it to one part (`/explain the AI hub`, `/explain the redirect layer`).

## Who the persona is

Pick the real end user of the thing, from the project context. Never write "the user" in the output itself: that is the abstraction this skill exists to remove. Give them a name, a situation and a reason to show up:

| Project type | Persona to write as |
|---|---|
| Content or publishing site | a working writer chasing a deadline, a rate, or a launch |
| B2B comparison or directory | a business owner or ops lead choosing a supplier |
| Procurement or tender data | a small-firm bidder deciding whether a bid is worth the effort |
| Consumer recommendation site | someone looking for the next thing to read, watch or buy |
| Local or regional publication | a resident, or someone moving to the area |
| Personal finance or trading tool | the person running their own money on a Monday morning |
| Internal tooling or developer skills | the developer at the terminal, mid-session |

If the project isn't listed, infer the persona from who actually visits or runs the thing. If genuinely ambiguous, pick the most likely one and say which you picked in a single line.

## Output shape

Lead with one sentence: **what changed for this person**. Then 3-6 use cases. Each one is a short scene, written as prose:

1. **The moment** - where they are and what they want, in their words ("It's Sunday night and she has one poem ready and no idea which competitions are still open.")
2. **What they do** - the actual steps they take, named the way they'd say them, not the way the code does ("She picks poetry, ticks free entry, sees four deadlines this month with the dates checked last week.")
3. **What they walk away with** - the concrete result ("Two entries submitted and the deadlines in her phone calendar.")

Then close with one honest line: **what it still doesn't do for them.** Not a caveat dump - the single most useful limitation for the reader to know.

## Rules

- **No developer vocabulary.** Banned unless the persona is developer-at-the-terminal: PR numbers, file paths, function names, schema/field names, component names, repo names, branch names, endpoints, JSON, build steps, deploy previews, commit hashes, "shipped", "merged", "wired", "implemented".
- **Name features the way a person would say them out loud**, not by their route or slug. "The page that tells you if you have to tell Amazon you used AI", not `/kdp-ai-disclosure/`.
- **Concrete over general.** A real scenario with a real number beats "users can filter results". If the data supports it, use an actual example from the work (a real contest, a real rate, a real market).
- **Scenes, not bullets of features.** Anything that reads like a changelog line has failed the skill.
- **Don't oversell.** If a use case only half-works, say so in the persona's terms ("she still has to check the magazine's own page for the exact word count").
- **Verification rules still apply.** Every concrete detail in a scene comes from something actually found or built this session. Do not invent a plausible-sounding example to make the story flow - if a detail wasn't verified, leave it out or mark it **`UNVERIFIED ASSUMPTION:`**.
- Plain sentences. No headers per use case unless there are more than four. No emojis. No em dashes in the persona prose.

## Do not

- Do not re-run analysis, re-read the codebase, or dispatch agents. Everything needed is already in the session.
- Do not write files or open PRs.
- Do not append a technical summary "for completeness" - the whole point is the other register. If they want both, they will ask.
