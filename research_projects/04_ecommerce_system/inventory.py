# =============================================================
# inventory.py — Inventory and Stock Management
# E-Commerce System
# =============================================================


def add_stock(inventory, product_id, quantity, warehouse_id="main"):
    """Add stock for a product in a warehouse."""
    if quantity <= 0:
        return False, "Quantity must be positive"
    if product_id not in inventory:
        inventory[product_id] = {}
    inventory[product_id][warehouse_id] = inventory[product_id].get(warehouse_id, 0) + quantity
    return True, f"{quantity} units added"


def remove_stock(inventory, product_id, quantity, warehouse_id="main"):
    """Remove stock after sale or damage."""
    if product_id not in inventory:
        return False, "Product not found"
    current = inventory[product_id].get(warehouse_id, 0)
    if current < quantity:
        return False, "Insufficient stock"
    inventory[product_id][warehouse_id] = current - quantity
    return True, "Stock removed"


def get_total_stock(inventory, product_id):
    """Get total stock across all warehouses."""
    if product_id not in inventory:
        return 0
    return sum(inventory[product_id].values())


def get_stock_in_warehouse(inventory, product_id, warehouse_id):
    """Get stock for a product in a specific warehouse."""
    if product_id not in inventory:
        return 0
    return inventory[product_id].get(warehouse_id, 0)


def transfer_stock(inventory, product_id, from_warehouse, to_warehouse, quantity):
    """Transfer stock between warehouses."""
    if get_stock_in_warehouse(inventory, product_id, from_warehouse) < quantity:
        return False, "Insufficient stock in source warehouse"
    remove_stock(inventory, product_id, quantity, from_warehouse)
    add_stock(inventory, product_id, quantity, to_warehouse)
    return True, "Stock transferred"


def is_in_stock(inventory, product_id, quantity_needed=1):
    """Check if required quantity is available."""
    return get_total_stock(inventory, product_id) >= quantity_needed


def get_low_stock_items(inventory, threshold=10):
    """Get products with total stock below threshold."""
    return {pid: get_total_stock(inventory, pid) for pid in inventory
            if get_total_stock(inventory, pid) <= threshold}


def get_out_of_stock_items(inventory):
    """Get products with zero stock."""
    return [pid for pid in inventory if get_total_stock(inventory, pid) == 0]


def calculate_reorder_quantity(current_stock, reorder_point, max_stock):
    """Calculate how much to reorder."""
    if current_stock >= reorder_point:
        return 0
    return max(0, max_stock - current_stock)


def needs_reorder(current_stock, reorder_point):
    """Check if product needs reordering."""
    return current_stock <= reorder_point


def calculate_stock_value(inventory, product_id, unit_cost):
    """Calculate total value of stock for a product."""
    total_stock = get_total_stock(inventory, product_id)
    return round(total_stock * unit_cost, 2)


def calculate_total_inventory_value(inventory, costs):
    """Calculate total value of all inventory."""
    total = 0
    for pid in inventory:
        cost = costs.get(pid, 0)
        total += get_total_stock(inventory, pid) * cost
    return round(total, 2)


def reserve_stock(reservations, product_id, order_id, quantity):
    """Reserve stock for a pending order."""
    if quantity <= 0:
        return False, "Quantity must be positive"
    if product_id not in reservations:
        reservations[product_id] = {}
    reservations[product_id][order_id] = quantity
    return True, "Stock reserved"


def release_reservation(reservations, product_id, order_id):
    """Release reserved stock (order cancelled)."""
    if product_id not in reservations or order_id not in reservations[product_id]:
        return False, "Reservation not found"
    del reservations[product_id][order_id]
    return True, "Reservation released"


def get_total_reserved(reservations, product_id):
    """Get total reserved quantity for a product."""
    if product_id not in reservations:
        return 0
    return sum(reservations[product_id].values())


def get_available_stock(inventory, reservations, product_id):
    """Get available stock after subtracting reservations."""
    total = get_total_stock(inventory, product_id)
    reserved = get_total_reserved(reservations, product_id)
    return max(0, total - reserved)


def get_warehouse_summary(inventory, warehouse_id):
    """Get all products and their stock in a warehouse."""
    return {pid: wh.get(warehouse_id, 0) for pid, wh in inventory.items()
            if warehouse_id in wh}
