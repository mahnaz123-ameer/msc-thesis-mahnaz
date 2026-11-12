# =============================================================
# seller.py — Seller Management and Commission
# E-Commerce System
# =============================================================


def register_seller(sellers, seller_id, name, shop_name, category, phone, email):
    """Register a new seller on the platform."""
    if seller_id in sellers:
        return False, "Seller ID already exists"
    if "@" not in email:
        return False, "Invalid email"
    sellers[seller_id] = {
        "name": name, "shop_name": shop_name, "category": category,
        "phone": phone, "email": email, "active": True,
        "verified": False, "rating": [], "total_sales": 0,
        "total_revenue": 0, "pending_payout": 0,
    }
    return True, "Seller registered"


def verify_seller(sellers, seller_id):
    """Mark a seller as verified."""
    if seller_id not in sellers:
        return False, "Seller not found"
    sellers[seller_id]["verified"] = True
    return True, "Seller verified"


def calculate_commission(sale_amount, category):
    """Calculate platform commission based on product category."""
    commission_rates = {
        "electronics": 8, "clothing": 12, "food": 5,
        "beauty": 15, "books": 10, "home": 10,
        "sports": 12, "default": 10,
    }
    rate = commission_rates.get(category.lower(), commission_rates["default"])
    return round(sale_amount * (rate / 100), 2)


def calculate_seller_payout(sale_amount, category, shipping_subsidy=0):
    """Calculate seller payout after commission and fees."""
    commission = calculate_commission(sale_amount, category)
    payout = sale_amount - commission - shipping_subsidy
    return round(max(0, payout), 2)


def add_sale(sellers, seller_id, sale_amount, category):
    """Record a sale for a seller."""
    if seller_id not in sellers:
        return False, "Seller not found"
    payout = calculate_seller_payout(sale_amount, category)
    sellers[seller_id]["total_sales"] += 1
    sellers[seller_id]["total_revenue"] += sale_amount
    sellers[seller_id]["pending_payout"] += payout
    return True, f"Sale recorded. Payout: {payout}"


def process_payout(sellers, seller_id):
    """Process pending payout for a seller."""
    if seller_id not in sellers:
        return False, "Seller not found"
    amount = sellers[seller_id]["pending_payout"]
    if amount <= 0:
        return False, "No pending payout"
    sellers[seller_id]["pending_payout"] = 0
    return True, f"Payout of {amount} processed"


def add_seller_rating(sellers, seller_id, rating):
    """Add customer rating for a seller."""
    if seller_id not in sellers:
        return False, "Seller not found"
    if rating < 1 or rating > 5:
        return False, "Rating must be 1-5"
    sellers[seller_id]["rating"].append(rating)
    return True, "Rating added"


def get_seller_rating(sellers, seller_id):
    """Get average seller rating."""
    if seller_id not in sellers:
        return None
    ratings = sellers[seller_id]["rating"]
    if not ratings:
        return 0.0
    return round(sum(ratings) / len(ratings), 2)


def calculate_seller_performance_score(sellers, seller_id):
    """Calculate overall seller performance score (0-100)."""
    if seller_id not in sellers:
        return None
    rating = get_seller_rating(sellers, seller_id) or 0
    sales = min(sellers[seller_id]["total_sales"], 1000)
    rating_score = (rating / 5) * 60
    sales_score = (sales / 1000) * 40
    return round(rating_score + sales_score, 2)


def suspend_seller(sellers, seller_id, reason):
    """Suspend a seller account."""
    if seller_id not in sellers:
        return False, "Seller not found"
    sellers[seller_id]["active"] = False
    sellers[seller_id]["suspension_reason"] = reason
    return True, "Seller suspended"


def reinstate_seller(sellers, seller_id):
    """Reinstate a suspended seller."""
    if seller_id not in sellers:
        return False, "Seller not found"
    sellers[seller_id]["active"] = True
    return True, "Seller reinstated"


def get_top_sellers(sellers, top_n=10):
    """Get top N sellers by total revenue."""
    active = [(sid, info["total_revenue"]) for sid, info in sellers.items() if info["active"]]
    return sorted(active, key=lambda x: x[1], reverse=True)[:top_n]


def get_verified_sellers(sellers):
    """Get all verified sellers."""
    return {sid: info for sid, info in sellers.items() if info["verified"] and info["active"]}


def calculate_total_commission_earned(sellers, sales_records, category):
    """Calculate total platform commission from all sellers in a category."""
    total = 0
    for sale_amount in sales_records:
        total += calculate_commission(sale_amount, category)
    return round(total, 2)
