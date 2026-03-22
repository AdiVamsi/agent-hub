# Cron Wizard: Optimization Hypotheses

## Baseline Problem
The current 40-job schedule clusters many jobs at the same time (top of hour, midnight, etc.), causing severe resource contention and missed execution windows. Baseline score: ~-200 to -400.

## Target
Optimal schedule with score ~+100 to +300 by eliminating contention and respecting constraints.

---

## Hypothesis 1: Distribute Jobs Across Hours
**Rationale:** Multiple jobs scheduled at :00 of each hour compete for the same resources.
**Action:** Shift jobs to different minutes within each hour (e.g., :05, :10, :15, :20, :25, :30, :35, :40, :45, :50).
**Expected Impact:** Reduce peak contention by spreading execution load.

---

## Hypothesis 2: Separate CPU and IO Jobs
**Rationale:** CPU-heavy jobs (ml-model-train, batch-process-images) and IO-heavy jobs (backup-db-primary, cleanup-logs) compete.
**Action:** Dedicate different hours to CPU vs. IO workloads. E.g., CPU jobs at even hours, IO jobs at odd hours.
**Expected Impact:** Eliminate cross-resource contention; allow each resource to saturate independently.

---

## Hypothesis 3: Respect Dependency Chains
**Rationale:** backup-db-primary must finish before backup-db-replica and database-vacuum can start.
**Action:** Stagger dependencies with gap buffers. E.g., if primary takes 45min and starts at 02:00, schedule replica at 02:50.
**Expected Impact:** Eliminate dependency violation penalties (20 pts per priority each).

---

## Hypothesis 4: Shift Non-Critical Jobs to Off-Peak Hours
**Rationale:** Priority-1 jobs (compress-old-logs, delete-expired-sessions, deep-analytics) are less time-sensitive.
**Action:** Move priority-1 and priority-2 jobs outside preferred windows or to very late hours; protect priority-4/5 slots.
**Expected Impact:** Reduce window-miss penalties for high-priority jobs.

---

## Hypothesis 5: Stagger Backup and Archive Jobs
**Rationale:** backup-db-primary, backup-db-replica, and final-backup all use IO and currently overlap.
**Action:** Schedule backups in sequence with gaps:
  - backup-db-primary: 02:00
  - backup-db-replica: 03:00
  - final-backup: 04:00
**Expected Impact:** Eliminate concurrent IO contention; maintain all backups within preferred windows.

---

## Hypothesis 6: Align with Preferred Windows
**Rationale:** Many jobs have preferred overnight windows (2-6am); some have daytime windows (8-14).
**Action:** Strictly honor preferred_window start/end times. Move jobs that fall outside to nearest in-window slot.
**Expected Impact:** Eliminate all window-miss penalties for on-time execution.

---

## Hypothesis 7: Minimize Concurrent Resource-Weight Sums
**Rationale:** Even if jobs don't share a resource type, high simultaneous weights stress system.
**Action:** Cap concurrent jobs by total weight. E.g., no more than 15 total weight in any 5-minute slot.
**Expected Impact:** Reduce aggregate system stress; lower contention scores.

---

## Hypothesis 8: Prioritize High-Priority Job Placement
**Rationale:** Penalties scale with priority (high-priority misses cost more).
**Action:** Place all priority-5 and priority-4 jobs first in uncongested slots, then fill gaps with lower priorities.
**Expected Impact:** Minimize weighted penalty sum; focus optimization on high-impact jobs.

---

## Hypothesis 9: Batch Similar Jobs Together
**Rationale:** backup jobs, sync jobs, cleanup jobs, and reporting jobs have similar resource profiles.
**Action:** Group jobs by resource type and schedule in bursts (e.g., all network jobs in the 9-11 window).
**Expected Impact:** Improve cache locality and predictability; easier to monitor and forecast.

---

## Hypothesis 10: Exploit Slack in Monitoring and Lightweight Jobs
**Rationale:** health-check (5min, priority 5) and metrics-collection (6min, priority 3) are quick and can fit in gaps.
**Action:** Interleave lightweight monitoring jobs throughout the schedule as gap-fillers without adding contention.
**Expected Impact:** Maintain health visibility without cost; improve utilization of idle slots.

---

## Optimization Experiment Plan
1. **Experiment 1-3:** Test Hypothesis 1 (spreading by minute).
2. **Experiment 4-6:** Test Hypothesis 2 (CPU/IO separation).
3. **Experiment 7-9:** Test Hypotheses 3 & 5 (dependency/backup alignment).
4. **Experiment 10-12:** Test Hypothesis 6 (preferred window alignment).
5. **Experiment 13-15:** Test Hypothesis 7 (weight capacity limits).
6. **Experiment 16-18:** Test Hypothesis 8 (priority-first placement).
7. **Experiment 19-21:** Test Hypothesis 9 (job batching).
8. **Experiment 22-25:** Iterative refinement and combined hypotheses.

**Target:** 15-25 total experiments to converge on optimal schedule.

---

## Constraints
- **Valid cron:** Must use 5-field standard cron syntax (minute hour day month dow).
- **Job IDs:** Must match manifest.
- **Duration:** Jobs cannot be modified; duration is fixed.
- **Resource types:** Cannot change; must work with existing assignments.
- **Dependencies:** Cannot be reordered; must respect completion times.

---

## Success Metric
**schedule_score > +100** indicates successful optimization over baseline.
