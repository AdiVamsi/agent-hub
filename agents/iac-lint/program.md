# IaC-Lint AutoResearch Program

## Objective
Optimize Infrastructure-as-Code (IaC) security and cost compliance rules to detect misconfigurations in Terraform resource definitions. Maximize `compliance_score` by identifying true security issues, cost overruns, and compliance violations while minimizing false positives.

## Baseline
- **Current Score:** 0 (returns empty list, finds nothing)
- **Theoretical Maximum:** ~380 points (all issues caught at their severity weights)
- **Target Range:** 300-400 points over 15-25 experiments

## Hypotheses

### 1. S3 Public Access Detection (S001)
**Rule:** Detect S3 buckets with public-read or public-read-write ACLs.
- Check `properties.acl` for "public-read", "public-read-write", "authenticated-read"
- Severity: critical (10 points each)
- Expected true positives: ~10-12 buckets across 80 resources

### 2. Security Group Unrestricted Ingress (S002)
**Rule:** Detect security groups with CIDR block 0.0.0.0/0 on ingress rules.
- Check `properties.ingress[].cidr_blocks` for "0.0.0.0/0"
- Severity: critical (10 points)
- Expected true positives: ~9-10 security groups

### 3. RDS Public Accessibility (S003)
**Rule:** Detect RDS instances set to publicly accessible.
- Check `properties.publicly_accessible == true`
- Severity: critical (10 points)
- Expected true positives: ~6-8 instances

### 4. RDS Encryption Check (S004)
**Rule:** Detect RDS instances without storage encryption.
- Check `properties.storage_encrypted != true`
- Severity: critical (10 points)
- Expected true positives: ~6-8 instances

### 5. IAM Wildcard Actions (S005)
**Rule:** Detect IAM roles allowing all actions (*).
- Parse `properties.inline_policy.policy` JSON for Action: ["*"]
- Severity: critical (10 points)
- Expected true positives: ~5-6 roles

### 6. IAM Wildcard Resources (S006)
**Rule:** Detect IAM roles with unrestricted resource access.
- Parse policy JSON for Resource: ["*"]
- Severity: critical (10 points)
- Expected true positives: ~5-6 roles

### 7. Missing Tag Enforcement (C008)
**Rule:** Detect resources missing required tags (e.g., Environment, Name).
- Check if `tags` dict is empty or missing critical keys
- Severity: high (5 points)
- Expected true positives: ~8-10 VPCs, several other resource types

### 8. RDS Backup Configuration (C004)
**Rule:** Detect RDS instances without backup configuration.
- Check `properties.backup_retention_period > 0`
- Severity: high (5 points)
- Expected true positives: ~6-8 instances

### 9. Encryption Check (C001)
**Rule:** Detect S3 buckets without encryption.
- Check if `properties.server_side_encryption_configuration` is missing or empty
- Severity: high (5 points)
- Expected true positives: ~8-12 buckets

### 10. Load Balancer Access Logging (C007)
**Rule:** Detect ELBs without access logging enabled.
- Check `properties.access_logs` for bucket configuration
- Severity: high (5 points)
- Expected true positives: ~5-6 load balancers

### 11. Load Balancer Instance Attachment (CO002)
**Rule:** Detect idle load balancers with no instances.
- Check `properties.instances` for empty list or missing field
- Severity: medium (2 points)
- Expected true positives: ~5-6 load balancers

### 12. Instance Right-Sizing (CO001)
**Rule:** Detect oversized EC2 instances for cost optimization.
- Flag instances with type m5.xlarge, m5.2xlarge as potentially oversized
- Severity: medium (2 points)
- Expected true positives: ~8-10 instances

## Experiment Strategy
1. **Rounds 1-5:** Implement core security rules (S001-S006) — expect 150-200 points
2. **Rounds 6-10:** Add compliance rules (C001-C008) — expect +80-120 points
3. **Rounds 11-15:** Add cost optimization rules (CO001-CO002) — expect +30-50 points
4. **Rounds 16-25:** Refine matching logic, reduce false positives, edge cases

## Anti-Gaming Rules
- Findings must have valid severity (critical, high, medium, low)
- Finding description must be non-empty
- Each true positive is scored only once per resource
- False positive penalty: -3 points per invalid finding
