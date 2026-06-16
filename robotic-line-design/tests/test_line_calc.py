"""Test-first. Stdlib + pytest only."""
import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import line_calc as q  # noqa: E402


def test_takt_time():
    # 8h shift = 28800 s, demand 480 units -> 60 s/unit
    assert q.takt_time(28800, 480) == 60.0


def test_takt_zero_demand_raises():
    with pytest.raises(ValueError):
        q.takt_time(100, 0)


def test_line_balance_min_stations_and_delay():
    r = q.line_balance([10, 20, 30], 40)   # sum 60, ceil(60/40)=2, delay=(80-60)/80=0.25
    assert r["theoretical_min_stations"] == 2
    assert abs(r["balance_delay"] - 0.25) < 1e-9
    assert r["infeasible_tasks_s"] == []


def test_line_balance_flags_task_longer_than_takt():
    r = q.line_balance([10, 50], 40)       # 50 > 40 can't fit one station
    assert r["infeasible_tasks_s"] == [50]


def test_oee_multiplies():
    assert abs(q.oee(0.9, 0.95, 0.99) - 0.84645) < 1e-9


def test_oee_from_raw():
    r = q.oee_from_raw(planned_time_s=28800, downtime_s=2880,
                       ideal_cycle_s=50, total_count=460, good_count=450)
    assert abs(r["availability"] - 0.9) < 1e-9
    assert abs(r["performance"] - (50 * 460 / 25920)) < 1e-9
    assert abs(r["quality"] - 450 / 460) < 1e-9
    assert abs(r["oee"] - r["availability"] * r["performance"] * r["quality"]) < 1e-12


def test_littles_law_solves_each_missing():
    assert abs(q.littles_law(throughput=2, flow_time=5)["wip"] - 10) < 1e-9
    assert abs(q.littles_law(wip=10, flow_time=5)["throughput"] - 2) < 1e-9
    assert abs(q.littles_law(wip=10, throughput=2)["flow_time"] - 5) < 1e-9


def test_littles_law_needs_exactly_two():
    with pytest.raises(ValueError):
        q.littles_law(wip=10)


def test_utilization():
    assert abs(q.utilization(45, 60) - 0.75) < 1e-9


def test_tolerance_stack_wc_vs_rss():
    r = q.tolerance_stack([0.1, 0.1, 0.1, 0.1])
    assert abs(r["worst_case"] - 0.4) < 1e-9   # arithmetic sum
    assert abs(r["rss"] - 0.2) < 1e-9          # sqrt(4 * 0.01)


def test_process_capability_centered_and_offset():
    r = q.process_capability(mean=10, sigma=1, lsl=7, usl=13)
    assert abs(r["cp"] - 1.0) < 1e-9
    assert abs(r["cpk"] - 1.0) < 1e-9
    r2 = q.process_capability(mean=11, sigma=1, lsl=7, usl=13)
    assert abs(r2["cpk"] - (2.0 / 3.0)) < 1e-9   # off-center: min(2,4)/3
    assert r2["cpk"] < r2["cp"]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
