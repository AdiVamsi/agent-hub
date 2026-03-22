#!/usr/bin/env python3
"""Generate 80 IaC resource definitions with known issues for compliance optimization."""

import json
import random
from pathlib import Path

def generate_resources():
    """Generate 80 IaC resources with 0-4 known issues each."""
    random.seed(42)

    resource_types = [
        "aws_instance",
        "aws_s3_bucket",
        "aws_rds_instance",
        "aws_security_group",
        "aws_iam_role",
        "aws_lambda_function",
        "aws_elb",
        "aws_vpc"
    ]

    regions = ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"]

    def generate_s3_bucket():
        is_public = random.random() < 0.4
        has_encryption = random.random() < 0.6
        has_versioning = random.random() < 0.5
        has_logging = random.random() < 0.3

        props = {
            "bucket": f"data-bucket-{random.randint(1000, 9999)}",
            "acl": "public-read" if is_public else "private",
            "server_side_encryption_configuration": {
                "rule": {
                    "apply_server_side_encryption_by_default": {
                        "sse_algorithm": "AES256"
                    }
                }
            } if has_encryption else {},
            "versioning": {
                "enabled": has_versioning
            } if has_versioning else {},
            "logging": {
                "target_bucket": "log-bucket"
            } if has_logging else {}
        }

        issues = []
        if is_public:
            issues.append({
                "severity": "critical",
                "category": "security",
                "rule_id": "S001",
                "description": "S3 bucket is publicly readable"
            })
        if not has_encryption:
            issues.append({
                "severity": "high",
                "category": "compliance",
                "rule_id": "C001",
                "description": "S3 bucket does not have encryption enabled"
            })
        if not has_logging:
            issues.append({
                "severity": "high",
                "category": "compliance",
                "rule_id": "C002",
                "description": "S3 bucket does not have logging enabled"
            })

        return props, issues

    def generate_instance():
        instance_type = random.choice(["t2.micro", "t2.small", "m5.large", "m5.xlarge", "m5.2xlarge"])
        has_monitoring = random.random() < 0.5
        has_encryption = random.random() < 0.7

        props = {
            "instance_type": instance_type,
            "monitoring": has_monitoring,
            "ebs_block_device": {
                "encrypted": has_encryption
            } if has_encryption else {}
        }

        issues = []
        if instance_type in ["m5.xlarge", "m5.2xlarge"]:
            issues.append({
                "severity": "medium",
                "category": "cost",
                "rule_id": "CO001",
                "description": "Instance type is oversized for typical workload"
            })
        if not has_monitoring:
            issues.append({
                "severity": "high",
                "category": "compliance",
                "rule_id": "C003",
                "description": "Instance monitoring is not enabled"
            })

        return props, issues

    def generate_security_group():
        has_ingress_open = random.random() < 0.35
        has_description = random.random() < 0.6

        ingress_rules = []
        if has_ingress_open:
            ingress_rules.append({
                "from_port": 0,
                "to_port": 65535,
                "protocol": "tcp",
                "cidr_blocks": ["0.0.0.0/0"]
            })
        else:
            ingress_rules.append({
                "from_port": 443,
                "to_port": 443,
                "protocol": "tcp",
                "cidr_blocks": ["10.0.0.0/8"]
            })

        props = {
            "name": f"sg-{random.randint(1000, 9999)}",
            "ingress": ingress_rules,
            "egress": [{"from_port": 0, "to_port": 65535, "protocol": "-1", "cidr_blocks": ["0.0.0.0/0"]}],
            "description": "Security group" if has_description else ""
        }

        issues = []
        if has_ingress_open:
            issues.append({
                "severity": "critical",
                "category": "security",
                "rule_id": "S002",
                "description": "Security group allows unrestricted ingress (0.0.0.0/0)"
            })
        if not has_description:
            issues.append({
                "severity": "low",
                "category": "best-practice",
                "rule_id": "BP001",
                "description": "Security group is missing description"
            })

        return props, issues

    def generate_rds_instance():
        is_publicly_accessible = random.random() < 0.3
        has_encryption = random.random() < 0.65
        has_backup = random.random() < 0.7
        has_multi_az = random.random() < 0.4

        props = {
            "allocated_storage": random.randint(20, 500),
            "engine": random.choice(["mysql", "postgres"]),
            "instance_class": random.choice(["db.t3.micro", "db.t3.small", "db.m5.large"]),
            "publicly_accessible": is_publicly_accessible,
            "storage_encrypted": has_encryption,
            "backup_retention_period": 7 if has_backup else 0,
            "multi_az": has_multi_az
        }

        issues = []
        if is_publicly_accessible:
            issues.append({
                "severity": "critical",
                "category": "security",
                "rule_id": "S003",
                "description": "RDS instance is publicly accessible"
            })
        if not has_encryption:
            issues.append({
                "severity": "critical",
                "category": "security",
                "rule_id": "S004",
                "description": "RDS instance is not encrypted"
            })
        if not has_backup:
            issues.append({
                "severity": "high",
                "category": "compliance",
                "rule_id": "C004",
                "description": "RDS instance does not have backups configured"
            })

        return props, issues

    def generate_iam_role():
        has_wildcard_actions = random.random() < 0.3
        has_wildcard_resources = random.random() < 0.25
        has_principal = random.random() < 0.8

        statements = []
        if has_wildcard_actions or has_wildcard_resources:
            statements.append({
                "Effect": "Allow",
                "Action": ["*"] if has_wildcard_actions else ["s3:GetObject"],
                "Resource": ["*"] if has_wildcard_resources else ["arn:aws:s3:::my-bucket/*"]
            })
        else:
            statements.append({
                "Effect": "Allow",
                "Action": ["ec2:DescribeInstances"],
                "Resource": ["*"]
            })

        props = {
            "name": f"role-{random.randint(1000, 9999)}",
            "assume_role_policy": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "ec2.amazonaws.com"} if has_principal else {},
                        "Action": "sts:AssumeRole"
                    }
                ]
            } if has_principal else {},
            "inline_policy": {
                "policy": json.dumps({"Statement": statements})
            }
        }

        issues = []
        if has_wildcard_actions:
            issues.append({
                "severity": "critical",
                "category": "security",
                "rule_id": "S005",
                "description": "IAM role allows all actions (*)"
            })
        if has_wildcard_resources:
            issues.append({
                "severity": "critical",
                "category": "security",
                "rule_id": "S006",
                "description": "IAM role allows access to all resources (*)"
            })
        if not has_principal:
            issues.append({
                "severity": "high",
                "category": "compliance",
                "rule_id": "C005",
                "description": "IAM role is missing principal definition"
            })

        return props, issues

    def generate_lambda_function():
        has_timeout = random.random() < 0.7
        has_env_vars = random.random() < 0.5
        has_vpc = random.random() < 0.4
        timeout_val = random.randint(3, 900) if has_timeout else None

        props = {
            "filename": "lambda.zip",
            "function_name": f"func-{random.randint(1000, 9999)}",
            "role": "arn:aws:iam::123456789012:role/lambda-role",
            "handler": "index.handler",
            "runtime": "python3.9",
            "timeout": timeout_val if has_timeout else 3
        }

        if has_env_vars:
            props["environment"] = {"variables": {"KEY": "value"}}

        if has_vpc:
            props["vpc_config"] = {
                "subnet_ids": ["subnet-12345"],
                "security_group_ids": ["sg-12345"]
            }

        issues = []
        if timeout_val and timeout_val < 10:
            issues.append({
                "severity": "medium",
                "category": "compliance",
                "rule_id": "C006",
                "description": "Lambda function timeout is too short"
            })
        if not has_vpc:
            issues.append({
                "severity": "low",
                "category": "best-practice",
                "rule_id": "BP002",
                "description": "Lambda function is not running in VPC"
            })

        return props, issues

    def generate_elb():
        has_security_groups = random.random() < 0.7
        has_logging = random.random() < 0.35
        has_instances = random.random() < 0.65

        props = {
            "name": f"elb-{random.randint(1000, 9999)}",
            "availability_zones": random.sample(regions[:2], 1),
            "listener": {
                "instance_port": 80,
                "instance_protocol": "HTTP",
                "lb_port": 80,
                "lb_protocol": "HTTP"
            },
            "security_groups": ["sg-12345"] if has_security_groups else [],
            "access_logs": {
                "bucket": "log-bucket"
            } if has_logging else {},
            "instances": ["i-1234567"] if has_instances else []
        }

        issues = []
        if not has_instances:
            issues.append({
                "severity": "medium",
                "category": "cost",
                "rule_id": "CO002",
                "description": "Load balancer has no instances attached (idle)"
            })
        if not has_logging:
            issues.append({
                "severity": "high",
                "category": "compliance",
                "rule_id": "C007",
                "description": "Load balancer does not have access logging enabled"
            })

        return props, issues

    def generate_vpc():
        has_tags = random.random() < 0.5

        props = {
            "cidr_block": f"10.{random.randint(0, 255)}.0.0/16",
            "enable_dns_hostnames": random.random() < 0.7,
            "enable_dns_support": random.random() < 0.8,
            "tags": {
                "Name": "my-vpc",
                "Environment": "prod"
            } if has_tags else {}
        }

        issues = []
        if not has_tags:
            issues.append({
                "severity": "high",
                "category": "compliance",
                "rule_id": "C008",
                "description": "VPC is missing required tags"
            })

        return props, issues

    generators = {
        "aws_s3_bucket": generate_s3_bucket,
        "aws_instance": generate_instance,
        "aws_security_group": generate_security_group,
        "aws_rds_instance": generate_rds_instance,
        "aws_iam_role": generate_iam_role,
        "aws_lambda_function": generate_lambda_function,
        "aws_elb": generate_elb,
        "aws_vpc": generate_vpc
    }

    resources = []
    for i in range(80):
        resource_type = resource_types[i % len(resource_types)]
        props, issues = generators[resource_type]()

        resource = {
            "resource_id": f"res-{i:03d}",
            "resource_type": resource_type,
            "properties": props,
            "tags": {
                "Name": f"resource-{i}",
                "Environment": random.choice(["dev", "staging", "prod"])
            },
            "region": random.choice(regions),
            "monthly_cost_estimate": round(random.uniform(10, 500), 2),
            "known_issues": issues
        }
        resources.append(resource)

    return {"resources": resources}

def main():
    import sys

    if len(sys.argv) < 2 or sys.argv[1] != "generate":
        print("Usage: python prepare.py generate")
        sys.exit(1)

    output_dir = Path(__file__).parent
    data = generate_resources()

    output_file = output_dir / "infra_resources.json"
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Generated {len(data['resources'])} resources to {output_file}")
    total_issues = sum(len(r["known_issues"]) for r in data["resources"])
    print(f"Total known issues: {total_issues}")

if __name__ == "__main__":
    main()
