# Regex Chef

**Regex Chef** is an AutoResearch agent that optimizes regex patterns for maximum accuracy on labeled validation sets. Submit a pattern type, test cases, and let the system iteratively refine your regexes.

## Features

- **Automated Optimization**: Uses Karpathy's AutoResearch pattern to systematically explore hypothesis space
- **Validation-Driven**: Tests patterns against 200 curated examples covering 6 pattern types
- **Edge Case Coverage**: Includes realistic tricky cases (leap years, IP ranges, email plus-addressing, etc.)
- **Anti-Gaming Checks**: Prevents overfitting and hardcoding via source code validation
- **Accuracy Metrics**: Per-type and overall accuracy with improvement tracking

## Pattern Types

1. **email**: RFC-ish email validation (40 examples)
2. **phone_us**: US phone number formats (35 examples)
3. **ipv4**: IPv4 address validation (30 examples)
4. **date_iso**: ISO 8601 date format (35 examples)
5. **url**: HTTP/HTTPS/FTP URLs (35 examples)
6. **semver**: Semantic versioning (25 examples)

## Quick Start

### Generate Validation Set
```bash
python prepare.py generate
```
Creates `validation_set.json` with 200 labeled test cases across all pattern types.

### Evaluate Baseline
```bash
python harness.py baseline
```
Shows baseline accuracy (~0.55-0.65) with simple patterns.

### Evaluate Current Patterns
```bash
python harness.py
```
Tests `patterns.py` against validation set and reports per-type accuracy + overall improvement %.

### Edit Patterns
Edit `PATTERNS` dict in `patterns.py` to refine regexes. Re-run `harness.py` to measure impact.

## Example Pattern Refinement

**Baseline** (phone_us):
```python
"phone_us": r"\d{3}-\d{3}-\d{4}"
```
Accuracy: 0.60 (only matches hyphens, fails on parens/spaces)

**Hypothesis 1** (add parens variant):
```python
"phone_us": r"(\d{3}-\d{3}-\d{4}|(\d{3}) \d{3}-\d{4})"
```
Accuracy: 0.72 (+20%)

**Hypothesis 2** (handle all separators + international):
```python
"phone_us": r"(\+1\s?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
```
Accuracy: 0.85 (+42% from baseline)

## Revenue Model

**Upload your patterns + test cases at [agent-hub.dev](https://agent-hub.dev)**

Regex Chef enables:
- **Consultants**: Publish custom pattern validators for domains (medical billing, compliance, etc.)
- **Teams**: Share optimized patterns across projects
- **Enterprises**: Version control regex libraries with validation guarantees

### Comparable Products
- **regex101 Pro**: $10/month (online tester, limited sharing)
- **Debuggex**: $5/month (regex visualizer, basic testing)
- **Regex Chef**: $0 (open-source) / $5/month (cloud optimization + pattern library)

## Structure

```
regex-chef/
├── prepare.py           # Generate validation_set.json
├── patterns.py          # EDITABLE: Your regex patterns here
├── harness.py           # Test harness & evaluation metrics
├── validation_set.json  # 200 labeled test cases (generated)
├── program.md           # AutoResearch hypothesis plan
├── README.md            # This file
└── pyproject.toml       # Project metadata
```

## Implementation Notes

- **Language**: Python 3.7+
- **Dependencies**: None (standard library only)
- **Metric**: Accuracy = (correct_predictions) / (total_tests)
- **Evaluation**: Uses `re.fullmatch()` for full-string matching
- **Anti-Gaming**: Harness validates patterns aren't hardcoding test strings

## Development Philosophy

Regex Chef follows **Karpathy's AutoResearch** methodology:
1. Start with curated, labeled data (validation_set.json)
2. Define baseline (simple patterns)
3. Formulate hypotheses (edge case handling, validation rules)
4. Test iteratively and measure improvement
5. Refine based on error analysis
6. Consolidate optimal patterns

Expected trajectory:
- Baseline: 0.55-0.65 accuracy
- After hypothesis exploration: 0.92-0.98 accuracy
- Typical: 15-25 experiments to reach optimal

## License

Open source. Use, modify, share freely.

## Contact

Questions? Issues? Contribute patterns or test cases at [agent-hub.dev](https://agent-hub.dev)
