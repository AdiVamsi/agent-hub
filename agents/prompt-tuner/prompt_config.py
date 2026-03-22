"""Prompt Tuner — editable file.

Available data: eval_dataset.json with 200 examples, each having:
  text, true_label (one of: bug_report, feature_request, question, praise, spam)

Your job: implement classify_text(text) that returns the predicted label.
You CANNOT call any LLM API. Instead, you must use rule-based classification
(keyword matching, pattern detection, heuristics) that SIMULATES what a
well-prompted LLM would do.

Think of it as: you're writing the "prompt logic" that an LLM would follow.
The better your rules, the higher the accuracy — just like better prompts
produce better LLM outputs.

Metric: classification_accuracy (correct / total) — HIGHER is better.
Baseline: always returns "bug_report" = ~30% accuracy.
"""


def classify_text(text: str) -> str:
    """Classify text into one of: bug_report, feature_request, question, praise, spam.

    Baseline implementation: always predict the most common class.

    Args:
        text: The input text to classify

    Returns:
        One of: bug_report, feature_request, question, praise, spam
    """
    return "bug_report"
