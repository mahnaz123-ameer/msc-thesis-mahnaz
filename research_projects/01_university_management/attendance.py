# =============================================================
# attendance.py — Attendance Tracking and Eligibility
# University Management System
# =============================================================


def mark_present(records, student_id, course_id, date):
    """Mark a student as present for a course on a date."""
    if student_id not in records:
        records[student_id] = {}
    if course_id not in records[student_id]:
        records[student_id][course_id] = {}
    records[student_id][course_id][date] = "present"
    return True


def mark_absent(records, student_id, course_id, date):
    """Mark a student as absent for a course on a date."""
    if student_id not in records:
        records[student_id] = {}
    if course_id not in records[student_id]:
        records[student_id][course_id] = {}
    records[student_id][course_id][date] = "absent"
    return True


def mark_late(records, student_id, course_id, date):
    """Mark a student as late for a course on a date."""
    if student_id not in records:
        records[student_id] = {}
    if course_id not in records[student_id]:
        records[student_id][course_id] = {}
    records[student_id][course_id][date] = "late"
    return True


def calculate_attendance_percentage(records, student_id, course_id):
    """Calculate attendance percentage for a student in a course."""
    if student_id not in records:
        return 0.0
    if course_id not in records[student_id]:
        return 0.0
    classes = records[student_id][course_id]
    total = len(classes)
    if total == 0:
        return 0.0
    present = sum(1 for s in classes.values() if s in ("present", "late"))
    return round((present / total) * 100, 2)


def is_eligible_for_exam(records, student_id, course_id, min_percent=75):
    """Check if student meets minimum attendance to sit exam."""
    pct = calculate_attendance_percentage(records, student_id, course_id)
    return pct >= min_percent


def get_absent_dates(records, student_id, course_id):
    """Return list of dates a student was absent from a course."""
    if student_id not in records or course_id not in records[student_id]:
        return []
    return [d for d, s in records[student_id][course_id].items() if s == "absent"]


def get_present_count(records, student_id, course_id):
    """Return total classes attended by a student in a course."""
    if student_id not in records or course_id not in records[student_id]:
        return 0
    return sum(1 for s in records[student_id][course_id].values() if s in ("present", "late"))


def get_total_classes(records, student_id, course_id):
    """Return total classes held for a course."""
    if student_id not in records or course_id not in records[student_id]:
        return 0
    return len(records[student_id][course_id])


def get_absent_students_on_date(records, course_id, date):
    """Return list of student IDs absent on a specific date."""
    absent = []
    for sid, courses in records.items():
        if course_id in courses and courses[course_id].get(date) == "absent":
            absent.append(sid)
    return absent


def calculate_shortage(records, student_id, course_id, min_percent=75):
    """Calculate how many more classes student must attend to be eligible."""
    if student_id not in records or course_id not in records[student_id]:
        return 0
    total = get_total_classes(records, student_id, course_id)
    present = get_present_count(records, student_id, course_id)
    required = (min_percent / 100) * total
    shortage = required - present
    return max(0, round(shortage))


def get_students_below_threshold(records, course_id, min_percent=75):
    """Return list of students below attendance threshold in a course."""
    below = []
    for sid in records:
        pct = calculate_attendance_percentage(records, sid, course_id)
        if pct < min_percent:
            below.append((sid, pct))
    return below


def get_overall_attendance(records, student_id):
    """Calculate overall attendance percentage across all courses."""
    if student_id not in records:
        return 0.0
    total_classes = 0
    total_present = 0
    for course_id in records[student_id]:
        total_classes += get_total_classes(records, student_id, course_id)
        total_present += get_present_count(records, student_id, course_id)
    if total_classes == 0:
        return 0.0
    return round((total_present / total_classes) * 100, 2)


def get_course_attendance_summary(records, course_id):
    """Get attendance summary statistics for a course."""
    percentages = []
    for sid in records:
        if course_id in records[sid]:
            pct = calculate_attendance_percentage(records, sid, course_id)
            percentages.append(pct)
    if not percentages:
        return {}
    return {
        "total_students": len(percentages),
        "average_attendance": round(sum(percentages) / len(percentages), 2),
        "highest": max(percentages),
        "lowest": min(percentages),
        "eligible_count": sum(1 for p in percentages if p >= 75),
    }


def has_consecutive_absences(records, student_id, course_id, threshold=3):
    """Check if student has more than threshold consecutive absences."""
    if student_id not in records or course_id not in records[student_id]:
        return False
    dates_sorted = sorted(records[student_id][course_id].keys())
    consecutive = 0
    for date in dates_sorted:
        if records[student_id][course_id][date] == "absent":
            consecutive += 1
            if consecutive >= threshold:
                return True
        else:
            consecutive = 0
    return False
