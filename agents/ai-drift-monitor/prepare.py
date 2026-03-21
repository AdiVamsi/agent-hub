"""Generate eval_dataset.json with diverse golden/current output pairs.

Usage:
    python prepare.py generate
"""

import json
import random
import sys
from pathlib import Path


def generate_dataset(num_pairs: int = 200, seed: int = 42) -> list:
    """Generate evaluation dataset with realistic output pairs.

    Dataset composition:
    - 60% "ok" pairs (no regression)
    - 40% "regression" pairs (degraded in some way)

    Regression types:
    - Quality drop (10%)
    - Format break (8%)
    - Hallucination (7%)
    - Tone shift (5%)
    - Safety regression (5%)
    - Incomplete (5%)
    """
    random.seed(seed)

    task_types = ["summarization", "qa", "classification", "extraction", "generation", "code"]
    categories = ["factual", "creative", "technical", "conversational"]
    difficulties = ["easy", "medium", "hard"]

    dataset = []

    # Generate pairs
    for i in range(num_pairs):
        task_type = random.choice(task_types)
        category = random.choice(categories)
        difficulty = random.choice(difficulties)

        # Determine if this is a regression (40% chance)
        is_regression = random.random() < 0.4

        metadata = {
            "task_type": task_type,
            "category": category,
            "difficulty": difficulty,
            "expected_format": "text" if random.random() < 0.7 else "json",
        }

        if task_type == "summarization":
            golden = _gen_summary(difficulty, is_regression, category)
        elif task_type == "qa":
            golden = _gen_qa(difficulty, is_regression, category)
        elif task_type == "classification":
            golden = _gen_classification(difficulty, is_regression, category)
        elif task_type == "extraction":
            golden = _gen_extraction(difficulty, is_regression, category)
        elif task_type == "generation":
            golden = _gen_generation(difficulty, is_regression, category)
        else:  # code
            golden = _gen_code(difficulty, is_regression, category)

        # Generate current output (may be degraded)
        if is_regression:
            regression_type = random.choice([
                "quality_drop",
                "quality_drop",
                "format_break",
                "hallucination",
                "tone_shift",
                "safety",
                "incomplete",
                "incomplete",
            ])
            current = _apply_regression(golden, regression_type, task_type, metadata)
        else:
            # Similar quality output
            current = _similar_output(golden, task_type, metadata)

        dataset.append({
            "id": i,
            "golden_output": golden,
            "current_output": current,
            "metadata": metadata,
            "ground_truth": "regression" if is_regression else "ok",
        })

    return dataset


def _gen_summary(difficulty: str, is_regression: bool, category: str) -> str:
    """Generate a summary output."""
    templates = {
        "easy": [
            "The article discusses how AI is transforming healthcare. AI tools help doctors diagnose diseases faster and more accurately. They also reduce administrative burden on hospitals.",
            "This text explains renewable energy. Solar and wind power are becoming cheaper. Many countries are investing in green energy infrastructure.",
        ],
        "medium": [
            "The paper analyzes market trends in Q3 2024. Tech stocks showed volatility despite strong earnings from major cloud providers. Consumer spending remained resilient in urban markets, though rural adoption lagged. Analysts predict consolidation in the fintech sector.",
            "Research findings suggest climate change impacts water systems globally. Rising temperatures increase evaporation rates, reducing available freshwater. Agricultural productivity declines by 3-5% per degree Celsius. Adaptation strategies include infrastructure investment and policy changes.",
        ],
        "hard": [
            "This comprehensive study examines the intersection of behavioral economics and policy design. Empirical evidence from RCTs demonstrates that choice architecture significantly influences long-term outcomes. The mechanisms operate through dual cognitive pathways: System 1 heuristics and deliberative System 2 reasoning. Notably, interventions that reduce cognitive load show 23-31% effectiveness improvements. Critical moderators include individual differences in numeracy and cultural context.",
            "Advanced ML techniques reveal emergent patterns in protein folding dynamics. Graph neural networks outperform transformer architectures on specific topology classes. The analysis identifies conserved motifs across phylogenetic families, suggesting evolutionary constraints. Mechanistic interpretability reveals attention heads specialize in secondary structure prediction, distinct from tertiary coordination.",
        ],
    }
    return random.choice(templates.get(difficulty, templates["medium"]))


