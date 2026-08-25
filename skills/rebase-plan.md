Drafts a pick / squash / reword plan for `git rebase -i` to clean up a feature branch before PR. Advisory only - never executes the rebase.

## Purpose

Interactive rebase is the right tool for consolidating wip commits - and the one most people get wrong on their first try. This skill proposes the todo-list your editor will show, so you walk into the rebase knowing what to do.

## When to use

- Branch has typo/fixup/wip commits you want to consolidate into 1-3 clean commits before opening a PR.
- You want to reword a vague message ("stuff" → "refactor: extract parser") before it lands on main.

**Never on branches already pushed to a shared remote** - rebase rewrites history other people may have cloned.

## Steps

1. Run `git log main..HEAD --oneline --reverse` to list commits on the current branch.
2. Refuse if the branch tracks a remote that has commits others may be using (`git branch -vv` shows `[origin/...]`) unless the user explicitly confirms they're the only collaborator.
3. Propose a rebase-todo grouping related commits:
   - `pick` the first logical commit in each group
   - `squash` (or `fixup`) follow-ups that fix typos or add missing changes
   - `reword` any commit whose message is vague or wrong
4. Print the proposed todo in the exact format git will show, and print the command to run (`git rebase -i main`).
5. Do not run the rebase. The human drives the editor.

## Output format

```
Proposed rebase-todo:
  pick a1b2c3 feat: add Skills hub
  squash d4e5f6 fixup
  squash g7h8i9 typo in heading
  reword j0k1l2 → feat: wire cross-links

Run: git rebase -i main
```

## Failure modes

- If the branch has ≤2 commits, report "no cleanup needed" and stop.
- Do not propose squashing across unrelated changes.
- Never run `git rebase` itself - advisory only.
- If `git log main..HEAD` returns empty, stop - branch may already match main.
