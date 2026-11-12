# =============================================================
# safety.py — Safety, SOS and Route Deviation Detection
# Ride Sharing System
# =============================================================


def trigger_sos(sos_alerts, ride_id, user_id, user_type, location):
    """Trigger an SOS emergency alert."""
    if not ride_id or not user_id:
        return False, "Invalid SOS request"
    alert_id = f"SOS-{ride_id}"
    sos_alerts[alert_id] = {
        "ride_id": ride_id, "user_id": user_id,
        "user_type": user_type, "location": location,
        "status": "active", "resolved": False,
    }
    return True, f"SOS alert {alert_id} triggered"


def resolve_sos(sos_alerts, alert_id, resolution_note=""):
    """Resolve an SOS alert."""
    if alert_id not in sos_alerts:
        return False, "Alert not found"
    sos_alerts[alert_id]["resolved"] = True
    sos_alerts[alert_id]["status"] = "resolved"
    sos_alerts[alert_id]["resolution"] = resolution_note
    return True, "SOS resolved"


def detect_route_deviation(planned_route, actual_location, deviation_threshold_km=0.5):
    """Detect if driver has deviated from planned route."""
    if not planned_route or not actual_location:
        return False
    for waypoint in planned_route:
        distance = calculate_distance(waypoint, actual_location)
        if distance <= deviation_threshold_km:
            return False
    return True


def calculate_distance(point1, point2):
    """Calculate simple Euclidean distance between two coordinate points."""
    if not point1 or not point2:
        return None
    lat1, lon1 = point1
    lat2, lon2 = point2
    return round(((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2) ** 0.5, 4)


def share_trip(trips_shared, ride_id, rider_id, contact_phone):
    """Share live trip details with an emergency contact."""
    if not ride_id or not contact_phone:
        return False, "Invalid share request"
    if len(str(contact_phone)) != 11:
        return False, "Invalid contact number"
    trips_shared[ride_id] = {
        "rider_id": rider_id,
        "contact": contact_phone,
        "active": True,
    }
    return True, f"Trip shared with {contact_phone}"


def stop_trip_sharing(trips_shared, ride_id):
    """Stop sharing trip after ride completes."""
    if ride_id not in trips_shared:
        return False, "No active trip sharing"
    trips_shared[ride_id]["active"] = False
    return True, "Trip sharing stopped"


def verify_driver_selfie(selfie_verified):
    """Check if driver passed selfie verification."""
    return selfie_verified is True


def calculate_safety_score(sos_count, deviation_count, total_rides):
    """Calculate driver safety score (0-100)."""
    if total_rides <= 0:
        return 100
    sos_rate = sos_count / total_rides
    deviation_rate = deviation_count / total_rides
    score = 100 - (sos_rate * 50 * 100) - (deviation_rate * 30 * 100)
    return round(max(0, min(100, score)), 2)


def is_driver_safe_to_operate(safety_score, min_score=70):
    """Check if driver safety score is above minimum threshold."""
    return safety_score >= min_score


def flag_ride(flagged_rides, ride_id, reason, flagged_by):
    """Flag a ride for safety review."""
    if not ride_id:
        return False, "Invalid ride ID"
    flagged_rides[ride_id] = {
        "reason": reason,
        "flagged_by": flagged_by,
        "reviewed": False,
    }
    return True, "Ride flagged for review"


def get_active_sos_alerts(sos_alerts):
    """Get all unresolved SOS alerts."""
    return {aid: a for aid, a in sos_alerts.items() if not a["resolved"]}


def calculate_ride_duration(start_time, end_time):
    """Calculate ride duration in minutes."""
    if end_time < start_time:
        return None
    return round((end_time - start_time).total_seconds() / 60, 2)


def is_ride_duration_suspicious(duration_mins, distance_km, max_speed_kmh=80):
    """Check if ride duration is suspiciously short for the distance."""
    if duration_mins <= 0 or distance_km <= 0:
        return False
    actual_speed = (distance_km / duration_mins) * 60
    return actual_speed > max_speed_kmh


def get_unreviewed_flags(flagged_rides):
    """Get all flagged rides not yet reviewed."""
    return {rid: r for rid, r in flagged_rides.items() if not r["reviewed"]}
