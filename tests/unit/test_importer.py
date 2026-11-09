import pytest

from student_app.exceptions import ImportDataError, ValidationError
from student_app.importer import parse_student_row, read_students


def test_valid_csv_is_imported(write_csv):
    path = write_csv("1,Anna,Koval,PI-21,90\n2,Oleh,Melnyk,PI-21,80.5\n")

    result = list(read_students(path))

    assert [s.student_id for s in result] == [1, 2]
    assert result[1].average_grade == pytest.approx(80.5)


def test_header_only_file_gives_no_students(write_csv):
    assert list(read_students(write_csv(""))) == []


def test_non_numeric_grade_raises_error_with_line_number_and_cause(write_csv):
    path = write_csv("1,Anna,Koval,PI-21,abc\n")

    with pytest.raises(ImportDataError, match="average_grade") as exc_info:
        list(read_students(path))

    assert exc_info.value.line_number == 2
    assert isinstance(exc_info.value.__cause__, ValueError)


def test_grade_out_of_range_keeps_validation_error_as_cause(write_csv):
    path = write_csv("1,Anna,Koval,PI-21,105\n")

    with pytest.raises(ImportDataError) as exc_info:
        list(read_students(path))

    assert exc_info.value.line_number == 2
    assert isinstance(exc_info.value.__cause__, ValidationError)


@pytest.mark.parametrize(
    ("row", "fragment"),
    [
        ("x,Anna,Koval,PI-21,90", "student_id"),
        ("1,,Koval,PI-21,90", "first_name"),
        ("1,Anna,,PI-21,90", "last_name"),
        ("1,Anna,Koval,,90", "group"),
        ("0,Anna,Koval,PI-21,90", "student_id"),
    ],
    ids=["text-id", "no-first-name", "no-last-name", "no-group", "zero-id"],
)
def test_malformed_record_is_reported(write_csv, row, fragment):
    with pytest.raises(ImportDataError, match=fragment):
        list(read_students(write_csv(row + "\n")))


def test_skip_invalid_collects_errors_and_keeps_valid_students(write_csv):
    path = write_csv("1,Anna,Koval,PI-21,90\nx,Bad,Id,PI-21,80\n3,Iryna,Bondar,PI-22,95\n4,Oleh,Melnyk,PI-21,\n")
    errors: list[ImportDataError] = []

    result = list(read_students(path, skip_invalid=True, errors=errors))

    assert [s.student_id for s in result] == [1, 3]
    assert [e.line_number for e in errors] == [3, 5]


def test_strict_mode_yields_valid_records_before_the_first_error(write_csv):
    path = write_csv("1,Anna,Koval,PI-21,90\nx,Bad,Id,PI-21,80\n")
    stream = read_students(path)

    assert next(stream).student_id == 1
    with pytest.raises(ImportDataError):
        next(stream)


def test_missing_columns_are_detected(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("student_id,name\n1,Anna\n", encoding="utf-8")

    with pytest.raises(ImportDataError, match="Missing columns"):
        list(read_students(path))


def test_missing_file_raises_import_error_with_original_cause(tmp_path):
    with pytest.raises(ImportDataError, match="Cannot read file") as exc_info:
        list(read_students(tmp_path / "absent.csv"))

    assert isinstance(exc_info.value.__cause__, FileNotFoundError)


def test_row_without_grade_column_value_is_invalid():
    with pytest.raises(ImportDataError, match="average_grade") as exc_info:
        parse_student_row({"student_id": "1"}, line_number=7)

    assert exc_info.value.line_number == 7


def test_values_are_stripped_while_parsing():
    row = {
        "student_id": "5",
        "first_name": " Anna ",
        "last_name": " Koval",
        "group": "PI-21 ",
        "average_grade": "88.5",
    }

    student = parse_student_row(row, line_number=2)

    assert (student.first_name, student.last_name, student.group) == ("Anna", "Koval", "PI-21")
