---
name: verify-done
description: Definition-of-done check before claiming a task is complete. Use at the end of every implementation, fix, refactor, or infra change, and whenever the user asks "is this done?", "ready to merge?", or "can I ship this?". It catches the gap between "code written" and "change verified".
metadata:
  tier: core
---

# Verify done

"Done" means someone else could merge and deploy this without talking to you. Run through this list and report honestly; a skipped item stated plainly is better than a false green.

## Checklist

- [ ] **Builds**: the compile/lint/typecheck step the project uses ran and passed. Paste the command.
- [ ] **Tests**: the relevant suite ran and passed, and at least one test covers the new behaviour (see the `tdd` skill).
- [ ] **Manually exercised** where tests cannot reach: the CLI was invoked, the endpoint was curled, the plan was read. Say what you did.
- [ ] **No leftovers**: no debug prints, TODO-without-ticket, commented-out blocks, stray files, or unrelated formatting churn in the diff. `git diff --stat` matches the intent.
- [ ] **Secrets**: nothing sensitive staged (see the `secrets-hygiene` skill).
- [ ] **Docs**: README, CLAUDE.md, variables, changelog updated if behaviour or configuration changed (see the `docs-sync` skill).
- [ ] **Infra specifics** (when applicable): `terraform plan` reviewed with zero unexpected destroys; IAM changes are least-privilege; resources are tagged; costs understood.
- [ ] **Rollback known**: you can state in one sentence how to undo this.
- [ ] **Scope honoured**: everything the user asked for is in, and nothing they did not ask for is in. If something was deliberately left out, it is listed below with the reason.

## Report format

```
Done: <one line>
Verified by: <commands run and their result lines>
Not done / left out: <item and why, or "nothing">
Follow-ups: <optional>
```

Never write "should work" or "tests should pass". Either you ran it or you did not.
