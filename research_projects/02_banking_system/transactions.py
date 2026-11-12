# =============================================================
# transactions.py — Transaction Processing and History
# Banking System
# =============================================================


def add_transaction(history, account_id, txn_type, amount, description=""):
    """Add a transaction record."""
    if account_id not in history:
        history[account_id] = []
    if amount <= 0:
        return False, "Amount must be positive"
    history[account_id].append({
        "type": txn_type,
        "amount": amount,
        "description": description,
    })
    return True, "Transaction recorded"


def get_transaction_history(history, account_id):
    """Get full transaction history for an account."""
    return history.get(account_id, [])


def get_last_n_transactions(history, account_id, n=10):
    """Get last N transactions for an account."""
    txns = history.get(account_id, [])
    return txns[-n:]


def calculate_total_credits(history, account_id):
    """Calculate total amount credited to account."""
    txns = history.get(account_id, [])
    return sum(t["amount"] for t in txns if t["type"] in ("deposit", "transfer_in", "credit"))


def calculate_total_debits(history, account_id):
    """Calculate total amount debited from account."""
    txns = history.get(account_id, [])
    return sum(t["amount"] for t in txns if t["type"] in ("withdrawal", "transfer_out", "debit"))


def get_largest_transaction(history, account_id):
    """Get the largest single transaction."""
    txns = history.get(account_id, [])
    if not txns:
        return None
    return max(txns, key=lambda t: t["amount"])


def get_transactions_by_type(history, account_id, txn_type):
    """Filter transactions by type."""
    txns = history.get(account_id, [])
    return [t for t in txns if t["type"] == txn_type]


def get_transaction_count(history, account_id):
    """Get total number of transactions."""
    return len(history.get(account_id, []))


def calculate_average_transaction(history, account_id):
    """Calculate average transaction amount."""
    txns = history.get(account_id, [])
    if not txns:
        return 0.0
    return round(sum(t["amount"] for t in txns) / len(txns), 2)


def check_daily_limit(history, account_id, new_amount, daily_limit=50000):
    """Check if a new transaction would exceed daily limit."""
    txns = history.get(account_id, [])
    today_total = sum(t["amount"] for t in txns if t["type"] in ("withdrawal", "transfer_out"))
    return (today_total + new_amount) <= daily_limit


def is_suspicious_transaction(amount, account_avg, threshold_multiplier=10):
    """Flag if a transaction is unusually large compared to account average."""
    if account_avg <= 0:
        return False
    return amount > (account_avg * threshold_multiplier)


def calculate_monthly_spending(history, account_id):
    """Calculate total spending (debits) this month."""
    txns = history.get(account_id, [])
    return sum(t["amount"] for t in txns if t["type"] in ("withdrawal", "transfer_out", "debit"))


def reverse_transaction(history, account_id, txn_index):
    """Reverse a transaction by index (adds reversal entry)."""
    txns = history.get(account_id, [])
    if txn_index < 0 or txn_index >= len(txns):
        return False, "Transaction not found"
    original = txns[txn_index]
    reversal_type = "credit" if original["type"] in ("debit", "withdrawal") else "debit"
    history[account_id].append({
        "type": reversal_type,
        "amount": original["amount"],
        "description": f"Reversal of transaction {txn_index}",
    })
    return True, "Transaction reversed"


def generate_statement_summary(history, account_id):
    """Generate a summary of account statement."""
    total_credits = calculate_total_credits(history, account_id)
    total_debits = calculate_total_debits(history, account_id)
    txn_count = get_transaction_count(history, account_id)
    return {
        "total_credits": total_credits,
        "total_debits": total_debits,
        "net_flow": round(total_credits - total_debits, 2),
        "transaction_count": txn_count,
    }
