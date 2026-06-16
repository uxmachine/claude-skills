# isaac-curobo Skill — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the portable `isaac-curobo` Claude skill — durable cuRobo / OpenUSD / Isaac-ROS judgment + traps, two deterministic tested tools — to the `system-architecture-design` standard.

**Architecture:** One skill, sub-sectioned by routing so the combined scope never blurs: `SKILL.md` routes to `resources/{curobo,usd-assets,isaac-ros}.md` (each principle sourced + confidence-tagged, authored from an adversarially-verified deep-research run) and ships two stdlib tools: `collision_config_check.py` (does a config *guarantee* clearance or only *penalize* penetration?) and `asset_lint.py` (URDF + USD-lite mistake catcher). Exact, churning cuRobo/Isaac API is delegated to `context7` at runtime; the skill holds only the durable layer.

**Tech Stack:** Python 3 stdlib only (`xml.etree`, `json`, `re`, `dataclasses`); pytest; the `Workflow` tool for research; `context7` MCP for live API. No third-party deps in shipped tools (matches the predecessor).

**Scope:** This plan builds **skill #1 only.** `ros2-system-design`, `robotic-line-design`, `realtime-determinism` each get their own plan from the same spec/template. Spec: `docs/specs/2026-06-16-robotics-skills-portfolio-design.md`.

---

## File structure (created by this plan)

```
~/claude-skills/isaac-curobo/
  SKILL.md                       # frontmatter + routing procedure + Rule-4 footer (Task 9)
  resources/
    curobo.md                    # GPU-planner guarantee-vs-penalty, world reprs, poison trap (Task 4)
    usd-assets.md                # composition arcs, up-axis, metersPerUnit, UsdPhysics (Task 5)
    isaac-ros.md                 # NITROS zero-copy, GEMs, nvblox->cuRobo bridge, frames (Task 6)
    contested.md                 # disagreements / version-fragile claims demoted here (Tasks 4-6)
  scripts/
    collision_config_check.py    # Task 7
    asset_lint.py                # Task 8
  tests/
    test_collision_config_check.py   # Task 7
    test_asset_lint.py               # Task 8
~/claude-skills/README.md        # add an isaac-curobo row (Task 10)
~/.claude/skills/isaac-curobo    # symlink (Task 10)
```

All paths below are relative to the worktree root: `~/.config/superpowers/worktrees/claude-skills/robotics-skills-portfolio/`.

---

## Phase 0 — Scaffold

### Task 1: Create the skill directory tree

**Files:** Create `isaac-curobo/{resources,scripts,tests}/` (empty dirs + `.gitkeep` where needed).

- [ ] **Step 1: Make the dirs**

Run:
```bash
cd ~/.config/superpowers/worktrees/claude-skills/robotics-skills-portfolio
mkdir -p isaac-curobo/resources isaac-curobo/scripts isaac-curobo/tests
```

- [ ] **Step 2: Commit the scaffold marker**

```bash
touch isaac-curobo/tests/.gitkeep
git add isaac-curobo/tests/.gitkeep
git commit -m "chore(isaac-curobo): scaffold skill directory"
```

---

## Phase 1 — Research (produces the raw material for resources)

### Task 2: Run the deep-research workflow for the three sub-areas

**Files:** none yet — this produces verified findings consumed by Tasks 4–6. Save the workflow's structured output to `isaac-curobo/resources/_research_findings.json` (gitignored scratch; deleted in Task 10).

**This is a research task, not TDD.** Definition of done: for each sub-area, a list of candidate principles, each with `{claim, source, confidence, survived_refutation: bool, contested_note?}`.

- [ ] **Step 1: Author and launch the research workflow**

Use the `Workflow` tool. The script fans out one finder per sub-area against **durable canonical sources only**, then runs a skeptic pass per candidate principle (adversarial verify — the skeptic tries to refute or find the counter-case / version-fragility), then returns structured findings. Target sources:
- **curobo:** cuRobo paper (Sundaralingam et al., ICRA 2023) + cuRobo docs *concepts* pages (collision world, motion_gen, robot config); the durable principle is *"a planner's hard feasibility is penetration-based; activation/cost terms are soft and vanish at feasibility."* Tag anything tied to a specific field name as `version_fragile` → `context7`-delegated, NOT a baked principle.
- **usd-assets:** OpenUSD docs (AOUSD) — composition arcs, `upAxis`, `metersPerUnit`; `UsdPhysics` schema docs; ROS `urdf`/Isaac URDF-importer docs.
- **isaac-ros:** Isaac ROS docs (NITROS / type adaptation), nvblox paper/docs (ESDF), REP-103/105 (frames).

