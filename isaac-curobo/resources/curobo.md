# cuRobo — durable motion-planning concepts & traps

GPU motion planning. These are concepts/semantics that survive version bumps. **Exact API field names change — fetch them from `context7` (resolve `cuRobo`) or curobo.org, never from this file.**

## 1. Feasibility is penetration-based; activation distance is a SOFT cost
**Heuristic:** Collision feasibility means *zero penetration*. `activation_distance` (and any collision-cost weight) is a soft penalty that is exactly **0 outside the band** and quadratic only inside it — it does **not** buy a clearance margin in the returned trajectory.
**Detect:** Is the code assuming `activation_distance` (or a collision weight) yields a guaranteed standoff, instead of a penalty that vanishes at the surface? For a real clearance guarantee you need an explicit hard margin — run `scripts/collision_config_check.py`.
*Source:* cuRobo report (arXiv:2310.17274) §3.3 Eq.10 (collision cost = 0 for d < −η). *Confidence: High.*

## 2. Gate on the success flag, not on pose cost
**Heuristic:** A trajectory is feasible only when **collision-free AND within joint limits AND within the configured position/orientation tolerance**. A low pose cost/error only *ranks seeds* — it is not a feasibility gate. `success = feasible ∧ converged`.
**Detect:** Does acceptance gate on a near-zero cost/pose-error instead of the explicit success flag? (The paper's 5 mm / 5 % are *evaluation* thresholds; the real gate is the configurable position/orientation tolerance.)
*Source:* cuRobo report §6 success criterion. *Confidence: High.*

## 3. Continuous (swept) collision checking is NOT everywhere
**Heuristic:** The swept/continuous collision cost that catches thin obstacles at coarse discretization runs **only in cuboid/mesh trajectory optimization**. It is **not** in the nvblox/ESDF kernel (waypoint-only) and **not** in IK or graph planning (discrete-time only).
**Detect:** Does the setup rely on an ESDF/voxel world or IK/graph checks to catch thin obstacles? Those can miss them — use cuboid/mesh trajopt, or widen the activation distance.
*Source:* cuRobo report §3.4 + App. E.3/E.5 ("did not implement the continuous algorithm for the nvblox kernel"; IK/graph "only check collisions at discrete times"). *Confidence: High.*

## 4. The robot body is ONLY spheres — unsphered links are invisible
**Heuristic:** cuRobo represents the robot's volume solely by per-link collision **spheres** (meshes/voxels are for the *world* and attached objects). A link not in `collision_link_names` / with no spheres contributes **nothing** to world- or self-collision — silently.
**Detect:** Did someone add an EE/flange/tool link and assume the planner "sees" its mesh? An unsphered link is never collision-checked. (See `collision_config_check.py` → `uncovered_link`.)
*Source:* cuRobo report §3.1 + Fig.3; cuRobo robot-config tutorial (links outside `collision_link_names` excluded). *Confidence: High.*

## 5. World representations are not interchangeable
**Heuristic:** cuboid/OBB = fastest (docs: ~4× faster than mesh) and exact for box obstacles → approximate to cuboids when shape allows. Mesh = NVIDIA Warp BVH, accurate for arbitrary shapes but **assumes watertight meshes** (non-watertight → wrong inside/outside). nvblox ESDF = camera-streamed depth worlds.
**Detect:** Is a mesh used where a cuboid would do (wasted compute), or a non-watertight mesh trusted for inside/outside? (Don't cite an unsourced "N× slower" range — docs state ~4× for cuboid only.)
*Source:* cuRobo report §3.5; cuRobo "Collision World Representation" docs. *Confidence: High.*

## 6. MotionGen ≠ IKSolver / TrajOptSolver
**Heuristic:** `MotionGen` is the full pipeline: collision-free IK for the goal → seed trajopt (interpolate start↔IK through a retract config) → **many parallel trajopt seeds** → final time-step optimization, with the **geometric/graph planner as a conditional fallback** (only after linear seeds fail). A single-seed `TrajOptSolver` or IK-only call is **not** equivalent to planning.
**Detect:** Is raw IK or a single trajopt seed being treated as a planned, collision-aware motion? Use the low-level solvers only when intentionally supplying your own seeds/costs.
*Source:* cuRobo report §2/Fig.2; NVlabs/curobo Discussion #227. *Confidence: High.*

## 7. Self-collision is a pruned sphere-pair set
**Heuristic:** Self-collision is checked only over a **precomputed set of sphere pairs** (consecutive / never-colliding links pruned — empirically ~50 % kept). Editing the sphere model or `self_collision_ignore` wrongly can **silently disable** real self-collision checks while plans still "succeed."
**Detect:** Were sphere/ignore edits made without re-checking that genuinely-colliding pairs are still in the set? cuRobo's default-pose sanity check won't catch other configurations.
*Source:* cuRobo report §3.2 Eq.9 (~50 % of pairs kept). *Confidence: High.*

---
**Live API → context7.** Field names (`activation_distance`, `MotionGenConfig`, `collision_link_names`, position/orientation tolerances) and defaults change by version. This file is the *concepts*; resolve the current API via `context7` or curobo.org. See `contested.md` for the mesh-SDF query-radius nuance.
