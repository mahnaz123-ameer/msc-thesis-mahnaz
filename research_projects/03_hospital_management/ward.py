# =============================================================
# ward.py — Ward and Bed Management
# Hospital Management System
# =============================================================


def add_ward(wards, ward_id, name, ward_type, total_beds):
    """Add a ward to the hospital."""
    if ward_id in wards:
        return False, "Ward already exists"
    if total_beds <= 0:
        return False, "Total beds must be positive"
    wards[ward_id] = {
        "name": name, "type": ward_type,
        "total_beds": total_beds, "occupied_beds": 0,
        "patients": [], "active": True,
    }
    return True, "Ward added"


def assign_bed(wards, ward_id, patient_id):
    """Assign a bed to a patient in a ward."""
    if ward_id not in wards:
        return False, "Ward not found"
    if not wards[ward_id]["active"]:
        return False, "Ward is not active"
    if wards[ward_id]["occupied_beds"] >= wards[ward_id]["total_beds"]:
        return False, "No beds available"
    if patient_id in wards[ward_id]["patients"]:
        return False, "Patient already in this ward"
    wards[ward_id]["patients"].append(patient_id)
    wards[ward_id]["occupied_beds"] += 1
    return True, "Bed assigned"


def release_bed(wards, ward_id, patient_id):
    """Release a bed when patient leaves."""
    if ward_id not in wards:
        return False, "Ward not found"
    if patient_id not in wards[ward_id]["patients"]:
        return False, "Patient not in this ward"
    wards[ward_id]["patients"].remove(patient_id)
    wards[ward_id]["occupied_beds"] -= 1
    return True, "Bed released"


def transfer_patient(wards, from_ward_id, to_ward_id, patient_id):
    """Transfer patient from one ward to another."""
    if from_ward_id not in wards or to_ward_id not in wards:
        return False, "Ward not found"
    if patient_id not in wards[from_ward_id]["patients"]:
        return False, "Patient not in source ward"
    if wards[to_ward_id]["occupied_beds"] >= wards[to_ward_id]["total_beds"]:
        return False, "No beds available in target ward"
    release_bed(wards, from_ward_id, patient_id)
    assign_bed(wards, to_ward_id, patient_id)
    return True, f"Patient transferred to {to_ward_id}"


def get_available_beds(wards, ward_id):
    """Get number of available beds in a ward."""
    if ward_id not in wards:
        return 0
    return wards[ward_id]["total_beds"] - wards[ward_id]["occupied_beds"]


def get_occupancy_rate(wards, ward_id):
    """Calculate occupancy rate of a ward."""
    if ward_id not in wards:
        return None
    w = wards[ward_id]
    if w["total_beds"] == 0:
        return 0.0
    return round((w["occupied_beds"] / w["total_beds"]) * 100, 2)


def is_ward_full(wards, ward_id):
    """Check if ward is at full capacity."""
    if ward_id not in wards:
        return False
    w = wards[ward_id]
    return w["occupied_beds"] >= w["total_beds"]


def get_patients_in_ward(wards, ward_id):
    """Get list of patients in a ward."""
    if ward_id not in wards:
        return []
    return wards[ward_id]["patients"]


def get_all_available_wards(wards):
    """Get all wards with at least one available bed."""
    return {wid: w for wid, w in wards.items()
            if w["active"] and w["occupied_beds"] < w["total_beds"]}


def get_wards_by_type(wards, ward_type):
    """Get all wards of a specific type."""
    return {wid: w for wid, w in wards.items()
            if w["type"].lower() == ward_type.lower()}


def calculate_total_hospital_capacity(wards):
    """Calculate total bed capacity across all wards."""
    return sum(w["total_beds"] for w in wards.values() if w["active"])


def calculate_total_occupied_beds(wards):
    """Calculate total occupied beds across all wards."""
    return sum(w["occupied_beds"] for w in wards.values())


def calculate_hospital_occupancy_rate(wards):
    """Calculate overall hospital occupancy rate."""
    total = calculate_total_hospital_capacity(wards)
    if total == 0:
        return 0.0
    occupied = calculate_total_occupied_beds(wards)
    return round((occupied / total) * 100, 2)


def deactivate_ward(wards, ward_id):
    """Deactivate a ward (e.g. for maintenance)."""
    if ward_id not in wards:
        return False, "Ward not found"
    if wards[ward_id]["occupied_beds"] > 0:
        return False, "Cannot deactivate ward with patients"
    wards[ward_id]["active"] = False
    return True, "Ward deactivated"


def increase_ward_capacity(wards, ward_id, additional_beds):
    """Increase total bed capacity of a ward."""
    if ward_id not in wards:
        return False, "Ward not found"
    if additional_beds <= 0:
        return False, "Must add at least 1 bed"
    wards[ward_id]["total_beds"] += additional_beds
    return True, f"{additional_beds} beds added"
