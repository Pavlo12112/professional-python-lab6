"""Fake (in-memory) repositories: simple working implementations."""

from student_app.exceptions import ValidationError
from student_app.models import Student


class InMemoryStudentRepository:
    def __init__(self) -> None:
        self._items: dict[int, Student] = {}

    def add(self, student: Student) -> None:
        if student.student_id in self._items:
            raise ValidationError(
                f"Student {student.student_id} already exists", field="student_id"
            )
        self._items[student.student_id] = student

    def get(self, student_id: int) -> Student | None:
        return self._items.get(student_id)

    def all(self) -> list[Student]:
        return list(self._items.values())

    def remove(self, student_id: int) -> bool:
        return self._items.pop(student_id, None) is not None

    def __len__(self) -> int:
        return len(self._items)


class AsyncInMemoryStudentRepository:
    def __init__(self, students: list[Student] | None = None) -> None:
        self._items = {s.student_id: s for s in students or []}

    async def get(self, student_id: int) -> Student | None:
        return self._items.get(student_id)

    async def all(self) -> list[Student]:
        return list(self._items.values())
