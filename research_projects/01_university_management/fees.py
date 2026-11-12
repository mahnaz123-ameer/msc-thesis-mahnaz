# =============================================================
# fees.py — Fee Calculation, Payment and Scholarship Management
# University Management System
# =============================================================


def calculate_tuition_fee(credit_hours, fee_per_credit=5000):
    """Calculate tuition fee based on enrolled credit hours."""
    if credit_hours < 0:
        return None
    return credit_hours * fee_per_credit


def apply_scholarship(fee, scholarship_percent):
    """Apply scholarship percentage discount to a fee."""
    if scholarship_percent < 0 or scholarship_percent > 100:
        return None
    if fee < 0:
        return None
    discount = fee * (scholarship_percent / 100)
    return round(fee - discount, 2)


def calculate_merit_scholarship_percent(cgpa):
    """Calculate scholarship percentage based on CGPA."""
    if cgpa < 0 or cgpa > 4.0:
        return None
    if cgpa >= 3.75:
        return 100
    elif cgpa >= 3.5:
        return 75
    elif cgpa >= 3.25:
        return 50
    elif cgpa >= 3.0:
        return 25
    else:
        return 0


def calculate_late_fine(days_late, fine_per_day=100):
    """Calculate fine for late fee payment."""
    if days_late < 0:
        return None
    return days_late * fine_per_day


def calculate_total_payable(tuition, fine=0, hostel=0, meal=0, other=0):
    """Calculate total amount payable by student."""
    if any(x < 0 for x in [tuition, fine, hostel, meal, other]):
        return None
    return tuition + fine + hostel + meal + other


def record_payment(payments, student_id, amount, semester):
    """Record a fee payment for a student."""
    if amount <= 0:
        return False, "Invalid payment amount"
    if student_id not in payments:
        payments[student_id] = {}
    payments[student_id][semester] = payments[student_id].get(semester, 0) + amount
    return True, "Payment recorded"


def get_outstanding_fee(total_fee, amount_paid):
    """Calculate remaining outstanding fee."""
    if total_fee < 0 or amount_paid < 0:
        return None
    return max(0, round(total_fee - amount_paid, 2))


def is_fee_cleared(total_fee, amount_paid, tolerance=0.01):
    """Check if fee is fully paid within tolerance."""
    outstanding = get_outstanding_fee(total_fee, amount_paid)
    if outstanding is None:
        return False
    return outstanding <= tolerance


def calculate_hostel_fee(months, room_type="single"):
    """Calculate hostel fee based on months and room type."""
    rates = {"single": 8000, "double": 5000, "dormitory": 3000}
    if months < 0:
        return None
    if room_type not in rates:
        return None
    return months * rates[room_type]


def calculate_meal_charges(days, plan="full"):
    """Calculate meal charges for given days and meal plan."""
    plans = {"full": 150, "half": 80, "dinner_only": 50}
    if days < 0:
        return None
    if plan not in plans:
        return None
    return days * plans[plan]


def calculate_library_fine(days_overdue, fine_per_day=10, max_fine=500):
    """Calculate library fine with a maximum cap."""
    if days_overdue < 0:
        return None
    return min(days_overdue * fine_per_day, max_fine)


def is_eligible_for_exam_on_fees(payments, student_id, semester, required_amount):
    """Check if student has paid enough to sit for exam."""
    if student_id not in payments:
        return False
    paid = payments[student_id].get(semester, 0)
    return paid >= required_amount


def calculate_refund(paid_amount, completed_weeks, total_weeks):
    """Calculate refund amount for a student who drops out."""
    if paid_amount < 0 or completed_weeks < 0 or total_weeks <= 0:
        return None
    if completed_weeks >= total_weeks:
        return 0
    refund_percent = (1 - completed_weeks / total_weeks) * 100
    if refund_percent > 75:
        refund_percent = 75
    return round(paid_amount * (refund_percent / 100), 2)


def get_total_collected(payments, semester):
    """Get total fee collected across all students in a semester."""
    total = 0
    for student_payments in payments.values():
        total += student_payments.get(semester, 0)
    return total


def get_defaulters(payments, students, semester, required_amount):
    """Get list of students who have not paid required fee."""
    defaulters = []
    for sid in students:
        paid = payments.get(sid, {}).get(semester, 0)
        if paid < required_amount:
            defaulters.append((sid, paid, required_amount - paid))
    return defaulters
