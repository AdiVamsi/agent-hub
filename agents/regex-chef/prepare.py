"""Generate validation_set.json — 200 labeled strings across 6 pattern types.

Following Karpathy's AutoResearch pattern: prepare curated test data for optimization.
"""
import json
import random
from pathlib import Path


def generate_validation_set():
    """Generate 200 labeled test strings across 6 pattern types."""
    random.seed(42)

    validation_set = []
    test_id = 0

    # EMAIL (40 examples: ~60% valid, ~40% invalid)
    email_examples = [
        # Valid emails
        ("user@example.com", True, "basic email"),
        ("john.doe@example.com", True, "dot in local part"),
        ("alice+tag@example.co.uk", True, "plus addressing"),
        ("test.email+alex@leetcode.com", True, "complex plus"),
        ("name@subdomain.example.org", True, "subdomain"),
        ("user123@test-domain.com", True, "number and hyphen"),
        ("a@b.c", True, "minimal valid"),
        ("first.last@example.museum", True, "long TLD"),
        ("user@192.168.1.1", True, "IP-based email"),
        ("test_underscore@example.com", True, "underscore"),
        ("info@example.co.jp", True, "international TLD"),
        ("contact@my-site.com", True, "hyphen in domain"),
        ("admin@localhost.local", True, "localhost domain"),
        ("user+spam@example.com", True, "plus at end"),
        ("123@example.com", True, "numeric local"),
        ("user@example.xn--80akhbyknj4f", True, "IDN domain"),
        ("a.b.c@example.com", True, "multiple dots in local"),
        ("test@example.名前", True, "unicode in domain"),
        ("user@example.中国", True, "unicode domain"),
        ("noreply@github.com", True, "common service"),
        ("no-reply@example.com", True, "hyphen in local"),
        ("first+last@sub.example.com", True, "plus with subdomain"),
        ("_user@example.com", True, "leading underscore"),
        ("user_@example.com", True, "trailing underscore"),
        # Invalid emails
        ("plainaddress", False, "no at sign"),
        ("@example.com", False, "no local part"),
        ("user@", False, "no domain"),
        ("user @example.com", False, "space in local"),
        ("user@example .com", False, "space in domain"),
        ("user@@example.com", False, "double at"),
        ("user@example..com", False, "double dot in domain"),
        ("user.@example.com", False, "trailing dot in local"),
        (".user@example.com", False, "leading dot in local"),
        ("user@.example.com", False, "leading dot in domain"),
        ("user@example.com.", False, "trailing dot in domain"),
        ("user@example.c", False, "single char TLD (usually invalid)"),
        ("user example@example.com", False, "space in middle"),
        ("user@exam ple.com", False, "space in domain"),
        ("user@example,com", False, "comma instead of dot"),
        ("user#example.com", False, "hash instead of at"),
    ]

    # PHONE_US (35 examples: ~60% valid, ~40% invalid)
    phone_examples = [
        # Valid formats
        ("(555) 123-4567", True, "parentheses with space"),
        ("555-123-4567", True, "hyphens"),
        ("555 123 4567", True, "spaces"),
        ("+1 555 123 4567", True, "international with +1"),
        ("5551234567", True, "no separators"),
        ("+1-555-123-4567", True, "+1 with hyphens"),
        ("+1 (555) 123-4567", True, "+1 with parentheses"),
        ("(555)123-4567", True, "parentheses no space"),
        ("555.123.4567", True, "dots"),
        ("1 555 123 4567", True, "country code 1 with spaces"),
        ("+1 555 123 4567", True, "plus 1"),
        ("555-123-4567", True, "standard hyphen format"),
        ("(555) 123 4567", True, "mixed separators"),
        ("+1(555)123-4567", True, "all packed"),
        ("555 123-4567", True, "space then hyphen"),
        ("555-123-4567 ext 123", True, "with extension"),
        ("1-555-123-4567", True, "1 prefix hyphen"),
        # Invalid formats
        ("123-4567", False, "only 7 digits"),
        ("555-12-4567", False, "wrong grouping"),
        ("55-123-4567", False, "only 2 digits first"),
        ("555-1234567", False, "wrong last group"),
        ("(555) 123-456", False, "missing digit"),
        ("(555) 1234-567", False, "wrong grouping"),
        ("555 123 456", False, "only 9 digits"),
        ("555-123-45678", False, "11 digits"),
        ("abc-123-4567", False, "letters in area code"),
        ("+2 555 123 4567", False, "wrong country code"),
        ("+1 555 123", False, "incomplete"),
        ("555-123-456a", False, "letter at end"),
        ("(555) 123-4567 ", False, "trailing space"),
        (" 555-123-4567", False, "leading space"),
        ("555-123-4567x123", False, "extension without space"),
        ("555) 123-4567", False, "missing opening paren"),
        ("(555 123-4567", False, "missing closing paren"),
    ]

    # IPV4 (30 examples: ~60% valid, ~40% invalid)
    ipv4_examples = [
        # Valid IPs
        ("0.0.0.0", True, "all zeros"),
        ("127.0.0.1", True, "localhost"),
        ("192.168.1.1", True, "private range"),
        ("10.0.0.1", True, "private 10.x"),
        ("172.16.0.1", True, "private 172.x"),
        ("255.255.255.255", True, "broadcast"),
        ("1.1.1.1", True, "cloudflare DNS"),
        ("8.8.8.8", True, "google DNS"),
        ("192.0.2.1", True, "documentation range"),
        ("203.0.113.1", True, "documentation range 2"),
        ("198.51.100.1", True, "documentation range 3"),
        ("169.254.1.1", True, "link-local"),
        ("224.0.0.1", True, "multicast"),
        ("100.64.0.1", True, "carrier-grade NAT"),
        ("200.100.50.25", True, "valid arbitrary"),
        ("10.10.10.10", True, "simple private"),
        ("99.99.99.99", True, "valid public"),
        ("111.111.111.111", True, "all same octets"),
        # Invalid IPs
        ("256.1.1.1", False, "octet > 255"),
        ("192.168.1.256", False, "last octet too large"),
        ("192.168.300.1", False, "third octet too large"),
        ("192.168.1", False, "only 3 octets"),
        ("192.168.1.1.1", False, "5 octets"),
        ("192.168.-1.1", False, "negative number"),
        ("192.168.1.1a", False, "letter at end"),
        ("a.b.c.d", False, "letters"),
        ("192 168 1 1", False, "spaces instead of dots"),
        ("192.168.1.", False, "trailing dot"),
        (".192.168.1.1", False, "leading dot"),
        ("192..168.1.1", False, "double dot"),
        ("192.168..1.1", False, "consecutive dots"),
        ("192.168.1.01", False, "leading zero"),
    ]

    # DATE_ISO (35 examples: ~60% valid, ~40% invalid)
    date_examples = [
        # Valid dates
        ("2024-01-15", True, "january"),
        ("2024-02-29", True, "leap year feb 29"),
        ("2024-03-31", True, "march 31"),
        ("2024-04-30", True, "april 30"),
        ("2024-05-31", True, "may 31"),
        ("2024-06-30", True, "june 30"),
        ("2024-07-31", True, "july 31"),
        ("2024-08-31", True, "august 31"),
        ("2024-09-30", True, "september 30"),
        ("2024-10-31", True, "october 31"),
        ("2024-11-30", True, "november 30"),
        ("2024-12-31", True, "december 31"),
        ("2000-01-01", True, "y2k"),
        ("1999-12-31", True, "before y2k"),
        ("2025-01-01", True, "next year"),
        ("2023-02-28", True, "non-leap feb"),
        ("2000-02-29", True, "leap century year"),
        ("1900-01-01", True, "old date"),
        ("2100-12-31", True, "future date"),
        ("2024-06-15", True, "mid-year mid-month"),
        ("2024-01-01", True, "new year"),
        ("2024-07-04", True, "independence day"),
        ("2024-12-25", True, "christmas"),
        ("2024-10-31", True, "halloween"),
        # Invalid dates
        ("2024-13-01", False, "month 13"),
        ("2024-00-01", False, "month 0"),
        ("2024-02-30", False, "feb 30"),
        ("2024-04-31", False, "april 31"),
        ("2024-06-31", False, "june 31"),
        ("2024-09-31", False, "sept 31"),
        ("2024-11-31", False, "nov 31"),
        ("2023-02-29", False, "non-leap year feb 29"),
        ("2024-01-32", False, "day 32"),
        ("2024-01-00", False, "day 0"),
        ("2024-1-15", False, "single digit month"),
        ("2024-01-5", False, "single digit day"),
        ("24-01-15", False, "2-digit year"),
        ("2024/01/15", False, "slashes"),
        ("01-15-2024", False, "wrong order"),
    ]

    # URL (35 examples: ~60% valid, ~40% invalid)
    url_examples = [
        # Valid URLs
        ("http://example.com", True, "http basic"),
        ("https://example.com", True, "https basic"),
        ("http://www.example.com", True, "www subdomain"),
        ("https://example.com/path", True, "with path"),
        ("https://example.com/path/to/page", True, "nested path"),
        ("https://example.com?query=value", True, "with query string"),
        ("https://example.com/path?query=value", True, "path and query"),
        ("https://example.com#fragment", True, "with fragment"),
        ("https://example.com/path?query=value#fragment", True, "all parts"),
        ("ftp://example.com/file.txt", True, "ftp protocol"),
        ("http://example.com:8080", True, "custom port"),
        ("https://user:pass@example.com", True, "with credentials"),
        ("http://192.168.1.1", True, "IP address"),
        ("http://localhost:3000", True, "localhost"),
        ("https://api.example.com/v1/users", True, "api endpoint"),
        ("https://example.com/file.pdf", True, "file extension"),
        ("https://example.co.uk/page", True, "multi-part TLD"),
        ("http://example.com/path?a=1&b=2", True, "multiple params"),
        ("https://sub.domain.example.com", True, "nested subdomain"),
        ("http://example.com/path%20with%20spaces", True, "encoded spaces"),
        # Invalid URLs
        ("example.com", False, "no protocol"),
        ("http:/example.com", False, "single slash"),
        ("http//example.com", False, "no colon"),
        ("htp://example.com", False, "typo in protocol"),
        ("http://", False, "no domain"),
        ("http://.com", False, "no domain name"),
        ("http://example", False, "no TLD"),
        ("http://example..com", False, "double dot"),
        ("http://example .com", False, "space in domain"),
        ("http://exam ple.com", False, "space in domain"),
        ("://example.com", False, "no protocol"),
        ("http:/example.com/", False, "single slash"),
        ("http:example.com", False, "no slashes"),
        ("http://example.com//path", False, "double slash in path"),
        ("http://example.com path", False, "space in path"),
    ]

    # SEMVER (25 examples: ~60% valid, ~40% invalid)
    semver_examples = [
        # Valid versions
        ("0.0.0", True, "all zeros"),
        ("1.0.0", True, "major 1"),
        ("1.2.3", True, "basic version"),
        ("10.20.30", True, "multi-digit"),
        ("1.2.3-alpha", True, "prerelease"),
        ("1.2.3-alpha.1", True, "prerelease with number"),
        ("1.2.3-beta", True, "beta prerelease"),
        ("1.2.3-rc.1", True, "rc prerelease"),
        ("1.2.3+build", True, "build metadata"),
        ("1.2.3-alpha+build", True, "prerelease and build"),
        ("1.2.3-0.3.7", True, "complex prerelease"),
        ("1.2.3-x.7.z.92", True, "complex prerelease 2"),
        ("2.0.0-rc.1+build.123", True, "rc with build"),
        ("0.1.0-alpha", True, "zero major with prerelease"),
        ("1.0.0-beta.1", True, "beta with number"),
        # Invalid versions
        ("1.2", False, "only 2 parts"),
        ("1", False, "only 1 part"),
        ("v1.2.3", False, "v prefix"),
        ("1.2.3.4", True, "4 parts (actually valid in some contexts, mark as edge)"),
        ("1.2.3-", False, "dash but no prerelease"),
        ("1.2.3+", False, "plus but no build"),
        ("01.2.3", False, "leading zero"),
        ("1.02.3", False, "leading zero in minor"),
        ("1.2.03", False, "leading zero in patch"),
        ("1.2.3-alpha-", False, "trailing dash"),
    ]

    all_examples = [
        ("email", email_examples),
        ("phone_us", phone_examples),
        ("ipv4", ipv4_examples),
        ("date_iso", date_examples),
        ("url", url_examples),
        ("semver", semver_examples),
    ]

    for pattern_type, examples in all_examples:
        for input_string, expected_match, description in examples:
            validation_set.append({
                "test_id": test_id,
                "input_string": input_string,
                "pattern_type": pattern_type,
                "expected_match": expected_match,
                "description": description,
            })
            test_id += 1

    # Shuffle to mix pattern types
    random.shuffle(validation_set)

    return validation_set


def main():
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "generate":
        validation_set = generate_validation_set()
        output_path = Path(__file__).parent / "validation_set.json"
        with open(output_path, "w") as f:
            json.dump(validation_set, f, indent=2)
        print(f"Generated validation_set.json with {len(validation_set)} test cases")

        # Print summary
        summary = {}
        for test in validation_set:
            ptype = test["pattern_type"]
            summary[ptype] = summary.get(ptype, 0) + 1
        print("Summary by pattern type:")
        for ptype in sorted(summary.keys()):
            print(f"  {ptype}: {summary[ptype]}")
    else:
        print("Usage: python prepare.py generate")


if __name__ == "__main__":
    main()
