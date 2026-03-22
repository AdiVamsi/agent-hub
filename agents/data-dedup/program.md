# Data Dedup — AutoResearch Program

## Problem Statement
Deduplicate a dataset of 300 records (100 unique entities with ~200 realistic duplicates). Maximize F1 score by optimizing fuzzy matching rules.

**Baseline**: F1 = 0.0 (no duplicates found)
**Target**: F1 ≥ 0.85

## Research Hypotheses

### H1: Exact Email Match
**Assumption**: If two records share the same email, they're the same person.
**Implementation**: Hash records by email, group records with identical emails.
**Expected Improvement**: High precision but lower recall (duplicates have different emails, typos).

### H2: Normalized Name Matching
**Assumption**: Names with whitespace/case variations are the same person.
**Implementation**: Normalize first_name and last_name (lowercase, strip whitespace), exact match.
**Expected Improvement**: Catches "Robert" vs "robert", handles some variation.

### H3: Levenshtein Distance on Names
**Assumption**: Names with small edit distances are duplicates.
**Implementation**: Calculate Levenshtein distance between first_name pairs and last_name pairs. Merge if both < threshold (e.g., 2).
**Expected Improvement**: Catches typos ("Robrt" vs "Robert"), phonetic variations.

### H4: Phone Number Normalization
**Assumption**: Matching phone numbers (after normalization) indicate same person.
**Implementation**: Strip non-digits from phone, exact match on normalized phone.
**Expected Improvement**: Reliable but incomplete (many duplicates have missing phone fields).

### H5: Company Name Normalization
**Assumption**: Company variations (Inc vs LLC) should be normalized.
**Implementation**: Remove common suffixes (Inc, LLC, Corp, Ltd) before matching.
**Expected Improvement**: Helps avoid false negatives when only company differs.

### H6: Blocking by City First
**Assumption**: Geographic locality reduces false positives.
**Implementation**: Block (partition) by city first, then apply fuzzy matching within blocks.
**Expected Improvement**: Reduces noise, improves precision.

### H7: TF-IDF on Concatenated Fields
**Assumption**: Concatenate all fields, compute TF-IDF similarity vectors.
**Implementation**: Build TF-IDF model on "first_name last_name email company city", compute cosine similarity between records.
**Expected Improvement**: Holistic approach, catches multi-field matches.

### H8: Transitive Closure
**Assumption**: If A matches B and B matches C, then A, B, C should be clustered together.
**Implementation**: Build match graph, compute connected components using union-find.
**Expected Improvement**: Significantly improves recall, catches chains of duplicates.

### H9: Email Domain Normalization
**Assumption**: Different email domains (@gmail vs @yahoo) but same username = same person.
**Implementation**: Extract email username, match on username alone.
**Expected Improvement**: Catches email provider changes.

### H10: First Name Abbreviations
**Assumption**: "Robert" == "Bob", "Michael" == "Mike", etc.
**Implementation**: Map common abbreviations to full names before matching.
**Expected Improvement**: Catches name abbreviations.

## Experimental Plan

1. **Baseline** (F1 = 0.0): All records treated as unique.

2. **Single Rule Tests** (Experiments 1-10):
   - Test each hypothesis independently.
   - Expected: Precision/recall tradeoffs.

3. **Combination Tests** (Experiments 11-20):
   - Combine high-precision rules (exact email) with high-recall rules (Levenshtein).
   - Use transitive closure to boost recall.
   - Optimize thresholds (e.g., Levenshtein distance <= 2).

4. **Refinement** (Experiments 21-25):
   - Fine-tune threshold parameters.
   - Adjust blocking strategy.
   - Resolve conflicts between rules.

## Success Criteria
- F1 ≥ 0.85 on golden_clusters validation
- Precision ≥ 0.90 (avoid false positives)
- Recall ≥ 0.80 (find most duplicates)
- Code remains in match_rules.find_duplicates() — no external files read
