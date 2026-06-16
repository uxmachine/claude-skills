# OEE, Little's law & utilization — durable

The metrics `scripts/line_calc.py` computes, and where the model gets them wrong.

## 1. OEE = A × P × Q (multiply, never add)
**Heuristic:** **OEE = Availability × Performance × Quality**, three ratios in [0, 1] that **multiply** — so three "respectable" 90 % factors give **72.9 %**, and OEE can never exceed its smallest factor. A = Run/Planned; P = (Ideal Cycle × Total Count)/Run; Q = Good/Total. Collapsed: OEE = (Good × Ideal Cycle)/Planned. "World-class 85 %" is the *product* 90 %×95 %×99 %, not an average.
**Detect:** Are the three averaged/added, or is an OEE reported above its smallest factor?
*Source:* Nakajima, *Introduction to TPM*; Vorne/OEE.com. *Confidence: High.*

## 2. Any factor > 100 % is a measurement error
**Heuristic:** A factor **> 1 is a definition/measurement error to flag, not report** — almost always the **Ideal Cycle Time was set too slow** (line appears to beat its theoretical max). Fix the ideal time down (or fix an over-counted piece count). **Performance uses TOTAL count** (rejects included by design), so **rejects belong to Quality, not Performance**; a reject miscounted as good inflates *Quality* instead.
**Detect:** Is a Performance/OEE > 100 % accepted as "overperformance," or are rejects blamed for high Performance?
*Source:* OEE.com FAQ (Vorne); Nakajima. *Confidence: High.*

## 3. Six big losses → three factors (and the two everyone inverts)
**Heuristic:** breakdowns + setup/adjustments → **Availability**; idling/**minor stops** + reduced speed → **Performance**; defects/rework + **startup/yield** → **Quality**. The two most-inverted mappings: **minor stops are Performance** (not Availability) and **startup/yield is Quality** (not Performance). The Availability↔Performance boundary for short stops is a **configurable threshold (~2-5 min)** — the same stoppage can land in either, so it's a labeling convention. (Don't invoke "double-counting": `Total Count` cancels algebraically, so a slow-and-defective unit correctly appears in *both* P and Q — by design.)
**Detect:** Are minor stops put in Availability or startup losses in Performance? Is "double-counting" used to (wrongly) justify the formula?
*Source:* Nakajima, *Introduction to TPM*, Ch. 3. *Confidence: High.*

## 4. Little's law: WIP = throughput × flow time — mind the units
**Heuristic:** **WIP = throughput × flow time** (solve for any one). It's **distribution- and discipline-free** (any stable long-run system). The **dominant error is inconsistent time units** (throughput/hr with cycle time in minutes). It's a **long-run average, not instantaneous**, and fails for a runaway system (WIP → ∞). With scrap/rework, "throughput" is ambiguous (started vs yielded) — use the measure consistent with your WIP and flow-time definitions.
**Detect:** Are units reconciled before multiplying/dividing? Is it applied instant-by-instant or to a non-stationary system?
*Source:* Little (1961); Hopp & Spearman, *Factory Physics*. *Confidence: High.*

## 5. Utilization near 100 % + variability → non-linear blow-up
**Heuristic:** Pushing utilization `u` toward 1 with **any** variability makes cycle time and WIP **explode non-linearly** (Kingman/VUT: queue time ∝ `u/(1−u)`). The same +5 % utilization adds far more delay at 95 % than at 70 %, worse with high variability. **Don't load a non-bottleneck near 100 %** — high utilization buys throughput only by paying a steep WIP/lead-time penalty. Only zero-variability lets `u → 1` without queue growth.
**Detect:** Is high utilization treated as purely good, or delay assumed to grow linearly/bounded?
*Source:* Hopp & Spearman, *Factory Physics* (VUT); Kingman. *Confidence: High.*

---
**Related:** takt vs station cycle time and the bottleneck bound → `takt-balance.md`; buffer sizing → `line-design.md`.
