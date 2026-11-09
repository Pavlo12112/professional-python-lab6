from datetime import datetime, timezone

import pytest

from student_app import reports


@pytest.fixture
def frozen_time(monkeypatch):
    """Deterministic time: the clock function is replaced by monkeypatch."""
    moment = datetime(2026, 11, 8, 12, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(reports, "utcnow", lambda: moment)
    return moment


def test_report_describes_all_students(students, frozen_time):
    report = reports.build_report(students)

    assert report["generated_at"] == "2026-11-08T12:00:00+00:00"
    assert report["count"] == 4
    assert report["average"] == pytest.approx(81.25)
    assert report["best"]["student_id"] == 3
    assert report["by_group"] == {"PI-21": 2, "PI-22": 2}


def test_report_filters_by_minimum_grade(students, frozen_time):
    report = reports.build_report(students, minimum_grade=80)

    assert report["count"] == 3
    assert report["by_group"] == {"PI-21": 2, "PI-22": 1}


def test_report_of_empty_collection(frozen_time):
    report = reports.build_report([])

    assert report["count"] == 0
    assert report["average"] == 0.0
    assert report["best"] is None
    assert report["by_group"] == {}


def test_utcnow_returns_timezone_aware_time():
    assert reports.utcnow().tzinfo is not None
