# =============================================================
# driver.py — Driver Profile, Verification and Earnings
# Ride Sharing System
# =============================================================


def register_driver(drivers, driver_id, name, phone, vehicle_type, vehicle_number, license_number):
    """Register a new driver."""
    if driver_id in drivers:
        return False, "Driver ID already exists"
    drivers[driver_id] = {
        "name": name, "phone": phone,
        "vehicle_type": vehicle_type, "vehicle_number": vehicle_number,
        "license_number": license_number, "verified": False,
        "active": False, "online": False,
        "total_earnings": 0, "total_rides": 0,
        "rating": [], "balance": 0,
    }
    return True, "Driver registered"


def verify_driver(drivers, driver_id):
    """Verify and activate a driver."""
    if driver_id not in drivers:
        return False, "Driver not found"
    drivers[driver_id]["verified"] = True
    drivers[driver_id]["active"] = True
    return True, "Driver verified and activated"


def go_online(drivers, driver_id):
    """Set driver as available for rides."""
    if driver_id not in drivers:
        return False, "Driver not found"
    if not drivers[driver_id]["verified"]:
        return False, "Driver not verified"
    if not drivers[driver_id]["active"]:
        return False, "Driver account is inactive"
    drivers[driver_id]["online"] = True
    return True, "Driver is now online"


def go_offline(drivers, driver_id):
    """Set driver as unavailable."""
    if driver_id not in drivers:
        return False, "Driver not found"
    drivers[driver_id]["online"] = False
    return True, "Driver is now offline"


def add_earning(drivers, driver_id, amount):
    """Add earnings to driver account."""
    if driver_id not in drivers:
        return False, "Driver not found"
    if amount <= 0:
        return False, "Invalid amount"
    drivers[driver_id]["total_earnings"] += amount
    drivers[driver_id]["balance"] += amount
    drivers[driver_id]["total_rides"] += 1
    return True, f"Earning of {amount} added"


def withdraw_earnings(drivers, driver_id, amount):
    """Withdraw earnings from driver balance."""
    if driver_id not in drivers:
        return False, "Driver not found"
    if amount <= 0:
        return False, "Invalid amount"
    if drivers[driver_id]["balance"] < amount:
        return False, "Insufficient balance"
    drivers[driver_id]["balance"] -= amount
    return True, f"Withdrawal of {amount} successful"


def add_rating(drivers, driver_id, rating):
    """Add rider rating for a driver."""
    if driver_id not in drivers:
        return False, "Driver not found"
    if rating < 1 or rating > 5:
        return False, "Rating must be 1-5"
    drivers[driver_id]["rating"].append(rating)
    return True, "Rating added"


def get_average_rating(drivers, driver_id):
    """Get driver average rating."""
    if driver_id not in drivers:
        return None
    ratings = drivers[driver_id]["rating"]
    if not ratings:
        return 5.0
    return round(sum(ratings) / len(ratings), 2)


def is_driver_eligible_for_ride(drivers, driver_id):
    """Check if driver can accept rides."""
    if driver_id not in drivers:
        return False
    d = drivers[driver_id]
    return d["verified"] and d["active"] and d["online"]


def calculate_driver_incentive(total_rides, ride_target, bonus_amount):
    """Calculate bonus incentive for reaching ride target."""
    if total_rides < ride_target:
        return 0
    return bonus_amount


def get_online_drivers(drivers):
    """Get all currently online drivers."""
    return {did: d for did, d in drivers.items() if d["online"]}


def get_drivers_by_vehicle_type(drivers, vehicle_type):
    """Get active drivers by vehicle type."""
    return {did: d for did, d in drivers.items()
            if d["vehicle_type"] == vehicle_type and d["online"]}


def suspend_driver(drivers, driver_id, reason):
    """Suspend a driver account."""
    if driver_id not in drivers:
        return False, "Driver not found"
    drivers[driver_id]["active"] = False
    drivers[driver_id]["online"] = False
    drivers[driver_id]["suspension_reason"] = reason
    return True, "Driver suspended"


def calculate_level(total_rides):
    """Calculate driver tier level based on rides completed."""
    if total_rides < 50:
        return "Bronze"
    elif total_rides < 200:
        return "Silver"
    elif total_rides < 500:
        return "Gold"
    else:
        return "Platinum"


def is_rating_below_threshold(drivers, driver_id, threshold=3.5):
    """Check if driver rating has fallen below minimum threshold."""
    avg = get_average_rating(drivers, driver_id)
    if avg is None:
        return False
    return avg < threshold


def calculate_weekly_summary(rides_this_week, earnings_this_week):
    """Calculate driver weekly performance summary."""
    if rides_this_week < 0 or earnings_this_week < 0:
        return None
    avg_per_ride = round(earnings_this_week / rides_this_week, 2) if rides_this_week > 0 else 0
    return {
        "rides": rides_this_week,
        "earnings": earnings_this_week,
        "avg_per_ride": avg_per_ride,
    }
