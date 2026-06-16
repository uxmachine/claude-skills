# Isaac ROS / nvblox / ROS frames — durable concepts & traps

Hardware-accelerated ROS2 + reconstruction. Concepts durable. **Exact package/topic/node names via `context7` (resolve `Isaac ROS`) or the docs.**

## 1. NITROS acceleration is per-edge and negotiated, not global
**Heuristic:** NITROS = **type adaptation (REP-2007) + type negotiation (REP-2009)**: adjacent nodes advertise supported types and the framework picks the format at runtime. It is **opt-in, per-edge** acceleration, not an automatic property of "using Isaac ROS"; each NITROS type maps **1:1** to a standard ROS message.
**Zero-copy** requires **same process AND successful negotiation**. At a **non-NITROS** boundary it converts to the 1:1 standard message; across a **separate-process** NITROS boundary it uses standard ROS2 inter-process transport (serialize + GPU→CPU staging) — *not* a mere copy. Exception: `isaac_ros_nitros_bridge` gives zero-copy GPU transfer **across** processes (e.g. Isaac Sim ↔ Isaac ROS).
**Detect:** Does the architecture assume zero-copy / GPU-resident data across a separate-process or non-NITROS edge (without the bridge), or where negotiation isn't guaranteed?
*Source:* Isaac ROS NITROS concept (REP-2007 / REP-2009). *Confidence: High.*

## 2. GEM vs NITROS
**Heuristic:** A **GEM** is a **GPU-accelerated ROS2 package** (the accelerated functional unit); **NITROS** is the **zero-copy transport between** NITROS-enabled nodes. A GEM's internal compute (CUDA/TensorRT) is accelerated **independently** of NITROS — *"most"* GEMs are NITROS-enabled, not all, and GPU acceleration is **not** "realized through NITROS."
**Detect:** Does the text equate "GEM" with "NITROS node", or claim a GEM's acceleration comes from NITROS transport?
*Source:* Isaac ROS docs (GEMs vs NITROS taxonomy). *Confidence: High.*

## 3. nvblox: plan against the ESDF, not the TSDF
**Heuristic:** nvblox keeps separate aligned voxel layers. The **ESDF** (full, non-truncated distance field, used for collision/planning) is computed **from the TSDF** (truncated — valid only in a small band near surfaces). The ESDF is a **lagging downstream product**: recompute it **after** TSDF integration; it may update slower than sensor rate. You **cannot** collision-query the TSDF at distance. Feed depth **+ accurate camera pose every cycle**; obstacle freeing is **not** instant (direct re-observation, or occupancy decay toward 0.5 out of view).
**Detect:** Does the design feed the planner the TSDF, assume the distance field is valid far from surfaces, or assume instant obstacle deletion?
*Source:* nvblox technical details; cuRobo 2D-nvblox demo. *Confidence: High.*

## 4. REP-103 frame & unit conventions (the `_optical` trap)
**Heuristic:** All frames **right-handed**. **Body** frames: **x-forward, y-left, z-up**. **Camera `_optical`** frames use a **different** convention: **z-forward, x-right, y-down**. Treating an optical frame as a body frame (or vice-versa) without the `_optical` transform injects a ~90° rotation. Units are SI; **angles in radians**.
**Detect:** Does code use raw camera/optical-frame axes as if x-forward (no `_optical` transform), or use degrees / non-SI units?
*Source:* REP-103. *Confidence: High.*

## 5. REP-105 TF tree: localization publishes map→odom
**Heuristic:** Every frame has **exactly one parent** (`earth→map→odom→base_link`). Localization must **not** broadcast `map→base_link` directly (that gives `base_link` two parents) — it publishes **`map→odom`** while odometry publishes `odom→base_link`. `odom` is **continuous but drifts unbounded**; `map` is **drift-free but jumps** discretely.
**Detect:** Does the TF setup publish `map→base_link` directly, or assume `map` is jump-free / `odom` is drift-free?
*Source:* REP-105. *Confidence: High.*

---
**Live API → context7.** Package/topic/node names evolve; resolve the current ones via `context7`/docs. See `contested.md` for the nvblox dynamic-clearing nuance.
