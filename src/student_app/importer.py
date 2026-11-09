"""CSV import with validation of every record."""

import csv
from collections.abc import Iterator
from pathlib import Path

from student_app.exceptions import ImportDataError, ValidationError
from student_app.models import Student

REQUIRED_COLUMNS = ("student_id", "first_name", "last_name", "group", "average_grade")


def parse_student_row(row: dict[str, str | None], line_number: int) -> Student:
    """Convert one CSV row to a Student; low-level errors keep their cause."""
    try:
        student_id = int(row["student_id"])  # type: ignore[arg-type]
    except (KeyError, TypeError, ValueError) as error:
        raise ImportDataError("Invalid student_id", line_number=line_number) from error

    try:
        grade = float(row["average_grade"])  # type: ignore[arg-type]
    except (KeyError, TypeError, ValueError) as error:
        raise ImportDataError("Invalid average_grade", line_number=line_number) from error

    try:
        return Student(
            student_id=student_id,
            first_name=(row.get("first_name") or "").strip(),
            last_name=(row.get("last_name") or "").strip(),
            group=(row.get("group") or "").strip(),
            average_grade=grade,
        )
    except ValidationError as error:
        raise ImportDataError(str(error), line_number=line_number) from error


def read_students(
    path: Path,
    *,
    skip_invalid: bool = False,
    errors: list[ImportDataError] | None = None,
) -> Iterator[Student]:
    """Stream valid students from a CSV file.

    In strict mode (default) the first invalid record raises ImportDataError.
    With ``skip_invalid=True`` invalid records are collected into ``errors``.
    """
    try:
        with path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)

            missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
            if missing:
                raise ImportDataError(f"Missing columns: {', '.join(missing)}")

            for line_number, row in enumerate(reader, start=2):
                try:
                    yield parse_student_row(row, line_number)
                except ImportDataError as error:
                    if errors is not None:
                        errors.append(error)
                    if skip_invalid:
                        continue
                    raise
    except OSError as error:
        raise ImportDataError(f"Cannot read file: {path}") from error
