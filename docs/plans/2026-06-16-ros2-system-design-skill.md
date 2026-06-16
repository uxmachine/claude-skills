# ros2-system-design Skill — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans (inline) — research Workflow + judgment authoring don't decompose into per-task subagents. Steps use `- [ ]`.

**Goal:** Build the portable `ros2-system-design` skill — durable ROS2 structure judgment (QoS / executors / lifecycle+composition / DDS+ros2_control) + a deterministic QoS-compatibility checker — to the repo standard.

**Architecture:** Same shape as `isaac-curobo`: `SKILL.md` routes to `resources/{qos,executors,lifecycle-composition,dds-control,contested}.md` (each principle sourced + confidence-tagged, authored from an adversarially-verified research run) and ships `scripts/qos_compat.py` (pub-vs-sub Request-vs-Offered compatibility) with a test.

**Tech Stack:** Python 3 stdlib (`json`, `dataclasses`); pytest; the research Workflow; `context7` for live API. Portfolio spec: `docs/specs/2026-06-16-robotics-skills-portfolio-design.md` §4.2.

---

## File structure

```
~/claude-skills/ros2-system-design/
  SKILL.md
  resources/{qos,executors,lifecycle-composition,dds-control,contested}.md
  scripts/qos_compat.py
  tests/test_qos_compat.py
```

Worktree root: `~/.config/superpowers/worktrees/claude-skills/ros2-system-design/`.

## Phase 1 — Research (background Workflow, already launched)

### Task 1: Run + harvest the research Workflow
- [ ] Workflow `ros2-system-design-research` (qos / executors / lifecycle_composition / dds_control finders → adversarial skeptics). On completion: apply the bar (model-reliably-wrong AND durable); confirmed-durable → baked, contested/fragile → `contested.md`, refuted → dropped.

## Phase 2 — Tool (TDD, full code)

### Task 2: `qos_compat.py` — Request-vs-Offered compatibility

**Files:** Create `ros2-system-design/scripts/qos_compat.py`, Test `ros2-system-design/tests/test_qos_compat.py`.

- [ ] **Step 1: Write the failing test**

```python
"""Test-first. Stdlib only."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import qos_compat as q  # noqa: E402


def codes(pub, sub):
    return {x.code for x in q.check(pub, sub)}


def test_default_profiles_compatible():
    assert q.compatible(q.check({}, {}))


def test_best_effort_pub_reliable_sub_incompatible():
    assert "reliability_incompatible" in codes({"reliability": "best_effort"}, {"reliability": "reliable"})
    assert not q.compatible(q.check({"reliability": "best_effort"}, {"reliability": "reliable"}))


def test_reliable_pub_best_effort_sub_ok():
    assert q.compatible(q.check({"reliability": "reliable"}, {"reliability": "best_effort"}))


def test_volatile_pub_transient_local_sub_incompatible():
    assert "durability_incompatible" in codes({"durability": "volatile"}, {"durability": "transient_local"})


def test_deadline_offered_longer_than_requested_incompatible():
    assert "deadline_incompatible" in codes({"deadline": 1.0}, {"deadline": 0.5})


def test_deadline_offered_shorter_ok():
    assert q.compatible(q.check({"deadline": 0.2}, {"deadline": 0.5}))


def test_liveliness_kind_incompatible():
    assert "liveliness_kind_incompatible" in codes({"liveliness": "automatic"}, {"liveliness": "manual_by_topic"})


def test_liveliness_lease_incompatible():
    assert "liveliness_lease_incompatible" in codes({"liveliness_lease": 2.0}, {"liveliness_lease": 1.0})


def test_history_is_local_not_rxo():
    assert q.compatible(q.check({"history": "keep_last", "depth": 1},
                                {"history": "keep_all", "depth": 1000}))


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
```

- [ ] **Step 2: Run; verify FAIL** — `python3 -m pytest ros2-system-design/tests/test_qos_compat.py -q` → `ModuleNotFoundError`.

- [ ] **Step 3: Implement** `ros2-system-design/scripts/qos_compat.py`:

