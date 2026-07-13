from collections.abc import Generator

import pluggy
import pytest
from pytest import CallInfo, Item, Parser, TestReport


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
        help="Path to generate the flaky tests summary JSON report \
            (default: flaky-report.json)"
    )

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(
    item: Item,        # noqa: ARG001
    call: CallInfo[None],  # noqa: ARG001
) -> Generator[None, pluggy.Result[TestReport], None]:
    """Hook wrapper to safely observe test outcomes during the call phase."""
    outcome = yield
    report: TestReport = outcome.get_result()

    if report.when == "call":
        print("\n================ Flaky Detective ================")
        print(f"{report.nodeid}")
        print(f"Outcome : {report.outcome}")
        print(f"Duration: {report.duration:.4f}s")
