#!/usr/bin/env python3
"""
wiring.py - "is the plumbing actually connected?"

Compares the secrets and env vars a repo's code DECLARES against what is
actually SET, on both sides:

  GitHub Actions : `secrets.X` in .github/workflows/*  vs  repo secrets + org secrets
  Netlify runtime: process.env.X / import.meta.env.X   vs  getEnvVars (production context)

Derived from the repo every run. There is deliberately no hand-maintained
registry of required vars, because those drift.

Usage:
  python3 wiring.py [path] [--repo owner/name] [--netlify-site <site_id>]

  path            repo checkout (default: current directory)
  --repo          GitHub repo; default `gh repo view --json nameWithOwner` in path
  --netlify-site  Netlify site id; default `.netlify/state.json` siteId in path

Needs `gh` (authed) for the GitHub side and `netlify` CLI (authed) for the Netlify side.
Either side degrades to UNKNOWN on any API error. Always exits 0.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

# --- Auto-provided by the platform. Declaring these is normal; they are never "missing".
PLATFORM = {
    # GitHub Actions
    "GITHUB_TOKEN", "GITHUB_OUTPUT", "GITHUB_ENV", "GITHUB_STEP_SUMMARY",
    "GITHUB_WORKSPACE", "GITHUB_REPOSITORY", "GITHUB_SHA", "GITHUB_REF",
    "GITHUB_ACTOR", "GITHUB_RUN_ID", "RUNNER_OS",
    # Netlify build + runtime (https://docs.netlify.com/configure-builds/environment-variables/)
    "NETLIFY", "NETLIFY_LOCAL", "NETLIFY_DEV", "NETLIFY_BLOBS_CONTEXT",
    "NETLIFY_IMAGES_CDN_DOMAIN", "CONTEXT", "DEPLOY_URL", "DEPLOY_PRIME_URL",
    "DEPLOY_ID", "BUILD_ID", "COMMIT_REF", "CACHED_COMMIT_REF", "BRANCH", "HEAD",
    "PULL_REQUEST", "REPOSITORY_URL", "SITE_ID", "SITE_NAME", "URL",
    # Generic
    "CI", "GITHUB_ACTIONS", "NODE_ENV", "MODE", "SITE", "PATH", "HOME", "PWD",
    "LANG", "TERM", "TZ", "PORT", "npm_lifecycle_event", "npm_package_version",
}

# --- Absent ON PURPOSE. Reporting these is a false positive and an active annoyance.
#     Keys are (repo slug or "*", VAR, "gh" | "netlify" | "*"). Each entry needs a
#     written reason; an unexplained suppression is worse than a false positive.
#     Example: on Netlify a user-set ANTHROPIC_API_KEY switches the AI Gateway OFF,
#     so its absence can be the wired state.
INTENTIONAL = {
    # ("*", "ANTHROPIC_API_KEY", "netlify"): "AI Gateway in use; a user-set key disables it.",
}

PREFIX_RE = re.compile(r"(?:process\.env|import\.meta\.env)\.([A-Z][A-Z0-9_]*)")
BRACKET_RE = re.compile(r"(?:process\.env|import\.meta\.env)\[[\"']([A-Z][A-Z0-9_]*)[\"']\]")
SECRET_RE = re.compile(r"secrets\.([A-Z][A-Z0-9_]*)")
# Only what Netlify actually executes: functions, edge functions, and the built site.
# `scripts/` is deliberately excluded - those run in GitHub Actions, and scanning them
# here reported every DataForSEO/CRO cron key as a missing Netlify var.
NETLIFY_DIRS = ("netlify", "src", "functions", "edge-functions")
SRC_EXT = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".astro", ".svelte", ".vue"}
# A reference is "guarded" if absence still yields working behaviour:
#   `|| 'default'`  `?? x`  `? a : b`  `=== 'true'` (absence -> false, a valid default)
FALLBACK = re.compile(r"^\s*(\|\||\?\?|\?[^.]|or\s|[!=]==?)")


def sh(cmd, **kw):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60, **kw)
        return r.stdout if r.returncode == 0 else None
    except Exception:
        return None


def declared_gh_secrets(path: Path):
    wf = path / ".github/workflows"
    found = set()
    if not wf.is_dir():
        return found
    for f in wf.rglob("*.y*ml"):
        try:
            found |= set(SECRET_RE.findall(f.read_text(errors="ignore")))
        except Exception:
            pass
    return found - PLATFORM


def available_gh_secrets(repo: str, path: Path):
    """repo-level + org-level. `gh secret list --org` is 403 without org-admin;
    repos/{repo}/actions/organization-secrets works with plain repo read."""
    avail, unknown = set(), []
    out = sh(f"gh secret list --repo {repo} --json name --jq '.[].name'")
    if out is None:
        unknown.append("repo secrets")
    else:
        avail |= {l.strip() for l in out.splitlines() if l.strip()}
    out = sh(f"gh api repos/{repo}/actions/organization-secrets --paginate --jq '.secrets[].name'")
    if out is None:
        unknown.append("org secrets")
    else:
        avail |= {l.strip() for l in out.splitlines() if l.strip()}
    return avail, unknown


def referenced_runtime_env(path: Path):
    """var -> True if AT LEAST ONE reference has no fallback (so it is genuinely
    required), False if every reference is guarded by `||` / `??` / a ternary
    (config with a default - absence is not a defect)."""
    found = {}
    for d in NETLIFY_DIRS:
        base = path / d
        if not base.is_dir():
            continue
        for f in base.rglob("*"):
            if f.suffix not in SRC_EXT or not f.is_file():
                continue
            if "node_modules" in f.parts or "dist" in f.parts or ".netlify" in f.parts:
                continue
            try:
                t = f.read_text(errors="ignore")
            except Exception:
                continue
            for m in list(PREFIX_RE.finditer(t)) + list(BRACKET_RE.finditer(t)):
                var = m.group(1)
                if var in PLATFORM:
                    continue
                tail = t[m.end():m.end() + 12]
                required = not FALLBACK.match(tail)
                found[var] = found.get(var, False) or required
    return found


def netlify_env(site_id: str):
    """Returns (set_of_keys_with_a_real_production_value, partial_dict, error).

    NEVER use `netlify env:list --plain` here: it prints secret-scoped vars as
    `KEY=` with an empty value, which reads as absent when it is only redacted.
    The API reports real value presence.
    """
    site = sh(f"""netlify api getSite --data '{{"site_id":"{site_id}"}}'""")
    if not site:
        return set(), {}, "getSite failed (netlify CLI not authed?)"
    try:
        account_id = json.loads(site).get("account_id")
    except Exception:
        return set(), {}, "getSite returned unparseable JSON"
    if not account_id:
        return set(), {}, "no account_id on site"
    raw = sh(
        f"""netlify api getEnvVars --data '{{"account_id":"{account_id}","site_id":"{site_id}"}}'"""
    )
    if not raw:
        return set(), {}, "getEnvVars failed"
    try:
        data = json.loads(raw)
    except Exception:
        return set(), {}, "getEnvVars returned unparseable JSON"

    live, partial = set(), {}
    for v in data:
        key = v.get("key")
        ctxs = {
            c.get("context")
            for c in v.get("values", [])
            if c.get("value") not in (None, "")
        }
        if {"all", "production"} & ctxs:
            live.add(key)
        elif ctxs:
            # set, but NOT on production - reads as wired and is not.
            partial[key] = sorted(ctxs)
    return live, partial, None


def intentional(slug, var, side):
    for (s, v, sd), why in INTENTIONAL.items():
        if v == var and s in ("*", slug) and sd in ("*", side):
            return why
    return None


def audit(name, repo, path, site_id):
    slug = (repo or path.name).split("/")[-1]
    out = {"name": name, "repo": repo, "slug": slug, "path": str(path), "notes": [],
           "gh_missing": [], "nf_missing": [], "nf_optional": [], "nf_partial": {},
           "suppressed": [], "unknown": []}

    if not path.is_dir():
        out["unknown"].append(f"checkout not found at {path}")
        return out

    # --- GitHub Actions side
    declared = declared_gh_secrets(path)
    if declared and repo:
        avail, unk = available_gh_secrets(repo, path)
        if unk:
            # A partial `avail` makes every unseen secret look missing. Report the
            # lookup failure and run no diff at all rather than manufacture defects.
            out["unknown"].append(f"GH secrets not compared - {' and '.join(unk)} lookup failed")
            declared = set()
        for var in sorted(declared - avail):
            why = intentional(slug, var, "gh")
            (out["suppressed"] if why else out["gh_missing"]).append(f"{var} - {why}" if why else var)
    elif declared:
        out["unknown"].append("GH secrets declared but no repo resolved (pass --repo)")
    else:
        out["notes"].append("no .github/workflows secrets declared")

    # --- Netlify side
    if site_id:
        live, partial, err = netlify_env(site_id)
        if err:
            out["unknown"].append(f"netlify: {err}")
        else:
            referenced = referenced_runtime_env(path)
            for var in sorted(set(referenced) - live - set(partial)):
                why = intentional(slug, var, "netlify")
                if why:
                    out["suppressed"].append(f"{var} - {why}")
                elif referenced[var]:
                    out["nf_missing"].append(var)
                else:
                    out["nf_optional"].append(var)
            out["nf_partial"] = {k: v for k, v in partial.items() if k in referenced}
    else:
        out["notes"].append("no Netlify site id (pass --netlify-site or link the site)")
    return out


def resolve(args):
    path, repo, site = Path.cwd(), None, None
    it = iter(args)
    for a in it:
        if a == "--repo": repo = next(it, None)
        elif a == "--netlify-site": site = next(it, None)
        elif not a.startswith("-"): path = Path(os.path.expanduser(a)).resolve()
    if not repo:
        out = sh("gh repo view --json nameWithOwner --jq .nameWithOwner", cwd=path)
        repo = out.strip() if out else None
    if not site:
        state = path / ".netlify/state.json"
        if state.is_file():
            try: site = json.loads(state.read_text()).get("siteId")
            except Exception: pass
    return path, repo, site


def main():
    path, repo, site = resolve(sys.argv[1:])
    r = audit(path.name, repo, path, site)
    print(f"wiring check - {r['name']}  ({r['repo'] or 'no repo'})")
    if r["gh_missing"]:
        print("  GH SECRET MISSING (declared in a workflow, not set on repo or org):")
        for v in r["gh_missing"]: print(f"    - {v}")
    if r["nf_missing"]:
        print("  NETLIFY ENV MISSING (referenced in code, no production value):")
        for v in r["nf_missing"]: print(f"    - {v}")
    if r["nf_partial"]:
        print("  NETLIFY ENV NOT ON PRODUCTION (set, but only on):")
        for k, v in r["nf_partial"].items(): print(f"    - {k}: {', '.join(v)}")
    if r["unknown"]:
        print("  UNKNOWN: " + "; ".join(r["unknown"]))
    if r["nf_optional"]:
        print("  netlify, unset but every reference has a fallback (probably fine): " + ", ".join(r["nf_optional"]))
    if r["suppressed"]:
        print("  suppressed (absent on purpose):")
        for v in r["suppressed"]: print(f"    . {v}")
    if not any([r["gh_missing"], r["nf_missing"], r["nf_partial"], r["unknown"]]):
        print("  ok" + (f" ({'; '.join(r['notes'])})" if r["notes"] else ""))
    print(f"summary: gh_missing={len(r['gh_missing'])} netlify_missing={len(r['nf_missing'])} netlify_not_production={len(r['nf_partial'])}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"wiring.py error: {e}")
    sys.exit(0)
