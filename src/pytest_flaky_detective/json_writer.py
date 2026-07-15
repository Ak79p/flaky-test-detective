import json
import warnings
from pathlib import Path

from pytest_flaky_detective.classifier import TestClassifier
from pytest_flaky_detective.models import TestHistory


class JsonReportWriter:
    """Serializes test execution histories to a versioned, CI-consumable JSON report."""

    @staticmethod
    def write(tests: list[TestHistory], output_path: str) -> None:
        """Analyze test histories and write the formatted schema to the specified path.

        Safely handles file system errors (e.g., full disk, invalid path, permissions)
        by emitting a standard pytest warning instead of crashing the process.
        """
        summary_counts = {"pass": 0, "broken": 0, "flaky": 0}
        serialized_tests = []

        for test in tests:
            if not test.attempts:
                continue

            # Classify and increment summary counters
            classification = TestClassifier.classify(test)
            summary_counts[classification.value.lower()] += 1

            # Format individual attempts
            serialized_attempts = [
                {
                    "attempt": attempt.attempt_number,
                    "outcome": attempt.outcome,
                    "duration": round(attempt.duration, 4),
                }
                for attempt in test.attempts
            ]

            # Append structured test entry
            serialized_tests.append(
                {
                    "nodeid": test.nodeid,
                    "classification": classification.value,
                    "attempts": serialized_attempts,
                }
            )

        # Assemble final versioned schema payload
        payload = {
            "schema_version": 1,
            "summary": summary_counts,
            "tests": serialized_tests,
        }

        # Safe Production Write Layer
        try:
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
        except OSError as e:
            warnings.warn(
                f"[Flaky Detective] Failed to write report to '{output_path}': {e}/",
                category=UserWarning,
                stacklevel=2,
            )
