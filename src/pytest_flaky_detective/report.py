from pytest_flaky_detective.classifier import Classification, TestClassifier
from pytest_flaky_detective.collector import SessionCollector


class ConsoleReporter:
    """Handles parsing test records and rendering analytical summaries to the console./
    """

    @staticmethod
    def render(collector: SessionCollector) -> None:
        """Analyze histories in the collector and format a clean terminal summary."""
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

                print(f"\n{test.nodeid}")
                print(f"Classification : {classification.value}")
                print(f"Attempts       : {len(test.attempts)}")
                for attempt in test.attempts:
                    print(
                        f"  - Attempt {attempt.attempt_number}: "
                        f"{attempt.outcome.upper()} ({attempt.duration:.3f}s)"
                    )

        print("\n" + "-" * 57)
        print(f"PASS    : {counts[Classification.PASS]}")
        print(f"BROKEN  : {counts[Classification.BROKEN]}")
        print(f"FLAKY   : {counts[Classification.FLAKY]}")
        print("=" * 57)
