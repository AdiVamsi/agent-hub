"""Data Dedup — editable file.

Available data: records.json with 300 records, each having:
  record_id, first_name, last_name, email, phone, company, city

golden_clusters: ground truth groupings (100 clusters)

Your job: implement find_duplicates(records) returning a list of clusters,
where each cluster is a list of record_ids that represent the same entity.

The harness calculates:
  - precision: fraction of predicted duplicate pairs that are true duplicates
  - recall: fraction of true duplicate pairs that were found
  - f1_score: harmonic mean of precision and recall

Metric: f1_score — HIGHER is better.
Baseline: return each record as its own cluster (no dedup = 0 recall, undefined precision -> f1=0).
"""


def find_duplicates(records: list[dict]) -> list[list[str]]:
    """Return list of clusters using union-find with multiple matching signals.

    Signals (in order of reliability):
    1. Same email username (part before @) — handles domain variation
    2. Same normalized phone (digits only) — handles formatting variation
    3. Same normalized full name + company — handles email/phone missing
    """
    # Union-Find
    parent = {r["record_id"]: r["record_id"] for r in records}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py

    def edit_distance(a, b):
        if a == b:
            return 0
        if abs(len(a) - len(b)) > 2:
            return 99
        m, n = len(a), len(b)
        dp = list(range(n + 1))
        for i in range(1, m + 1):
            ndp = [i] + [0] * n
            for j in range(1, n + 1):
                if a[i-1] == b[j-1]:
                    ndp[j] = dp[j-1]
                else:
                    ndp[j] = 1 + min(dp[j], ndp[j-1], dp[j-1])
            dp = ndp
        return dp[n]

    # Extract normalized keys
    def email_username(email):
        if not email:
            return None
        local = email.split("@")[0].lower()
        # Normalize separators
        return local.replace("_", ".").replace("-", ".")

    def normalize_phone(phone):
        if not phone:
            return None
        digits = "".join(c for c in phone if c.isdigit())
        if len(digits) < 7:
            return None
        return digits[-10:]  # last 10 digits

    def normalize_name(first, last):
        return (first or "").lower().strip(), (last or "").lower().strip()

    # Build index by email username
    email_index = {}
    phone_index = {}
    for r in records:
        rid = r["record_id"]
        eu = email_username(r.get("email"))
        if eu:
            email_index.setdefault(eu, []).append(rid)
        np = normalize_phone(r.get("phone"))
        if np:
            phone_index.setdefault(np, []).append(rid)

    # Union by email username
    for rids in email_index.values():
        for i in range(1, len(rids)):
            union(rids[0], rids[i])

    # Union by phone
    for rids in phone_index.values():
        for i in range(1, len(rids)):
            union(rids[0], rids[i])

    # Union by fuzzy name + company (for records not yet linked by email/phone)
    # Build name+company groups
    name_company_index = {}
    for r in records:
        fn, ln = normalize_name(r.get("first_name"), r.get("last_name"))
        # Handle swapped first/last
        company = (r.get("company") or "").lower().strip()
        city = (r.get("city") or "").lower().strip()
        # Key: canonical (sorted) name pair + company
        name_set = tuple(sorted([fn, ln]))
        key = (name_set, company)
        name_company_index.setdefault(key, []).append(r["record_id"])

    for rids in name_company_index.values():
        if len(rids) > 1:
            for i in range(1, len(rids)):
                union(rids[0], rids[i])

    # Fuzzy name matching: edit distance <= 1 on either first or last name, same company
    # Group by company first to limit comparisons
    company_groups = {}
    for r in records:
        company = (r.get("company") or "").lower().strip()
        company_groups.setdefault(company, []).append(r)

    for company, grp in company_groups.items():
        for i in range(len(grp)):
            for j in range(i + 1, len(grp)):
                ri, rj = grp[i], grp[j]
                # Skip if already in same cluster
                if find(ri["record_id"]) == find(rj["record_id"]):
                    continue
                fni, lni = normalize_name(ri.get("first_name"), ri.get("last_name"))
                fnj, lnj = normalize_name(rj.get("first_name"), rj.get("last_name"))
                # Match: edit distance <= 1 on first AND <= 1 on last (or swapped)
                d1 = edit_distance(fni, fnj) + edit_distance(lni, lnj)
                d2 = edit_distance(fni, lnj) + edit_distance(lni, fnj)  # swapped
                if min(d1, d2) <= 2:
                    union(ri["record_id"], rj["record_id"])

    # Collect clusters
    clusters = {}
    for r in records:
        root = find(r["record_id"])
        clusters.setdefault(root, []).append(r["record_id"])

    return list(clusters.values())
