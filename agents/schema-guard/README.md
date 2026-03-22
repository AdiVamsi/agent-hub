# Schema Guard

Detect breaking changes and anti-patterns in API schema evolution.

## Overview

When APIs evolve, breaking changes can silently break client applications. Schema Guard automatically analyzes schema changes to identify:

- **Removed fields** — clients expect them, server removes them
- **Type changes** — clients code for string, server sends int
- **Required field additions** — forces all clients to update
- **Enum narrowing** — clients send now-invalid values
- **Nullable removal** — clients send null, server rejects
- **Format changes** — validation rules shift unexpectedly

## Quick Start

```bash
# Generate 100 sample schema changes
python prepare.py generate

# See what baseline achieves (always says "non-breaking")
python harness.py baseline

# Run your detector
python harness.py evaluate
```

## Your Job

Edit `check_rules.py` and implement `is_breaking_change(change)` to detect breaking changes.

The function receives a schema change with:
- `endpoint` (e.g., "/users/{id}")
- `method` (GET, POST, PUT, DELETE)
- `old_schema` — the old field definition
- `new_schema` — the new field definition (or None if removed)
- `change_type` — hint (field_removed, type_changed, etc.)

Return a dict with:
- `breaking`: bool — is this a breaking change?
- `severity`: str — "critical"/"major"/"minor"/"none"
- `reason`: str — explanation for debugging

## Scoring

- ✅ Correctly identified breaking: +1
- ✅ Correctly identified non-breaking: +1
- ❌ Missed breaking (false negative): -2 (dangerous!)
- ⚠️ False alarm (false positive): -0.5 (annoying)
- 🎯 Correct severity on breaking: +0.5 bonus

**Baseline score:** -65 (always says non-breaking, misses all 55 breaking changes)

**Optimal score:** ~+120 (catch all breaking + severity bonuses)

## Data Format

Each change in `schema_changes.json`:

```json
{
  "change_id": "breaking_5432",
  "endpoint": "/users/{id}",
  "method": "GET",
  "version_from": "1.0.0",
  "version_to": "2.0.0",
  "old_schema": {
    "name": "email",
    "type": "string",
    "required": true,
    "description": "User email address"
  },
  "new_schema": {
    "name": "email",
    "type": "integer",
    "required": true,
    "description": "User email address"
  },
  "change_type": "type_changed",
  "is_breaking": true,
  "severity": "major",
  "description": "Field 'email' type changed from string to integer"
}
```

## Examples

### Breaking Change: Field Removed
```python
change = {
  "endpoint": "/users/{id}",
  "method": "GET",
  "old_schema": {"name": "email", "type": "string", "required": true},
  "new_schema": None,  # Removed!
  "change_type": "field_removed"
}

# Should return:
{
  "breaking": True,
  "severity": "critical",
  "reason": "Field 'email' was removed; clients can't parse response"
}
```

### Non-Breaking Change: Optional Field Added
```python
change = {
  "endpoint": "/users/{id}",
  "method": "GET",
  "old_schema": {"name": "id", "type": "string", "required": true},
  "new_schema": {"name": "age", "type": "integer", "required": false},
  "change_type": "field_added"
}

# Should return:
{
  "breaking": False,
  "severity": "none",
  "reason": "New optional field 'age' doesn't break clients"
}
```

### Breaking Change: Required Field Added
```python
change = {
  "endpoint": "/users",
  "method": "POST",
  "old_schema": {"name": "name", "type": "string", "required": false},
  "new_schema": {"name": "name", "type": "string", "required": true},
  "change_type": "required_added"
}

# Should return:
{
  "breaking": True,
  "severity": "critical",
  "reason": "Field 'name' now required; old clients won't send it"
}
```

## Connect Your OpenAPI Spec

Ready to protect your real API? Connect at **agent-hub.dev** and get:

- Real-time breaking change detection
- Slack/email notifications
- Historical schema tracking
- Severity scoring for your domain
- Integration with CI/CD pipelines

**Comparable pricing:**
- Optic: $149/mo
- Speakeasy: $99/mo
- Bump.sh: $79/mo

**Schema Guard:** FREE while in beta. Professional tiers coming soon.

## Resources

- [program.md](program.md) — 10+ detection hypotheses
- [API Design Best Practices](https://semver.org/) — semantic versioning
- [OpenAPI Spec](https://spec.openapis.org/) — schema format reference

## License

MIT