Acceptance gate (encode in the script): drop any claim a majority of skeptics refute; demote `version_fragile` or contested survivors to a `contested` bucket. Return `{curobo: [...], usd_assets: [...], isaac_ros: [...], contested: [...]}`.

- [ ] **Step 2: Save findings**

Write the workflow's returned object to `isaac-curobo/resources/_research_findings.json`. Verify each sub-area has ≥3 survived principles; if not, re-run that finder with broadened sources.

### Task 3: Sanity-check findings against the bar

- [ ] **Step 1: Apply the inclusion gate by hand**

For each candidate principle confirm BOTH: (a) the model reliably gets it wrong, (b) it is durable. Delete any that are merely "how X works." Move version-fragile survivors to the `contested`/`context7`-delegated set. No code; this is a judgment pass over the JSON.

---

## Phase 2 — Resources (author from verified findings)

> Each resource file: one principle per subsection — a one-line heuristic, the **detection question**, then `Source: … · Confidence: High|Medium|contested`. Progressive disclosure: `SKILL.md` tells the reader to open only the file whose step is live.

### Task 4: Write `resources/curobo.md`

**Files:** Create `isaac-curobo/resources/curobo.md`.

- [ ] **Step 1: Author the file** from the `curobo` findings. Required subsections (each only if it survived verification — do not invent):
  - **Guarantee vs penalty** — heuristic: *"`activation_distance` is a soft cost, not a clearance guarantee; for guaranteed clearance you need an explicit hard margin."* Detection question: *"Does the config set a hard clearance/feasibility margin ≥ the clearance you need, or only an activation distance?"* (This is the durable principle behind the `collision_config_check` tool.)
  - **World representations** — cuboid / mesh-SDF / sphere / voxel / nvblox-ESDF tradeoffs; the **mesh-SDF search-radius ≥ largest robot sphere** trap ("poison").
  - **Robot sphere coverage** — uncovered links are invisible to the planner.
  - **MotionGen vs IKSolver; seeds; success gates** — a tight position tolerance is *cost-only*, not a feasibility gate.
  - A closing **"Live API → context7"** note: field names (`activation_distance`, `MotionGenConfig`, etc.) change by version — fetch current names from `context7`/cuRobo docs; this file holds only the concepts.
- [ ] **Step 2: Verify every subsection has a `Source:` + `Confidence:` line.** Move any version-fragile claim to `contested.md`.
- [ ] **Step 3: Commit**

```bash
git add isaac-curobo/resources/curobo.md
git commit -m "docs(isaac-curobo): cuRobo guarantee-vs-penalty + world-repr resource"
```

### Task 5: Write `resources/usd-assets.md`

**Files:** Create `isaac-curobo/resources/usd-assets.md`.

- [ ] **Step 1: Author** from `usd_assets` findings: composition arcs (reference/payload/sublayer/variant — which when); **up-axis Z vs Y**; **metersPerUnit** (the mm↔m trap); `UsdPhysics` (collision approximation, mass, joints); URDF↔USD importer pitfalls; instancing. Each with source + confidence. Note which checks the `asset_lint` tool automates.
- [ ] **Step 2: Commit**

```bash
git add isaac-curobo/resources/usd-assets.md
git commit -m "docs(isaac-curobo): OpenUSD asset conventions + unit traps resource"
```

### Task 6: Write `resources/isaac-ros.md` + `resources/contested.md`

**Files:** Create `isaac-curobo/resources/isaac-ros.md`, `isaac-curobo/resources/contested.md`.

- [ ] **Step 1: Author `isaac-ros.md`** from `isaac_ros` findings: NITROS type-adaptation / zero-copy (when it applies); GEMs; the **nvblox ESDF → cuRobo world** bridge; frame conventions (REP-103/105); GPU/CPU sync. Source + confidence each.
- [ ] **Step 2: Author `contested.md`** from the `contested` bucket: each disagreement / version-fragile claim with both sides and why it's not a baked principle.
- [ ] **Step 3: Commit**

