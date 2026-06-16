# Decoupling slow computation from a fast control loop — durable

The pattern behind a fast feedback loop fed by a slow planner.

## 1. Heavy variable-time computation runs OUTSIDE the fast loop
**Heuristic:** Motion planning, perception, optimization, IK — anything **data-dependent and variable** — must **not** run synchronously inside the fast control loop. Run it as a **separate, lower-rate, lower-priority** activity; the loop runs at a fixed high rate and consumes only the **latest available result**. Gating the loop on the planner forces the loop's effective period **up to the planner's worst-case time**, destroying the periodicity the controller depends on. (`ros2_control` makes this structural: a real-time `SCHED_FIFO` `read→update→write` thread, separate from a non-RT thread for ROS comms and planning.)
**Detect:** Does the design call a planner/IK/perception/optimizer from inside the same loop or thread that emits actuator commands every cycle?
*Source:* Buttazzo Ch.1–2; `ros2_control` architecture (control.ros.org). *Confidence: High.*

## 2. Interpolate the slow result up to the loop rate
**Heuristic:** The planner emits **sparse waypoints** (or a parameterized trajectory) at a slow/irregular cadence; the RT loop **interpolates a smooth setpoint at every tick** (cubic/quintic Hermite, or linear on position/velocity), keeps **tracking the in-progress segment** between plan arrivals, and requests a fresh setpoint only when the current segment's time domain expires — with a **defined fallback** (e.g. braking) if the next plan is late or lost. This is what lets a 250 Hz–1 kHz loop (fast for closed-loop stability/sensor sampling) have a valid target **every** cycle while the planner updates at a few Hz. Anti-pattern: a loop that only moves when a fresh result arrives → idle/jerky actuator.
**Detect:** Does the fast loop interpolate/resample and keep tracking between updates, or only move when a fresh planner result arrives?
*Source:* real-time trajectory-interpolation literature; ROS2 `joint_trajectory_controller`. *Confidence: High.*

## 3. The hand-off must be NON-BLOCKING on the control thread
**Heuristic:** The fast loop must **never block/wait/spin** on the slow producer — no blocking-acquire mutex, no blocking queue read, no condition-variable wait. A lock **may** be *shared* with the producer **as long as the RT side only ever `try_lock`s and proceeds on failure** (returns the last value) — exactly what `ros2_control`'s `RealtimeBuffer` (`readFromRT` uses `try_to_lock`) and `RealtimePublisher` (best-effort `try_publish`, drops if held) do. The reason blocking is forbidden: the **producer's critical section is unbounded** (it may allocate, page-fault, do I/O), so it falls **outside** the bounded-blocking guarantee of PI/ceiling protocols → **unbounded** priority inversion. (Bounded blocking on a short, bounded critical section under PI/PCP is a legitimate, deterministic pattern — it's the *unbounded producer* that forbids blocking here.) Standard mechanisms: double-buffer / atomic pointer swap, SPSC lock-free, seqlock.
**Detect:** Can the control loop ever block/wait/spin (or allocate/fault/do I/O) reading the planner output — vs. grabbing the latest published value (or a non-blocking try) and continuing?
*Source:* `ros2_control` `realtime_tools`; Buttazzo Ch.7; ROS 2 RT design rule ("RT threads should never be blocked on non-RT threads"). *Confidence: High.*

## 4. Bound the queue; for control, keep only the latest
**Heuristic:** An **unbounded** queue with a sustained producer/consumer rate mismatch is a **latency/memory bug** — the backlog grows without bound (by flow conservation: ∫(arrival−departure) > 0) until OOM. (Little's law is a **steady-state** identity and does **not** govern this unstable-growth regime; its durable lesson is only that, at fixed throughput, a deeper queue means proportionally higher latency.) **Bound every hot-path queue** with an explicit full-policy: drop-oldest / drop-newest / **overwrite-latest** / backpressure. For the **planner→control** hand-off, use a **single-slot overwrite "latest value"** buffer (for a closed-loop controller, **staleness matters more than completeness**). A bounded **FIFO** is correct only where ordered execution is required (a small lookahead buffer of trajectory segments).
**Detect:** Is there an unbounded queue between producer and control loop, or a FIFO-drain where the loop should consume the **latest** and discard stale results?
*Source:* bounded-queue/backpressure literature (Reactive Streams; bufferbloat); `ros2_control` `RealtimeBuffer`. *Confidence: High.*

---
**Live API → context7.** **Related:** `hotpath.md` (the loop body rules), `priority-inversion.md` (why the unbounded producer breaks PI guarantees), `ros2-system-design` (the `ros2_control` thread split), `robotic-line-design` (Little's law done right).
