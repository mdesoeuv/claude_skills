---
name: cost-review
description: Estimate and reduce AWS cost impact of a change — new resources in Terraform/CDK, instance and storage sizing, data transfer, NAT, logs retention, and idle resources. Use when a change adds or resizes infrastructure, when the user asks "how much will this cost", "why is the bill high", "optimise cost", or before applying a plan that creates billable resources.
metadata:
  tier: recommended
---

# Cost review

Nobody notices a 40 dollar a month resource until there are two hundred of them. Catch cost at review time, when it is a line in a diff rather than a line in the bill.

## When reviewing an infra diff

For each new or resized resource, state the rough monthly cost and the driver. Use `infracost breakdown --path .` when available and paste the summary; otherwise estimate from on-demand pricing and say it is an estimate.

Look for the usual money leaks:

- **NAT Gateway**: ~35 USD/month each plus per-GB processing. One per AZ in every environment adds up; dev can share or use VPC endpoints for S3/DynamoDB/ECR.
- **Data transfer**: cross-AZ and cross-region traffic, public egress. Keep chatty services in one AZ-aware topology; use VPC endpoints and PrivateLink.
- **Over-provisioned instances**: RDS/EC2/OpenSearch sized for peak with no autoscaling or schedule. Check CloudWatch utilisation before accepting the size.
- **Storage classes and retention**: S3 without lifecycle rules, EBS gp2 instead of gp3, CloudWatch Logs with infinite retention, snapshots never pruned, ECR without lifecycle policy.
- **Always-on non-prod**: dev/staging running nights and weekends. Scheduled scale-to-zero or instance scheduler.
- **Managed services with minimums**: NAT, ALB, MSK, OpenSearch, Aurora Serverless v2 min ACU, Redshift, SageMaker endpoints.
- **Lambda**: memory too high, Provisioned Concurrency left on, logging whole payloads.
- **Observability**: high-cardinality custom metrics, detailed monitoring on everything, CloudWatch Logs ingestion of debug logs in prod.

## Guardrails to recommend

- Mandatory tags (`CostCenter`, `Service`, `Environment`, `Owner`) enforced by SCP or tag policy so Cost Explorer can allocate spend.
- AWS Budgets with alerts per account/environment; anomaly detection on.
- Savings Plans or Reserved Instances once baseline is stable; Graviton where the workload is arm-compatible.
- Right-sizing from Compute Optimizer and Trusted Advisor, reviewed monthly.

## Investigating a high bill

```bash
aws ce get-cost-and-usage --time-period Start=2026-09-01,End=2026-10-01 \
  --granularity MONTHLY --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --query 'ResultsByTime[0].Groups[?Metrics.UnblendedCost.Amount>`50`].[Keys[0],Metrics.UnblendedCost.Amount]' --output table
```

Then group by `USAGE_TYPE` within the top service, then by tag. Correlate spikes with deploys and `git log`.

## Report format

```
Estimated delta: +X USD/month (driver: …)
Risks: …
Cheaper alternative: … (trade-off: …)
```
