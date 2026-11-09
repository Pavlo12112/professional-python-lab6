"""Experiment 3, step 1: only two of three branches are tested."""

from grading import classify_grade


def test_excellent():
    assert classify_grade(95) == "excellent"


def test_passed():
    assert classify_grade(70) == "passed"
