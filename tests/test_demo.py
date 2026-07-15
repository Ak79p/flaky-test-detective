import random


def test_pass() -> None:
    """A reliably passing test."""
    assert True


def test_fail() -> None:
    """A reliably broken test."""
    assert False


def test_flaky() -> None:
    """An unstable, intermittent test to verify Flaky classification."""
    # This will randomly fail or pass, allowing us to exercise the
    # Flaky Detective multi-run capture and classification logic!
    assert random.random() > 0.5