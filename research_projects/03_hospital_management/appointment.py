# =============================================================
# appointment.py — Appointment Booking and Scheduling
# Hospital Management System
# =============================================================


def book_appointment(appointments, appt_id, patient_id, doctor_id, date, time_slot, appt_type="consultation"):
    """Book a new appointment."""
    if appt_id in appointments:
        return False, "Appointment ID already exists"
    conflict = check_doctor_conflict(appointments, doctor_id, date, time_slot)
    if conflict:
        return False, "Doctor not available at this time"
    appointments[appt_id] = {
        "patient_id": patient_id, "doctor_id": doctor_id,
        "date": date, "time_slot": time_slot, "type": appt_type,
        "status": "scheduled", "notes": "",
    }
    return True, "Appointment booked"


def cancel_appointment(appointments, appt_id, reason=""):
    """Cancel an appointment."""
    if appt_id not in appointments:
        return False, "Appointment not found"
    if appointments[appt_id]["status"] == "completed":
        return False, "Cannot cancel completed appointment"
    appointments[appt_id]["status"] = "cancelled"
    appointments[appt_id]["cancel_reason"] = reason
    return True, "Appointment cancelled"


def reschedule_appointment(appointments, appt_id, new_date, new_time_slot):
    """Reschedule an existing appointment."""
    if appt_id not in appointments:
        return False, "Appointment not found"
    if appointments[appt_id]["status"] == "completed":
        return False, "Cannot reschedule completed appointment"
    doctor_id = appointments[appt_id]["doctor_id"]
    conflict = check_doctor_conflict(appointments, doctor_id, new_date, new_time_slot, exclude_id=appt_id)
    if conflict:
        return False, "Doctor not available at new time"
    appointments[appt_id]["date"] = new_date
    appointments[appt_id]["time_slot"] = new_time_slot
    appointments[appt_id]["status"] = "rescheduled"
    return True, "Appointment rescheduled"


def complete_appointment(appointments, appt_id, notes=""):
    """Mark an appointment as completed."""
    if appt_id not in appointments:
        return False, "Appointment not found"
    if appointments[appt_id]["status"] == "cancelled":
        return False, "Cannot complete cancelled appointment"
    appointments[appt_id]["status"] = "completed"
    appointments[appt_id]["notes"] = notes
    return True, "Appointment completed"


def check_doctor_conflict(appointments, doctor_id, date, time_slot, exclude_id=None):
    """Check if doctor already has appointment at given time."""
    for appt_id, appt in appointments.items():
        if appt_id == exclude_id:
            continue
        if (appt["doctor_id"] == doctor_id and
                appt["date"] == date and
                appt["time_slot"] == time_slot and
                appt["status"] not in ("cancelled",)):
            return True
    return False


def get_doctor_appointments(appointments, doctor_id, date=None):
    """Get all appointments for a doctor, optionally filtered by date."""
    result = {aid: a for aid, a in appointments.items() if a["doctor_id"] == doctor_id}
    if date:
        result = {aid: a for aid, a in result.items() if a["date"] == date}
    return result


def get_patient_appointments(appointments, patient_id):
    """Get all appointments for a patient."""
    return {aid: a for aid, a in appointments.items() if a["patient_id"] == patient_id}


def get_appointments_by_status(appointments, status):
    """Get all appointments with a specific status."""
    return {aid: a for aid, a in appointments.items() if a["status"] == status}


def get_available_slots(appointments, doctor_id, date, all_slots):
    """Get available time slots for a doctor on a given date."""
    booked = {a["time_slot"] for a in appointments.values()
              if a["doctor_id"] == doctor_id and a["date"] == date
              and a["status"] not in ("cancelled",)}
    return [slot for slot in all_slots if slot not in booked]


def count_appointments_by_doctor(appointments, doctor_id):
    """Count total appointments for a doctor."""
    return sum(1 for a in appointments.values() if a["doctor_id"] == doctor_id)


def count_no_shows(appointments, doctor_id):
    """Count no-show appointments for a doctor."""
    return sum(1 for a in appointments.values()
               if a["doctor_id"] == doctor_id and a["status"] == "no_show")


def calculate_doctor_utilization(appointments, doctor_id, total_slots):
    """Calculate doctor's appointment utilization rate."""
    if total_slots <= 0:
        return 0.0
    booked = count_appointments_by_doctor(appointments, doctor_id)
    return round((booked / total_slots) * 100, 2)


def mark_no_show(appointments, appt_id):
    """Mark an appointment as no-show."""
    if appt_id not in appointments:
        return False, "Appointment not found"
    if appointments[appt_id]["status"] in ("completed", "cancelled"):
        return False, "Invalid status transition"
    appointments[appt_id]["status"] = "no_show"
    return True, "Marked as no-show"


def add_appointment_notes(appointments, appt_id, notes):
    """Add clinical notes to an appointment."""
    if appt_id not in appointments:
        return False, "Appointment not found"
    appointments[appt_id]["notes"] = notes
    return True, "Notes added"


def get_upcoming_appointments(appointments, today):
    """Get all future scheduled appointments from today."""
    return {aid: a for aid, a in appointments.items()
            if a["status"] == "scheduled" and a["date"] >= today}


def get_todays_appointments(appointments, today):
    """Get all appointments scheduled for today."""
    return {aid: a for aid, a in appointments.items() if a["date"] == today}
