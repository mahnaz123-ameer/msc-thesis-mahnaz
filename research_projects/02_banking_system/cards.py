# =============================================================
# cards.py — Debit and Credit Card Management
# Banking System
# =============================================================


def issue_card(cards, card_id, account_id, card_type="debit", credit_limit=0):
    """Issue a new debit or credit card."""
    if card_id in cards:
        return False, "Card already exists"
    if card_type not in ("debit", "credit"):
        return False, "Invalid card type"
    if card_type == "credit" and credit_limit <= 0:
        return False, "Credit limit required for credit card"
    cards[card_id] = {
        "account_id": account_id,
        "type": card_type,
        "credit_limit": credit_limit,
        "outstanding": 0,
        "active": True,
        "blocked": False,
        "reward_points": 0,
    }
    return True, "Card issued"


def block_card(cards, card_id, reason="Lost/Stolen"):
    """Block a card."""
    if card_id not in cards:
        return False, "Card not found"
    if cards[card_id]["blocked"]:
        return False, "Card already blocked"
    cards[card_id]["blocked"] = True
    return True, f"Card blocked: {reason}"


def unblock_card(cards, card_id):
    """Unblock a card."""
    if card_id not in cards:
        return False, "Card not found"
    if not cards[card_id]["blocked"]:
        return False, "Card is not blocked"
    cards[card_id]["blocked"] = False
    return True, "Card unblocked"


def validate_card(cards, card_id):
    """Check if card is valid for transactions."""
    if card_id not in cards:
        return False, "Card not found"
    if not cards[card_id]["active"]:
        return False, "Card is not active"
    if cards[card_id]["blocked"]:
        return False, "Card is blocked"
    return True, "Card valid"


def get_available_credit(cards, card_id):
    """Get available credit for a credit card."""
    if card_id not in cards:
        return None
    if cards[card_id]["type"] != "credit":
        return None
    return cards[card_id]["credit_limit"] - cards[card_id]["outstanding"]


def make_credit_card_payment(cards, card_id, amount):
    """Pay outstanding credit card balance."""
    if card_id not in cards:
        return False, "Card not found"
    if cards[card_id]["type"] != "credit":
        return False, "Not a credit card"
    if amount <= 0:
        return False, "Invalid amount"
    cards[card_id]["outstanding"] = max(0, cards[card_id]["outstanding"] - amount)
    return True, "Payment processed"


def charge_to_credit_card(cards, card_id, amount):
    """Charge an amount to a credit card."""
    if card_id not in cards:
        return False, "Card not found"
    valid, msg = validate_card(cards, card_id)
    if not valid:
        return False, msg
    if cards[card_id]["type"] != "credit":
        return False, "Not a credit card"
    available = get_available_credit(cards, card_id)
    if amount > available:
        return False, "Insufficient credit limit"
    cards[card_id]["outstanding"] += amount
    return True, "Charge applied"


def calculate_credit_utilization(cards, card_id):
    """Calculate credit utilization percentage."""
    if card_id not in cards:
        return None
    card = cards[card_id]
    if card["type"] != "credit" or card["credit_limit"] == 0:
        return None
    return round((card["outstanding"] / card["credit_limit"]) * 100, 2)


def add_reward_points(cards, card_id, spend_amount, points_per_100=1):
    """Add reward points based on spending."""
    if card_id not in cards:
        return False, "Card not found"
    if spend_amount <= 0:
        return False, "Invalid spend amount"
    points = int(spend_amount / 100) * points_per_100
    cards[card_id]["reward_points"] += points
    return True, f"{points} points added"


def redeem_reward_points(cards, card_id, points, value_per_point=0.25):
    """Redeem reward points for cash value."""
    if card_id not in cards:
        return None
    if points <= 0:
        return None
    if cards[card_id]["reward_points"] < points:
        return None
    cards[card_id]["reward_points"] -= points
    return round(points * value_per_point, 2)


def calculate_minimum_payment(outstanding, min_percent=5, min_amount=500):
    """Calculate minimum monthly payment on credit card."""
    if outstanding <= 0:
        return 0
    calculated = outstanding * (min_percent / 100)
    return max(calculated, min_amount)


def calculate_late_payment_fee(outstanding, fee_percent=2, min_fee=300):
    """Calculate late payment fee on credit card."""
    if outstanding <= 0:
        return 0
    fee = outstanding * (fee_percent / 100)
    return max(fee, min_fee)


def calculate_cash_advance_fee(amount, fee_percent=3, min_fee=250):
    """Calculate fee for cash advance on credit card."""
    if amount <= 0:
        return None
    fee = amount * (fee_percent / 100)
    return max(fee, min_fee)


def upgrade_credit_limit(cards, card_id, new_limit):
    """Upgrade credit limit on a card."""
    if card_id not in cards:
        return False, "Card not found"
    if cards[card_id]["type"] != "credit":
        return False, "Not a credit card"
    if new_limit <= cards[card_id]["credit_limit"]:
        return False, "New limit must be higher than current limit"
    cards[card_id]["credit_limit"] = new_limit
    return True, "Credit limit upgraded"
