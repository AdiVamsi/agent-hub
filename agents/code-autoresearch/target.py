"""Product Catalog API — the ONE file the agent modifies.

A deliberately slow Python module simulating a real API's business logic.
The agent experiments with this file to maximize requests_per_second.

Contains intentional performance problems that an optimization agent can
find and fix. All function signatures and return values must stay the same —
the harness verifies correctness after every change.
"""

import copy
import hashlib
import random
import string
import time

# Module-level caches keyed by id(list) to avoid rebuilding per call
_product_search_cache = {}  # id(products) -> list of (product, full_str, name, desc)
_reviews_index_cache = {}   # id(reviews) -> dict of product_id -> [ratings sum, count]
_product_index_cache = {}   # id(products) -> dict of product_id -> product


# ---------------------------------------------------------------------------
# Data generation (deterministic — do not modify seed behavior)
# ---------------------------------------------------------------------------

CATEGORIES = [
    "Electronics", "Books", "Clothing", "Home & Kitchen", "Sports",
    "Toys", "Health", "Automotive", "Garden", "Music",
    "Office", "Pet Supplies", "Food", "Beauty", "Tools",
]

ADJECTIVES = [
    "Premium", "Professional", "Deluxe", "Ultra", "Classic",
    "Modern", "Essential", "Advanced", "Original", "Elite",
    "Compact", "Portable", "Heavy-Duty", "Lightweight", "Smart",
]

NOUNS = [
    "Widget", "Gadget", "Device", "Tool", "Kit",
    "System", "Pack", "Set", "Bundle", "Station",
    "Hub", "Pro", "Max", "Lite", "Plus",
]


def generate_sample_data():
    """Generate deterministic sample data for benchmarking.

    Returns:
        dict with keys: products, reviews, orders, users
    """
    rng = random.Random(42)

    # --- Products: 1000 ---
    products = []
    for i in range(1000):
        adj = rng.choice(ADJECTIVES)
        noun = rng.choice(NOUNS)
        cat = rng.choice(CATEGORIES)
        price = round(rng.uniform(5.0, 500.0), 2)
        tags = rng.sample(
            ["sale", "new", "popular", "limited", "exclusive",
             "bestseller", "eco", "premium", "budget", "trending"],
            k=rng.randint(1, 4),
        )
        products.append({
            "id": i,
            "name": f"{adj} {noun} {i}",
            "category": cat,
            "price": price,
            "description": f"A high-quality {cat.lower()} product. "
                           f"The {adj.lower()} {noun.lower()} delivers "
                           f"outstanding performance and reliability. "
                           f"Perfect for everyday use. Model #{i}.",
            "tags": tags,
            "rating_cache": None,  # intentionally unused
        })

    # --- Reviews: 5000 ---
    reviews = []
    for i in range(5000):
        product_id = rng.randint(0, 999)
        rating = rng.randint(1, 5)
        words = rng.randint(5, 30)
        text_parts = []
        for _ in range(words):
            word_len = rng.randint(3, 10)
            text_parts.append(
                "".join(rng.choices(string.ascii_lowercase, k=word_len))
            )
        reviews.append({
            "id": i,
            "product_id": product_id,
            "rating": rating,
            "text": " ".join(text_parts),
            "helpful_votes": rng.randint(0, 50),
        })

    # --- Orders: 500 ---
    orders = []
    months = ["2025-01", "2025-02", "2025-03", "2025-04", "2025-05", "2025-06",
              "2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2025-12"]
    for i in range(500):
        num_items = rng.randint(1, 8)
        items = []
        for _ in range(num_items):
            pid = rng.randint(0, 999)
            qty = rng.randint(1, 5)
            items.append({"product_id": pid, "quantity": qty})
        orders.append({
            "id": i,
            "items": items,
            "date": f"{rng.choice(months)}-{rng.randint(1,28):02d}",
            "customer_id": rng.randint(0, 199),
            "status": rng.choice(["completed", "shipped", "processing"]),
        })

    # --- Users: 200 ---
    users = []
    for i in range(200):
        num_purchases = rng.randint(3, 20)
        history = [rng.randint(0, 999) for _ in range(num_purchases)]
        users.append({
            "id": i,
            "purchase_history": history,
            "preferred_categories": rng.sample(CATEGORIES, k=rng.randint(1, 4)),
        })

    return {
        "products": products,
        "reviews": reviews,
        "orders": orders,
        "users": users,
    }


# ---------------------------------------------------------------------------
# API Functions — these have INTENTIONAL performance problems
# ---------------------------------------------------------------------------


