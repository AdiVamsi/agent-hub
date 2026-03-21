"""Generate synthetic issue backlog for repo-pilot evaluation.

Deterministic generation with seed=42.
200 issues for a fictional web framework project.
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path


# Issue templates by type
BUG_TITLES = [
    "App crashes on startup with Python {version}",
    "{framework} crashes when handling {scenario}",
    "Error: {error_type} when {action}",
    "{function} throws unexpected exception",
    "Memory leak when {action}",
    "Segmentation fault during {operation}",
    "Database connection lost after {time} of inactivity",
    "{feature} is broken in latest release",
    "Infinite loop in {component}",
    "Race condition in {module}",
]

BUG_BODIES = [
    "When I try to {action}, the app immediately crashes with the error: {error}. This started happening after the last update.",
    "Running {code}, I get: {error}. Expected behavior: {expected}. Actual behavior: {actual}.",
    "The {feature} feature is completely broken. It worked in version {old_version}, but not in {new_version}.",
    "I'm consistently seeing {error} when {scenario}. Stack trace attached. This is blocking my work.",
]

FEATURE_TITLES = [
    "Add support for {technology}",
    "Implement {capability} middleware",
    "Request: native {feature} support",
    "Feature request: {functionality}",
    "Allow {action} without {limitation}",
    "Add option to configure {setting}",
    "Support for {platform} environments",
]

FEATURE_BODIES = [
    "Currently {framework} doesn't support {feature}. This would be useful because {reason}. I'm happy to contribute.",
    "It would be great if {action} was possible. This would enable {use_case}.",
    "I'd like to request the ability to {action}. Many users are asking for this.",
    "Adding {feature} would be a major improvement. Here's my implementation idea: {idea}.",
]

DOCS_TITLES = [
    "Typo in {doc}",
    "Missing example in {section}",
    "{section} documentation is unclear",
    "Broken link in {doc}",
    "Add {section} to docs",
]

DOCS_BODIES = [
    "The docs for {section} contain a typo on line {line}. Should be '{correct}' not '{wrong}'.",
    "The {section} documentation doesn't explain {topic}. It would help to add an example.",
    "The documentation link to {page} is broken. It returns 404.",
    "Could you add documentation for {feature}? It's mentioned in the changelog but not covered in docs.",
]

PERF_TITLES = [
    "Slow performance when {scenario}",
    "High memory usage during {operation}",
    "{endpoint} takes {time}ms to respond",
    "Performance regression in {component}",
    "Database queries are too slow",
]

PERF_BODIES = [
    "When I {action}, it takes over {time}ms. This is a performance regression. In version {old_version}, it was instant.",
    "The {endpoint} endpoint is very slow. For {count} items, it takes {time}ms. Can this be optimized?",
    "Memory usage spikes to {memory}MB when {scenario}. This is a memory leak or inefficiency.",
]

SECURITY_TITLES = [
    "Security: {vulnerability}",
    "{component} has {issue} vulnerability",
    "XSS vulnerability in {feature}",
    "Authentication bypass in {module}",
    "SQL injection risk in {function}",
]

SECURITY_BODIES = [
    "I found a {type} vulnerability in {component}. An attacker could {exploit}. Severity: {severity}.",
    "The {feature} functionality is vulnerable to {attack}. Please fix ASAP.",
]

QUESTION_TITLES = [
    "How do I {action}?",
    "How to configure {setting}?",
    "Best practice for {topic}?",
    "Is {capability} supported?",
    "Can I {action} using {method}?",
]

QUESTION_BODIES = [
    "I'm trying to {action}. The documentation doesn't explain this clearly. Can someone help?",
    "How do I {action}? I've tried {attempt1} and {attempt2} but neither works.",
    "What's the recommended way to {action}?",
]

BREAKING_TITLES = [
    "Breaking change: {change}",
    "{version} breaks {feature}",
    "Upgrade to {version} fails due to {issue}",
    "API change in {version}",
]

BREAKING_BODIES = [
    "Upgrading from {old_version} to {new_version} breaks because {reason}.",
    "The {feature} API changed in {version}. Our code that relied on {old_api} no longer works.",
]

FRAMEWORKS = ["FastAPI", "Django", "Flask", "Starlette", "Tornado"]
VERSIONS = ["3.10", "3.11", "3.12", "2.1", "2.2"]
PRIORITIES = ["critical", "high", "medium", "low"]
AUTHOR_TYPES = ["first-time", "contributor", "maintainer"]
LABELS_AVAILABLE = [
    "bug", "feature", "docs", "performance", "security",
    "breaking-change", "good-first-issue", "help-wanted", "question", "duplicate"
]


def random_choice_safe(lst, rng):
    """Safely choose from list using random."""
    return lst[rng.randint(0, len(lst) - 1)] if lst else ""


def generate_issues(count: int = 200, seed: int = 42) -> list[dict]:
    """Generate synthetic issues for a web framework."""
    rng = random.Random(seed)
    issues = []

    # Distribution
    bug_count = int(count * 0.35)
    feature_count = int(count * 0.25)
    docs_count = int(count * 0.10)
    perf_count = int(count * 0.10)
    security_count = int(count * 0.05)
    question_count = int(count * 0.10)
    breaking_count = int(count * 0.05)

    issue_id = 1
    base_date = datetime(2024, 1, 1)

    def generate_bug():
        nonlocal issue_id
        framework = random_choice_safe(FRAMEWORKS, rng)
        version = random_choice_safe(VERSIONS, rng)
        error_type = rng.choice(["TypeError", "ValueError", "RuntimeError", "AttributeError"])
        error = f"{error_type}: {rng.choice(['invalid', 'unexpected', 'missing'])} {rng.choice(['argument', 'value', 'field'])}"
        function = rng.choice(["parse_request", "handle_route", "validate_schema"])

        title_template = random_choice_safe(BUG_TITLES, rng)
        try:
            title = title_template.format(
                framework=framework,
                version=version,
                error_type=error_type,
                function=function
            )
        except KeyError:
            title = f"{framework} error: {error_type}"

        body_template = random_choice_safe(BUG_BODIES, rng)
        try:
            body = body_template.format(
                action="process request",
                error=error,
                feature="routing",
                old_version="1.0.0",
                new_version="2.0.0",
                scenario="concurrent requests",
                expected="success",
                actual="failure",
                code="my_handler()",
                line="42"
            )
        except KeyError:
            body = f"Got error: {error}. This is a bug."

        priority = rng.choice(["critical", "high", "medium"])
        labels = ["bug"]
        if rng.random() < 0.3:
            labels.append(rng.choice(["performance", "security"]))

        return {
            "id": issue_id,
            "title": title,
            "body": body,
            "ground_truth_labels": labels,
            "ground_truth_priority": priority,
            "duplicate_of": None,
            "created_at": (base_date + timedelta(days=rng.randint(0, 365))).isoformat(),
            "author_type": rng.choice(AUTHOR_TYPES),
        }

    def generate_feature():
        nonlocal issue_id
        technology = rng.choice(["WebSocket", "GraphQL", "gRPC", "CORS", "OAuth2", "JWT"])
        capability = rng.choice(["caching", "compression", "rate limiting", "logging"])

        title = rng.choice([
            f"Add support for {technology}",
            f"Implement {capability} middleware",
            f"Request: native {technology} support",
        ])

        body = rng.choice([
            f"Currently the framework doesn't support {technology}. This would be useful for real-time applications.",
            f"It would be great if {capability} was built-in. Many users are asking for this feature.",
            f"I'd like to request {technology} support. Implementation idea attached.",
        ])

        priority = rng.choice(["high", "medium", "low"])
        labels = ["feature"]
        if rng.random() < 0.2:
            labels.append("help-wanted")

        return {
            "id": issue_id,
            "title": title,
            "body": body,
            "ground_truth_labels": labels,
            "ground_truth_priority": priority,
            "duplicate_of": None,
            "created_at": (base_date + timedelta(days=rng.randint(0, 365))).isoformat(),
            "author_type": rng.choice(AUTHOR_TYPES),
        }

    def generate_docs():
        nonlocal issue_id
        section = rng.choice(["Routing", "Middleware", "Database", "Authentication", "Testing"])

        title = rng.choice([
            f"Typo in {section} documentation",
            f"Missing example in {section}",
            f"{section} docs need clarification",
        ])

        body = rng.choice([
            f"The {section} docs contain a typo. Should be 'decorator' not 'decorater'.",
            f"The {section} documentation lacks an example. Please add one.",
            f"Could you clarify how {section} works in the documentation?",
        ])

        priority = "low"
        labels = ["docs"]
        if rng.random() < 0.3:
            labels.append("good-first-issue")

        return {
            "id": issue_id,
            "title": title,
            "body": body,
            "ground_truth_labels": labels,
            "ground_truth_priority": priority,
            "duplicate_of": None,
            "created_at": (base_date + timedelta(days=rng.randint(0, 365))).isoformat(),
            "author_type": rng.choice(AUTHOR_TYPES),
        }

    def generate_perf():
        nonlocal issue_id
        endpoint = rng.choice(["GET /users", "POST /api/data", "GET /search", "DELETE /items"])
        time_val = rng.choice([100, 500, 1000, 5000])

        title = rng.choice([
            f"Slow performance: {endpoint} takes {time_val}ms",
            f"Performance regression in database queries",
            f"High memory usage during batch processing",
        ])

        body = rng.choice([
            f"The {endpoint} endpoint is very slow. For 1000 items, it takes {time_val}ms.",
            f"Memory usage spikes when processing large datasets.",
            f"Query performance has degraded significantly.",
        ])

        priority = "high"
        labels = ["performance"]

        return {
            "id": issue_id,
            "title": title,
            "body": body,
            "ground_truth_labels": labels,
            "ground_truth_priority": priority,
            "duplicate_of": None,
            "created_at": (base_date + timedelta(days=rng.randint(0, 365))).isoformat(),
            "author_type": rng.choice(AUTHOR_TYPES),
        }

    def generate_security():
        nonlocal issue_id
        vuln = rng.choice(["XSS", "SQL injection", "CSRF", "authentication bypass"])

        title = f"Security: {vuln} vulnerability"
        body = f"Found a {vuln} vulnerability in the {rng.choice(['routing', 'template', 'database'])} layer. Needs immediate fix."

        priority = "critical"
        labels = ["security"]

        return {
            "id": issue_id,
            "title": title,
            "body": body,
            "ground_truth_labels": labels,
            "ground_truth_priority": priority,
            "duplicate_of": None,
            "created_at": (base_date + timedelta(days=rng.randint(0, 365))).isoformat(),
            "author_type": rng.choice(AUTHOR_TYPES),
        }

    def generate_question():
        nonlocal issue_id
        action = rng.choice(["configure CORS", "set up authentication", "use middleware", "handle file uploads"])

        title = f"How do I {action}?"
        body = f"I'm trying to {action}. The documentation doesn't explain this clearly. Can someone help?"

        priority = "low"
        labels = ["question"]

        return {
            "id": issue_id,
            "title": title,
            "body": body,
            "ground_truth_labels": labels,
            "ground_truth_priority": priority,
            "duplicate_of": None,
            "created_at": (base_date + timedelta(days=rng.randint(0, 365))).isoformat(),
            "author_type": "first-time",  # questions often from first-time users
        }

    def generate_breaking():
        nonlocal issue_id
        change = rng.choice(["routing API", "middleware interface", "config format"])

        title = f"Breaking change: {change} updated"
        body = f"Upgrading to v3.0 breaks {change}. Migration path unclear."

        priority = "high"
        labels = ["breaking-change"]

        return {
            "id": issue_id,
            "title": title,
            "body": body,
            "ground_truth_labels": labels,
            "ground_truth_priority": priority,
            "duplicate_of": None,
            "created_at": (base_date + timedelta(days=rng.randint(0, 365))).isoformat(),
            "author_type": rng.choice(AUTHOR_TYPES),
        }

    # Generate all issues
    for _ in range(bug_count):
        issue = generate_bug()
        issues.append(issue)
        issue_id += 1

    for _ in range(feature_count):
        issue = generate_feature()
        issues.append(issue)
        issue_id += 1

    for _ in range(docs_count):
        issue = generate_docs()
        issues.append(issue)
        issue_id += 1

    for _ in range(perf_count):
        issue = generate_perf()
        issues.append(issue)
        issue_id += 1

    for _ in range(security_count):
        issue = generate_security()
        issues.append(issue)
        issue_id += 1

    for _ in range(question_count):
        issue = generate_question()
        issues.append(issue)
        issue_id += 1

    for _ in range(breaking_count):
        issue = generate_breaking()
        issues.append(issue)
        issue_id += 1

    # Add duplicates to 15% of issues
    duplicate_indices = rng.sample(range(len(issues)), k=int(len(issues) * 0.15))
    for idx in duplicate_indices:
        # Find a similar earlier issue to duplicate
        if idx > 0:
            dup_target = rng.randint(0, idx - 1)
            issues[idx]["duplicate_of"] = issues[dup_target]["id"]

    return issues


def main():
    """CLI interface."""
    import sys

    if len(sys.argv) < 2 or sys.argv[1] == "generate":
        issues = generate_issues(count=200, seed=42)
        output_path = Path(__file__).parent / "issue_backlog.json"

        with open(output_path, "w") as f:
            json.dump(issues, f, indent=2)

        print(f"Generated {len(issues)} issues to {output_path}")

        # Print distribution
        bug_count = sum(1 for i in issues if "bug" in i["ground_truth_labels"])
        feature_count = sum(1 for i in issues if "feature" in i["ground_truth_labels"])
        docs_count = sum(1 for i in issues if "docs" in i["ground_truth_labels"])
        perf_count = sum(1 for i in issues if "performance" in i["ground_truth_labels"])
        security_count = sum(1 for i in issues if "security" in i["ground_truth_labels"])
        question_count = sum(1 for i in issues if "question" in i["ground_truth_labels"])
        breaking_count = sum(1 for i in issues if "breaking-change" in i["ground_truth_labels"])
        dup_count = sum(1 for i in issues if i["duplicate_of"] is not None)

        print(f"\nIssue distribution:")
        print(f"  Bugs: {bug_count} ({100*bug_count/len(issues):.0f}%)")
        print(f"  Features: {feature_count} ({100*feature_count/len(issues):.0f}%)")
        print(f"  Docs: {docs_count} ({100*docs_count/len(issues):.0f}%)")
        print(f"  Performance: {perf_count} ({100*perf_count/len(issues):.0f}%)")
        print(f"  Security: {security_count} ({100*security_count/len(issues):.0f}%)")
        print(f"  Questions: {question_count} ({100*question_count/len(issues):.0f}%)")
        print(f"  Breaking changes: {breaking_count} ({100*breaking_count/len(issues):.0f}%)")
        print(f"  Duplicates: {dup_count} ({100*dup_count/len(issues):.0f}%)")

    else:
        print("Usage: python prepare.py [generate]")
        sys.exit(1)


if __name__ == "__main__":
    main()
