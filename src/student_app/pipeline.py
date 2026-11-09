"""Whole use case: import -> validation -> filtering -> report -> export."""

from dataclasses import dataclass
from pathlib import Path

from student_app.config import AppConfig
from student_app.exceptions import ImportDataError
from student_app.exporters import export_students_json
from student_app.importer import read_students
from student_app.models import Student
from student_app.reports import build_report


@dataclass(frozen=True)
class PipelineResult:
    students: list[Student]
    errors: list[ImportDataError]
    report: dict[str, object]
    exported: int


def process(input_path: Path, config: AppConfig) -> PipelineResult:
    errors: list[ImportDataError] = []
    students = list(
        read_students(input_path, skip_invalid=config.skip_invalid, errors=errors)
    )
    selected = [s for s in students if s.average_grade >= config.minimum_grade]
    report = build_report(students, config.minimum_grade)
    exported = export_students_json(selected, config.output_path)
    return PipelineResult(selected, errors, report, exported)
