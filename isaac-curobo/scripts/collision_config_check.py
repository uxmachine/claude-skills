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
