---
name: runbook
description: Write operational runbooks and blameless incident postmortems. Use when the user asks for a runbook, on-call doc, "what to do when X alerts", playbook, or a postmortem/RCA/incident review, and after any debugging session that uncovered a production failure mode worth recording.
argument-hint: "<alert or incident name>"
metadata:
  tier: recommended
---

# Runbooks and postmortems

A runbook is read at 3 a.m. by someone who did not write the system. A postmortem is read by people deciding whether to fund the fix. Write for those readers.

## Runbook template

`docs/runbooks/<alert-or-service>.md`

```markdown
# <Alert name or scenario>

**Severity:** <P1..P4> **Owner:** <team> **Escalation:** <who, how>
**Dashboards:** <links> **Logs:** <query link or CloudWatch Insights snippet>

## What this means
<One paragraph: what is broken from the user's point of view, and what the alert actually measures.>

## First 5 minutes
1. <Check X> — command or link, expected healthy output
2. <Check Y>
3. If <condition>, go to "Mitigate A"; else "Mitigate B".

## Mitigate
### A: <most common cause>
<exact commands, with the account/region/cluster spelled out; what success looks like>
### B: <second cause>
…

## Do not
- <things that look helpful and make it worse, e.g. restarting the primary during failover>

## After
- <what to verify, who to inform, ticket to open, how to close the alert>
```

Rules: every step has a command or a link, and says what a good result looks like. No "investigate the logs". Test the runbook by having someone unfamiliar follow it.

## Postmortem template

`docs/postmortems/YYYY-MM-DD-<short-title>.md`

```markdown
# <Title>: <one-line impact>

**Date:** **Duration:** **Severity:** **Author:** **Status:** Draft | Reviewed

## Impact
<Who was affected, how many, for how long, in user terms. Numbers.>

## Timeline (UTC)
| Time | Event |
|---|---|
| 09:12 | Alert X fired |
| 09:15 | On-call acknowledged |
| … | … |

## Root cause
<The technical chain of events, as mechanism, not blame. Why the system allowed it.>

## Contributing factors
<Missing alert, ambiguous runbook, unreviewed change, lack of canary…>

## What went well / What went badly / Where we got lucky

## Action items
| Action | Owner | Priority | Ticket | Due |
|---|---|---|---|---|
```

Blameless means naming systems and gaps, not people. "The deploy pipeline allowed an untested migration to reach prod" rather than "X deployed without testing". Action items must be specific enough to close and have an owner, or they will not happen.

## When $ARGUMENTS is given

Treat it as the alert name or incident title and pick the matching template.
