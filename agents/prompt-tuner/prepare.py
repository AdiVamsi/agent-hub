"""prepare.py — Generate synthetic evaluation dataset for prompt tuning.

Generates eval_dataset.json with 200 text classification examples.
Each example has: text, true_label
Labels: bug_report, feature_request, question, praise, spam
Distribution: 30% bug, 25% feature, 20% question, 15% praise, 10% spam
"""

import json
import random
import argparse


def generate_dataset(num_examples: int = 200, seed: int = 42) -> list:
    """Generate synthetic dataset with specified distribution.

    Ensures all examples are unique by cycling through template pools
    rather than using random.choice with replacement.
    """
    random.seed(seed)

    # Define template pools for each class
    bug_templates = [
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
        "The application threw a NullPointerException when loading data",
        "Critical bug: data is being lost on every save operation",
        "Getting 'Connection refused' when trying to reach the API",
        "The form validation is broken and allows invalid entries",
        "Users experiencing data corruption after upgrade to v2.5",
        "Severe performance degradation when processing large files",
        "The application hangs indefinitely on startup",
        "File upload fails silently with no error message displayed",
        "The report export feature crashes every time I try to use it",
        "Authentication tokens are not being refreshed properly",
        "The web interface is throwing JavaScript errors in the console",
        "Data synchronization is completely broken across devices",
        "The API endpoint is returning 400 errors for valid requests",
        "The background job queue is stuck and nothing is being processed",
        "The cache is never invalidated, showing stale data permanently",
        "Search functionality returns duplicate results repeatedly",
        "The email notification system is completely non-functional",
        "Users report 'Access Denied' errors on files they own",
        "The backup process is failing with write permission errors",
        "Encoding issues causing corrupted text in database records",
        "The date picker crashes when trying to select dates in 2025",
        "Users cannot import data due to format validation bug",
        "The system is throwing out of memory errors under normal load",
        "The undo functionality is corrupting the document state",
        "The system crashes when exporting to PDF format",
        "Critical: the admin panel is returning 403 errors for admins",
        "The API rate limiter is blocking legitimate requests incorrectly",
        "The cron job for cleanup has not run in 6 months",
        "Users report inability to reset their password via email",
        "The mobile app crashes on iOS 15 devices",
        "The payment processing is failing with unhelpful error messages",
        "The database index corruption is causing query failures",
        "The session management is terminating users randomly",
        "The real-time updates are not working due to websocket issues",
        "Critical security bug: password hashing was not applied",
        "The image processing service is crashing on large uploads",
        "Users cannot log in due to session validation errors",
        "The report scheduler is not triggering scheduled tasks",
        "Console errors when switching between different views",
        "The tooltip functionality is broken in the new UI",
        "Batch processing is failing with timeout exceptions",
        "The search index is out of sync with the database",
        "Users experiencing random logouts during active sessions",
        "The audit log viewer is crashing on large datasets",
        "Field validation errors are blocking legitimate submissions",
    ]

    feature_templates = [
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
        "It would be amazing to support Slack integration",
        "Feature request: automatic backup scheduling",
        "Could you please add keyboard shortcuts to the UI?",
        "Would love to have email notifications for events",
        "Please implement batch operations for efficiency",
        "Feature: ability to customize dashboard widgets",
        "Can we add support for multiple languages?",
        "Feature request: advanced search with filters",
        "Would be great to have API rate limit information visible",
        "Please add mobile app for iOS users",
        "Could we implement role-based access control?",
        "Feature: export reports in multiple formats",
        "Would love a read-only viewer mode for clients",
        "Please add integration with Jira",
        "Feature request: scheduled email digests",
        "Can we implement field-level encryption?",
        "Feature: bulk import from external sources",
        "Would it be possible to add audit logging?",
        "Please implement workflow automation capabilities",
        "Feature: ability to clone existing configurations",
        "Could you add support for custom API endpoints?",
        "Feature request: advanced filtering and saved views",
        "Would love to have a template system for tickets",
        "Please add integration with GitHub",
        "Feature: automatic retry logic for failed operations",
        "Can we implement nested folder structures?",
        "Feature request: user activity logging and monitoring",
        "Would be nice to have a dark theme option",
        "Please add support for inline file uploads",
        "Feature: customizable email templates",
        "Could you implement dependency tracking?",
        "Feature request: batch user provisioning",
        "Would love bulk labeling capabilities",
        "Please add webhook delivery status tracking",
        "Feature: multi-currency support for pricing",
        "Could we add support for SAML authentication?",
    ]

    question_templates = [
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
        "How do I set up two-factor authentication?",
        "What is the pricing for enterprise plans?",
        "How can I export my data in bulk?",
        "Is there an API available for automation?",
        "How do I upgrade my subscription plan?",
        "Can I use this on multiple devices simultaneously?",
        "What are the bandwidth limitations?",
        "How do I delete my account permanently?",
        "Is there offline mode available?",
        "How often is the service backed up?",
        "What are the data retention policies?",
        "Can I customize the interface for my team?",
        "How do I set up custom webhooks?",
        "What are the uptime guarantees?",
        "How can I report a bug to the team?",
        "Is there a command-line interface available?",
        "How do I organize files into different projects?",
        "Can I share access with external collaborators?",
        "What is the latency of API calls typically?",
        "How do I monitor usage and costs?",
        "Is there a way to automate recurring tasks?",
        "What authentication methods are supported?",
        "How long does customer support take to respond?",
        "Can I customize notification preferences?",
        "Is the application GDPR compliant?",
        "How do I bulk import users to my account?",
        "What are the supported file formats?",
        "How do I enable single sign-on for my team?",
        "Is there a mobile app for Android?",
        "How do I manage API keys and tokens?",
        "Can I schedule tasks to run at specific times?",
        "What regions are supported for data storage?",
        "How do I troubleshoot connection issues?",
        "Is there version control for my files?",
        "How can I improve performance for large datasets?",
        "What happens to my data if I cancel my subscription?",
    ]

    praise_templates = [
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
        "Absolutely love how easy it is to use!",
        "The integration with our other tools is seamless",
        "Best product in its category, hands down",
        "Your support team is incredibly responsive",
        "The features are exactly what we needed",
        "I'm impressed by how well this scales",
        "The update yesterday was phenomenal",
        "Your attention to detail is remarkable",
        "The performance has improved dramatically",
        "I can't believe how much time we save now",
        "The user interface is beautifully designed",
        "This product exceeded all our expectations",
        "The quality of your work is exceptional",
        "I love the attention to user experience",
        "Your team is super helpful and responsive",
        "The reliability of this service is outstanding",
        "I'm thrilled with the latest features",
        "The value for money is incredible",
        "This is by far the best solution available",
        "The customer service experience was excellent",
        "I'm really impressed with your innovation",
        "The product keeps getting better",
        "Kudos to your engineering team",
        "This solved all our problems perfectly",
        "I appreciate the frequent updates",
    ]

    spam_templates = [
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
        "Forex trading signals guaranteed to make profits!!! tinyurl.com/abc",
        "Get Viagra NOW - BEST PRICES ONLINE!!! Click here",
        "SEO SERVICES - GUARANTEED FIRST PAGE RANKING!!! http://seo.fake",
        "WIN BIG at our online casino!! LIMITED SLOTS AVAILABLE!!!",
        "Inheritance from long lost relative - claim your $2 million NOW",
        "WEIGHT LOSS PILLS - Lose 30 pounds in 30 days!!!",
        "Refinance your mortgage!!! GET CASH NOW!!! http://loan.scam",
        "PENNY STOCKS that will TRIPLE in value!!! Buy now!!!",
        "Congratulations, you have been selected for a FREE VACATION!!!",
        "Nigerian prince needs your help! Easy money for you!!!",
        "ROLEX WATCHES 50% OFF!!! ORIGINAL QUALITY!!! Buy here!!!",
        "MALE ENHANCEMENT PILLS - ROCK HARD PERFORMANCE!!!",
        "Emergency: Confirm your bank details or account frozen!!!",
        "Click now to see EXCLUSIVE CONTENT!!! Adults only!!!",
        "Become a millionaire in 90 days with our system!!!",
        "FREE IPADS - Just pay shipping!!! http://freestuff.fake",
        "INSTANT PAYDAY LOANS - NO CREDIT CHECK NEEDED!!!",
        "FAKE DESIGNER BAGS - Cheap and authentic!!! Order now!!!",
    ]

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

    # Generate examples by cycling through templates to ensure uniqueness
    examples = []
    template_pools = {
        "bug_report": bug_templates,
        "feature_request": feature_templates,
        "question": question_templates,
        "praise": praise_templates,
        "spam": spam_templates,
    }

    # Create cycle indices for each class
    indices = {label: 0 for label in counts.keys()}

    for label, count in counts.items():
        pool = template_pools[label]
        for i in range(count):
            # Cycle through the template pool to avoid duplicates
            text = pool[indices[label] % len(pool)]
            indices[label] += 1
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
