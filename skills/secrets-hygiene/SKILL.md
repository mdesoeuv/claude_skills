---
name: secrets-hygiene
description: Keep credentials, tokens, keys and PII out of code, git history, logs, and chat. Use whenever a task touches .env files, API keys, AWS credentials, kubeconfigs, certificates, database URLs, or when the user pastes something that looks like a secret. Also use before any commit or PR, and when wiring secrets into CI, Lambda, ECS, or Kubernetes.
metadata:
  tier: core
---

# Secrets hygiene

A secret that lands in git is compromised the moment it is pushed, even if removed in the next commit. Prevention is cheap; rotation and incident write-ups are not.

## Detect before commit

Run a scanner on the staged diff when available:

```bash
gitleaks protect --staged --redact      # preferred
# or
git diff --staged | grep -nE 'AKIA[0-9A-Z]{16}|-----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY|ghp_[A-Za-z0-9]{36}|xox[baprs]-|password\s*[:=]'
```

Patterns to treat as secrets even without a scanner: AWS access keys (`AKIA…`, `ASIA…`), session tokens, private keys, OAuth client secrets, Slack/GitHub tokens, database connection strings with passwords, `.pem`/`.p12`/`.jks` files, `terraform.tfstate` (state contains plaintext secrets), kubeconfig files, `.npmrc`/`.pypirc` with tokens.

If you find one: do not commit, do not print the full value back to the user, tell them which file and line, and recommend rotation if it was ever pushed.

## Where secrets belong

| Runtime | Store | Inject |
|---|---|---|
| Local dev | `.env` (gitignored) or `direnv` | loaded by the app, never committed; commit `.env.example` with placeholder values |
| CI (GitHub Actions) | repository/environment secrets; prefer OIDC to AWS over long-lived keys | `${{ secrets.NAME }}`; set `permissions:` minimally |
| AWS Lambda / ECS / EC2 | Secrets Manager or SSM Parameter Store (SecureString) | read at startup via IAM role, cache in memory; never bake into env vars in IaC |
| Kubernetes | External Secrets Operator or Secrets Store CSI backed by Secrets Manager | mounted volume or env from secretRef; never plain `Secret` manifests in git |
| Terraform | `sensitive = true` variables, values from Secrets Manager data sources or `TF_VAR_*` | remote state with encryption and restricted access |

## Rules that are easy to forget

- Logs are a sink: never log request headers, tokens, full connection strings, or whole event payloads. Redact.
- Chat is a sink: if the user pastes a secret, acknowledge it as "the token you shared" and do not echo it.
- `.gitignore` must include `.env`, `.env.*`, `*.pem`, `*.key`, `*.tfstate*`, `.terraform/`, `kubeconfig*`, `*.p12`. Check it exists before the first commit.
- A secret in a public repo should be considered leaked within minutes. Rotate first, then clean history (`git filter-repo`), then force-push, in that order.
- Use IAM roles and OIDC wherever possible so there is no secret to leak.
