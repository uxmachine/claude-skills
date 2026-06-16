# ROS2 executors & callback groups — durable traps

Where ROS2 concurrency bugs live. **Exact API (`ReentrantCallbackGroup`, `call_async`) via `context7` (resolve `rclpy`/`rclcpp`).**

## 1. Single-threaded executor = no parallelism, period
**Heuristic:** A `SingleThreadedExecutor` (incl. `rclpy.spin()` / the default) runs **every callback sequentially on one thread**. Callback groups buy you **nothing** there — only a `MultiThreadedExecutor` runs callbacks concurrently, and even then parallelism is a **capability bounded by the thread-pool size**, not a guarantee.
**Detect:** Does the code expect a Reentrant (or any) callback group to give parallelism while spun by a single-threaded executor?
*Source:* docs.ros.org "About Executors"; "Using callback groups". *Confidence: High.*

## 2. The default callback group is MutuallyExclusive
**Heuristic:** Entities created **without** an explicit callback group land in the node's **one default group, which is MutuallyExclusive** — so all of them are serialized (behaves single-threaded for that group), even under a `MultiThreadedExecutor`.
**Detect:** Does the design assume callbacks created without an explicit group run independently / in parallel?
*Source:* docs.ros.org "About Executors"; rclcpp/rclpy `NodeBase`. *Confidence: High.*

## 3. The sync-call-in-callback deadlock — cause is the shared MX group, not a busy thread
**Heuristic:** A **synchronous** service/action call (waiting on the future) **inside a callback** deadlocks **silently** when the calling callback and the client share the **same MutuallyExclusive callback group** (the default): the future's done-callback can never run while the callback is blocked. The cause is **callback-group contention, NOT "the one executor thread is busy."** It's **avoidable, not forbidden**: put the client in a **different** callback group (any type) or a **Reentrant** group under a `MultiThreadedExecutor` — or just prefer `call_async` + `add_done_callback`. **Moving both into the same *new* MX group fixes nothing.**
**Detect:** Is the fix "a second MutuallyExclusive group" (still deadlocks), or is the cause mis-attributed to thread count rather than the shared MX group?
*Source:* docs.ros.org "Using callback groups" ("…different callback groups (of any type), or a Reentrant Callback Group"); rclpy #1016. *Confidence: High.*

## 4. Don't drive an executor from inside its own callback
**Heuristic:** Calling `spin()` / `spin_once()` / `spin_until_future_complete()` on the **already-spinning** executor raises `RuntimeError("Executor is already spinning")`. The global `rclpy.spin_until_future_complete()` is worse — it spins up a **throwaway executor and detaches your node** from its real one. Use `call_async` + `add_done_callback`; never nest spin.
**Detect:** Does a callback call any `spin*` on its own executor, or use the global `spin_until_future_complete` on a node that already has an executor?
*Source:* rclpy `executors.py` `_enter_spin` guard; rclpy #1159/#398. *Confidence: High.*

---
**Live API → context7.** Method/class names evolve; resolve current API via `context7`/docs. **Related:** `lifecycle-composition.md` (managed nodes), `dds-control.md` (the `ros2_control` RT loop), `realtime-determinism` (hot-path rules).
