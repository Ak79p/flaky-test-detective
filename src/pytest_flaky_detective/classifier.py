from enum import Enum

from pytest_flaky_detective.models import TestHistory


class Classification(Enum):
    """The final analytical classification of a test's execution history."""

    PASS = "PASS"
    BROKEN = "BROKEN"
    FLAKY = "FLAKY"


class TestClassifier:
    """Business logic engine to classify a test's execution history."""

    @staticmethod
    def classify(history: TestHistory) -> Classification:
        """Analyze the test attempts and determine its classification.

        Current behavior (Chunk 4):
            Single PASS -> PASS
            Single FAIL -> BROKEN

        Future behavior (Chunk 5):
            FAIL then PASS -> FLAKY
            FAIL then FAIL -> BROKEN
        """
        if not history.attempts:
            raise ValueError("Cannot classify a test with no attempts.")

        # In Chunk 4, each test has exactly 1 attempt.
        # We determine classification based on the outcome of this latest attempt.
        latest_attempt = history.latest_attempt
        outcome = latest_attempt.outcome

        if outcome == "passed":
            return Classification.PASS

        # TODO: Handle mixed-outcome attempts once rerun support is implemented in
        # Chunk 5.
        return Classification.BROKEN
