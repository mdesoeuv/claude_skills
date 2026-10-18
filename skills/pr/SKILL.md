---
name: pr
description: Open or update a pull request with a reviewer-friendly description, test plan, and risk notes. Use whenever the user wants to "open a PR", "create a merge request", "push this up for review", or asks for a PR description or title. Also use after a series of commits when the user says the work is ready.
argument-hint: "[base branch] [--draft]"
metadata:
  tier: core
---

# Pull request

A PR description is written for two readers: the reviewer today and the engineer doing `git blame` during an outage. Give both what they need in under a minute of reading.

## Before opening

1. `git status` and `git log <base>..HEAD --oneline`. Understand every commit in the range, not just the last one.
2. Run the project's tests and linters. If you cannot, say so in the description instead of claiming green.
3. Make sure you are not on the default branch. If you are, create a branch first.
4. Push with `git push -u origin <branch>`.

## Create with the GitHub CLI

```bash
gh pr create --base main --title "<type>(<scope>): <summary>" --body "$(cat <<'BODY'
## Why
<the problem or goal, one short paragraph; link the ticket>

## What changed
- <bullet per meaningful change, grouped by component>

## How to test
- [ ] <exact commands or clicks a reviewer can repeat>
- [ ] <what output proves it works>

## Risk and rollback
- Blast radius: <which envs/services/customers>
- Rollback: <revert the PR | terraform apply previous state | feature flag off>
- Migration or IaC apply needed: <yes/no, order of operations>

## Notes for the reviewer
<anything surprising, deliberate trade-offs, follow-ups left out on purpose>
BODY
)"
```

Add `--draft` when the work is not ready for a full review. Add reviewers with `--reviewer` only if the user names them.

Keep the title in Conventional Commit style so a squash merge produces a clean history (see the `commit` skill).

## Section guidance

- **Why** comes first. Reviewers who understand the motivation catch design errors, not just typos.
- **How to test** must be executable. "Tested locally" is not a test plan. For infra changes paste the relevant `terraform plan` summary line (`Plan: 3 to add, 1 to change, 0 to destroy`).
- **Risk and rollback** is mandatory for anything touching production, IAM, networking, data stores, or CI. Write "None, docs only" when truly none.
- Leave out sections that would be empty rather than writing "N/A" everywhere.

## Updating an existing PR

Use `gh pr view` to read the current body, then `gh pr edit --body` with the full updated text. Do not drop sections the user wrote by hand.