def search_products(query: str, products: list) -> list:
    """Search products by query string. Returns top 10 matches.

    INTENTIONAL PROBLEMS:
    - Nested O(n²) loop: iterates every product for every query word
    - Converts product to str() for matching instead of checking fields
    - Bubble sort for ranking instead of sorted()
    """
    query_words = query.lower().split()
    scored = []

    # Use cached search strings (rebuilt only when products list identity changes)
    cache_key = id(products)
    if cache_key not in _product_search_cache:
        search_strings = []
        for product in products:
            name_lower = product["name"].lower()
            desc_lower = product["description"].lower()
            cat_lower = product["category"].lower()
            tags_lower = " ".join(product["tags"]).lower()
            full_str = (name_lower + " " + desc_lower + " " + cat_lower + " " + tags_lower)
            search_strings.append((product, full_str, name_lower, desc_lower))
        _product_search_cache[cache_key] = search_strings
    product_search_strings = _product_search_cache[cache_key]

    for product, product_str, name_lower, desc_lower in product_search_strings:
        score = 0
        for word in query_words:
            if word in product_str:
                score += 1
            if word in name_lower:
                score += 2
            if word in desc_lower:
                score += 1
        if score > 0:
            scored.append({"product": product, "score": score})

    # Use sorted() instead of bubble sort
    scored.sort(key=lambda x: x["score"], reverse=True)

    # Return top 10
    return [item["product"] for item in scored[:10]]


def get_product_with_reviews(product_id: int, products: list,
                              reviews: list) -> dict:
    """Get a product with its reviews and average rating.

    INTENTIONAL PROBLEMS:
    - Linear scan to find product instead of dict lookup
    - N+1 pattern: scans ALL reviews to find matching ones
    - Computes average by iterating twice (sum + count separately)
    - Deep copies the product unnecessarily
    """
    # SLOW: linear scan for product
    product = None
    for p in products:
        if p["id"] == product_id:
            product = p
            break

    if product is None:
        return {"product": None, "reviews": [], "avg_rating": 0.0}

    # Shallow copy instead of expensive deep copy
    result_product = dict(product)

    # Single pass: collect reviews and accumulate rating sum together
    product_reviews = []
    total_rating = 0
    for review in reviews:
        if review["product_id"] == product_id:
            product_reviews.append(review)
            total_rating += review["rating"]

    review_count = len(product_reviews)
    avg_rating = total_rating / review_count if review_count > 0 else 0.0

    return {
        "product": result_product,
        "reviews": product_reviews,
        "avg_rating": round(avg_rating, 2),
    }


def generate_recommendations(user_history: list, products: list,
                              reviews: list) -> list:
    """Generate product recommendations based on purchase history.

    INTENTIONAL PROBLEMS:
    - Recomputes average ratings for ALL products from scratch every call
    - Sorts ALL products even though only top 5 are needed
    - String concatenation in loop for category building
    """
    # Use cached reviews index (rebuilt only when reviews list identity changes)
    rev_cache_key = id(reviews)
    if rev_cache_key not in _reviews_index_cache:
        review_totals = {}
        for review in reviews:
            pid = review["product_id"]
            if pid not in review_totals:
                review_totals[pid] = [0, 0]
            review_totals[pid][0] += review["rating"]
            review_totals[pid][1] += 1
        _reviews_index_cache[rev_cache_key] = review_totals
    review_totals = _reviews_index_cache[rev_cache_key]

    # Compute average ratings from index
    product_ratings = {pid: round(total / count, 2)
                       for pid, (total, count) in review_totals.items()}

    # Use cached product index
    prod_cache_key = id(products)
    if prod_cache_key not in _product_index_cache:
        _product_index_cache[prod_cache_key] = {p["id"]: p for p in products}
    product_index = _product_index_cache[prod_cache_key]

    history_set = set(user_history)
    user_cat_set = {product_index[pid]["category"]
                   for pid in history_set if pid in product_index}

    # Score products
    scored = []
    for product in products:
        if product["id"] in history_set:
            continue  # skip already purchased
        score = 0.0
        # Category match bonus
        if product["category"] in user_cat_set:
            score += 3.0
        # Rating bonus
        score += product_ratings.get(product["id"], 0.0)
        # Price bonus (prefer mid-range)
        if 20 <= product["price"] <= 200:
            score += 1.0
        scored.append({"product": product, "score": round(score, 2)})

    # Use sorted() and only get top 5
    scored.sort(key=lambda x: x["score"], reverse=True)

    return [item["product"] for item in scored[:5]]


