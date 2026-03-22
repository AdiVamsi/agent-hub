# Env Shrinker — Right-Sizing Algorithm Research

## Objective
Minimize cloud infrastructure monthly costs while maintaining performance SLAs (Service Level Agreements). Currently managing 60+ cloud resources across EC2, RDS, ElastiCache, Lambda, and ECS. Baseline cost ~$45-60k/month. Goal: reduce to $15-25k/month through intelligent right-sizing.

## Available Data
- **infra_inventory.json**: 60 resources with current instance types, monthly costs, and performance metrics
  - CPU utilization (avg %, p99 %)
  - Memory utilization (avg %, p99 %)
  - Network bandwidth (Mbps avg)
  - Storage IOPS (avg)
  - SLA requirements: min CPU headroom (20%), min memory headroom (15%), min IOPS
- **instance_types catalog**: All AWS instance types with specs (vCPU, memory, network, IOPS, cost)

## Constraints
- **CPU**: `cpu_p99 + sla_cpu_headroom_pct <= instance_vcpu * 100`
- **Memory**: `memory_p99 + sla_memory_headroom_pct <= instance_memory_gb * 100`
- **IOPS**: `instance_iops >= sla_min_iops`
- **Family consistency**: Must stay within instance family (m5 → m5, r5 → r5, etc.)

## Success Metric
**Total monthly cost** after right-sizing. Lower is better.
- Baseline: ~$45-60k/month (keeping all current types)
- Target: ~$15-25k/month (aggressive right-sizing)
- Headroom: 15-25 experiments

## Hypotheses to Test

### 1. Downsize by CPU Utilization
Many resources show low CPU avg (5-25%) and p99 (20-40%). Moving from m5.4xlarge (16 vCPU) to m5.2xlarge (8 vCPU) or m5.xlarge (4 vCPU) could cut costs 50-75% while maintaining SLAs.

**Strategy**: For each resource, find the smallest instance in the same family where:
- `cpu_p99 + 20% <= vcpu * 100`
- Other constraints still met

**Expected savings**: 20-35%

---

### 2. Downsize by Memory Utilization
Many resources show low memory avg (10-35%) and p99 (25-50%). Especially beneficial for:
- EC2 general-purpose (m5, m6i) using 30% of available memory
- RDS instances with conservative allocation

**Strategy**: Target resources where `memory_p99 + 15% <= 50 * memory_gb`. Move down 1-2 size tiers.

**Expected savings**: 10-20%

---

### 3. Find Smallest Type Meeting All SLAs
For each resource, enumerate all instance types in the same family. Filter to those meeting:
- CPU constraint
- Memory constraint
- IOPS constraint

Return the cheapest option.

**Strategy**: Greedy approach — always pick minimum cost instance that doesn't violate SLAs.

**Expected savings**: 30-50% (combines CPU and memory optimization)

---

### 4. Graviton (ARM) Instances
AWS Graviton-based instances (t4g, m6g, c6g, r6g) are ~20% cheaper than Intel/AMD equivalents with same specs.

**Prerequisites**: Application must be Graviton-compatible (most are).

**Strategy**: For resources currently on Intel, try same-size Graviton variant:
- m5.large (95/mo) → m6g.large (80/mo)
- r5.xlarge (300/mo) → r6g.xlarge (240/mo)

**Expected savings**: 15-25% for compatible workloads

---

### 5. Spot-Eligible Workloads
Spot instances are 60-90% cheaper but require fault-tolerance (batch, stateless, queue-based).

**Strategy**: Identify resources that can tolerate interruption:
- Lambda (inherently ephemeral)
- ECS tasks with auto-restart
- Batch processing jobs
- Non-critical caches

**Expected savings**: 40-70% for eligible resources

---

### 6. Reserved Instances (RI) Pricing
1-year RIs: 30-40% discount vs. On-Demand
3-year RIs: 50-60% discount

**Strategy**: For stable, predictable workloads (prod databases, critical services), commit to RIs.

**Expected savings**: 20-40% for stable workloads

---

### 7. Right-Size RDS Separately
RDS instances often over-provisioned. Optimization:
- **CPU-limited**: Downsize from db.m5.large to db.t3.large
- **Memory-limited**: Switch to db.r5.* family
- **Burst workloads**: Use db.t3.* with credit system

**Strategy**: For RDS, more aggressive downsizing acceptable (t3 burstable often sufficient).

**Expected savings**: 25-45% for RDS

---

### 8. Batch Similar Workloads
Consolidate similar resources to reduce management overhead and enable volume discounts.

**Strategy**:
- Group EC2 instances by workload (web servers, workers, caches)
- Consolidate to fewer, larger instances or managed services (ALB, managed cache)
- Use auto-scaling groups instead of fixed sizing

**Expected savings**: 10-30% + operational simplification

---

## Next Steps
1. **Baseline**: Confirm current sizing with no changes (~$45-60k/month)
2. **Hypothesis 1-3**: Test conservative CPU/memory downsizing
3. **Hypothesis 4**: Evaluate Graviton compatibility
4. **Hypothesis 5-8**: Advanced cost optimization (Spot, RI, consolidation)
5. **Iterate**: Refine sizing_rules based on metrics

## Optimal Target
- **Total monthly cost**: $18-22k (60% reduction)
- **Improvement**: 55-65%
- **Key drivers**: CPU downsizing (30%), memory optimization (15%), Graviton migration (10%), consolidation (10%)
