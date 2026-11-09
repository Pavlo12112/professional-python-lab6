"""Experiments 1 and 2: a weak test executes code, a strong test verifies the result.

Run:  pytest experiments/test_exp1_2_weak_vs_strong.py -k weak
      pytest experiments/test_exp1_2_weak_vs_strong.py -k strong        (fails on purpose)
"""

import pytest

from buggy import buggy_average


def test_average_weak():
    buggy_average([10, 20, 30])  # the code is executed, but nothing is checked


def test_average_strong():
    assert buggy_average([10, 20, 30]) == pytest.approx(20)  # real result is 15.0
