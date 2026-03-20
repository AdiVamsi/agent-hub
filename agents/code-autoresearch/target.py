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

    # O(n * m) where n=products, m=query_words — but done inefficiently
    for product in products:
        score = 0
        # SLOW: convert entire product dict to string for every comparison
        product_str = str(product).lower()
        for word in query_words:
            if word in product_str:
                score += 1
            # SLOW: also do a redundant check on name specifically
            if word in product["name"].lower():
                score += 2
            # SLOW: and description
            if word in product["description"].lower():
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

    # SLOW: deep copy the entire product dict
    result_product = copy.deepcopy(product)

    # SLOW: N+1 — scan ALL reviews to find ones for this product
    product_reviews = []
    for review in reviews:
        if review["product_id"] == product_id:
            product_reviews.append(review)

    # SLOW: compute average rating with two separate passes
    total_rating = 0
    for r in product_reviews:
        total_rating += r["rating"]
    review_count = 0
    for r in product_reviews:
        review_count += 1
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
    # Build reviews index: product_id -> (sum_ratings, count)
    review_totals = {}
    for review in reviews:
        pid = review["product_id"]
        if pid not in review_totals:
            review_totals[pid] = [0, 0]
        review_totals[pid][0] += review["rating"]
        review_totals[pid][1] += 1

    # Compute average ratings from index
    product_ratings = {}
    for pid, (total, count) in review_totals.items():
        product_ratings[pid] = round(total / count, 2)

    # Build set of categories user has bought from using list comprehension
    history_set = set(user_history)
    product_index = {p["id"]: p for p in products}
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
    lines = []
    # SLOW: build invoice text with string concatenation
    invoice_text = ""
    invoice_text += "=" * 50 + "\n"
    invoice_text += "INVOICE\n"
    invoice_text += "=" * 50 + "\n"

    subtotal = 0.0
    for item in order_items:
        # SLOW: linear scan through all products for each item
        product = None
        for p in products:
            if p["id"] == item["product_id"]:
                product = p
                break

        if product is None:
            continue

        qty = item["quantity"]
        line_total = product["price"] * qty

        # SLOW: recalculate running subtotal with explicit re-sum
        lines.append({
            "product_id": product["id"],
            "name": product["name"],
            "quantity": qty,
            "unit_price": product["price"],
            "line_total": round(line_total, 2),
        })

        # SLOW: string concatenation in loop
        invoice_text += f"  {product['name'][:30]:30s} x{qty:2d}  ${line_total:8.2f}\n"

    # SLOW: recalculate subtotal by iterating lines again
    subtotal = 0.0
    for line in lines:
        subtotal += line["line_total"]

    # SLOW: recalculate subtotal AGAIN for tax
    recalc_subtotal = 0.0
    for line in lines:
        recalc_subtotal += line["line_total"]
    tax = round(recalc_subtotal * tax_rate, 2)
    total = round(recalc_subtotal + tax, 2)

    invoice_text += "-" * 50 + "\n"
    invoice_text += f"  {'Subtotal':30s}        ${subtotal:8.2f}\n"
    invoice_text += f"  {'Tax (' + str(int(tax_rate*100)) + '%)':30s}        ${tax:8.2f}\n"
    invoice_text += f"  {'TOTAL':30s}        ${total:8.2f}\n"
    invoice_text += "=" * 50 + "\n"

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
    # Build product lookup (but do it SLOWLY — iterate list each time)
    # SLOW: nested loop to compute revenue by category
    category_revenue = {}
    for order in orders:
        for item in order["items"]:
            # SLOW: linear scan for product
            product = None
            for p in products:
                if p["id"] == item["product_id"]:
                    product = p
                    break
            if product is None:
                continue
            cat = product["category"]
            revenue = product["price"] * item["quantity"]
            if cat not in category_revenue:
                category_revenue[cat] = 0.0
            category_revenue[cat] += revenue

    # SLOW: compute total revenue by summing category_revenue values
    # then recompute by iterating orders again
    total_revenue_1 = 0.0
    for cat_val in category_revenue.values():
        total_revenue_1 += cat_val

    # SLOW: recompute total from scratch for "verification"
    total_revenue_2 = 0.0
    all_line_revenues = []  # SLOW: materializes entire list
    for order in orders:
        for item in order["items"]:
            for p in products:
                if p["id"] == item["product_id"]:
                    rev = p["price"] * item["quantity"]
                    all_line_revenues.append(rev)
                    total_revenue_2 += rev
                    break

    # Monthly revenue
    monthly_revenue = {}
    for order in orders:
        month = order["date"][:7]  # "2025-01"
        order_total = 0.0
        for item in order["items"]:
            # SLOW: yet another linear scan per item
            for p in products:
                if p["id"] == item["product_id"]:
                    order_total += p["price"] * item["quantity"]
                    break
        if month not in monthly_revenue:
            monthly_revenue[month] = 0.0
        monthly_revenue[month] += order_total

    # Top categories
    # SLOW: sort using bubble sort
    cat_list = [{"category": k, "revenue": round(v, 2)}
                for k, v in category_revenue.items()]
    for i in range(len(cat_list)):
        for j in range(len(cat_list) - 1 - i):
            if cat_list[j]["revenue"] < cat_list[j + 1]["revenue"]:
                cat_list[j], cat_list[j + 1] = cat_list[j + 1], cat_list[j]

    # Average order value
    # SLOW: recompute total yet again
    total_for_avg = 0.0
    for order in orders:
        for item in order["items"]:
            for p in products:
                if p["id"] == item["product_id"]:
                    total_for_avg += p["price"] * item["quantity"]
                    break
    avg_order_value = round(total_for_avg / len(orders), 2) if orders else 0

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
