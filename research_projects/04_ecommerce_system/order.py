# =============================================================
# order.py — Order Placement, Tracking and Management
# E-Commerce System
# =============================================================


def place_order(orders, order_id, user_id, items, total_amount, payment_method, address):
    """Place a new order."""
    if order_id in orders:
        return False, "Order ID already exists"
    if not items:
        return False, "No items in order"
    if total_amount <= 0:
        return False, "Invalid order amount"
    orders[order_id] = {
        "user_id": user_id, "items": items, "total": total_amount,
        "payment_method": payment_method, "address": address,
        "status": "placed", "cancellation_reason": None,
    }
    return True, "Order placed"


def cancel_order(orders, order_id, reason="Customer request"):
    """Cancel an order."""
    if order_id not in orders:
        return False, "Order not found"
    if orders[order_id]["status"] in ("shipped", "delivered"):
        return False, "Cannot cancel shipped or delivered order"
    if orders[order_id]["status"] == "cancelled":
        return False, "Order already cancelled"
    orders[order_id]["status"] = "cancelled"
    orders[order_id]["cancellation_reason"] = reason
    return True, "Order cancelled"


def update_order_status(orders, order_id, new_status):
    """Update order status in fulfillment pipeline."""
    valid_statuses = ["placed", "confirmed", "packed", "shipped", "out_for_delivery", "delivered", "cancelled", "returned"]
    if order_id not in orders:
        return False, "Order not found"
    if new_status not in valid_statuses:
        return False, "Invalid status"
    if orders[order_id]["status"] == "cancelled":
        return False, "Cannot update cancelled order"
    orders[order_id]["status"] = new_status
    return True, f"Status updated to {new_status}"


def request_return(orders, order_id, reason):
    """Request a return for a delivered order."""
    if order_id not in orders:
        return False, "Order not found"
    if orders[order_id]["status"] != "delivered":
        return False, "Can only return delivered orders"
    orders[order_id]["status"] = "return_requested"
    orders[order_id]["return_reason"] = reason
    return True, "Return requested"


def calculate_refund_amount(orders, order_id, refund_policy="full"):
    """Calculate refund amount based on order and policy."""
    if order_id not in orders:
        return None
    total = orders[order_id]["total"]
    policies = {"full": 100, "partial": 80, "no_shipping": 90}
    percent = policies.get(refund_policy, 100)
    return round(total * (percent / 100), 2)


def get_order_details(orders, order_id):
    """Get details of a specific order."""
    return orders.get(order_id, None)


def get_user_orders(orders, user_id):
    """Get all orders for a user."""
    return {oid: o for oid, o in orders.items() if o["user_id"] == user_id}


def get_orders_by_status(orders, status):
    """Get all orders with a specific status."""
    return {oid: o for oid, o in orders.items() if o["status"] == status}


def calculate_order_item_count(order):
    """Count total items in an order."""
    if not order or "items" not in order:
        return 0
    return sum(item.get("quantity", 1) for item in order["items"].values())


def is_order_cancellable(orders, order_id):
    """Check if an order can be cancelled."""
    if order_id not in orders:
        return False
    return orders[order_id]["status"] not in ("shipped", "delivered", "cancelled")


def get_total_revenue(orders):
    """Calculate total revenue from all delivered orders."""
    return round(sum(o["total"] for o in orders.values() if o["status"] == "delivered"), 2)


def calculate_average_order_value(orders):
    """Calculate average order value."""
    completed = [o["total"] for o in orders.values() if o["status"] == "delivered"]
    if not completed:
        return 0.0
    return round(sum(completed) / len(completed), 2)


def get_top_customers(orders, top_n=10):
    """Get top N customers by total spend."""
    spend = {}
    for o in orders.values():
        if o["status"] == "delivered":
            spend[o["user_id"]] = spend.get(o["user_id"], 0) + o["total"]
    return sorted(spend.items(), key=lambda x: x[1], reverse=True)[:top_n]


def count_orders_by_payment_method(orders):
    """Count orders grouped by payment method."""
    counts = {}
    for o in orders.values():
        method = o["payment_method"]
        counts[method] = counts.get(method, 0) + 1
    return counts


def has_order_been_delivered(orders, order_id):
    """Check if an order has been delivered."""
    if order_id not in orders:
        return False
    return orders[order_id]["status"] == "delivered"


def get_pending_orders(orders):
    """Get all orders pending fulfillment."""
    pending_statuses = ["placed", "confirmed", "packed"]
    return {oid: o for oid, o in orders.items() if o["status"] in pending_statuses}
