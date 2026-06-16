# Priority inversion & shared-resource blocking — durable

Why high RT priority alone doesn't guarantee deadlines once tasks share a lock.

## 1. Unbounded inversion is caused by MEDIUM-priority tasks
**Heuristic:** High task H blocks on a resource held by low task L. The inversion becomes **unbounded** only because **medium-priority tasks M** (which don't use the resource) preempt L, indefinitely delaying L's release — and thus H. **Without any medium task, the inversion is bounded** to L's critical section. The defect is the absence of a protocol that raises L's priority while it holds H's lock.
**Detect:** Does the explanation blame "L is slow" or "H itself," instead of medium-priority tasks preempting the low-priority holder?
*Source:* Sha, Rajkumar & Lehoczky (1990) §2; Buttazzo (resource-access protocols). *Confidence: High.*

## 2. The fix bounds blocking — and applies only to cross-priority contention
**Heuristic:** Any lock shared between RT tasks of **different** priorities must use **priority inheritance** (`PTHREAD_PRIO_INHERIT`) or a **ceiling** protocol (`PTHREAD_PRIO_PROTECT`) — **or eliminate the shared lock** (lock-free queue, single-owner data, message passing). A plain mutex with **no** protocol leaves inversion **unbounded**. The rule is **cross-priority only**: a lock used by tasks all at the same priority needs no protocol (equal-priority `SCHED_FIFO` tasks don't preempt). **Verify the default per platform** — POSIX mutexes default to `PTHREAD_PRIO_NONE`, but e.g. FreeRTOS mutexes default PI *on*.
**Detect:** Are RT tasks of different priorities sharing a plain mutex, or is PI assumed automatic?
*Source:* Sha et al. (1990); POSIX `pthread_mutexattr_setprotocol`. *Confidence: High.*

## 3. Inheritance ≠ ceiling — don't conflate their guarantees
**Heuristic:** **Basic priority inheritance** bounds blocking but **NOT to one critical section** (up to `min(n,m)` critical sections) and does **NOT** prevent **deadlock** or **chained/transitive blocking**. **Priority ceiling** (original PCP, or the Immediate-Ceiling / Highest-Locker variant = `PTHREAD_PRIO_PROTECT`) bounds blocking to **one** critical section and provably prevents deadlock — at the cost of needing **a-priori knowledge of every task that uses each resource** (static analysis to set ceilings).
**Detect:** Does the answer claim priority inheritance limits blocking to one critical section or prevents deadlock? (That's the ceiling protocol's guarantee, not inheritance's.)
*Source:* Sha et al. (1990) theorems; Buttazzo. *Confidence: High.*

## 4. Inheritance is transitive and dynamic
**Heuristic:** A lock holder inherits the **maximum** priority of **all** tasks currently blocked on it (not the first blocker, not a fixed boost), and if it's itself blocked on a second lock the inheritance **propagates down the chain**. It reverts to base priority only on **release** (or to the next-highest level it still inherits from remaining held locks).
**Detect:** Is inheritance described as a fixed boost / first-waiter, or non-propagating?
*Source:* Sha et al. (1990); Buttazzo. *Confidence: High.*

## 5. Add the blocking term to the analysis — the Pathfinder lesson
**Heuristic:** A bounded blocking term `B_i` must be **added into the schedulability/response-time analysis** — protocols make blocking bounded, not zero. **Mars Pathfinder:** the mutex **already existed** (a VxWorks `semMCreate` on the shared `select()` fd-list); the bug was **priority inheritance not enabled**; the fix was **flipping the existing semaphore's inversion-safe flag** (`SEM_INVERSION_SAFE`, uplinked as a config change) — **not** adding a mutex, removing a lock, or rewriting the scheduler.
**Detect:** Is the Pathfinder fix described as "adding/removing a lock" or "rewriting the scheduler" instead of enabling PI on an existing mutex?
*Source:* Reeves, "What really happened on Mars" (1997); VxWorks `SEM_INVERSION_SAFE`. *Confidence: High.*

---
**Related:** `hotpath.md` (a hot-path lock is now RT code), `rate-decoupling.md` (the unbounded non-RT producer). See `contested.md` for platform mutex-default variation.
