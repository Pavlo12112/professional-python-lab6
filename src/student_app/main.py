"""Command line entry point."""

import argparse
from collections.abc import Sequence
from pathlib import Path

from student_app.config import load_config
from student_app.exceptions import StudentAppError
from student_app.pipeline import process


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Student registry")
    parser.add_argument("--config", type=Path, default=Path("config.yaml"))
    parser.add_argument("--input", type=Path, default=Path("data/students.csv"))
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
        result = process(args.input, config)
    except StudentAppError as error:
        print(f"Error: {error}")
        return 1

    print(
        f"Exported {result.exported} students, skipped {len(result.errors)} invalid records, "
        f"average {result.report['average']}"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
