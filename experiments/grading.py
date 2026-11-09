"""Function with three branches for experiment 3."""


def classify_grade(grade: float) -> str:
    if grade >= 90:
        return "excellent"
    if grade >= 60:
        return "passed"
    return "failed"
