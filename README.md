# Student App - automated testing

Laboratory work No. 6 for the course "Professional Python":
automated testing with pytest (variant 1, student registry).

## Description

Small student registry used as the object of testing:

    CSV -> import and validation -> filtering -> report -> atomic JSON export

with a YAML configuration, an application service over injected
`StudentRepository` and `Notifier` (Protocols) and an asynchronous service.
The test suite contains unit tests, integration tests, fixtures,
parametrization, `tmp_path`, `monkeypatch`, `Mock`, `AsyncMock` and coverage.

## Requirements

Python 3.11+

## Installation

    python -m venv .venv

Activate the virtual environment
(Windows: `.venv\Scripts\activate`, Linux/macOS: `source .venv/bin/activate`).

    python -m pip install -e ".[dev]"

## Run the application

    python -m student_app.main --config config.yaml --input data/students.csv

## Run the tests

Whole suite with statement and branch coverage and HTML report
(one command, the same for CI):

    pytest -v --cov=student_app --cov-branch --cov-report=term-missing --cov-report=html

Other useful commands:

    pytest -m "not integration"          # only unit tests
    pytest -m integration                # only integration tests
    pytest tests/unit/test_models.py     # one file
    pytest -k "boundary"                 # tests by name
    pytest -x --tb=short                 # stop at first failure

The coverage threshold (80%) is set in `pyproject.toml`
(`[tool.coverage.report] fail_under`).

## Experiments

The `experiments/` folder is not collected by default. Use `--cov-fail-under=0`
for partial coverage runs:

    pytest experiments/test_exp1_2_weak_vs_strong.py -k weak
    pytest experiments/test_exp1_2_weak_vs_strong.py -k weak --cov=experiments --cov-report=term-missing --cov-fail-under=0
    pytest experiments/test_exp1_2_weak_vs_strong.py -k strong
    pytest experiments/test_exp3_partial.py --cov=experiments --cov-branch --cov-report=term-missing --cov-fail-under=0
    pytest experiments/test_exp3_full.py --cov=experiments --cov-branch --cov-report=term-missing --cov-fail-under=0
    pytest experiments/test_exp5_flaky.py

## Project structure

- `src/student_app/` - production code.
- `tests/conftest.py` - shared fixtures.
- `tests/unit/` - unit tests.
- `tests/integration/` - integration tests (marker `integration`).
- `experiments/` - experiments 1, 2, 3 and 5.

## Author

Student: Tsiastun Pavlo
Group: FeP-33s
