#!/usr/bin/env python3
"""Traffic generator for llm-cost-pilot. DO NOT MODIFY.

Usage:
    python prepare.py generate   — create traffic/sample.jsonl with 1000 requests
"""

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).parent
TRAFFIC_DIR = ROOT / "traffic"

# ---------------------------------------------------------------------------
# Tier definitions with realistic message templates
# ---------------------------------------------------------------------------

NANO_TASKS = [
    ("Translate this to French: 'Hello, how are you today?'", "translation"),
    ("Extract the email address from: 'Contact us at info@example.com for details.'", "extraction"),
    ("Is the following sentence positive or negative? 'I love sunny days.'", "classification"),
    ("Format this date: 2026-03-15 → March 15, 2026", "formatting"),
    ("Classify this support ticket as billing, technical, or general: 'My invoice is wrong.'", "classification"),
    ("Convert this to uppercase: 'hello world'", "formatting"),
    ("Yes or no: Is 7 a prime number?", "yes_no"),
    ("Extract the phone number from: 'Call us at (555) 123-4567.'", "extraction"),
    ("Translate 'Good morning' to Spanish.", "translation"),
    ("Is this a question or statement? 'The weather is nice.'", "classification"),
    ("Fix the capitalization: 'the QUICK brown FOX'", "formatting"),
    ("Translate to German: 'Thank you very much.'", "translation"),
    ("Label sentiment: 'This product is terrible and broke immediately.'", "classification"),
    ("Extract the URL from: 'Visit https://example.com for more.'", "extraction"),
    ("Is 42 even or odd?", "yes_no"),
]

SMALL_TASKS = [
    ("What is the capital of France and what is it known for?", "simple_qa"),
    ("Summarize in one sentence: Machine learning is a subset of AI that enables systems to learn from data.", "short_summary"),
    ("Write a one-paragraph product description for wireless earbuds.", "basic_generation"),
    ("What are three benefits of exercise?", "simple_qa"),
    ("Explain what an API is in two sentences.", "simple_qa"),
    ("Write a short email declining a meeting invitation politely.", "basic_generation"),
    ("Summarize: The stock market fell 2% today due to inflation concerns.", "short_summary"),
    ("List the planets in our solar system.", "simple_qa"),
    ("Write a haiku about programming.", "basic_generation"),
    ("What does HTTP stand for and what is it used for?", "simple_qa"),
    ("Rewrite this sentence more formally: 'Hey, can u help me with this?'", "basic_generation"),
    ("Summarize the concept of supply and demand in economics.", "short_summary"),
]

MEDIUM_TASKS = [
    ("Write a 300-word blog post about the future of remote work.", "content_writing"),
    ("Summarize the key themes in the provided quarterly earnings report.", "longer_summary"),
    ("Write a Python function that validates email addresses using regex.", "standard_code"),
    ("Create a marketing email for a new SaaS product launch.", "content_writing"),
    ("Explain the differences between SQL and NoSQL databases with examples.", "longer_summary"),
    ("Write a bash script that backs up a directory with timestamps.", "standard_code"),
    ("Draft a professional LinkedIn post announcing a new job.", "content_writing"),
    ("Compare React and Vue.js for frontend development.", "longer_summary"),
    ("Write a REST API endpoint in Python Flask for user registration.", "standard_code"),
    ("Create a product comparison table for three CRM tools.", "content_writing"),
]

LARGE_TASKS = [
    ("Analyze the provided dataset and identify correlations between user engagement and revenue.", "complex_analysis"),
    ("Write a complete Python class for a binary search tree with insert, delete, search, and traversal.", "advanced_code"),
    ("Design a microservices architecture for an e-commerce platform. Include service boundaries, communication patterns, and data management.", "multi_step_reasoning"),
    ("Write a comprehensive technical design document for a real-time notification system.", "complex_analysis"),
    ("Implement a thread-safe connection pool in Python with retry logic and health checks.", "advanced_code"),
    ("Analyze the trade-offs between consistency and availability in distributed systems with concrete examples.", "multi_step_reasoning"),
    ("Write a complete CI/CD pipeline configuration for a Python monorepo with multiple services.", "advanced_code"),
    ("Evaluate three cloud providers for hosting a high-traffic application. Consider cost, scalability, and compliance.", "complex_analysis"),
]

FLAGSHIP_TASKS = [
    ("Using the provided API, analyze customer churn patterns, build a predictive model, and generate actionable recommendations with confidence intervals.", "research_grade"),
    ("Design and implement a complete authentication system with OAuth 2.0, MFA, rate limiting, and audit logging. Provide the full architecture and code.", "complex_multi_turn_tools"),
    ("Conduct a thorough security audit of the provided codebase. Identify vulnerabilities, classify by severity, and provide remediation code for each.", "research_grade"),
    ("Analyze this legal contract for potential risks, compare against industry standards, and draft amendment suggestions with legal reasoning.", "complex_multi_turn_tools"),
    ("Build a complete data pipeline: ingest from three APIs, transform, deduplicate, validate, load into a warehouse, and create monitoring dashboards.", "research_grade"),
]

