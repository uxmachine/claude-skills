# robotic-line-design Skill — Implementation Plan

> Executed inline (research Workflow + judgment authoring). Same shape as `isaac-curobo` / `ros2-system-design`.

**Goal:** Portable `robotic-line-design` skill — durable robotic assembly line/cell math + judgment, with a deterministic `line_calc` toolkit. Spec: `docs/specs/2026-06-16-robotics-skills-portfolio-design.md` §4.3.

**Architecture:** `SKILL.md` routes to `resources/{takt-balance,oee-throughput,tolerance-capability,line-design,contested}.md` (sourced + confidence-tagged, authored from an adversarially-verified research run) and ships `scripts/line_calc.py` (pure functions + JSON CLI) with tests. **Boundary:** this skill owns the *physical line math*; ISA-95/MES *integration architecture* stays in `system-architecture-design` (`isa95-mes.md`) — cross-link, don't duplicate.

**Tech:** Python stdlib (`math`, `json`); pytest. "Use code, not AI" — the math is the leverage.

## Tasks
1. **Research Workflow** (background): takt/balance · OEE/throughput · tolerance/capability · DFMA/cell finders → adversarial skeptics (Groover, Hopp & Spearman, Boothroyd DFMA, ASME Y14.5, ISA-95). Bar: model-reliably-wrong AND durable → baked; else contested; refuted dropped.
2. **`line_calc.py` (TDD, done):** `takt_time`, `line_balance` (min stations / balance delay / infeasible-task flag), `oee` + `oee_from_raw`, `littles_law` (solve the missing of 3), `utilization`, `tolerance_stack` (WC + RSS), `process_capability` (Cp/Cpk). 11 tests pass.
3. **Resources + SKILL.md** from verified findings — each principle: heuristic + detection question + source + confidence; explicit cross-link to `system-architecture-design` for the integration layer.
4. **Wire-up + merge:** README row, full suite, symlink, FF-merge to `main` + push, cleanup.

## Self-Review
- Spec §4.3 coverage: takt/balance/OEE/utilization/tolerance/Cpk tools (Task 2); ISA-95-as-context + DFMA judgment in resources (Tasks 1, 3); boundary vs the architecture skill stated (Task 3). ✓
- Tool code complete, type-consistent, tested. ✓
