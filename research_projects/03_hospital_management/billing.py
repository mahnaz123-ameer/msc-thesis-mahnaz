# =============================================================
# billing.py — Hospital Billing and Insurance
# Hospital Management System
# =============================================================


def calculate_consultation_fee(doctor_type, duration_mins=30):
    """Calculate consultation fee based on doctor type and duration."""
    base_fees = {"general": 500, "specialist": 1500, "senior_specialist": 3000, "professor": 5000}
    if doctor_type not in base_fees:
        return None
    base = base_fees[doctor_type]
    if duration_mins > 30:
        extra = ((duration_mins - 30) // 15) * (base * 0.25)
        return base + extra
    return base


def calculate_bed_charge(ward_type, days):
    """Calculate bed charge based on ward type and days."""
    if days < 0:
        return None
    daily_rates = {"general": 1000, "semi_private": 2500, "private": 5000, "icu": 15000, "nicu": 20000}
    if ward_type not in daily_rates:
        return None
    return daily_rates[ward_type] * days


def calculate_medicine_bill(medicines):
    """Calculate total medicine bill from list of (price, quantity)."""
    if not medicines:
        return 0.0
    return round(sum(price * qty for price, qty in medicines), 2)


def calculate_lab_test_fee(tests):
    """Calculate total lab test fees from list of test names."""
    test_fees = {
        "blood_test": 500, "urine_test": 300, "x_ray": 1500,
        "mri": 8000, "ct_scan": 5000, "ecg": 800, "ultrasound": 2000,
        "biopsy": 3000, "covid_test": 1200, "culture_test": 1500,
    }
    total = 0
    for test in tests:
        if test not in test_fees:
            return None
        total += test_fees[test]
    return total


def calculate_surgery_fee(surgery_type):
    """Calculate surgery fee based on type."""
    surgery_fees = {
        "minor": 15000, "moderate": 50000, "major": 150000,
        "emergency": 200000, "cardiac": 500000,
    }
    return surgery_fees.get(surgery_type, None)


def apply_insurance(total_bill, insurance_coverage_percent, max_coverage=None):
    """Apply insurance coverage to hospital bill."""
    if total_bill < 0 or insurance_coverage_percent < 0 or insurance_coverage_percent > 100:
        return None
    covered = total_bill * (insurance_coverage_percent / 100)
    if max_coverage is not None:
        covered = min(covered, max_coverage)
    return round(total_bill - covered, 2)


def calculate_total_bill(consultation, bed_charge, medicine, lab_tests, surgery=0, other=0):
    """Calculate total hospital bill."""
    if any(x < 0 for x in [consultation, bed_charge, medicine, lab_tests, surgery, other]):
        return None
    return round(consultation + bed_charge + medicine + lab_tests + surgery + other, 2)


def apply_discount(bill, discount_percent, reason=""):
    """Apply discount to hospital bill."""
    if bill < 0 or discount_percent < 0 or discount_percent > 100:
        return None
    discount = bill * (discount_percent / 100)
    return round(bill - discount, 2)


def calculate_vat(amount, vat_percent=15):
    """Calculate VAT on services."""
    if amount < 0 or vat_percent < 0:
        return None
    return round(amount * (vat_percent / 100), 2)


def calculate_outstanding_payment(total_bill, advance_paid):
    """Calculate remaining outstanding hospital bill."""
    if total_bill < 0 or advance_paid < 0:
        return None
    return max(0, round(total_bill - advance_paid, 2))


def calculate_refund(advance_paid, services_rendered):
    """Calculate refund if patient pays more than services cost."""
    if advance_paid < 0 or services_rendered < 0:
        return None
    return max(0, round(advance_paid - services_rendered, 2))


def is_insurance_valid(insurance, patient_id, treatment_type):
    """Check if patient insurance covers a treatment."""
    if patient_id not in insurance:
        return False
    policy = insurance[patient_id]
    return treatment_type in policy.get("covered_treatments", []) and policy.get("active", False)


def calculate_co_payment(bill, co_pay_percent):
    """Calculate patient's co-payment amount."""
    if bill < 0 or co_pay_percent < 0 or co_pay_percent > 100:
        return None
    return round(bill * (co_pay_percent / 100), 2)


def generate_bill_summary(patient_id, items):
    """Generate a structured bill summary."""
    total = sum(v for v in items.values() if v is not None and v >= 0)
    return {
        "patient_id": patient_id,
        "items": items,
        "subtotal": round(total, 2),
        "vat": calculate_vat(total),
        "grand_total": round(total + (calculate_vat(total) or 0), 2),
    }


def calculate_package_discount(bill, package_name):
    """Apply package discount to bill."""
    packages = {"maternity": 15, "cardiac_care": 10, "cancer_care": 20, "wellness": 5}
    if package_name not in packages:
        return None
    return apply_discount(bill, packages[package_name], package_name)
