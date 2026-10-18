---
name: iam-least-privilege
description: Author and review AWS IAM policies, roles, trust policies, and resource policies with least privilege. Use whenever a task creates or edits IAM (in Terraform, CDK, CloudFormation, SAM, or JSON), grants a service or user access, debugs AccessDenied, or when the user says "give the lambda access to", "allow CI to deploy", "the role needs permission".
metadata:
  tier: recommended
---

# IAM least privilege

Every `"Action": "*"` is a future incident report. Write the policy the service needs this week, with a path to widen it on purpose later.

## Writing a policy

1. **List the actual API calls** the code makes. Read the SDK calls, not the feature description. `s3:PutObject` is not `s3:*`.
2. **Scope resources** to ARNs. Use account ID and region from variables, never hardcoded. Bucket policies need both `arn:aws:s3:::bucket` and `arn:aws:s3:::bucket/*` when both listing and object access are required.
3. **Add conditions** where they are cheap and meaningful: `aws:SourceAccount`/`aws:SourceArn` on service trust policies (confused deputy), `aws:RequestedRegion`, `s3:prefix`, `aws:ResourceTag/...`, `kms:ViaService`.
4. **Split statements** by purpose with a `Sid` each so a reviewer can read intent. One statement per resource family.
5. **Trust policy** is as important as the permission policy. Restrict `Principal` to the exact service or role; for GitHub Actions OIDC, pin `token.actions.githubusercontent.com:sub` to `repo:org/repo:ref:refs/heads/main` or the environment, not `repo:org/*`.
6. **Validate**: `aws accessanalyzer validate-policy --policy-document file://p.json --policy-type IDENTITY_POLICY` (or `RESOURCE_POLICY`) and fix every ERROR and SECURITY_WARNING. In Terraform, prefer `data "aws_iam_policy_document"` over heredoc JSON so it is linted.

## Shape

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadConfigObjects",
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": "arn:aws:s3:::${bucket}/config/*"
    },
    {
      "Sid": "ListConfigPrefix",
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": "arn:aws:s3:::${bucket}",
      "Condition": { "StringLike": { "s3:prefix": ["config/*"] } }
    }
  ]
}
```

## Things that are not least privilege

- `iam:PassRole` on `*`: lets the principal hand any role to any service. Scope it to the exact role ARN and add `iam:PassedToService`.
- `sts:AssumeRole` on `*`.
- `kms:*`, `secretsmanager:*`, `ssm:*` on `*` to "get it working".
- Managed policies like `AdministratorAccess`, `PowerUserAccess`, `AmazonS3FullAccess` attached to workloads or CI.
- `NotAction` / `NotResource` without a very good reason.
- Permission added to debug an AccessDenied without finding which single action was missing. Read the CloudTrail `errorMessage`; it names the action and resource.

## Reviewing

Ask three questions per statement: who can assume this, what can it do, on which resources. If any answer is "anything", stop. Use IAM Access Analyzer findings and `aws iam simulate-principal-policy` to test rather than guessing.

## Debugging AccessDenied

Check in order: identity policy, permission boundary, SCP, resource policy (bucket/KMS/secret), session policy, VPC endpoint policy, and whether the principal is in the account you think. The CloudTrail event has the answer; the `errorMessage` says which action on which ARN was denied and often which policy type did it.
