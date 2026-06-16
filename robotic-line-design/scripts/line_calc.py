"""Robotic assembly line-design math — the deterministic calculations the model fumbles.
takt, line balancing, OEE, Little's law, utilization, tolerance stack (worst-case + RSS),
process capability (Cp/Cpk). Pure functions + a JSON CLI. Stdlib only.

This skill owns the PHYSICAL line math; integration/MES architecture (ISA-95 wiring,
UNS topic design) belongs to the system-architecture-design skill.
"""
from __future__ import annotations
import json
import math
import sys


def takt_time(available_s: float, demand_units: float) -> float:
    """Demand rhythm = available production time per period / units demanded. NOT cycle time."""
    if demand_units <= 0:
        raise ValueError("demand_units must be > 0")
    return available_s / demand_units


def line_balance(task_times, takt: float) -> dict:
    """Theoretical-min stations + idle (balance delay). Flags tasks that can't fit one station.

    theoretical_min_stations = ceil(sum(task_times) / takt) is a LOWER BOUND; if any task
    exceeds takt it must be split or run in parallel stations, so the bound is optimistic.
    """
    if takt <= 0:
        raise ValueError("takt must be > 0")
    total = float(sum(task_times))
    infeasible = [t for t in task_times if t > takt]
    n = math.ceil(total / takt) if total > 0 else 0
    balance_delay = (n * takt - total) / (n * takt) if n > 0 else 0.0
    return {
        "total_work_s": total,
        "theoretical_min_stations": n,
        "balance_delay": balance_delay,      # idle fraction in [0, 1)
        "infeasible_tasks_s": infeasible,    # tasks > takt: must split or parallelize
    }


def oee(availability: float, performance: float, quality: float) -> float:
    """OEE = Availability x Performance x Quality (multiply, never add)."""
    return availability * performance * quality


def oee_from_raw(planned_time_s, downtime_s, ideal_cycle_s, total_count, good_count) -> dict:
    """Compute A/P/Q and OEE from raw shift numbers."""
    run_time = planned_time_s - downtime_s
    availability = run_time / planned_time_s if planned_time_s else 0.0
    performance = (ideal_cycle_s * total_count) / run_time if run_time else 0.0
    quality = good_count / total_count if total_count else 0.0
    return {
        "availability": availability,
        "performance": performance,
        "quality": quality,
        "oee": availability * performance * quality,
    }


def littles_law(wip=None, throughput=None, flow_time=None) -> dict:
    """WIP = throughput x flow_time. Provide exactly two (consistent units); returns all three."""
    if sum(x is not None for x in (wip, throughput, flow_time)) != 2:
        raise ValueError("provide exactly two of wip, throughput, flow_time")
    if wip is None:
        wip = throughput * flow_time
    elif throughput is None:
        throughput = wip / flow_time
    else:
        flow_time = wip / throughput
    return {"wip": wip, "throughput": throughput, "flow_time": flow_time}


def utilization(busy_time: float, available_time: float) -> float:
    if available_time <= 0:
        raise ValueError("available_time must be > 0")
    return busy_time / available_time


def tolerance_stack(tolerances) -> dict:
    """Worst-case (arithmetic sum) vs statistical RSS (sqrt of sum of squares).

    RSS is valid only for independent, centered, ~normal contributors; use worst-case when
    those assumptions fail (safety-critical, few parts, no statistical process control).
    """
    worst_case = float(sum(abs(t) for t in tolerances))
    rss = math.sqrt(sum(float(t) * float(t) for t in tolerances))
    return {"worst_case": worst_case, "rss": rss}


def process_capability(mean, sigma, lsl, usl) -> dict:
    """Cp = spread only; Cpk = accounts for centering. Cpk <= Cp always (equal only when centered)."""
    if sigma <= 0:
        raise ValueError("sigma must be > 0")
    cp = (usl - lsl) / (6 * sigma)
    cpk = min(usl - mean, mean - lsl) / (3 * sigma)
    return {"cp": cp, "cpk": cpk}


_OPS = {
    "takt": lambda a: {"takt_s": takt_time(**a)},
    "line_balance": lambda a: line_balance(**a),
    "oee": lambda a: {"oee": oee(**a)},
    "oee_from_raw": lambda a: oee_from_raw(**a),
    "littles_law": lambda a: littles_law(**a),
    "utilization": lambda a: {"utilization": utilization(**a)},
    "tolerance_stack": lambda a: tolerance_stack(**a),
    "process_capability": lambda a: process_capability(**a),
}


def main(argv) -> int:
    if len(argv) != 2:
        print('usage: line_calc.py <spec.json>   # {"op": "takt", "args": {...}}', file=sys.stderr)
        return 2
    with open(argv[1]) as fh:
        spec = json.load(fh)
    op = spec.get("op")
    if op not in _OPS:
        print(f"unknown op '{op}'; choose from {sorted(_OPS)}", file=sys.stderr)
        return 2
    print(json.dumps(_OPS[op](spec.get("args", {})), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
