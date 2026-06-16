# ROS2 DDS discovery & the ros2_control RT boundary — durable

Why nodes do/don't see each other, and the real-time control seam. **Exact env-var/API names via `context7` (resolve `ros2`/`ros2_control`).**

## 1. ROS_DOMAIN_ID is a hard discovery boundary, not a namespace
**Heuristic:** Nodes discover and talk only to other nodes on the **same `ROS_DOMAIN_ID`** (default 0). The domain id **seeds the discovery UDP ports** — it is a hard DDS/RTPS boundary, not a cosmetic label; different domains **cannot even discover** each other. Same domain is **necessary but not sufficient** (`ROS_LOCALHOST_ONLY` / `ROS_AUTOMATIC_DISCOVERY_RANGE`, RMW-vendor mismatch, incompatible QoS, unreachable network can still block). Pick a domain in **0–101**.
**Detect:** Does the answer assume two nodes communicate without confirming the same domain id, or call domain ids a namespacing label?
*Source:* ROS2 docs "The ROS_DOMAIN_ID". *Confidence: High.*

## 2. At defaults, the LAN is NOT isolated
**Heuristic:** Default domain 0 + DDS simple discovery (SPDP multicast) means processes **auto-discover across the LAN subnet** at current defaults (`ROS_AUTOMATIC_DISCOVERY_RANGE=SUBNET`; the docs intend the default to become `LOCALHOST` later). **Isolation is opt-in** — give separate launches/robots/teams **distinct `ROS_DOMAIN_ID`s**; don't assume they're isolated, and set the discovery range explicitly if you depend on a scope.
**Detect:** Are two robots/teams on one LAN at default settings assumed isolated, with no distinct domain ids?
*Source:* ROS2 docs "The ROS_DOMAIN_ID". *Confidence: High.*

## 3. Cross-vendor RMW interop is not guaranteed
**Heuristic:** Nodes on **different RMW implementations** communicate in many cases but **not all** — and the breakage is **asymmetric**: pub/sub topics over RTPS usually interoperate, but **request/reply (services, and therefore actions) can fail** across vendors (the documented case: `rmw_connextdds ↔ rmw_cyclonedds_cpp`). Use the **same ROS version + same RMW** across a distributed system.
**Detect:** Does the answer assert any two ROS2 nodes interoperate because "they all use DDS/RTPS," ignoring RMW-mixing breakage (esp. services/actions)?
*Source:* ROS2 docs "Different middleware vendors". *Confidence: High.*

## 4. ros2_control is a fixed-rate RT loop, not pub/sub
**Heuristic:** At the controller↔hardware boundary, `controller_manager` runs a **fixed-rate real-time loop**: each cycle **read() hardware → update() all active controllers → write() commands**, via the Resource Manager's **interface method calls — not ROS topic callbacks** (`update_rate` default 100 Hz, configurable). Controllers reach hardware **only through exported state/command interfaces** (`hardware_interface` = the HAL seam), never the driver directly. The hot path (`update()`, `read()`/`write()`) must be **RT-safe: no allocation, blocking, locks, or logging** (`get_lifecycle_state()` is flagged not-RT-safe). Heavy/non-deterministic work (planning, perception, I/O) goes **outside**, crossing in via a `realtime_tools` **single-writer hand-off** (note: `RealtimeBuffer` is a *try-lock*, not truly lock-free; `LockFreeQueue` is the lock-free one).
**Detect:** Is the CM↔hardware path modeled as topics/pub-sub, or is allocation/logging/locking/blocking placed inside `update()`/`read()`/`write()`?
*Source:* control.ros.org `controller_manager` + `hardware_interface` userdocs; `realtime_tools`. *Confidence: High.*

---
**Live API → context7.** Env-var defaults (discovery range), RMW names, and `realtime_tools` primitives change; resolve via `context7`/docs. See `contested.md` for the `realtime_tools` / `update_rate` version notes. **Related:** `realtime-determinism` owns the general RT hot-path rules; `system-architecture-design` owns the HAL-seam / coupling view.
