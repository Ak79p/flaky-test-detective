import time


def test_pass() -> None:
    """A test that always passes."""
    assert True

def test_fail() -> None:
    """A test that always fails."""
    assert False

def test_slow() -> None:
    """A test that simulates an operation taking noticeable time."""
    time.sleep(0.20)
    assert True
