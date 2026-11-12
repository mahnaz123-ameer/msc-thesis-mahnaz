# =============================================================
# account.py — Bank Account Management
# Banking System
# =============================================================


def create_account(accounts, account_id, name, account_type="savings", initial_deposit=0):
    """Create a new bank account."""
    if account_id in accounts:
        return False, "Account already exists"
    if initial_deposit < 0:
        return False, "Initial deposit cannot be negative"
    valid_types = ["savings", "current", "fixed_deposit", "student"]
    if account_type not in valid_types:
        return False, "Invalid account type"
    min_deposit = {"savings": 500, "current": 1000, "fixed_deposit": 5000, "student": 0}
    if initial_deposit < min_deposit[account_type]:
        return False, f"Minimum deposit for {account_type} is {min_deposit[account_type]}"
    accounts[account_id] = {
        "name": name,
        "type": account_type,
        "balance": initial_deposit,
        "active": True,
        "frozen": False,
        "transactions": [],
    }
    return True, "Account created"


def close_account(accounts, account_id):
    """Close a bank account."""
    if account_id not in accounts:
        return False, "Account not found"
    if not accounts[account_id]["active"]:
        return False, "Account already closed"
    if accounts[account_id]["balance"] > 0:
        return False, "Please withdraw remaining balance before closing"
    accounts[account_id]["active"] = False
    return True, "Account closed"


def freeze_account(accounts, account_id, reason="Suspicious activity"):
    """Freeze an account to prevent transactions."""
    if account_id not in accounts:
        return False, "Account not found"
    if accounts[account_id]["frozen"]:
        return False, "Account already frozen"
    accounts[account_id]["frozen"] = True
    return True, f"Account frozen: {reason}"


def unfreeze_account(accounts, account_id):
    """Unfreeze a previously frozen account."""
    if account_id not in accounts:
        return False, "Account not found"
    if not accounts[account_id]["frozen"]:
        return False, "Account is not frozen"
    accounts[account_id]["frozen"] = False
    return True, "Account unfrozen"


def get_balance(accounts, account_id):
    """Get current balance of an account."""
    if account_id not in accounts:
        return None
    if not accounts[account_id]["active"]:
        return None
    return accounts[account_id]["balance"]


def deposit(accounts, account_id, amount):
    """Deposit money into an account."""
    if account_id not in accounts:
        return False, "Account not found"
    if not accounts[account_id]["active"]:
        return False, "Account is closed"
    if accounts[account_id]["frozen"]:
        return False, "Account is frozen"
    if amount <= 0:
        return False, "Deposit amount must be positive"
    accounts[account_id]["balance"] += amount
    accounts[account_id]["transactions"].append(("deposit", amount))
    return True, f"Deposited {amount}"


def withdraw(accounts, account_id, amount):
    """Withdraw money from an account."""
    if account_id not in accounts:
        return False, "Account not found"
    if not accounts[account_id]["active"]:
        return False, "Account is closed"
    if accounts[account_id]["frozen"]:
        return False, "Account is frozen"
    if amount <= 0:
        return False, "Withdrawal amount must be positive"
    if accounts[account_id]["balance"] < amount:
        return False, "Insufficient balance"
    accounts[account_id]["balance"] -= amount
    accounts[account_id]["transactions"].append(("withdrawal", amount))
    return True, f"Withdrawn {amount}"


def transfer(accounts, from_id, to_id, amount):
    """Transfer money between two accounts."""
    if from_id not in accounts or to_id not in accounts:
        return False, "Account not found"
    if not accounts[from_id]["active"] or not accounts[to_id]["active"]:
        return False, "One or both accounts are closed"
    if accounts[from_id]["frozen"]:
        return False, "Sender account is frozen"
    if amount <= 0:
        return False, "Transfer amount must be positive"
    if accounts[from_id]["balance"] < amount:
        return False, "Insufficient balance"
    accounts[from_id]["balance"] -= amount
    accounts[to_id]["balance"] += amount
    accounts[from_id]["transactions"].append(("transfer_out", amount))
    accounts[to_id]["transactions"].append(("transfer_in", amount))
    return True, "Transfer successful"


def check_minimum_balance(accounts, account_id):
    """Check if account meets its minimum balance requirement."""
    if account_id not in accounts:
        return False
    minimums = {"savings": 500, "current": 1000, "fixed_deposit": 5000, "student": 0}
    acc = accounts[account_id]
    return acc["balance"] >= minimums.get(acc["type"], 0)


def is_account_active(accounts, account_id):
    """Check if account is active."""
    if account_id not in accounts:
        return False
    return accounts[account_id]["active"]


def is_account_frozen(accounts, account_id):
    """Check if account is frozen."""
    if account_id not in accounts:
        return False
    return accounts[account_id]["frozen"]


def get_transaction_count(accounts, account_id):
    """Get number of transactions made on an account."""
    if account_id not in accounts:
        return 0
    return len(accounts[account_id]["transactions"])


def get_account_type(accounts, account_id):
    """Get account type."""
    if account_id not in accounts:
        return None
    return accounts[account_id]["type"]


def get_all_active_accounts(accounts):
    """Return all active accounts."""
    return {aid: info for aid, info in accounts.items() if info["active"]}


def calculate_total_deposits(accounts):
    """Calculate total deposits across all active accounts."""
    return sum(info["balance"] for info in accounts.values() if info["active"])
