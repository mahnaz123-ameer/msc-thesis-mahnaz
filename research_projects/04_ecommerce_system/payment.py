# =============================================================
# payment.py — Payment Processing (Card, bKash, COD, Refunds)
# E-Commerce System
# =============================================================


def process_card_payment(payments, payment_id, order_id, amount, card_last4):
    """Process a card payment."""
    if payment_id in payments:
        return False, "Payment ID already exists"
    if amount <= 0:
        return False, "Invalid amount"
    if len(str(card_last4)) != 4:
        return False, "Invalid card digits"
    payments[payment_id] = {
        "order_id": order_id, "amount": amount,
        "method": "card", "status": "completed",
        "card_last4": card_last4,
    }
    return True, "Card payment successful"


def process_bkash_payment(payments, payment_id, order_id, amount, phone):
    """Process a bKash mobile payment."""
    if payment_id in payments:
        return False, "Payment ID already exists"
    if amount <= 0:
        return False, "Invalid amount"
    if len(str(phone)) != 11:
        return False, "Invalid bKash number"
    payments[payment_id] = {
        "order_id": order_id, "amount": amount,
        "method": "bkash", "status": "completed",
        "phone": phone,
    }
    return True, "bKash payment successful"


def process_cod_payment(payments, payment_id, order_id, amount):
    """Register cash on delivery payment."""
    if payment_id in payments:
        return False, "Payment ID already exists"
    if amount <= 0:
        return False, "Invalid amount"
    payments[payment_id] = {
        "order_id": order_id, "amount": amount,
        "method": "cod", "status": "pending",
    }
    return True, "COD registered"


def confirm_cod_payment(payments, payment_id):
    """Confirm COD payment has been collected."""
    if payment_id not in payments:
        return False, "Payment not found"
    if payments[payment_id]["method"] != "cod":
        return False, "Not a COD payment"
    if payments[payment_id]["status"] == "completed":
        return False, "Already confirmed"
    payments[payment_id]["status"] = "completed"
    return True, "COD payment confirmed"


def process_refund(payments, payment_id, refund_amount, reason=""):
    """Process a refund for a payment."""
    if payment_id not in payments:
        return False, "Payment not found"
    if payments[payment_id]["status"] != "completed":
        return False, "Can only refund completed payments"
    if refund_amount <= 0 or refund_amount > payments[payment_id]["amount"]:
        return False, "Invalid refund amount"
    payments[payment_id]["refund"] = refund_amount
    payments[payment_id]["refund_reason"] = reason
    payments[payment_id]["status"] = "refunded"
    return True, f"Refund of {refund_amount} processed"


def calculate_tax(subtotal, tax_rate=5):
    """Calculate tax on order."""
    if subtotal < 0 or tax_rate < 0:
        return None
    return round(subtotal * (tax_rate / 100), 2)


def calculate_platform_fee(subtotal, fee_percent=1.5):
    """Calculate platform processing fee."""
    if subtotal < 0:
        return None
    return round(subtotal * (fee_percent / 100), 2)


def calculate_cashback(amount, cashback_percent, max_cashback=100):
    """Calculate cashback on payment."""
    if amount <= 0 or cashback_percent <= 0:
        return 0
    cashback = amount * (cashback_percent / 100)
    return round(min(cashback, max_cashback), 2)


def validate_payment_amount(expected, received, tolerance=0.01):
    """Validate received payment matches expected amount."""
    return abs(expected - received) <= tolerance


def get_payment_by_order(payments, order_id):
    """Get payment record for an order."""
    for pid, payment in payments.items():
        if payment["order_id"] == order_id:
            return pid, payment
    return None, None


def get_total_revenue_by_method(payments, method):
    """Get total revenue from a payment method."""
    return round(sum(p["amount"] for p in payments.values()
                    if p["method"] == method and p["status"] == "completed"), 2)


def is_payment_complete(payments, payment_id):
    """Check if payment is completed."""
    if payment_id not in payments:
        return False
    return payments[payment_id]["status"] == "completed"


def get_failed_payments(payments):
    """Get all failed payments."""
    return {pid: p for pid, p in payments.items() if p["status"] == "failed"}


def calculate_installment_amount(total, num_installments, interest_rate=0):
    """Calculate installment amount for EMI payment."""
    if total <= 0 or num_installments <= 0:
        return None
    if interest_rate == 0:
        return round(total / num_installments, 2)
    monthly_rate = interest_rate / 100 / 12
    emi = total * monthly_rate / (1 - (1 + monthly_rate) ** (-num_installments))
    return round(emi, 2)


def apply_wallet_balance(wallets, user_id, amount):
    """Apply wallet balance toward payment."""
    if user_id not in wallets:
        return 0, amount
    wallet_balance = wallets[user_id]
    used = min(wallet_balance, amount)
    wallets[user_id] -= used
    remaining = round(amount - used, 2)
    return round(used, 2), remaining
