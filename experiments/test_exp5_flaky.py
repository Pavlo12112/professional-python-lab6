"""Experiment 5: flaky and deterministic versions of the same check.

Run the bad test many times (PowerShell):
    1..10 | ForEach-Object { pytest experiments/test_exp5_flaky.py -k bad -q }
"""

import random


def test_random_bad():
    assert random.randint(1, 2) == 1  # passes only in about half of the runs


def test_random_deterministic(monkeypatch):
    monkeypatch.setattr(random, "randint", lambda a, b: 1)

    assert random.randint(1, 2) == 1  # always passes: the randomness is controlled