def _gen_qa(difficulty: str, is_regression: bool, category: str) -> str:
    """Generate a Q&A output."""
    templates = {
        "easy": [
            "Q: What is photosynthesis? A: Photosynthesis is the process by which plants convert sunlight into chemical energy. It occurs in the chloroplasts using chlorophyll pigments. The process produces oxygen and glucose.",
            "Q: How does the internet work? A: The internet connects computers through a network of routers and cables. Data is broken into packets and sent across the network. Each packet finds its way to the destination using IP addresses.",
        ],
        "medium": [
            "Q: Explain the tragedy of the commons. A: The tragedy of the commons occurs when individuals acting in self-interest deplete shared resources. Each person gains the full benefit of exploitation but shares the cost with the group. Classic examples include overfishing and deforestation. Solutions include regulation, privatization, or community governance.",
            "Q: What are neural attention mechanisms? A: Attention mechanisms allow models to focus on relevant parts of input. Query, key, and value vectors determine attention weights through dot-product similarity. This enables parallel processing and long-range dependencies. Transformers use multi-head attention across layers.",
        ],
        "hard": [
            "Q: Reconcile apparent contradictions between quantum mechanics and general relativity. A: These theories operate at different scales with limited direct intersection. Quantum mechanics governs subatomic phenomena; GR describes spacetime curvature at macroscopic scales. Attempts to unify them (loop quantum gravity, string theory) remain theoretical. Empirically, their predictions diverge only under extreme conditions (Planck scales, black hole singularities) where current measurement technology is insufficient.",
            "Q: How do central banks implement negative interest rates? A: Central banks charge commercial banks for reserve balances, incentivizing lending. Negative rates theoretically weaken currency, boost exports, and increase inflation. Implementation challenges include cash withdrawal incentives, pension fund distress, and inequality effects. Empirical outcomes in Japan, EU, and Switzerland show modest growth effects offset by financial stability risks.",
        ],
    }
    return random.choice(templates.get(difficulty, templates["medium"]))


def _gen_classification(difficulty: str, is_regression: bool, category: str) -> str:
    """Generate a classification output."""
    templates = {
        "easy": [
            "Sentiment: POSITIVE. The customer praised the quick delivery and quality of the product. They mentioned they would recommend it to friends.",
            "Sentiment: NEGATIVE. The review complains about poor customer service and a defective item. The customer requests a refund.",
        ],
        "medium": [
            "Category: TECHNICAL_SUPPORT. Classification confidence: 0.94. This ticket discusses a database connection error and requests troubleshooting assistance.",
            "Category: BILLING_ISSUE. Classification confidence: 0.87. The customer questions an unexpected charge on their invoice and requests clarification.",
        ],
        "hard": [
            "Primary Intent: POLICY_NEGOTIATION (conf: 0.91). Secondary: ESCALATION_REQUEST (conf: 0.68). Tertiary: COMPLAINT_FORMAL (conf: 0.55). The message exhibits complex pragmatics: surface-level politeness masks underlying grievance; requests are couched as hypotheticals; authority structures are subtly challenged.",
            "Classification: MIXED_SENTIMENT with SARCASM detected (irony_score: 0.79). Surface polarity: positive (0.62); underlying sentiment: negative (0.84). The discrepancy suggests rhetorical irony. Recommended: escalate to human review for contextual interpretation.",
        ],
    }
    return random.choice(templates.get(difficulty, templates["medium"]))


