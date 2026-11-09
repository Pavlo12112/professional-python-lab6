"""Interfaces of external dependencies (system boundaries)."""

from typing import Protocol

from student_app.models import Student


class StudentRepository(Protocol):
    def add(self, student: Student) -> None: ...

    def get(self, student_id: int) -> Student | None: ...

    def all(self) -> list[Student]: ...

    def remove(self, student_id: int) -> bool: ...


class AsyncStudentRepository(Protocol):
    async def get(self, student_id: int) -> Student | None: ...

    async def all(self) -> list[Student]: ...


class Notifier(Protocol):
    def send(self, recipient: str, message: str) -> None: ...
