# IaC-Lint: Infrastructure-as-Code Security & Compliance Agent

Catch security misconfigurations, compliance violations, and cost overruns in your Terraform infrastructure before they reach production.

## Revenue Hook

**Upload your Terraform plans at agent-hub.dev** — get instant security scanning, compliance reporting, and cost optimization insights.

## How It Works

IaC-Lint analyzes Infrastructure-as-Code resource definitions (Terraform HCL, JSON plans, etc.) and returns actionable compliance findings:

- **Security Issues:** Public S3 buckets, open security groups, unencrypted databases, overly permissive IAM roles
- **Compliance Violations:** Missing tags, no backup configuration, logging disabled
- **Cost Opportunities:** Oversized instances, idle load balancers, underutilized resources

Each finding includes:
- **Severity Level:** critical | high | medium | low
- **Category:** security | compliance | cost
- **Rule ID:** Machine-readable identifier (e.g., S001, C007, CO002)
- **Description:** Human-friendly explanation and remediation guidance

## Comparison

| Feature | IaC-Lint | Checkov | Bridgecrew | Snyk IaC |
|---------|----------|---------|-----------|----------|
| **Price** | Free (agent-hub.dev) | Free/Open-Source | $250/month | $100/month |
| **Setup** | Upload & scan | Manual CLI | SaaS + CLI | SaaS + CLI |
| **Security Rules** | 20+ | 500+ | 500+ | 300+ |
| **Cost Optimization** | Yes | No | Limited | No |
| **Custom Rules** | Via agent experiments | YAML templates | Limited | Limited |
| **API** | REST (agent-hub.dev) | Python SDK | REST API | REST API |

## Quick Start

```bash
# Generate test infrastructure dataset (80 resources)
python prepare.py generate

# Run baseline (0 score - no detection)
python harness.py baseline

# Evaluate your lint rules
python harness.py evaluate

# Expected output:
# RESULT: compliance_score=XX.X improvement_pct=YY.Y
```

## Architecture

**prepare.py**
- Generates 80 synthetic IaC resource definitions
- Injects 120+ known misconfigurations (ground truth)
- Includes: aws_instance, aws_s3_bucket, aws_rds_instance, aws_security_group, aws_iam_role, aws_lambda_function, aws_elb, aws_vpc
- Covers security, compliance, and cost categories

**lint_rules.py** (Editable)
- Implement `check_resource(resource: dict) -> list[dict]`
- Returns findings: `[{"severity": "...", "category": "...", "rule_id": "...", "description": "..."}]`
- Scoring: true_positive +severity_points, false_positive -3 points
- Your job: maximize compliance_score while minimizing false positives

**harness.py**
- Loads infra_resources.json (ground truth)
- Executes check_resource() for each resource
- Matches findings against known_issues using fuzzy description matching
- Computes compliance_score and improvement_pct
- Commands: `baseline` (0 score), `evaluate` (your implementation)

**program.md**
- 12 core hypotheses for IaC compliance optimization
- Experiment roadmap: security → compliance → cost optimization
- Expected score progression: 0 → 150 → 250 → 380

## Rule Examples

### S001: Public S3 Bucket
```python
def check_s3_bucket(resource):
    if resource["resource_type"] != "aws_s3_bucket":
        return []

    acl = resource["properties"].get("acl", "")
    if "public-read" in acl or "public-read-write" in acl:
        return [{
            "severity": "critical",
            "category": "security",
            "rule_id": "S001",
            "description": "S3 bucket is publicly readable"
        }]
    return []
```

### S002: Security Group 0.0.0.0/0
```python
def check_security_group(resource):
    if resource["resource_type"] != "aws_security_group":
        return []

    issues = []
    for rule in resource["properties"].get("ingress", []):
        if "0.0.0.0/0" in rule.get("cidr_blocks", []):
            issues.append({
                "severity": "critical",
                "category": "security",
                "rule_id": "S002",
                "description": "Security group allows unrestricted ingress"
            })
            break
    return issues
```

### C008: Missing Tags
```python
def check_tags(resource):
    tags = resource.get("tags", {})
    required = {"Name", "Environment"}
    if not required.issubset(tags.keys()):
        return [{
            "severity": "high",
            "category": "compliance",
            "rule_id": "C008",
            "description": "Resource is missing required tags"
        }]
    return []
```

## Scoring Explained

- **True Positive (TP):** Found real issue → +severity_points (critical=10, high=5, medium=2, low=1)
- **False Positive (FP):** Flagged non-issue → -3 points
- **False Negative (FN):** Missed real issue → 0 points (silent loss)
- **compliance_score = ΣTP - ΣFP×3** (higher is better)
- **improvement_pct = (compliance_score / theoretical_max) × 100%**

## Next Steps

1. Review program.md for 12 core hypotheses
2. Start with security rules (S001-S006)
3. Add compliance rules (C001-C008)
4. Fine-tune cost optimization (CO001-CO002)
5. Run experiments and iterate on lint_rules.py
6. Push results to agent-hub.dev for production validation

## Resources

- **Terraform Docs:** https://www.terraform.io/docs/configuration/
- **AWS Well-Architected Framework:** https://aws.amazon.com/architecture/well-architected/
- **CIS Benchmarks:** https://www.cisecurity.org/cis-benchmarks/
- **Checkov:** https://www.checkov.io/ (reference implementation)

## License

MIT