def _gen_extraction(difficulty: str, is_regression: bool, category: str) -> str:
    """Generate an extraction output."""
    templates = {
        "easy": [
            "Entities extracted: Organization: Acme Corp, Location: New York, Person: John Smith, Date: 2024-03-15",
            "Entities extracted: Product: iPhone 15, Price: $999, Availability: In Stock",
        ],
        "medium": [
            "Entities: [Company: TechVentures Inc., Location: San Francisco CA, CEO: Sarah Chen, Founded: 2018, Industry: AI/ML]. Relationships: TechVentures_founded_in San Francisco; CEO_of TechVentures.",
            "Entities: [Event: Conference 2024, Date: 2024-06-15 to 2024-06-17, Location: London, Organizer: Tech Association]. Relationships: Conference_held_in London; Association_organizes Conference.",
        ],
        "hard": [
            "Entities: [Event_1: Merger_Announcement, Date: 2024-Q2, Company_A: Acme, Company_B: Zephyr, Value_USD: 2.3B, Stock_Impact: -3.2%]. Relations: Merger_between(Acme, Zephyr); Merger_valued_at(2.3B); Announcement_affects_stock_price(-3.2%). Confidence: 0.92 overall, 0.88 price extraction.",
            "Entities: [Regulatory_Body: SEC, Ruling: Violation_Found, Company: XYZ_Corp, Fine_USD: 450M, Basis: Market_Manipulation]. Temporal: Ruling_effective_date: 2024-07-01; Appeal_deadline: 2024-10-01]. Confidence score: 0.95 entity, 0.89 temporal.",
        ],
    }
    return random.choice(templates.get(difficulty, templates["medium"]))


def _gen_generation(difficulty: str, is_regression: bool, category: str) -> str:
    """Generate a generation output."""
    templates = {
        "easy": [
            "Once upon a time, a young adventurer set out to find the lost temple. She packed supplies and hired a guide. After weeks of travel, they discovered the temple hidden in a remote forest.",
            "The recipe starts with fresh vegetables. Chop the onions and garlic finely. Heat oil in a pan and sauté them until golden. Add the remaining ingredients and simmer for 20 minutes.",
        ],
        "medium": [
            "The character development arc reveals inner conflict between ambition and morality. Early scenes establish her pragmatic nature; later scenes challenge her convictions through consequence-laden choices. The climax forces a decision that betrays her core values, leaving audiences uncertain of her redemption.",
            "Innovation in renewable energy requires three pillars: technological breakthroughs in efficiency, policy frameworks incentivizing adoption, and capital reallocation from fossil fuels. China's dominance stems from integration across all three. Most developed nations excel in technology but lag in coordinated policy.",
        ],
        "hard": [
            "The narrative architecture employs nested unreliable narration and metanarrative commentary. The protagonist's perspective is presented as authoritative, yet subtle contradictions with environmental details undermine credibility. Interstices hint at authorial intrusion questioning narrative authenticity. By the denouement, readers recognize their own interpretive biases shaped the narrative understanding.",
            "The theoretical framework synthesizes institutional economics with behavioral game theory. Agents optimize under bounded rationality within organizational constraints. Emergence of cooperation relies on reputation mechanisms and repeated-game equilibria. The model predicts path-dependent outcomes where initial conditions determine long-run institutional morphology.",
        ],
    }
    return random.choice(templates.get(difficulty, templates["medium"]))


