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
