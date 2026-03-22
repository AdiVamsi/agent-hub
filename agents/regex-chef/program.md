# Regex Chef — AutoResearch Program

## Objective
Optimize regex patterns for maximum accuracy on a labeled validation set of 200 strings across 6 pattern types (email, phone_us, ipv4, date_iso, url, semver).

Baseline accuracy: ~0.55-0.65 (simple patterns catch obvious cases but fail on edge cases)
Target accuracy: ~0.92-0.98 (proper anchoring, validation, and edge case handling)

## Validation Set
- 200 labeled examples (test_id, input_string, pattern_type, expected_match, description)
- 6 pattern types with 25-40 examples each
- ~60% true positives, ~40% true negatives (balanced negatives)
- Realistic edge cases that trip up naive regexes

## Metric
**Accuracy** = (correct predictions) / (total tests)
- Higher is better
- Compute improvement_pct = ((accuracy - baseline) / baseline) * 100

## Hypotheses (8+ explorations)

### H1: Anchor patterns with ^ and $
**Rationale**: Simple patterns match substrings. Full string matching (fullmatch) still has edge cases where regex metacharacters aren't properly constrained.
- email: anchor invalid edge cases like multiple @ or missing parts
- phone_us: prevent partial matches and ensure format strictness
- ipv4: prevent leading/trailing non-digit cruft
- date_iso: ensure exactly YYYY-MM-DD format
- url: validate protocol and domain boundaries strictly
- semver: ensure exact X.Y.Z format with optional pre-release/build

**Expected impact**: +5-10% accuracy

---

### H2: Validate numeric ranges for IP/dates
**Rationale**: Naive digit patterns allow octet=999 or month=99. Need conditional ranges.
- ipv4: each octet must be 0-255 (use alternation: ([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))
- date_iso: validate month (01-12), day (01-31), and day-of-month (e.g., Feb not 30)

**Expected impact**: +10-15% accuracy (catches many invalid but format-correct cases)

---

### H3: Handle optional format variations for phone
**Rationale**: US phones have many valid formats: (555) 123-4567, 555-123-4567, 555 123 4567, +1 555 123 4567, 5551234567, etc.
- Make separators optional or allow alternation
- Support optional +1 prefix
- Handle various spacing/punctuation conventions

**Expected impact**: +8-12% accuracy

---

### H4: Add protocol validation for URLs
**Rationale**: Valid protocols are http, https, ftp (and rarely others). Restrict to known set.
- Protocol: (https?|ftp)://
- Prevent typos like "htp://" or "http//example.com"

**Expected impact**: +5-8% accuracy

---

### H5: Handle pre-release/build metadata for semver
**Rationale**: Semver allows X.Y.Z-prerelease+build metadata. Current pattern ignores these.
- Pattern: \d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?(\+[a-zA-Z0-9.]+)?
- Prerelease: hyphen followed by alphanumeric + dots, no leading zeros (except single 0)
- Build: plus followed by alphanumeric + dots

**Expected impact**: +8-12% accuracy

---

### H6: Reject invalid email local parts
**Rationale**: Valid local parts (before @) have rules:
- Can't start/end with dot
- Can't have consecutive dots
- Limited special chars: . + - _
- Current pattern ".+@.+" too permissive

**Expected impact**: +10-15% accuracy

---

### H7: Validate month/day ranges for ISO dates
**Rationale**: Feb 30, April 31, June 31, Sept 31, Nov 31 are invalid. Need per-month validation.
- 31-day months: Jan, Mar, May, Jul, Aug, Oct, Dec
- 30-day months: Apr, Jun, Sep, Nov
- Feb: 28 (or 29 in leap years)
- Leap year: divisible by 4, except centuries (divisible by 400)

**Expected impact**: +8-12% accuracy

---

### H8: Handle edge cases like localhost URLs
**Rationale**: Valid URLs include localhost, IP addresses, and edge cases.
- Allow localhost without TLD
- Allow IP-based URLs
- Allow ports (http://example.com:8080)
- Disallow URLs with spaces, double slashes in path

**Expected impact**: +5-10% accuracy

---

### H9: Email domain validation
**Rationale**: Domains must have at least one dot and valid TLDs (2+ chars), or special cases (localhost, IP).
- Reject domains ending with dot or starting with dot
- Reject consecutive dots in domain
- Require at least one dot in domain (or allow IP: user@192.168.1.1)

**Expected impact**: +5-8% accuracy

---

### H10: Phone extension handling
**Rationale**: Some valid patterns include extensions (e.g., "555-123-4567 ext 123").
- Make extensions optional
- Allow "ext", "x", or just separation

**Expected impact**: +2-3% accuracy

---

### H11: URL query string and fragment validation
**Rationale**: Query strings (?) and fragments (#) must be properly ordered and not contain unencoded spaces.
- Format: protocol://domain[:port][/path][?query][#fragment]
- Reject spaces in path (unless encoded as %20)
- Reject unordered fragments

**Expected impact**: +5-10% accuracy

---

### H12: Case sensitivity and whitespace handling
**Rationale**: Protocols (http/https/ftp) are case-insensitive. Patterns should handle variations.
- Use (?i) flag or [Hh][Tt][Tt][Pp] for case-insensitive matching
- Handle leading/trailing whitespace (already stripped)

**Expected impact**: +2-3% accuracy

---

## Experiment Plan
1. **Iteration 1-3**: Implement H1-H3 (anchoring, IP/date validation, phone variations)
2. **Iteration 4-6**: Implement H4-H6 (URL protocol, semver metadata, email local part)
3. **Iteration 7-9**: Implement H7-H9 (date month/day, localhost URLs, email domain)
4. **Iteration 10-15**: Refine based on error analysis, implement H10-H12
5. **Final**: Consolidate optimal patterns, verify no gaming, document rationale

## Anti-Gaming Checks
- Harness validates patterns.py doesn't hardcode test strings
- Harness verifies each pattern compiles as valid regex
- Patterns must be general, not overfitted to specific test cases

## Expected Trajectory
- Baseline: 0.55-0.65
- After H1: 0.60-0.70
- After H2: 0.70-0.80
- After H3-H7: 0.85-0.95
- Final optimized: 0.92-0.98
