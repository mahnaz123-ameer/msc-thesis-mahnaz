# =============================================================
# medicine.py — Medicine Inventory, Dosage and Prescription
# Hospital Management System
# =============================================================


def add_medicine(inventory, med_id, name, category, stock, unit_price, expiry_date):
    """Add medicine to inventory."""
    if med_id in inventory:
        return False, "Medicine already exists"
    if stock < 0 or unit_price <= 0:
        return False, "Invalid stock or price"
    inventory[med_id] = {
        "name": name, "category": category, "stock": stock,
        "unit_price": unit_price, "expiry_date": expiry_date,
        "reorder_level": 50,
    }
    return True, "Medicine added"


def update_stock(inventory, med_id, quantity):
    """Update medicine stock (add or subtract)."""
    if med_id not in inventory:
        return False, "Medicine not found"
    new_stock = inventory[med_id]["stock"] + quantity
    if new_stock < 0:
        return False, "Insufficient stock"
    inventory[med_id]["stock"] = new_stock
    return True, f"Stock updated to {new_stock}"


def dispense_medicine(inventory, med_id, quantity):
    """Dispense medicine to patient."""
    if med_id not in inventory:
        return False, "Medicine not found"
    if inventory[med_id]["stock"] < quantity:
        return False, "Insufficient stock"
    inventory[med_id]["stock"] -= quantity
    return True, "Medicine dispensed"


def check_stock(inventory, med_id):
    """Check current stock of a medicine."""
    if med_id not in inventory:
        return None
    return inventory[med_id]["stock"]


def is_stock_low(inventory, med_id):
    """Check if medicine stock is below reorder level."""
    if med_id not in inventory:
        return False
    return inventory[med_id]["stock"] <= inventory[med_id]["reorder_level"]


def get_low_stock_medicines(inventory):
    """Get all medicines with low stock."""
    return {mid: info for mid, info in inventory.items()
            if info["stock"] <= info["reorder_level"]}


def is_expired(inventory, med_id, today):
    """Check if medicine has expired."""
    if med_id not in inventory:
        return False
    return inventory[med_id]["expiry_date"] < today


def get_expired_medicines(inventory, today):
    """Get all expired medicines."""
    return {mid: info for mid, info in inventory.items()
            if info["expiry_date"] < today}


def get_expiring_soon(inventory, today, days_threshold=30):
    """Get medicines expiring within threshold days."""
    expiring = {}
    for mid, info in inventory.items():
        days_left = (info["expiry_date"] - today).days if hasattr(info["expiry_date"], 'days') else 0
        if 0 <= days_left <= days_threshold:
            expiring[mid] = info
    return expiring


def calculate_dosage(weight_kg, dose_per_kg, frequency_per_day):
    """Calculate daily dosage based on patient weight."""
    if weight_kg <= 0 or dose_per_kg <= 0 or frequency_per_day <= 0:
        return None
    total_daily = weight_kg * dose_per_kg
    per_dose = total_daily / frequency_per_day
    return round(per_dose, 2)


def calculate_medicine_cost(inventory, med_id, quantity):
    """Calculate cost for given quantity of medicine."""
    if med_id not in inventory:
        return None
    if quantity <= 0:
        return None
    return round(inventory[med_id]["unit_price"] * quantity, 2)


def check_drug_interaction(drug_1, drug_2, interaction_db):
    """Check if two drugs have known interactions."""
    pair = tuple(sorted([drug_1, drug_2]))
    return pair in interaction_db


def is_safe_for_allergy(medicine_name, patient_allergies):
    """Check if medicine is safe given patient allergies."""
    if not patient_allergies:
        return True
    medicine_lower = medicine_name.lower()
    return not any(allergy.lower() in medicine_lower for allergy in patient_allergies)


def calculate_total_inventory_value(inventory):
    """Calculate total value of medicine inventory."""
    return round(sum(info["stock"] * info["unit_price"] for info in inventory.values()), 2)


def search_medicine_by_name(inventory, keyword):
    """Search medicines by name keyword."""
    keyword = keyword.lower()
    return {mid: info for mid, info in inventory.items()
            if keyword in info["name"].lower()}


def get_medicines_by_category(inventory, category):
    """Get all medicines in a category."""
    return {mid: info for mid, info in inventory.items()
            if info["category"].lower() == category.lower()}


def set_reorder_level(inventory, med_id, level):
    """Set reorder level for a medicine."""
    if med_id not in inventory:
        return False, "Medicine not found"
    if level < 0:
        return False, "Reorder level cannot be negative"
    inventory[med_id]["reorder_level"] = level
    return True, "Reorder level updated"
