# Contested / nuance notes

Survived research but **not baked principles** — terminology clashes, idealizations, or tool simplifications. Consult before treating a borderline point as settled.

## "Cycle time" has two incompatible meanings
- **Groover / lean:** the per-unit **station** interval (`Tc = Ts + Tr`, max station service + repositioning) — the quantity compared against **takt** in line balancing.
- **Hopp & Spearman (Factory Physics):** total **flow time** (release→completion, **queue-inclusive**) — the variable in Little's law (`CT = WIP/TH`); their **rate** concept is **throughput**, and **lead time** is a *separate* quoted/promised duration (service level = P(flow time ≤ lead time)).
Name the variable explicitly ("station cycle time" vs "flow time"); **don't attribute the station-interval definition to Hopp & Spearman**, and don't say "flow time ≫ sum of station cycle times" (it's ≫ sum of station *process* times, due to queueing).
*Status: contested — durable terminology clash, not a single fact.*

## Throughput = r_b is an idealization
TH ≤ r_b is the durable bound. **TH = r_b only in the zero-variability Best Case with WIP ≥ critical WIP `W0`.** Under real variability throughput **approaches but never reaches** r_b, and added WIP only inflates flow time (Factory Physics Capacity Law / Practical Worst Case). Treat r_b as a ceiling, not the operating point.
*Status: contested — equality is an idealization.*

## Boothroyd DFA specifics (handling/insertion tables)
The design-efficiency index uses an **ideal per-part time of ~3 s** — a rounded **convention** (Boothroyd's value ≈ 2.93 s), not a law. The **α/β handling tables yield MANUAL handling/insertion seconds and a difficulty ranking**, not robot cell-cost or cycle time directly — so applying them to a **robotic** cell is a sound *adaptation*: use the orientation/insertion **difficulty ranking** to drive cell-design choices (feeder type, vision yes/no, gripper/compliance, re-grip count), then map difficulty to robot cost/cycle. (α is conventionally a constrained value, e.g. 180°/360°, not raw continuous symmetry.)
*Status: contested — convention-fragile constant + manual→robot adaptation.*

## `line_calc` tool simplifications (honest defaults)
- **`line_balance.balance_delay`** is computed against **takt** (not Groover's `Tc = max station time`). When the line is loaded to the bottleneck they agree; if `takt > max station time`, the figure folds deliberate **capacity slack** into "imbalance."
- **`tolerance_stack`** assumes **unit sensitivity** and treats each input as the contributor's tolerance (for RSS, a 3σ-equivalent). For lever/angular-amplified dimensions, **pre-multiply each input by its sensitivity coefficient**.
*Status: documented tool conventions — correct within their stated assumptions.*
