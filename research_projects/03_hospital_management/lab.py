# =============================================================
# lab.py — Laboratory Tests, Results and Reports
# Hospital Management System
# =============================================================


def book_lab_test(lab_orders, order_id, patient_id, doctor_id, tests):
    """Book laboratory tests for a patient."""
    if order_id in lab_orders:
        return False, "Order ID already exists"
    if not tests:
        return False, "No tests specified"
    lab_orders[order_id] = {
        "patient_id": patient_id, "doctor_id": doctor_id,
        "tests": tests, "results": {}, "status": "pending",
    }
    return True, "Lab tests booked"


def record_test_result(lab_orders, order_id, test_name, value, unit, reference_range):
    """Record result for a specific lab test."""
    if order_id not in lab_orders:
        return False, "Order not found"
    if test_name not in lab_orders[order_id]["tests"]:
        return False, "Test not in order"
    is_normal = check_normal_range(value, reference_range)
    lab_orders[order_id]["results"][test_name] = {
        "value": value, "unit": unit,
        "reference_range": reference_range, "is_normal": is_normal,
    }
    return True, "Result recorded"


def check_normal_range(value, reference_range):
    """Check if a test result is within normal range (min, max)."""
    if not reference_range or len(reference_range) != 2:
        return None
    min_val, max_val = reference_range
    return min_val <= value <= max_val


def mark_order_complete(lab_orders, order_id):
    """Mark a lab order as complete."""
    if order_id not in lab_orders:
        return False, "Order not found"
    if not lab_orders[order_id]["results"]:
        return False, "No results recorded yet"
    lab_orders[order_id]["status"] = "completed"
    return True, "Order marked complete"


def get_abnormal_results(lab_orders, order_id):
    """Get all abnormal test results in an order."""
    if order_id not in lab_orders:
        return {}
    return {test: info for test, info in lab_orders[order_id]["results"].items()
            if info.get("is_normal") is False}


def has_critical_results(lab_orders, order_id, critical_tests):
    """Check if any critical tests have abnormal results."""
    abnormals = get_abnormal_results(lab_orders, order_id)
    return any(test in abnormals for test in critical_tests)


def get_pending_orders(lab_orders):
    """Get all pending lab orders."""
    return {oid: info for oid, info in lab_orders.items() if info["status"] == "pending"}


def get_patient_lab_history(lab_orders, patient_id):
    """Get all lab orders for a patient."""
    return {oid: info for oid, info in lab_orders.items() if info["patient_id"] == patient_id}


def calculate_lab_bill(tests, test_prices):
    """Calculate total lab bill for a list of tests."""
    if not tests:
        return 0
    total = 0
    for test in tests:
        if test not in test_prices:
            return None
        total += test_prices[test]
    return total


def get_test_result(lab_orders, order_id, test_name):
    """Get result for a specific test in an order."""
    if order_id not in lab_orders:
        return None
    return lab_orders[order_id]["results"].get(test_name, None)


def calculate_result_deviation(value, reference_range):
    """Calculate how far a result deviates from normal range."""
    if not reference_range or len(reference_range) != 2:
        return None
    min_val, max_val = reference_range
    if value < min_val:
        return round(min_val - value, 2)
    elif value > max_val:
        return round(value - max_val, 2)
    return 0


def get_all_results_summary(lab_orders, order_id):
    """Get summary of all results — normal and abnormal counts."""
    if order_id not in lab_orders:
        return None
    results = lab_orders[order_id]["results"]
    normal = sum(1 for r in results.values() if r.get("is_normal") is True)
    abnormal = sum(1 for r in results.values() if r.get("is_normal") is False)
    return {
        "total_tests": len(results),
        "normal": normal,
        "abnormal": abnormal,
        "pending": len(lab_orders[order_id]["tests"]) - len(results),
    }


def cancel_lab_order(lab_orders, order_id, reason=""):
    """Cancel a pending lab order."""
    if order_id not in lab_orders:
        return False, "Order not found"
    if lab_orders[order_id]["status"] == "completed":
        return False, "Cannot cancel completed order"
    lab_orders[order_id]["status"] = "cancelled"
    return True, "Order cancelled"


def get_lab_orders_by_doctor(lab_orders, doctor_id):
    """Get all lab orders placed by a specific doctor."""
    return {oid: info for oid, info in lab_orders.items() if info["doctor_id"] == doctor_id}
