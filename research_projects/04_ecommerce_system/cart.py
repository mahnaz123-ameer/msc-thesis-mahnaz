# =============================================================
# cart.py — Shopping Cart Management
# E-Commerce System
# =============================================================


def add_to_cart(carts, user_id, product_id, quantity, price):
    """Add a product to user's cart."""
    if quantity <= 0:
        return False, "Quantity must be positive"
    if price <= 0:
        return False, "Invalid price"
    if user_id not in carts:
        carts[user_id] = {}
    if product_id in carts[user_id]:
        carts[user_id][product_id]["quantity"] += quantity
    else:
        carts[user_id][product_id] = {"quantity": quantity, "price": price}
    return True, "Added to cart"


def remove_from_cart(carts, user_id, product_id):
    """Remove a product from cart."""
    if user_id not in carts or product_id not in carts[user_id]:
        return False, "Item not in cart"
    del carts[user_id][product_id]
    return True, "Item removed"


def update_cart_quantity(carts, user_id, product_id, new_quantity):
    """Update quantity of a product in cart."""
    if user_id not in carts or product_id not in carts[user_id]:
        return False, "Item not in cart"
    if new_quantity <= 0:
        return remove_from_cart(carts, user_id, product_id)
    carts[user_id][product_id]["quantity"] = new_quantity
    return True, "Quantity updated"


def clear_cart(carts, user_id):
    """Clear all items from user's cart."""
    if user_id not in carts:
        return False, "Cart not found"
    carts[user_id] = {}
    return True, "Cart cleared"


def get_cart_items(carts, user_id):
    """Get all items in user's cart."""
    return carts.get(user_id, {})


def calculate_cart_subtotal(carts, user_id):
    """Calculate subtotal (before discounts and shipping)."""
    items = get_cart_items(carts, user_id)
    return round(sum(item["price"] * item["quantity"] for item in items.values()), 2)


def calculate_cart_item_count(carts, user_id):
    """Get total number of items in cart."""
    items = get_cart_items(carts, user_id)
    return sum(item["quantity"] for item in items.values())


def apply_coupon(subtotal, coupon_code, coupons):
    """Apply a coupon code to the cart subtotal."""
    if coupon_code not in coupons:
        return None, "Invalid coupon"
    coupon = coupons[coupon_code]
    if not coupon.get("active", False):
        return None, "Coupon expired"
    if subtotal < coupon.get("min_order", 0):
        return None, f"Minimum order {coupon['min_order']} required"
    if coupon["type"] == "percent":
        discount = subtotal * (coupon["value"] / 100)
        discount = min(discount, coupon.get("max_discount", discount))
    else:
        discount = coupon["value"]
    return round(max(0, subtotal - discount), 2), "Coupon applied"


def calculate_shipping_cost(subtotal, weight_kg, zone="local"):
    """Calculate shipping cost based on order value, weight and zone."""
    if subtotal >= 1000:
        return 0
    base_rates = {"local": 60, "domestic": 120, "international": 500}
    base = base_rates.get(zone, 60)
    if weight_kg > 5:
        base += (weight_kg - 5) * 20
    return round(base, 2)


def calculate_vat(subtotal, vat_percent=5):
    """Calculate VAT on order."""
    if subtotal < 0:
        return None
    return round(subtotal * (vat_percent / 100), 2)


def calculate_order_total(subtotal, shipping, vat=0, discount=0):
    """Calculate final order total."""
    if any(x < 0 for x in [subtotal, shipping, vat, discount]):
        return None
    return round(subtotal + shipping + vat - discount, 2)


def is_cart_empty(carts, user_id):
    """Check if cart is empty."""
    return len(carts.get(user_id, {})) == 0


def merge_carts(carts, guest_id, user_id):
    """Merge guest cart into logged-in user cart."""
    if guest_id not in carts:
        return True, "Nothing to merge"
    for pid, item in carts[guest_id].items():
        add_to_cart(carts, user_id, pid, item["quantity"], item["price"])
    del carts[guest_id]
    return True, "Carts merged"


def get_cart_product_ids(carts, user_id):
    """Get list of product IDs in cart."""
    return list(carts.get(user_id, {}).keys())


def calculate_savings(carts, user_id, original_prices):
    """Calculate total savings from discounts in cart."""
    items = get_cart_items(carts, user_id)
    savings = 0
    for pid, item in items.items():
        original = original_prices.get(pid, item["price"])
        savings += (original - item["price"]) * item["quantity"]
    return round(max(0, savings), 2)


def validate_stock_availability(carts, user_id, products):
    """Check all cart items are still in stock."""
    items = get_cart_items(carts, user_id)
    out_of_stock = []
    for pid, item in items.items():
        if pid not in products or products[pid]["stock"] < item["quantity"]:
            out_of_stock.append(pid)
    return out_of_stock
