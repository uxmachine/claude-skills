# Tolerance stack-up & process capability — durable

What `scripts/line_calc.py` `tolerance_stack` / `process_capability` compute, and the judgment the model skips.

## 1. Worst-case = arithmetic sum; the safe default when data is absent
**Heuristic:** **WC stack = Σ |sensitivity · tolerance|** — the bound when every contributor is at its worst extreme simultaneously. It **guarantees 100 % interchangeability** (no out-of-spec assembly) but is conservative and drives tight, costly part tolerances. It is **required for safety-critical interfaces** and is the **only defensible method when RSS's assumptions can't be verified** (no SPC, no Cpk data). **Default to WC when data is absent.**
**Detect:** Does the model jump to RSS without first asking whether WC is required (safety-critical, few parts, no SPC)? Is WC computed as an arithmetic (absolute) sum, not an average or root-sum?
*Source:* Drake, *Dimensioning & Tolerancing Handbook*; Fischer, *Mechanical Tolerance Stackup*. *Confidence: High.*

## 2. RSS is a probability, not a guarantee — and only under its assumptions
**Heuristic:** **RSS = √(Σ sensitivity²·σ²)**, valid **only** when contributors are **independent, ~normal, centered, and in statistical control**. It predicts a *probability* (a 3σ RSS limit still lets ~0.27 % exceed), **not** a guarantee. When assumptions fail (mean shift, drift, correlation, skew, mixed lots) raw RSS **under-predicts** real spread — apply an inflation factor (Bender ~1.5×) or a mean-shift model.
**Detect:** Are the independence/normality/centering preconditions stated, the residual defect fraction acknowledged, and inflation flagged when assumptions are weak?
*Source:* Bender (SAE); Creveling, *Tolerance Design*; Drake handbook. *Confidence: High.*

## 3. WC vs RSS is a risk/cost tradeoff
**Heuristic:** For *n* equal contributors **WC/RSS = √n** (4 → RSS is half WC; 16 → a quarter), so longer chains give bigger RSS savings — but RSS's real failure is **off-center/mean-shift and correlation**, not chain length (more independent contributors actually strengthen the normality premise via CLT). Ask **which guarantee the application needs** — bounded 100 % interchangeability vs statistical yield on a known, centered, capable process — not which formula is "more advanced."
**Detect:** Is the choice framed as a risk/cost tradeoff tied to criticality and process control, or is one method treated as universally correct?
*Source:* Drake; Fischer. *Confidence: High.*

## 4. Tolerances ADD (weighted by sensitivity), they don't average
**Heuristic:** Contributor tolerances **accumulate** (arithmetically for WC, in quadrature for RSS) — many "loose" tolerances on a long chain can exceed the assembly requirement. You **cannot** divide an assembly tolerance equally among parts: weight each by its **sensitivity coefficient** `a_i` in `gap = Σ a_i·x_i` (an angular/lever-amplified dimension with `a_i > 1` contributes *more* than its nominal tolerance). *(`line_calc.tolerance_stack` assumes unit sensitivity — pre-multiply each input by its sensitivity for amplified dimensions.)*
**Detect:** Are tolerances averaged, or sensitivity coefficients / directional signs ignored?
*Source:* Drake (loop/sensitivity); Fischer. *Confidence: High.*

## 5. Cp vs Cpk — spread vs centering, and the one-sided exception
**Heuristic:** **Cp = (USL−LSL)/(6σ)** measures spread only; **Cpk = min(USL−mean, mean−LSL)/(3σ)** adds centering. **Cpk ≤ Cp only for two-sided (bilateral) specs** (equal only when centered) — for a **one-sided spec, Cp is undefined** and Cpk reduces to the single Cpu/Cpl. Both are meaningful **only for a process in statistical control**, adequately sampled, ~normal (skew → percentile/transform methods). Separate **short-term** within-subgroup σ (Cp/Cpk) from **long-term** overall σ (Pp/Ppk).
**Detect:** Is capability declared from Cp alone, "Cpk ≤ Cp" asserted for a one-sided spec, or short-term confused with long-term?
*Source:* AIAG SPC manual; Montgomery, *Introduction to SQC*. *Confidence: High.*

---
**Related:** the WC-vs-RSS hybrid/inflation refinements → `contested.md`.
