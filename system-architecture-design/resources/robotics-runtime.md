# Robotics runtime architecture

Decision-oriented. Pull this when reviewing/designing a robot execution stack (ROS2, planning, control, hardware seams). Sources: ROS2 / `ros2_control` official docs, Macenski et al. (*Science Robotics*), Iovino/Colledanchise BT survey, Ahmad & Babar systematic mapping. Where a claim was contested or refuted, it is marked.

## 1. Standardize on a substrate, hide it behind a driver seam

ROS2 is itself a worked example of the principles in `principles.md`:
- It standardizes on a proven communication substrate (DDS — chosen for UDP transport, distributed discovery, built-in security) rather than a custom protocol.
- It hides that substrate behind an **interchangeable abstraction** (`rmw`, with shared logic in `rcl`) so the middleware vendor can swap without application-code changes.

**Encode the *pattern*, not DDS specifically.** The substrate choice is contested today (Zenoh cuts discovery traffic ~97–99%; iceoryx for shared-memory). The durable lesson: *standardize on one proven substrate and confine it behind a single driver/HAL seam* — so swapping it is a one-file change, not a 12-file change.

**Detect violation:** grep for the vendor SDK constructor (e.g. `XArmAPI(`, `from xarm`). If it is constructed at many sites across many files, there is no HAL seam — hardware coupling is diffused through application logic.
**Fix:** one `ArmController`-style Protocol; construct the vendor SDK in exactly one factory/adapter; everything else takes the interface. A `Sim<Controller>` implementing the same Protocol gives hardware-free tests. (This is hexagonal/ports-and-adapters, `principles.md`.)

## 2. Composition — decouple logical granularity from process topology

Write nodes as **components** that can be allocated to any process by configuration. Logical node boundaries (what's a clean unit) should not be dictated by how many OS processes you want at runtime.

## 3. The real-time / planning-vs-execution boundary

Keep heavy compute (planning, IK, collision-checking, vision) **off** the real-time control/execution loop.

- `ros2_control` is the canonical pattern: a hardware-agnostic framework with a **kernel/HAL seam** (abstracts hardware; manages lifecycle, communication, access control) beneath reusable controllers, and **asynchronous / side-load controllers** that run heavy calculations without injecting jitter into the control loop.
- Concrete budget rule: at a 100 Hz controller manager, the sum of controller update times must stay under 10 ms (one cycle) — else go async. Make this a **fitness function** (assert the loop budget in CI/bench).
- Pattern that works in practice: an offline/compile-time planner (e.g. cuRobo, ~10–50 ms/segment) produces pre-baked trajectories; a thin executor streams waypoints at servo rate (e.g. 250 Hz) and never imports the planner. An import-boundary test (executor must not import the planner) is the fitness function that keeps the seam honest.

**Detect violation:** planner/`MotionGen`/IK imports inside the executor or control-loop file; live-robot command code inside an offline/bake tool.

## 4. Layered, component/service-oriented — not monolithic

Robotic systems are inherently layered (each layer encapsulates a functionality and hides lower-level detail). The mature direction is component-/service-oriented with decoupled, fault-contained layers and a clear deliberative (planning) vs reactive (real-time) split. *(Directional conclusion; the specific OO→component→service→cloud taxonomy is from 2016–17 literature but the layered/HAL conclusion holds and is stronger in current ROS2 production guidance.)*

## 5. Behavior Trees vs FSMs — task-dependent, no universal winner

- **BTs** are modular by design (every node shares one return interface, so any subtree is a relocatable/reusable building block). They win when a control policy must be **modified or reused later**. Steeper learning curve.
- **FSMs** are easier to conceive for **short tasks in controlled environments**; without enforced hierarchy they lack structural interfaces (not modular).
- **Caveat (a real smell):** BT modularity **breaks when blackboard / shared mutable state is introduced** — that is hidden coupling; treat heavy blackboard use as a smell.
- **Do NOT claim** BTs scale O(1) vs FSMs O(n) (or "linear vs quadratic"). That quantitative scaling claim was **refuted** in verification. The defensible advantage is modularity/reuse only.

## Quick review checklist

- [ ] One HAL/driver seam; vendor SDK constructed in one place. (`grep` the constructor.)
- [ ] Executor does not import the planner; heavy compute off the RT loop. (import-boundary test.)
- [ ] RT loop budget stated and asserted.
- [ ] No live-execution code inside an offline/bake tool.
- [ ] BT-vs-FSM choice matches task lifetime; no hidden blackboard coupling.
- [ ] Components allocatable to processes by config, not hard-wired.
