import json
from pathlib import Path

import pytest

from student_app.exceptions import ExportError
from student_app.exporters import export_students_json


def test_export_writes_utf8_json_array(output_dir, student_factory):
    path = output_dir / "students.json"
    items = [
        student_factory(student_id=1, first_name="Олена", last_name="Коваль"),
        student_factory(student_id=2),
    ]

    count = export_students_json(items, path)

    data = json.loads(path.read_text(encoding="utf-8"))
    assert count == 2
    assert [row["student_id"] for row in data] == [1, 2]
    assert data[0]["first_name"] == "Олена"


def test_export_of_empty_collection_gives_empty_array(output_dir):
    path = output_dir / "empty.json"

    assert export_students_json([], path) == 0
    assert json.loads(path.read_text(encoding="utf-8")) == []


def test_export_creates_missing_directories(tmp_path, student):
    path = tmp_path / "a" / "b" / "students.json"

    export_students_json([student], path)

    assert path.exists()


def test_failed_export_keeps_previous_output(output_dir, student_factory):
    path = output_dir / "students.json"
    path.write_text("old valid data", encoding="utf-8")

    def broken_stream():
        yield student_factory(student_id=1)
        raise RuntimeError("stream failed")

    with pytest.raises(RuntimeError, match="stream failed"):
        export_students_json(broken_stream(), path)

    assert path.read_text(encoding="utf-8") == "old valid data"
    assert not path.with_name("students.json.tmp").exists()


def test_os_error_becomes_export_error_and_keeps_previous_output(output_dir, student, monkeypatch):
    path = output_dir / "students.json"
    path.write_text("old valid data", encoding="utf-8")

    def disk_full(self, *args, **kwargs):
        raise OSError("disk is full")

    monkeypatch.setattr(Path, "write_text", disk_full)

    with pytest.raises(ExportError, match="Cannot write") as exc_info:
        export_students_json([student], path)

    monkeypatch.undo()
    assert isinstance(exc_info.value.__cause__, OSError)
    assert path.read_text(encoding="utf-8") == "old valid data"
