import pytest
from courses import has_time_conflict


def test_courses_with_overlapping_time_slots():
    schedule = {
        "CS101": {"Monday 9AM", "Wednesday 10AM"},
        "CS102": {"Monday 9AM", "Thursday 11AM"}
    }
    assert has_time_conflict(schedule, "CS101", "CS102") is True


def test_courses_without_overlapping_time_slots():
    schedule = {
        "CS101": {"Monday 9AM", "Wednesday 10AM"},
        "CS102": {"Tuesday 9AM", "Thursday 11AM"}
    }
    assert has_time_conflict(schedule, "CS101", "CS102") is False


def test_courses_with_multiple_overlapping_slots():
    schedule = {
        "CS101": {"Monday 9AM", "Tuesday 10AM", "Wednesday 11AM"},
        "CS102": {"Monday 9AM", "Tuesday 10AM", "Friday 2PM"}
    }
    assert has_time_conflict(schedule, "CS101", "CS102") is True


def test_courses_with_one_overlapping_slot():
    schedule = {
        "CS101": {"Monday 9AM", "Tuesday 10AM"},
        "CS102": {"Monday 9AM", "Friday 2PM"}
    }
    assert has_time_conflict(schedule, "CS101", "CS102") is True


def test_first_course_not_found():
    schedule = {
        "CS102": {"Monday 9AM"}
    }
    assert has_time_conflict(schedule, "CS101", "CS102") is False


def test_second_course_not_found():
    schedule = {
        "CS101": {"Monday 9AM"}
    }
    assert has_time_conflict(schedule, "CS101", "CS102") is False


def test_both_courses_not_found():
    schedule = {}
    assert has_time_conflict(schedule, "CS101", "CS102") is False


def test_first_course_has_empty_slots():
    schedule = {
        "CS101": set(),
        "CS102": {"Monday 9AM"}
    }
    assert has_time_conflict(schedule, "CS101", "CS102") is False


def test_second_course_has_empty_slots():
    schedule = {
        "CS101": {"Monday 9AM"},
        "CS102": set()
    }
    assert has_time_conflict(schedule, "CS101", "CS102") is False


def test_both_courses_have_empty_slots():
    schedule = {
        "CS101": set(),
        "CS102": set()
    }
    assert has_time_conflict(schedule, "CS101", "CS102") is False


def test_same_course_with_non_empty_slots():
    schedule = {
        "CS101": {"Monday 9AM", "Tuesday 10AM"}
    }
    assert has_time_conflict(schedule, "CS101", "CS101") is True


def test_same_course_with_empty_slots():
    schedule = {
        "CS101": set()
    }
    assert has_time_conflict(schedule, "CS101", "CS101") is False


def test_integer_course_ids():
    schedule = {
        101: {"Monday 9AM"},
        102: {"Monday 9AM"}
    }
    assert has_time_conflict(schedule, 101, 102) is True


def test_string_and_integer_course_ids_are_distinct():
    schedule = {
        101: {"Monday 9AM"},
        "101": {"Tuesday 10AM"}
    }
    assert has_time_conflict(schedule, 101, "101") is False


def test_empty_string_course_ids():
    schedule = {
        "": {"Monday 9AM"},
        "CS102": {"Monday 9AM"}
    }
    assert has_time_conflict(schedule, "", "CS102") is True


def test_none_as_course_id():
    schedule = {
        None: {"Monday 9AM"},
        "CS102": {"Monday 9AM"}
    }
    assert has_time_conflict(schedule, None, "CS102") is True


def test_invalid_schedule_none():
    with pytest.raises(AttributeError):
        has_time_conflict(None, "CS101", "CS102")


def test_invalid_schedule_list():
    with pytest.raises(AttributeError):
        has_time_conflict([], "CS101", "CS102")


def test_invalid_schedule_integer():
    with pytest.raises(AttributeError):
        has_time_conflict(123, "CS101", "CS102")


def test_unhashable_first_course_id():
    schedule = {"CS101": {"Monday 9AM"}}
    with pytest.raises(TypeError):
        has_time_conflict(schedule, ["CS101"], "CS101")


def test_unhashable_second_course_id():
    schedule = {"CS101": {"Monday 9AM"}}
    with pytest.raises(TypeError):
        has_time_conflict(schedule, "CS101", ["CS101"])


def test_invalid_time_slots_list():
    schedule = {
        "CS101": ["Monday 9AM"],
        "CS102": ["Monday 9AM"]
    }
    with pytest.raises(TypeError):
        has_time_conflict(schedule, "CS101", "CS102")


def test_invalid_time_slots_none():
    schedule = {
        "CS101": None,
        "CS102": {"Monday 9AM"}
    }
    with pytest.raises(TypeError):
        has_time_conflict(schedule, "CS101", "CS102")


def test_non_overlapping_different_data_types():
    schedule = {
        "CS101": {9, 10, 11},
        "CS102": {"9", "10", "11"}
    }
    assert has_time_conflict(schedule, "CS101", "CS102") is False
