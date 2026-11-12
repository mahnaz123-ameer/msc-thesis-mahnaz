# =============================================================
# delivery.py — Delivery Zones, Costs and Tracking
# E-Commerce System
# =============================================================


def calculate_delivery_charge(weight_kg, zone, subtotal=0):
    """Calculate delivery charge based on weight, zone and order value."""
    if weight_kg < 0:
        return None
    free_delivery_threshold = {"dhaka": 500, "chittagong": 800, "sylhet": 1000, "international": 5000}
    if subtotal >= free_delivery_threshold.get(zone, 1000):
        return 0
    base_rates = {"dhaka": 60, "chittagong": 120, "sylhet": 150, "other": 100, "international": 1500}
    base = base_rates.get(zone, 100)
    if weight_kg > 1:
        base += (weight_kg - 1) * 30
    return round(base, 2)


def estimate_delivery_days(zone, is_express=False):
    """Estimate delivery days based on zone."""
    standard_days = {"dhaka": 1, "chittagong": 2, "sylhet": 3, "other": 4, "international": 14}
    days = standard_days.get(zone, 5)
    return max(1, days // 2) if is_express else days


def assign_courier(couriers, order_id, zone):
    """Assign a courier to an order."""
    available = [cid for cid, info in couriers.items()
                 if info["active"] and zone in info["zones"]]
    if not available:
        return None, "No courier available for this zone"
    best = min(available, key=lambda c: couriers[c]["current_load"])
    couriers[best]["current_load"] += 1
    return best, f"Assigned to courier {best}"


def update_delivery_status(deliveries, delivery_id, new_status, location=""):
    """Update delivery tracking status."""
    valid = ["dispatched", "in_transit", "out_for_delivery", "delivered", "failed", "returned"]
    if delivery_id not in deliveries:
        return False, "Delivery not found"
    if new_status not in valid:
        return False, "Invalid status"
    deliveries[delivery_id]["status"] = new_status
    deliveries[delivery_id]["current_location"] = location
    return True, f"Status: {new_status}"


def calculate_express_surcharge(base_charge, surcharge_percent=50):
    """Calculate express delivery surcharge."""
    if base_charge < 0:
        return None
    return round(base_charge * (surcharge_percent / 100), 2)


def is_deliverable_to_zone(zones_served, target_zone):
    """Check if delivery is available to a zone."""
    return target_zone.lower() in [z.lower() for z in zones_served]


def calculate_cod_charge(order_total, cod_percent=1.5):
    """Calculate COD handling charge."""
    if order_total <= 0:
        return None
    return round(order_total * (cod_percent / 100), 2)


def get_active_deliveries(deliveries):
    """Get all deliveries currently in transit."""
    active = ["dispatched", "in_transit", "out_for_delivery"]
    return {did: d for did, d in deliveries.items() if d["status"] in active}


def get_failed_deliveries(deliveries):
    """Get all failed deliveries."""
    return {did: d for did, d in deliveries.items() if d["status"] == "failed"}


def calculate_courier_efficiency(couriers, deliveries, courier_id):
    """Calculate delivery success rate for a courier."""
    courier_deliveries = [d for d in deliveries.values() if d.get("courier_id") == courier_id]
    if not courier_deliveries:
        return 0.0
    delivered = sum(1 for d in courier_deliveries if d["status"] == "delivered")
    return round((delivered / len(courier_deliveries)) * 100, 2)


def schedule_pickup(pickups, pickup_id, seller_id, pickup_date, items_count):
    """Schedule a pickup from seller."""
    if pickup_id in pickups:
        return False, "Pickup ID exists"
    if items_count <= 0:
        return False, "No items to pick up"
    pickups[pickup_id] = {
        "seller_id": seller_id, "date": pickup_date,
        "items_count": items_count, "status": "scheduled",
    }
    return True, "Pickup scheduled"


def calculate_total_delivery_cost(deliveries):
    """Calculate total delivery cost across all orders."""
    return round(sum(d.get("charge", 0) for d in deliveries.values()), 2)


def get_delivery_by_order(deliveries, order_id):
    """Get delivery record for a specific order."""
    for did, d in deliveries.items():
        if d.get("order_id") == order_id:
            return did, d
    return None, None


def calculate_delivery_sla_breach(deliveries, today):
    """Get deliveries that breached SLA (overdue)."""
    breached = {}
    for did, d in deliveries.items():
        if d["status"] not in ("delivered", "returned") and d.get("expected_date") and d["expected_date"] < today:
            breached[did] = d
    return breached
