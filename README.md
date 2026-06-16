# claude-skills

Personal Claude Code skills (uxmachine). Each top-level directory is one skill, symlinked into `~/.claude/skills/`.

## Skills

- **`system-architecture-design`** — review/diagnose the architecture of an existing software or platform system for simplicity, loose coupling, and longevity. Grounded in verified sources (Brooks, Ousterhout, DORA, evolutionary architecture, ROS2/`ros2_control`, ISA-95/UNS). Carries manufacturing (ISA-95/MES) and robotics-runtime domain knowledge as on-demand resources, and ships a small deterministic `architecture_scan.py` (file-size / import-boundary / duplicated-tree checks) with its own test.
- **`isaac-curobo`** — durable cuRobo / OpenUSD / Isaac-ROS judgment + traps for the NVIDIA robotics stack: guarantee-vs-penalty collision semantics, world-representation tradeoffs, USD unit/up-axis/physics-schema traps, NITROS per-edge negotiation, the ESDF-not-TSDF planning world, REP-103/105 frames. Exact (churning) API is delegated to `context7`; the skill holds only the durable concepts. Ships `collision_config_check.py` and `asset_lint.py` with tests. Part of the robotics/ROS/manufacturing portfolio (`docs/specs/2026-06-16-robotics-skills-portfolio-design.md`).
- **`ros2-system-design`** — durable ROS2 structure judgment + traps: QoS Request-vs-Offered compatibility (the silent no-connection bug), executor/callback-group deadlocks (cause = a shared MutuallyExclusive group, not a busy thread), managed-lifecycle bring-up (Inactive does **not** auto-suppress ordinary subs/timers), composition & intra-process zero-copy conditions, `ROS_DOMAIN_ID`/RMW discovery, and the `ros2_control` real-time loop. Exact API delegated to `context7`. Ships `qos_compat.py` (RxO compatibility checker) with tests.
- **`robotic-line-design`** — durable robotic assembly line/cell math + DFA judgment: takt vs cycle time vs throughput, line balancing (min-stations lower bound, over-takt infeasibility), OEE (multiply A·P·Q; >100 % = measurement error), Little's law / utilization queueing blow-up, tolerance stack-up (worst-case **and** RSS, with the assumptions), Cp/Cpk (one-sided exception), single-direction DFA build-up, dexterous-workspace reach, deliberate buffer sizing. Owns the *physical line math*; ISA-95/MES integration architecture defers to `system-architecture-design`. Ships `line_calc.py` with tests. `realtime-determinism` to follow.

## Install (symlink a skill into Claude Code)

```sh
ln -s "$PWD/system-architecture-design" ~/.claude/skills/system-architecture-design
ln -s "$PWD/isaac-curobo"               ~/.claude/skills/isaac-curobo
ln -s "$PWD/ros2-system-design"         ~/.claude/skills/ros2-system-design
ln -s "$PWD/robotic-line-design"        ~/.claude/skills/robotic-line-design
```

## Run the tests

```sh
PYTHONPATH= python3 -m pytest -q        # all skills (PYTHONPATH= avoids a sourced-ROS pytest-plugin leak)
```
(No third-party dependencies — standard library only.)

## House rules (how these skills stay good)

These follow the four rules from *"How Anthropic Engineers ACTUALLY Prompt Claude Code"*:

1. **Skills, not prompts** — repeatable tasks live here as skills, not as one-off chat prompts.
2. **More than prompts** — invest in the tools layer (scripts + reference files), not just the instructions.
3. **Composable, not custom** — small focused skills that defer to each other; never one mega-skill. Don't rebuild what `superpowers`/built-ins already do (`brainstorming`, `systematic-debugging`, `/simplify`, `claude-md-improver`).
4. **Smarter every session** — after using a skill, ask *"one-time fix, or forever?"* If forever, write the rule/example/edge-case into the skill **now**. The compounding loop is the whole point.

## Scope

These are *meta* skills for how I work — deliberately **not** SMC product code, and **not** in the SMC org. Domain knowledge inside a skill stays general/portable; org-specific audits live outside this repo.
