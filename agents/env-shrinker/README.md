# Env Shrinker

**Automated cloud infrastructure right-sizing to minimize cost while maintaining performance.**

## Overview

Env Shrinker uses data-driven right-sizing to reduce cloud infrastructure costs by 50-65% while maintaining performance SLAs. It analyzes your cloud resource utilization (EC2, RDS, ElastiCache, Lambda, ECS) and recommends optimal instance types, saving tens of thousands of dollars monthly.

- **Baseline cost**: ~$45-60k/month (60 resources, oversized)
- **Optimal cost**: ~$18-22k/month (through right-sizing)
- **Typical savings**: $25-40k/month (50-65%)

## Features

✅ **Multi-cloud support**: EC2, RDS, ElastiCache, Lambda, ECS
✅ **SLA-aware**: Maintains performance headrooms (CPU 20%, memory 15%)
✅ **Family-consistent**: Downsizes within instance families (m5 → m5, r5 → r5)
✅ **Zero violations**: Harness validates all constraints before accepting recommendations
✅ **Cost-optimized**: Finds cheapest instance type meeting all requirements

## Quick Start

### 1. Generate Infrastructure Inventory
```bash
python prepare.py generate
```
Creates `infra_inventory.json` with 60 cloud resources, current instance types, and utilization metrics.

### 2. Edit Sizing Rules
Edit `sizing_rules.py` to implement your right-sizing strategy. The baseline implementation finds the smallest instance type in each family that meets all SLA constraints.

**Key function**: `right_size(resource, instance_types) -> str`
- Input: resource dict with utilization metrics and SLA requirements
- Output: recommended instance type (as string)
- Constraints: CPU headroom, memory headroom, IOPS, family consistency

### 3. Evaluate Recommendations
```bash
python harness.py
```
Evaluates all recommendations, validates SLA constraints, and reports:
- Total monthly cost after right-sizing
- Improvement percentage vs. baseline
- Any SLA violations (with $100 penalty each)

## Example

**Current resource**:
- Instance: m5.4xlarge (16 vCPU, 64 GB memory, $760/month)
- CPU utilization: avg 18%, p99 38%
- Memory utilization: avg 22%, p99 45%
- SLA: CPU min headroom 20%, memory min headroom 15%

**Right-sizing analysis**:
- CPU requirement: 38% (p99) + 20% (headroom) = 58% → need 1 vCPU
- Memory requirement: 45% (p99) + 15% (headroom) = 60% → need 0.6 GB
- Recommendation: m5.large (2 vCPU, 8 GB, $95/month)
- Savings: $665/month (87%)

## Hypothesis-Driven Optimization

See `program.md` for 8+ research hypotheses:

1. **Downsize by CPU utilization** (30% savings)
2. **Downsize by memory utilization** (15% savings)
3. **Greedy smallest-type selection** (50% combined savings)
4. **Graviton ARM instances** (20% cheaper alternatives)
5. **Spot-eligible workloads** (60-90% discount)
6. **Reserved instances** (30-60% discount)
7. **RDS-specific optimization** (25-45% RDS savings)
8. **Batch similar workloads** (consolidation savings)

## SLA Constraints

Env Shrinker enforces three SLA constraints validated by the harness:

### CPU Constraint
```
cpu_p99_pct + sla_cpu_headroom_pct <= instance_vcpu * 100
```
Ensures p99 CPU utilization plus safety headroom fits within instance capacity.

**Example**: p99=38%, headroom=20%, instance=m5.large (2 vCPU)
- Check: 38 + 20 = 58 <= 2 * 100 = 200 ✅

### Memory Constraint
```
memory_p99_pct + sla_memory_headroom_pct <= instance_memory_gb * 100
```
Ensures p99 memory utilization plus safety headroom fits within instance capacity.

**Example**: p99=45%, headroom=15%, instance=m5.large (8 GB)
- Check: 45 + 15 = 60 <= 8 * 100 = 800 ✅

### IOPS Constraint
```
instance_iops >= sla_min_iops
```
Ensures storage IOPS meet minimum SLA requirements.

### Family Consistency
Downsizing must stay within instance family:
- m5.4xlarge → m5.2xlarge or m5.xlarge (not c5 or r5)
- r5.xlarge → r5.large (not m5 or c5)
- db.m5.xlarge → db.m5.large (not db.r5)

## Cost Model

Instance types include realistic AWS pricing (March 2026):

| Type | vCPU | Memory | IOPS | Monthly |
|------|------|--------|------|---------|
| m5.large | 2 | 8 GB | 3k | $95 |
| m5.xlarge | 4 | 16 GB | 4k | $190 |
| m5.2xlarge | 8 | 32 GB | 8k | $380 |
| m5.4xlarge | 16 | 64 GB | 20k | $760 |
| m6g.large (Graviton) | 2 | 8 GB | 3k | $80 |
| r5.large | 2 | 16 GB | 3k | $150 |
| db.t3.large | 2 | 8 GB | 3k | $232 |
| cache.t3.small | 1 | 2 GB | 1k | $40 |

## Comparable Solutions

| Solution | Price | Features |
|----------|-------|----------|
| **Env Shrinker** | Free (OSS) | Custom rules, multi-cloud, SLA-aware |
| Spot.io | $200/month | Real-time optimization, Spot automation |
| Vantage | $99/month | Cost analysis dashboard, benchmarking |
| CloudHealth | $150/month | Comprehensive FinOps, multi-cloud |
| AWS Compute Optimizer | ~$50/month | AWS-native, EC2-focused |

## Future Integration

### Connect Your AWS Account
[Coming soon](https://agent-hub.dev)

Env Shrinker will integrate with your AWS account via IAM to:
- Automatically fetch real CloudWatch metrics
- Validate recommendations against actual utilization
- Generate AWS CloudFormation templates for safe migration
- Track savings over time

## File Structure

```
env-shrinker/
├── README.md              # This file
├── program.md             # Research hypotheses
├── prepare.py             # Generate infra_inventory.json
├── sizing_rules.py        # Your editable right-sizing logic
├── harness.py             # Evaluate recommendations
├── pyproject.toml         # Python configuration
└── infra_inventory.json   # Generated data (60 resources)
```

## Development

### Running All Checks
```bash
# 1. Generate inventory
python prepare.py generate

# 2. Edit sizing_rules.py with your strategy

# 3. Evaluate
python harness.py
```

### Example Output
```
Generated 60 resources
Baseline monthly cost: $52,345.67
Saved to ./infra_inventory.json

RESULT: total_monthly_cost=$18,456.23 improvement_pct=64.7%
```

## FAQ

**Q: Will right-sizing break my applications?**
A: No. Env Shrinker enforces SLA constraints. If an instance can't be downsized safely, it stays at its current size.

**Q: Can I right-size Lambda and ECS?**
A: Yes. Lambda and ECS use Fargate instance families with vCPU/memory combinations. The harness validates all constraints.

**Q: How often should I re-run optimization?**
A: Monthly. Utilization patterns change seasonally; re-analyze quarterly at minimum.

**Q: What about reserved instances?**
A: Track RI commitments separately. Env Shrinker recommends instance types; on-demand pricing is used for cost calculation. RI discounts are applied separately.

## License

MIT

## Contact

Questions? [agent-hub.dev](https://agent-hub.dev)
