# =============================================================
# rider.py — Rider Profile, Wallet and Loyalty
# Ride Sharing System
# =============================================================


def register_rider(riders, rider_id, name, phone, email):
    """Register a new rider."""
    if rider_id in riders:
        return False, "Rider ID already exists"
    if "@" not in email:
        return False, "Invalid email"
    riders[rider_id] = {
        "name": name, "phone": phone, "email": email,
        "active": True, "wallet_balance": 0,
        "total_rides": 0, "loyalty_points": 0,
        "referral_code": f"RIDE{rider_id[:4].upper()}",
    }
    return True, "Rider registered"


def top_up_wallet(riders, rider_id, amount):
    """Add money to rider wallet."""
    if rider_id not in riders:
        return False, "Rider not found"
    if amount <= 0:
        return False, "Invalid amount"
    riders[rider_id]["wallet_balance"] += amount
    return True, f"Wallet topped up by {amount}"


def deduct_wallet(riders, rider_id, amount):
    """Deduct fare from rider wallet."""
    if rider_id not in riders:
        return False, "Rider not found"
    if amount <= 0:
        return False, "Invalid amount"
    if riders[rider_id]["wallet_balance"] < amount:
        return False, "Insufficient wallet balance"
    riders[rider_id]["wallet_balance"] -= amount
    return True, "Payment deducted"


def get_wallet_balance(riders, rider_id):
    """Get rider's current wallet balance."""
    if rider_id not in riders:
        return None
    return riders[rider_id]["wallet_balance"]


def has_sufficient_balance(riders, rider_id, amount):
    """Check if rider has enough wallet balance."""
    balance = get_wallet_balance(riders, rider_id)
    if balance is None:
        return False
    return balance >= amount


def add_loyalty_points(riders, rider_id, points):
    """Add loyalty points after ride completion."""
    if rider_id not in riders:
        return False, "Rider not found"
    if points <= 0:
        return False, "Invalid points"
    riders[rider_id]["loyalty_points"] += points
    return True, f"{points} points added"


def redeem_loyalty_points(riders, rider_id, points, value_per_point=0.5):
    """Redeem loyalty points for wallet credit."""
    if rider_id not in riders:
        return None, "Rider not found"
    if points <= 0:
        return None, "Invalid points"
    if riders[rider_id]["loyalty_points"] < points:
        return None, "Insufficient points"
    riders[rider_id]["loyalty_points"] -= points
    credit = round(points * value_per_point, 2)
    riders[rider_id]["wallet_balance"] += credit
    return credit, f"Redeemed {points} points for {credit} credit"


def calculate_loyalty_points_earned(fare):
    """Calculate loyalty points earned from a fare."""
    if fare <= 0:
        return 0
    return int(fare / 10)


def increment_ride_count(riders, rider_id):
    """Increment total ride count."""
    if rider_id not in riders:
        return False, "Rider not found"
    riders[rider_id]["total_rides"] += 1
    return True, "Ride count updated"


def get_rider_level(riders, rider_id):
    """Get rider tier based on total rides."""
    if rider_id not in riders:
        return None
    total = riders[rider_id]["total_rides"]
    if total < 10:
        return "New"
    elif total < 50:
        return "Regular"
    elif total < 150:
        return "Frequent"
    else:
        return "VIP"


def apply_referral(riders, referrer_id, new_rider_id, bonus=50):
    """Apply referral bonus to both referrer and new rider."""
    if referrer_id not in riders or new_rider_id not in riders:
        return False, "Rider not found"
    riders[referrer_id]["wallet_balance"] += bonus
    riders[new_rider_id]["wallet_balance"] += bonus
    return True, f"Referral bonus of {bonus} given to both"


def deactivate_rider(riders, rider_id):
    """Deactivate a rider account."""
    if rider_id not in riders:
        return False, "Rider not found"
    riders[rider_id]["active"] = False
    return True, "Rider deactivated"


def is_rider_active(riders, rider_id):
    """Check if a rider is active."""
    if rider_id not in riders:
        return False
    return riders[rider_id]["active"]


def get_vip_riders(riders):
    """Get all VIP riders."""
    return {rid: r for rid, r in riders.items()
            if r["total_rides"] >= 150 and r["active"]}


def calculate_cashback(fare, cashback_percent, max_cashback=50):
    """Calculate cashback for a ride."""
    if fare <= 0 or cashback_percent <= 0:
        return 0
    cashback = fare * (cashback_percent / 100)
    return round(min(cashback, max_cashback), 2)


def search_rider(riders, phone):
    """Search rider by phone number."""
    return next((rid for rid, r in riders.items() if r["phone"] == phone), None)
