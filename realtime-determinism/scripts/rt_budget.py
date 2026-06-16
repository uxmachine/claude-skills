"""Real-time budget math: control-loop period / headroom / utilization and rate-monotonic
(Liu & Layland) schedulability. Stdlib only.

A control loop is real-time only if its WORST-CASE work fits the period with headroom.
Rate-monotonic sufficient bound: U <= n(2^(1/n) - 1) -> ln 2 ~ 0.693 as n -> inf.
EDF is feasible iff U <= 1. The LL bound is SUFFICIENT, not necessary.
"""
from __future__ import annotations
import json
import sys


def loop_budget(rate_hz, wcet_s, max_utilization=1.0):
    """One loop at rate_hz with one or more WCET work items. Over budget if utilization > max."""
    if rate_hz <= 0:
        raise ValueError("rate_hz must be > 0")
    period = 1.0 / rate_hz
    items = wcet_s if isinstance(wcet_s, (list, tuple)) else [wcet_s]
    total = float(sum(items))
    util = total / period
    return {
        "period_s": period,
        "total_wcet_s": total,
        "utilization": util,
        "headroom_s": period - total,
        "over_budget": util > max_utilization,
    }


def rm_utilization_bound(n):
    """Liu & Layland least-upper-bound utilization for n fixed-priority periodic tasks."""
    if n <= 0:
        raise ValueError("n must be > 0")
    return n * (2.0 ** (1.0 / n) - 1.0)


def rm_schedulable(tasks):
    """tasks: list of {"period": T, "wcet": C}. Total utilization vs the LL sufficient bound and U<=1."""
    n = len(tasks)
    util = sum(float(t["wcet"]) / float(t["period"]) for t in tasks)
    bound = rm_utilization_bound(n) if n else 0.0
    return {
        "utilization": util,
        "ll_bound": bound,
        "schedulable_sufficient": util <= bound,   # sufficient — schedulable; above it, inconclusive (try response-time analysis)
        "feasible_necessary": util <= 1.0,          # necessary — above 1.0 no scheduler can meet all deadlines
    }


_OPS = {
    "loop_budget": lambda a: loop_budget(**a),
    "rm_utilization_bound": lambda a: {"bound": rm_utilization_bound(**a)},
    "rm_schedulable": lambda a: rm_schedulable(**a),
}


def main(argv):
    if len(argv) != 2:
        print('usage: rt_budget.py <spec.json>   # {"op": "loop_budget", "args": {...}}', file=sys.stderr)
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