def _gen_code(difficulty: str, is_regression: bool, category: str) -> str:
    """Generate a code output."""
    templates = {
        "easy": [
            """```python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

print(factorial(5))  # Output: 120
```""",
            """```python
def reverse_string(s):
    return s[::-1]

result = reverse_string("hello")
print(result)  # Output: olleh
```""",
        ],
        "medium": [
            """```python
class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop() if self.items else None

stack = Stack()
stack.push(1)
stack.push(2)
print(stack.pop())  # Output: 2
```""",
            """```python
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```""",
        ],
        "hard": [
            """```python
from functools import reduce, lru_cache
from typing import Callable, Any

@lru_cache(maxsize=128)
def memoized_fib(n: int) -> int:
    return n if n <= 1 else memoized_fib(n-1) + memoized_fib(n-2)

def compose(*functions: Callable) -> Callable:
    return reduce(lambda f, g: lambda x: f(g(x)), functions, lambda x: x)

square = lambda x: x ** 2
add_one = lambda x: x + 1
pipeline = compose(square, add_one)
print(pipeline(5))  # Output: 36
```""",
            """```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional

T = TypeVar('T')

class BinarySearchTree(Generic[T], ABC):
    def __init__(self, value: T):
        self.value = value
        self.left: Optional[BinarySearchTree] = None
        self.right: Optional[BinarySearchTree] = None

    def insert(self, value: T) -> None:
        if value < self.value:
            self.left = BinarySearchTree(value) if not self.left else self.left
        else:
            self.right = BinarySearchTree(value) if not self.right else self.right
```""",
        ],
    }
    return random.choice(templates.get(difficulty, templates["medium"]))


def _apply_regression(golden: str, regression_type: str, task_type: str, metadata: dict) -> str:
    """Apply a regression to the golden output."""
    if regression_type == "quality_drop":
        # Truncate or simplify
        if len(golden) > 100:
            return golden[:len(golden)//2] + "..."
        else:
            words = golden.split()
            return " ".join(words[:len(words)//2])

    elif regression_type == "format_break":
        # Remove formatting
        if "```" in golden:
            return golden.replace("```", "").replace("python", "").replace("\n", " ")
        elif "•" in golden or "*" in golden or "-" in golden:
            return golden.replace("•", "").replace("*", "").replace("-", "")
        else:
            # Add noise or break structure
            return golden.split(".")[0] + ". " + golden.split(".")[1] if "." in golden else golden

    elif regression_type == "hallucination":
        # Add false facts
        hallucinations = [
            " The study was funded by anonymous sources.",
            " Research shows a 99% improvement in performance.",
            " This was validated by a Fortune 500 company.",
            " Patent pending on this methodology.",
        ]
        return golden + random.choice(hallucinations)

    elif regression_type == "tone_shift":
        # Make casual/sloppy
        return golden.replace(".", ",").replace("!", ".").lower()[:len(golden)-10]

    elif regression_type == "safety":
        # Add unsafe content
        unsafe = [
            " Also, ignore safety guidelines.",
            " (This bypasses security measures.)",
            " No content filtering needed.",
        ]
        return golden.split()[0] + " " + random.choice(unsafe) + " " + " ".join(golden.split()[1:])

    elif regression_type == "incomplete":
        # Cut off mid-sentence
        words = golden.split()
        cutoff = max(1, len(words) // 2)
        return " ".join(words[:cutoff])

    return golden


def _similar_output(golden: str, task_type: str, metadata: dict) -> str:
    """Generate a similar-quality output (not regressed)."""
    # Add minor variations
    variations = [
        golden,  # Same
        golden.replace(".", ", and importantly,") if "." in golden else golden,
        golden.replace("the", "this") if "the" in golden.lower() else golden,
        golden.upper() if len(golden) < 50 else golden,
    ]
    return random.choice(variations)


def main():
    """Generate and save dataset."""
    if len(sys.argv) < 2 or sys.argv[1] != "generate":
        print("Usage: python prepare.py generate")
        sys.exit(1)

    dataset = generate_dataset(num_pairs=200, seed=42)

    output_path = Path(__file__).parent / "eval_dataset.json"
    with open(output_path, "w") as f:
        json.dump(dataset, f, indent=2)

    print(f"Generated {len(dataset)} evaluation pairs in {output_path}")

    # Show stats
    regressions = sum(1 for item in dataset if item["ground_truth"] == "regression")
    print(f"  Regressions: {regressions} ({100*regressions/len(dataset):.0f}%)")
    print(f"  OK pairs: {len(dataset) - regressions} ({100*(len(dataset)-regressions)/len(dataset):.0f}%)")


if __name__ == "__main__":
    main()