def generate_invoice(order_items: list, products: list,
                      tax_rate: float) -> dict:
    """Generate an invoice from order items.

    INTENTIONAL PROBLEMS:
    - Linear scan to find each product (O(n) per item)
    - String concatenation with += in loop
    - Recalculates subtotal multiple times
    """
    # Build product dict index for O(1) lookups
    product_index = {p["id"]: p for p in products}

    lines = []
    # Use list for building invoice text, join at end
    invoice_parts = ["=" * 50 + "\n", "INVOICE\n", "=" * 50 + "\n"]

    subtotal = 0.0
    for item in order_items:
        product = product_index.get(item["product_id"])
        if product is None:
            continue

        qty = item["quantity"]
        line_total = product["price"] * qty
        subtotal += line_total

        lines.append({
            "product_id": product["id"],
            "name": product["name"],
            "quantity": qty,
            "unit_price": product["price"],
            "line_total": round(line_total, 2),
        })

        invoice_parts.append(
            f"  {product['name'][:30]:30s} x{qty:2d}  ${line_total:8.2f}\n"
        )

    subtotal = round(subtotal, 2)
    tax = round(subtotal * tax_rate, 2)
    total = round(subtotal + tax, 2)

    invoice_parts.append("-" * 50 + "\n")
    invoice_parts.append(f"  {'Subtotal':30s}        ${subtotal:8.2f}\n")
    invoice_parts.append(f"  {'Tax (' + str(int(tax_rate*100)) + '%)':30s}        ${tax:8.2f}\n")
    invoice_parts.append(f"  {'TOTAL':30s}        ${total:8.2f}\n")
    invoice_parts.append("=" * 50 + "\n")
    invoice_text = "".join(invoice_parts)

    return {
        "lines": lines,
        "subtotal": round(subtotal, 2),
        "tax": tax,
        "total": total,
        "invoice_text": invoice_text,
    }


def analyze_sales(orders: list, products: list) -> dict:
    """Analyze sales data — categories, revenue, trends.

    INTENTIONAL PROBLEMS:
    - Nested loops to group by category
    - Recomputes total revenue in multiple passes
    - Creates intermediate lists where generators would work
    """
    # Build product dict index once for O(1) lookups
    product_index = {p["id"]: p for p in products}

    # Single pass over all orders/items to compute all needed values
    category_revenue = {}
    monthly_revenue = {}
    total_revenue_1 = 0.0
    order_totals = []

    for order in orders:
        month = order["date"][:7]  # "2025-01"
        order_total = 0.0
        for item in order["items"]:
            product = product_index.get(item["product_id"])
            if product is None:
                continue
            revenue = product["price"] * item["quantity"]
            cat = product["category"]
            category_revenue[cat] = category_revenue.get(cat, 0.0) + revenue
            total_revenue_1 += revenue
            order_total += revenue
        monthly_revenue[month] = monthly_revenue.get(month, 0.0) + order_total
        order_totals.append(order_total)

    # Top categories using sorted()
    cat_list = sorted(
        [{"category": k, "revenue": round(v, 2)} for k, v in category_revenue.items()],
        key=lambda x: x["revenue"],
        reverse=True,
    )

    # Average order value from already-computed totals
    avg_order_value = round(total_revenue_1 / len(orders), 2) if orders else 0

    # Sort monthly revenue
    sorted_months = sorted(monthly_revenue.keys())
    monthly_sorted = [{"month": m, "revenue": round(monthly_revenue[m], 2)}
                      for m in sorted_months]

    return {
        "total_revenue": round(total_revenue_1, 2),
        "top_categories": cat_list[:5],
        "monthly_revenue": monthly_sorted,
        "avg_order_value": avg_order_value,
        "total_orders": len(orders),
        "total_items_sold": sum(
            item["quantity"]
            for order in orders
            for item in order["items"]
        ),
    }


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Generating sample data...")
    data = generate_sample_data()
    print(f"  Products: {len(data['products'])}")
    print(f"  Reviews:  {len(data['reviews'])}")
    print(f"  Orders:   {len(data['orders'])}")
    print(f"  Users:    {len(data['users'])}")

    print("\nRunning self-test...")

    # Test search
    results = search_products("premium widget electronics", data["products"])
    assert len(results) <= 10, "search should return at most 10"
    assert len(results) > 0, "search should find something"
    print(f"  search_products: OK ({len(results)} results)")

    # Test product with reviews
    result = get_product_with_reviews(42, data["products"], data["reviews"])
    assert result["product"] is not None, "should find product 42"
    assert "avg_rating" in result, "should have avg_rating"
    print(f"  get_product_with_reviews: OK (rating={result['avg_rating']})")

    # Test recommendations
    user = data["users"][0]
    recs = generate_recommendations(
        user["purchase_history"], data["products"], data["reviews"]
    )
    assert len(recs) == 5, "should return 5 recommendations"
    print(f"  generate_recommendations: OK ({len(recs)} recs)")

    # Test invoice
    order = data["orders"][0]
    inv = generate_invoice(order["items"], data["products"], 0.08)
    assert inv["total"] > 0, "invoice total should be positive"
    assert "invoice_text" in inv, "should have invoice text"
    print(f"  generate_invoice: OK (total=${inv['total']})")

    # Test analytics
    analysis = analyze_sales(data["orders"], data["products"])
    assert analysis["total_revenue"] > 0, "revenue should be positive"
    assert len(analysis["top_categories"]) == 5, "should have top 5 categories"
    print(f"  analyze_sales: OK (revenue=${analysis['total_revenue']})")

    print("\nAll self-tests passed!")
