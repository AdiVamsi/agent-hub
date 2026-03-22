"""prepare.py — Generate synthetic evaluation dataset for prompt tuning.

Generates eval_dataset.json with 200 text classification examples.
Each example has: text, true_label
Labels: bug_report, feature_request, question, praise, spam
Distribution: 30% bug, 25% feature, 20% question, 15% praise, 10% spam
"""

import json
import random
import argparse


def generate_bug_report():
    """Generate a realistic bug report message."""
    bugs = [
        "Getting an error when I try to upload files: 'FileNotFound' exception",
        "The dashboard keeps crashing when I open the analytics tab",
        "Search is broken, it returns no results even for existing items",
        "Login button doesn't work on mobile devices",
        "Database connection times out after 5 minutes of inactivity",
        "The export to CSV feature is throwing a JSON parse error",
        "Users report that notifications stop working after 24 hours",
        "API returns 500 error when querying with special characters",
        "Memory leak detected in the background sync process",
        "Timezone calculation is incorrect, off by 2 hours",
        "Password reset emails are not being delivered",
        "Can't delete old records, getting 'permission denied' error",
        "The autocomplete feature crashed my browser tab",
        "Scheduled jobs are failing silently without error messages",
        "Widget rendering is glitchy on older browsers",
    ]
    return random.choice(bugs)


def generate_feature_request():
    """Generate a realistic feature request message."""
    features = [
        "Would be nice to have dark mode for the interface",
        "Please add bulk export functionality to save time",
        "Can we implement two-factor authentication?",
        "It would be great if we could schedule reports automatically",
        "Feature request: custom domain support",
        "Would love to see API documentation in OpenAPI format",
        "Please add webhook support for integrations",
        "Can you add support for exporting to Excel?",
        "We need the ability to filter by date ranges",
        "It would help if we could set custom notification rules",
        "Feature request: team collaboration features",
        "Could you add a redo button to the undo feature?",
        "Would it be possible to add SSO integration?",
        "Please implement data import from CSV files",
        "Can we have more granular permission controls?",
    ]
    return random.choice(features)


def generate_question():
    """Generate a realistic support question."""
    questions = [
        "How do I reset my password if I forgot it?",
        "What's the maximum file size for uploads?",
        "Why is my account locked? How can I unlock it?",
        "How do I integrate this with my Slack workspace?",
        "Can you explain how the API rate limiting works?",
        "How long does the verification process take?",
        "Why am I seeing different results in different regions?",
        "How do I migrate my data from the old system?",
        "What are the system requirements for the desktop app?",
        "How can I backup my data regularly?",
        "Is there a free trial available?",
        "How do I contact support for urgent issues?",
        "What payment methods do you accept?",
        "How long are backups kept?",
        "Is the service available in my country?",
    ]
    return random.choice(questions)


def generate_praise():
    """Generate a realistic praise/positive feedback message."""
    praise_messages = [
        "Love the new interface! Much cleaner than before.",
        "Amazing product, saved us so much time!",
        "Great customer support, they resolved my issue quickly",
        "This tool is exactly what we needed for our workflow",
        "Impressive performance improvements in the latest update",
        "The team did an excellent job on this release",
        "I've recommended this to all my colleagues",
        "The documentation is clear and very helpful",
        "Best investment we made this year for our team",
        "Outstanding work on the new features!",
        "Your product stands out from competitors",
        "Can't imagine our workflow without this now",
        "The mobile app is incredibly smooth",
        "Your pricing is fair and the value is great",
        "Fantastic UI/UX design, very intuitive",
    ]
    return random.choice(praise_messages)


def generate_spam():
    """Generate a realistic spam message."""
    spam_messages = [
        "CLICK HERE NOW!!! Get free money instantly!!!",
        "Buy cryptocurrency with our amazing service! Visit bit.ly/xyz123",
        "🚀🚀🚀 MAKE $5000/WEEK AT HOME 🚀🚀🚀 www.scam-site.com",
        "You've been selected to claim your prize! Verify identity: http://phishing.fake",
        "LIMITED TIME OFFER!!! 90% OFF!!! Act now!!!",
        "Check out this opportunity to get rich quick!",
        "UNSUBSCRIBE: http://malware.site - if you can find it!",
        "Congratulations! You've won our lottery drawing!",
        "Hot singles in your area want to meet you!!!",
        "Dear valued customer, verify your account: hxxps://fake-bank.com",
        "URGENT: Your account will be deleted unless you verify NOW",
        "You MUST click this link immediately!!!",
        "FREE MONEY - no strings attached! Visit our site!",
        "AMAZING DEAL - limited to first 100 people! HURRY!!!",
        "Work from home and earn BIG MONEY!! http://dodgy-site.xyz",
    ]
    return random.choice(spam_messages)


def generate_dataset(num_examples: int = 200, seed: int = 42) -> list:
    """Generate synthetic dataset with specified distribution."""
    random.seed(seed)

    # Calculate counts based on distribution
    counts = {
        "bug_report": int(num_examples * 0.30),      # 30%
        "feature_request": int(num_examples * 0.25), # 25%
        "question": int(num_examples * 0.20),        # 20%
        "praise": int(num_examples * 0.15),          # 15%
        "spam": int(num_examples * 0.10),            # 10%
    }

    # Adjust to ensure we hit exactly num_examples
    counts["bug_report"] += num_examples - sum(counts.values())

    # Generate examples
    examples = []
    generators = {
        "bug_report": generate_bug_report,
        "feature_request": generate_feature_request,
        "question": generate_question,
        "praise": generate_praise,
        "spam": generate_spam,
    }

    for label, count in counts.items():
        for _ in range(count):
            text = generators[label]()
            examples.append({
                "text": text,
                "true_label": label
            })

    # Shuffle the dataset
    random.shuffle(examples)

    return examples


def save_dataset(examples: list, filepath: str = "eval_dataset.json"):
    """Save dataset to JSON file."""
    with open(filepath, "w") as f:
        json.dump(examples, f, indent=2)
    print(f"Generated {len(examples)} examples and saved to {filepath}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic evaluation dataset for prompt tuning"
    )
    parser.add_argument(
        "command",
        choices=["generate"],
        help="Command to execute"
    )
    parser.add_argument(
        "--num-examples",
        type=int,
        default=200,
        help="Number of examples to generate (default: 200)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="eval_dataset.json",
        help="Output file path (default: eval_dataset.json)"
    )

    args = parser.parse_args()

    if args.command == "generate":
        examples = generate_dataset(num_examples=args.num_examples, seed=args.seed)
        save_dataset(examples, filepath=args.output)


if __name__ == "__main__":
    main()
