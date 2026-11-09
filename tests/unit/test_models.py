import dataclasses

import pytest

from student_app.exceptions import ValidationError
from student_app.models import Student, classify_grade


def test_student_is_created_with_given_values(student):
    assert student.student_id == 1
    assert student.first_name == "Anna"
    assert student.group == "PI-21"
    assert student.average_grade == pytest.approx(91.5)


def test_full_name_joins_first_and_last_name(student):
    assert student.full_name == "Anna Koval"


@pytest.mark.parametrize(
    "grade",
    [
        pytest.param(0, id="minimum"),
        pytest.param(0.01, id="just-above-minimum"),
        pytest.param(50, id="middle"),
        pytest.param(99.99, id="just-below-maximum"),
        pytest.param(100, id="maximum"),
    ],
)
def test_boundary_grades_are_accepted(student_factory, grade):
    assert student_factory(average_grade=grade).average_grade == pytest.approx(grade)


@pytest.mark.parametrize(
    "grade",
    [-0.01, 100.01, float("nan"), "90", None, True],
    ids=["below-minimum", "above-maximum", "nan", "string", "none", "bool"],
)
def test_invalid_grades_are_rejected(student_factory, grade):
    with pytest.raises(ValidationError, match="between 0 and 100") as exc_info:
        student_factory(average_grade=grade)

    assert exc_info.value.field == "average_grade"


@pytest.mark.parametrize(
    ("kwargs", "field"),
    [
        ({"student_id": 0}, "student_id"),
        ({"student_id": -5}, "student_id"),
        ({"student_id": "1"}, "student_id"),
        ({"first_name": ""}, "first_name"),
        ({"last_name": "   "}, "last_name"),
        ({"group": ""}, "group"),
    ],
    ids=["zero-id", "negative-id", "string-id", "empty-first-name", "blank-last-name", "empty-group"],
)
def test_invalid_required_fields_are_rejected(student_factory, kwargs, field):
    with pytest.raises(ValidationError) as exc_info:
        student_factory(**kwargs)

    assert exc_info.value.field == field


def test_student_is_immutable(student):
    with pytest.raises(dataclasses.FrozenInstanceError):
        student.average_grade = 10  # type: ignore[misc]


def test_to_dict_contains_all_fields(student):
    assert student.to_dict() == {
        "student_id": 1,
        "first_name": "Anna",
        "last_name": "Koval",
        "group": "PI-21",
        "average_grade": 91.5,
    }


@pytest.mark.parametrize(
    ("grade", "expected"),
    [
        (100, "excellent"),
        (90, "excellent"),
        (89.99, "passed"),
        (60, "passed"),
        (59.99, "failed"),
        (0, "failed"),
    ],
)
def test_classify_grade_covers_every_branch(grade, expected):
    assert classify_grade(grade) == expected