# Model distribution: 60% gpt-4o, 20% claude-sonnet, 10% opus, 10% gpt-5.2
MODEL_WEIGHTS = [
    ("gpt-4o", 0.60),
    ("claude-sonnet-4-6", 0.20),
    ("claude-opus-4-6", 0.10),
    ("gpt-5.2", 0.10),
]

# Tier distribution: nano 30%, small 25%, medium 25%, large 15%, flagship 5%
TIER_WEIGHTS = [
    ("nano", 0.30),
    ("small", 0.25),
    ("medium", 0.25),
    ("large", 0.15),
    ("flagship", 0.05),
]

TIER_TASKS = {
    "nano": NANO_TASKS,
    "small": SMALL_TASKS,
    "medium": MEDIUM_TASKS,
    "large": LARGE_TASKS,
    "flagship": FLAGSHIP_TASKS,
}

METADATA_TAGS = ["realtime", "async", "batch", "interactive", "background"]

TOOL_EXAMPLES = [
    {"name": "web_search", "description": "Search the web"},
    {"name": "calculator", "description": "Perform calculations"},
    {"name": "file_reader", "description": "Read file contents"},
    {"name": "database_query", "description": "Query a database"},
    {"name": "api_call", "description": "Call an external API"},
]


def weighted_choice(items_weights):
    items, weights = zip(*items_weights)
    return random.choices(items, weights=weights, k=1)[0]


def generate_messages(task_text: str, tier: str) -> list:
    """Generate a realistic conversation with 1-8 messages."""
    messages = [{"role": "user", "content": task_text}]

    # Add context messages for higher tiers
    if tier in ("medium", "large", "flagship"):
        num_extra = random.randint(1, min(4, {"medium": 3, "large": 5, "flagship": 7}[tier]))
        for i in range(num_extra):
            if i % 2 == 0:
                messages.append({
                    "role": "assistant",
                    "content": f"I'll help with that. Let me work through this step by step. "
                               f"{'Here is my analysis so far. ' * random.randint(1, 3)}"
                               f"Would you like me to continue with more detail?"
                })
            else:
                messages.append({
                    "role": "user",
                    "content": random.choice([
                        "Yes, please continue with more detail.",
                        "Can you also consider the edge cases?",
                        "That's good. Now apply it to the specific scenario I mentioned.",
                        "Add error handling and make it production-ready.",
                        "Great. Now summarize the key takeaways.",
                    ])
                })
    return messages


def generate_request(request_id: int) -> dict:
    """Generate a single synthetic API request."""
    tier = weighted_choice(TIER_WEIGHTS)
    tasks = TIER_TASKS[tier]
    task_text, task_type = random.choice(tasks)

    model = weighted_choice(MODEL_WEIGHTS)
    messages = generate_messages(task_text, tier)

    request = {
        "id": request_id,
        "messages": messages,
        "model": model,
        "max_tokens": random.choice([100, 200, 500, 1000, 2000, 4000]),
        "temperature": round(random.uniform(0, 1), 2),
        "reference_tier": tier,
        "metadata": {
            "tags": random.sample(METADATA_TAGS, k=random.randint(1, 2)),
            "task_type": task_type,
        },
    }

    # 10% have tools
    if random.random() < 0.10:
        request["tools"] = random.sample(TOOL_EXAMPLES, k=random.randint(1, 3))

    # 30% have stream=True
    if random.random() < 0.30:
        request["stream"] = True

    return request


def generate_traffic(n: int = 1000):
    """Generate n synthetic requests and save to traffic/sample.jsonl."""
    TRAFFIC_DIR.mkdir(parents=True, exist_ok=True)
    output_path = TRAFFIC_DIR / "sample.jsonl"

    random.seed(42)  # Reproducible
    requests = [generate_request(i) for i in range(n)]

    with open(output_path, "w") as f:
        for req in requests:
            f.write(json.dumps(req) + "\n")

    # Print tier distribution
    tier_counts = {}
    for req in requests:
        t = req["reference_tier"]
        tier_counts[t] = tier_counts.get(t, 0) + 1

    print(f"Generated {n} requests → {output_path}")
    print(f"Tier distribution:")
    for tier in ["nano", "small", "medium", "large", "flagship"]:
        count = tier_counts.get(tier, 0)
        print(f"  {tier:10s}: {count:4d} ({count/n*100:.0f}%)")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python prepare.py generate")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "generate":
        generate_traffic(1000)
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: python prepare.py generate")
        sys.exit(1)
