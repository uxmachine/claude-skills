# Design Spec — Robotics / ROS / Manufacturing Claude skill portfolio

- **Date:** 2026-06-16
- **Status:** Approved design (pre-implementation)
- **Owner:** uko (uxmachine)
- **Repo (target):** `uxmachine/claude-skills` → `~/claude-skills`, each skill symlinked into `~/.claude/skills`
- **Predecessor:** `2026-06-09-system-architecture-design-skill-design.md` (the first skill; this portfolio reuses its shape and house rules)

---

## 1. Problem

The user codes with Claude Code ~99% of the time across a robotics + manufacturing-automation stack and wants a **targeted, durable knowledge base "smarter than me"** — encoded as Claude skills — so that hard-won judgment, traps, and deterministic checks stop being re-derived every session.

The success target is **not** a SOTA survey. Two framing decisions (made during brainstorming) constrain everything:

1. **Portable / general, not SMC-specific.** The skills live in the personal `~/claude-skills` repo and carry **no** SMC/cuRobo-internal specifics. Rationale (user's words): *"the product will develop … the specific SMC and cuRobo stack will change. Good robotic principles are constant."* The SMC-specific layer, if ever wanted, is a separate future repo that builds on these.
2. **The bar = judgment + tools + conventions — never a fact-dump.** A principle earns a place only if **(a) the model reliably gets it wrong AND (b) it is durable** (survives a stack/version change). Anything that is merely "how robotics works" is cut. This is the same bar that makes the existing `system-architecture-design` skill good: it encodes contested, slow-moving *judgment* (Brooks/Ousterhout/DORA) plus a deterministic scanner — not facts.

### 1.1 The durable-vs-live split (key mechanism)

The user named the NVIDIA/Isaac/cuRobo stack as most important — but those APIs churn fast, which fights "durable." Resolution, applied to every skill that touches a fast-moving tool:

> **The skill holds the durable layer** — concepts, collision/sim semantics, failure modes, judgment, traps. **It explicitly delegates the *exact current API* to `context7` / official docs at runtime.** When cuRobo or Isaac Sim bumps a version, the judgment still holds; the API is always fetched fresh.

This is composability done right: the skill is the durable judgment layer; `context7` is the live-API layer.

## 2. Goals / Non-goals

**Goals**
- A small portfolio of **portable** skills across robotics-runtime, ROS2, real-time, and manufacturing-line design, each shaped like `system-architecture-design`: cited + confidence-tagged `resources/`, a deterministic tool in `scripts/`, and a test.
- Every skill names a **mistake-class the model reliably makes** and ships a tool that catches or prevents it.
- Content grounded in **durable canonical sources** (standards, seminal texts, design docs) via adversarially-verified deep research — not arXiv-of-the-month.

**Non-goals**
- No SMC/cuRobo-internal specifics (frames, part names, fork branches, hardware IPs). Those stay in `~/context/*`.
- No SOTA-survey / reference-encyclopedia skills (they age and the model half-knows them).
- No mega-skill. Each skill is one task; the one combined skill (§4.1) is sub-sectioned so it does not blur.
- No duplication of existing skills — defer to `system-architecture-design`, `superpowers:brainstorming`, `superpowers:systematic-debugging`, `/simplify`, `/code-review`.

## 3. Design constraints — the transcript's four rules

From *"How Anthropic Engineers ACTUALLY Prompt Claude Code"* (each skill is audited against these):

1. **Prompt skills, not Claude.** Each skill = one repeatable task. Durable knowledge is a *resource*; fast-moving API is delegated to `context7`.
2. **Skills are more than prompts** — description (trigger) + instructions (playbook) + **tools** (the leverage). Every skill ships a real, tested, deterministic script. *"If you can use code instead of AI, you should."*
3. **Composable, not custom.** Small, focused, cross-linked; defers to existing skills; no ceremony.
4. **Smarter every session.** A literal "one-time fix, or forever?" footer in each `SKILL.md`.

## 4. The portfolio (this batch — 4 skills)

| # | Skill | Mistake-class it kills | Deterministic tool | Durable vs live |
|---|---|---|---|---|
| 1 | **isaac-curobo** (combined) | confusing what a GPU planner *guarantees* vs *penalizes*; wrong collision-world representation; broken USD/URDF assets (units/up-axis/physics schema); Isaac ROS frame/zero-copy mistakes | collision-config / clearance validator **+** USD/URDF asset linter | concepts+traps in skill · API via `context7` |
| 2 | **ros2-system-design** | QoS mismatch ("messages never arrive"); callback-group deadlock; misplaced `ros2_control` RT boundary | QoS-compatibility checker | stable (ROS2 design docs are durable) |
| 3 | **robotic-line-design** | hand-wavy cell/line math: takt, balance, utilization, OEE, tolerance stack | takt / line-balance / utilization / OEE / tolerance-stack calculators | stable |
| 4 | **realtime-determinism** | alloc/blocking/logging in hot paths; priority inversion; planning-rate vs control-rate confusion | RT-budget calculator **+** hot-path hazard scan | stable |

**Build order:** **#1 first** (user's "most important"); under ultracode the per-skill deep-research runs can fan out in parallel, but each skill is *wired and reviewed one at a time* so the pattern can be corrected cheaply. "Done" per skill = `SKILL.md` + cited `resources/` + tool **with a passing test** + cross-links.

### 4.1 Skill 1 — `isaac-curobo` (combined, sub-sectioned)

**Trigger (description):** *Use when planning robot motion with cuRobo, authoring/importing robot or scene assets for Isaac Sim or OpenUSD, or wiring Isaac ROS / nvblox perception — covers the durable concepts, collision & sim semantics, and traps, and fetches exact current API via `context7`.*

The `SKILL.md` procedure **routes** to one resource so the combined skill never blurs:

- **`resources/curobo.md`** — *what a GPU motion planner optimizes vs guarantees* (collision cost as soft penalty vs hard feasibility — the durable principle behind the user's "feasibility is penetration-only" finding); world-representation tradeoffs (cuboid / mesh-SDF / sphere / voxel / nvblox-ESDF), incl. the **mesh-SDF search-radius ≥ min robot sphere** trap ("poison"); robot sphere-model coverage; MotionGen vs IKSolver; seeds & success gates (a tight position tolerance is *cost-only*, not a feasibility gate); trajopt vs graph search; free-axis tool-pose criteria.
- **`resources/usd-assets.md`** — OpenUSD composition arcs (reference / payload / sublayer / variant) and which to use when; **up-axis (Z vs Y)** and **meters-per-unit** (the recurring mm-vs-m scale bug); `UsdPhysics` schema (collision approximation, mass, joints); URDF↔USD importer pitfalls; instancing.
- **`resources/isaac-ros.md`** — NITROS type-adaptation / zero-copy (when it does and doesn't apply); GEMs; the **nvblox ESDF → cuRobo world** bridge; frame conventions (REP-103/105); GPU/CPU sync.

**Tools:**
- `collision_config_check.py` — given a robot sphere model + world-representation + margin/activation config, report whether the config **guarantees clearance** or only **penalizes penetration**, and flag the mesh search-radius "poison" condition and uncovered links. (Operates on the *concepts*; exact field names resolved via `context7` at use.)
- `usd_asset_lint.py` — parse USD/URDF: up-axis, meters-per-unit, missing/!approximated collision, mass/inertia sanity, scale heuristic, unresolved reference/payload paths.

**Live layer (`context7`):** cuRobo `MotionGenConfig` / `IKSolverConfig`, Omniverse Kit / Isaac Sim API, Isaac ROS package names. **Sources (durable):** cuRobo (Sundaralingam et al., ICRA 2023) — concepts; OpenUSD (AOUSD) + `UsdPhysics` schema; Isaac Sim / Isaac ROS / nvblox design docs (concepts); REP-103/105.
**Excluded:** Isaac Lab (RL) and Replicator (synthetic data) — heaviest, least-durable corner; out of scope per user.

### 4.2 Skill 2 — `ros2-system-design`

**Trigger:** *Use when structuring or debugging a ROS2 system — QoS, executors/callback groups, lifecycle nodes, node composition, DDS discovery, or the `ros2_control` boundary.*
**Principles:** QoS **RxO (request-vs-offered) compatibility** across reliability / durability / history / deadline / liveliness; executors (single vs multi-threaded) and callback groups (`MutuallyExclusive` vs `Reentrant`) — the **service-call-inside-an-MX-callback deadlock**; managed lifecycle nodes; DDS discovery + `ROS_DOMAIN_ID` + vendor differences; intra-process composition (when zero-copy applies); the `ros2_control` kernel/HAL + RT-loop boundary.
**Tool:** `qos_compat.py` — pub QoS vs sub QoS (or a topic YAML) → compatible? which axis fails? (encodes the actual DDS RxO rules; stdlib). **Test** ships with it.
**Sources:** design.ros2.org (QoS / executors / lifecycle / composition), DDS-RTPS spec, `ros2_control` docs, REP-2004. **Defers to:** `system-architecture-design` (architecture-level), `systematic-debugging`. **Cross-links:** `realtime-determinism`.

### 4.3 Skill 3 — `robotic-line-design`

**Trigger:** *Use when sizing or balancing a robotic assembly cell/line — takt, cycle time, station/line balancing, robot utilization, OEE, buffer/WIP, tolerance stack-up — or mapping it to ISA-95 / MES / UNS.*
**Principles:** takt = available/demand; cycle vs takt; line balancing (min stations = Σtask/takt, balance delay, precedence-constrained assignment); robot utilization & reach budgeting; OEE = A×P×Q; Little's law (WIP = throughput×cycle) + bottleneck; buffer sizing; tolerance stack (**worst-case vs RSS**); Cpk. ISA-95 levels + UNS as *context*, not centerpiece.
**Tools (pure math → ideal "code not AI"):** `takt.py`, `line_balance.py` (precedence-constrained min-station assignment), `oee.py`, `utilization.py`, `tolerance_stack.py` (WC + RSS), `cpk.py` — packaged as one CLI with sub-tests.
**Sources:** Groover *Automation, Production Systems*; Boothroyd DFMA; ISA-95 / IEC 62264; Little's law; ASME Y14.5 tolerance methods. **Boundary vs `system-architecture-design`:** that skill owns *integration/data architecture* (publish-don't-couple, UNS topic design, its `isa95-mes.md`); this skill owns *physical-line math + design*. Cross-link, do not duplicate.

### 4.4 Skill 4 — `realtime-determinism`

**Trigger:** *Use when designing or auditing a real-time control loop or hot path — scheduling, jitter/WCET budgets, priority inversion, lock-free vs locks, allocation/blocking in the loop, or matching planning-rate to control-rate.*
**Principles:** RT scheduling (`SCHED_FIFO`/`RR`/`DEADLINE`; RTOS vs PREEMPT_RT Linux); priority inversion + inheritance/ceiling; jitter / WCET / headroom (Σwork < period); **no alloc / blocking / syscall / logging in the hot path**; lock-free vs mutex (and when lock-free is premature); determinism vs throughput; the **slow-planner → fast-controller** rate decoupling + interpolation/resampling; bounded queues / backpressure.
**Tools:** `rt_budget.py` (rate→period→headroom; flags over-budget) + `hotpath_scan.py` (heuristic AST/regex flag of malloc/`new`, blocking I/O, logging, unbounded loops, lock acquisition inside RT-marked sections; Python first, C++ heuristic next). **Test** ships with each.
**Sources:** Liu & Layland (rate-monotonic); Sha et al. (priority inheritance); Buttazzo *Hard Real-Time Computing Systems*; PREEMPT_RT docs; ROS2 real-time design notes. **Defers to:** `ros2-system-design`, `system-architecture-design`.

## 5. Shared conventions (what "a skill" means in this repo)

```
~/claude-skills/<skill-name>/
  SKILL.md            # frontmatter (name + sharp description) + routing procedure; ends with the Rule-4 footer
  resources/*.md      # each principle SOURCED + CONFIDENCE-TAGGED; progressive disclosure (read only when its step is live)
  scripts/*.py        # deterministic tool(s), stdlib-only where possible
  tests/*             # at least one passing test per tool
```

- **The bar, written into each `SKILL.md` as a gate:** a principle is included only if the model reliably gets it wrong AND it is durable. "How X works" is cut.
- **Confidence tags** on every principle: High (primary/verbatim) / Medium (inference) / contested (→ a `contested.md` note). Refuted claims are recorded as "do NOT encode …" (as the predecessor does for the BT O(1)-vs-O(n) claim).
- **Rule-4 footer** + **Related skills** line in every `SKILL.md`.
- **Invocation flags:** considered per skill. None in this batch is risky (no deploy/send) or agent-only, so `user-invocable: false` / `disable-model-invocation` stay unused — reserved for a future SMC real-arm-execution skill.
- **Install:** symlink `~/claude-skills/<skill>` → `~/.claude/skills/<skill>` (same as the predecessor). `README.md` gets a row per new skill.

## 6. Research method (the "massive research")

Per skill, one **deep-research workflow** (ultracode-appropriate):

1. **Fan-out** searches across the canonical sources named above (standards, seminal texts, design docs).
2. **Fetch + deep-read** the primary sources (not summaries).
3. **Adversarially verify** each candidate principle — a skeptic agent tries to refute it or find the counter-case; majority-refuted claims are dropped or demoted to `contested.md`.
4. **Distill** survivors into `resources/*.md` with source + confidence tag.

Aimed at **durable** sources so the content does not age; bleeding-edge results are admitted only as clearly-tagged `contested.md` notes, never as load-bearing principles.

## 7. Backlog — next batch (recorded, NOT built now)

Per the user, these are *to be built later*, not part of this batch. Recorded so the trigger boundaries of the batch-1 skills are drawn with them in mind:

1. **assembly-process-planning (Layer A)** — liaison & AND/OR graphs, precedence, subassembly detection, stability, mating-direction (NDBG), DFA. *Highest-leverage future skill* (the user's differentiator; the model is weakest here; fully durable). Tool: sequence enumerator / precedence-DAG validator.
2. **grasp / fixture / insertion** — force/form closure, antipodal grasps, fixture synthesis, peg-in-hole/insertion strategy.
3. **force / contact control** — impedance/admittance, hybrid force-position, operational-space (the zone-3 contact loop).
4. **calibration / accuracy / metrology** — kinematic + hand-eye + TCP calibration, error budgets.

## 8. Risks / open questions

- **Combined-skill bloat (#1).** Mitigation: the routing procedure + three separate sub-resources keep each area sharp; re-evaluate a split if `SKILL.md` drifts toward a mega-skill.
- **"Durable concepts, live API" honesty.** If a skill's concept layer can't be stated without naming a churning API, that content belongs in `context7`-delegated guidance, not a baked principle. Audit each resource for this.
- **Tool feasibility.** The `hotpath_scan.py` and `collision_config_check.py` heuristics are the least-deterministic tools; start narrow (Python; concept-level config) and grow per Rule 4 rather than over-claim coverage.
- **Overlap with `system-architecture-design`.** `robotic-line-design` (line math) and `ros2-system-design` (ROS structure) both touch architecture; boundaries in §4.2/§4.3 must hold. Cross-link, never duplicate.
- **Source quality for line math.** Prefer textbooks/standards (Groover, ASME Y14.5) over vendor blogs; tag any vendor-sourced claim as the predecessor does.

## 9. Implementation notes

- Feature work isolated in worktree `…/worktrees/claude-skills/robotics-skills-portfolio` (branch `robotics-skills-portfolio` off dated dev `20260616_1910`); never commit to `main` (PR to integrate).
- Build to the predecessor's standard; commit each skill (and ideally each phase) separately for `commit-review`.
- After the batch, run `/revise-docs`; add a `README.md` row per skill and update the repo house-rules if anything changed.
