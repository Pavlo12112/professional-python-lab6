"""Atomic JSON export."""

import json
from collections.abc import Iterable
from pathlib import Path

from student_app.exceptions import ExportError
from student_app.models import Student


def export_students_json(students: Iterable[Student], path: Path) -> int:
    """Write students as a JSON array; the previous file survives any failure."""
    temporary = path.with_name(path.name + ".tmp")

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = [student.to_dict() for student in students]
        temporary.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        temporary.replace(path)
    except OSError as error:
        temporary.unlink(missing_ok=True)
        raise ExportError(f"Cannot write {path}") from error
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise

    return len(data)
