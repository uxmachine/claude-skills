# Contested / version-fragile notes

Survived research but **not baked principles** — version-specific or true-only-with-a-caveat.

## PREEMPT_RT / Linux RT knobs are version-specific
The durable part: **mainline Linux is not a hard RTOS**; PREEMPT_RT bounds **soft/firm** latency (typically µs-scale), not a mathematically proven hard bound for arbitrary code, and you still need `mlockall`. The **version-specific knobs** (don't bake the numbers): RT throttling reserves CPU for non-RT (`sched_rt_runtime_us`/`sched_rt_period_us` default 950000/1000000 → RT throttled to 95 %); `SCHED_DEADLINE` runs an admission test (`sched_setattr` returns `EBUSY` if infeasible; total `U ≤ #CPUs` is necessary, not sufficient) and the CBS **throttles** a task overrunning its Runtime.
*Source:* Linux `sched(7)`, `sched-rt-group.rst`, `sched_setattr(2)`. *Status: contested — durable "not a hard RTOS" + version-pinned knobs.*

## RM-vs-EDF under overload — "clean priority order" is a myth
"Rate-monotonic degrades predictably, the lowest-priority tasks miss first in order" is a **misconception** (Buttazzo, "Rate Monotonic vs. EDF: Judgment Day"): a single overrun can disturb **any or all** lower-priority tasks in **no particular order**. The defensible statement: under **permanent overload** RM provides **isolation** — the highest-priority / shortest-period tasks keep meeting deadlines while some lower set is starved; EDF can exhibit a domino/cascade but is **often comparable or better**. EDF's `U ≤ 1` optimality is **uniprocessor only** (Dhall effect on multiprocessors).
*Source:* Buttazzo, "Judgment Day"; Dhall & Liu (1978). *Status: contested — common framing is inverted.*

## "All allocation / GC is non-deterministic" is over-broad
Bounded-WCET allocators exist (**TLSF**, O(1) worst case) and **hard-real-time GCs** deliver bounded pauses (IBM Metronome ~6 ms, JamaicaVM). The hot-path no-allocation rule holds because it targets **commodity** runtimes — CPython refcount/arena churn, default JVM/Go GC — where pauses are effectively unbounded and the glibc heap isn't RT-safe. State the rule as practical, not universal.
*Source:* Masmano et al. (TLSF, ECRTS 2004); IBM Metronome. *Status: contested — over-broad mechanism, correct conclusion for commodity runtimes.*

## Mutex protocol defaults vary by platform
POSIX `pthread` mutexes default to `PTHREAD_PRIO_NONE` (no protocol) — but **FreeRTOS mutexes default priority-inheritance ON** (its semaphores do not). Don't assume a protocol is (or isn't) active; **check and set it explicitly** per platform.
*Source:* POSIX `pthread_mutexattr_getprotocol`; FreeRTOS mutex docs. *Status: contested — platform-dependent default.*
