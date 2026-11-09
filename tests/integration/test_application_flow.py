import json

import pytest

from student_app.async_service import AsyncStudentService
from student_app.exceptions import NotFoundError
from student_app.main import main
from student_app.repositories import AsyncInMemoryStudentRepository

pytestmark = pytest.mark.integration

ROWS = "1,Anna,Koval,PI-21,90\n2,Iryna,Bondar,PI-22,96\n3,Bad,Row,PI-22,abc\n"


def write_config(tmp_path, *, skip_invalid="true"):
    path = tmp_path / "config.yaml"
    out = (tmp_path / "result.json").as_posix()
    path.write_text(
        f"processing:\n  minimum_grade: 60\n  skip_invalid: {skip_invalid}\noutput:\n  path: {out}\n",
        encoding="utf-8",
    )
    return path


def test_main_runs_whole_application_with_config_and_input(tmp_path, write_csv):
    config = write_config(tmp_path)

    code = main(["--config", str(config), "--input", str(write_csv(ROWS))])

    data = json.loads((tmp_path / "result.json").read_text(encoding="utf-8"))
    assert code == 0
    assert [row["student_id"] for row in data] == [1, 2]


def test_main_returns_error_code_for_missing_configuration(tmp_path):
    assert main(["--config", str(tmp_path / "absent.yaml")]) == 1


def test_main_returns_error_code_for_invalid_input_in_strict_mode(tmp_path, write_csv):
    config = write_config(tmp_path, skip_invalid="false")

    code = main(["--config", str(config), "--input", str(write_csv(ROWS))])

    assert code == 1
    assert not (tmp_path / "result.json").exists()


def test_environment_variable_changes_application_behaviour(tmp_path, write_csv, monkeypatch):
    monkeypatch.setenv("STUDENT_APP_MINIMUM_GRADE", "95")
    config = write_config(tmp_path)

    code = main(["--config", str(config), "--input", str(write_csv(ROWS))])

    data = json.loads((tmp_path / "result.json").read_text(encoding="utf-8"))
    assert code == 0
    assert [row["student_id"] for row in data] == [2]


def test_default_relative_paths_are_resolved_in_current_directory(tmp_path, write_csv, monkeypatch):
    write_csv(ROWS).rename(tmp_path / "input.csv")
    (tmp_path / "config.yaml").write_text(
        "processing:\n  minimum_grade: 0\n  skip_invalid: true\noutput:\n  path: out/students.json\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    code = main(["--config", "config.yaml", "--input", "input.csv"])

    assert code == 0
    assert (tmp_path / "out" / "students.json").exists()


@pytest.mark.asyncio
async def test_async_flow_with_real_fake_repository(students):
    service = AsyncStudentService(AsyncInMemoryStudentRepository(students))

    assert (await service.load(2)).last_name == "Melnyk"
    assert await service.average_grade() == pytest.approx(81.25)
    best = await service.best_student()
    assert best is not None and best.student_id == 3
    with pytest.raises(NotFoundError):
        await service.load(99)
