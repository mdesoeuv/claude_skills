---
name: github-actions
description: Build and fix GitHub Actions workflows — CI for test/lint/build, CD to AWS via OIDC, least-privilege permissions, pinned actions, caching, matrix builds, reusable workflows, and debugging failed runs. Use for any .github/workflows file, "set up CI", "deploy on merge", "the pipeline is failing", or questions about Actions security.
metadata:
  tier: recommended
---

# GitHub Actions

CI is code that runs with your credentials on every PR, including PRs from forks. Treat workflows with the same care as the IAM policies they assume.

## Baseline workflow

```yaml
name: ci
on:
  pull_request:
  push:
    branches: [main]
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-24.04
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@<sha>   # pin to a full commit SHA, comment the tag
      - uses: actions/setup-node@<sha>
        with: { node-version-file: .nvmrc, cache: npm }
      - run: npm ci
      - run: npm run lint
      - run: npm test -- --ci
```

## Deploy to AWS with OIDC, no stored keys

```yaml
  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    environment: production          # gates on required reviewers
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@<sha>
      - uses: aws-actions/configure-aws-credentials@<sha>
        with:
          role-to-assume: arn:aws:iam::${{ vars.AWS_ACCOUNT_ID }}:role/gha-deploy-${{ github.event.repository.name }}
          aws-region: eu-west-1
      - run: ./scripts/deploy.sh
```

The IAM role's trust policy must pin `sub` to this repo and branch or environment (see the `iam-least-privilege` skill).

## Rules

- Top-level `permissions: contents: read`; elevate per job only for what it needs (`id-token`, `pull-requests: write`, `packages: write`).
- Pin third-party actions to a full SHA. Tags move; SHAs do not. Let Dependabot/Renovate bump them.
- Never use `pull_request_target` with checkout of the PR head unless you fully understand the injection risk. Never interpolate untrusted input (`github.event.*.title`, branch names) directly into `run:`; pass it through `env:`.
- Add `timeout-minutes` to every job. Default is six hours of billed runner time on a hang.
- Cache dependency directories keyed on the lockfile hash. Do not cache `node_modules` directly; cache the package manager store.
- Use `environment:` for prod with required reviewers and environment-scoped secrets.
- Prefer reusable workflows (`workflow_call`) over copy-pasted YAML across repos.
- Matrix only what differs; a 3×3 matrix on every PR costs nine times more than you think.
- For Terraform: plan on PR and post the plan as a PR comment; apply on merge with `environment` protection. Never apply from a PR.

## Debugging a failed run

```bash
gh run list --workflow ci --limit 5
gh run view <id> --log-failed
gh run rerun <id> --failed
```

Reproduce locally first with the same versions; `act` is useful for simple workflows. Check for the usual suspects: missing secret in this environment, different default shell (`bash -e` vs `sh`), `set -o pipefail` absent, concurrency cancelling the run, a runner image update changing a tool version.