```bash
git add isaac-curobo/resources/isaac-ros.md isaac-curobo/resources/contested.md
git commit -m "docs(isaac-curobo): Isaac ROS/nvblox bridge + contested notes"
```

---

## Phase 3 — Tools (TDD, full code)

### Task 7: `collision_config_check.py` — guarantee-vs-penalty + poison + coverage

**Files:**
- Create: `isaac-curobo/scripts/collision_config_check.py`
- Test: `isaac-curobo/tests/test_collision_config_check.py`

- [ ] **Step 1: Write the failing test**

`isaac-curobo/tests/test_collision_config_check.py`:
```python
"""Test-first. Stdlib only; runs under pytest or as a plain script."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import collision_config_check as c  # noqa: E402


def codes(cfg):
    return {f.code for f in c.check(cfg)}


def test_activation_distance_is_only_soft_penalty():
    cfg = {"collision": {"activation_distance": 0.01},
           "request": {"required_clearance": 0.01}}
    assert "soft_penalty_only" in codes(cfg)
    assert not c.guaranteed(c.check(cfg))


def test_explicit_hard_margin_guarantees():
    cfg = {"collision": {"clearance_margin": 0.012},
           "request": {"required_clearance": 0.01}}
    assert c.guaranteed(c.check(cfg))


def test_margin_too_small_is_error():
    cfg = {"collision": {"clearance_margin": 0.005},
           "request": {"required_clearance": 0.01}}
    assert "margin_too_small" in codes(cfg)


def test_mesh_sdf_poison_detected():
    cfg = {"robot": {"spheres": {"link6": [{"radius": 0.05}]}},
           "world": {"representation": "mesh", "mesh_max_distance": 0.02}}
    assert "mesh_sdf_poison" in codes(cfg)


def test_mesh_ok_when_band_large_enough():
    cfg = {"robot": {"spheres": {"link6": [{"radius": 0.05}]}},
           "world": {"representation": "mesh", "mesh_max_distance": 0.06}}
    assert "mesh_sdf_poison" not in codes(cfg)


def test_uncovered_link_flagged():
    cfg = {"robot": {"spheres": {"tool": []}}}
    assert "uncovered_link" in codes(cfg)


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
```

- [ ] **Step 2: Run it; verify it fails**

Run: `cd ~/.config/superpowers/worktrees/claude-skills/robotics-skills-portfolio && python3 -m pytest isaac-curobo/tests/test_collision_config_check.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'collision_config_check'`.

- [ ] **Step 3: Write the implementation**

`isaac-curobo/scripts/collision_config_check.py`:
```python
"""Concept-level check: does a cuRobo-style collision config GUARANTEE clearance,
or only PENALIZE penetration? Operates on a NORMALIZED schema (field names map to the
live cuRobo API via context7). Stdlib only.

Schema (JSON):
  robot.spheres: { link_name: [ {radius: float}, ... ] }
  world.representation: "cuboid"|"mesh"|"sphere"|"voxel"|"nvblox"
  world.mesh_max_distance: float        # SDF query band (mesh only)
  collision.activation_distance: float  # SOFT cost term
  collision.clearance_margin: float     # HARD clearance margin (None => none)
  request.required_clearance: float     # what the caller wants guaranteed
"""
from __future__ import annotations
import json
import sys
from dataclasses import dataclass

ERROR, WARN, INFO = "error", "warn", "info"


@dataclass
class Finding:
    severity: str
    code: str
    message: str


def check(cfg: dict) -> list:
    f: list = []
    robot = cfg.get("robot", {})
    spheres = robot.get("spheres", {})
    world = cfg.get("world", {})
    coll = cfg.get("collision", {})
    req = cfg.get("request", {})

    required = req.get("required_clearance")
    margin = coll.get("clearance_margin")
    act = coll.get("activation_distance")
    if required is not None:
        if margin is not None and margin >= required:
            f.append(Finding(INFO, "clearance_guaranteed",
                     f"hard clearance_margin {margin} >= required {required}: clearance guaranteed."))
        elif margin is not None and margin < required:
            f.append(Finding(ERROR, "margin_too_small",
                     f"clearance_margin {margin} < required {required}."))
        elif act is not None:
            f.append(Finding(ERROR, "soft_penalty_only",
                     f"only activation_distance ({act}) constrains collision; it is a SOFT cost "
                     f"that vanishes at feasibility and does NOT guarantee {required} clearance. "
                     f"Set an explicit hard clearance margin >= {required}."))
        else:
            f.append(Finding(WARN, "no_clearance_constraint",
                     "no clearance_margin and no activation_distance: collision is unconstrained."))

    if world.get("representation") == "mesh":
        radii = [s.get("radius", 0.0) for L in spheres.values() for s in L]
        max_r = max(radii) if radii else 0.0
        mmd = world.get("mesh_max_distance")
        if mmd is not None and max_r > 0 and mmd < max_r:
            f.append(Finding(ERROR, "mesh_sdf_poison",
                     f"mesh_max_distance ({mmd}) < largest robot sphere radius ({max_r}): the SDF "
                     f"has no gradient beyond its band, so collisions are under-reported ('poison'). "
                     f"Set mesh_max_distance >= {max_r}."))

    for link, L in spheres.items():
        if not L:
            f.append(Finding(WARN, "uncovered_link",
                     f"link '{link}' has no collision spheres: it is invisible to the planner."))
    return f


def guaranteed(findings: list) -> bool:
    return (any(x.code == "clearance_guaranteed" for x in findings)
            and not any(x.severity == ERROR for x in findings))


def main(argv: list) -> int:
    if len(argv) != 2:
        print("usage: collision_config_check.py <config.json>", file=sys.stderr)
        return 2
    with open(argv[1]) as fh:
        cfg = json.load(fh)
    findings = check(cfg)
    for x in findings:
        print(f"[{x.severity.upper()}] {x.code}: {x.message}")
    return 1 if any(x.severity == ERROR for x in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
```

