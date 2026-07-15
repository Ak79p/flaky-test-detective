from pytest_flaky_detective.models import AttemptResult, TestHistory


class SessionCollector:
    """In-memory collection database for tracking test execution attempts."""

    def __init__(self) -> None:
        self._histories: dict[str, TestHistory] = {}

    def record(self, nodeid: str, outcome: str, duration: float) -> None:
        """Record a single test execution attempt."""
        if nodeid not in self._histories:
            self._histories[nodeid] = TestHistory(nodeid=nodeid)

        # Calculate attempt number (1-based index)
        attempt_number = len(self._histories[nodeid].attempts) + 1

        attempt = AttemptResult(
            attempt_number=attempt_number,
            outcome=outcome,
            duration=duration
        )
        self._histories[nodeid].attempts.append(attempt)

    def all_tests(self) -> list[TestHistory]:
        """Retrieve the execution history of all observed tests."""
        return list(self._histories.values())

    def failed_tests(self) -> list[TestHistory]:
        """Identify and return all tests whose most recent attempt was a failure."""
        return [
            history for history in self._histories.values()
            if history.attempts and history.latest_attempt.outcome == "failed"
        ]
