# =============================================================
# promotions.py — Vouchers, Flash Sales, Bundles and Referrals
# E-Commerce System
# =============================================================


def create_voucher(vouchers, code, discount_type, value, min_order=0, max_uses=None, max_discount=None):
    """Create a discount voucher."""
    if code in vouchers:
        return False, "Voucher code already exists"
    if discount_type not in ("percent", "fixed"):
        return False, "Invalid discount type"
    if value <= 0:
        return False, "Discount value must be positive"
    vouchers[code] = {
        "type": discount_type, "value": value,
        "min_order": min_order, "max_discount": max_discount,
        "max_uses": max_uses, "used_count": 0, "active": True,
    }
    return True, "Voucher created"


def apply_voucher(vouchers, code, subtotal):
    """Apply a voucher to get discounted total."""
    if code not in vouchers:
        return None, "Invalid voucher"
    v = vouchers[code]
    if not v["active"]:
        return None, "Voucher expired"
    if v["max_uses"] and v["used_count"] >= v["max_uses"]:
        return None, "Voucher limit reached"
    if subtotal < v["min_order"]:
        return None, f"Minimum order {v['min_order']} required"
    if v["type"] == "percent":
        discount = subtotal * (v["value"] / 100)
        if v["max_discount"]:
            discount = min(discount, v["max_discount"])
    else:
        discount = v["value"]
    vouchers[code]["used_count"] += 1
    return round(max(0, subtotal - discount), 2), "Voucher applied"


def deactivate_voucher(vouchers, code):
    """Deactivate a voucher."""
    if code not in vouchers:
        return False, "Voucher not found"
    vouchers[code]["active"] = False
    return True, "Voucher deactivated"


def create_flash_sale(flash_sales, sale_id, product_ids, discount_percent, stock_limit):
    """Create a flash sale."""
    if sale_id in flash_sales:
        return False, "Sale ID exists"
    if discount_percent <= 0 or discount_percent > 90:
        return False, "Invalid discount"
    flash_sales[sale_id] = {
        "products": product_ids, "discount": discount_percent,
        "stock_limit": stock_limit, "sold": 0, "active": True,
    }
    return True, "Flash sale created"


def apply_flash_sale_discount(flash_sales, sale_id, original_price):
    """Get flash sale price for a product."""
    if sale_id not in flash_sales:
        return None, "Sale not found"
    sale = flash_sales[sale_id]
    if not sale["active"]:
        return None, "Sale ended"
    if sale["sold"] >= sale["stock_limit"]:
        return None, "Sale stock exhausted"
    discounted = original_price * (1 - sale["discount"] / 100)
    return round(discounted, 2), "Flash sale price applied"


def is_flash_sale_active(flash_sales, sale_id):
    """Check if a flash sale is currently active."""
    if sale_id not in flash_sales:
        return False
    return flash_sales[sale_id]["active"] and flash_sales[sale_id]["sold"] < flash_sales[sale_id]["stock_limit"]


def calculate_bundle_discount(item_prices, bundle_discount_percent):
    """Calculate discount for buying items as a bundle."""
    if not item_prices or bundle_discount_percent <= 0:
        return None
    total = sum(item_prices)
    discount = total * (bundle_discount_percent / 100)
    return round(total - discount, 2)


def generate_referral_code(user_id):
    """Generate a unique referral code for a user."""
    return f"REF{str(user_id).upper()[:6]}"


def apply_referral_bonus(referrals, referrer_id, new_user_id, bonus_amount):
    """Apply referral bonus when new user completes first purchase."""
    if referrer_id not in referrals:
        referrals[referrer_id] = {"bonus": 0, "referred_users": []}
    if new_user_id in referrals[referrer_id]["referred_users"]:
        return False, "Already referred"
    referrals[referrer_id]["bonus"] += bonus_amount
    referrals[referrer_id]["referred_users"].append(new_user_id)
    return True, f"Referral bonus of {bonus_amount} added"


def get_referral_earnings(referrals, user_id):
    """Get total referral earnings for a user."""
    if user_id not in referrals:
        return 0
    return referrals[user_id]["bonus"]


def calculate_loyalty_points(order_total, points_per_100=1):
    """Calculate loyalty points earned from an order."""
    if order_total <= 0:
        return 0
    return int(order_total / 100) * points_per_100


def redeem_loyalty_points(loyalty, user_id, points, value_per_point=0.5):
    """Redeem loyalty points for discount."""
    if user_id not in loyalty:
        return None, "No loyalty points"
    if points <= 0 or points > loyalty[user_id]:
        return None, "Insufficient points"
    loyalty[user_id] -= points
    return round(points * value_per_point, 2), "Points redeemed"


def calculate_buy_x_get_y_discount(quantity, price, buy_x, get_y_free):
    """Calculate discount for buy X get Y free offer."""
    if quantity <= 0 or price <= 0 or buy_x <= 0 or get_y_free <= 0:
        return None
    sets = quantity // (buy_x + get_y_free)
    free_items = sets * get_y_free
    payable = quantity - free_items
    return round(payable * price, 2)
