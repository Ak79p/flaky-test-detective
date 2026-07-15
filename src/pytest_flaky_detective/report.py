from pytest_flaky_detective.classifier import Classification, TestClassifier
from pytest_flaky_detective.collector import SessionCollector


class ConsoleReporter:
    """Handles parsing test records and rendering analytical summaries to the console."""

    @staticmethod
    def render(collector: SessionCollector) -> None:
        """Analyze histories in the collector and format a clean terminal summary.

        Includes an explicit numbered visual trace for multi-attempt histories.
        """
        tests = collector.all_tests()

        counts = {
            Classification.PASS: 0,
            Classification.BROKEN: 0,
            Classification.FLAKY: 0,
        }

        print("\n" + "=" * 16 + " Flaky Detective Summary " + "=" * 16)

        for test in tests:
            if test.attempts:
                classification = TestClassifier.classify(test)
                counts[classification] += 1

                # Build a chronological visual trace using explicit attempt numbers
                # e.g., "1: FAILED, 2: FAILED, 3: PASSED"
                trace_elements = [
                    f"{attempt.attempt_number}: {attempt.outcome.upper()}"
                    for attempt in test.attempts
                ]
                history_trace = ", ".join(trace_elements)

                print(f"\n{test.nodeid}")
                print(f"Classification : {classification.value}")
                print(f"History        : {history_trace}")
                print(f"Attempts       : {len(test.attempts)}")

        print("\n" + "-" * 57)
        print(f"PASS    : {counts[Classification.PASS]}")
        print(f"BROKEN  : {counts[Classification.BROKEN]}")
        print(f"FLAKY   : {counts[Classification.FLAKY]}")
        print("=" * 57)