- [ ] **Step 4: Run; verify pass**

Run: `python3 -m pytest isaac-curobo/tests/test_collision_config_check.py -q`
Expected: PASS (6 passed).

- [ ] **Step 5: Commit**

```bash
git add isaac-curobo/scripts/collision_config_check.py isaac-curobo/tests/test_collision_config_check.py
git commit -m "feat(isaac-curobo): collision_config_check tool (guarantee vs penalty, mesh poison)"
```

### Task 8: `asset_lint.py` — URDF mistakes + USD-lite

**Files:**
- Create: `isaac-curobo/scripts/asset_lint.py`
- Test: `isaac-curobo/tests/test_asset_lint.py`

- [ ] **Step 1: Write the failing test**

`isaac-curobo/tests/test_asset_lint.py`:
```python
"""Test-first. Stdlib only."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import asset_lint as a  # noqa: E402

GOOD = """<robot name="r">
  <link name="base"><inertial><mass value="1"/>
    <inertia ixx="1" iyy="1" izz="1" ixy="0" ixz="0" iyz="0"/></inertial></link>
  <link name="l1"><inertial><mass value="1"/>
    <inertia ixx="1" iyy="1" izz="1" ixy="0" ixz="0" iyz="0"/></inertial></link>
  <joint name="j1" type="revolute"><parent link="base"/><child link="l1"/></joint>
</robot>"""


def codes(text):
    return {f.code for f in a.lint_urdf(text)}


def test_good_urdf_has_no_errors():
    assert [f for f in a.lint_urdf(GOOD) if f.severity == "error"] == []


def test_inertia_not_positive_definite():
    bad = GOOD.replace('ixx="1" iyy="1" izz="1" ixy="0" ixz="0" iyz="0"/></inertial></link>\n  <joint',
                       'ixx="-1" iyy="1" izz="1" ixy="0" ixz="0" iyz="0"/></inertial></link>\n  <joint')
    assert "inertia_not_pd" in codes(bad)


def test_nonpositive_mass_on_movable_link():
    bad = GOOD.replace('<link name="l1"><inertial><mass value="1"/>',
                       '<link name="l1"><inertial><mass value="0"/>')
    assert "nonpositive_mass" in codes(bad)


def test_duplicate_joint_name():
    bad = GOOD.replace("</robot>",
        '<joint name="j1" type="fixed"><parent link="l1"/><child link="base"/></joint></robot>')
    assert "duplicate_name" in codes(bad)


def test_dangling_mimic():
    bad = GOOD.replace('<parent link="base"/><child link="l1"/></joint>',
        '<parent link="base"/><child link="l1"/><mimic joint="ghost"/></joint>')
    assert "dangling_mimic" in codes(bad)


def test_two_roots():
    bad = GOOD.replace(
        '<joint name="j1" type="revolute"><parent link="base"/><child link="l1"/></joint>', "")
    assert "bad_tree_root" in codes(bad)


def test_unit_scale_smell():
    bad = GOOD.replace("</robot>",
        '<link name="l2"><visual><geometry><mesh filename="a.stl" scale="0.001 0.001 0.001"/>'
        '</geometry></visual></link></robot>')
    assert "unit_scale_smell" in codes(bad)


def test_usd_meters_per_unit_warning():
    usd = 'def "World" {\n  metersPerUnit = 0.01\n  upAxis = "Z"\n}\n'
    assert "usd_meters_per_unit" in {f.code for f in a.lint_usd_text(usd)}


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
```

