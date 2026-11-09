"""Report over a collection of students."""

from collections import Counter
from collections.abc import Sequence
from datetime import datetime, timezone

from student_app.models import Student
from student_app.services import calculate_average, find_best_student


def utcnow() -> datetime:
    """Current time; a separate function so that tests can replace it."""
    return datetime.now(timezone.utc)


def build_report(students: Sequence[Student], minimum_grade: float = 0.0) -> dict[str, object]:
    selected = [s for s in students if s.average_grade >= minimum_grade]
    best = find_best_student(selected)

    return {
        "generated_at": utcnow().isoformat(),
        "count": len(selected),
        "average": round(calculate_average(selected), 2),
        "best": best.to_dict() if best is not None else None,
        "by_group": dict(Counter(s.group for s in selected)),
    }
