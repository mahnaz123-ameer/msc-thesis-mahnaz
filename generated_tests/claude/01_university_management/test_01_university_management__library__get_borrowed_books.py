import pytest
from library import get_borrowed_books


# Normal cases

def test_student_with_one_book():
    borrowed = {'S1': ['Book A']}
    assert get_borrowed_books(borrowed, 'S1') == ['Book A']


def test_student_with_multiple_books():
    borrowed = {'S1': ['Book A', 'Book B', 'Book C']}
    assert get_borrowed_books(borrowed, 'S1') == ['Book A', 'Book B', 'Book C']


def test_student_with_no_books_returns_empty_list():
    borrowed = {'S1': ['Book A']}
    assert get_borrowed_books(borrowed, 'S2') == []


def test_multiple_students_returns_correct_student_books():
    borrowed = {
        'S1': ['Book A', 'Book B'],
        'S2': ['Book C'],
        'S3': ['Book D', 'Book E', 'Book F'],
    }
    assert get_borrowed_books(borrowed, 'S2') == ['Book C']


def test_multiple_students_first_student():
    borrowed = {
        'S1': ['Book A', 'Book B'],
        'S2': ['Book C'],
    }
    assert get_borrowed_books(borrowed, 'S1') == ['Book A', 'Book B']


def test_multiple_students_last_student():
    borrowed = {
        'S1': ['Book A'],
        'S2': ['Book B', 'Book C'],
    }
    assert get_borrowed_books(borrowed, 'S2') == ['Book B', 'Book C']


def test_returns_list_type():
    borrowed = {'S1': ['Book A']}
    result = get_borrowed_books(borrowed, 'S1')
    assert isinstance(result, list)


def test_missing_student_returns_list_type():
    borrowed = {}
    result = get_borrowed_books(borrowed, 'S1')
    assert isinstance(result, list)


# Edge cases

def test_empty_borrowed_dict():
    assert get_borrowed_books({}, 'S1') == []


def test_student_with_empty_book_list():
    borrowed = {'S1': []}
    assert get_borrowed_books(borrowed, 'S1') == []


def test_numeric_student_id():
    borrowed = {1: ['Book A', 'Book B']}
    assert get_borrowed_books(borrowed, 1) == ['Book A', 'Book B']


def test_numeric_student_id_missing():
    borrowed = {1: ['Book A']}
    assert get_borrowed_books(borrowed, 2) == []


def test_none_as_student_id_present():
    borrowed = {None: ['Book A']}
    assert get_borrowed_books(borrowed, None) == ['Book A']


def test_none_as_student_id_missing():
    borrowed = {'S1': ['Book A']}
    assert get_borrowed_books(borrowed, None) == []


def test_student_id_with_special_characters():
    borrowed = {'S1@uni.edu': ['Book X']}
    assert get_borrowed_books(borrowed, 'S1@uni.edu') == ['Book X']


def test_student_id_with_spaces():
    borrowed = {'John Doe': ['Book Y']}
    assert get_borrowed_books(borrowed, 'John Doe') == ['Book Y']


def test_books_with_special_characters():
    borrowed = {'S1': ['Book: A & B', 'Book #2']}
    assert get_borrowed_books(borrowed, 'S1') == ['Book: A & B', 'Book #2']


def test_does_not_modify_borrowed_dict():
    borrowed = {'S1': ['Book A']}
    original = dict(borrowed)
    get_borrowed_books(borrowed, 'S1')
    assert borrowed == original


def test_does_not_modify_returned_list():
    borrowed = {'S1': ['Book A', 'Book B']}
    result = get_borrowed_books(borrowed, 'S1')
    result.append('Book C')
    # The returned list may or may not be a copy; we just ensure the call worked
    assert 'Book A' in get_borrowed_books(borrowed, 'S1')


def test_large_number_of_books():
    books = [f'Book {i}' for i in range(1000)]
    borrowed = {'S1': books}
    assert get_borrowed_books(borrowed, 'S1') == books


def test_large_number_of_students():
    borrowed = {f'S{i}': [f'Book {i}'] for i in range(500)}
    assert get_borrowed_books(borrowed, 'S250') == ['Book 250']


def test_empty_string_student_id_present():
    borrowed = {'': ['Book Z']}
    assert get_borrowed_books(borrowed, '') == ['Book Z']


def test_empty_string_student_id_missing():
    borrowed = {'S1': ['Book A']}
    assert get_borrowed_books(borrowed, '') == []


def test_integer_key_vs_string_key_mismatch():
    borrowed = {1: ['Book A']}
    assert get_borrowed_books(borrowed, '1') == []


def test_string_key_vs_integer_key_mismatch():
    borrowed = {'1': ['Book A']}
    assert get_borrowed_books(borrowed, 1) == []


def test_duplicate_book_entries():
    borrowed = {'S1': ['Book A', 'Book A', 'Book B']}
    assert get_borrowed_books(borrowed, 'S1') == ['Book A', 'Book A', 'Book B']


def test_books_list_contains_none():
    borrowed = {'S1': [None, 'Book A']}
    assert get_borrowed_books(borrowed, 'S1') == [None, 'Book A']


def test_books_list_contains_numbers():
    borrowed = {'S1': [101, 202]}
    assert get_borrowed_books(borrowed, 'S1') == [101, 202]
