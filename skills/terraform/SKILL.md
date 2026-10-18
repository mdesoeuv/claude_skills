---
name: terraform
description: Write, change, review and apply Terraform/OpenTofu safely — plan before apply, module conventions, state handling, provider pinning, tagging, and policy checks. Use for anything involving .tf files, terraform plan/apply, modules, workspaces, state, drift, or "infra as code", including when the user only says "add an S3 bucket" or "change the ALB" in a Terraform repo.
argument-hint: "[stack path] [env]"
metadata:
  tier: recommended
---

# Terraform

Terraform turns a typo into a deleted database. Every step below exists because of a real outage somewhere.

## Workflow for any change

1. **Orient**: find the stack layout (`environments/`, `modules/`, `live/`, Terragrunt?), the backend (`backend "s3"`), the provider lock file, and how the team runs it (Makefile, Atlantis, Terragrunt, CI). Respect it.
2. **Edit** in the smallest surface: a module if the resource is reusable, the stack if it is a one-off. Match the existing naming and file split (`main.tf`, `variables.tf`, `outputs.tf`, `versions.tf`).
3. **Format and validate** before anything else:
   ```bash
   terraform fmt -recursive
   terraform init -backend=false   # or with backend if credentials are available
   terraform validate
   tflint --recursive              # if configured
   ```
4. **Plan** with explicit var files and an explicit profile/region. Save it:
   ```bash
   terraform plan -var-file=envs/dev.tfvars -out=tfplan
   terraform show -no-color tfplan | head -200
   ```
5. **Read the plan like a reviewer.** Count adds/changes/destroys. Any `destroy` or `replace` (`-/+`) on stateful resources (RDS, DynamoDB, S3, EBS, EFS, KMS, Cognito pools, Route53 zones) stops the task until the user confirms. Explain why the replacement happens (immutable attribute, renamed resource needing `moved {}`).
6. **Apply only the saved plan**, only when the user asks, never against prod without explicit go-ahead:
   ```bash
   terraform apply tfplan
   ```
7. **Report** the final `Apply complete! Resources: X added, Y changed, Z destroyed.` line.

## Conventions

- Pin everything: `required_version`, provider `version = "~> 5.60"`, commit `.terraform.lock.hcl`.
- Every resource gets the standard tags through `default_tags` in the provider block plus `var.tags` merge. Minimum: `Environment`, `Service`, `Owner`, `ManagedBy = "terraform"`, `CostCenter` when the org uses one.
- Variables have `description` and `type`; secrets are `sensitive = true` and come from Secrets Manager / SSM data sources, never tfvars in git.
- Prefer `for_each` with stable string keys over `count` so removing one item does not reindex and recreate the rest.
- Use `moved {}` blocks for renames instead of `terraform state mv` by hand.
- `lifecycle { prevent_destroy = true }` on stateful resources; `ignore_changes` only with a comment explaining what external system mutates the attribute.
- Outputs are the module's API. Keep them stable and documented.
- Never run `terraform import`, `state rm`, `taint`, or `-target` without stating why and getting agreement; these bypass the plan safety net.

## Reviewing someone else's Terraform

Look for: public S3/ingress 0.0.0.0/0 on non-public ports, `*` in IAM, unencrypted storage, missing deletion protection and backups on databases, hardcoded account IDs/ARNs, provider blocks inside modules, un-pinned module sources (`ref=main`), resources without tags, giant blast radius in one stack.

Run `checkov -d .` or `tfsec .` when available and paste the summary.

## When $ARGUMENTS is given

Treat the first token as the stack directory and the second as the environment name to select the tfvars/workspace.
