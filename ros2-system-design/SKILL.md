---
name: ros2-system-design
description: Use when structuring or debugging a ROS2 system — QoS compatibility, executors & callback groups, managed lifecycle, node composition / intra-process comms, DDS discovery (ROS_DOMAIN_ID / RMW), or the ros2_control real-time boundary. Holds the durable concepts + traps; fetches exact current API via context7. Defers to system-architecture-design for system structure and realtime-determinism for hot-path rules.
---

# ROS2 system design — durable concepts, traps, and a QoS checker

ROS2's foot-guns are concurrency, QoS matching, lifecycle, and the real-time boundary — and the failures are usually **silent** (no error, just no data / a deadlock). This skill holds the **durable** concepts and traps; it **delegates exact current API to `context7` / docs.** Read only the resource whose step is live.

## Procedure (route, don't dump)

1. **"Subscriber gets no messages" / choosing QoS?** → open `resources/qos.md`. Run `scripts/qos_compat.py <pair.json>` (`{"pub":{...},"sub":{...}}`) to check Request-vs-Offered compatibility (reliability / durability / deadline / liveliness; history & lifespan are local-only). Incompatible = silent no-connection.
2. **Concurrency / a callback hangs / a service call deadlocks?** → open `resources/executors.md` (single- vs multi-threaded; the default-MutuallyExclusive group; the sync-call-in-callback deadlock — cause is the shared MX group, fix is a separate/Reentrant group + MultiThreadedExecutor or `call_async`).
3. **Bring-up ordering / one process vs many / managed nodes?** → open `resources/lifecycle-composition.md` (Inactive does NOT auto-suppress ordinary subs/timers; intra-process is opt-in on both ends; zero-copy depends on message ownership; the configure-vs-activate hardware boundary).
4. **Nodes don't discover each other / RMW / the control loop?** → open `resources/dds-control.md` (`ROS_DOMAIN_ID` is a hard boundary; LAN isn't isolated at defaults; cross-RMW services can fail; `ros2_control` is a fixed-rate RT read→update→write loop, not topics).
5. **Need an exact signature / current default?** → fetch from `context7` (resolve `rclcpp` / `rclpy` / `ros2_control`) or the docs. The skill names the *concept*; context7 has the *current API*.
6. Version-fragile / oversimplified points live in `resources/contested.md`.

## Tools

- `scripts/qos_compat.py <pair.json>` — pub-vs-sub QoS Request-vs-Offered compatibility (the durable RxO inequalities; history/depth/lifespan correctly ignored as local). `tests/test_qos_compat.py`.

## Scope guards

- System structure / coupling / boundaries → `system-architecture-design`.
- Real-time hot-path budgets / scheduling / priority inversion → `realtime-determinism`.
- A specific runtime failure → `superpowers:systematic-debugging`.

---

### Improving this skill (every session you use it)

After using this skill, ask: **one-time fix, or forever?** If a correction / example / edge-case should apply every future time, add it to the right `resources/` file now. If you re-derived an analysis by hand, add it to a tool.

**Related:** `system-architecture-design` · `realtime-determinism` · `isaac-curobo` · `superpowers:systematic-debugging`.
