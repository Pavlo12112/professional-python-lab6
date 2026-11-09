"""Shared fixtures (pytest finds them automatically, no imports in tests)."""

from collections.abc import Callable
from pathlib import Path
from unittest.mock import Mock

import pytest

from student_app.models import Student
from student_app.protocols import Notifier
from student_app.repositories import InMemoryStudentRepository

CSV_HEADER = "student_id,first_name,last_name,group,average_grade\n"


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Autouse: every test starts without application variables (isolation)."""
    monkeypatch.delenv("STUDENT_APP_MINIMUM_GRADE", raising=False)
    monkeypatch.delenv("APP_ENV", raising=False)


@pytest.fixture
def student() -> Student:
    return Student(1, "Anna", "Koval", "PI-21", 91.5)


@pytest.fixture
def student_factory() -> Callable[..., Student]:
    """Fixture factory: creates students with only the needed fields changed."""

    def create(
        *,
        student_id: int = 1,
        first_name: str = "Anna",
        last_name: str = "Koval",
        group: str = "PI-21",
        average_grade: float = 90.0,
    ) -> Student:
        return Student(student_id, first_name, last_name, group, average_grade)

    return create


@pytest.fixture
def students(student_factory: Callable[..., Student]) -> list[Student]:
    return [
        student_factory(student_id=1, first_name="Anna", last_name="Koval", group="PI-21", average_grade=90),
        student_factory(student_id=2, first_name="Oleh", last_name="Melnyk", group="PI-21", average_grade=80),
        student_factory(student_id=3, first_name="Iryna", last_name="Bondar", group="PI-22", average_grade=95),
        student_factory(student_id=4, first_name="Andrii", last_name="Koval", group="PI-22", average_grade=60),
    ]


@pytest.fixture
def repository(students: list[Student]) -> InMemoryStudentRepository:
    """Fake repository filled with the standard students."""
    repo = InMemoryStudentRepository()
    for item in students:
        repo.add(item)
    return repo


@pytest.fixture
def notifier() -> Mock:
    """Mock restricted to the Notifier interface."""
    return Mock(spec=Notifier)


@pytest.fixture
def write_csv(tmp_path: Path) -> Callable[..., Path]:
    """Returns a function that writes a CSV file with the standard header."""

    def write(rows: str, name: str = "students.csv") -> Path:
        path = tmp_path / name
        path.write_text(CSV_HEADER + rows, encoding="utf-8")
        return path

    return write


@pytest.fixture
def output_dir(tmp_path: Path):  # type: ignore[no-untyped-def]
    """Fixture with teardown: after the test no temporary file may remain."""
    directory = tmp_path / "output"
    directory.mkdir()

    yield directory

    leftovers = list(directory.glob("*.tmp"))
    assert not leftovers, f"temporary files were left: {leftovers}"
