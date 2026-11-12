# =============================================================
# loans.py — Loan Management, EMI and Repayment
# Banking System
# =============================================================


def check_loan_eligibility(monthly_income, existing_debt, credit_score, age):
    """Check if applicant is eligible for a loan."""
    if age < 21 or age > 65:
        return False, "Age must be between 21 and 65"
    if credit_score < 600:
        return False, "Credit score too low (minimum 600)"
    if monthly_income <= 0:
        return False, "Invalid income"
    debt_to_income = (existing_debt / monthly_income) * 100
    if debt_to_income > 50:
        return False, "Debt-to-income ratio too high"
    return True, "Eligible for loan"


def calculate_max_loan_amount(monthly_income, credit_score, loan_type="personal"):
    """Calculate maximum loan amount based on income and credit score."""
    if monthly_income <= 0:
        return None
    multipliers = {"personal": 10, "home": 60, "car": 24, "education": 36}
    base = monthly_income * multipliers.get(loan_type, 10)
    if credit_score >= 750:
        return base * 1.2
    elif credit_score >= 700:
        return base * 1.1
    elif credit_score >= 650:
        return base
    else:
        return base * 0.8


def calculate_simple_interest(principal, rate_percent, years):
    """Calculate simple interest."""
    if principal <= 0 or rate_percent <= 0 or years <= 0:
        return None
    return round(principal * (rate_percent / 100) * years, 2)


def calculate_compound_interest(principal, rate_percent, years, compounds_per_year=12):
    """Calculate compound interest."""
    if principal <= 0 or rate_percent <= 0 or years <= 0:
        return None
    r = rate_percent / 100 / compounds_per_year
    n = compounds_per_year * years
    amount = principal * ((1 + r) ** n)
    return round(amount - principal, 2)


def calculate_emi(principal, annual_rate_percent, tenure_months):
    """Calculate Equated Monthly Installment (EMI)."""
    if principal <= 0 or tenure_months <= 0:
        return None
    if annual_rate_percent == 0:
        return round(principal / tenure_months, 2)
    monthly_rate = annual_rate_percent / 100 / 12
    emi = principal * monthly_rate * ((1 + monthly_rate) ** tenure_months)
    emi /= ((1 + monthly_rate) ** tenure_months - 1)
    return round(emi, 2)


def calculate_total_repayment(emi, tenure_months):
    """Calculate total amount to be repaid."""
    if emi <= 0 or tenure_months <= 0:
        return None
    return round(emi * tenure_months, 2)


def calculate_total_interest_paid(principal, emi, tenure_months):
    """Calculate total interest paid over loan tenure."""
    total = calculate_total_repayment(emi, tenure_months)
    if total is None:
        return None
    return round(total - principal, 2)


def process_repayment(loans, loan_id, amount):
    """Process a loan repayment."""
    if loan_id not in loans:
        return False, "Loan not found"
    if loans[loan_id]["status"] == "closed":
        return False, "Loan already closed"
    if amount <= 0:
        return False, "Invalid repayment amount"
    loans[loan_id]["outstanding"] -= amount
    loans[loan_id]["payments"].append(amount)
    if loans[loan_id]["outstanding"] <= 0:
        loans[loan_id]["outstanding"] = 0
        loans[loan_id]["status"] = "closed"
    return True, "Repayment recorded"


def calculate_outstanding_balance(principal, payments_made):
    """Calculate remaining outstanding loan balance."""
    if principal <= 0:
        return None
    total_paid = sum(payments_made)
    return max(0, round(principal - total_paid, 2))


def calculate_prepayment_penalty(outstanding, penalty_percent=2):
    """Calculate penalty for early loan repayment."""
    if outstanding <= 0:
        return None
    return round(outstanding * (penalty_percent / 100), 2)


def calculate_late_payment_penalty(emi, days_late, penalty_rate=0.02):
    """Calculate penalty for late EMI payment."""
    if emi <= 0 or days_late < 0:
        return None
    return round(emi * penalty_rate * days_late, 2)


def is_loan_overdue(due_date, payment_date):
    """Check if a loan payment is overdue."""
    return payment_date > due_date


def get_loan_summary(principal, annual_rate, tenure_months):
    """Get complete loan summary including EMI, total interest, total repayment."""
    emi = calculate_emi(principal, annual_rate, tenure_months)
    if emi is None:
        return None
    total_repayment = calculate_total_repayment(emi, tenure_months)
    total_interest = calculate_total_interest_paid(principal, emi, tenure_months)
    return {
        "principal": principal,
        "annual_rate": annual_rate,
        "tenure_months": tenure_months,
        "emi": emi,
        "total_repayment": total_repayment,
        "total_interest": total_interest,
    }


def calculate_loan_to_value_ratio(loan_amount, asset_value):
    """Calculate LTV ratio for secured loans."""
    if asset_value <= 0:
        return None
    return round((loan_amount / asset_value) * 100, 2)


def is_ltv_acceptable(ltv_ratio, loan_type="home"):
    """Check if LTV ratio is within acceptable limits."""
    limits = {"home": 80, "car": 85, "personal": 100}
    max_ltv = limits.get(loan_type, 80)
    return ltv_ratio <= max_ltv
