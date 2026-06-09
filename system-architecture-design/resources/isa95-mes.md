# ISA-95 / MES — manufacturing systems

Decision-oriented, not exhaustive. Pull this when the system spans equipment → cell/line runtime → MES/ERP, or anyone says "what layer is this?"

## The level model (ISA-95 / IEC 62264)

| Level | Concern | Timescale |
|---|---|---|
| **L0** | Physical process — sense & actuate | ms |
| **L1** | Sensing & manipulation control (the device-control loop) | ms |
| **L2** | Supervisory control — monitor & control a cell/line; execute pre-baked work | sub-second → seconds |
| **L3** | **MES / MOM** — work-order dispatch, detailed scheduling, production tracking, performance analysis | minutes → shift |
| **L4** | Business / ERP — planning, logistics | days → months |

Plus the equipment/role hierarchy: **Enterprise → Site → Area → Line / Work-Cell → Unit / Machine.**

## Getting the layer label right (a common, expensive error)

A repo's **claimed** level must match its **actual responsibility**. The frequent category error: calling a **design-time / offline tool a "L3 / MES."** An offline CAD→line *compiler* (consumes a process plan, plans trajectories, emits deployment bundles "hours/days before the run") is **not** an MES — it does no runtime work-order dispatch, scheduling, or production tracking. It sits *above* L3 as an engineering/authoring tool and feeds artifacts *down* to the L2 runtime.

**Detect:** grep the repo for `work_order | dispatch | schedul | production tracking | oee | throughput`. If those responsibilities are absent, it is not an MES, whatever the label says. (Beware naming collisions — `L3` as a *step label* in a plan file is not ISA-95 L3.)

**Why it matters:** mislabeling invites runtime concerns to creep into a design-time tool (e.g. live-execution code landing in a bake tool), and lets an org believe it has an MES when the L3 slot is actually empty. Name the gap explicitly; scope any real MES functions as a **separate service that consumes the compiler's bundles**, not a retrofit into the SDK.

A clean generic map for a CAD-to-line robotics stack:
- **L0–L1** — device-control leaf skills (sense/actuate + the contact loop). *Owns only its zone; no scheduling.*
- **L2** — cell/line runtime: orchestrates and executes **pre-baked** work; no planning/IK/collision on the path.
- **above L3** — offline compiler: planning/IK/collision/sim at compile time, emits versioned bundles.
- **L3 (MES)** — a separate service (often a future build): consumes bundles, dispatches work orders, tracks production.

## ISA-95 in an Industry-4.0 world — it organizes integrations, not a monolith

The modern role of ISA-95 has shifted from *blueprint for a bespoke monolithic MES* toward *the topic structure for event-driven integration* linking equipment → MES → ERP → data lakes. **(Source: HighByte/HiveMQ — vendor-originated; treat "new-age MES" as consensus-in-formation, not settled standard.)**

- **Unified Namespace (UNS):** a single, structured, event-driven source of truth. Map the equipment hierarchy onto the topic tree: `Enterprise/Site/Area/Line/Cell/Machine/...`. Transport is typically **MQTT + Sparkplug B**.
- The mapping is a **recommended, adaptable pattern — not a rigid 1:1**; levels can be flattened or merged.
- The critique that "the automation pyramid blocks digital transformation" targets the **vertical communication pyramid**, *not* the equipment/role **naming hierarchy** — even the strongest critics recommend ISA-95 Part 2 / RAMI 4.0 to structure the UNS.
- **Skepticism to keep (`contested.md`):** a UNS can become a glorified data lake if it is dumped into without modeling; model the namespace, don't just pipe everything.

## The integration default: publish, don't couple

A lower layer (L0–L2 runtime) should integrate **up** by **publishing into an ISA-95-keyed UNS** (events on `.../Cell/<id>/...`) rather than coupling directly to a specific MES implementation. This is DORA loose coupling (`principles.md` §3) applied across the L2↔L3 boundary, and the rmw/`ros2_control` driver-seam pattern (a stable published interface as the abstraction) applied to manufacturing.

> **Confidence:** the publish-don't-couple recommendation is an **inference** synthesizing ISA-95/UNS sources with DORA — present it as a strong default, not a proven fact. Whether the published boundary is *available* depends on whether an MES/UNS exists to publish to; if not, the org is also building L3 and should design that boundary deliberately.