- [ ] **Step 2: Run it; verify it fails**

Run: `python3 -m pytest isaac-curobo/tests/test_asset_lint.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'asset_lint'`.

- [ ] **Step 3: Write the implementation**

`isaac-curobo/scripts/asset_lint.py`:
```python
"""Lint robot-description assets for DURABLE mistakes: broken inertia, zero mass,
unit / up-axis traps, name clashes, broken kinematic tree, dangling mimic.
URDF via stdlib XML; USD via a lightweight text scan (full USD parsing needs `pxr` —
deferred, grows per Rule 4). Stdlib only.
"""
from __future__ import annotations
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass

ERROR, WARN, INFO = "error", "warn", "info"


@dataclass
class Finding:
    severity: str
    code: str
    message: str


def _pd_and_triangle(ixx, iyy, izz, ixy, ixz, iyz):
    # Inertia tensor M = [[ixx,-ixy,-ixz],[-ixy,iyy,-iyz],[-ixz,-iyz,izz]]
    a, b, cc = ixx, iyy, izz
    d, e, ff = -ixy, -ixz, -iyz
    m1 = a
    m2 = a * b - d * d
    m3 = a * (b * cc - ff * ff) - d * (d * cc - ff * e) + e * (d * ff - b * e)
    is_pd = m1 > 0 and m2 > 0 and m3 > 0
    triangle_ok = (ixx + iyy >= izz) and (iyy + izz >= ixx) and (ixx + izz >= iyy)
    return is_pd, triangle_ok


def lint_urdf(xml_text: str) -> list:
    out: list = []
    root = ET.fromstring(xml_text)
    links = [l.get("name") for l in root.findall("link")]
    joints = root.findall("joint")
    jnames = [j.get("name") for j in joints]

    for kind, names in (("link", links), ("joint", jnames)):
        seen = set()
        for n in names:
            if n in seen:
                out.append(Finding(ERROR, "duplicate_name", f"duplicate {kind} name '{n}'"))
            seen.add(n)

    fixed_children = {j.find("child").get("link") for j in joints if j.get("type") == "fixed"}
    for l in root.findall("link"):
        name = l.get("name")
        inertial = l.find("inertial")
        if inertial is None:
            if name not in fixed_children:
                out.append(Finding(WARN, "missing_inertial",
                           f"movable link '{name}' has no <inertial>"))
            continue
        mass_el = inertial.find("mass")
        mass = float(mass_el.get("value")) if mass_el is not None else 0.0
        if mass <= 0 and name not in fixed_children:
            out.append(Finding(ERROR, "nonpositive_mass",
                       f"link '{name}' has mass {mass} but is not a fixed-joint child"))
        i = inertial.find("inertia")
        if i is not None:
            vals = {k: float(i.get(k, 0.0)) for k in ("ixx", "iyy", "izz", "ixy", "ixz", "iyz")}
            is_pd, tri = _pd_and_triangle(**vals)
            if not is_pd:
                out.append(Finding(ERROR, "inertia_not_pd",
                           f"link '{name}' inertia tensor is not positive-definite: {vals}"))
            elif not tri:
                out.append(Finding(WARN, "inertia_triangle",
                           f"link '{name}' principal moments violate the triangle inequality"))

    for mesh in root.iter("mesh"):
        scale = mesh.get("scale")
        if scale:
            comps = [abs(float(x)) for x in scale.split()]
            if any(abs(v - 0.001) < 1e-9 or abs(v - 1000.0) < 1e-6 for v in comps):
                out.append(Finding(WARN, "unit_scale_smell",
                           f"mesh scale '{scale}' has a 1000x/0.001x factor — likely an mm<->m unit "
                           f"fix; verify the source mesh units instead of scaling"))

    jset = set(jnames)
    for j in joints:
        m = j.find("mimic")
        if m is not None and m.get("joint") not in jset:
            out.append(Finding(ERROR, "dangling_mimic",
                       f"joint '{j.get('name')}' mimics unknown joint '{m.get('joint')}'"))

    children = {j.find("child").get("link") for j in joints}
    roots = [l for l in links if l not in children]
    if len(roots) != 1:
        out.append(Finding(ERROR, "bad_tree_root",
                   f"expected exactly one root link, found {len(roots)}: {roots}"))
    return out


_USD_UP = re.compile(r'upAxis\s*=\s*"([XYZ])"')
_USD_MPU = re.compile(r'metersPerUnit\s*=\s*([0-9.eE+-]+)')


def lint_usd_text(text: str) -> list:
    out: list = []
    up = _USD_UP.search(text)
    if up and up.group(1) != "Z":
        out.append(Finding(WARN, "usd_up_axis",
                   f"stage upAxis is {up.group(1)}; robotics/cuRobo conventionally expect Z"))
    mpu = _USD_MPU.search(text)
    if mpu and abs(float(mpu.group(1)) - 1.0) > 1e-9:
        out.append(Finding(WARN, "usd_meters_per_unit",
                   f"metersPerUnit={mpu.group(1)} (not 1.0): every length is scaled — a classic "
                   f"mm<->m trap"))
    return out


def main(argv: list) -> int:
    if len(argv) != 2:
        print("usage: asset_lint.py <file.urdf|file.usd[a]>", file=sys.stderr)
        return 2
    path = argv[1]
    with open(path) as fh:
        text = fh.read()
    findings = lint_urdf(text) if path.endswith(".urdf") else lint_usd_text(text)
    for x in findings:
        print(f"[{x.severity.upper()}] {x.code}: {x.message}")
    return 1 if any(x.severity == ERROR for x in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
```

