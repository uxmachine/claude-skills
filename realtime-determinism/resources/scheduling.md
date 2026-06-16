# Real-time scheduling — durable

What `scripts/rt_budget.py` reasons about, plus the judgment. **Exact `SCHED_*` / `sched_setattr` API via `context7` (resolve `Linux sched`) or the man pages.**

## 1. "Real-time" = bounded worst case, not "fast"
**Heuristic:** Real-time means meeting a **deadline with a predictable, bounded worst case** — correctness depends on *when* the result is produced. A system averaging 1 ms but spiking to 50 ms is **not** real-time for a 10 ms deadline; one that provably hits 10 ms every time is. The goal is **determinism**, which frequently **trades off against average throughput** (PREEMPT_RT, disabling power-management/turbo/SMT lower the worst case while reducing peak throughput).
**Detect:** Does the answer equate real-time with "fast"/"low-latency", or treat improving the *average* as making something real-time?
*Source:* Buttazzo, *Hard Real-Time Computing Systems*, Ch.1; Liu & Layland (1973). *Confidence: High.*

## 2. Schedulability is governed by WCET, not the average
**Heuristic:** A task set can pass an **average**-utilization check and still miss deadlines because one job hit its **worst case at the critical instant**. All classical analysis is parameterized on **WCET** (`C_i`). On `SCHED_DEADLINE`, the CBS **throttles** a task that overruns its Runtime — it's not merely late.
**Detect:** Is the analysis using average/measured-typical time (or just "it's fast under normal load") instead of explicit worst-case reasoning?
*Source:* Buttazzo; Liu & Layland; Linux `sched(7)` `SCHED_DEADLINE`. *Confidence: High.*

## 3. RMS by period; the 0.693 bound is sufficient, not necessary; EDF is U≤1
**Heuristic:** **Rate-monotonic** assigns fixed priority by **period** (shorter period → higher priority), optimal among fixed-priority for deadline=period on a uniprocessor. Bound `U ≤ n(2^(1/n)−1) → 0.693`, but it's **sufficient, not necessary** — harmonic sets are schedulable up to `U=1`; above the bound use **response-time analysis**, don't declare "unschedulable." **EDF** (dynamic priority) is **uniprocessor-optimal** with the exact test **`U ≤ 1`**. Under overload, EDF can cascade while RM **isolates the highest-priority** tasks (not "misses in clean priority order" — that's a myth). EDF's `U ≤ 1` is **uniprocessor** (Dhall effect breaks it on multiprocessors).
**Detect:** Are RMS priorities set by "importance" instead of period? Is 0.693 treated as a hard ceiling, or the bound treated as necessary?
*Source:* Liu & Layland (1973); Buttazzo (RTA; "RM vs EDF: Judgment Day"). *Confidence: High.* (Tool: `rt_budget.rm_schedulable` encodes the LL bound + `U≤1`.)

## 4. A normal Linux thread is NOT real-time
**Heuristic:** `SCHED_OTHER` (CFS, the default) is **not** real-time — static priority 0, optimizes fairness, always preempted by any RT thread. RT = `SCHED_FIFO`/`SCHED_RR` (fixed priority 1–99) and `SCHED_DEADLINE` (EDF+CBS). **Spawning a thread, a high `nice`, busy-spinning, or "making the loop faster" gives no RT guarantee** — set an explicit RT policy, `mlockall` to avoid page-fault jitter, and use a PREEMPT_RT/low-latency kernel for tight bounds. `nice` only biases CFS — it is **not** RT priority. PREEMPT_RT lowers worst-case latency but **mainline Linux is not a hard RTOS** (and RT throttling reserves ~5 % for non-RT by default).
**Detect:** Is a default/CFS/high-nice/busy-loop thread assumed real-time, or `nice` conflated with RT priority?
*Source:* Linux `sched(7)`, `sched_setscheduler(2)`, `sched_setattr(2)`. *Confidence: High.*

---
**Live API → context7.** Kernel knobs/defaults change; resolve via `context7`/man pages. **Related:** `priority-inversion.md` (shared resources), `hotpath.md` (what runs in the period). See `contested.md` for PREEMPT_RT specifics and the RM-vs-EDF overload nuance.
