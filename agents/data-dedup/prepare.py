"""Generate records.json — 300 records with realistic duplicates.

Usage: python prepare.py generate
"""

import json
import random
import sys

SEED = 42


def generate_dataset():
    """Generate 300 records: 100 unique entities + ~200 realistic duplicates."""
    random.seed(SEED)

    # Base entity data (100 unique people)
    first_names = [
        "John", "Mary", "Robert", "Patricia", "Michael", "Jennifer", "William", "Linda",
        "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah",
        "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Elizabeth", "Matthew", "Lisa",
        "Anthony", "Betty", "Mark", "Margaret", "Donald", "Sandra", "Steven", "Ashley",
        "Paul", "Kimberly", "Andrew", "Donna", "Joshua", "Michelle", "Kenneth", "Emily",
        "Kevin", "Dorothy", "Brian", "Melissa", "George", "Deborah", "Edward", "Stephanie",
        "Ronald", "Rebecca", "Timothy", "Sharon", "Jason", "Laura", "Jeffrey", "Cynthia",
        "Ryan", "Kathleen", "Jacob", "Amy", "Gary", "Angela", "Nicholas", "Shirley",
        "Eric", "Anna", "Jonathan", "Brenda", "Stephen", "Pamela", "Larry", "Nicole",
        "Justin", "Emma", "Scott", "Helen", "Brandon", "Samantha", "Benjamin", "Katherine",
        "Samuel", "Christine", "Frank", "Debra", "Gregory", "Rachel", "Raymond", "Catherine",
        "Patrick", "Carolyn", "Jack", "Janet", "Dennis", "Ruth", "Jerry", "Maria",
        "Tyler", "Heather", "Aaron", "Diane", "Jose", "Virginia", "Adam", "Julie",
        "Henry", "Joyce", "Douglas", "Victoria", "Zachary", "Olivia", "Peter", "Kelly",
        "Kyle", "Christina", "Walter", "Lauren"
    ]

    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
        "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
        "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Young",
        "Stroh", "King", "Wright", "Lopez", "Hill", "Scott", "Green", "Adams",
        "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts",
        "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker", "Edwards", "Collins",
        "Reyes", "Stewart", "Morris", "Morales", "Rojas", "Gutierrez", "Ortiz", "Jimenez",
        "Blake", "Graham", "Ruiz", "Medina", "Sandoval", "Herrera", "Alvarado", "Cruz",
        "Montes", "Castro", "Vargas", "Ramos", "Vazquez", "Chavez", "Salazar", "Calderon",
        "Erickson", "Larson", "Olson", "Erson", "Peterson", "Bergstrom", "Swanson",
        "Klein", "Schmidt", "Mueller", "Wagner", "Schultz", "Schroeder", "Fischer",
        "Hoffman", "Bauer", "Schneider", "Keller", "Hellman", "Newman", "Goldman",
        "Freedman", "Kaufman", "Feldman", "Silverman", "Goodman", "Rothman", "Wasser"
    ]

    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia",
              "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville",
              "Seattle", "Denver", "Washington", "Boston", "Miami", "Atlanta"]

    companies = [
        "Acme Corp", "TechVentures Inc", "Global Solutions LLC", "Innovation Labs",
        "Digital Dynamics", "Future Systems", "CloudNet Inc", "DataFlow LLC",
        "NetTech Corp", "SoftWare Plus", "SmartTech Solutions", "FirstData Inc",
        "BestSoft LLC", "NextGen Systems", "Apex Corp", "QuantumLeap Inc"
    ]

    # Generate 100 unique base entities
    base_entities = []
    for i in range(100):
        first = random.choice(first_names)
        last = random.choice(last_names)
        base_entities.append({
            "first_name": first,
            "last_name": last,
            "email": f"{first.lower()}.{last.lower()}@company.com",
            "phone": f"+1-{random.randint(200,999)}-{random.randint(200,999)}-{random.randint(1000,9999)}",
            "company": random.choice(companies),
            "city": random.choice(cities)
        })

    # Variation functions for realistic duplicates
    def first_name_variations(name):
        """Generate common first name variations."""
        variations = {
            "Robert": ["Bob", "Rob", "Roberto", "Robbie"],
            "Michael": ["Mike", "Mikey", "Mikhail"],
            "William": ["Bill", "Will", "Liam"],
            "Christopher": ["Chris", "Christoph"],
            "Jonathan": ["Jon", "John", "Johnny"],
            "Elizabeth": ["Liz", "Beth", "Lizzy"],
            "Margaret": ["Marge", "Maggie", "Meg"],
            "Jennifer": ["Jen", "Jenny"],
            "Patricia": ["Pat", "Patti", "Patrice"],
            "William": ["Bill", "Liam", "Will"],
        }
        return variations.get(name, [])

    def last_name_variations(name):
        """Generate common last name variations."""
        return [name.replace(".", ""), name.replace(".", " "), name.upper(), name.lower()]

    def email_variations(email):
        """Generate email variations."""
        base = email.split("@")[0]
        return [
            email.replace("@company.com", "@gmail.com"),
            email.replace("@company.com", "@yahoo.com"),
            email.replace("@company.com", "@outlook.com"),
            base.replace(".", "") + "@company.com",
            base.replace(".", "_") + "@company.com",
        ]

    def phone_variations(phone):
        """Vary or remove phone."""
        return [None, phone, phone.replace("-", ""), phone.replace("-", " ")]

    def company_variations(company):
        """Generate company name variations."""
        variations = {
            "Inc": ["LLC", "Corp", "Incorporated", "Ltd"],
            "LLC": ["Inc", "Corp", "L.L.C."],
            "Corp": ["Corporation", "Inc", "LLC"],
        }
        for key, vals in variations.items():
            if key in company:
                return [company.replace(key, v) for v in vals] + [company]
        return [company]

    # Build records and golden clusters
    records = []
    golden_clusters = {}
    record_id_counter = 0

    for cluster_id, base_entity in enumerate(base_entities):
        # Add base record
        record = {
            "record_id": f"R{record_id_counter:04d}",
            "first_name": base_entity["first_name"],
            "last_name": base_entity["last_name"],
            "email": base_entity["email"],
            "phone": base_entity["phone"],
            "company": base_entity["company"],
            "city": base_entity["city"],
        }
        records.append(record)
        cluster_members = [record["record_id"]]
        record_id_counter += 1

        # Add 1-5 realistic duplicates per base entity
        num_duplicates = random.randint(1, 5)
        for dup_idx in range(num_duplicates):
            dup = record.copy()
            dup["record_id"] = f"R{record_id_counter:04d}"
            record_id_counter += 1

            # Apply realistic variations
            variation_type = random.choice([
                "name_typo",
                "name_variation",
                "email_variation",
                "missing_field",
                "swapped_names",
                "company_variation",
                "phone_variation",
                "multiple_variations"
            ])

            if variation_type == "name_typo":
                # Introduce typo in name
                if random.random() < 0.5:
                    name = dup["first_name"]
                    if len(name) > 2:
                        idx = random.randint(0, len(name) - 1)
                        name = name[:idx] + random.choice("abcdefghijklmnopqrstuvwxyz") + name[idx+1:]
                    dup["first_name"] = name
                else:
                    name = dup["last_name"]
                    if len(name) > 2:
                        idx = random.randint(0, len(name) - 1)
                        name = name[:idx] + random.choice("abcdefghijklmnopqrstuvwxyz") + name[idx+1:]
                    dup["last_name"] = name

            elif variation_type == "name_variation":
                # Use common name variation (Bob for Robert, etc.)
                alts = first_name_variations(dup["first_name"])
                if alts:
                    dup["first_name"] = random.choice(alts)

            elif variation_type == "email_variation":
                # Vary the email
                alts = email_variations(dup["email"])
                dup["email"] = random.choice(alts)

            elif variation_type == "missing_field":
                # Remove or blank out a field
                blank_field = random.choice(["phone", "email"])
                if blank_field == "phone":
                    dup["phone"] = None
                else:
                    dup["email"] = ""

            elif variation_type == "swapped_names":
                # Swap first and last name
                dup["first_name"], dup["last_name"] = dup["last_name"], dup["first_name"]

            elif variation_type == "company_variation":
                # Vary company name (e.g., Inc vs LLC)
                alts = company_variations(dup["company"])
                dup["company"] = random.choice(alts)

            elif variation_type == "phone_variation":
                # Vary phone format
                alts = phone_variations(dup["phone"])
                dup["phone"] = random.choice(alts)

            elif variation_type == "multiple_variations":
                # Combine 2-3 variations
                if random.random() < 0.5:
                    alts = first_name_variations(dup["first_name"])
                    if alts:
                        dup["first_name"] = random.choice(alts)
                if random.random() < 0.5:
                    alts = email_variations(dup["email"])
                    dup["email"] = random.choice(alts)
                if random.random() < 0.5:
                    dup["phone"] = None

            # Add to records and cluster
            records.append(dup)
            cluster_members.append(dup["record_id"])

        golden_clusters[f"C{cluster_id:03d}"] = cluster_members

    return records, golden_clusters


def save_dataset(records, golden_clusters):
    """Save records and golden_clusters to records.json."""
    data = {
        "records": records,
        "golden_clusters": golden_clusters
    }
    with open("records.json", "w") as f:
        json.dump(data, f, indent=2)
    print(f"Generated {len(records)} records with {len(golden_clusters)} true clusters")
    print(f"Sample record: {records[0]}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "generate":
        records, golden_clusters = generate_dataset()
        save_dataset(records, golden_clusters)
    else:
        print("Usage: python prepare.py generate")
