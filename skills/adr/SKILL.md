---
name: adr
description: Write an Architecture Decision Record for a non-trivial technical choice. Use when the user says "should we use X or Y", "document why we chose", "write an ADR", or when a change introduces a new service, datastore, vendor, pattern, or cross-cutting convention that future engineers will question.
argument-hint: "<decision title>"
metadata:
  tier: recommended
---

# Architecture Decision Record

An ADR exists so that in eighteen months nobody reopens a settled question without knowing why it was settled, and so that when the context changes, the decision can be revisited deliberately.

## Where

`docs/adr/NNNN-short-title.md`, numbered sequentially. Check the directory for the next number and the house template; follow it if one exists.

## Template

```markdown
# NNNN. <Title in the form of the decision: "Use Aurora PostgreSQL for the orders service">

Date: YYYY-MM-DD
Status: Proposed | Accepted | Superseded by NNNN | Deprecated
Deciders: <names or team>

## Context
<What forces are at play: requirements, constraints, current pain, deadlines, compliance,
team skills, cost envelope. Two to four paragraphs. Facts, not opinions.>

## Decision
<One or two sentences, present tense: "We will …">

## Options considered
### Option A: <name>
Pros / Cons / Rough cost / Operational burden
### Option B: <name>
…

## Consequences
<What becomes easier, what becomes harder, what we now have to do (migrations, training,
new runbooks), what we are explicitly accepting as risk.>

## Follow-ups
- [ ] <concrete tasks with owners if known>
```

## Writing guidance

- Write the context so a newcomer agrees the problem is real before reading the decision.
- Compare options on the same axes: cost, operational load, lock-in, team familiarity, time to deliver, security/compliance. Put numbers where you have them (monthly cost estimate, RTO/RPO, throughput).
- Be honest about the losing options' strengths. An ADR that strawmans alternatives will be distrusted.
- Consequences include the negative ones. "We now have two databases to back up" belongs there.
- Keep it under two pages. Link to spikes, benchmarks, and tickets rather than inlining them.
- When superseding, update the old ADR's status and link both ways.

## When $ARGUMENTS is given

Use it as the title; derive the filename from it.
