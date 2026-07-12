from pytest import Parser


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
