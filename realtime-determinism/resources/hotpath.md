# The real-time hot path — what's forbidden, and why

The control-loop body between two period boundaries. Run `scripts/hotpath_scan.py <file.py> [func]` to catch the obvious hazards (heuristic — a clean scan is *necessary*, not *sufficient*).

## 1. No blocking/I/O — and logging is the sneaky one
**Heuristic:** No file/disk, network/socket, or console I/O inline — and **critically no logging** (`print`, `logging.info`, `printf`, `RCLCPP_INFO`). Logging *looks* harmless but takes a lock (stdio `flockfile`), formats strings (often allocating), writes a fd that can block, buffers, and may page-fault — it's one of the most common LLM-introduced RT violations. RT-safe alternative isn't "never log": the hot path does a **bounded, non-allocating, lock-free enqueue** of raw data to a preallocated ring buffer, and a **separate lower-priority non-RT thread** formats and does the I/O.
**Detect:** Does the loop call any logging/print or do file/socket/console I/O inline, instead of handing data to a non-RT thread?
*Source:* ROS 2 Real-Time-Programming tutorial; PREEMPT_RT/rt.wiki guidance; glibc stdio-lock docs. *Confidence: High.*

## 2. No dynamic memory — and `mlockall` + pre-fault
**Heuristic:** **Zero** dynamic memory operations in the hot path: no `malloc`/`new`, no implicitly-allocating container growth (`vector` past capacity, `std::string`, dict/list growth), and in GC/managed languages nothing that allocates and can trigger a collector (Python object/refcount churn, `numpy` array creation, f-strings). The dominant non-determinism is the **first-touch page fault** (kernel allocates the physical page synchronously) + allocator lock contention. Mitigation: **(a)** pre-allocate/pre-size all buffers before the loop and reuse them (object pool/ring), **(b)** `mlockall(MCL_CURRENT|MCL_FUTURE)` at startup + **pre-fault** the heap (touch one byte per page) + `mallopt(M_TRIM_THRESHOLD,-1)`/`M_MMAP_MAX,0`; pre-fault the stack to a max depth as defense-in-depth. **cuRobo/Python in an inner contact loop is a red flag** — allocation belongs in the planner, not the contact loop.
**Detect:** Does the loop allocate / grow a container / create arrays, or is there no `mlockall` + pre-fault before the loop?
*Source:* ROS 2 realtime proposal; PREEMPT_RT memory-locking guidance; `mlockall(2)`. *Confidence: High.* (Bounded-WCET allocators (TLSF) and hard-RT GCs exist — see `contested.md` — but commodity runtimes are effectively unbounded.)

## 3. A hot-path lock can block unboundedly
**Heuristic:** A lock taken in the hot path can block the high-priority thread **unboundedly** via priority inversion; plain mutexes (`std::mutex`, default `pthread_mutex` = `PRIO_NONE`, Python `threading.Lock`) have **no** PI control. In order: **(a)** avoid shared-lock contention — single-writer or wait-free **SPSC** ring-buffer hand-off; **(b)** atomics, but verify `is_lock_free` (lock-free ≠ bounded-latency; **wait-free** is); **(c)** if unavoidable, a **PI/ceiling** mutex — and its critical section is now **RT code** (no allocation, syscalls, or unbounded loops). **"Just add a lock to make it thread-safe" is the wrong instinct in an RT loop.**
**Detect:** Does the hot path take a lock lacking priority inheritance, instead of an atomic / PI mutex / lock-free SPSC hand-off?
*Source:* PickNik "Real-Time Programming: Priority Inversion"; ROS 2 design proposal; Buttazzo. *Confidence: High.*

## 4. Deterministic ≠ fast; bound every loop
**Heuristic:** Hard-RT wants **bounded WCET + low jitter**, NOT minimal work or best average. Trap: optimizations that lower the average but **widen the tail** — caches/memoization that sometimes miss, lazy/first-touch init, adaptive/iterative refinement, dynamic structures that occasionally rehash/realloc. Keep in-loop work **fixed-cost and branch-stable**; pre-bake heavy/variable work in an **init phase** (preallocate, prefault, `mlockall`, warm caches). Every loop needs a **statically known iteration bound** — no "iterate until converged" (unanalyzable WCET); data-dependent loops are OK only with a provable upper bound you budget against. Validate by the **MAX and overrun count over a long stressed run** (cyclictest's "Max"), not the mean — and respect **response time ≤ deadline** (deadline may be shorter than the period).
**Detect:** Was the loop tuned for best average in a way that introduces occasional slow iterations, or does it contain an unbounded ("until converged") loop?
*Source:* Buttazzo (predictability over speed); NI RT best practices; cyclictest practice. *Confidence: High.*

---
**Live API → context7.** **Related:** `priority-inversion.md` (the lock protocol), `rate-decoupling.md` (pre-baking heavy work), `ros2-system-design` (the `ros2_control` update loop).
