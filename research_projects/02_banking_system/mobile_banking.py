# =============================================================
# mobile_banking.py — Mobile Banking, bKash/Nagad Style Transfers
# Banking System
# =============================================================


def send_money(wallets, sender_id, receiver_id, amount):
    """Send money between mobile wallets."""
    if sender_id not in wallets or receiver_id not in wallets:
        return False, "Wallet not found"
    if wallets[sender_id]["balance"] < amount:
        return False, "Insufficient balance"
    if amount <= 0:
        return False, "Amount must be positive"
    if amount > 25000:
        return False, "Exceeds single transaction limit of 25,000"
    fee = calculate_send_money_fee(amount)
    total_deduct = amount + fee
    if wallets[sender_id]["balance"] < total_deduct:
        return False, "Insufficient balance including fee"
    wallets[sender_id]["balance"] -= total_deduct
    wallets[receiver_id]["balance"] += amount
    return True, f"Sent {amount}. Fee: {fee}"


def calculate_send_money_fee(amount):
    """Calculate fee for sending money (bKash-style)."""
    if amount <= 0:
        return None
    if amount <= 1000:
        return 5
    elif amount <= 5000:
        return 10
    elif amount <= 10000:
        return 15
    else:
        return 20


def cash_in(wallets, wallet_id, amount):
    """Add money to mobile wallet (cash in)."""
    if wallet_id not in wallets:
        return False, "Wallet not found"
    if amount <= 0:
        return False, "Invalid amount"
    if amount > 30000:
        return False, "Single cash-in limit is 30,000"
    wallets[wallet_id]["balance"] += amount
    return True, f"Cash in of {amount} successful"


def cash_out(wallets, wallet_id, amount):
    """Withdraw money from mobile wallet (cash out)."""
    if wallet_id not in wallets:
        return False, "Wallet not found"
    if amount <= 0:
        return False, "Invalid amount"
    fee = calculate_cash_out_fee(amount)
    total = amount + fee
    if wallets[wallet_id]["balance"] < total:
        return False, "Insufficient balance"
    wallets[wallet_id]["balance"] -= total
    return True, f"Cash out of {amount} successful. Fee: {fee}"


def calculate_cash_out_fee(amount):
    """Calculate cash out fee (1.85% of amount)."""
    if amount <= 0:
        return None
    return round(amount * 0.0185, 2)


def pay_bill(wallets, wallet_id, biller_id, amount, bill_type="electricity"):
    """Pay utility bill from mobile wallet."""
    if wallet_id not in wallets:
        return False, "Wallet not found"
    if amount <= 0:
        return False, "Invalid bill amount"
    if wallets[wallet_id]["balance"] < amount:
        return False, "Insufficient balance"
    wallets[wallet_id]["balance"] -= amount
    return True, f"{bill_type.capitalize()} bill of {amount} paid to {biller_id}"


def mobile_recharge(wallets, wallet_id, phone_number, amount):
    """Recharge mobile phone from wallet."""
    if wallet_id not in wallets:
        return False, "Wallet not found"
    if amount < 10:
        return False, "Minimum recharge amount is 10"
    if amount > 1000:
        return False, "Maximum recharge amount is 1000"
    if wallets[wallet_id]["balance"] < amount:
        return False, "Insufficient balance"
    if len(str(phone_number)) != 11:
        return False, "Invalid phone number"
    wallets[wallet_id]["balance"] -= amount
    return True, f"Recharged {amount} to {phone_number}"


def get_wallet_balance(wallets, wallet_id):
    """Get current wallet balance."""
    if wallet_id not in wallets:
        return None
    return wallets[wallet_id]["balance"]


def check_daily_send_limit(wallets, wallet_id, new_amount, daily_limit=25000):
    """Check if sending would exceed daily limit."""
    if wallet_id not in wallets:
        return False
    sent_today = wallets[wallet_id].get("sent_today", 0)
    return (sent_today + new_amount) <= daily_limit


def check_monthly_transaction_limit(wallets, wallet_id, daily_limit=200000):
    """Check if wallet is within monthly transaction limits."""
    if wallet_id not in wallets:
        return False
    return wallets[wallet_id].get("monthly_total", 0) <= daily_limit


def calculate_payment_convenience_fee(amount, percent=1.0):
    """Calculate convenience fee for bill payments."""
    if amount <= 0:
        return None
    return round(amount * (percent / 100), 2)


def transfer_to_bank(wallets, wallet_id, bank_account_id, amount):
    """Transfer money from mobile wallet to bank account."""
    if wallet_id not in wallets:
        return False, "Wallet not found"
    if amount < 50:
        return False, "Minimum transfer is 50"
    fee = round(amount * 0.015, 2)
    total = amount + fee
    if wallets[wallet_id]["balance"] < total:
        return False, "Insufficient balance"
    wallets[wallet_id]["balance"] -= total
    return True, f"Transferred {amount} to bank. Fee: {fee}"


def request_money(requests, from_id, to_id, amount, note=""):
    """Send a money request to another wallet user."""
    if amount <= 0:
        return False, "Invalid amount"
    request_id = f"REQ-{from_id}-{to_id}-{amount}"
    requests[request_id] = {
        "from": from_id,
        "to": to_id,
        "amount": amount,
        "note": note,
        "status": "pending",
    }
    return True, f"Money request sent for {amount}"
