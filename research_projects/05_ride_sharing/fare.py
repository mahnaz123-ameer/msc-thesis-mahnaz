# =============================================================
# fare.py — Fare Calculation, Surge Pricing and Promo Codes
# Ride Sharing System
# =============================================================


def calculate_base_fare(ride_type):
    """Get base fare for a ride type."""
    base_fares = {"bike": 25, "cng": 40, "auto": 35, "car": 80, "premium": 150}
    return base_fares.get(ride_type, 40)


def calculate_distance_fare(distance_km, ride_type):
    """Calculate distance-based fare."""
    if distance_km <= 0:
        return None
    per_km_rates = {"bike": 12, "cng": 15, "auto": 14, "car": 25, "premium": 40}
    rate = per_km_rates.get(ride_type, 15)
    return round(distance_km * rate, 2)


def calculate_time_fare(duration_mins, ride_type):
    """Calculate time-based fare component."""
    if duration_mins < 0:
        return None
    per_min_rates = {"bike": 1.5, "cng": 2, "auto": 1.8, "car": 3, "premium": 5}
    rate = per_min_rates.get(ride_type, 2)
    return round(duration_mins * rate, 2)


def calculate_total_fare(ride_type, distance_km, duration_mins, surge_multiplier=1.0):
    """Calculate total ride fare."""
    base = calculate_base_fare(ride_type)
    distance_cost = calculate_distance_fare(distance_km, ride_type)
    time_cost = calculate_time_fare(duration_mins, ride_type)
    if distance_cost is None or time_cost is None:
        return None
    total = (base + distance_cost + time_cost) * surge_multiplier
    return round(max(total, base), 2)


def calculate_surge_multiplier(active_rides, available_drivers):
    """Calculate surge pricing multiplier based on demand vs supply."""
    if available_drivers <= 0:
        return 2.5
    ratio = active_rides / available_drivers
    if ratio < 1.0:
        return 1.0
    elif ratio < 1.5:
        return 1.2
    elif ratio < 2.0:
        return 1.5
    elif ratio < 3.0:
        return 2.0
    else:
        return 2.5


def is_surge_active(surge_multiplier, threshold=1.2):
    """Check if surge pricing is currently active."""
    return surge_multiplier >= threshold


def apply_promo_code(fare, code, promo_codes):
    """Apply a promo code to reduce fare."""
    if code not in promo_codes:
        return None, "Invalid promo code"
    promo = promo_codes[code]
    if not promo.get("active", False):
        return None, "Promo code expired"
    if fare < promo.get("min_fare", 0):
        return None, f"Minimum fare {promo['min_fare']} required"
    if promo["type"] == "percent":
        discount = fare * (promo["value"] / 100)
        discount = min(discount, promo.get("max_discount", discount))
    else:
        discount = promo["value"]
    new_fare = max(0, fare - discount)
    return round(new_fare, 2), "Promo applied"


def calculate_driver_commission(fare, commission_percent=80):
    """Calculate driver's share of fare."""
    if fare <= 0 or commission_percent <= 0:
        return None
    return round(fare * (commission_percent / 100), 2)


def calculate_platform_cut(fare, platform_percent=20):
    """Calculate platform's cut from fare."""
    if fare <= 0:
        return None
    return round(fare * (platform_percent / 100), 2)


def calculate_cancellation_fee(fare, cancel_policy="standard"):
    """Calculate cancellation fee."""
    if fare <= 0:
        return 0
    fees = {"none": 0, "standard": 20, "after_accept": 30, "after_start": 50}
    return fees.get(cancel_policy, 0)


def calculate_waiting_charge(wait_mins, free_wait_mins=3, rate_per_min=5):
    """Calculate waiting charge after free waiting period."""
    if wait_mins <= free_wait_mins:
        return 0
    billable = wait_mins - free_wait_mins
    return round(billable * rate_per_min, 2)


def estimate_fare_range(ride_type, distance_km):
    """Estimate fare range (min-max) for a ride."""
    min_fare = calculate_total_fare(ride_type, distance_km, 0, 1.0)
    max_fare = calculate_total_fare(ride_type, distance_km, distance_km * 3, 2.5)
    if min_fare is None or max_fare is None:
        return None
    return {"min": min_fare, "max": max_fare}


def calculate_toll_adjustment(base_fare, toll_amount):
    """Add toll charges to fare."""
    if base_fare < 0 or toll_amount < 0:
        return None
    return round(base_fare + toll_amount, 2)


def is_minimum_fare_met(fare, ride_type):
    """Check if calculated fare meets minimum fare requirement."""
    minimums = {"bike": 40, "cng": 60, "auto": 55, "car": 100, "premium": 200}
    min_fare = minimums.get(ride_type, 50)
    return fare >= min_fare
