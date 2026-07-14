from collections.abc import Generator

import pluggy
import pytest
from pytest import CallInfo, Config, Item, Parser, TestReport

from pytest_flaky_detective.collector import SessionCollector


def pytest_addoption(parser: Parser) -> None:
    """Register Flaky Detective command-line options."""
    parser.addoption(
        "--flaky-runs",
        action="store",
        default=1,
        type=int,
        help="Number of times to rerun a test if it fails (example --flaky-runs=3)"
    )

    parser.addoption(
        "--flaky-report",
        action="store",
        default="flaky-report.json",
        type=str,
        help="Path to generate the flaky tests summary JSON report /"
        "(default: flaky-report.json)"
    )

def pytest_configure(config: Config) -> None:
    """Initialize and attach the collector to the pytest session configuration."""
    # Use a unique namespaced attribute name to prevent collision with other plugins
    config.flaky_detective_collector = SessionCollector()  # type: ignore[attr-defined]

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(
    item: Item,            # noqa: ARG001
    call: CallInfo[None],  # noqa: ARG001
) -> Generator[None, pluggy.Result[TestReport], None]:
    """Hook wrapper to safely observe test outcomes during the call phase."""
    outcome = yield
    report: TestReport = outcome.get_result()

    if report.when == "call":
        collector: SessionCollector = item.config.flaky_detective_collector  # type: ignore[attr-defined]
        collector.record(
            nodeid=report.nodeid,
            outcome=report.outcome,
            duration=report.duration
        )

def pytest_sessionfinish(
    session: pytest.Session,
    exitstatus: int,  # noqa: ARG001
) -> None:
    """Render the final summary from data stored in the collector."""
    collector: SessionCollector = session.config.flaky_detective_collector  # type: ignore[attr-defined]
    tests = collector.all_tests()

    print("\n" + "=" * 16 + " Flaky Detective " + "=" * 16)
    print(f"Collected Tests : {len(tests)}")

    for test in tests:
        if test.attempts:
            latest = test.latest_attempt
            print(f"\n{test.nodeid}")
            print(f"Outcome : {latest.outcome}")
            print(f"Attempts: {len(test.attempts)}")
