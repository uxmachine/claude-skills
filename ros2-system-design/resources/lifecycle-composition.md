# ROS2 managed lifecycle & composition — durable traps

Bring-up determinism + process topology. **Exact API (`use_intra_process_comms`, transition callbacks) via `context7` (resolve `rclcpp`/`rclpy`).**

## 1. Composition decouples node granularity from process topology
**Heuristic:** Write nodes as **components** (`rclcpp::Node` subclasses compiled to shared libraries, **no `main()`**) and choose the process layout — one shared container vs separate processes — as a **deploy-time** decision (launch / `ros2 component load`), without changing or recompiling node code.
**Detect:** Is the process boundary hard-coded (a `main()` per node), instead of authoring components and picking the container layout at deploy time?
*Source:* design.ros2.org "Composition". *Confidence: High.*

## 2. Intra-process comms is NOT automatic
**Heuristic:** Same-process nodes do **not** auto-get the in-process fast path. It is **opt-in on BOTH endpoints** (`NodeOptions.use_intra_process_comms`, or per-endpoint), and the manager only matches a pair with the **same topic + compatible QoS**. A message goes intra-process **only when ALL matched subscriptions are in the same process**; any other subscription is served over DDS.
**Detect:** Does the design assume two nodes in one process get zero-copy without enabling intra-process on both ends?
*Source:* design.ros2.org "Intra-process Communications". *Confidence: High.*

## 3. Intra-process zero-copy depends on message OWNERSHIP
**Heuristic:** Zero-copy needs a message published as a **`unique_ptr`** and subscribers that don't contend for ownership: a single owning subscriber → **0 copies**; N owners → **N−1 copies** (last gets the original); subscribers taking `shared_ptr<const>` share one buffer → 0 copies. **Ownership demand**, not merely being in-process, sets the copy count. (Publishing an already-shared `shared_ptr` deep-copies — publish `unique_ptr` or use loaned messages.)
**Detect:** Is zero-copy claimed regardless of `unique_ptr` vs `shared_ptr` and how many subscribers take ownership?
*Source:* design.ros2.org "Intra-process Communications". *Confidence: High.*

## 4. Inactive ≠ auto-suppressed — guard your own subs/timers
**Heuristic:** A managed node in **Inactive** is *designed* to be dormant, but that dormancy is a **contract over MANAGED entities, not a framework guarantee**. Only lifecycle-aware entities gate automatically (a `LifecyclePublisher` drops publishes while Inactive). **Ordinary `create_subscription` / `create_wall_timer` callbacks on a `LifecycleNode` STILL FIRE while Inactive** — you must enforce dormancy (cancel/recreate timers on activate/deactivate, or guard the callback on the active state).
**Detect:** Does the code assume the framework suppresses incoming data / timers in the Inactive state? (It doesn't — the #1 lifecycle bug.)
*Source:* design.ros2.org "Managed nodes"; rclcpp #1838/#1846. *Confidence: High.*

## 5. Managed lifecycle = orchestrator-driven, ordered bring-up
**Heuristic:** A managed node sits in **Unconfigured until transitioned** — it does **not** start executing merely by being launched (unlike a plain node). The point is an external tool driving `configure → activate` so everything is instantiated/configured **before** anything runs. Self-configure/activate on startup (autostart) is **possible but discouraged** (it interferes with external coordination) — so the durable default is orchestrator-driven ordering, not "nodes can never self-activate."
**Detect:** Does the design assume a managed node publishes/acts on launch, or that self-activation is impossible?
*Source:* design.ros2.org "Managed nodes". *Confidence: High.*

## 6. Transition-callback pairing — and "no hardware in configure" is wrong
**Heuristic:** Pair the transitions: **configure ↔ cleanup** (Unconfigured ↔ Inactive), **activate ↔ deactivate** (Inactive ↔ Active). `configure` sets up state and **may start communicating with hardware and reading state**, but must avoid lengthy init and must **not energize power or command actuators**; `activate` does fast final prep and acquires active-only resources (power, command interfaces, streaming). In `ros2_control`, **hardware comms + state reads begin in Inactive (`on_configure`)**; only **power/actuation is gated to Active (`on_activate`)** — so the rule is "**no actuation/power in configure**," not "no hardware in configure." `deactivate` **should reverse** activate (+ safe-stop), not be an exact inverse.
**Detect:** Does the reasoning ban all hardware access in `configure`, or treat `deactivate` as a literal mirror of `activate`?
*Source:* design.ros2.org "Managed nodes"; control.ros.org Hardware Components. *Confidence: High.*

---
**Live API → context7.** Method names / autostart args evolve; resolve via `context7`/docs. See `contested.md` for the intra-process `transient_local` history. **Related:** `dds-control.md`.
