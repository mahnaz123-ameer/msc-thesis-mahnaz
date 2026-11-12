# =============================================================
# fraud.py — Fraud Detection and Security
# Banking System
# =============================================================


def check_transaction_velocity(transactions, account_id, time_window_minutes=10, max_count=5):
    """Flag if too many transactions in short time."""
    recent = transactions.get(account_id, [])[-max_count:]
    return len(recent) >= max_count


def is_amount_anomalous(amount, account_average, multiplier=5):
    """Flag transaction if amount is unusually high."""
    if account_average <= 0:
        return False
    return amount > account_average * multiplier


def check_location_mismatch(last_country, current_country):
    """Flag if transaction is from unexpected country."""
    return last_country != current_country


def calculate_risk_score(factors):
    """
    Calculate fraud risk score from multiple factors.
    factors: dict with keys: amount_anomaly, velocity, location_mismatch, odd_hour
    Each True = adds to risk score.
    """
    if not factors:
        return 0
    weights = {
        "amount_anomaly": 30,
        "velocity": 25,
        "location_mismatch": 35,
        "odd_hour": 10,
    }
    score = sum(weights.get(k, 0) for k, v in factors.items() if v)
    return min(score, 100)


def should_block_transaction(risk_score, threshold=70):
    """Determine if transaction should be blocked based on risk score."""
    return risk_score >= threshold


def flag_account(accounts, account_id, reason):
    """Flag an account for review."""
    if account_id not in accounts:
        return False, "Account not found"
    accounts[account_id]["flagged"] = True
    accounts[account_id]["flag_reason"] = reason
    return True, f"Account flagged: {reason}"


def unflag_account(accounts, account_id):
    """Remove fraud flag from account."""
    if account_id not in accounts:
        return False, "Account not found"
    accounts[account_id]["flagged"] = False
    accounts[account_id].pop("flag_reason", None)
    return True, "Account unflagged"


def is_account_flagged(accounts, account_id):
    """Check if account is currently flagged."""
    if account_id not in accounts:
        return False
    return accounts[account_id].get("flagged", False)


def lock_account_after_failed_attempts(accounts, account_id, failed_attempts, max_attempts=3):
    """Lock account after too many failed PIN/password attempts."""
    if account_id not in accounts:
        return False, "Account not found"
    if failed_attempts >= max_attempts:
        accounts[account_id]["frozen"] = True
        return True, "Account locked due to multiple failed attempts"
    return False, f"{max_attempts - failed_attempts} attempts remaining"


def validate_pin(stored_pin, entered_pin):
    """Validate entered PIN against stored PIN."""
    if not stored_pin or not entered_pin:
        return False
    return str(stored_pin) == str(entered_pin)


def is_pin_format_valid(pin):
    """Check if PIN meets format requirements (4-6 digits)."""
    pin_str = str(pin)
    return pin_str.isdigit() and 4 <= len(pin_str) <= 6


def detect_round_number_pattern(transactions, threshold=5):
    """Detect suspicious pattern of many round-number transactions."""
    if not transactions:
        return False
    round_count = sum(1 for t in transactions if t["amount"] % 1000 == 0)
    return round_count >= threshold


def check_new_beneficiary_risk(account_id, beneficiary_id, known_beneficiaries):
    """Flag transfers to new/unknown beneficiaries."""
    return beneficiary_id not in known_beneficiaries.get(account_id, [])


def calculate_fraud_probability(risk_score):
    """Convert risk score to fraud probability percentage."""
    if risk_score < 0 or risk_score > 100:
        return None
    return round(risk_score * 0.85, 2)


def generate_fraud_alert(account_id, risk_score, reason):
    """Generate a fraud alert record."""
    if risk_score < 0 or risk_score > 100:
        return None
    severity = "HIGH" if risk_score >= 70 else "MEDIUM" if risk_score >= 40 else "LOW"
    return {
        "account_id": account_id,
        "risk_score": risk_score,
        "severity": severity,
        "reason": reason,
        "action_required": risk_score >= 70,
    }
