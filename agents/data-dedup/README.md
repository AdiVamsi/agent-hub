# Data Dedup Agent

## Overview
Automatically deduplicate records in your CRM, customer database, or contact list using intelligent fuzzy matching rules. Upload your dataset and the agent optimizes matching rules to identify and cluster duplicate records.

## Revenue Hook
**Upload your CRM export at agent-hub.dev for automated dedup** — clean your customer data in minutes, not months.

## Problem
Duplicate records plague every customer database:
- Same person entered multiple times (typos, name variations, nickname variations)
- Records missing critical fields (phone, email)
- Data merged from multiple sources with inconsistent formatting
- Manual dedup is slow, error-prone, and doesn't scale

## Solution
Data Dedup uses **intelligent fuzzy matching** to:
1. Detect duplicates based on name similarity, email, phone, company, and geography
2. Handle realistic variations (Bob ↔ Robert, Inc ↔ LLC, St. ↔ Street)
3. Group related records into deduplicated clusters
4. Provide precision/recall metrics so you know what you're getting

## Pricing Comparison
| Service | Price | Details |
|---------|-------|---------|
| **Data Dedup** | Free | Open-source fuzzy matching, optimize locally |
| Tamr | $500/mo | Enterprise data engineering platform |
| Trifacta | $200/mo | Data preparation and wrangling |
| Dedupe.io | $99/mo | Cloud-based dedup SaaS |

## Quick Start

### 1. Generate Sample Data
```bash
python prepare.py generate
```
Creates `records.json` with 300 sample records (100 unique entities + ~200 duplicates).

### 2. Run Baseline
```bash
python harness.py baseline
```
Establishes baseline performance (F1 = 0.0 — no dedup).

### 3. Optimize Rules
Edit `match_rules.py` and implement `find_duplicates(records)`:
- Returns a list of clusters: `[[rec1, rec2, rec3], [rec4, rec5], ...]`
- Each cluster is a list of record_ids that represent the same entity
- See `program.md` for 10+ matching strategy hypotheses

### 4. Evaluate
```bash
python harness.py evaluate
```
Computes precision, recall, and F1 score against golden ground truth.

## Data Format

### Input: records.json
```json
{
  "records": [
    {
      "record_id": "R0000",
      "first_name": "John",
      "last_name": "Smith",
      "email": "john.smith@company.com",
      "phone": "+1-555-123-4567",
      "company": "Acme Corp",
      "city": "New York"
    },
    ...
  ],
  "golden_clusters": {
    "C000": ["R0000", "R0042", "R0189"],
    "C001": ["R0001", "R0043"],
    ...
  }
}
```

### Output: Clusters
```python
[
  ["R0000", "R0042", "R0189"],  # John Smith (3 duplicate records)
  ["R0001", "R0043"],            # Jane Doe (2 records)
  ...
]
```

## Matching Strategies

See `program.md` for detailed hypotheses:

1. **Exact Email Match** — High precision, identifies unambiguous duplicates
2. **Normalized Name Matching** — Handles case/whitespace variations
3. **Levenshtein Distance** — Catches typos (e.g., "Robrt" vs "Robert")
4. **Phone Normalization** — Reliable when phone is present
5. **Company Name Normalization** — Remove Inc/LLC suffixes
6. **Blocking by City** — Reduce false positives via geographic partition
7. **TF-IDF Similarity** — Holistic multi-field matching
8. **Transitive Closure** — Chain matches (if A↔B and B↔C, then A↔B↔C)
9. **Email Domain Normalization** — Username match across providers
10. **First Name Abbreviations** — Map Bob → Robert, Mike → Michael

## Evaluation Metrics

- **Precision**: Fraction of predicted duplicate pairs that are true duplicates
  - High precision = few false positives (wrongly clustered)
  - Formula: TP / (TP + FP)

- **Recall**: Fraction of true duplicate pairs that were found
  - High recall = few false negatives (missed duplicates)
  - Formula: TP / (TP + FN)

- **F1 Score**: Harmonic mean of precision and recall
  - Balanced metric, best single number to optimize
  - Formula: 2 * (P * R) / (P + R)

## Example Workflow

```bash
# 1. Generate data
python prepare.py generate
# → records.json created with 300 records

# 2. Baseline
python harness.py baseline
# → F1 = 0.0000 (no duplicates found)

# 3. Implement matching (edit match_rules.py)
# Add: exact email match, normalized name match, transitive closure

# 4. Evaluate
python harness.py evaluate
# → F1 = 0.8234 (82.34% improvement)
```

## Architecture

- **prepare.py**: Generates realistic duplicate dataset
- **match_rules.py**: Editable file with `find_duplicates()` function
- **harness.py**: Evaluation harness with anti-cheating safeguards
- **program.md**: Research plan with 10 hypotheses and experimental methodology
- **records.json**: Generated dataset (not version-controlled)

## Anti-Gaming Safeguards

The harness includes checks to ensure honest optimization:
1. **Source code inspection**: find_duplicates() cannot reference "golden" or read "records.json"
2. **Record ID validation**: All returned record_ids must exist in dataset
3. **Cluster validation**: No synthetic clusters allowed; all records must come from input

## Performance Targets

- **Baseline**: F1 = 0.0
- **Realistic Target**: F1 ≥ 0.85 (high precision + good recall)
- **Optimal**: F1 ≥ 0.95 (near-perfect dedup)

## Future Enhancements

- [ ] Support for custom fields (address, date_of_birth, etc.)
- [ ] Machine learning ranking of match scores
- [ ] Interactive UI for manual confirmation of edge cases
- [ ] Batch processing of large datasets (millions of records)
- [ ] API server for integration with CRMs

## License
Open source. Optimize, experiment, learn.