- [ ] **Step 4: Run; verify pass**

Run: `python3 -m pytest isaac-curobo/tests/test_asset_lint.py -q`
Expected: PASS (8 passed).

- [ ] **Step 5: Commit**

```bash
git add isaac-curobo/scripts/asset_lint.py isaac-curobo/tests/test_asset_lint.py
git commit -m "feat(isaac-curobo): asset_lint tool (URDF inertia/tree/mimic + USD unit traps)"
```

---

## Phase 4 — SKILL.md

### Task 9: Write `SKILL.md` (description + routing procedure + footer)

**Files:** Create `isaac-curobo/SKILL.md`.

- [ ] **Step 1: Author the file**

```markdown
---
name: isaac-curobo
description: Use when planning robot motion with cuRobo, authoring or importing robot/scene assets for Isaac Sim or OpenUSD, or wiring Isaac ROS / nvblox perception — covers the durable concepts, collision & sim semantics, and traps the model gets wrong, and fetches exact current API via context7. Defers to system-architecture-design for system structure.
---

# Isaac / cuRobo — durable concepts, traps, and checks

GPU motion planning (cuRobo), OpenUSD/Isaac Sim assets, and Isaac ROS/nvblox perception change APIs fast. This skill holds only the **durable** layer — what a GPU planner guarantees vs penalizes, collision/sim semantics, the recurring unit and frame traps — and **delegates exact current API to `context7`/official docs.** Read only the resource whose step is live (progressive disclosure).

## Procedure (route, don't dump)

1. **Motion planning / collision?** → open `resources/curobo.md`. Then run `scripts/collision_config_check.py <config.json>` to confirm the config *guarantees* clearance rather than only *penalizing* penetration, and to catch the mesh-SDF "poison" radius and uncovered links.
2. **Authoring / importing a robot or scene asset (URDF / USD)?** → open `resources/usd-assets.md`. Then run `scripts/asset_lint.py <file.urdf|.usd>` for inertia/mass/tree/mimic (URDF) and up-axis / metersPerUnit (USD) traps.
3. **Isaac ROS / nvblox perception?** → open `resources/isaac-ros.md` (NITROS zero-copy, GEMs, the nvblox→cuRobo world bridge, frames).
4. **Need an exact API signature / current field name?** → do NOT trust this skill's wording; fetch it from `context7` (resolve `cuRobo` / `Isaac Sim` / `Isaac ROS`) or the official docs. The skill names the *concept*; context7 has the *current API*.
5. Disagreements / version-fragile claims live in `resources/contested.md` — consult before treating a borderline point as settled.

## Scope guards

- System structure / coupling / boundaries → `system-architecture-design`.
- A specific runtime failure → `superpowers:systematic-debugging`.
- New feature design → `superpowers:brainstorming`.

---

### Improving this skill (every session you use it)

After using this skill, ask: **one-time fix, or forever?** If a correction/example/edge-case should apply every future time, add it to the right `resources/` file now. If you found yourself re-deriving an analysis by hand, add it to a tool.

**Related:** `system-architecture-design` · `ros2-system-design` · `realtime-determinism` · `superpowers:systematic-debugging`.
```

