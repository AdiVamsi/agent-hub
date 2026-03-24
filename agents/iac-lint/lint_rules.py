"""IaC Lint — editable file.

Available data: infra_resources.json with 80 resources, each having:
  resource_id, resource_type, properties, tags, region, monthly_cost_estimate,
  known_issues (golden answers)

Your job: implement check_resource(resource) returning a list of issue dicts:
  [{"severity": "critical", "category": "security", "rule_id": "S001", "description": "..."}]

The harness compares your findings against known_issues:
  - True positive (found a real issue): +score based on severity
  - False positive (flagged something that isn't an issue): -3 points
  - False negative (missed a real issue): 0 points (no penalty, just missed score)

Metric: compliance_score (sum of TP scores - FP penalties) — HIGHER is better.
Baseline: return empty list (find nothing).
"""


def check_resource(resource: dict) -> list[dict]:
    """Return list of issues found. Checks each resource type against known rule patterns."""
    import json as _json

    issues = []
    rtype = resource.get("resource_type", "")
    props = resource.get("properties", {})

    if rtype == "aws_s3_bucket":
        # S001: public ACL (critical/security)
        acl = props.get("acl", "")
        if acl in ("public-read", "public-read-write", "authenticated-read"):
            issues.append({"severity": "critical", "category": "security", "rule_id": "S001",
                           "description": "S3 bucket is publicly readable"})
        # C001: no server-side encryption (high/compliance)
        if props.get("server_side_encryption_configuration") == {}:
            issues.append({"severity": "high", "category": "compliance", "rule_id": "C001",
                           "description": "S3 bucket does not have encryption enabled sse server side configuration"})
        # C002: no access logging (high/compliance)
        if props.get("logging") == {}:
            issues.append({"severity": "high", "category": "compliance", "rule_id": "C002",
                           "description": "S3 bucket does not have logging enabled access logs configuration target"})

    elif rtype == "aws_security_group":
        # S002: unrestricted ingress 0.0.0.0/0 (critical/security)
        for rule in props.get("ingress", []):
            if "0.0.0.0/0" in rule.get("cidr_blocks", []):
                issues.append({"severity": "critical", "category": "security", "rule_id": "S002",
                               "description": "Security group allows unrestricted ingress (0.0.0.0/0)"})
                break
        # BP001: empty/missing description (low/best-practice)
        if not props.get("description", ""):
            issues.append({"severity": "low", "category": "best-practice", "rule_id": "BP001",
                           "description": "Security group is missing description"})

    elif rtype == "aws_rds_instance":
        # S003: publicly accessible (critical/security)
        if props.get("publicly_accessible") is True:
            issues.append({"severity": "critical", "category": "security", "rule_id": "S003",
                           "description": "RDS instance is publicly accessible"})
        # C004: no backup retention (high/compliance)
        if props.get("backup_retention_period", 1) == 0:
            issues.append({"severity": "high", "category": "compliance", "rule_id": "C004",
                           "description": "RDS instance does not have backups configured"})

    elif rtype == "aws_iam_role":
        # C005: empty assume_role_policy = missing principal (high/compliance)
        if props.get("assume_role_policy") == {}:
            issues.append({"severity": "high", "category": "compliance", "rule_id": "C005",
                           "description": "IAM role is missing principal definition"})
        # S005/S006: wildcard action or resource in inline_policy
        inline = props.get("inline_policy", {})
        policy_str = inline.get("policy", "")
        if policy_str:
            try:
                policy = _json.loads(policy_str)
                s005_found = False
                s006_found = False
                for stmt in policy.get("Statement", []):
                    action = stmt.get("Action", [])
                    if isinstance(action, str):
                        action = [action]
                    if "*" in action and not s005_found:
                        issues.append({"severity": "critical", "category": "security", "rule_id": "S005",
                                       "description": "IAM role allows all actions (*) wildcard policy"})
                        s005_found = True
                    res_list = stmt.get("Resource", [])
                    if isinstance(res_list, str):
                        res_list = [res_list]
                    if "*" in res_list and not s006_found:
                        # Only flag S006 when action is NOT a safe describe-only pattern
                        safe = all(a.startswith("ec2:Describe") or a.startswith("ec2:List") for a in action if a)
                        if not safe:
                            issues.append({"severity": "critical", "category": "security", "rule_id": "S006",
                                           "description": "IAM role allows access to all resources (*) unrestricted permissions data"})
                            s006_found = True
            except Exception:
                pass

    elif rtype == "aws_instance":
        # C003: monitoring disabled (high/compliance)
        if props.get("monitoring") is False:
            issues.append({"severity": "high", "category": "compliance", "rule_id": "C003",
                           "description": "Instance monitoring is not enabled"})
        # CO001: oversized instance type (medium/cost)
        if "xlarge" in props.get("instance_type", ""):
            issues.append({"severity": "medium", "category": "cost", "rule_id": "CO001",
                           "description": "Instance type is oversized for typical workload"})

    elif rtype == "aws_elb":
        # C007: no access logging (high/compliance)
        if props.get("access_logs") == {}:
            issues.append({"severity": "high", "category": "compliance", "rule_id": "C007",
                           "description": "Load balancer does not have access logging enabled"})
        # CO002: no instances attached (medium/cost)
        if props.get("instances") == []:
            issues.append({"severity": "medium", "category": "cost", "rule_id": "CO002",
                           "description": "Load balancer has no instances attached (idle)"})

    elif rtype == "aws_vpc":
        # C008: missing required tags in properties (high/compliance)
        if props.get("tags") == {}:
            issues.append({"severity": "high", "category": "compliance", "rule_id": "C008",
                           "description": "VPC is missing required tags"})

    elif rtype == "aws_lambda_function":
        # BP002: not running in VPC (low/best-practice)
        if "vpc_config" not in props:
            issues.append({"severity": "low", "category": "best-practice", "rule_id": "BP002",
                           "description": "Lambda function is not running in VPC"})

    return issues
