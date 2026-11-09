"""Experiment 3, step 2: the missing branch (50 -> failed) is added."""

import pytest

from grading import classify_grade


@pytest.mark.parametrize(
    ("grade", "expected"),
    [(95, "excellent"), (70, "passed"), (50, "failed")],
)
def test_classify_grade(grade, expected):
    assert classify_grade(grade) == expected
