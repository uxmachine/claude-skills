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
