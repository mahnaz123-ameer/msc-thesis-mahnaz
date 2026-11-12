# =============================================================
# examination.py — Exam Scheduling, Results and Retakes
# University Management System
# =============================================================


def schedule_exam(exams, exam_id, course_id, date, duration_mins, room):
    """Schedule an exam for a course."""
    if exam_id in exams:
        return False, "Exam ID already exists"
    if duration_mins <= 0:
        return False, "Duration must be positive"
    exams[exam_id] = {
        "course_id": course_id,
        "date": date,
        "duration_mins": duration_mins,
        "room": room,
        "results": {},
    }
    return True, "Exam scheduled"


def cancel_exam(exams, exam_id):
    """Cancel a scheduled exam."""
    if exam_id not in exams:
        return False, "Exam not found"
    del exams[exam_id]
    return True, "Exam cancelled"


def record_result(exams, exam_id, student_id, marks):
    """Record exam result for a student."""
    if exam_id not in exams:
        return False, "Exam not found"
    if marks < 0 or marks > 100:
        return False, "Marks must be between 0 and 100"
    exams[exam_id]["results"][student_id] = marks
    return True, "Result recorded"


def get_student_result(exams, exam_id, student_id):
    """Get a student's result for an exam."""
    if exam_id not in exams:
        return None
    return exams[exam_id]["results"].get(student_id, None)


def get_exam_results(exams, exam_id):
    """Get all results for an exam."""
    if exam_id not in exams:
        return {}
    return exams[exam_id]["results"]


def calculate_exam_average(exams, exam_id):
    """Calculate average marks for an exam."""
    results = get_exam_results(exams, exam_id)
    if not results:
        return 0.0
    return round(sum(results.values()) / len(results), 2)


def get_exam_highest(exams, exam_id):
    """Get highest marks in an exam."""
    results = get_exam_results(exams, exam_id)
    if not results:
        return None
    return max(results.values())


def get_exam_lowest(exams, exam_id):
    """Get lowest marks in an exam."""
    results = get_exam_results(exams, exam_id)
    if not results:
        return None
    return min(results.values())


def get_failed_students(exams, exam_id, passing_marks=40):
    """Get list of students who failed an exam."""
    results = get_exam_results(exams, exam_id)
    return [sid for sid, marks in results.items() if marks < passing_marks]


def get_passed_students(exams, exam_id, passing_marks=40):
    """Get list of students who passed an exam."""
    results = get_exam_results(exams, exam_id)
    return [sid for sid, marks in results.items() if marks >= passing_marks]


def calculate_pass_rate(exams, exam_id, passing_marks=40):
    """Calculate pass rate for an exam."""
    results = get_exam_results(exams, exam_id)
    if not results:
        return 0.0
    passed = sum(1 for m in results.values() if m >= passing_marks)
    return round((passed / len(results)) * 100, 2)


def is_eligible_for_retake(marks, retake_count, max_retakes=2):
    """Check if student is eligible to retake exam."""
    if marks >= 40:
        return False, "Student already passed"
    if retake_count >= max_retakes:
        return False, "Maximum retakes exhausted"
    return True, "Eligible for retake"


def calculate_retake_fee(original_fee, retake_number):
    """Calculate retake exam fee (increases with each retake)."""
    if retake_number <= 0:
        return None
    return original_fee * retake_number


def has_room_conflict(exams, room, date, new_duration_mins):
    """Check if a room is already booked for a given date."""
    for exam in exams.values():
        if exam["room"] == room and exam["date"] == date:
            return True
    return False


def get_exams_by_course(exams, course_id):
    """Get all exams scheduled for a course."""
    return {eid: info for eid, info in exams.items() if info["course_id"] == course_id}


def get_student_exam_history(exams, student_id):
    """Get all exam results for a student across all exams."""
    history = {}
    for exam_id, info in exams.items():
        if student_id in info["results"]:
            history[exam_id] = {
                "course_id": info["course_id"],
                "date": info["date"],
                "marks": info["results"][student_id],
            }
    return history


def get_top_performers(exams, exam_id, top_n=5):
    """Get top N performers in an exam."""
    results = get_exam_results(exams, exam_id)
    if not results:
        return []
    sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
    return sorted_results[:top_n]
