"""Schema Guard — Data Generation.

Generates 100 schema change pairs for testing schema evolution detection.
"""

import json
import random
from typing import Any, Dict, List

# Realistic field names and their properties
FIELD_NAMES = [
    "id", "name", "email", "status", "created_at", "updated_at",
    "user_id", "product_id", "price", "quantity", "description",
    "active", "verified", "role", "permissions", "tags",
    "metadata", "settings", "timestamp", "version", "hash",
    "parent_id", "owner_id", "category", "type", "format",
    "url", "path", "token", "secret", "api_key",
    "first_name", "last_name", "phone", "address", "city",
    "state", "zip_code", "country", "latitude", "longitude",
    "score", "rating", "likes", "views", "comments",
    "published", "archived", "deleted", "expires_at", "started_at"
]

FIELD_TYPES = ["string", "integer", "number", "boolean", "object", "array", "null"]

CHANGE_TYPES = [
    "field_removed",
    "type_changed",
    "required_added",
    "enum_narrowed",
    "field_renamed",
    "field_added",
    "default_changed",
    "nullable_removed",
    "safe_addition",
    "format_changed"
]

ENDPOINTS = [
    "/users/{id}",
    "/users",
    "/products/{id}",
    "/products",
    "/orders/{id}",
    "/orders",
    "/posts/{id}",
    "/posts",
    "/comments/{id}",
    "/comments",
    "/auth/login",
    "/auth/register",
    "/auth/refresh",
    "/teams/{id}",
    "/teams",
    "/projects/{id}",
    "/projects",
    "/issues/{id}",
    "/issues",
]

METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH"]

STATUSES = ["draft", "published", "archived", "deleted", "pending"]
ROLES = ["admin", "user", "guest", "moderator", "owner"]


def generate_old_field(field_name: str, rng: random.Random) -> Dict[str, Any]:
    """Generate a realistic old schema field."""
    field_type = rng.choice(FIELD_TYPES)
    return {
        "name": field_name,
        "type": field_type,
        "required": rng.choice([True, False]),
        "description": f"The {field_name} field"
    }


def generate_new_field(field_name: str, rng: random.Random) -> Dict[str, Any]:
    """Generate a realistic new schema field."""
    field_type = rng.choice(FIELD_TYPES)
    return {
        "name": field_name,
        "type": field_type,
        "required": rng.choice([True, False]),
        "description": f"The {field_name} field"
    }


def generate_breaking_change(rng: random.Random) -> Dict[str, Any]:
    """Generate a breaking change."""
    field_name = rng.choice(FIELD_NAMES)
    endpoint = rng.choice(ENDPOINTS)
    method = rng.choice(METHODS)
    change_type = rng.choice([
        "field_removed",
        "type_changed",
        "required_added",
        "enum_narrowed",
        "nullable_removed"
    ])

    old_schema = generate_old_field(field_name, rng)
    new_schema = generate_new_field(field_name, rng)

    # Make it actually breaking based on change_type
    if change_type == "field_removed":
        old_schema["name"] = field_name
        new_schema = None
        description = f"Field '{field_name}' was removed"
    elif change_type == "type_changed":
        old_type = rng.choice(["string", "integer", "boolean"])
        new_type = rng.choice([t for t in FIELD_TYPES if t != old_type])
        old_schema["type"] = old_type
        new_schema["type"] = new_type
        description = f"Field '{field_name}' type changed from {old_type} to {new_type}"
    elif change_type == "required_added":
        old_schema["required"] = False
        new_schema["required"] = True
        description = f"Field '{field_name}' is now required"
    elif change_type == "enum_narrowed":
        old_schema["enum"] = ["draft", "published", "archived", "deleted"]
        new_schema["enum"] = ["draft", "published"]
        description = "Enum values were narrowed"
    elif change_type == "nullable_removed":
        old_schema["nullable"] = True
        new_schema["nullable"] = False
        description = f"Field '{field_name}' is no longer nullable"

    return {
        "change_id": f"breaking_{rng.randint(1000, 9999)}",
        "endpoint": endpoint,
        "method": method,
        "version_from": "1.0.0",
        "version_to": "2.0.0",
        "old_schema": old_schema,
        "new_schema": new_schema,
        "change_type": change_type,
        "is_breaking": True,
        "severity": rng.choice(["critical", "major"]),
        "description": description
    }


def generate_non_breaking_change(rng: random.Random) -> Dict[str, Any]:
    """Generate a non-breaking change."""
    field_name = rng.choice(FIELD_NAMES)
    endpoint = rng.choice(ENDPOINTS)
    method = rng.choice(METHODS)
    change_type = rng.choice([
        "field_added",
        "field_renamed",
        "default_changed",
        "safe_addition",
        "format_changed"
    ])

    old_schema = generate_old_field(field_name, rng)
    new_schema = generate_new_field(field_name, rng)

    # Make it actually non-breaking
    if change_type == "safe_addition":
        old_schema = generate_old_field(rng.choice(FIELD_NAMES), rng)
        new_field = rng.choice(FIELD_NAMES)
        new_schema = generate_new_field(new_field, rng)
        new_schema["required"] = False
        description = f"New optional field '{new_field}' added"
    elif change_type == "field_added":
        new_schema["required"] = False
        new_schema["name"] = f"{field_name}_new"
        description = "New optional field added"
    elif change_type == "default_changed":
        old_schema["default"] = "draft"
        new_schema["default"] = "published"
        description = "Default value changed"
    elif change_type == "format_changed":
        old_schema["format"] = "email"
        new_schema["format"] = "uuid"
        description = "Field format changed"
    elif change_type == "field_renamed":
        old_schema["name"] = field_name
        new_schema["name"] = f"{field_name}_v2"
        description = f"Field renamed from {field_name} to {field_name}_v2"

    severity = rng.choice(["minor", "none"])
    if change_type == "default_changed":
        severity = "minor"

    return {
        "change_id": f"safe_{rng.randint(1000, 9999)}",
        "endpoint": endpoint,
        "method": method,
        "version_from": "1.0.0",
        "version_to": "1.1.0",
        "old_schema": old_schema,
        "new_schema": new_schema,
        "change_type": change_type,
        "is_breaking": False,
        "severity": severity,
        "description": description
    }


def generate_dataset(num_changes: int = 100, seed: int = 42) -> List[Dict[str, Any]]:
    """Generate a dataset of schema changes."""
    rng = random.Random(seed)
    changes = []

    # 55% breaking, 45% non-breaking
    num_breaking = int(num_changes * 0.55)
    num_non_breaking = num_changes - num_breaking

    for _ in range(num_breaking):
        changes.append(generate_breaking_change(rng))

    for _ in range(num_non_breaking):
        changes.append(generate_non_breaking_change(rng))

    # Shuffle
    rng.shuffle(changes)
    return changes


def main():
    """CLI entry point."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python prepare.py generate")
        sys.exit(1)

    command = sys.argv[1]

    if command == "generate":
        print("Generating schema_changes.json...")
        changes = generate_dataset(100, seed=42)

        with open("schema_changes.json", "w") as f:
            json.dump(changes, f, indent=2)

        print(f"Generated {len(changes)} schema changes")
        breaking_count = sum(1 for c in changes if c["is_breaking"])
        print(f"Breaking: {breaking_count} ({breaking_count/len(changes)*100:.1f}%)")
        print(f"Non-breaking: {len(changes) - breaking_count} ({(1 - breaking_count/len(changes))*100:.1f}%)")
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
