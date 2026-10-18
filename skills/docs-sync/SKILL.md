---
name: docs-sync
description: Keep README, CLAUDE.md, runbooks, module docs, and inline comments in sync with code changes. Use after implementing a feature, changing a CLI flag, env var, config key, API, Terraform variable, or deployment step. Also use when asked to "document this", "write a README", or "update the docs".
metadata:
  tier: core
---

# Docs sync

Documentation that lags the code is worse than none, because readers trust it. Every change that alters how something is run, configured, or called should be checked against the docs in the same PR.

## After a code change, check

1. **README** of the service or module: usage examples, flags, env vars, prerequisites, "how to run locally", "how to deploy".
2. **CLAUDE.md**: build/test commands, conventions, gotchas. If you discovered a non-obvious fact while working (a flaky test, an ordering constraint, a required env var), record it there so the next session does not rediscover it.
3. **Terraform modules**: `variables.tf` descriptions and the README variables/outputs table. Run `terraform-docs markdown table . > README.md` if the project uses it.
4. **OpenAPI / schema files** when an endpoint or field changed.
5. **Runbooks and on-call docs** when alerts, dashboards, or recovery steps changed.
6. **CHANGELOG** if the project keeps one (see the `release` skill).

## Writing style

- Lead with what the reader does, not what the system is. "Run `make dev` to start the stack" beats "This project uses Docker Compose".
- Show the command, then its expected output, then what to do when it fails.
- Keep examples copy-pasteable and real. Placeholders in angle brackets: `<account-id>`.
- Prefer one short paragraph plus a code block over a wall of bullets.
- Delete stale text. Do not add "deprecated, see below" layers.

## README skeleton for a service or module

```markdown
# <name>
<one sentence: what it does and for whom>

## Quick start
<three to five commands to run it locally>

## Configuration
| Variable | Required | Default | Description |

## Deploy
<how it gets to each environment, who approves, how to roll back>

## Operations
<dashboards, alerts, runbook links, common failures>
```

## Comments in code

Explain why, not what. A comment that restates the line is noise; a comment that explains a workaround, a constraint from another system, or a rejected alternative is gold. Reference the ticket or incident where relevant.
