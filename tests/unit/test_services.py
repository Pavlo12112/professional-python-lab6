"""StudentService with test doubles: Mock for interaction, fake for state."""

from unittest.mock import Mock, create_autospec

import pytest

from student_app.exceptions import NotificationError, ValidationError
from student_app.protocols import Notifier, StudentRepository
from student_app.repositories import InMemoryStudentRepository
from student_app.services import StudentService


@pytest.fixture
def mock_repository() -> Mock:
    repository = Mock(spec=StudentRepository)
    repository.get.return_value = None
    return repository


def test_register_stores_student_and_sends_notification(student, mock_repository, notifier):
    service = StudentService(mock_repository, notifier)

    delivered = service.register(student)

    assert delivered is True
    mock_repository.get.assert_called_once_with(1)
    mock_repository.add.assert_called_once_with(student)
    notifier.send.assert_called_once_with("Anna Koval", "Registered in group PI-21")


def test_registering_duplicate_is_rejected_without_side_effects(student, mock_repository, notifier):
    mock_repository.get.return_value = student
    service = StudentService(mock_repository, notifier)

    with pytest.raises(ValidationError, match="already exists"):
        service.register(student)

    mock_repository.add.assert_not_called()
    notifier.send.assert_not_called()


def test_failed_notification_does_not_undo_registration(student, notifier):
    repository = InMemoryStudentRepository()
    notifier.send.side_effect = NotificationError("SMTP is down")
    service = StudentService(repository, notifier)

    delivered = service.register(student)

    assert delivered is False
    assert repository.get(1) == student
    notifier.send.assert_called_once()


def test_repository_failure_is_propagated_and_nobody_is_notified(student, mock_repository, notifier):
    mock_repository.add.side_effect = RuntimeError("database is down")
    service = StudentService(mock_repository, notifier)

    with pytest.raises(RuntimeError, match="database is down"):
        service.register(student)

    notifier.send.assert_not_called()


def test_find_by_id_delegates_to_repository(student, mock_repository, notifier):
    mock_repository.get.return_value = student
    service = StudentService(mock_repository, notifier)

    assert service.find_by_id(1) is student
    mock_repository.get.assert_called_once_with(1)


def test_find_by_last_name_uses_all_students_of_repository(students, mock_repository, notifier):
    mock_repository.all.return_value = students
    service = StudentService(mock_repository, notifier)

    result = service.find_by_last_name("Koval")

    assert [s.student_id for s in result] == [1, 4]
    mock_repository.all.assert_called_once_with()


def test_students_of_group_with_fake_repository(repository, notifier):
    service = StudentService(repository, notifier)

    assert [s.student_id for s in service.students_of_group("PI-21")] == [1, 2]


@pytest.mark.parametrize(
    ("group", "expected"),
    [(None, 81.25), ("PI-21", 85.0), ("PI-22", 77.5), ("XX-00", 0.0)],
    ids=["all", "pi-21", "pi-22", "unknown-group"],
)
def test_average_grade_overall_and_by_group(repository, notifier, group, expected):
    service = StudentService(repository, notifier)

    assert service.average_grade(group) == pytest.approx(expected)


def test_best_student_with_fake_repository(repository, notifier):
    best = StudentService(repository, notifier).best_student()

    assert best is not None
    assert best.last_name == "Bondar"


def test_empty_registry_has_no_best_student_and_zero_average(notifier):
    service = StudentService(InMemoryStudentRepository(), notifier)

    assert service.best_student() is None
    assert service.average_grade() == 0.0


def test_plain_mock_with_spec_does_not_check_call_signature():
    notifier = Mock(spec=Notifier)

    notifier.send("only recipient")  # wrong call, but the mock accepts it

    notifier.send.assert_called_once_with("only recipient")


def test_autospec_detects_wrong_call_signature():
    notifier = create_autospec(Notifier, instance=True)

    with pytest.raises(TypeError):
        notifier.send("only recipient")
