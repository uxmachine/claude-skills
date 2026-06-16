---
name: isaac-curobo
description: Use when planning robot motion with cuRobo, authoring or importing robot/scene assets for Isaac Sim or OpenUSD, or wiring Isaac ROS / nvblox perception — covers the durable concepts, collision & sim semantics, and traps the model gets wrong, and fetches exact current API via context7. Defers to system-architecture-design for system structure.
---

# Isaac / cuRobo — durable concepts, traps, and checks

GPU motion planning (cuRobo), OpenUSD / Isaac Sim assets, and Isaac ROS / nvblox perception change APIs fast. This skill holds only the **durable** layer — what a GPU planner guarantees vs penalizes, collision & sim semantics, the recurring unit and frame traps — and **delegates exact current API to `context7` / official docs.** Read only the resource whose step is live (progressive disclosure).

## Procedure (route, don't dump)

1. **Motion planning / collision?** → open `resources/curobo.md`. Then run `scripts/collision_config_check.py <config.json>` to confirm the config *guarantees* clearance rather than only *penalizing* penetration, and to catch the mesh-SDF "poison" radius and uncovered links.
2. **Authoring / importing a robot or scene asset (URDF / USD)?** → open `resources/usd-assets.md`. Then run `scripts/asset_lint.py <file.urdf|.usd>` for inertia / mass / tree / mimic (URDF) and up-axis / metersPerUnit (USD) traps.
3. **Isaac ROS / nvblox perception?** → open `resources/isaac-ros.md` (NITROS per-edge negotiation, GEM vs NITROS, the ESDF-not-TSDF planning world, REP-103/105 frames).
4. **Need an exact API signature / current field name?** → do NOT trust this skill's wording; fetch it from `context7` (resolve `cuRobo` / `Isaac Sim` / `Isaac ROS`) or the official docs. The skill names the *concept*; context7 has the *current API*.
5. Disagreements / version-fragile claims live in `resources/contested.md` — consult before treating a borderline point as settled.

## Tools

- `scripts/collision_config_check.py <config.json>` — does a (normalized) cuRobo collision config **guarantee** clearance, or only **penalize** penetration? Also flags the mesh-SDF query-radius "poison" and links with no collision spheres. (`tests/test_collision_config_check.py`.)
- `scripts/asset_lint.py <file.urdf|.usd>` — URDF inertia-not-PD / non-positive mass / duplicate names / dangling mimic / broken tree, plus USD up-axis & metersPerUnit traps. Full USD parsing (needs `pxr`) is deferred — grow per Rule 4. (`tests/test_asset_lint.py`.)

## Scope guards

- System structure / coupling / boundaries → `system-architecture-design`.
- A specific runtime failure → `superpowers:systematic-debugging`.
- New feature design → `superpowers:brainstorming`.

---

### Improving this skill (every session you use it)

After using this skill, ask: **one-time fix, or forever?** If a correction / example / edge-case should apply every future time, add it to the right `resources/` file now. If you found yourself re-deriving an analysis by hand, add it to a tool.

**Related:** `system-architecture-design` · `ros2-system-design` · `realtime-determinism` · `superpowers:systematic-debugging`.