```python
"""ROS2 QoS Request-vs-Offered (RxO) compatibility checker. Given a publisher (offered)
and subscriber (requested) QoS, decide whether they CONNECT — an incompatible pair silently
exchanges no data with no error. Only RxO policies matter: reliability, durability, deadline,
liveliness. history/depth/lifespan are LOCAL and do NOT affect compatibility. Stdlib only.

Normalized schema (JSON), keys optional (ROS2 default profile assumed if absent):
  reliability: "reliable" | "best_effort"      (default reliable)
  durability:  "transient_local" | "volatile"  (default volatile)
  deadline:    number seconds | null=infinite   (default infinite)
  liveliness:  "manual_by_topic" | "automatic"  (default automatic)
  liveliness_lease: number seconds | null=infinite (default infinite)
"""
from __future__ import annotations
import json
import sys
from dataclasses import dataclass

ERROR = "error"
_REL = {"best_effort": 1, "reliable": 2}
_DUR = {"volatile": 1, "transient_local": 2}
_LIV = {"automatic": 1, "manual_by_topic": 2}
INF = float("inf")


@dataclass
class Finding:
    severity: str
    code: str
    message: str


def _period(v):
    return INF if v is None else float(v)


def check(pub: dict, sub: dict) -> list:
    f: list = []
    if _REL[pub.get("reliability", "reliable")] < _REL[sub.get("reliability", "reliable")]:
        f.append(Finding(ERROR, "reliability_incompatible",
                 "offered BEST_EFFORT < requested RELIABLE: subscriber will not connect (no data, no error)."))
    if _DUR[pub.get("durability", "volatile")] < _DUR[sub.get("durability", "volatile")]:
        f.append(Finding(ERROR, "durability_incompatible",
                 "offered VOLATILE < requested TRANSIENT_LOCAL: no connection (and no late-joiner history)."))
    p_dl, s_dl = _period(pub.get("deadline")), _period(sub.get("deadline"))
    if p_dl > s_dl:
        f.append(Finding(ERROR, "deadline_incompatible",
                 f"offered deadline {p_dl}s > requested {s_dl}s: publisher does not promise updates "
                 f"often enough; no connection."))
    if _LIV[pub.get("liveliness", "automatic")] < _LIV[sub.get("liveliness", "automatic")]:
        f.append(Finding(ERROR, "liveliness_kind_incompatible",
                 "offered AUTOMATIC < requested MANUAL_BY_TOPIC: no connection."))
    p_lease, s_lease = _period(pub.get("liveliness_lease")), _period(sub.get("liveliness_lease"))
    if p_lease > s_lease:
        f.append(Finding(ERROR, "liveliness_lease_incompatible",
                 f"offered liveliness lease {p_lease}s > requested {s_lease}s: no connection."))
    return f


def compatible(findings: list) -> bool:
    return not any(x.severity == ERROR for x in findings)


def main(argv: list) -> int:
    if len(argv) != 2:
        print('usage: qos_compat.py <pair.json>   # {"pub": {...}, "sub": {...}}', file=sys.stderr)
        return 2
    with open(argv[1]) as fh:
        d = json.load(fh)
    findings = check(d.get("pub", {}), d.get("sub", {}))
    if not findings:
        print("[OK] QoS compatible: publisher and subscriber will connect.")
        return 0
    for x in findings:
        print(f"[{x.severity.upper()}] {x.code}: {x.message}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
```

- [ ] **Step 4: Run; verify PASS** (9 passed). **Step 5: Commit** `feat(ros2-system-design): qos_compat RxO checker`.

## Phase 3 — Resources (from verified findings)

### Task 3: Author `resources/*.md`
- [ ] `qos.md` — RxO compatibility per policy (reliability/durability/deadline/liveliness), the silent-no-connect trap, RxO-vs-local (history/lifespan), default-profile mismatch. Ties to `qos_compat.py`.
- [ ] `executors.md` — single vs multi-threaded; MutuallyExclusive vs Reentrant callback groups; the service-call-inside-callback deadlock + the separate-callback-group fix.
- [ ] `lifecycle-composition.md` — managed-node state machine (inactive ⇒ no processing); components/process-topology decoupling; intra-process zero-copy conditions.
- [ ] `dds-control.md` — `ROS_DOMAIN_ID`/RMW-must-match discovery; the `ros2_control` RT update loop + HAL seam (no alloc/block in `update()`).
- [ ] `contested.md` — version-fragile / oversimplified survivors.
- [ ] Each principle: heuristic + detection question + `Source:` + `Confidence:`. Commit `docs(ros2-system-design): sourced resources`.

## Phase 4 — SKILL.md + wire-up + merge

### Task 4: SKILL.md, README, suite, integrate
- [ ] `SKILL.md`: trigger (QoS/executors/lifecycle/composition/DDS/ros2_control), routing procedure (run `qos_compat.py` for pub/sub mismatches), `context7` delegation note, Rule-4 footer, cross-links (`isaac-curobo`, `realtime-determinism`, `system-architecture-design`).
- [ ] README row + install + (tests already covered by the all-skills command).
- [ ] Full suite green; symlink `~/.claude/skills/ros2-system-design`.
- [ ] FF-merge feature → main + push to `uxmachine/claude-skills`; remove worktree + delete branches.

## Self-Review
- Spec §4.2 coverage: QoS checker (Task 2), QoS/executor/lifecycle/DDS-control resources (Task 3), trigger + routing (Task 4), context7 split + cross-links (Task 4). ✓
- Tool code complete + type-consistent (`check`/`compatible`/`Finding`). ✓
- Resource prose gated on Task 1 findings (structure + sources + confidence specified, not placeholders). ✓
