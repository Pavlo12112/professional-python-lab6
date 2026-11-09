"""Pure business functions: searching, filtering and statistics."""

import pytest

from student_app.services import (
    calculate_average,
    filter_by_group,
    find_best_student,
    find_by_last_name,
)


def test_search_by_last_name_ignores_case_and_spaces(students):
    result = find_by_last_name(students, "  koval ")

    assert [s.student_id for s in result] == [1, 4]


def test_search_by_unknown_last_name_gives_empty_list(students):
    assert find_by_last_name(students, "Unknown") == []


def test_filter_by_group_returns_only_that_group(students):
    assert [s.student_id for s in filter_by_group(students, "PI-21")] == [1, 2]


def test_filter_by_unknown_group_gives_empty_list(students):
    assert filter_by_group(students, "XX-00") == []


def test_average_grade_of_students(students):
    assert calculate_average(students) == pytest.approx(81.25)


def test_average_grade_of_empty_collection_is_zero():
    assert calculate_average([]) == 0.0


def test_best_student_has_the_highest_grade(students):
    best = find_best_student(students)

    assert best is not None
    assert best.student_id == 3


def test_best_student_of_empty_collection_is_none():
    assert find_best_student([]) is None


def test_best_student_with_equal_grades_is_the_first_one(student_factory):
    first = student_factory(student_id=1, average_grade=70)
    second = student_factory(student_id=2, average_grade=70)

    assert find_best_student([first, second]) is first
