"""Test-first. Stdlib only."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import rt_budget as q  # noqa: E402


def test_loop_budget_under():
    r = q.loop_budget(1000, [0.0003, 0.0002], max_utilization=0.8)
    assert abs(r["period_s"] - 0.001) < 1e-12
    assert abs(r["utilization"] - 0.5) < 1e-9
    assert abs(r["headroom_s"] - 0.0005) < 1e-12
    assert r["over_budget"] is False


def test_loop_budget_over():
    r = q.loop_budget(1000, [0.0009, 0.0003])
    assert r["utilization"] > 1.0
    assert r["over_budget"] is True


def test_loop_budget_single_scalar_wcet():
    r = q.loop_budget(500, 0.001)
    assert abs(r["utilization"] - 0.5) < 1e-9


def test_rm_bound_values():
    assert abs(q.rm_utilization_bound(1) - 1.0) < 1e-12
    assert abs(q.rm_utilization_bound(2) - 0.8284271247) < 1e-7


def test_rm_schedulable_sufficient():
    r = q.rm_schedulable([{"period": 0.010, "wcet": 0.003},
                          {"period": 0.020, "wcet": 0.004}])
    assert abs(r["utilization"] - 0.5) < 1e-9       # 0.3 + 0.2
    assert r["schedulable_sufficient"] is True       # 0.5 <= bound(2)=0.828
    assert r["feasible_necessary"] is True


def test_rm_infeasible_over_100pct():
    r = q.rm_schedulable([{"period": 0.010, "wcet": 0.008},
                          {"period": 0.010, "wcet": 0.004}])
    assert r["feasible_necessary"] is False          # U = 1.2 > 1
    assert r["schedulable_sufficient"] is False


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
