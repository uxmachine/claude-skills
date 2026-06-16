# ROS2 QoS — Request-vs-Offered compatibility (durable)

The single biggest source of "my topic publishes but the subscriber never gets messages." Run `scripts/qos_compat.py` on a pub/sub pair. **Exact profile constants change by distro — resolve via `context7` (resolve `rclcpp`/`rclpy`) or the docs.**

## 1. Incompatible QoS → silent no-connection
**Heuristic:** An incompatible pub/sub QoS pair **never matches at the DDS layer** → no data flows, and ROS2 raises **no error/exception by default**. (Since Foxy/Galactic a non-fatal warning is logged; the incompatibility is observable via the `*_incompatible_qos` QoS-event callbacks.)
**Detect:** When debugging "subscriber receives nothing," is QoS incompatibility on the candidate list — alongside topic name, node liveness, and network — or overlooked?
*Source:* design.ros2.org "About QoS Settings"; ROS2 "QoS Compatibility"; RTI Connext RxO. *Confidence: High.*

## 2. Only four policies are RxO; the rest are local
**Heuristic:** Only **reliability, durability, deadline, liveliness (+ its lease)** participate in Request-vs-Offered compatibility and can break a connection. **History (KEEP_LAST/KEEP_ALL), depth, lifespan are LOCAL** — they change buffering/expiry but never prevent matching.
**Detect:** Does the reasoning claim a history-mode / depth / lifespan mismatch stopped a pub/sub from connecting? It cannot.
*Source:* ROS2 "QoS compatibility"; design.ros2.org "Deadline, Liveliness, and Lifespan". *Confidence: High.*

## 3. Reliability: offered ≥ requested
**Heuristic:** `RELIABLE > BEST_EFFORT`; publisher (offered) must be ≥ subscriber (requested). **Broken pair = BEST_EFFORT publisher + RELIABLE subscriber.** RELIABLE pub + BEST_EFFORT sub is fine.
**Detect:** Is the broken direction identified correctly (not reversed, not "any mix breaks")?
*Source:* ROS2 QoS reliability table; RTI Connext RxO. *Confidence: High.*

## 4. Durability: offered ≥ requested, an independent gate
**Heuristic:** `TRANSIENT_LOCAL > VOLATILE`; offered ≥ requested. **Broken = VOLATILE publisher + TRANSIENT_LOCAL subscriber** (the classic broken "latched" topic). Checked **independently** of reliability — compatible reliability + incompatible durability still fails.
**Detect:** Is VOLATILE-pub + TRANSIENT_LOCAL-sub flagged, and durability treated as a separate gate (both must pass)?
*Source:* ROS2 QoS durability table; RTI Connext. *Confidence: High.*

## 5. Deadline & liveliness: the DURATION inequalities FLIP
**Heuristic:** Kind follows the usual direction (liveliness `MANUAL_BY_TOPIC > AUTOMATIC`, offered ≥ requested). But **durations flip — a shorter interval is the stronger promise**: deadline compatible iff **offered period ≤ requested period**; liveliness compatible iff offered kind ≥ requested **AND offered lease ≤ requested lease**.
**Detect:** For deadline/liveliness, is the period/lease direction (offered ≤ requested) used, not a mechanical "offered ≥ requested"?
*Source:* OMG DDS spec; design.ros2.org "Deadline, Liveliness, and Lifespan"; RTI Connext RxO. *Confidence: High.*

## 6. RxO is asymmetric — reason about offered vs requested, not equality
**Heuristic:** Always **publisher = offered, subscriber = requested**, evaluated in that fixed direction. The same two values can be compatible one way and not the other. Don't ask "are the two QoS equal?" — ask "does the offered satisfy the requested?"
**Detect:** Is matching treated as symmetric/equality, or correctly as directional offered-satisfies-requested?
*Source:* RTI Connext "RxO Property"; design.ros2.org. *Confidence: High.*

## 7. Built-in profiles mix badly — match the full profile both ends
**Heuristic:** The default profile is **RELIABLE/VOLATILE**; the **sensor-data** profile is **BEST_EFFORT/VOLATILE**. So a node **publishing with the sensor-data profile won't serve a subscriber left on the default (reliable)** — silently. Reliability isn't the only axis; a durability/deadline/liveliness mismatch breaks it too. Match the *whole* profile on both ends.
**Detect:** Are a sensor-data publisher and a default-profile subscriber assumed to interoperate?
*Source:* `ros2/rmw` `qos_profiles.h`; design.ros2.org QoS profiles / REP-2003. *Confidence: High (values are distro-stable; treat exact depths as version-pinned).*

---
**Live API → context7.** Exact profile constants (`rmw_qos_profile_*`), depth defaults, and per-distro warning behavior change; resolve via `context7`/docs. The tool `scripts/qos_compat.py` encodes the durable RxO rules above. **Related:** the executor/callback-group traps are in `executors.md`.
