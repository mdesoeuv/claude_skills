---
name: aws-cli-safety
description: Run AWS CLI and SDK commands safely — explicit profile and region, read-only first, dry runs, pagination, JMESPath filtering, and confirmation before anything mutating or production-facing. Use whenever a task runs `aws ...`, inspects or changes AWS resources, assumes roles, or the user asks "what's in this account", "list the ...", "delete the ...", "update the ...".
metadata:
  tier: recommended
---

# AWS CLI safety

The CLI has no undo. The difference between "list" and "delete" is one word, and the difference between dev and prod is one env var you may not have checked.

## Before the first command

```bash
aws sts get-caller-identity --profile "$P"
aws configure list --profile "$P"
```

State the account ID, role, and region you are about to act in. If the task is production and the user did not say so, ask before mutating.

Always pass `--profile` and `--region` explicitly, or export `AWS_PROFILE`/`AWS_REGION` in the same command, so a stale shell default cannot bite. Never put `--profile prod` on a command the user asked to run against dev; re-read the request.

## Read-only first

Start with `describe-*`, `list-*`, `get-*`. Understand state before changing it. Prefer `--output json` with `--query` so results are precise and small:

```bash
aws ec2 describe-instances --region eu-west-1 \
  --filters Name=tag:Service,Values=api \
  --query 'Reservations[].Instances[].{id:InstanceId,state:State.Name,az:Placement.AvailabilityZone}' \
  --output table
```

Use `--no-cli-pager` in scripts and `--max-items` / `--starting-token` for big lists. Many APIs are paginated by default and the CLI handles it; some (S3 `list-objects-v2`, CloudWatch Logs) need explicit care.

## Mutating commands

- Use `--dry-run` where it exists (EC2) and `--generate-cli-skeleton` to build complex input safely.
- Show the exact command and the resources it targets before running. For anything that deletes, detaches, scales to zero, modifies IAM, security groups, DNS, or a database, get explicit confirmation from the user in that turn.
- Prefer tags over IDs when selecting resources, and print what was selected before acting on it.
- Delete in the reverse order of dependencies; expect `DependencyViolation` and do not force.
- If the resource is managed by Terraform/CDK/CloudFormation, change it there, not by hand. Manual changes become drift and get reverted or cause the next apply to fail.

## Credentials

- Prefer SSO (`aws sso login`) or `assume-role` with short-lived credentials. Never ask for or paste long-lived access keys in chat.
- Never print `aws configure get aws_secret_access_key` or environment variables containing credentials.
- For cross-account work use `aws sts assume-role` with an `--external-id` when one is configured.

## Useful patterns

```bash
# Who has been doing what (CloudTrail, last 2h)
aws cloudtrail lookup-events --lookup-attributes AttributeKey=EventName,AttributeValue=DeleteBucket \
  --start-time "$(date -u -v-2H +%FT%TZ)" --query 'Events[].{t:EventTime,u:Username}'

# Tail logs
aws logs tail /aws/lambda/my-fn --since 30m --follow

# Which SG rules are open to the world
aws ec2 describe-security-groups --query 'SecurityGroups[?IpPermissions[?IpRanges[?CidrIp==`0.0.0.0/0`]]].[GroupId,GroupName]'
```

## Report

Finish with the account, region, and the exact commands run so the user can audit them.
