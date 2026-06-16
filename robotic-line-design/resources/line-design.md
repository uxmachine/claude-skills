# Robotic cell/line design & DFA — durable

Design judgment for a robotic assembly cell/line, before and around the math.

## 1. Design for single-direction, layered build-up
**Heuristic:** Build the product in **layers, each part inserted from one direction — ideally top-down (z-axis) onto a locating base part — and self-retaining** before the next part is added (no hold-down). Chamfers/tapers guide; use modular subassemblies; avoid repositioning the partial assembly. A true one-direction build isn't always possible, so the rule is **minimize the number of assembly directions (ideally one)** — it lets gravity help and suits SCARA/6-axis arms.
**Detect:** Does the design accept multi-direction insertion or a mid-line flip and "fix" it with reorientation/flip stations or a second arm — instead of pushing back on the **product geometry** first?
*Source:* Boothroyd, Dewhurst & Knight, *PDMA* (single-direction, base part, layered build-up). *Confidence: High.*

## 2. Run DFA part-count reduction BEFORE sizing the line
**Heuristic:** Apply Boothroyd's three minimum-part questions to every part — (1) does it **move** relative to parts already assembled? (2) must it be a **different material** for fundamental reasons? (3) must it be **separate** to allow assembly/service? "No" to all three → candidate to **eliminate or combine**. Sizing stations/feeders/cycle-time around the **as-given BOM** is the classic trap (you provision robots and feeders for fasteners/brackets that snap-fits would remove). Consolidation is **bounded** (process capability, tooling amortization, service/separability) — validate at **product-level** cost, not part-level.
**Detect:** Does the model allocate a station/feeder per BOM line, instead of first challenging the part count?
*Source:* Boothroyd, Dewhurst & Knight, *PDMA* (minimum-part criteria); dfma.com. *Confidence: High.*

## 3. Reach means the DEXTEROUS workspace, not the envelope
**Heuristic:** A task is feasible only if the arm has a **collision-free, singularity-free pose achieving the required ORIENTATION** there — a reachable XYZ is necessary, not sufficient (near a singularity the Jacobian is ill-conditioned and orientation/velocity control degrades). **Effective payload = tool + gripper + grasped part**, checked against the **payload-moment** (mass + CoG offset + inertia) at the **actual working reach** (rated capacity falls with extension/eccentricity). Prefer **deterministic fixturing** (3-2-1 locating, all 6 DOF) so the line runs open-loop; reach for **vision** when part variety/mix/changeover economics beat dedicated tooling — not as a default substitute for a fixture.
**Detect:** Is point-in-envelope treated as feasible (ignoring orientation, singularities, payload-at-reach), and a camera bolted on to recover a pose a fixture would establish for free?
*Source:* Groover (work envelope, payload); Boothroyd (part presentation & fixturing). *Confidence: High.*

## 4. Size buffers deliberately — every buffer unit is WIP
**Heuristic:** Buffers/WIP **decouple variability** (a zero-buffer serial line behaves as one machine — any breakdown halts everything), but **every buffer unit is WIP and adds lead time** (Little's law) with **diminishing returns**. Size each buffer to the **measured variability/reliability of its adjacent stations** (Hopp & Spearman's Variability Buffering Law) — not by reflex "conveyor between everything" or "zero buffers, it's lean." Under real variability, **protective capacity / buffers at non-bottlenecks do raise throughput**, and a deliberately **unbalanced** line (bowl phenomenon) can beat a perfectly balanced one.
**Detect:** Are inter-station buffers dropped entirely or sized as large "safety" buffers, with no reasoning about the WIP/lead-time cost?
*Source:* Hopp & Spearman (Little's law, critical WIP, buffering); Groover (starving/blocking). *Confidence: High.*

## 5. ISA-95 is a naming scheme — defer the integration architecture
**Heuristic:** Use the **ISA-95 / IEC 62264 equipment hierarchy** — *Enterprise > Site > Area > Work Center > Work Unit* (discrete: **Production Line / Work Cell**) — purely as the **naming/addressing scheme** for *which physical element a line metric refers to*. It is **not** a metric definition or a cell-design method: **ISA-95 does not define OEE/takt or mandate aggregation levels** (OEE = Nakajima, takt = lean, standardized KPIs = ISO 22400). (Equipment Module / Control Module are **ISA-88** terms *below* Work Unit — don't equate them.) **Boundary:** the MES/integration stack — functional **Levels 0-4, B2MML, ERP↔MES** — belongs to **`system-architecture-design`**, not here.
**Detect:** Does the model start designing the MES / Levels-0-4 / B2MML stack when the task is physical cell/line design, or treat ISA-95 as the authority for where metrics attach?
*Source:* ANSI/ISA-95.00.01 (IEC 62264-1) equipment hierarchy; ISO 22400 (KPIs). *Confidence: High.*

---
**Related:** the math → `takt-balance.md`, `oee-throughput.md`, `tolerance-capability.md`; integration architecture → `system-architecture-design`. DFA difficulty-coding nuance → `contested.md`.
