# =============================================================
# product.py — Product Catalog and Pricing
# E-Commerce System (Daraz / Chaldal style)
# =============================================================


def add_product(products, product_id, name, category, price, stock, seller_id):
    """Add a product to the catalog."""
    if product_id in products:
        return False, "Product already exists"
    if price <= 0:
        return False, "Price must be positive"
    if stock < 0:
        return False, "Stock cannot be negative"
    products[product_id] = {
        "name": name, "category": category, "price": price,
        "original_price": price, "stock": stock, "seller_id": seller_id,
        "active": True, "ratings": [], "sold_count": 0,
    }
    return True, "Product added"


def remove_product(products, product_id):
    """Remove a product from catalog."""
    if product_id not in products:
        return False, "Product not found"
    del products[product_id]
    return True, "Product removed"


def update_price(products, product_id, new_price):
    """Update product price."""
    if product_id not in products:
        return False, "Product not found"
    if new_price <= 0:
        return False, "Price must be positive"
    products[product_id]["price"] = new_price
    return True, "Price updated"


def apply_discount(products, product_id, discount_percent):
    """Apply percentage discount to a product."""
    if product_id not in products:
        return False, "Product not found"
    if discount_percent < 0 or discount_percent > 90:
        return False, "Discount must be between 0 and 90%"
    original = products[product_id]["original_price"]
    discounted = original * (1 - discount_percent / 100)
    products[product_id]["price"] = round(discounted, 2)
    return True, f"Discount applied. New price: {products[product_id]['price']}"


def add_rating(products, product_id, rating, review=""):
    """Add customer rating to a product."""
    if product_id not in products:
        return False, "Product not found"
    if rating < 1 or rating > 5:
        return False, "Rating must be 1-5"
    products[product_id]["ratings"].append(rating)
    return True, "Rating added"


def get_average_rating(products, product_id):
    """Get average rating for a product."""
    if product_id not in products:
        return None
    ratings = products[product_id]["ratings"]
    if not ratings:
        return 0.0
    return round(sum(ratings) / len(ratings), 2)


def search_products(products, keyword):
    """Search products by keyword in name."""
    keyword = keyword.lower()
    return {pid: p for pid, p in products.items()
            if keyword in p["name"].lower() and p["active"]}


def get_products_by_category(products, category):
    """Get all active products in a category."""
    return {pid: p for pid, p in products.items()
            if p["category"].lower() == category.lower() and p["active"]}


def get_products_by_price_range(products, min_price, max_price):
    """Get products within a price range."""
    if min_price > max_price:
        return {}
    return {pid: p for pid, p in products.items()
            if min_price <= p["price"] <= max_price and p["active"]}


def is_in_stock(products, product_id):
    """Check if product is in stock."""
    if product_id not in products:
        return False
    return products[product_id]["stock"] > 0


def update_stock(products, product_id, quantity_change):
    """Update product stock (add or subtract)."""
    if product_id not in products:
        return False, "Product not found"
    new_stock = products[product_id]["stock"] + quantity_change
    if new_stock < 0:
        return False, "Insufficient stock"
    products[product_id]["stock"] = new_stock
    return True, f"Stock updated to {new_stock}"


def get_low_stock_products(products, threshold=10):
    """Get products with stock below threshold."""
    return {pid: p for pid, p in products.items() if p["stock"] <= threshold}


def calculate_discount_percentage(original_price, current_price):
    """Calculate discount percentage between original and current price."""
    if original_price <= 0:
        return None
    if current_price > original_price:
        return 0
    return round(((original_price - current_price) / original_price) * 100, 2)


def get_top_rated_products(products, top_n=10):
    """Get top N products by rating."""
    rated = [(pid, get_average_rating(products, pid)) for pid in products if products[pid]["active"]]
    return sorted(rated, key=lambda x: x[1] or 0, reverse=True)[:top_n]


def get_best_selling_products(products, top_n=10):
    """Get top N products by sales count."""
    active = [(pid, p["sold_count"]) for pid, p in products.items() if p["active"]]
    return sorted(active, key=lambda x: x[1], reverse=True)[:top_n]


def deactivate_product(products, product_id):
    """Deactivate a product (hide from catalog)."""
    if product_id not in products:
        return False, "Product not found"
    products[product_id]["active"] = False
    return True, "Product deactivated"


def calculate_seller_revenue(products, seller_id):
    """Calculate total revenue for a seller."""
    total = 0
    for p in products.values():
        if p["seller_id"] == seller_id:
            total += p["price"] * p["sold_count"]
    return round(total, 2)
