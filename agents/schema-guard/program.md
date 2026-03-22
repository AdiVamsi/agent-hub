# Schema Guard — AutoResearch Program

## Problem Statement

API schemas evolve. Most changes are safe (adding optional fields), but some are dangerous (removing fields, changing types, tightening enums). We need to automatically detect breaking changes to prevent painful runtime errors.

**Success metric:** Detection score (higher is better). Baseline = -65.

## 8+ Hypotheses

### H1: Field Removal
**Hypothesis:** If a field exists in old_schema but not in new_schema, it's always breaking.
- **Why:** Consumers expect that field to exist. Removing it breaks their code.
- **Test:** Look for changes where new_schema is None or field not present
- **Severity:** critical

### H2: Type Changes
**Hypothesis:** If a field's type changes (string→int, boolean→string, etc.), it's breaking.
- **Why:** Consumers code for a specific type. Type changes break deserialization and logic.
- **Test:** Compare old_schema["type"] vs new_schema["type"]
- **Severity:** major (critical for core fields like id, email)

### H3: Required Field Addition
**Hypothesis:** If a field becomes required (was optional), it's breaking.
- **Why:** Consumers may not provide this field. Making it required breaks their requests.
- **Test:** old_schema["required"]=False, new_schema["required"]=True
- **Severity:** critical (forces all clients to change)

### H4: Enum Narrowing
**Hypothesis:** If enum values shrink (fewer allowed values), it's breaking.
- **Why:** Consumer code may be sending now-invalid enum values. Server rejects them.
- **Test:** old_schema["enum"] has more values than new_schema["enum"]
- **Severity:** major

### H5: Nullable Removal
**Hypothesis:** If a field was nullable and no longer is, it's breaking.
- **Why:** Consumer code may send null. Server now rejects it.
- **Test:** old_schema["nullable"]=True, new_schema["nullable"]=False
- **Severity:** major

### H6: Format Changes
**Hypothesis:** Format changes (email→uuid, date-time→date) can be breaking.
- **Why:** Consumers may not know the validation rules changed.
- **Test:** old_schema["format"] != new_schema["format"]
- **Severity:** major (depends on field importance)

### H7: Safe Field Additions
**Hypothesis:** Adding optional fields is NOT breaking.
- **Why:** Consumers can ignore unknown fields. It's backward compatible.
- **Test:** Field exists only in new_schema AND required=False
- **Severity:** none

### H8: Safe Default Changes
**Hypothesis:** Changing default values is NOT breaking (only minor).
- **Why:** Consumers who don't send the field get a new default. Old behavior changes but doesn't break.
- **Test:** old_schema["default"] != new_schema["default"]
- **Severity:** minor

### H9: Field Importance Heuristic
**Hypothesis:** Some fields are more critical than others (id, email vs description).
- **Why:** Type change on "id" is more breaking than on "description".
- **Test:** Use field name patterns (id, email, password, token, etc.)
- **Severity:** critical for critical fields, major for others

### H10: Change Type Patterns
**Hypothesis:** The change_type field itself gives strong hints.
- **Why:** change_type="field_removed" is always breaking; change_type="safe_addition" is not.
- **Test:** Map change_type directly
- **Severity:** Trust the label

## Experiment Plan

1. **Exp 1:** Implement H1 (field removal) — should catch ~10 breaking changes
2. **Exp 2:** Add H2 (type changes) — should catch ~20 more
3. **Exp 3:** Add H3 (required additions) — should catch ~15 more
4. **Exp 4:** Add H4 (enum narrowing) — should catch ~5 more
5. **Exp 5:** Add H5 (nullable removal) — should catch ~3 more
6. **Exp 6:** Implement H7 (safe additions) to reduce false positives
7. **Exp 7:** Add severity scoring based on field importance
8. **Exp 8:** Add H6 (format changes) and H8 (defaults)
9. **Exp 9-25:** Iterate on thresholds, refine heuristics, handle edge cases

## Expected Trajectory

- **Exp 1-3:** Score ~+20 to +40 (catching obvious breaking changes)
- **Exp 4-6:** Score ~+60 to +90 (handling enum/nullable, reducing false positives)
- **Exp 7-9:** Score ~+100 to +120 (severity scoring, edge cases)
- **Final:** Score ~+120+ (optimal detection with minimal false positives)

## Key Metrics

- **TP (True Positive):** Correctly identified breaking change → +1
- **TN (True Negative):** Correctly identified non-breaking change → +1
- **FP (False Positive):** Flagged non-breaking as breaking → -0.5
- **FN (False Negative):** Missed breaking change → -2 (very bad!)
- **Severity Bonus:** Correct severity on breaking changes → +0.5

## Edge Cases to Handle

1. What if old_schema or new_schema has extra fields not in the spec?
2. What if enum becomes "open" (any value allowed) vs closed?
3. What if required=null (implicit behavior)?
4. What if type changes but format makes it compatible (int→number)?
5. What about additionalProperties in object types?
