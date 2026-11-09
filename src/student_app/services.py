"""Business logic: pure functions and the application service."""

import logging
from collections.abc import Iterable

from student_app.exceptions import NotificationError, ValidationError
from student_app.models import Student
from student_app.protocols import Notifier, StudentRepository

logger = logging.getLogger(__name__)


def find_by_last_name(students: Iterable[Student], last_name: str) -> list[Student]:
    needle = last_name.strip().lower()
    return [s for s in students if s.last_name.lower() == needle]


def filter_by_group(students: Iterable[Student], group: str) -> list[Student]:
    return [s for s in students if s.group == group]


def calculate_average(students: Iterable[Student]) -> float:
    grades = [s.average_grade for s in students]
    if not grades:
        return 0.0
    return sum(grades) / len(grades)


def find_best_student(students: Iterable[Student]) -> Student | None:
    return max(students, key=lambda s: s.average_grade, default=None)


class StudentService:
    """Registers and searches students; repository and notifier are injected."""

    def __init__(self, repository: StudentRepository, notifier: Notifier) -> None:
        self._repository = repository
        self._notifier = notifier

    def register(self, student: Student) -> bool:
        """Store a student and notify him.

        Returns True if the notification was delivered. A failed notification
        does not undo the registration; a repository error is propagated and
        no notification is sent.
        """
        if self._repository.get(student.student_id) is not None:
            raise ValidationError(
                f"Student {student.student_id} already exists", field="student_id"
            )

        self._repository.add(student)

        try:
            self._notifier.send(student.full_name, f"Registered in group {student.group}")
        except NotificationError:
            logger.warning("Notification for student %s failed", student.student_id)
            return False

        return True

    def find_by_id(self, student_id: int) -> Student | None:
        return self._repository.get(student_id)

    def find_by_last_name(self, last_name: str) -> list[Student]:
        return find_by_last_name(self._repository.all(), last_name)

    def students_of_group(self, group: str) -> list[Student]:
        return filter_by_group(self._repository.all(), group)

    def average_grade(self, group: str | None = None) -> float:
        students = self._repository.all()
        if group is not None:
            students = filter_by_group(students, group)
        return calculate_average(students)

    def best_student(self) -> Student | None:
        return find_best_student(self._repository.all())
