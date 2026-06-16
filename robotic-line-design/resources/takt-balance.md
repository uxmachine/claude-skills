# Takt, cycle time & line balancing — durable

The math `scripts/line_calc.py` automates, plus the judgment around it.

## 1. Takt is a demand rhythm — not cycle time, not throughput
**Heuristic:** **Takt = available production time per period / customer demand per period** (28 800 s ÷ 480 = 60 s/unit). It's what you *need*. The **station cycle time** is what the line *does*; **throughput** is the realized rate (set by the bottleneck). The line meets demand only if **every station's cycle time ≤ takt**.
**Beware two meanings of "cycle time":** Groover/lean = the per-unit **station** interval (the quantity compared to takt); Factory Physics = total **flow time** (queue-inclusive, the variable in Little's law) — their rate concept is *throughput*, not cycle time. Name the variable explicitly.
**Detect:** Is takt computed as available/demand, or wrongly equated with the longest station time / throughput?
*Source:* Groover (line balancing / takt); Lean Enterprise Institute. *Confidence: High.*

## 2. Theoretical-min stations is a LOWER BOUND, not the answer
**Heuristic:** `min stations = ceil(total work content / takt)` is a **lower bound**. The real count is usually higher: tasks are indivisible (bin-packing), precedence constrains assignment, and per-cycle repositioning eats available time. Never report a fraction ("5.42 stations"); apply the ceiling and treat it as a floor real balancing exceeds (measured by balance delay).
**Detect:** Is the result a non-integer, or is the lower bound assumed achievable without precedence/indivisibility?
*Source:* Groover (theoretical minimum workstations). *Confidence: High.*

## 3. A task longer than takt is infeasible under *serial* assignment
**Heuristic:** A station's time is floored by its **longest indivisible task** (`Tc ≥ max task`). If one task exceeds takt, **redistributing other tasks or adding more serial stations cannot fix it.** Valid remedies: (a) decompose the task if divisible, (b) **parallel/duplicate** stations for that operation (this *is* adding stations — in parallel, not series), (c) speed up the method, or (d) accept a longer takt (lower throughput).
**Detect:** Is "add stations / rebalance" offered for an over-takt task, instead of split/parallelize/speed-up/relax-takt?
*Source:* Groover (`Tc ≥ Max{Tek}`). *Confidence: High.*

## 4. Throughput is BOUNDED by the bottleneck — and the bottleneck is utilization, not raw time
**Heuristic:** Steady-state **throughput ≤ r_b**, the rate of the **highest-utilization** station (lowest *effective* capacity after availability/setup/yield) — **not necessarily the longest-process-time station** (parallel machines, yield, and product mix move it). Adding capacity off the bottleneck doesn't raise the ceiling — **but** de-starving/buffering the constraint *can* raise realized throughput, and the bottleneck can **shift** after improvement or with mix. Output approaches r_b but, under variability, never reaches it (TH = r_b only in the zero-variability ideal with WIP ≥ critical).
**Detect:** Is throughput computed from a sum/average of station times, or set equal to (not bounded by) the slowest station ignoring utilization/variability?
*Source:* Hopp & Spearman (bottleneck rate); Goldratt (TOC). *Confidence: High.*

## 5. Balance delay = idle fraction
**Heuristic:** `balance delay = (n·Tc − Σtask) / (n·Tc)`; efficiency = 1 − delay = `Σtask / (n·Tc)`. Strictly, **Tc is the bottleneck station time**, ≤ takt. `line_calc.line_balance` computes the delay against **takt** for convenience — when the line is loaded to the bottleneck (Tc = takt) they agree; if takt > max station time, the figure folds deliberate **capacity slack** into "imbalance," so read it accordingly.
**Detect:** Is balance delay computed without the `n·Tc` denominator, or is deliberate under-loading mistaken for imbalance?
*Source:* Groover (balance-delay / line-efficiency). *Confidence: High.*

---
**Related:** throughput/utilization queueing effects → `oee-throughput.md`; the "cycle time" terminology clash and the TH≤r_b idealization → `contested.md`.
