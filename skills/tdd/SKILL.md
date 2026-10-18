---
name: tdd
description: Drive code changes with tests first, red-green-refactor, and run the real test suite before declaring anything done. Use for any request to implement a feature, fix a bug, or refactor logic, even if the user does not mention tests. Also use when asked to "add tests", "cover this", or "make sure it works".
metadata:
  tier: core
---

# Test-driven changes

Untested code written by an AI is a liability the user inherits. A failing test written first is the cheapest proof that you understood the requirement and the cheapest guard that you did not break it later.

## Loop

1. **Find the harness.** Look for `package.json` scripts, `pytest.ini`/`pyproject.toml`, `go.mod`, `Makefile`, `Taskfile`, `.github/workflows`. Run the existing suite once before touching anything so you know the baseline. If it is red before you start, tell the user.
2. **Write the failing test.** Name it after the behaviour, not the function: `test_expired_token_is_rejected`, not `test_validate`. Put it next to the existing tests for that module and follow their style and fixtures.
3. **Run it and watch it fail** for the right reason. A test that fails on an import error has not tested anything yet.
4. **Write the minimum code** to make it pass.
5. **Run the whole relevant suite**, not just the new test.
6. **Refactor** with the suite green, then run again.
7. Report the actual command and its actual result. Paste the summary line.

## What to test

- The bug the user reported, reproduced exactly, before fixing it. That test is the regression guard.
- Boundaries: empty input, missing field, zero, negative, unicode, timeouts.
- Error paths: what happens when the dependency fails. Mock the network, never the thing under test.
- For infrastructure code: `terraform validate`, `terraform plan` on a fixture, policy checks (`checkov`, `tfsec`, `conftest`), and a smoke test of the deployed thing when one exists.

## What not to do

- Do not weaken or delete a failing existing test to get green. Explain why it fails and ask.
- Do not mark a task done with "tests should pass". Either they passed in front of you or they did not.
- Do not write tests that only assert the mock was called. Assert on behaviour and outputs.
- Do not add a test framework to a project that has one. Match the existing one.

## Reporting

End with the exact command and the result line, for example:

```
pytest tests/auth -q
...
42 passed in 3.1s
```
