Reviews the session for facts worth keeping, writes them to a file-based memory store, and periodically flags memories whose commitment date has passed. Cheap by design: it never reads the store in bulk.

## Purpose

Agent memory rots in two directions and most setups only notice the first.

The obvious failure is forgetting: you tell the agent something, and next session it has no idea. The less obvious one is accumulation. A memory store that only ever grows fills with decisions that were reversed, projects that died, gates whose dates passed months ago, and near-duplicate entries written because nobody checked whether the fact was already there. Every one of those is loaded into context at the start of every session, so a stale store is not neutral. You pay for it on every single run, and worse, the agent acts on facts that stopped being true.

This skill does both halves. It captures what the session taught, and it flags what has expired, without ever loading the whole store to do either.

The cost discipline is the part that makes it usable daily. A naive version reads every memory file to decide what is stale, which turns a routine end-of-session habit into an expensive one and you stop running it. Here the staleness pass is a deterministic script that reads the files outside the model and prints a shortlist, and the model only looks at what the script surfaced.

## When to use

- At the end of a working session, when a decision was made, a preference was stated, or something cost you real time to discover.
- Any time you catch yourself explaining something to the agent for the second time.
- Weekly, for the staleness pass, which throttles itself so daily use costs one script call.

Not for: notes about what code does. That belongs in the repo or in a `CLAUDE.md`, which the agent already reads.

## Steps

**1. Extract from the session. No tool calls needed.**

The conversation is already in context, so this phase is free. Look for facts that will still matter in a month and that are **not derivable** from the repo, git history or a config file.

Worth saving: a decision and the reasoning behind it, a correction the user made, a gotcha that cost real time, a constraint, where a credential lives, a piece of live state that exists nowhere in code.

Not worth saving: what a file does, what a commit changed, anything true only for this session, anything already written in a config file the agent loads anyway.

**2. Check the index before writing.**

The index is already in context. If a memory on the topic exists, update that file rather than adding a near-duplicate. Duplicates are the main reason these stores double in size without gaining information.

**3. One fact per file.**

A session that produced three lessons is three files, not one. Granular files mean the agent can pull in exactly the relevant one instead of the whole store. Use frontmatter for a `name`, a one-line `description` used to judge relevance, and a `type`. Link related memories so a retrieved memory can pull its neighbours.

**4. Date every future commitment, in the body, explicitly.**

"hold until 2026-10-01". "gate reads about 2026-11-15". "expires 2026-12-02".

That wording is the entire mechanism behind step 5. A commitment written as "revisit this later" is invisible forever.

**5. The staleness pass, as a script rather than a model pass.**

Write a small script that walks the store and prints only what needs attention. It should:

- Parse ISO dates out of each file's body, skipping the frontmatter and any line that is describing history rather than a commitment (`why:`, `source:`, `description:`) - otherwise every "the user said this on 2026-04-25" fires as an expiry.
- Report a file only when a **future-tense commitment date has passed**. Historical dates are noise.
- Honour a review stamp: a comment such as `<!-- reviewed: YYYY-MM-DD -->` at the end of a file. Skip any file whose reviewed date is at or after its passed commitment. Without this, a memory you already settled reappears on every sweep forever.
- Self-throttle. Run a full pass only if none has run in the last seven days, with a `--force` flag to override.
- Print the store size and the index's per-session token cost, so the growth is visible.

**6. Verify before proposing a delete, with one subagent at most.**

A passed date means "check this", not "delete this". When a candidate's status can be settled from live state - a pull request merged, a domain lapsed, a threshold reached - hand the whole candidate list to a single read-only subagent and have it return one line each: STILL TRUE, SUPERSEDED, EXPIRED, or NEEDS USER. Its file reads stay out of the main context, which is the point.

Anything resting on human judgement - is that project really dead, does that preference still hold - is always NEEDS USER. Never decide those on the user's behalf.

**7. Stamp everything you reviewed, whatever the verdict**, and write the finding into the file. A stamp with no note tells the next session nothing.

**8. Propose, then write.**

Show one numbered list and change nothing until the user replies:

```
ADD    <name>  what it says, in one line
UPDATE <name>  what changes
DELETE <name>  why it is dead, and the evidence
ASK    <name>  the question only the user can answer
```

On approval, write the files and update the index in the same pass.

## Failure modes

- **Reading the store in bulk defeats the whole design.** Not with a glob, not with a loop, not "just to check". If you are about to read more files than the script shortlisted, stop. This is the failure mode the split between script and model exists to prevent.

- **Undated commitments are permanently invisible.** The sweep can only find what was written as a date. A memory saying "revisit when traffic picks up" will never surface again. Push back at write time and get a date, even a rough one.

- **Historical dates masquerade as expiries.** Every memory contains dates that are provenance rather than commitment. Without a skip rule the sweep flags the entire store on its first run, you learn to ignore it, and it becomes decoration.

- **A store that only grows is a tax on every session.** The index loads every time. A line added there costs the user tokens on every run for the rest of its life, so it has to earn the place. When the index gets too big, compact it: group related entries, cut restated detail, keep every filename. Compacting the index is not deleting memories, and the two must never be conflated.

- **Softening a stated preference is worse than forgetting it.** When the user says never do X, the memory says never, not "prefers not to". An agent that rounds a hard rule down to a preference will break it and believe it complied.

- **The store must be the same store everywhere.** If you run the agent on more than one machine, memory written on one and not synced to the other is worse than no memory, because behaviour silently diverges and you cannot tell which machine is right. Keep the store in a directory that is version controlled and synced, and check that the sync actually ran rather than assuming it did.
