# =============================================================
# interest.py — Interest Calculations for Deposits and Savings
# Banking System
# =============================================================


def calculate_savings_interest(balance, annual_rate_percent, months):
    """Calculate interest earned on savings account."""
    if balance <= 0 or annual_rate_percent <= 0 or months <= 0:
        return None
    monthly_rate = annual_rate_percent / 100 / 12
    return round(balance * monthly_rate * months, 2)


def calculate_fixed_deposit_maturity(principal, annual_rate_percent, years, compounding="quarterly"):
    """Calculate FD maturity amount."""
    if principal <= 0 or annual_rate_percent <= 0 or years <= 0:
        return None
    n_map = {"monthly": 12, "quarterly": 4, "half_yearly": 2, "yearly": 1}
    n = n_map.get(compounding, 4)
    r = annual_rate_percent / 100
    amount = principal * ((1 + r / n) ** (n * years))
    return round(amount, 2)


def calculate_fd_interest_earned(principal, annual_rate_percent, years, compounding="quarterly"):
    """Calculate interest earned on fixed deposit."""
    maturity = calculate_fixed_deposit_maturity(principal, annual_rate_percent, years, compounding)
    if maturity is None:
        return None
    return round(maturity - principal, 2)


def get_fd_rate_by_tenure(tenure_months):
    """Get fixed deposit interest rate based on tenure."""
    if tenure_months < 3:
        return None
    elif tenure_months < 6:
        return 5.5
    elif tenure_months < 12:
        return 6.0
    elif tenure_months < 24:
        return 6.5
    elif tenure_months < 36:
        return 7.0
    else:
        return 7.5


def calculate_recurring_deposit_maturity(monthly_deposit, annual_rate_percent, months):
    """Calculate maturity amount for recurring deposit."""
    if monthly_deposit <= 0 or annual_rate_percent <= 0 or months <= 0:
        return None
    monthly_rate = annual_rate_percent / 100 / 12
    maturity = monthly_deposit * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
    return round(maturity, 2)


def calculate_effective_annual_rate(nominal_rate, compounds_per_year):
    """Calculate Effective Annual Rate (EAR) from nominal rate."""
    if nominal_rate <= 0 or compounds_per_year <= 0:
        return None
    ear = ((1 + nominal_rate / 100 / compounds_per_year) ** compounds_per_year - 1) * 100
    return round(ear, 4)


def calculate_real_interest_rate(nominal_rate, inflation_rate):
    """Calculate real interest rate adjusted for inflation."""
    if nominal_rate is None or inflation_rate is None:
        return None
    real_rate = ((1 + nominal_rate / 100) / (1 + inflation_rate / 100) - 1) * 100
    return round(real_rate, 4)


def calculate_tax_on_interest(interest_earned, tax_rate_percent=10):
    """Calculate tax deducted at source on interest."""
    if interest_earned < 0 or tax_rate_percent < 0:
        return None
    return round(interest_earned * (tax_rate_percent / 100), 2)


def calculate_net_interest(interest_earned, tax_rate_percent=10):
    """Calculate net interest after tax deduction."""
    tax = calculate_tax_on_interest(interest_earned, tax_rate_percent)
    if tax is None:
        return None
    return round(interest_earned - tax, 2)


def calculate_break_even_months(principal, monthly_fee, monthly_interest_rate_percent):
    """Calculate months needed to break even on a fixed deposit after fees."""
    if principal <= 0 or monthly_fee < 0:
        return None
    if monthly_interest_rate_percent <= 0:
        return None
    monthly_interest = principal * (monthly_interest_rate_percent / 100)
    if monthly_interest <= monthly_fee:
        return None
    months = monthly_fee / (monthly_interest - monthly_fee)
    return round(months, 1)


def compare_fd_plans(principal, plans):
    """
    Compare multiple FD plans and return the best one.
    plans: list of (name, rate, years, compounding)
    """
    if not plans or principal <= 0:
        return None
    results = []
    for name, rate, years, compounding in plans:
        maturity = calculate_fixed_deposit_maturity(principal, rate, years, compounding)
        if maturity:
            results.append({"plan": name, "maturity": maturity, "interest": round(maturity - principal, 2)})
    if not results:
        return None
    return max(results, key=lambda x: x["maturity"])


def calculate_penalty_for_early_fd_withdrawal(principal, rate, months_held, penalty_rate=1.0):
    """Calculate penalty for withdrawing FD before maturity."""
    if principal <= 0 or months_held < 0:
        return None
    effective_rate = max(0, rate - penalty_rate)
    interest = principal * (effective_rate / 100 / 12) * months_held
    return round(interest, 2)
