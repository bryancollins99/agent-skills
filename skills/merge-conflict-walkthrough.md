Walks through each conflicted file in a merge or rebase - lists files, reads markers, proposes a resolution with rationale.

## Purpose

Merge conflicts are where solo developers lose the most time. This skill removes the "which side was mine again?" confusion by reading both sides of each conflict, proposing a resolution that preserves both intents where possible, and explaining its reasoning.

## When to use

- Any merge or rebase with 3+ conflicted files.
- A single file with non-obvious conflicts (renames, import reorders, formatting clashes).
- Mid-rebase when you've lost track of which commit you're replaying.

## Steps

1. Run `git status` and `git diff --name-only --diff-filter=U` to list conflicted files.
2. For each conflicted file, read the `<<<<<<<` / `=======` / `>>>>>>>` blocks.
3. Classify the conflict:
   - **Additive**: both sides added different entries to a list → keep both
   - **Version bump**: both sides changed the same version number → keep the newer
   - **Semantic clash**: same logic changed two different ways → human judgment needed
   - **Rename + edit**: one side renamed, other edited → flag for manual review
4. Propose a merged version inline. Show what each side contributed in a one-line comment.
5. Do not write the resolution to disk. Present it; the human copies or asks for the Edit.

## Output format

```
4 conflicted files:

1. pages/sitemap.js - ADDITIVE
   Both sides added sitemap entries. Merge is concatenation.
   Proposed: [merged block]

2. package.json - VERSION BUMP
   Your side: 1.4.2. Their side: 1.4.1. Keep HEAD.

3. src/auth.ts - SEMANTIC CLASH
   Your side refactored to async. Their side added retry logic.
   Needs human - both behaviours matter.

4. README.md - RENAME + EDIT
   Flag for manual review.
```

## Failure modes

- Do not auto-resolve semantic clashes - report them and stop.
- If the conflict involves binary files, report and stop.
- Do not run `git add` or `git rebase --continue` - the human confirms before advancing.
- If you can't parse the conflict markers (nested conflicts, corrupted file), stop and report.
