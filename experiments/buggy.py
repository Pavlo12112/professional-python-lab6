"""Function with a deliberate defect for experiments 1 and 2."""


def buggy_average(values: list[float]) -> float:
    """Wrong on purpose: divides by len(values) + 1."""
    return sum(values) / (len(values) + 1)
