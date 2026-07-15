import subprocess
import time

from pytest_flaky_detective.collector import SessionCollector


class RerunEngine:
    """Orchestrates executing failed tests in isolated subprocess environments."""

    @staticmethod
    def rerun_failed_tests(
        collector: SessionCollector,
        rerun_limit: int,
    ) -> None:
        """Identify and execute a batch of isolated reruns for failed/
          tests up to the rerun limit.

        Spawns a clean pytest subprocess for each failed test to guarantee
        perfect test isolation and prevent in-process state/fixture contamination.
        """
        failed_tests = collector.failed_tests()
        if not failed_tests:
            return

        print(f"\n[Flaky Detective] Rerunning {len(failed_tests)} failed tests...")

        for test in failed_tests:
            for _ in range(rerun_limit):
                start_time = time.perf_counter()

                # Spawn clean out-of-process pytest execution
                result = subprocess.run(
                    ["pytest", test.nodeid, "-q", "--no-summary"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                duration = time.perf_counter() - start_time
                outcome = "passed" if result.returncode == 0 else "failed"

                # Record the new attempt back into the collector
                collector.record(
                    nodeid=test.nodeid,
                    outcome=outcome,
                    duration=duration,
                )
