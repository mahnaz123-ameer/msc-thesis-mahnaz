import pytest
from library import get_borrowed_books


def test_student_with_multiple_borrowed_books():
    borrowed = {
        101: ["Python Basics", "Data Structures", "Algorithms"]
    }
    assert get_borrowed_books(borrowed, 101) == [
        "Python Basics",
        "Data Structures",
        "Algorithms"
    ]


def test_student_with_one_borrowed_book():
    borrowed = {101: ["Python Basics"]}
    assert get_borrowed_books(borrowed, 101) == ["Python Basics"]


def test_student_with_no_borrowed_books():
    borrowed = {101: [], 102: ["Database Systems"]}
    assert get_borrowed_books(borrowed, 101) == []


def test_student_id_not_found():
    borrowed = {101: ["Python Basics"], 102: ["Operating Systems"]}
    assert get_borrowed_books(borrowed, 103) == []


def test_empty_borrowed_dictionary():
    assert get_borrowed_books({}, 101) == []


def test_empty_student_id():
    borrowed = {"": ["Python Basics"]}
    assert get_borrowed_books(borrowed, "") == ["Python Basics"]


def test_string_student_id():
    borrowed = {"STU001": ["Python Basics", "Database Systems"]}
    assert get_borrowed_books(borrowed, "STU001") == [
        "Python Basics",
        "Database Systems"
    ]


def test_integer_and_string_student_ids_are_distinct():
    borrowed = {
        101: ["Python Basics"],
        "101": ["Database Systems"]
    }
    assert get_borrowed_books(borrowed, 101) == ["Python Basics"]
    assert get_borrowed_books(borrowed, "101") == ["Database Systems"]


def test_none_as_student_id():
    borrowed = {None: ["Python Basics"]}
    assert get_borrowed_books(borrowed, None) == ["Python Basics"]


def test_none_as_borrowed_books_value():
    borrowed = {101: None}
    assert get_borrowed_books(borrowed, 101) is None


def test_duplicate_borrowed_books():
    borrowed = {101: ["Python Basics", "Python Basics"]}
    assert get_borrowed_books(borrowed, 101) == [
        "Python Basics",
        "Python Basics"
    ]


def test_borrowed_dictionary_is_not_modified():
    borrowed = {
        101: ["Python Basics"],
        102: ["Database Systems"]
    }
    original = borrowed.copy()

    get_borrowed_books(borrowed, 101)

    assert borrowed == original


def test_returned_list_is_same_object():
    books = ["Python Basics", "Algorithms"]
    borrowed = {101: books}

    result = get_borrowed_books(borrowed, 101)

    assert result is books


def test_invalid_borrowed_none():
    with pytest.raises(AttributeError):
        get_borrowed_books(None, 101)


def test_invalid_borrowed_list():
    with pytest.raises(AttributeError):
        get_borrowed_books([], 101)


def test_invalid_borrowed_string():
    with pytest.raises(AttributeError):
        get_borrowed_books("invalid", 101)


def test_invalid_borrowed_integer():
    with pytest.raises(AttributeError):
        get_borrowed_books(123, 101)


def test_unhashable_student_id():
    borrowed = {101: ["Python Basics"]}

    with pytest.raises(TypeError):
        get_borrowed_books(borrowed, [101])
