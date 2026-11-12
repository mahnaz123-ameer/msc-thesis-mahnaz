# =============================================================
# courses.py — Course Registration and Credit Management
# University Management System
# =============================================================


def add_course(courses, course_id, name, credits, max_students=40):
    """Add a new course to the system."""
    if course_id in courses:
        return False, "Course already exists"
    if credits <= 0:
        return False, "Credits must be positive"
    if max_students <= 0:
        return False, "Max students must be positive"
    courses[course_id] = {
        "name": name,
        "credits": credits,
        "max_students": max_students,
        "enrolled": [],
        "active": True,
    }
    return True, "Course added"


def remove_course(courses, course_id):
    """Remove a course from the system."""
    if course_id not in courses:
        return False, "Course not found"
    del courses[course_id]
    return True, "Course removed"


def register_student_for_course(courses, student_id, course_id):
    """Register a student for a course."""
    if course_id not in courses:
        return False, "Course not found"
    if not courses[course_id]["active"]:
        return False, "Course is not active"
    if student_id in courses[course_id]["enrolled"]:
        return False, "Student already enrolled"
    if len(courses[course_id]["enrolled"]) >= courses[course_id]["max_students"]:
        return False, "Course is full"
    courses[course_id]["enrolled"].append(student_id)
    return True, "Registered successfully"


def drop_course(courses, student_id, course_id):
    """Drop a student from a course."""
    if course_id not in courses:
        return False, "Course not found"
    if student_id not in courses[course_id]["enrolled"]:
        return False, "Student not enrolled in this course"
    courses[course_id]["enrolled"].remove(student_id)
    return True, "Course dropped"


def get_enrolled_students(courses, course_id):
    """Get list of students enrolled in a course."""
    if course_id not in courses:
        return []
    return courses[course_id]["enrolled"]


def get_student_courses(courses, student_id):
    """Get all courses a student is enrolled in."""
    return [cid for cid, info in courses.items() if student_id in info["enrolled"]]


def count_enrolled(courses, course_id):
    """Count students enrolled in a course."""
    if course_id not in courses:
        return 0
    return len(courses[course_id]["enrolled"])


def is_course_full(courses, course_id):
    """Check if a course is at maximum capacity."""
    if course_id not in courses:
        return False
    c = courses[course_id]
    return len(c["enrolled"]) >= c["max_students"]


def get_available_seats(courses, course_id):
    """Get number of available seats in a course."""
    if course_id not in courses:
        return 0
    c = courses[course_id]
    return c["max_students"] - len(c["enrolled"])


def calculate_total_credit_hours(courses, student_id):
    """Calculate total credit hours a student is enrolled in."""
    student_courses = get_student_courses(courses, student_id)
    return sum(courses[cid]["credits"] for cid in student_courses)


def is_credit_limit_exceeded(total_credits, max_credits=24):
    """Check if student has exceeded maximum credit limit."""
    return total_credits > max_credits


def is_credit_minimum_met(total_credits, min_credits=12):
    """Check if student has minimum required credits for full-time status."""
    return total_credits >= min_credits


def has_time_conflict(schedule, course_id_1, course_id_2):
    """
    Check if two courses have overlapping time slots.
    schedule: {course_id: set of time_slots}
    """
    slots_1 = schedule.get(course_id_1, set())
    slots_2 = schedule.get(course_id_2, set())
    return bool(slots_1 & slots_2)


def get_course_credits(courses, course_id):
    """Get credit hours for a course."""
    if course_id not in courses:
        return None
    return courses[course_id]["credits"]


def deactivate_course(courses, course_id):
    """Deactivate a course so no new registrations are allowed."""
    if course_id not in courses:
        return False, "Course not found"
    courses[course_id]["active"] = False
    return True, "Course deactivated"


def get_active_courses(courses):
    """Return all active courses."""
    return {cid: info for cid, info in courses.items() if info["active"]}


def get_courses_with_seats(courses):
    """Return courses that still have available seats."""
    return {cid: info for cid, info in courses.items()
            if info["active"] and len(info["enrolled"]) < info["max_students"]}


def calculate_course_fill_rate(courses, course_id):
    """Calculate how full a course is as a percentage."""
    if course_id not in courses:
        return None
    c = courses[course_id]
    if c["max_students"] == 0:
        return 0.0
    return round((len(c["enrolled"]) / c["max_students"]) * 100, 2)
