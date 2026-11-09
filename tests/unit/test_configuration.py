import pytest
import yaml

from student_app.config import ENV_MINIMUM_GRADE, get_environment, load_config
from student_app.exceptions import ConfigurationError

VALID = "processing:\n  minimum_grade: 60\n  skip_invalid: true\noutput:\n  path: output/students.json\n"


@pytest.fixture
def config_file(tmp_path):
    def write(text: str = VALID):
        path = tmp_path / "config.yaml"
        path.write_text(text, encoding="utf-8")
        return path

    return write


def test_valid_configuration_is_loaded(config_file):
    config = load_config(config_file())

    assert config.minimum_grade == pytest.approx(60)
    assert config.skip_invalid is True
    assert config.output_path.name == "students.json"


def test_environment_variable_overrides_minimum_grade(config_file, monkeypatch):
    monkeypatch.setenv(ENV_MINIMUM_GRADE, "75")

    assert load_config(config_file()).minimum_grade == pytest.approx(75)


def test_non_numeric_environment_value_is_rejected(config_file, monkeypatch):
    monkeypatch.setenv(ENV_MINIMUM_GRADE, "abc")

    with pytest.raises(ConfigurationError, match="must be a number"):
        load_config(config_file())


@pytest.mark.parametrize("grade", [-1, 100.5, 101, 1000], ids=["negative", "just-above", "above", "huge"])
def test_minimum_grade_out_of_range_is_rejected(config_file, grade):
    text = VALID.replace("minimum_grade: 60", f"minimum_grade: {grade}")

    with pytest.raises(ConfigurationError, match="between 0 and 100"):
        load_config(config_file(text))


def test_missing_file_gives_configuration_error_with_cause(tmp_path):
    with pytest.raises(ConfigurationError, match="not found") as exc_info:
        load_config(tmp_path / "absent.yaml")

    assert isinstance(exc_info.value.__cause__, FileNotFoundError)


def test_invalid_yaml_gives_configuration_error_with_cause(config_file):
    with pytest.raises(ConfigurationError, match="Invalid YAML") as exc_info:
        load_config(config_file("a: [unclosed"))

    assert isinstance(exc_info.value.__cause__, yaml.YAMLError)


@pytest.mark.parametrize(
    "text",
    ["", "processing:\n  minimum_grade: 60\n", "output:\n  path: x.json\n"],
    ids=["empty-file", "no-output-section", "no-processing-section"],
)
def test_incomplete_structure_is_rejected(config_file, text):
    with pytest.raises(ConfigurationError, match="structure"):
        load_config(config_file(text))


def test_skip_invalid_must_be_boolean(config_file):
    text = VALID.replace("skip_invalid: true", "skip_invalid: maybe")

    with pytest.raises(ConfigurationError, match="true or false"):
        load_config(config_file(text))


def test_default_environment_name():
    assert get_environment() == "development"


def test_environment_name_from_variable(monkeypatch):
    monkeypatch.setenv("APP_ENV", "testing")

    assert get_environment() == "testing"
