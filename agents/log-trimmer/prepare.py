#!/usr/bin/env python3
"""Log Trimmer — Data Preparation.

Generates log_samples.json with 500 realistic log entries.
Each entry: message, level, source, timestamp, size_bytes, is_signal.
"""

import json
import random
from datetime import datetime, timedelta

def generate():
    """Generate 500 log entries and save to log_samples.json."""
    random.seed(42)

    # Configuration
    num_logs = 500
    sources = ["api", "db", "auth", "cache", "scheduler", "worker"]

    # Level distribution: 40% DEBUG, 30% INFO, 15% WARN, 10% ERROR, 5% FATAL
    levels = (
        ["DEBUG"] * 200 +
        ["INFO"] * 150 +
        ["WARN"] * 75 +
        ["ERROR"] * 50 +
        ["FATAL"] * 25
    )
    random.shuffle(levels)

    # Signal keywords for detection
    warn_signal_keywords = ["timeout", "retry", "circuit"]
    info_signal_keywords = ["deploy", "startup", "shutdown", "user_created"]

    logs = []
    base_time = datetime(2026, 3, 20, 0, 0, 0)

    # Debug message templates (mostly noise)
    debug_messages = [
        "Request received from client",
        "Cache miss for key: {}",
        "Database query executed in 5ms",
        "JSON parsing completed",
        "Function foo() called with args",
        "Variable x = 42",
        "Loop iteration {}",
        "Config loaded from file",
        "Memory usage: {}MB",
        "Thread pool size: {}",
        "Processed batch of {} items",
        "Health check passed",
        "Heartbeat from worker node",
        "Cache hit for key",
        "No errors detected",
        "Request completed successfully",
        "Slow query detected: {} ms",
    ]

    # Info message templates
    info_messages = [
        "Server startup initiated",
        "User created: user_{}",
        "Deployment started for version 1.2.3",
        "Service shutdown gracefully",
        "Configuration reloaded",
        "Background job scheduled",
        "API endpoint available at /health",
        "Database migration completed",
        "Session established for user_{}",
        "Cache cleared",
    ]

    # Warning message templates
    warn_messages = [
        "Request timeout after 30s",
        "Retry attempt {} for operation",
        "Circuit breaker opened",
        "High memory usage detected",
        "Slow query detected: {} ms",
        "Rate limit approaching",
        "Disk space low",
        "Connection pool exhausted",
    ]

    # Error message templates
    error_messages = [
        "Database connection failed",
        "Authentication error: invalid token",
        "File not found: {}",
        "Permission denied",
        "Internal server error",
        "Request validation failed",
        "Service unavailable",
        "Deadlock detected in database",
    ]

    # Fatal message templates
    fatal_messages = [
        "Critical system failure",
        "Unrecoverable database error",
        "Out of memory",
        "System shutdown triggered",
    ]

    for i, level in enumerate(levels):
        source = random.choice(sources)
        timestamp = base_time + timedelta(seconds=random.randint(0, 86400))

        # Generate message based on level
        if level == "DEBUG":
            message = random.choice(debug_messages).format(random.randint(0, 999))
            # Stack traces and slow queries are signal
            if random.random() < 0.05 or "slow query" in message.lower():
                is_signal = True
            else:
                is_signal = False
        elif level == "INFO":
            message = random.choice(info_messages).format(random.randint(1000, 9999))
            # Key events are signal
            is_signal = any(kw in message.lower() for kw in info_signal_keywords)
        elif level == "WARN":
            message = random.choice(warn_messages).format(random.randint(1, 100))
            # Specific keywords make it signal
            is_signal = any(kw in message.lower() for kw in warn_signal_keywords)
        elif level == "ERROR":
            message = random.choice(error_messages).format(random.randint(1, 999))
            is_signal = True  # All errors are signal
        else:  # FATAL
            message = random.choice(fatal_messages)
            is_signal = True  # All fatals are signal

        # Size varies: 50-2000 bytes
        size_bytes = random.randint(50, 2000)

        logs.append({
            "id": i,
            "message": message,
            "level": level,
            "source": source,
            "timestamp": timestamp.isoformat(),
            "size_bytes": size_bytes,
            "is_signal": is_signal,
        })

    # Calculate stats
    total_signal = sum(1 for log in logs if log["is_signal"])
    total_noise = sum(1 for log in logs if not log["is_signal"])
    total_bytes = sum(log["size_bytes"] for log in logs)

    # Save to file
    with open("log_samples.json", "w") as f:
        json.dump(logs, f, indent=2)

    print(f"Generated {num_logs} log entries:")
    print(f"  Signal logs: {total_signal} ({total_signal/num_logs*100:.1f}%)")
    print(f"  Noise logs: {total_noise} ({total_noise/num_logs*100:.1f}%)")
    print(f"  Total volume: {total_bytes:,} bytes (~{total_bytes/1024:.1f}KB)")
    print(f"\nLog levels:")
    for level in ["DEBUG", "INFO", "WARN", "ERROR", "FATAL"]:
        count = sum(1 for log in logs if log["level"] == level)
        print(f"  {level}: {count}")
    print(f"\nSources:")
    for source in sorted(set(log["source"] for log in logs)):
        count = sum(1 for log in logs if log["source"] == source)
        print(f"  {source}: {count}")
    print(f"\nSaved to log_samples.json")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "generate":
        generate()
    else:
        print("Usage: python prepare.py generate")
