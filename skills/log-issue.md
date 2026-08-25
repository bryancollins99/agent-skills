Files a bug or QA finding you just spotted as a GitHub issue on the current repo, dedupes against open issues, and then stops. Never fixes.

## Purpose

The gap between spotting a bug and fixing it is where bugs die unrecorded. This skill closes that gap in one line, without the context switch: you describe what you saw, it files a clean issue on the right repo and hands back a number.

The hard rule is that it does not fix. The moment a capture tool starts investigating, capture stops being cheap and you stop using it.

## When to use

- You are browsing your own site or app and something is wrong.
- You are mid-task on something else and notice an unrelated defect.
- An agent finds an out-of-scope bug while working and needs somewhere to put it.

## Steps

### 1. Resolve the target repo

`gh repo view --json nameWithOwner -q .nameWithOwner` from the current directory.

If that fails (not a git repo, no remote), ask once which repo to file against, then proceed. Do not guess from directory names.

### 2. Check for duplicates first

```
gh issue list --repo <repo> --label qa --state open --limit 50 --json number,title
```

If a clear match exists, comment on the existing issue with the note verbatim plus today's date instead of filing a new one:

```
gh issue comment <num> --repo <repo> --body "$(cat <<'EOF'
Re-confirmed: <the note, verbatim>

**Spotted:** YYYY-MM-DD
EOF
)"
```

Report back `Already logged -> #N <title>. Added a re-confirmed comment.`

Judge the match yourself, do not ask. **Strong signal:** same surface (homepage, `/tools/x`, footer) AND same fault verb (broken, missing, empty, wrong). **Weak signal:** a shared keyword only - file a new one.

If the match is partial (same surface, different bug), file a new issue and cross-reference the related one with `Related: #N`.

### 3. Draft title and body

- **Title:** a tight, scannable one-liner, surface first. `homepage hero: image clipping on iOS Safari`. Cap around 70 characters. No trailing period, no emoji.
- **Body:** the raw note as the first paragraph, verbatim - clean obvious typos only, never paraphrase. Link any URL or page slug that was mentioned. End with `**Spotted:** YYYY-MM-DD`.

Do not add "Steps to reproduce / Expected / Actual" scaffolding unless the note already contained it. Most QA notes are one line, and padding them out makes the issue harder to scan, not easier.

### 4. File it

```
gh issue create --repo <repo> --title "<title>" --label qa --body "$(cat <<'EOF'
<body markdown>
EOF
)"
```

If the `qa` label does not exist on that repo, retry without it. Do not auto-create labels - repos differ and label taxonomies are somebody's deliberate choice.

### 5. Report back

One line: number, title, URL.

```
#47 homepage hero: image clipping on iOS Safari -> https://github.com/owner/repo/issues/47
```

## Failure modes

- Do not read or edit source files. This is a logging skill.
- Do not run builds, tests, screenshots or audits to "verify" what was reported.
- Do not propose a fix, in the issue body or in the reply.
- Do not assign, milestone, or set a priority you were not given.
- Do not ask whether to start working on it. Assume no.
- Called repeatedly, treat each invocation independently. One spot, one issue - do not try to consolidate.
