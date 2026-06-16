---
name: robotic-line-design
description: Use when sizing or balancing a robotic assembly cell/line — takt, cycle time, station/line balancing, robot utilization, OEE, WIP/Little's law, buffer sizing, tolerance stack-up, or process capability (Cpk) — and for design-for-assembly and cell-layout judgment. Owns the physical line math; defers ISA-95/MES integration architecture to system-architecture-design.
---

# Robotic line design — the math the model fumbles, plus design judgment

Manufacturing line/cell math is textbook-stable and a place LLMs reliably slip (averaging what should multiply, treating takt as cycle time, defaulting to RSS, calling a process capable from Cp alone). This skill **owns the physical line math**; the **MES/integration architecture (ISA-95 Levels 0-4, UNS, B2MML) belongs to `system-architecture-design`**. Use code, not arithmetic-by-LLM: run `scripts/line_calc.py`.

## Procedure (route, don't dump)

1. **Takt / cycle time / station count / bottleneck?** → `resources/takt-balance.md`. Compute with `line_calc.py` ops `takt`, `line_balance`.
2. **OEE / WIP / throughput / utilization?** → `resources/oee-throughput.md`. Ops `oee`, `oee_from_raw`, `littles_law`, `utilization`. (Multiply A·P·Q; any factor >1 is a measurement error; mind Little's-law units.)
3. **Tolerance stack-up / process capability?** → `resources/tolerance-capability.md`. Ops `tolerance_stack` (worst-case **and** RSS), `process_capability` (Cp/Cpk). Establish whether worst-case is *required* before using RSS.
4. **Cell layout / DFA / fixturing / buffers?** → `resources/line-design.md` (single-direction build-up, DFA part-count reduction *before* sizing, dexterous-workspace reach, deliberate buffer sizing, ISA-95-as-vocabulary).
5. **A borderline definition?** → `resources/contested.md` (the "cycle time" dual meaning, TH ≤ r_b idealization, DFA constants, tool conventions).
6. **Integration / MES / data architecture?** → that's `system-architecture-design`, not this skill.

## Tool

- `scripts/line_calc.py <spec.json>` — `{"op": <name>, "args": {...}}`. Ops: `takt`, `line_balance`, `oee`, `oee_from_raw`, `littles_law`, `utilization`, `tolerance_stack`, `process_capability`. Pure functions, JSON in/out. `tests/test_line_calc.py`.

## Scope guards

- ISA-95 / MES / UNS integration architecture → `system-architecture-design`.
- Robot motion planning / reach feasibility in a specific cell → `isaac-curobo` (and a real planner); this skill reasons about reach/payload at the *design* level only.
- A specific runtime/throughput failure to debug → `superpowers:systematic-debugging`.

---

### Improving this skill (every session you use it)

After using this skill, ask: **one-time fix, or forever?** If a correction / example / edge-case should apply every future time, add it to the right `resources/` file now. If you re-derived a calculation by hand, add it to `line_calc.py`.

**Related:** `system-architecture-design` (integration architecture) · `isaac-curobo` · `ros2-system-design` · `realtime-determinism`.
