from collections.abc import Generator
import pluggy
import pytest
from pytest import CallInfo, Config, Item, Parser, TestReport

from pytest_flaky_detective.classifier import Classification, TestClassifier
from pytest_flaky_detective.collector import SessionCollector
from pytest_flaky_detective.rerunner import RerunEngine

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
        help="Path to generate the flaky tests summary JSON report (default: flaky-report.json)"
    )

def pytest_configure(config: Config) -> None:
    """Initialize and attach the collector to the pytest session configuration."""
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
    """Render the final classified summary after running out-of-process reruns."""
    collector: SessionCollector = session.config.flaky_detective_collector  # type: ignore[attr-defined]
    
    # Retrieve configurations and calculate limits
    flaky_runs = int(session.config.getoption("--flaky-runs"))
    rerun_limit = flaky_runs - 1
    
    # Delegate rerun logic completely to the RerunEngine
    if rerun_limit > 0:
        RerunEngine.rerun_failed_tests(collector, rerun_limit)

    # ------------------ Reporting & Analysis ------------------
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
                print(f"  - Attempt {attempt.attempt_number}: {attempt.outcome.upper()} ({attempt.duration:.3f}s)")

    print("\n" + "-" * 57)
    print(f"PASS    : {counts[Classification.PASS]}")
    print(f"BROKEN  : {counts[Classification.BROKEN]}")
    print(f"FLAKY   : {counts[Classification.FLAKY]}")
    print("=" * 57)