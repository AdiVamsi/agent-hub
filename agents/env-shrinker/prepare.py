#!/usr/bin/env python3
"""
Prepare: Generate infra_inventory.json with 60 cloud resources.
Implements Karpathy's AutoResearch pattern: data -> hypothesis -> experiment -> optimize.
"""

import json
import random
from pathlib import Path


def generate_inventory():
    """Generate realistic cloud infrastructure inventory with right-sizing opportunities."""
    random.seed(42)

    # Instance type catalog: realistic AWS pricing and specs (March 2026)
    instance_types = {
        # M-series (general purpose, baseline)
        "m5.large": {"vcpu": 2, "memory_gb": 8, "network_gbps": 10, "iops": 3000, "monthly_cost": 95.00},
        "m5.xlarge": {"vcpu": 4, "memory_gb": 16, "network_gbps": 10, "iops": 4000, "monthly_cost": 190.00},
        "m5.2xlarge": {"vcpu": 8, "memory_gb": 32, "network_gbps": 10, "iops": 8000, "monthly_cost": 380.00},
        "m5.4xlarge": {"vcpu": 16, "memory_gb": 64, "network_gbps": 10, "iops": 20000, "monthly_cost": 760.00},
        "m6i.large": {"vcpu": 2, "memory_gb": 8, "network_gbps": 10, "iops": 3000, "monthly_cost": 100.00},
        "m6i.xlarge": {"vcpu": 4, "memory_gb": 16, "network_gbps": 10, "iops": 4000, "monthly_cost": 200.00},
        "m6i.2xlarge": {"vcpu": 8, "memory_gb": 32, "network_gbps": 10, "iops": 8000, "monthly_cost": 400.00},

        # R-series (memory-optimized)
        "r5.large": {"vcpu": 2, "memory_gb": 16, "network_gbps": 10, "iops": 3000, "monthly_cost": 150.00},
        "r5.xlarge": {"vcpu": 4, "memory_gb": 32, "network_gbps": 10, "iops": 4000, "monthly_cost": 300.00},
        "r5.2xlarge": {"vcpu": 8, "memory_gb": 64, "network_gbps": 10, "iops": 8000, "monthly_cost": 600.00},
        "r5.4xlarge": {"vcpu": 16, "memory_gb": 128, "network_gbps": 10, "iops": 20000, "monthly_cost": 1200.00},

        # C-series (compute-optimized)
        "c5.large": {"vcpu": 2, "memory_gb": 4, "network_gbps": 10, "iops": 3000, "monthly_cost": 85.00},
        "c5.xlarge": {"vcpu": 4, "memory_gb": 8, "network_gbps": 10, "iops": 4000, "monthly_cost": 170.00},
        "c5.2xlarge": {"vcpu": 8, "memory_gb": 16, "network_gbps": 10, "iops": 8000, "monthly_cost": 340.00},
        "c6i.large": {"vcpu": 2, "memory_gb": 4, "network_gbps": 10, "iops": 3000, "monthly_cost": 90.00},
        "c6i.xlarge": {"vcpu": 4, "memory_gb": 8, "network_gbps": 10, "iops": 4000, "monthly_cost": 180.00},

        # T-series (burstable, cheaper for variable workloads)
        "t3.medium": {"vcpu": 1, "memory_gb": 4, "network_gbps": 5, "iops": 1000, "monthly_cost": 30.00},
        "t3.large": {"vcpu": 2, "memory_gb": 8, "network_gbps": 5, "iops": 2000, "monthly_cost": 60.00},

        # Graviton (ARM-based, 20% cheaper)
        "t4g.medium": {"vcpu": 1, "memory_gb": 4, "network_gbps": 5, "iops": 1000, "monthly_cost": 24.00},
        "t4g.large": {"vcpu": 2, "memory_gb": 8, "network_gbps": 5, "iops": 2000, "monthly_cost": 48.00},
        "m6g.large": {"vcpu": 2, "memory_gb": 8, "network_gbps": 10, "iops": 3000, "monthly_cost": 80.00},
        "m6g.xlarge": {"vcpu": 4, "memory_gb": 16, "network_gbps": 10, "iops": 4000, "monthly_cost": 160.00},
        "m6g.2xlarge": {"vcpu": 8, "memory_gb": 32, "network_gbps": 10, "iops": 8000, "monthly_cost": 320.00},

        # RDS instances
        "db.t3.micro": {"vcpu": 1, "memory_gb": 1, "network_gbps": 1, "iops": 1000, "monthly_cost": 29.00},
        "db.t3.small": {"vcpu": 1, "memory_gb": 2, "network_gbps": 1, "iops": 1000, "monthly_cost": 58.00},
        "db.t3.medium": {"vcpu": 1, "memory_gb": 4, "network_gbps": 1, "iops": 1000, "monthly_cost": 116.00},
        "db.t3.large": {"vcpu": 2, "memory_gb": 8, "network_gbps": 1, "iops": 3000, "monthly_cost": 232.00},
        "db.m5.large": {"vcpu": 2, "memory_gb": 8, "network_gbps": 1, "iops": 3000, "monthly_cost": 210.00},
        "db.m5.xlarge": {"vcpu": 4, "memory_gb": 16, "network_gbps": 1, "iops": 4000, "monthly_cost": 420.00},
        "db.r5.large": {"vcpu": 2, "memory_gb": 16, "network_gbps": 1, "iops": 3000, "monthly_cost": 350.00},
        "db.r5.xlarge": {"vcpu": 4, "memory_gb": 32, "network_gbps": 1, "iops": 4000, "monthly_cost": 700.00},

        # ElastiCache instances
        "cache.t3.micro": {"vcpu": 1, "memory_gb": 1, "network_gbps": 1, "iops": 1000, "monthly_cost": 20.00},
        "cache.t3.small": {"vcpu": 1, "memory_gb": 2, "network_gbps": 1, "iops": 1000, "monthly_cost": 40.00},
        "cache.m5.large": {"vcpu": 2, "memory_gb": 6.12, "network_gbps": 1, "iops": 3000, "monthly_cost": 160.00},
        "cache.m5.xlarge": {"vcpu": 4, "memory_gb": 12.24, "network_gbps": 1, "iops": 4000, "monthly_cost": 320.00},
        "cache.r5.large": {"vcpu": 2, "memory_gb": 16, "network_gbps": 1, "iops": 3000, "monthly_cost": 240.00},
        "cache.r5.xlarge": {"vcpu": 4, "memory_gb": 32, "network_gbps": 1, "iops": 4000, "monthly_cost": 480.00},

        # ECS/Fargate (vCPU * memory)
        "fargate_0.25": {"vcpu": 0.25, "memory_gb": 0.5, "network_gbps": 1, "iops": 100, "monthly_cost": 10.00},
        "fargate_0.5": {"vcpu": 0.5, "memory_gb": 1, "network_gbps": 1, "iops": 100, "monthly_cost": 20.00},
        "fargate_1": {"vcpu": 1, "memory_gb": 2, "network_gbps": 1, "iops": 100, "monthly_cost": 40.00},
        "fargate_2": {"vcpu": 2, "memory_gb": 4, "network_gbps": 1, "iops": 100, "monthly_cost": 80.00},
        "fargate_4": {"vcpu": 4, "memory_gb": 8, "network_gbps": 1, "iops": 100, "monthly_cost": 160.00},
    }

    regions = ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"]
    resource_types = ["ec2", "rds", "elasticache", "lambda", "ecs"]

    resources = []
    resource_id_counter = {"ec2": 1, "rds": 1, "elasticache": 1, "lambda": 1, "ecs": 1}

    # Generate 60 resources with varied sizing patterns
    for _ in range(60):
        rtype = random.choice(resource_types)
        counter = resource_id_counter[rtype]
        resource_id_counter[rtype] += 1

        region = random.choice(regions)

        # Choose current instance type based on resource type
        if rtype == "ec2":
            current_type = random.choice([
                "m5.large", "m5.xlarge", "m5.2xlarge", "m5.4xlarge",
                "c5.large", "c5.xlarge", "c5.2xlarge",
                "r5.large", "r5.xlarge", "r5.2xlarge",
                "t3.medium", "t3.large",
                "m6g.large", "m6g.xlarge", "m6g.2xlarge",
            ])
        elif rtype == "rds":
            current_type = random.choice([
                "db.t3.micro", "db.t3.small", "db.t3.medium", "db.t3.large",
                "db.m5.large", "db.m5.xlarge", "db.r5.large", "db.r5.xlarge",
            ])
        elif rtype == "elasticache":
            current_type = random.choice([
                "cache.t3.micro", "cache.t3.small", "cache.m5.large", "cache.m5.xlarge",
                "cache.r5.large", "cache.r5.xlarge",
            ])
        elif rtype == "lambda":
            current_type = random.choice([
                "fargate_0.25", "fargate_0.5", "fargate_1", "fargate_2", "fargate_4"
            ])
        else:  # ecs
            current_type = random.choice([
                "fargate_0.5", "fargate_1", "fargate_2", "fargate_4"
            ])

        specs = instance_types[current_type]

        # Simulate realistic utilization patterns
        # Generate CPU and memory p99 that respect the current instance size
        max_cpu_p99 = int(specs["vcpu"] * 100 - 20)  # Leave headroom
        max_memory_p99 = int(specs["memory_gb"] * 100 - 15)

        # Many resources are oversized: low CPU/memory, high cost
        if random.random() < 0.4:  # 40% oversized resources
            cpu_avg = random.randint(5, min(25, max(5, max_cpu_p99)))
            cpu_p99 = random.randint(20, min(40, max(20, max_cpu_p99)))
        elif random.random() < 0.3:  # 30% correctly sized
            cpu_avg = random.randint(40, min(70, max(40, max_cpu_p99)))
            cpu_p99 = random.randint(75, min(95, max(75, max_cpu_p99)))
        else:  # 30% undersized or variable
            cpu_avg = random.randint(15, max(15, max_cpu_p99))
            cpu_p99 = random.randint(30, max(30, max_cpu_p99))

        if random.random() < 0.4:  # 40% oversized memory
            memory_avg = random.randint(10, min(35, max(10, max_memory_p99)))
            memory_p99 = random.randint(25, min(50, max(25, max_memory_p99)))
        elif random.random() < 0.3:  # 30% correctly sized
            memory_avg = random.randint(50, min(75, max(50, max_memory_p99)))
            memory_p99 = random.randint(80, min(95, max(80, max_memory_p99)))
        else:  # 30% variable
            memory_avg = random.randint(15, max(15, max_memory_p99))
            memory_p99 = random.randint(30, max(30, max_memory_p99))

        # Ensure p99 >= avg
        cpu_p99 = max(cpu_p99, cpu_avg)
        memory_p99 = max(memory_p99, memory_avg)

        network_mbps = random.randint(50, 500) if rtype == "ec2" else random.randint(10, 100)
        # IOPS are realistic to current instance baseline, not exaggerated
        if rtype in ["rds", "ec2"]:
            storage_iops = specs["iops"] * random.uniform(0.1, 0.8)
        else:
            storage_iops = specs["iops"] * random.uniform(0.1, 0.6)

        resource = {
            "resource_id": f"{rtype}-server-{counter}",
            "resource_type": rtype,
            "region": region,
            "current_instance_type": current_type,
            "monthly_cost_usd": specs["monthly_cost"],
            "cpu_avg_pct": cpu_avg,
            "cpu_p99_pct": cpu_p99,
            "memory_avg_pct": memory_avg,
            "memory_p99_pct": memory_p99,
            "network_mbps_avg": network_mbps,
            "storage_iops_avg": storage_iops,
            "sla_cpu_headroom_pct": 20,
            "sla_memory_headroom_pct": 15,
            "sla_min_iops": storage_iops,  # Current utilization is the minimum required
        }
        resources.append(resource)

    inventory = {
        "resources": resources,
        "instance_types": instance_types,
        "metadata": {
            "total_resources": len(resources),
            "baseline_monthly_cost": sum(r["monthly_cost_usd"] for r in resources),
            "generated_with_seed": 42,
        }
    }

    return inventory


def main():
    import sys

    if len(sys.argv) < 2 or sys.argv[1] != "generate":
        print("Usage: python prepare.py generate")
        sys.exit(1)

    output_dir = Path(__file__).parent
    inventory = generate_inventory()

    output_file = output_dir / "infra_inventory.json"
    with open(output_file, "w") as f:
        json.dump(inventory, f, indent=2)

    print(f"Generated {len(inventory['resources'])} resources")
    print(f"Baseline monthly cost: ${inventory['metadata']['baseline_monthly_cost']:,.2f}")
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
