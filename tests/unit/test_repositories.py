"""The fake repositories are production-like code and must be tested too."""

import pytest

from student_app.exceptions import ValidationError
from student_app.repositories import AsyncInMemoryStudentRepository, InMemoryStudentRepository


def test_repository_stores_and_returns_students(student):
    repository = InMemoryStudentRepository()

    repository.add(student)

    assert repository.get(1) == student
    assert repository.all() == [student]
    assert len(repository) == 1


def test_get_of_unknown_id_returns_none():
    assert InMemoryStudentRepository().get(999) is None


def test_adding_duplicate_id_is_rejected(student, student_factory):
    repository = InMemoryStudentRepository()
    repository.add(student)

    with pytest.raises(ValidationError, match="already exists") as exc_info:
        repository.add(student_factory(student_id=1, first_name="Other"))

    assert exc_info.value.field == "student_id"
    assert len(repository) == 1


def test_remove_reports_whether_student_existed(student):
    repository = InMemoryStudentRepository()
    repository.add(student)

    assert repository.remove(1) is True
    assert repository.remove(1) is False
    assert len(repository) == 0


def test_all_returns_a_copy_that_cannot_change_the_repository(repository):
    snapshot = repository.all()

    snapshot.clear()

    assert len(repository) == 4


@pytest.mark.asyncio
async def test_async_repository_returns_students_and_none(students):
    repository = AsyncInMemoryStudentRepository(students)

    assert (await repository.get(3)).last_name == "Bondar"
    assert await repository.get(99) is None
    assert len(await repository.all()) == 4


@pytest.mark.asyncio
async def test_empty_async_repository_has_no_students():
    assert await AsyncInMemoryStudentRepository().all() == []
