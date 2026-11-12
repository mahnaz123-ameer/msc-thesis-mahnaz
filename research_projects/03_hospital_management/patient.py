# =============================================================
# patient.py — Patient Registration and Records
# Hospital Management System
# =============================================================


def register_patient(patients, patient_id, name, age, gender, blood_group, phone):
    """Register a new patient."""
    if patient_id in patients:
        return False, "Patient ID already exists"
    if age < 0 or age > 150:
        return False, "Invalid age"
    if gender not in ("Male", "Female", "Other"):
        return False, "Invalid gender"
    valid_blood = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    if blood_group not in valid_blood:
        return False, "Invalid blood group"
    patients[patient_id] = {
        "name": name, "age": age, "gender": gender,
        "blood_group": blood_group, "phone": phone,
        "medical_history": [], "admitted": False,
        "ward": None, "allergies": [],
    }
    return True, "Patient registered"


def discharge_patient(patients, patient_id):
    """Discharge an admitted patient."""
    if patient_id not in patients:
        return False, "Patient not found"
    if not patients[patient_id]["admitted"]:
        return False, "Patient is not admitted"
    patients[patient_id]["admitted"] = False
    patients[patient_id]["ward"] = None
    return True, "Patient discharged"


def admit_patient(patients, patient_id, ward):
    """Admit a patient to a ward."""
    if patient_id not in patients:
        return False, "Patient not found"
    if patients[patient_id]["admitted"]:
        return False, "Patient already admitted"
    patients[patient_id]["admitted"] = True
    patients[patient_id]["ward"] = ward
    return True, f"Patient admitted to {ward}"


def add_medical_history(patients, patient_id, condition):
    """Add a medical condition to patient history."""
    if patient_id not in patients:
        return False, "Patient not found"
    if not condition.strip():
        return False, "Condition cannot be empty"
    patients[patient_id]["medical_history"].append(condition.strip())
    return True, "Medical history updated"


def add_allergy(patients, patient_id, allergy):
    """Record a patient allergy."""
    if patient_id not in patients:
        return False, "Patient not found"
    if allergy in patients[patient_id]["allergies"]:
        return False, "Allergy already recorded"
    patients[patient_id]["allergies"].append(allergy)
    return True, "Allergy recorded"


def has_allergy(patients, patient_id, substance):
    """Check if patient is allergic to a substance."""
    if patient_id not in patients:
        return False
    return substance in patients[patient_id]["allergies"]


def search_patient(patients, patient_id):
    """Find a patient by ID."""
    return patients.get(patient_id, None)


def search_by_name(patients, name):
    """Search patients by name."""
    name = name.lower()
    return {pid: info for pid, info in patients.items() if name in info["name"].lower()}


def get_admitted_patients(patients):
    """Get all currently admitted patients."""
    return {pid: info for pid, info in patients.items() if info["admitted"]}


def get_patients_by_blood_group(patients, blood_group):
    """Get all patients with a specific blood group."""
    return {pid: info for pid, info in patients.items() if info["blood_group"] == blood_group}


def get_patients_by_ward(patients, ward):
    """Get all patients in a specific ward."""
    return {pid: info for pid, info in patients.items() if info.get("ward") == ward}


def calculate_patient_age_group(age):
    """Classify patient into age group."""
    if age < 0:
        return None
    if age < 2:
        return "Infant"
    elif age < 13:
        return "Child"
    elif age < 18:
        return "Adolescent"
    elif age < 60:
        return "Adult"
    else:
        return "Senior"


def update_phone(patients, patient_id, new_phone):
    """Update patient contact number."""
    if patient_id not in patients:
        return False, "Patient not found"
    patients[patient_id]["phone"] = new_phone
    return True, "Phone updated"


def get_total_patients(patients):
    """Get total registered patients."""
    return len(patients)


def get_total_admitted(patients):
    """Get total currently admitted patients."""
    return sum(1 for p in patients.values() if p["admitted"])


def is_patient_admitted(patients, patient_id):
    """Check if a patient is currently admitted."""
    if patient_id not in patients:
        return False
    return patients[patient_id]["admitted"]


def transfer_ward(patients, patient_id, new_ward):
    """Transfer admitted patient to a different ward."""
    if patient_id not in patients:
        return False, "Patient not found"
    if not patients[patient_id]["admitted"]:
        return False, "Patient is not admitted"
    patients[patient_id]["ward"] = new_ward
    return True, f"Transferred to {new_ward}"
