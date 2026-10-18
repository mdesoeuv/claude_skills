# Claude Code skills — baseline for developers and AWS platform engineers

A curated, opinionated set of [Claude Code skills](https://code.claude.com/docs/en/skills). Skills are short Markdown playbooks Claude loads when a task matches their description, so it works the way your team works instead of improvising each time.

Two tiers:

- **Core** — the skills every developer should have installed, regardless of language or cloud. They cover the daily loop: change, test, debug, commit, review, document, ship.
- **Recommended** — the skills that make an AWS / platform engineer fast and safe. Install them when you work with Terraform, AWS accounts, containers, CI/CD, Kubernetes, or on-call.

## Install

Personal (available in every repo on this machine):

```bash
git clone <this-repo> ~/claude_skills
cd ~/claude_skills
./install.py          # core only
./install.py --all    # core + recommended
```

Project (committed with a repo so the whole team gets them):

```bash
cd ~/work/some-repo
~/claude_skills/install.py --all --project --copy
git add .claude/skills
```

As a plugin (namespaced as `/baseline-skills:<name>`):

```
/plugin marketplace add <owner>/<repo>
/plugin install baseline-skills@baseline
```

Verify with `/skills` inside Claude Code. Skills trigger automatically when a request matches their description, or explicitly with `/commit`, `/pr`, `/terraform envs/prod`, and so on.

## Core skills (mandatory)

| Skill | What it enforces | Why it is mandatory |
|---|---|---|
| [`commit`](skills/commit/SKILL.md) | Inspect the diff, stage deliberately, Conventional Commit message with a "why" body | History is the primary documentation during an incident. Bad commits cost every future reader. |
| [`pr`](skills/pr/SKILL.md) | PR body with Why / What / How to test / Risk and rollback | Reviewers catch design errors only when they know the motivation; rollback notes are what ops needs at 3 a.m. |
| [`tdd`](skills/tdd/SKILL.md) | Failing test first, run the real suite, report the real result | AI-written code without a test is a liability the user inherits. The test proves the requirement was understood. |
| [`debug`](skills/debug/SKILL.md) | Capture, reproduce, what changed, ranked hypotheses, one change at a time, regression test | Prevents fixing the first plausible symptom and the "widen permissions until it works" anti-pattern. |
| [`secrets-hygiene`](skills/secrets-hygiene/SKILL.md) | Scan before commit, where secrets live per runtime, never echo secrets | A pushed secret is a compromised secret. Prevention is cheap; rotation and incident reports are not. |
| [`docs-sync`](skills/docs-sync/SKILL.md) | README / CLAUDE.md / variables / runbooks updated in the same PR as the change | Stale docs are worse than none because people trust them. CLAUDE.md is also how Claude learns the repo. |
| [`verify-done`](skills/verify-done/SKILL.md) | Definition-of-done checklist and honest "not done" reporting | Closes the gap between "code written" and "change verified", which is where most AI-assisted mistakes live. |

Claude Code ships built-in `/code-review`, `/security-review`, `/init`, and plan mode. These core skills complement them rather than duplicate them.

## Recommended skills (AWS / platform engineering)

| Skill | Scope | Key safeguards |
|---|---|---|
| [`terraform`](skills/terraform/SKILL.md) | Terraform / OpenTofu changes, modules, state | fmt + validate + saved plan; stop on any destroy of stateful resources; pinned providers; tags; `moved {}` over state surgery |
| [`aws-cli-safety`](skills/aws-cli-safety/SKILL.md) | Any `aws` command or SDK call | `get-caller-identity` first, explicit profile/region, read-only before mutating, confirm destructive prod actions, no long-lived keys |
| [`iam-least-privilege`](skills/iam-least-privilege/SKILL.md) | IAM policies, roles, trust policies, AccessDenied | Actions from real API calls, scoped ARNs, conditions, OIDC `sub` pinning, Access Analyzer validation |
| [`dockerfile`](skills/dockerfile/SKILL.md) | Dockerfiles, compose, ECR, Lambda images | Multi-stage, digest-pinned bases, non-root, cache-friendly layers, hadolint + trivy, deploy by SHA |
| [`github-actions`](skills/github-actions/SKILL.md) | CI/CD workflows | Least-privilege `permissions`, SHA-pinned actions, OIDC to AWS, timeouts, environments, injection-safe inputs |
| [`kubernetes`](skills/kubernetes/SKILL.md) | EKS workloads, Helm, kubectl | Context check first, dry-run/diff before apply, requests/limits/probes/securityContext, IRSA, debugging recipes |
| [`adr`](skills/adr/SKILL.md) | Architecture decisions | Standard ADR template with honest option comparison and consequences |
| [`runbook`](skills/runbook/SKILL.md) | On-call runbooks and postmortems | Every step is a command with expected output; blameless postmortem with owned action items |
| [`release`](skills/release/SKILL.md) | Versioning and changelogs | Semver from conventional commits, Keep a Changelog, tags, GitHub releases, artifacts built by CI |
| [`cost-review`](skills/cost-review/SKILL.md) | Cost impact of infra changes | Monthly delta per resource, NAT/transfer/retention leaks, guardrails, Cost Explorer queries |

## Not included on purpose

- Language-specific style guides: put those in the project's `CLAUDE.md` or a project skill; they vary too much to ship globally.
- CDK / CloudFormation / Pulumi: add a sibling of `terraform` when a team needs it, reusing the same plan-review discipline.
- Anything that duplicates a built-in Claude Code command.

## Writing a new skill

1. `mkdir skills/<name>` and write `SKILL.md` with `name`, `description`, and `metadata.tier`.
2. The description is the trigger. Say what the skill does **and** when to use it, including the casual phrasings users actually type.
3. Explain the why behind rules. Keep it under ~150 lines; move long references to `skills/<name>/references/`.
4. `claude plugin validate .` then `./install.py --all` and try it on a real task.
5. Optional: use the `skill-creator` skill to run eval prompts with and without the skill and tune the description.

## Layout

```
.claude-plugin/
  plugin.json          # plugin manifest (install as baseline-skills)
  marketplace.json     # lets this repo act as its own marketplace
skills/<name>/SKILL.md # one skill per directory, tier in frontmatter
install.py             # symlink/copy skills into ~/.claude/skills or ./.claude/skills
```
