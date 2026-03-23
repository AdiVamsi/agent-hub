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
    import re
    t = text.strip()
    lower = t.lower()
    alpha_chars = [c for c in t if c.isalpha()]
    caps_ratio = sum(1 for c in alpha_chars if c.isupper()) / max(len(alpha_chars), 1)
    excl_count = t.count("!")

    if re.search(r"https?://|tinyurl|bit\.ly|hxxps|phishing|\.xyz\b", t, re.I):
        return "spam"
    if re.search(r"www\.\w", t):
        return "spam"
    if caps_ratio > 0.30 and excl_count >= 1:
        return "spam"
    if excl_count >= 3:
        return "spam"
    for w in ["lottery", "casino", "prize", "viagra", "cryptocurrency", "inheritance", "unsubscribe"]:
        if re.search(r"\b" + w + r"\b", lower):
            return "spam"
    if re.search(r"\bFREE\b", t) or re.search(r"\bURGENT\b", t):
        return "spam"
    if re.search(r"\bdear\s+valued\b", lower) or re.search(r"\bclick\s+here\b", lower):
        return "spam"
    if re.search(r"\brich\s*quick\b", lower):
        return "spam"

    if re.search(r"\bfeature\s*(request|:)", lower):
        return "feature_request"
    if re.search(r"\bplease\s+(add|implement|include|enable|build|create|support)\b", lower):
        return "feature_request"
    if re.search(r"\bwould\b.{1,30}\b(nice|helpful|great)\b", lower):
        return "feature_request"
    if re.search(r"\bwould\s+love\b", lower):
        return "feature_request"
    if re.search(r"\bwould\b.{1,40}\bto\s+(have|see|support|add|implement)\b", lower):
        return "feature_request"
    if re.search(r"\bwould\b.{1,15}\bhelp\b", lower):
        return "feature_request"
    if re.search(r"\bcould\s+(you|we)\s+(add|implement|introduce|build|create|support)\b", lower):
        return "feature_request"
    if re.search(r"\bcan\s+(you|we)\s+(add|implement|support|build|create|include)\b", lower):
        return "feature_request"
    if re.search(r"\bpossible\b.{1,20}\b(add|implement|support|integrate)\b", lower):
        return "feature_request"
    if re.search(r"\bability\s+to\b", lower):
        return "feature_request"

    if t.endswith("?"):
        return "question"
    if re.match(r"^(what|how|why|when|where|who)\b", lower):
        return "question"
    if re.match(r"^can\s+[iy]\b", lower):
        return "question"
    if re.match(r"^is\s+\w", lower):
        return "question"
    if re.match(r"^(do|does|are|will)\s+\w", lower):
        return "question"

    if re.match(r"^i\s+can.t\s+(imagine|believe)\b", lower):
        return "praise"
    for w in ["impressed", "outstanding", "phenomenal", "remarkable", "exceptional",
              "fantastic", "excellent", "seamless", "intuitive", "incredible",
              "amazing", "exceeded", "smooth", "beautifully", "responsive",
              "recommended", "impressive", "great", "helpful", "improved",
              "exactly", "saved", "imagine"]:
        if re.search(r"\b" + w + r"\b", lower):
            return "praise"
    if re.search(r"stands\s+out", lower):
        return "praise"
    if re.search(r"\blove\b", lower) and "feature" not in lower:
        return "praise"
    if re.search(r"\bbest\b", lower) and not re.search(r"\b(bug|error|fail)\b", lower):
        return "praise"

    for w in ["broken", "failing", "failed", "fails", "error", "crash", "crashes",
              "exception", "bug", "problem", "silently", "incorrect", "unexpected",
              "regression", "intermittent"]:
        if re.search(r"\b" + w + r"\b", lower):
            return "bug_report"
    if re.search(r"not\s+working|doesn.t\s+work|does\s+not\s+work", lower):
        return "bug_report"

    return "bug_report"
