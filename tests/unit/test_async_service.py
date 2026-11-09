from unittest.mock import AsyncMock

import pytest

from student_app.async_service import AsyncStudentService
from student_app.exceptions import NotFoundError
from student_app.protocols import AsyncStudentRepository


@pytest.fixture
def async_repository() -> AsyncMock:
    return AsyncMock(spec=AsyncStudentRepository)


@pytest.mark.asyncio
async def test_load_returns_student_and_awaits_repository(async_repository, student):
    async_repository.get.return_value = student

    result = await AsyncStudentService(async_repository).load(1)

    assert result is student
    async_repository.get.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_load_of_missing_student_raises_not_found(async_repository):
    async_repository.get.return_value = None

    with pytest.raises(NotFoundError, match="not found"):
        await AsyncStudentService(async_repository).load(99)


@pytest.mark.asyncio
async def test_connection_error_of_dependency_is_propagated(async_repository):
    async_repository.get.side_effect = ConnectionError("Network error")

    with pytest.raises(ConnectionError, match="Network error"):
        await AsyncStudentService(async_repository).load(1)


@pytest.mark.asyncio
async def test_average_grade_uses_all_students(async_repository, students):
    async_repository.all.return_value = students

    result = await AsyncStudentService(async_repository).average_grade()

    assert result == pytest.approx(81.25)
    async_repository.all.assert_awaited_once()


@pytest.mark.asyncio
async def test_best_student_of_empty_repository_is_none(async_repository):
    async_repository.all.return_value = []

    assert await AsyncStudentService(async_repository).best_student() is None
