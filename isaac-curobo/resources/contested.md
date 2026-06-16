# Contested / version-fragile notes

These survived research but are **not baked principles** — they are oversimplified, version-specific, or a wrong framing of a real fact. Consult before treating a borderline point as settled.

## cuRobo mesh-SDF query radius "poison" — auto-guarded in current cuRobo
**Generic truth (durable):** any closest-point / mesh-SDF query with a search distance **smaller than the queried collision-sphere radius** can truncate a penetrating sphere to "no hit" and under-report collision. So a sound *generic* mesh-SDF check needs search distance ≥ sphere radius + margin.
**cuRobo-specific (do NOT treat as a user invariant):** current cuRobo (post-v0.7 `_src` layout) **auto-sizes** the per-query mesh distance to the obstacle's bbox half-diagonal and **floors it by the sphere's `radius_adjusted`** (`wp.max(bbox_half_diag, query_distance)`), so the per-query search distance is **always ≥ sphere radius + activation distance by construction**. The user-facing `max_distance` is not a cap that can truncate below the sphere radius.
**Implication for our tooling:** `scripts/collision_config_check.py`'s `mesh_sdf_poison` check is a **generic defensive guard** (valid for custom/older/non-cuRobo SDF worlds); on current cuRobo it is conservative — the engine already guarantees the floor.
*Source:* NVIDIA Warp `wp.mesh_query_point` `max_dist` semantics; cuRobo `_src/geom/data/data_mesh.py`. *Status: contested — generic concept kept, cuRobo footgun refuted.*

## nvblox dynamic clearing — "not detected as dynamic" ≠ "never cleared"
A slow-moving object that Dynablox can't flag (slower than odometry drift) is **still cleared** once its vacated space is **re-observed**; the regular TSDF/occupancy integration handles it. A true persistent **phantom** only occurs while the freed region stays **occluded / out of FOV**, or when **pose/odometry drift** corrupts integration. Don't overstate the Dynablox limitation as a permanent obstacle.
*Source:* nvblox technical details. *Status: contested — caution, not a hard rule.*

## USD RigidBodyAPI nesting — the whitepaper is stale
The **old** "Rigid Body Physics in USD Proposal" says nested bodies are ignored. The **shipping** `usdPhysics` schema supersedes that: a descendant prim with its **own** `RigidBodyAPI` marks a **separate sub-body** that moves independently of the parent (and `resetXformStack` also decouples a subtree). Don't rely on the "nested = ignored" wording when reasoning about composed assets.
*Source:* PixarAnimationStudios/OpenUSD `usdPhysics/schema.usda`; Omniverse Physics. *Status: contested — proposal doc contradicts shipping schema.*
