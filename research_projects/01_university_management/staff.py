# =============================================================
# staff.py — Staff Payroll, Workload and Evaluation
# University Management System
# =============================================================


def add_staff(staff, staff_id, name, role, basic_salary, department):
    """Add a new staff member."""
    if staff_id in staff:
        return False, "Staff ID already exists"
    if basic_salary <= 0:
        return False, "Salary must be positive"
    staff[staff_id] = {
        "name": name,
        "role": role,
        "basic_salary": basic_salary,
        "department": department,
        "active": True,
    }
    return True, "Staff added"


def remove_staff(staff, staff_id):
    """Remove a staff member."""
    if staff_id not in staff:
        return False, "Staff not found"
    del staff[staff_id]
    return True, "Staff removed"


def calculate_gross_salary(basic_salary, house_allowance_pct=30,
                            medical_allowance_pct=10, transport_allowance=2000):
    """Calculate gross salary including allowances."""
    if basic_salary <= 0:
        return None
    house = basic_salary * (house_allowance_pct / 100)
    medical = basic_salary * (medical_allowance_pct / 100)
    return round(basic_salary + house + medical + transport_allowance, 2)


def calculate_income_tax(gross_salary):
    """Calculate income tax based on gross salary (monthly)."""
    if gross_salary < 0:
        return None
    annual = gross_salary * 12
    if annual <= 300000:
        return 0
    elif annual <= 400000:
        return round(((annual - 300000) * 0.05) / 12, 2)
    elif annual <= 700000:
        return round(((100000 * 0.05) + (annual - 400000) * 0.10) / 12, 2)
    else:
        return round(((100000 * 0.05) + (300000 * 0.10) + (annual - 700000) * 0.15) / 12, 2)


def calculate_provident_fund(basic_salary, pf_percent=10):
    """Calculate provident fund deduction."""
    if basic_salary <= 0:
        return None
    return round(basic_salary * (pf_percent / 100), 2)


def calculate_net_salary(gross_salary, tax, provident_fund, other_deductions=0):
    """Calculate net take-home salary."""
    if any(x < 0 for x in [gross_salary, tax, provident_fund, other_deductions]):
        return None
    return round(gross_salary - tax - provident_fund - other_deductions, 2)


def calculate_overtime_pay(hourly_rate, overtime_hours, multiplier=1.5):
    """Calculate overtime payment."""
    if hourly_rate <= 0 or overtime_hours < 0:
        return None
    return round(hourly_rate * overtime_hours * multiplier, 2)


def calculate_annual_bonus(basic_salary, bonus_months=1):
    """Calculate annual festival bonus."""
    if basic_salary <= 0 or bonus_months <= 0:
        return None
    return basic_salary * bonus_months


def calculate_workload(courses_assigned, credit_hours_per_course):
    """Calculate total teaching workload in credit hours."""
    if not courses_assigned:
        return 0
    return sum(credit_hours_per_course.get(c, 0) for c in courses_assigned)


def is_overloaded(workload, max_workload=18):
    """Check if staff is overloaded."""
    return workload > max_workload


def is_underloaded(workload, min_workload=9):
    """Check if staff has minimum required workload."""
    return workload < min_workload


def calculate_performance_score(ratings):
    """Calculate average performance score from list of ratings (1-10)."""
    if not ratings:
        return 0.0
    valid = [r for r in ratings if 1 <= r <= 10]
    if not valid:
        return None
    return round(sum(valid) / len(valid), 2)


def get_performance_grade(score):
    """Return performance grade based on score."""
    if score is None:
        return None
    if score >= 9:
        return "Outstanding"
    elif score >= 7:
        return "Excellent"
    elif score >= 5:
        return "Good"
    elif score >= 3:
        return "Average"
    else:
        return "Poor"


def calculate_leave_balance(total_leave_days, used_leave_days):
    """Calculate remaining leave balance."""
    if total_leave_days < 0 or used_leave_days < 0:
        return None
    return max(0, total_leave_days - used_leave_days)


def is_leave_eligible(leave_balance, days_requested):
    """Check if staff has enough leave balance."""
    if leave_balance is None or days_requested <= 0:
        return False
    return leave_balance >= days_requested


def get_department_payroll(staff, department):
    """Calculate total monthly payroll for a department."""
    total = 0
    for info in staff.values():
        if info["department"] == department and info["active"]:
            gross = calculate_gross_salary(info["basic_salary"])
            if gross:
                total += gross
    return round(total, 2)


def get_staff_by_department(staff, department):
    """Get all active staff in a department."""
    return {sid: info for sid, info in staff.items()
            if info["department"] == department and info["active"]}