- [ ] **Step 2: Commit**

```bash
git add isaac-curobo/SKILL.md
git commit -m "feat(isaac-curobo): SKILL.md routing procedure + Rule-4 footer"
```

---

## Phase 5 — Wire-up & verify

### Task 10: README row, gitignore scratch, symlink, full-suite green

**Files:** Modify `README.md`; create `.gitignore` entry; symlink into `~/.claude/skills`.

- [ ] **Step 1: Remove the research scratch and ignore it**

```bash
rm -f isaac-curobo/resources/_research_findings.json
echo "isaac-curobo/resources/_research_findings.json" >> .gitignore
```

- [ ] **Step 2: Add a README row** under `## Skills` in `README.md`:

```markdown
- **`isaac-curobo`** — durable cuRobo / OpenUSD / Isaac-ROS judgment + traps (guarantee-vs-penalty collision, world-representation tradeoffs, USD unit/up-axis traps, nvblox→cuRobo bridge). Exact API delegated to `context7`. Ships `collision_config_check.py` and `asset_lint.py` with tests.
```

- [ ] **Step 3: Run the whole skill's tests**

Run: `python3 -m pytest isaac-curobo/tests -q`
Expected: PASS (14 passed — 6 + 8).

- [ ] **Step 4: Symlink into Claude Code and confirm it loads**

```bash
ln -sfn ~/claude-skills/isaac-curobo ~/.claude/skills/isaac-curobo
ls -l ~/.claude/skills/isaac-curobo
```
(The symlink targets the canonical `~/claude-skills` path; the worktree merges there via PR before this is relied on.)

- [ ] **Step 5: Commit**

```bash
git add README.md .gitignore
git commit -m "chore(isaac-curobo): README row + ignore research scratch"
```

### Task 11: Integrate

- [ ] **Step 1: Merge the feature branch into the dev branch** once `commit-review` is clean, then open a PR dev→main (never push to main). Remove the worktree after merge: `git worktree remove <path>`.

---

## Self-Review

**1. Spec coverage** (against `2026-06-16-…-design.md` §4.1):
- Trigger/description → Task 9. ✓
- `resources/{curobo,usd-assets,isaac-ros}.md` routing → Tasks 4–6, 9. ✓
- `collision_config_check.py` (guarantee-vs-penalty, mesh poison, coverage) → Task 7. ✓
- `usd_asset_lint` → Task 8 (`asset_lint.py`, URDF + USD-lite). ✓
- Durable-vs-live (context7) split → Task 9 step 4 + each resource's closing note. ✓
- Excludes Isaac Lab/Replicator → not in any task. ✓
- Sourced + confidence-tagged, adversarially verified → Tasks 2–6. ✓
- Test per tool → Tasks 7–8; full-suite gate Task 10. ✓
- Cross-links + Rule-4 footer → Task 9. ✓

**2. Placeholder scan:** Tool code and SKILL.md are complete. The only intentionally-deferred content is the *resource prose*, which is gated on Task 2's verified findings — Tasks 4–6 specify structure, sources, and the source+confidence acceptance gate, not "TODO." USD full-parse is explicitly deferred (needs `pxr`) and labeled, not silently dropped.

**3. Type consistency:** `check()`/`guaranteed()`/`Finding(severity,code,message)` consistent across Task 7 test+impl; `lint_urdf()`/`lint_usd_text()`/`_pd_and_triangle()` consistent across Task 8 test+impl. Test import pattern (`sys.path.insert … parent.parent/"scripts"`) matches the predecessor.
