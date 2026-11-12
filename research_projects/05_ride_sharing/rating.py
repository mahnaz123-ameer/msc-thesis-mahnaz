# =============================================================
# rating.py — Rating, Review and Performance Management
# Ride Sharing System
# =============================================================


def submit_driver_rating(ratings, ride_id, rider_id, driver_id, score, comment=""):
    """Submit a rating for a driver after ride completion."""
    if score < 1 or score > 5:
        return False, "Score must be between 1 and 5"
    rating_id = f"DR-{ride_id}"
    if rating_id in ratings:
        return False, "Rating already submitted for this ride"
    ratings[rating_id] = {
        "type": "driver", "ride_id": ride_id,
        "from_id": rider_id, "to_id": driver_id,
        "score": score, "comment": comment,
    }
    return True, "Driver rated"


def submit_rider_rating(ratings, ride_id, driver_id, rider_id, score, comment=""):
    """Submit a rating for a rider after ride completion."""
    if score < 1 or score > 5:
        return False, "Score must be between 1 and 5"
    rating_id = f"RR-{ride_id}"
    if rating_id in ratings:
        return False, "Rating already submitted for this ride"
    ratings[rating_id] = {
        "type": "rider", "ride_id": ride_id,
        "from_id": driver_id, "to_id": rider_id,
        "score": score, "comment": comment,
    }
    return True, "Rider rated"


def get_average_rating(ratings, user_id, user_type="driver"):
    """Calculate average rating for a driver or rider."""
    user_ratings = [r["score"] for r in ratings.values()
                    if r["to_id"] == user_id and r["type"] == user_type]
    if not user_ratings:
        return 5.0
    return round(sum(user_ratings) / len(user_ratings), 2)


def get_rating_count(ratings, user_id, user_type="driver"):
    """Get total number of ratings received."""
    return sum(1 for r in ratings.values()
               if r["to_id"] == user_id and r["type"] == user_type)


def get_rating_breakdown(ratings, user_id, user_type="driver"):
    """Get count of each rating score (1-5) for a user."""
    breakdown = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for r in ratings.values():
        if r["to_id"] == user_id and r["type"] == user_type:
            breakdown[r["score"]] += 1
    return breakdown


def is_below_minimum_rating(ratings, user_id, user_type="driver", threshold=3.5):
    """Check if user rating is below minimum acceptable threshold."""
    avg = get_average_rating(ratings, user_id, user_type)
    return avg < threshold


def get_recent_ratings(ratings, user_id, user_type="driver", last_n=10):
    """Get the most recent N ratings for a user."""
    user_ratings = [(rid, r) for rid, r in ratings.items()
                    if r["to_id"] == user_id and r["type"] == user_type]
    return user_ratings[-last_n:]


def calculate_rating_trend(ratings, user_id, user_type="driver"):
    """Compare recent 10 ratings vs overall to detect trend."""
    all_ratings = [r["score"] for r in ratings.values()
                   if r["to_id"] == user_id and r["type"] == user_type]
    if len(all_ratings) < 10:
        return "insufficient_data"
    overall_avg = sum(all_ratings) / len(all_ratings)
    recent_avg = sum(all_ratings[-10:]) / 10
    if recent_avg > overall_avg + 0.3:
        return "improving"
    elif recent_avg < overall_avg - 0.3:
        return "declining"
    return "stable"


def get_highly_rated_drivers(ratings, drivers, min_rating=4.5, min_rides=20):
    """Get drivers with high ratings and sufficient ride count."""
    result = []
    for driver_id in drivers:
        avg = get_average_rating(ratings, driver_id, "driver")
        count = get_rating_count(ratings, driver_id, "driver")
        if avg >= min_rating and count >= min_rides:
            result.append((driver_id, avg, count))
    return sorted(result, key=lambda x: x[1], reverse=True)


def apply_rating_penalty(drivers, driver_id, penalty_points):
    """Apply penalty to driver for bad behaviour (reduces effective rating)."""
    if driver_id not in drivers:
        return False, "Driver not found"
    if penalty_points <= 0:
        return False, "Invalid penalty"
    drivers[driver_id]["penalty_points"] = drivers[driver_id].get("penalty_points", 0) + penalty_points
    return True, f"Penalty of {penalty_points} applied"


def calculate_effective_rating(raw_rating, penalty_points):
    """Calculate effective rating after applying penalties."""
    if raw_rating < 1 or raw_rating > 5:
        return None
    deduction = penalty_points * 0.1
    return round(max(1.0, raw_rating - deduction), 2)


def should_suspend_for_rating(avg_rating, total_ratings, min_rating=3.0, min_ratings_required=10):
    """Determine if user should be suspended based on consistently low rating."""
    if total_ratings < min_ratings_required:
        return False
    return avg_rating < min_rating


def get_unrated_rides(rides, ratings, user_id, user_type="rider"):
    """Get rides that have not yet been rated."""
    rated_ride_ids = {r["ride_id"] for r in ratings.values() if r["from_id"] == user_id}
    if user_type == "rider":
        completed = {rid for rid, r in rides.items()
                     if r["rider_id"] == user_id and r["status"] == "completed"}
    else:
        completed = {rid for rid, r in rides.items()
                     if r["driver_id"] == user_id and r["status"] == "completed"}
    return completed - rated_ride_ids
