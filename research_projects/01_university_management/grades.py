# =============================================================
# grades.py — Grade, GPA and Academic Performance Management
# University Management System
# =============================================================


def assign_letter_grade(marks):
    """Assign letter grade based on marks (0-100)."""
    if marks is None or marks < 0 or marks > 100:
        return None
    if marks >= 80: return "A+"
    elif marks >= 75: return "A"
    elif marks >= 70: return "A-"
    elif marks >= 65: return "B+"
    elif marks >= 60: return "B"
    elif marks >= 55: return "B-"
    elif marks >= 50: return "C+"
    elif marks >= 45: return "C"
    elif marks >= 40: return "D"
    else: return "F"


def assign_grade_point(marks):
    """Return grade point (0.0 to 4.0) for given marks."""
    if marks is None or marks < 0 or marks > 100:
        return None
    if marks >= 80: return 4.0
    elif marks >= 75: return 3.75
    elif marks >= 70: return 3.5
    elif marks >= 65: return 3.25
    elif marks >= 60: return 3.0
    elif marks >= 55: return 2.75
    elif marks >= 50: return 2.5
    elif marks >= 45: return 2.25
    elif marks >= 40: return 2.0
    else: return 0.0


def is_passing(marks):
    """Check if marks are passing (>= 40)."""
    if marks is None:
        return False
    return marks >= 40


def is_failing(marks):
    """Check if marks are failing (< 40)."""
    if marks is None:
        return True
    return marks < 40


def calculate_sgpa(courses):
    """
    Calculate Semester GPA from list of (marks, credit_hours).
    Example: [(85, 3), (70, 4), (60, 2)]
    """
    if not courses:
        return 0.0
    total_points = 0.0
    total_credits = 0
    for marks, credits in courses:
        gp = assign_grade_point(marks)
        if gp is None or credits <= 0:
            return None
        total_points += gp * credits
        total_credits += credits
    if total_credits == 0:
        return 0.0
    return round(total_points / total_credits, 2)


def calculate_cgpa(all_semesters):
    """
    Calculate Cumulative GPA across all semesters.
    all_semesters: list of lists of (marks, credit_hours)
    """
    if not all_semesters:
        return 0.0
    all_courses = [course for semester in all_semesters for course in semester]
    return calculate_sgpa(all_courses)


def calculate_class_average(marks_list):
    """Calculate average marks for a class."""
    if not marks_list:
        return 0.0
    return round(sum(marks_list) / len(marks_list), 2)


def get_highest_marks(marks_list):
    """Return highest marks in the class."""
    if not marks_list:
        return None
    return max(marks_list)


def get_lowest_marks(marks_list):
    """Return lowest marks in the class."""
    if not marks_list:
        return None
    return min(marks_list)


def count_failed_students(marks_list):
    """Count students who failed (marks < 40)."""
    return sum(1 for m in marks_list if m < 40)


def count_passed_students(marks_list):
    """Count students who passed (marks >= 40)."""
    return sum(1 for m in marks_list if m >= 40)


def calculate_pass_rate(marks_list):
    """Calculate pass rate percentage."""
    if not marks_list:
        return 0.0
    passed = count_passed_students(marks_list)
    return round((passed / len(marks_list)) * 100, 2)


def get_grade_distribution(marks_list):
    """Return count of each letter grade."""
    distribution = {"A+": 0, "A": 0, "A-": 0, "B+": 0, "B": 0,
                    "B-": 0, "C+": 0, "C": 0, "D": 0, "F": 0}
    for m in marks_list:
        grade = assign_letter_grade(m)
        if grade:
            distribution[grade] += 1
    return distribution


def calculate_rank(marks_list, student_marks):
    """Calculate rank of a student in class."""
    if not marks_list or student_marks not in marks_list:
        return None
    sorted_marks = sorted(marks_list, reverse=True)
    return sorted_marks.index(student_marks) + 1


def is_first_class(cgpa):
    """Check if CGPA qualifies for first class honours (>= 3.5)."""
    return cgpa >= 3.5


def is_second_class(cgpa):
    """Check if CGPA qualifies for second class (>= 3.0)."""
    return 3.0 <= cgpa < 3.5


def is_eligible_for_scholarship(cgpa, attendance_percent):
    """Check scholarship eligibility: CGPA >= 3.75 and attendance >= 90%."""
    return cgpa >= 3.75 and attendance_percent >= 90


def is_on_probation(cgpa):
    """Check if student is on academic probation (CGPA < 2.0)."""
    return cgpa < 2.0


def calculate_marks_needed_to_pass(current_marks, total_marks, passing_percent=40):
    """Calculate marks needed in remaining assessment to pass overall."""
    passing_total = total_marks * (passing_percent / 100)
    needed = passing_total - current_marks
    return max(0, round(needed, 2))


def is_eligible_for_retake(marks, max_retakes, retake_count):
    """Check if student is eligible to retake an exam."""
    if marks >= 40:
        return False, "Student already passed"
    if retake_count >= max_retakes:
        return False, "Maximum retakes reached"
    return True, "Eligible for retake"


def calculate_weighted_average(assessments):
    """
    Calculate weighted average.
    assessments: list of (marks, weight_percent)
    Example: [(80, 30), (70, 70)] = 30% midterm + 70% final
    """
    if not assessments:
        return 0.0
    total_weight = sum(w for _, w in assessments)
    if total_weight != 100:
        return None
    return round(sum(m * (w / 100) for m, w in assessments), 2)
