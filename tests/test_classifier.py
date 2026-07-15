import pytest
from pytest_flaky_detective.classifier import Classification, TestClassifier
from pytest_flaky_detective.models import AttemptResult, TestHistory


def test_classify_empty_history_raises_error() -> None:
    """An empty test history sequence should raise a ValueError."""
    history = TestHistory(nodeid="test_empty")
    with pytest.raises(ValueError, match="Cannot classify a test with no attempts"):
        TestClassifier.classify(history)


def test_classify_clean_pass() -> None:
    """A test that passes on its first attempt must be classified as PASS."""
    history = TestHistory(
        nodeid="test_pass",
        attempts=[AttemptResult(attempt_number=1, outcome="passed", duration=0.1)]
    )
    assert TestClassifier.classify(history) == Classification.PASS


def test_classify_solid_broken() -> None:
    """A test where every single attempt fails must be classified as BROKEN."""
    history = TestHistory(
        nodeid="test_fail",
        attempts=[
            AttemptResult(attempt_number=1, outcome="failed", duration=0.1),
            AttemptResult(attempt_number=2, outcome="failed", duration=0.1),
        ]
    )
    assert TestClassifier.classify(history) == Classification.BROKEN


def test_classify_flaky_recovery() -> None:
    """A failing test that eventually recovers to a pass must be classified as FLAKY."""
    history = TestHistory(
        nodeid="test_flaky",
        attempts=[
            AttemptResult(attempt_number=1, outcome="failed", duration=0.1),
            AttemptResult(attempt_number=2, outcome="passed", duration=0.1),
        ]
    )
    assert TestClassifier.classify(history) == Classification.FLAKY