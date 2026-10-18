---
name: debug
description: Systematic root-cause debugging. Use whenever something is broken, failing, flaky, slow, or "weird" — error messages, stack traces, failing CI, 5xx in production, a Lambda timing out, a Terraform apply erroring, a pod in CrashLoopBackOff. Use it before proposing any fix so the fix targets the cause, not the symptom.
metadata:
  tier: core
---

# Debug

The expensive mistake is fixing the first plausible cause. Spend the first minutes narrowing, not patching.

## Method

1. **Capture the exact failure.** Full error text, stack trace, exit code, timestamps, request IDs, the command that was run. Put it in a code block. Paraphrased errors lose the one token that matters.
2. **Reproduce it.** Find the smallest, fastest way to trigger it on demand. If you cannot reproduce, say so and work from logs; do not guess silently.
3. **Establish what changed.** `git log --since`, recent deploys, dependency bumps, config or IAM changes, provider upgrades, a certificate expiring. Most incidents are a change.
4. **Form two or three hypotheses** and rank them by likelihood and by how cheap they are to check. Write them down before testing.
5. **Test one hypothesis at a time** with a change that would only matter if that hypothesis is true. Revert what did not help; do not accumulate speculative edits.
6. **Fix the cause.** Then write a regression test that fails without the fix (see the `tdd` skill).
7. **Verify in the same way you reproduced it**, and run the wider suite.

## Where to look, by symptom

| Symptom | First checks |
|---|---|
| Works locally, fails in CI | env vars, secrets, OS/arch, node/python version, cached deps, timezone, working directory |
| Intermittent / flaky | shared state between tests, time, ordering, network, retries hiding real failures |
| AWS AccessDenied | which principal (`aws sts get-caller-identity`), resource policy vs identity policy, SCPs, permission boundary, KMS key policy, region |
| Lambda timeout / cold start | VPC attachment, DNS, init outside handler, memory size, downstream latency in X-Ray |
| Terraform error | provider version, state drift (`terraform plan -refresh-only`), `-target` leftovers, lock file |
| Kubernetes pod not ready | `kubectl describe pod`, events, probes, resource limits, image pull, secret/configmap mounts |
| 5xx after deploy | compare previous image/commit, health check path, env/config diffs, DB migration order |

## Rules

- Read the logs before reading the code. Logs tell you where; code tells you why.
- Add temporary logging if needed, and remove it before committing.
- Never "fix" by widening permissions, disabling TLS verification, catching and swallowing exceptions, or adding retries without understanding what is being retried.
- When you fix it, write down in one paragraph: cause, why it was not caught, what prevents it next time. That paragraph goes in the PR or the commit body.
