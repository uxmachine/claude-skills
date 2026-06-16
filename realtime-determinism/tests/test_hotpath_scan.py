"""Test-first. Stdlib only."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import hotpath_scan as q  # noqa: E402

SRC = '''
import time, logging
log = logging.getLogger()

def control_loop(state, lock):
    print("tick")
    time.sleep(0.001)
    log.info("x")
    lock.acquire()
    data = [i * 2 for i in range(10)]
    return data

def clean_loop(state):
    y = state * 2
    return y
'''


def codes(func):
    return {x.code for x in q.scan_source(SRC, func=func)}


def test_flags_hazards_in_named_function():
    c = codes("control_loop")
    assert {"io_call", "blocking_call", "logging_call", "lock_acquire", "alloc"} <= c


def test_clean_function_has_no_errors():
    f = q.scan_source(SRC, func="clean_loop")
    assert [x for x in f if x.severity == "error"] == []


def test_scans_all_functions_when_unspecified():
    assert any(x.code == "blocking_call" for x in q.scan_source(SRC))


def test_with_lock_flagged():
    src = "def loop():\n    with my_lock:\n        pass\n"
    assert any(x.code == "lock_with" for x in q.scan_source(src, func="loop"))


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
