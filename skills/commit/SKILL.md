---
name: commit
description: Create well-scoped git commits with Conventional Commit messages. Use this whenever the user asks to commit, save work, "ship this", or finishes a change and wants it recorded in git, even if they do not say "commit". Also use when writing or rewriting a commit message.
argument-hint: "[optional scope or message hint]"
metadata:
  tier: core
---

# Commit

A commit is the smallest unit of history someone will read in a year, under pressure, during an incident. Optimise for that reader.

## Workflow

1. Look before you commit: `git status`, `git diff --staged`, `git diff`. Never commit blindly.
2. Check for anything that must not land: credentials, `.env` files, private keys, large binaries, debug prints, commented-out code. If found, stop and tell the user. See the `secrets-hygiene` skill.
3. Stage deliberately. Prefer `git add <paths>` over `git add -A`. One logical change per commit; if the diff mixes a refactor and a feature, split it.
4. Write the message in the format below.
5. Commit with a heredoc so multi-line bodies survive the shell:

```bash
git commit -m "$(cat <<'MSG'
feat(auth): add OIDC login for the admin console

Replaces the shared basic-auth password with Cognito-backed OIDC so
access can be revoked per user. Sessions expire after 8h.

Refs: PLAT-412
MSG
)"
```

6. Confirm with `git log -1 --stat`. Never amend or force-push unless the user explicitly asks.

## Message format

```
<type>(<scope>): <imperative summary, ≤72 chars, no trailing period>

<why this change exists, not what the diff shows — the diff already shows that>

<footer: Refs/Closes ticket, BREAKING CHANGE: ..., Co-Authored-By>
```

Types: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `build`, `ci`, `chore`, `revert`.
Scope is the module, service, or stack touched (`api`, `terraform/vpc`, `ci`). Omit it when the change is global.

The body matters more than the summary. Answer "why now?" and "what did we consider?" in two to four sentences. A one-line commit is fine for trivial changes.

## Examples

Input: fixed the null pointer when the S3 bucket has no tags
Output: `fix(s3-inventory): handle buckets with no tag set`

Input: bumped terraform aws provider from 5.40 to 5.60, needed for the new lambda runtime attribute
Output:
```
build(terraform): bump aws provider to 5.60

Required for `aws_lambda_function.runtime = "python3.13"`. No resource
diffs on `terraform plan` across all stacks.
```

## When $ARGUMENTS is given

Treat it as the scope or summary hint from the user, but still inspect the diff and correct it if it does not match what actually changed.
