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

        Implements the structured classification algorithm:
        1. Read initial attempt.
        2. If initial attempt passed -> PASS.
        3. Else (initial failed), check if *any* subsequent attempt passed -> FLAKY.
        4. Else (all attempts failed) -> BROKEN.
        """
        if not history.attempts:
            raise ValueError("Cannot classify a test with no attempts.")

        initial_attempt = history.attempts[0]

        # 1. Initial attempt check
        if initial_attempt.outcome == "passed":
            return Classification.PASS

        # 2. Check if *any* subsequent attempt recovered to 'passed'
        # This scales naturally if we later support richer outcomes (like xfail/skipped)
        subsequent_attempts = history.attempts[1:]
        if any(attempt.outcome == "passed" for attempt in subsequent_attempts):
            return Classification.FLAKY

        # 3. All runs failed
        return Classification.BROKEN
