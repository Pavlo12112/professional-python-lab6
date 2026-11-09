"""Domain model."""

from dataclasses import asdict, dataclass

from student_app.exceptions import ValidationError

MIN_GRADE = 0.0
MAX_GRADE = 100.0


@dataclass(frozen=True, slots=True)
class Student:
    student_id: int
    first_name: str
    last_name: str
    group: str
    average_grade: float

    def __post_init__(self) -> None:
        if (
            isinstance(self.student_id, bool)
            or not isinstance(self.student_id, int)
            or self.student_id <= 0
        ):
            raise ValidationError("student_id must be a positive integer", field="student_id")

        for name in ("first_name", "last_name", "group"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValidationError(f"{name} must not be empty", field=name)

        grade = self.average_grade
        if (
            isinstance(grade, bool)
            or not isinstance(grade, (int, float))
            or not MIN_GRADE <= grade <= MAX_GRADE
        ):
            raise ValidationError(
                f"average_grade must be between {MIN_GRADE:g} and {MAX_GRADE:g}",
                field="average_grade",
            )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def classify_grade(grade: float) -> str:
    """Label of an average grade: three branches."""
    if grade >= 90:
        return "excellent"

    if grade >= 60:
        return "passed"

    return "failed"
