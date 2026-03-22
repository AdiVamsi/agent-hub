# Prompt Tuner — Research Program

## Objective
Optimize text classification accuracy from 30% (baseline) to 85-95% through rule-based prompt logic.

## Core Hypothesis
A well-structured rule-based system with keyword dictionaries, pattern matching, and weighted scoring can effectively classify support tickets into 5 categories: bug_report, feature_request, question, praise, spam.

## Hypotheses to Test

### H1: Keyword Dictionary Matching
**Rationale:** Each class has distinctive keywords that appear frequently.
- Bug signals: error, crash, broken, failing, exception, bug, issue, problem, not working
- Feature signals: would be nice, please add, feature request, can we, could you, would love
- Question signals: how, why, what, when, can you, is it, how do I
- Praise signals: love, great, amazing, excellent, impressed, fantastic, outstanding
- Spam signals: click here, limited time, free money, act now, urgent

**Implementation:** Create keyword sets per class, score text based on keyword presence.

---

### H2: Regex Pattern Detection
**Rationale:** Certain patterns are strongly indicative of class membership.
- Bug patterns: `error.*message`, `crash`, `exception`, `stack trace`
- Feature patterns: `would.*be.*nice`, `feature request`, `please add`, `can we implement`
- Question patterns: Text ending with `?`, contains `how do`, `why`, `what is`
- Spam patterns: `click here`, `!!!`, `limited.*time`, `act now`, URLs with shorteners

**Implementation:** Compile regexes, match against text, assign class scores.

---

### H3: Weighted Scoring System
**Rationale:** Different signals have different confidence levels.
- Exact phrase matches: weight 3.0
- Keyword presence: weight 2.0
- Pattern match: weight 1.5
- Punctuation/caps intensity: weight 0.5

**Implementation:** Sum weighted scores per class, choose class with highest score.

---

### H4: Negation Handling
**Rationale:** Negations flip meaning (e.g., "Not working" vs "Working").
- Words like "not", "no", "don't", "can't" often precede the actual problem
- Affects bug detection: "not working" should be detected as bug

**Implementation:** Look back 1-2 words from keywords to check for negation markers.

---

### H5: Multi-Signal Voting System
**Rationale:** Ensemble of independent classifiers is more robust.
- Signal 1: Keyword matching (40% weight)
- Signal 2: Regex patterns (30% weight)
- Signal 3: Question mark detection (15% weight)
- Signal 4: Urgency/spam signals (15% weight)

**Implementation:** Run each signal independently, aggregate with weights.

---

### H6: Spam Detection with URL and Capitalization
**Rationale:** Spam has distinctive formatting patterns.
- Presence of shortened URLs (bit.ly, tinyurl, etc.)
- Excessive capitalization (MAKE MONEY, LIMITED TIME)
- Multiple exclamation marks (!!!!)
- "Unsubscribe" links
- Promises of easy money or prizes

**Implementation:** Score text for spam characteristics, high threshold triggers spam label.

---

### H7: Question Detection via Question Mark Presence
**Rationale:** Questions almost always end with `?`.
- Simple heuristic: If text contains `?`, likely a question
- Refine: Check for question keywords (how, why, what, can you, is it)
- Edge case: Bug reports sometimes include questions, but leading context is "broken"

**Implementation:** High confidence for `?` presence, boost with question keywords.

---

### H8: Feature Request Semantic Patterns
**Rationale:** Feature requests use specific linguistic markers.
- Polite/conditional: "would be nice", "would like", "could you", "please add"
- Future-oriented: "implement", "add", "support", "enable"
- Common phrases: "feature request:", "new feature", "enhancement"

**Implementation:** Look for these phrase patterns, score accordingly.

---

### H9: Bug Signal Detection with Error Keywords
**Rationale:** Bug reports contain specific technical error language.
- Error keywords: error, exception, crash, fail, broken, not working
- Technical context: code, function, API, database, memory
- Action language: "getting", "getting an", "trying to"

**Implementation:** Heavy weight on error keywords, moderate on technical context.

---

### H10: Praise vs Neutral Sentiment
**Rationale:** Praise uses positive adjectives and exclamation marks.
- Positive words: love, great, amazing, excellent, awesome, fantastic, impressed
- Sentiment intensity: Multiple positive words in short text
- Exclamation marks (but not spam-level multiple)

**Implementation:** Positive word dictionary, sentiment scoring.

---

## Experimental Strategy

### Phase 1: Baseline (Accuracy ~30%)
- Implement H1: Keyword dictionary matching
- Expected improvement: +15-25%

### Phase 2: Pattern Enhancement (Accuracy ~55-60%)
- Add H2: Regex patterns
- Add H4: Negation handling
- Expected improvement: +10-15%

### Phase 3: Refinement (Accuracy ~70-80%)
- Implement H3: Weighted scoring
- Tune class-specific thresholds
- Expected improvement: +10-15%

### Phase 4: Polish (Accuracy ~85-95%)
- Add H5-H10: Specialized detectors
- Ensemble voting
- Fine-tune via confusion matrix analysis

## Success Metrics

- **Primary:** classification_accuracy ≥ 0.85
- **Secondary:** Per-class F1 scores ≥ 0.75 for each class
- **Target:** Improvement of 55-65 percentage points from baseline

## Experimentation Headroom

Estimated 15-25 experiments possible before diminishing returns:
1. Keyword set tuning
2. Regex pattern refinement
3. Weight optimization
4. Negation window sizes
5. Voting thresholds
6. Per-class score multipliers
7. etc.

---

## Critical Constraint: Anti-Memorization

Your `classify_text()` function must work through **GENERAL RULES** (keywords, patterns, regex), not by memorizing specific examples from the evaluation dataset.

**Memorization is Prohibited:** The harness will check that your function source code does not contain more than 5 specific words appearing in eval_dataset.json examples.

**Why:** With 200 unique examples in eval_dataset.json, memorization would trivially achieve high accuracy but would fail on new data. Your goal is to build a generalizable classifier using linguistic patterns and rule-based logic.

**How to Pass:** Use general patterns like:
- Keyword dictionaries (error, crash, bug, request, please, feature, etc.)
- Regex patterns (question marks, URLs, ALL CAPS, emojis, etc.)
- Weighted scoring systems
- Do NOT hardcode specific phrases from the dataset

---

## Notes for Implementation

- Keep all logic in `prompt_config.py` in the `classify_text()` function
- No external API calls allowed
- Optimize for readability and interpretability
- Comment your rules so they're understandable
- Track changes via confusion matrix improvements per class
- **Remember: generalize from patterns, not from memorization**
