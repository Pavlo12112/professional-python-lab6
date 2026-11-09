"""Service over an asynchronous repository."""

from student_app.exceptions import NotFoundError
from student_app.models import Student
from student_app.protocols import AsyncStudentRepository
from student_app.services import calculate_average, find_best_student


class AsyncStudentService:
    def __init__(self, repository: AsyncStudentRepository) -> None:
        self._repository = repository

    async def load(self, student_id: int) -> Student:
        student = await self._repository.get(student_id)
        if student is None:
            raise NotFoundError(f"Student {student_id} not found")
        return student

    async def average_grade(self) -> float:
        return calculate_average(await self._repository.all())

    async def best_student(self) -> Student | None:
        return find_best_student(await self._repository.all())
