# =============================================================
# ride.py — Ride Booking, Matching and Tracking
# Ride Sharing System (Pathao / Shohoz style)
# =============================================================


def request_ride(rides, ride_id, rider_id, pickup, dropoff, ride_type="bike"):
    """Request a new ride."""
    if ride_id in rides:
        return False, "Ride ID already exists"
    valid_types = ["bike", "car", "cng", "auto", "premium"]
    if ride_type not in valid_types:
        return False, "Invalid ride type"
    rides[ride_id] = {
        "rider_id": rider_id, "driver_id": None,
        "pickup": pickup, "dropoff": dropoff,
        "type": ride_type, "status": "requested",
        "fare": 0, "distance_km": 0,
    }
    return True, "Ride requested"


def assign_driver(rides, ride_id, driver_id):
    """Assign a driver to a ride."""
    if ride_id not in rides:
        return False, "Ride not found"
    if rides[ride_id]["status"] != "requested":
        return False, "Ride not available for assignment"
    rides[ride_id]["driver_id"] = driver_id
    rides[ride_id]["status"] = "accepted"
    return True, "Driver assigned"


def start_ride(rides, ride_id):
    """Mark ride as started."""
    if ride_id not in rides:
        return False, "Ride not found"
    if rides[ride_id]["status"] != "accepted":
        return False, "Cannot start ride in current state"
    rides[ride_id]["status"] = "in_progress"
    return True, "Ride started"


def complete_ride(rides, ride_id, distance_km, fare):
    """Complete a ride and record distance and fare."""
    if ride_id not in rides:
        return False, "Ride not found"
    if rides[ride_id]["status"] != "in_progress":
        return False, "Ride not in progress"
    if distance_km <= 0 or fare <= 0:
        return False, "Invalid distance or fare"
    rides[ride_id]["status"] = "completed"
    rides[ride_id]["distance_km"] = distance_km
    rides[ride_id]["fare"] = fare
    return True, "Ride completed"


def cancel_ride(rides, ride_id, cancelled_by, reason=""):
    """Cancel a ride."""
    if ride_id not in rides:
        return False, "Ride not found"
    if rides[ride_id]["status"] in ("completed", "cancelled"):
        return False, "Cannot cancel this ride"
    rides[ride_id]["status"] = "cancelled"
    rides[ride_id]["cancelled_by"] = cancelled_by
    rides[ride_id]["cancel_reason"] = reason
    return True, "Ride cancelled"


def get_ride_details(rides, ride_id):
    """Get details of a ride."""
    return rides.get(ride_id, None)


def get_rider_rides(rides, rider_id):
    """Get all rides for a rider."""
    return {rid: r for rid, r in rides.items() if r["rider_id"] == rider_id}


def get_driver_rides(rides, driver_id):
    """Get all rides for a driver."""
    return {rid: r for rid, r in rides.items() if r["driver_id"] == driver_id}


def get_active_rides(rides):
    """Get all currently active rides."""
    return {rid: r for rid, r in rides.items() if r["status"] in ("requested", "accepted", "in_progress")}


def count_completed_rides(rides, driver_id):
    """Count completed rides for a driver."""
    return sum(1 for r in rides.values()
               if r["driver_id"] == driver_id and r["status"] == "completed")


def calculate_driver_total_earnings(rides, driver_id):
    """Calculate total earnings for a driver."""
    return round(sum(r["fare"] for r in rides.values()
                    if r["driver_id"] == driver_id and r["status"] == "completed"), 2)


def calculate_total_distance(rides, driver_id):
    """Calculate total distance covered by a driver."""
    return round(sum(r["distance_km"] for r in rides.values()
                    if r["driver_id"] == driver_id and r["status"] == "completed"), 2)


def get_cancellation_rate(rides, driver_id):
    """Calculate ride cancellation rate for a driver."""
    driver_rides = [r for r in rides.values() if r["driver_id"] == driver_id]
    if not driver_rides:
        return 0.0
    cancelled = sum(1 for r in driver_rides if r["status"] == "cancelled")
    return round((cancelled / len(driver_rides)) * 100, 2)


def is_ride_active(rides, ride_id):
    """Check if ride is currently active."""
    if ride_id not in rides:
        return False
    return rides[ride_id]["status"] in ("requested", "accepted", "in_progress")
