# =============================================================
# student.py — Student Registration and Profile Management
# University Management System
# =============================================================


def add_student(students, student_id, name, age, email, program, year):
    """Add a new student to the system."""
    if student_id in students:
        return False, "Student ID already exists"
    if not name or not name.strip():
        return False, "Name cannot be empty"
    if age < 16 or age > 60:
        return False, "Age must be between 16 and 60"
    if "@" not in email or "." not in email:
        return False, "Invalid email address"
    if year < 1 or year > 6:
        return False, "Year must be between 1 and 6"
    students[student_id] = {
        "name": name.strip(),
        "age": age,
        "email": email.lower(),
        "program": program,
        "year": year,
        "active": True,
        "cgpa": 0.0,
    }
    return True, "Student added successfully"


def remove_student(students, student_id):
    """Remove a student from the system."""
    if student_id not in students:
        return False, "Student not found"
    del students[student_id]
    return True, "Student removed"


def deactivate_student(students, student_id):
    """Deactivate a student account without removing."""
    if student_id not in students:
        return False, "Student not found"
    if not students[student_id]["active"]:
        return False, "Student already inactive"
    students[student_id]["active"] = False
    return True, "Student deactivated"


def reactivate_student(students, student_id):
    """Reactivate a previously deactivated student."""
    if student_id not in students:
        return False, "Student not found"
    if students[student_id]["active"]:
        return False, "Student already active"
    students[student_id]["active"] = True
    return True, "Student reactivated"


def update_student_email(students, student_id, new_email):
    """Update student email address."""
    if student_id not in students:
        return False, "Student not found"
    if "@" not in new_email or "." not in new_email:
        return False, "Invalid email address"
    students[student_id]["email"] = new_email.lower()
    return True, "Email updated"


def update_student_year(students, student_id, new_year):
    """Update student current year of study."""
    if student_id not in students:
        return False, "Student not found"
    if new_year < 1 or new_year > 6:
        return False, "Invalid year"
    students[student_id]["year"] = new_year
    return True, "Year updated"


def search_student_by_id(students, student_id):
    """Search for a student by ID."""
    return students.get(student_id, None)


def search_students_by_name(students, keyword):
    """Search students by partial name match."""
    keyword = keyword.lower()
    return {sid: info for sid, info in students.items()
            if keyword in info["name"].lower()}


def search_students_by_program(students, program):
    """Get all students in a specific program."""
    return {sid: info for sid, info in students.items()
            if info["program"].lower() == program.lower()}


def get_active_students(students):
    """Return all active students."""
    return {sid: info for sid, info in students.items() if info["active"]}


def get_inactive_students(students):
    """Return all inactive students."""
    return {sid: info for sid, info in students.items() if not info["active"]}


def get_students_by_year(students, year):
    """Get all students in a specific year."""
    return {sid: info for sid, info in students.items()
            if info["year"] == year}


def get_total_students(students):
    """Return total number of students."""
    return len(students)


def get_total_active_students(students):
    """Return total number of active students."""
    return sum(1 for s in students.values() if s["active"])


def is_student_registered(students, student_id):
    """Check if a student ID is registered."""
    return student_id in students


def is_student_active(students, student_id):
    """Check if a student is currently active."""
    if student_id not in students:
        return False
    return students[student_id]["active"]


def update_cgpa(students, student_id, cgpa):
    """Update student CGPA record."""
    if student_id not in students:
        return False, "Student not found"
    if cgpa < 0.0 or cgpa > 4.0:
        return False, "CGPA must be between 0.0 and 4.0"
    students[student_id]["cgpa"] = round(cgpa, 2)
    return True, "CGPA updated"


def get_top_students(students, n=10):
    """Return top N students sorted by CGPA."""
    active = get_active_students(students)
    sorted_students = sorted(active.items(), key=lambda x: x[1]["cgpa"], reverse=True)
    return sorted_students[:n]


def transfer_student_program(students, student_id, new_program):
    """Transfer student to a different program."""
    if student_id not in students:
        return False, "Student not found"
    if not new_program.strip():
        return False, "Program name cannot be empty"
    students[student_id]["program"] = new_program.strip()
    return True, "Program transferred"
