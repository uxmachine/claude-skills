# Contested / version-fragile notes

Survived research but **not baked principles** — version-specific or true-only-with-a-caveat. Consult before treating a borderline point as settled.

## Intra-process `transient_local` — added later, and in-process reliability never resends
The **original** intra-process design **could not be used with `transient_local` durability** ("can't be used when the QoS durability value is set to Transient Local"). Support was **added in `rclcpp` PR #2303 (merged Jan 2024, Jazzy onward)** via a publisher-side buffer; serving late-joining subscriptions in *other* processes requires dual intra+inter-process publishing (only for the cross-process late-joiner case, not unconditionally). Durable takeaway that does **not** age: in-process **reliability is compatibility-checked only — there is no in-process retransmission** for either reliable or best-effort (buffers guarantee delivery without resending). So don't assume QoS-transparency across the intra-process vs DDS paths.
*Source:* design.ros2.org "Intra-process Communications"; rclcpp PR #2303. *Status: contested — transient_local support is distro-dependent (Jazzy+).*

## `ros2_control` specifics — the 100 Hz default and "lock-free" wording
The `update_rate` "**100 Hz**" is a **default, configurable** value — don't bake the number. And `realtime_tools` **`RealtimeBuffer` is a try-lock, NOT lock-free** (it falls back to the last value); the genuinely lock-free primitive is **`LockFreeQueue`**, while `RealtimeThreadSafeBox` is best-effort locking. The **durable** invariant is the RT/non-RT boundary + a **single-writer hand-off** + reaching hardware only through `hardware_interface` — the specific class names and the rate are version-pinned.
*Source:* control.ros.org `controller_manager`; `realtime_tools` (#14). *Status: contested — API/rate are version-specific; the boundary concept is durable.*
