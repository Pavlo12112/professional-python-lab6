"""YAML configuration with environment override."""

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

import yaml

from student_app.exceptions import ConfigurationError

ENV_MINIMUM_GRADE = "STUDENT_APP_MINIMUM_GRADE"


@dataclass(frozen=True, slots=True)
class AppConfig:
    minimum_grade: float
    skip_invalid: bool
    output_path: Path


def get_environment() -> str:
    """Name of the environment, 'development' by default."""
    return os.getenv("APP_ENV", "development")


def load_config(path: Path, environ: Mapping[str, str] | None = None) -> AppConfig:
    env = os.environ if environ is None else environ

    try:
        with path.open("r", encoding="utf-8") as file:
            raw = yaml.safe_load(file)
    except FileNotFoundError as error:
        raise ConfigurationError(f"Configuration file not found: {path}") from error
    except yaml.YAMLError as error:
        raise ConfigurationError(f"Invalid YAML in {path}") from error

    try:
        minimum_raw = env.get(ENV_MINIMUM_GRADE, raw["processing"]["minimum_grade"])
        skip_invalid = raw["processing"]["skip_invalid"]
        output_path = Path(raw["output"]["path"])
    except (KeyError, TypeError) as error:
        raise ConfigurationError("Configuration structure is invalid") from error

    try:
        minimum_grade = float(minimum_raw)
    except (TypeError, ValueError) as error:
        raise ConfigurationError(f"minimum_grade must be a number, got {minimum_raw!r}") from error

    if not 0 <= minimum_grade <= 100:
        raise ConfigurationError("minimum_grade must be between 0 and 100")

    if not isinstance(skip_invalid, bool):
        raise ConfigurationError("skip_invalid must be true or false")

    return AppConfig(minimum_grade, skip_invalid, output_path)
