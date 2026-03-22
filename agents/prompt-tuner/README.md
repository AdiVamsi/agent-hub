# Prompt Tuner

Optimize LLM prompt templates for text classification accuracy on your labeled dataset.

## Overview

The Prompt Tuner helps you systematically improve classification performance by iterating through prompt logic. Instead of manually tuning prompts in an LLM API, you optimize rule-based classification logic locally—which simulates what a well-prompted LLM would do.

**Baseline accuracy:** ~30% (always predict majority class)
**Achievable accuracy:** 85-95% through iterative hypothesis testing

## Quick Start

### 1. Generate Evaluation Dataset
```bash
python prepare.py generate
```
Creates `eval_dataset.json` with 200 synthetic support ticket examples:
- **bug_report** (30%): Error messages, crashes, broken functionality
- **feature_request** (25%): Requests for new capabilities
- **question** (20%): How-to questions, clarifications
- **praise** (15%): Positive feedback, compliments
- **spam** (10%): Malicious or unsolicited messages

### 2. View Baseline Performance
```bash
python harness.py baseline
```
Shows baseline accuracy with default classifier (always predicts "bug_report").

### 3. Optimize Classification Logic
Edit `prompt_config.py` and implement the `classify_text(text: str) -> str` function.

Start with simple keyword matching:
```python
def classify_text(text: str) -> str:
    text_lower = text.lower()

    # Bug signals
    if any(word in text_lower for word in ['error', 'crash', 'broken', 'failing']):
        return "bug_report"

    # Feature signals
    if any(phrase in text_lower for phrase in ['would be nice', 'please add', 'feature request']):
        return "feature_request"

    # Question signals
    if '?' in text:
        return "question"

    # Praise signals
    if any(word in text_lower for word in ['love', 'amazing', 'great', 'excellent']):
        return "praise"

    # Spam signals
    if any(word in text_lower for word in ['click here', 'limited time', 'free money']):
        return "spam"

    return "bug_report"  # Default fallback
```

### 4. Evaluate Your Classifier
```bash
python harness.py evaluate
```
Outputs:
- Overall accuracy
- Precision, recall, F1 per class
- Confusion matrix to identify misclassifications

## Research Program

See `program.md` for 10 hypothesis-driven improvements:

1. **Keyword Dictionary Matching** — Class-specific keyword sets
2. **Regex Pattern Detection** — Pattern-based class signals
3. **Weighted Scoring System** — Different signals have different weights
4. **Negation Handling** — Account for "not working" vs "working"
5. **Multi-Signal Voting** — Ensemble of classifiers
6. **Spam Detection** — URLs, capitalization, urgency signals
7. **Question Detection** — Question mark + question keywords
8. **Feature Request Patterns** — Specific linguistic markers
9. **Bug Signal Detection** — Error keywords and technical context
10. **Praise vs Neutral Sentiment** — Positive adjectives and emotion

## Experimental Strategy

- **Phase 1:** Keyword matching → ~55% accuracy
- **Phase 2:** Patterns + negation → ~65% accuracy
- **Phase 3:** Weighted scoring → ~80% accuracy
- **Phase 4:** Specialized detectors → ~85-95% accuracy

Each experiment takes ~5-10 minutes. Total headroom: 15-25 experiments.

## Why Prompt Tuner?

Traditional LLM-based prompting is:
- **Expensive:** Pay per token to API services (OpenAI, Anthropic, etc.)
- **Slow:** Iterate via API calls, wait for responses
- **Opaque:** Hard to debug why a particular prompt works
- **Inflexible:** Locked into the API provider's model versions

Prompt Tuner lets you:
- **Run locally** — No API costs, instant feedback loops
- **Understand** — See exactly why each rule fires
- **Iterate fast** — 30 experiments/hour instead of 3/hour
- **Deploy** — Convert optimized rules to prompt engineering guidance

## Comparable Services

| Service | Price | Use Case |
|---------|-------|----------|
| **PromptLayer** | $29/mo | Prompt versioning & analytics |
| **Humanloop** | $79/mo | Prompt optimization & deployment |
| **Braintrust** | $49/mo | Evaluation & prompt testing |
| **Prompt Tuner** | **Free (local)** | **Hypothesis-driven optimization** |

## Upload & Scale

Optimize your own labeled datasets with Prompt Tuner, then upload results to **agent-hub.dev** for:
- Custom classification models trained on your data
- Benchmark comparisons with other datasets
- Team collaboration on prompt engineering

**Ready to supercharge your prompts?** Generate a dataset and start experimenting.

## Files

- `prepare.py` — Generate synthetic evaluation dataset
- `prompt_config.py` — **EDIT THIS** — Your classification logic
- `harness.py` — Evaluation framework (accuracy, F1, confusion matrix)
- `program.md` — Research hypotheses and experimental strategy
- `pyproject.toml` — Project metadata (no dependencies)

## License

MIT
