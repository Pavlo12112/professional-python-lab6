import json

import pytest

from student_app.config import AppConfig
from student_app.exceptions import ImportDataError
from student_app.pipeline import process

pytestmark = pytest.mark.integration

ROWS = (
    "1,Anna,Koval,PI-21,90\n"
    "2,Oleh,Melnyk,PI-21,55\n"
    "3,Iryna,Bondar,PI-22,x\n"
    "4,,Boyko,PI-22,70\n"
    "5,Petro,Novak,PI-23,70\n"
)


def test_tolerant_pipeline_imports_validates_reports_and_exports(write_csv, output_dir):
    config = AppConfig(60.0, True, output_dir / "students.json")

    result = process(write_csv(ROWS), config)

    exported = json.loads((output_dir / "students.json").read_text(encoding="utf-8"))
    assert [row["student_id"] for row in exported] == [1, 5]
    assert result.exported == 2
    assert [e.line_number for e in result.errors] == [4, 5]
    assert result.report["count"] == 2
    assert result.report["average"] == pytest.approx(80.0)
    assert result.report["best"]["student_id"] == 1
    assert result.report["by_group"] == {"PI-21": 1, "PI-23": 1}


def test_strict_pipeline_stops_at_invalid_record_and_writes_nothing(write_csv, output_dir):
    config = AppConfig(60.0, False, output_dir / "students.json")

    with pytest.raises(ImportDataError, match="average_grade"):
        process(write_csv(ROWS), config)

    assert not (output_dir / "students.json").exists()
