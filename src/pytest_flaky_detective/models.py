from dataclasses import dataclass, field


@dataclass(frozen=True)
class AttemptResult:
    """Represents the execution outcome and duration of a single test attempt."""
    outcome: str
    duration: float

@dataclass
class TestHistory:
    """Execution history for one logical pytest test."""
    nodeid: str
    attempts: list[AttemptResult] = field(default_factory=list)

    @property
    def latest_attempt(self) -> AttemptResult:
        """Return the most recent execution attempt."""
        return self.attempts[-1]
