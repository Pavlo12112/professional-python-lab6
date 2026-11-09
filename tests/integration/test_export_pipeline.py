import json

import pytest

from student_app.exporters import export_students_json
from student_app.models import Student

pytestmark = pytest.mark.integration


def test_json_round_trip_restores_equal_students(output_dir, student_factory):
    path = output_dir / "students.json"
    original = [
        student_factory(student_id=1, first_name="Олена", last_name="Савчук", average_grade=87.1),
        student_factory(student_id=2, group="PI-22", average_grade=0),
    ]

    export_students_json(original, path)
    restored = [Student(**row) for row in json.loads(path.read_text(encoding="utf-8"))]

    assert restored == original


def test_second_export_replaces_first_atomically(output_dir, student_factory):
    path = output_dir / "students.json"
    export_students_json([student_factory(student_id=1)], path)

    export_students_json([student_factory(student_id=1), student_factory(student_id=2)], path)

    assert len(json.loads(path.read_text(encoding="utf-8"))) == 2
    assert [p.name for p in output_dir.iterdir()] == ["students.json"]
