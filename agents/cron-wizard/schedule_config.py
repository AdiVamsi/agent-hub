"""Cron Wizard — editable file.

Available data: job_manifest.json with 40 cron jobs.

Your job: implement optimize_schedule(jobs) -> dict mapping job_id to new cron expression.
Return only jobs you want to reschedule. Omitted jobs keep their current schedule.

The harness simulates 24 hours and checks:
  - Resource contention: penalty for concurrent jobs using same resource type
  - Missed windows: penalty if job starts outside preferred_window
  - Dependency violations: penalty if job starts before its dependency finishes
  - Priority weighting: high-priority missed deadlines cost more

Metric: schedule_score (higher = less contention, fewer misses) — HIGHER is better.
Baseline: return empty dict (keep all current schedules).
"""


def optimize_schedule(jobs: list[dict]) -> dict:
    """Return optimized cron schedules.

    Optimizations:
    1. Fix dependency violations (sync-pricing after sync-inventory, final-backup after nightly-agg)
    2. Fix window misses (backup-db-primary should run 2-6, not 0:00)
    3. Stagger same-resource hourly jobs to eliminate contention
    4. Reduce high-frequency log-aggregation and metrics-collection
    5. Avoid health-check/process-queue cpu conflicts
    6. Skip process-queue during long cpu jobs (ml-model-train hr2, batch-process-images hr3, deep-analytics hr22)
    7. Move daily network jobs to :20 to avoid sync-user-data (:00-:20 every hour)
    8. Move daily io jobs to :15 to avoid cleanup-logs (:00-:15 every hour)
    """
    return {
        # === Fix window misses ===
        # backup-db-primary: window 2-6, move to 2:15 (avoids cleanup-logs at :00-:15)
        "backup-db-primary": "15 2 * * *",
        # backup-db-replica: window 2-7, move to 3:15 (primary done 3:00, avoids cleanup-logs)
        "backup-db-replica": "15 3 * * *",
        # database-vacuum: window 3-7, move to 4:15 (avoids cleanup-logs at 4:00)
        "database-vacuum": "15 4 * * *",
        # index-optimization: window 3-8, move to 5:15 (avoids cleanup-logs at 5:00)
        "index-optimization": "15 5 * * *",
        # delete-expired-sessions: window 17-21, move to 18:15 (avoids cleanup-logs at 18:00)
        "delete-expired-sessions": "15 18 * * *",
        # purge-old-uploads: window 18-22, move to 19:15 (avoids cleanup-logs at 19:00)
        "purge-old-uploads": "15 19 * * *",
        # archive-data: window 7-11 (weekly), move to 8:15 (avoids cleanup-logs at 8:00)
        "archive-data": "15 8 * * 0",

        # === Fix network daily jobs — start at :25 to avoid:
        # 1. sync-user-data (:00-:20 every hour)
        # 2. send-sms-alerts (:22-:27, done by :25) — was 3-way contention at :20
        # At :25, only push-notifications (done :29) overlaps (2-way, cheaper than 3-way at :20)
        # send-reports: window 1-8, move to 1:25
        "send-reports": "25 1 * * *",
        # export-analytics: window 1-8, depends on generate-daily-metrics (done 0:25)
        # keep at 1:50 (avoids sync-inventory skipped at hour 1)
        "export-analytics": "50 1 * * *",
        # preload-cdn: window 7-11, move to 8:25
        "preload-cdn": "25 8 * * *",
        # send-email-digest: window 8-12, move to 9:25
        "send-email-digest": "25 9 * * *",
        # batch-email-send: window 9-13, move to 10:25
        "batch-email-send": "25 10 * * *",
        # batch-sms-send: window 10-14, move to 11:25
        "batch-sms-send": "25 11 * * *",

        # === Fix dependency violations ===
        # final-backup depends on nightly-aggregation (starts 23:00, done 23:35) → start at 23:35
        "final-backup": "35 23 * * *",

        # === Stagger hourly io jobs (no overlap within resource type) ===
        # cleanup-logs (io, 15m): keep at :00 (slots 0-2)
        # cleanup-temp-files (io, 12m): move to :20, skip hours where long io jobs run at :20
        # Skip: 2(backup-primary 2:15-3:00), 3(backup-replica 3:15-3:55),
        #        4(db-vacuum 4:15-4:45), 5(index-opt 5:15-5:40), 8(archive-data 8:15-8:50),
        #        18(delete-sessions 18:15-18:35), 19(purge-uploads 19:15-19:40)
        "cleanup-temp-files": "20 0,1,6,7,9,10,11,12,13,14,15,16,17,20,21,22,23 * * *",
        # log-aggregation (io, 8m): once/hr at :40, skip hours where long io jobs still running at :40
        # Skip: 2(backup-primary until 3:00), 3(backup-replica until 3:55),
        #        4(db-vacuum until 4:45), 8(archive-data until 8:50), 23(final-backup starts 23:35)
        "log-aggregation": "40 0,1,5,6,7,9,10,11,12,13,14,15,16,17,18,19,20,21,22 * * *",

        # === Stagger hourly network jobs ===
        # sync-user-data (network, 20m): keep at :00 (slots 0-3)
        # send-sms-alerts (network, 5m): was :30 → move to :22 (after sync-user-data, before sync-inventory)
        "send-sms-alerts": "22 * * * *",
        # push-notifications (network, 7m): was :30 → move to :22 (done :29)
        "push-notifications": "22 * * * *",
        # sync-inventory (network, 18m): skip hours where daily network jobs overlap (:20-:50 jobs)
        # Skip hours 1(send-reports),8(preload-cdn),9(send-email-digest),10(batch-email-send),11(batch-sms-send)
        "sync-inventory": "30 0,2,3,4,5,6,7,12,13,14,15,16,17,18,19,20,21,22,23 * * *",
        # sync-pricing (network, 15m): depends on sync-inventory (done :48) → :50
        # Skip hours where daily network jobs run and overlap with sync-pricing at :50:
        #   hour 1 (export-analytics 1:50-2:10 overlaps), hour 10 (batch-email-send 10:50+), hour 11 (batch-sms-send ends :50)
        # Dep still satisfied: latest sync-inventory (from any prior non-skipped hour) finishes before :50
        "sync-pricing": "50 0,2,3,4,5,6,7,8,9,12,13,14,15,16,17,18,19,20,21,22,23 * * *",

        # === Stagger hourly memory jobs ===
        # cleanup-cache (memory, 10m): keep at :00 (slots 0-1)
        # metrics-collection (memory, 6m): was */10 → once/hr at :15 (slots 3-4, no overlap)
        "metrics-collection": "15 * * * *",
        # warm-cache (memory, 15m): move to :25 (avoids cleanup-cache at :00-:10 AND metrics at :15-:26)
        # Hour 8 has cleanup-temp-files and log-aggregation skipped, so :25 is clear
        "warm-cache": "25 8 * * *",

        # === Reduce cpu contention ===
        # health-check (cpu, 5m): skip hours with long cpu jobs running at :00/:15
        # Skip: 0(gen-daily-metrics,25m), 2,3(ml-model-train,batch-process-images),
        #        7(compress-old-logs,40m), 20(reconcile-payments,30m), 21(reconcile-inventory,25m),
        #        22(deep-analytics,40m), 23(nightly-aggregation,35m)
        "health-check": "0,15 1,4,5,6,8,9,10,11,12,13,14,15,16,17,18,19 * * *",
        # process-queue (cpu, 25m): skip hours with overlapping long cpu jobs at :30
        # Skip: 2,3(ml-model-train,batch-process-images), 7(compress-old-logs),
        #        20(reconcile-payments done :30 = exact overlap), 22(deep-analytics),
        #        23(nightly-aggregation done :35 overlaps :30 start)
        "process-queue": "30 0,1,4,5,6,8,9,10,11,12,13,14,15,16,17,18,19,21 * * *",
    }
