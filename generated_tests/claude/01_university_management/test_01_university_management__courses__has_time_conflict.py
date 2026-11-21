import pytest
from courses import has_time_conflict


# Normal cases

def test_no_conflict_different_slots():
    schedule = {
        'CS101': {'Mon9', 'Wed9'},
        'CS102': {'Tue10', 'Thu10'},
    }
    assert has_time_conflict(schedule, 'CS101', 'CS102') is False


def test_conflict_one_shared_slot():
    schedule = {
        'CS101': {'Mon9', 'Wed9'},
        'CS102': {'Mon9', 'Thu10'},
    }
    assert has_time_conflict(schedule, 'CS101', 'CS102') is True


def test_conflict_multiple_shared_slots():
    schedule = {
        'CS101': {'Mon9', 'Wed9', 'Fri9'},
        'CS102': {'Mon9', 'Wed9', 'Tue10'},
    }
    assert has_time_conflict(schedule, 'CS101', 'CS102') is True


def test_conflict_all_slots_identical():
    schedule = {
        'CS101': {'Mon9', 'Wed9'},
        'CS102': {'Mon9', 'Wed9'},
    }
    assert has_time_conflict(schedule, 'CS101', 'CS102') is True


def test_no_conflict_many_courses():
    schedule = {
        'CS101': {'Mon9', 'Wed9'},
        'CS102': {'Tue10', 'Thu10'},
        'CS103': {'Mon11', 'Wed11'},
    }
    assert has_time_conflict(schedule, 'CS101', 'CS103') is False


def test_conflict_between_non_adjacent_courses():
    schedule = {
        'CS101': {'Mon9'},
        'CS102': {'Tue10'},
        'CS103': {'Mon9'},
    }
    assert has_time_conflict(schedule, 'CS101', 'CS103') is True


def test_returns_bool_true():
    schedule = {
        'A': {'slot1'},
        'B': {'slot1'},
    }
    result = has_time_conflict(schedule, 'A', 'B')
    assert isinstance(result, bool)
    assert result is True


def test_returns_bool_false():
    schedule = {
        'A': {'slot1'},
        'B': {'slot2'},
    }
    result = has_time_conflict(schedule, 'A', 'B')
    assert isinstance(result, bool)
    assert result is False


# Edge cases: missing course IDs

def test_first_course_missing():
    schedule = {
        'CS102': {'Mon9', 'Wed9'},
    }
    assert has_time_conflict(schedule, 'CS101', 'CS102') is False


def test_second_course_missing():
    schedule = {
        'CS101': {'Mon9', 'Wed9'},
    }
    assert has_time_conflict(schedule, 'CS101', 'CS102') is False


def test_both_courses_missing():
    schedule = {}
    assert has_time_conflict(schedule, 'CS101', 'CS102') is False


def test_empty_schedule():
    assert has_time_conflict({}, 'A', 'B') is False


# Edge cases: empty slot sets

def test_first_course_empty_slots():
    schedule = {
        'CS101': set(),
        'CS102': {'Mon9'},
    }
    assert has_time_conflict(schedule, 'CS101', 'CS102') is False


def test_second_course_empty_slots():
    schedule = {
        'CS101': {'Mon9'},
        'CS102': set(),
    }
    assert has_time_conflict(schedule, 'CS101', 'CS102') is False


def test_both_courses_empty_slots():
    schedule = {
        'CS101': set(),
        'CS102': set(),
    }
    assert has_time_conflict(schedule, 'CS101', 'CS102') is False


# Edge cases: same course compared with itself

def test_same_course_id_with_slots():
    schedule = {
        'CS101': {'Mon9', 'Wed9'},
    }
    assert has_time_conflict(schedule, 'CS101', 'CS101') is True


def test_same_course_id_empty_slots():
    schedule = {
        'CS101': set(),
    }
    assert has_time_conflict(schedule, 'CS101', 'CS101') is False


def test_same_course_id_missing():
    schedule = {}
    assert has_time_conflict(schedule, 'CS101', 'CS101') is False


# Edge cases: slot types

def test_numeric_slot_values_conflict():
    schedule = {
        'CS101': {1, 2, 3},
        'CS102': {3, 4, 5},
    }
    assert has_time_conflict(schedule, 'CS101', 'CS102') is True


def test_numeric_slot_values_no_conflict():
    schedule = {
        'CS101': {1, 2, 3},
        'CS102': {4, 5, 6},
    }
    assert has_time_conflict(schedule, 'CS101', 'CS102') is False


def test_tuple_slot_values_conflict():
    schedule = {
        'CS101': {('Mon', 9), ('Wed', 9)},
        'CS102': {('Mon', 9), ('Fri', 11)},
    }
    assert has_time_conflict(schedule, 'CS101', 'CS102') is True


def test_tuple_slot_values_no_conflict():
    schedule = {
        'CS101': {('Mon', 9), ('Wed', 9)},
        'CS102': {('Tue', 10), ('Thu', 10)},
    }
    assert has_time_conflict(schedule, 'CS101', 'CS102') is False


# Edge cases: numeric course IDs

def test_numeric_course_ids_conflict():
    schedule = {
        101: {'Mon9', 'Wed9'},
        102: {'Mon9', 'Fri11'},
    }
    assert has_time_conflict(schedule, 101, 102) is True


def test_numeric_course_ids_no_conflict():
    schedule = {
        101: {'Mon9'},
        102: {'Tue10'},
    }
    assert has_time_conflict(schedule, 101, 102) is False


def test_numeric_vs_string_course_id_mismatch():
    schedule = {
        'CS101': {'Mon9'},
        101: {'Mon9'},
    }
    assert has_time_conflict(schedule, 'CS101', 101) is True


# Edge cases: single-slot sets

def test_single_slot_each_conflict():
    schedule = {
        'A': {'Mon9'},
        'B': {'Mon9'},
    }
    assert has_time_conflict(schedule, 'A', 'B') is True


def test_single_slot_each_no_conflict():
    schedule = {
        'A': {'Mon9'},
        'B': {'Tue10'},
    }
    assert has_time_conflict(schedule, 'A', 'B') is False


# Edge cases: large slot sets

def test_large_slot_sets_no_conflict():
    slots_1 = {f'slot{i}' for i in range(100)}
    slots_2 = {f'slot{i}' for i in range(100, 200)}
    schedule = {'A': slots_1, 'B': slots_2}
    assert has_time_conflict(schedule, 'A', 'B') is False


def test_large_slot_sets_with_conflict():
    slots_1 = {f'slot{i}' for i in range(100)}
    slots_2 = {f'slot{i}' for i in range(99, 199)}
    schedule = {'A': slots_1, 'B': slots_2}
    assert has_time_conflict(schedule, 'A', 'B') is True


# Does not mutate the schedule

def test_does_not_mutate_schedule():
    schedule = {
        'CS101': {'Mon9', 'Wed9'},
        'CS102': {'Mon9', 'Thu10'},
    }
    original_slots_1 = set(schedule['CS101'])
    original_slots_2 = set(schedule['CS102'])
    has_time_conflict(schedule, 'CS101', 'CS102')
    assert schedule['CS101'] == original_slots_1
    assert schedule['CS102'] == original_slots_2
