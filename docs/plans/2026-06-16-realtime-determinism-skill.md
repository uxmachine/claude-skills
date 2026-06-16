# realtime-determinism Skill — Implementation Plan

> Executed inline (research Workflow + judgment authoring). Same shape as the other portfolio skills. Spec: `docs/specs/2026-06-16-robotics-skills-portfolio-design.md` §4.4.

**Goal:** Portable `realtime-determinism` skill — durable real-time / determinism judgment + two deterministic tools (RT-budget math, hot-path hazard scan). Last of the batch-1 portfolio.

**Architecture:** `SKILL.md` routes to `resources/{scheduling,priority-inversion,hotpath,rate-decoupling,contested}.md` (sourced + confidence-tagged, from an adversarially-verified research run) and ships `scripts/rt_budget.py` (loop period/headroom/utilization + Liu & Layland rate-monotonic bound) and `scripts/hotpath_scan.py` (AST scan for I/O / blocking / logging / locks / allocation in a marked function), each with tests.

**Tech:** Python stdlib (`ast`, `json`); pytest. Cross-links `ros2-system-design` (the `ros2_control` RT loop) and `system-architecture-design` (the HAL/RT-boundary view).

## Tasks
1. **Research Workflow** (background): scheduling · priority-inversion · hotpath · rate-decoupling finders → adversarial skeptics (Liu & Layland, Sha et al. priority inheritance, Buttazzo, SCHED_* man pages, PREEMPT_RT). Bar: model-reliably-wrong AND durable → baked; else contested; refuted dropped.
2. **Tools (TDD, done):** `rt_budget.py` (`loop_budget`, `rm_utilization_bound`, `rm_schedulable` — sufficient LL test + necessary U≤1); `hotpath_scan.py` (`scan_source` flags io/blocking/logging/lock/alloc per function). 10 tests pass.
3. **Resources + SKILL.md** from verified findings — each principle: heuristic + detection question + source + confidence.
4. **Wire-up + merge:** README row, full suite, symlink, FF-merge to `main` + push, cleanup. Completes batch 1.

## Self-Review
- Spec §4.4 coverage: RT-budget + hazard-scan tools (Task 2); scheduling / priority-inversion / hot-path / rate-decoupling judgment in resources (Tasks 1, 3); cross-links (Task 3). ✓
- Tool code complete, type-consistent, tested. ✓
