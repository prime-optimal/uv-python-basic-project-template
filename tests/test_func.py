"""Tests for the main functionality."""

from test_project.func import random_sum


def test_random_sum():
    """Test random_sum function."""
    assert random_sum(1) < 101
    assert random_sum(100) < 200
