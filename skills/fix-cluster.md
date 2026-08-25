Fixes a cluster of related GitHub issues as a single pull request. Issue bodies are the spec. Args: issue numbers (`#22 #26 #39`) or a label (`trust`, `p0 trust`).

## Purpose

Five small related bugs handled as five separate sessions costs five context loads, five branches and five reviews, and each fix is made without sight of the other four. This groups them: one root cause, one branch, one PR, one review.

It is the execute half of a capture-and-execute pair. `/log-issue` puts findings in; this takes a related set out.

## When to use

- Several open issues touch the same surface or share a root cause.
- A label has accumulated enough items to be worth one focused pass.
- You want a reviewable unit of work rather than a trickle of one-line commits.

**Must run from inside the repo** - this writes code, so it needs the working tree.

## Steps

### 1. Resolve the issue list

- Numeric args (`#37`, or `#22 #26 #39`) - that exact list.
- Label args (`trust`, or `p0 trust`) - `gh issue list --label <labels> --state open --json number,title,body,labels`, run from inside the repo. AND semantics across labels. If your repo scopes bugs under a `qa` label, add it to the list; do not hardcode one, because a label that does not exist returns zero issues silently and that reads as "nothing to fix".

Fetch each body. **The body is the spec.** If a body is too thin to implement from, say so and stop rather than inventing the requirement.

### 2. Plan, and show the plan before touching code

```
Cluster: trust-fast-wins (3 issues)
  #22 fake testimonial - replace homepage testimonial section with a real quote, or remove
  #26 favicon - add favicon set
  #39 blog placeholder images - wire the featured-image field, fall back to the OG card

Approach:
  Edits in: src/components/Testimonials.astro, public/favicon.*, src/layouts/BlogPost.astro
  Branch: fix/trust-fast-wins
  PR: "fix: trust-fast-wins (closes #22, #26, #39)"

Risks:
  #22 no real testimonials exist yet - confirm removal is acceptable
  #39 the fallback design is a judgment call

Proceed? (yes / no / change-scope)
```

Wait for confirmation. The risks block is the whole point of the pause: it surfaces the calls that are not yours to make.

### 3. Split if the cluster is too big

If a label pulls in 10+ issues, or the set spans more than one obvious code surface, **stop here and propose splitting into 2-3 sub-PRs** before any edits. One PR closing twelve unrelated issues is review-hostile, and review-hostile PRs get rubber-stamped, which defeats the point of opening one.

### 4. Branch and implement

```
git checkout -b fix/<cluster-name>
```

Short kebab-case descriptor (`fix/trust-fast-wins`). Single-issue mode: `fix/<number>-<slug>`.

Stay strictly inside the cluster scope. Do not refactor adjacent code, do not add features beyond what the issues describe. **If you find an unrelated bug while working, file it as a new issue and keep going** - scope creep inside a fix PR is how a two-hour job becomes a two-day one.

### 5. Open a PR that closes all of them

```
gh pr create --title "<short title>" --body "$(cat <<'EOF'
Closes #N1, #N2, #N3.

## Summary
<one paragraph: what shipped, and what was deliberately left out>

## Per-issue notes
- #N1 - <what changed>
- #N2 - <what changed>
- #N3 - <what changed>

## Test plan
- [ ] <golden path 1>
- [ ] <golden path 2>
EOF
)"
```

One `Closes #N` per issue auto-closes them all on merge. Pick one keyword (`Closes`, `Fixes` or `Resolves`) and reuse it - GitHub accepts all three but a mixed list reads like an error.

### 6. Report back

```
PR: <url>
Closes: #22, #26, #39
Branch: fix/trust-fast-wins
```

## Failure modes

- Do not edit files before the plan is confirmed.
- Do not work on `main`. Always branch.
- Do not skip hooks with `--no-verify`.
- Do not close issues directly - let the merge do it, so the PR stays the audit trail.
- Do not pull adjacent fixes into the branch. File them.
- If an issue turns out to be already fixed, say so and drop it from the cluster rather than manufacturing a diff for it.
