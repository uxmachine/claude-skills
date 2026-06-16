---
name: realtime-determinism
description: Use when designing or auditing a real-time control loop or hot path — RT scheduling, priority inversion / inheritance / ceiling, WCET & jitter budgets, what's forbidden in the hot path (allocation/blocking/logging/locks), or decoupling a slow planner from a fast control loop. Holds the durable concepts; fetches exact OS/API specifics via context7. Pairs with ros2-system-design for the ros2_control loop.
---

# Real-time & determinism — concepts, traps, and budget checks

Real-time failures are about the **worst case and jitter**, not the average — and they're where LLMs slip (calling a loop "fast enough" from the mean, putting a planner or a `logging.info` in the control loop, conflating priority inheritance with the ceiling protocol). This skill holds the durable concepts; it **delegates exact OS/API specifics to `context7` / man pages.** Read only the resource whose step is live.

## Procedure (route, don't dump)

1. **Scheduling / "is this real-time?" / WCET budget?** → `resources/scheduling.md`. Use `scripts/rt_budget.py` ops `loop_budget` (period/headroom/utilization) and `rm_schedulable` (Liu & Layland bound — sufficient — plus `U≤1` — necessary).
2. **Shared locks / a high-priority task missing deadlines?** → `resources/priority-inversion.md` (medium-task cause, inheritance vs ceiling, transitivity, the Pathfinder fix).
3. **What can run in the control loop?** → `resources/hotpath.md`. Run `scripts/hotpath_scan.py <file.py> [func]` to flag I/O, blocking, logging, lock-acquire, and allocation inside a loop body.
4. **A planner/perception feeding a fast loop?** → `resources/rate-decoupling.md` (run heavy work outside; interpolate up to the loop rate; non-blocking hand-off; bound the queue / keep-latest).
5. **A borderline OS/version detail?** → `resources/contested.md` (PREEMPT_RT knobs, RM-vs-EDF overload, allocator/GC exceptions, platform mutex defaults).
6. **Need an exact syscall / flag?** → fetch from `context7` (resolve `Linux sched` / `pthread` / `ros2_control`) or the man pages.

## Tools

- `scripts/rt_budget.py <spec.json>` — `loop_budget`, `rm_utilization_bound`, `rm_schedulable`. Period/headroom/utilization + rate-monotonic schedulability (LL sufficient test + `U≤1` necessary). `tests/test_rt_budget.py`.
- `scripts/hotpath_scan.py <file.py> [func]` — AST scan flagging I/O / blocking / logging / lock-acquire / allocation in a control-loop function. Heuristic (a clean scan is necessary, not sufficient). `tests/test_hotpath_scan.py`.

## Scope guards

- ROS2 structure / QoS / executors / the `ros2_control` boundary → `ros2-system-design`.
- Cell/line throughput & WIP math → `robotic-line-design`.
- System structure / HAL-seam coupling → `system-architecture-design`.
- A specific runtime failure to debug → `superpowers:systematic-debugging`.

---

### Improving this skill (every session you use it)

After using this skill, ask: **one-time fix, or forever?** If a correction / example / edge-case should apply every future time, add it to the right `resources/` file now. If you re-derived a budget by hand, add it to `rt_budget.py`; a new hot-path hazard, add it to `hotpath_scan.py`.

**Related:** `ros2-system-design` · `robotic-line-design` · `isaac-curobo` · `system-architecture-design` · `superpowers:systematic-debugging`.
