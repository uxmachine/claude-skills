# OpenUSD / Isaac Sim assets — durable conventions & traps

USD asset authoring for Isaac Sim / PhysX. Concepts are durable. **Exact UI flags / API tokens churn — fetch from `context7` (resolve `OpenUSD` / `Isaac Sim`) or the docs.**

## 1. Composition strength: LIVRPS (modern: LIVERPS)
**Heuristic:** Strength order, strongest → weakest: **Local > Inherits > VariantSets > (rElocates) > References > Payloads > Specializes.** A local/sublayer opinion always beats a referenced/variant/payload opinion. **Specializes is the WEAKEST arc** (deliberately — so base opinions stay overridable), not a strong override.
**Detect:** Does the code assume a reference overrides a local sublayer edit, or treat `specializes` as a strong override? Is the L-I-V-R-P-S order right?
*Source:* OpenUSD Glossary "LIVRPS Strength Ordering". *Confidence: High.*

## 2. Units & up-axis do NOT auto-convert across a reference
**Heuristic:** `metersPerUnit` unauthored fallback = **0.01 (cm)**; `upAxis` fallback = **Y**. Referencing a meters/Z-up asset into a cm/Y-up stage silently **mis-scales/mis-orients** it — USD takes raw coordinate values as-is. Setting `metersPerUnit` alone does **not** rescale geometry; the assembler must apply `xformOp` scale/rotate correctives.
**Detect:** Does it assume USD rescales/reorients on a unit/axis mismatch, or assume the default is meters/Z when it's actually cm/Y? (See `scripts/asset_lint.py` USD check.)
*Source:* OpenUSD "Encoding Stage Linear Units" / "Encoding Stage UpAxis". *Confidence: High.*

## 3. Reference vs payload
**Heuristic:** A **payload** is (a) **load-elidable** (deferrable/unloadable via Load/Unload, `LoadNone`) and (b) **weaker than a reference** in LIVRPS. Use payloads for heavy/deferrable geometry; references for content that must always compose and/or win over payload-strength opinions. Both are list-editable; **sublayers are not**.
**Detect:** Is a reference emitted for heavy mesh assets that should be deferrable payloads? Is "reference vs payload" treated as identical except loading (it also differs in composition strength)?
*Source:* OpenUSD Glossary "Payload"/"References"/"List Editing". *Confidence: High.*

## 4. ArticulationRootAPI: exactly once, no nesting
**Heuristic:** Apply `PhysicsArticulationRootAPI` **exactly once** per articulation; roots **cannot nest**. **Fixed-base arm (bolted):** put it on the fixed joint to world (or an ancestor). **Floating-base:** put it on the root body/link. Misplacement often fails **silently** — a bolted arm gets mis-parsed as floating-base (no world fixed joint).
**Detect:** Is the root on the correct prim for the base type, applied once, with no nested roots?
*Source:* OpenUSD "Rigid Body Physics in USD Proposal" (ArticulationRootAPI placement). *Confidence: High.*

## 5. Mesh collider approximation: default 'none' breaks on dynamic bodies
**Heuristic:** `physics:approximation` default = **none** (raw triangle mesh), valid only on **static/kinematic** colliders. A **dynamic** rigid body cannot use a raw triangle mesh: it falls back to **convexHull** (with a logged warning — not silent), which **fills concavities** (a hollow fixture/pocket becomes solid). For a concave dynamic part use **convexDecomposition** or an **SDF collider** (the one way to run a full concave triangle mesh on a dynamic body — GPU collision pipeline only). `sdf` is an Omniverse extension, not a core USD token.
**Detect:** Is a dynamic concave part (fixture, tray, pocket) left at `none` or `convexHull`, silently losing its cavities?
*Source:* OpenUSD UsdPhysics MeshCollisionAPI; Omniverse Physics "Colliders". *Confidence: High.*

## 6. No MassAPI ≠ weightless or 1 kg
**Heuristic:** A rigid body with **no** `MassAPI` is **not** weightless and **not** default-1 kg. If colliders exist, mass + inertia are **auto-computed from collider geometry** at an inferred density of **1000 kg/m³ (water)** when none is authored. Only with **no** collider volumes does mass fall back to 1.0.
**Detect:** Does the code assume an un-massed part is 1 kg or weightless? (The `physics:density` *attribute* default is 0.0 = "fall back to inferred", not literally 1000.)
*Source:* OpenUSD "Rigid Body Physics in USD Proposal"; Omniverse Physics. *Confidence: High.*

## 7. URDF→USD import (Isaac Sim) needs explicit, non-default choices
**Heuristic:** The importer does **not** infer these from the URDF — set them: **(1)** base **Fixed** for a bolted arm vs **Mobile** for a wheeled robot; **(2)** **Merge Fixed Joints** so the articulation spans only moving joints (note: Isaac Sim 5.1+ won't merge fixed links that carry their own mass/inertia); **(3)** **Self-Collision = false** unless certain links don't intersect at joints (intersecting meshes at a joint → instability); **(4)** **stage-units / scale** — Kit's default length unit is **centimeters**, URDF is **meters** → 100× mismatch if ignored (uniform global scaling only).
**Detect:** Was the URDF imported on defaults, assuming they encode bolted-arm-vs-wheeled intent or meter units?
*Source:* Isaac Sim "URDF Importer Extension" docs (4.5–6.0). *Confidence: High.*

> **Aside (corrected).** A path-less reference/payload resolves to the target layer's `defaultPrim`. A **missing** `defaultPrim` is a **loud** composition error (`PcpErrorUnresolvedPrimPath` + warning), **not** a silent empty — set `defaultPrim` on any referenceable asset layer.

---
**Live API → context7.** Importer UI/flags and Omniverse physics tokens change across Isaac Sim versions; resolve the current names via `context7`/docs. See `contested.md` for the RigidBody-nesting nuance.
