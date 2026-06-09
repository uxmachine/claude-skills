#!/usr/bin/env python3
"""architecture_scan.py — deterministic, dependency-free facts for an architecture review.

Three checks (the high-signal floor; grow per Rule 4 only when you keep re-running an analysis):
  1. god files        — files over a line threshold
  2. import boundary   — designated packages must not import forbidden prefixes (AST-based)
  3. duplicate files   — byte-identical content at multiple paths (the contract-by-copy smell)

Usage:
  architecture_scan.py <root> [--max-lines N] [--config cfg.json] [--json]

Config JSON (all optional): {"max_lines": 400, "exts": [".py"],
  "rules": [{"package": "src/core", "forbid": ["xarm", "rclpy"]}]}
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
from pathlib import Path

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".mypy_cache", ".pytest_cache"}


def _walk_files(root: Path, exts):
    for p in sorted(Path(root).rglob("*")):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if exts and p.suffix not in exts:
            continue
        yield p


def find_god_files(root, max_lines: int = 400, exts=(".py",)):
    """Return [(Path, line_count), ...] for files exceeding max_lines, largest first."""
    hits = []
    for p in _walk_files(Path(root), exts):
        try:
            n = sum(1 for _ in p.open("r", encoding="utf-8", errors="ignore"))
        except OSError:
            continue
        if n > max_lines:
            hits.append((p, n))
    return sorted(hits, key=lambda t: t[1], reverse=True)


def _imported_modules(source: str):
    """Yield dotted module names imported by a Python source string."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                yield node.module


def _matches_prefix(name: str, prefix: str) -> bool:
    return name == prefix or name.startswith(prefix + ".")


def find_import_boundary_violations(root, rules):
    """rules: [{"package": <relpath>, "forbid": [<prefix>, ...]}]. Returns list of violation dicts."""
    root = Path(root)
    violations = []
    for rule in rules or []:
        pkg = root / rule["package"]
        if not pkg.exists():
            continue
        for p in _walk_files(pkg, (".py",)):
            try:
                src = p.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for mod in _imported_modules(src):
                for prefix in rule.get("forbid", []):
                    if _matches_prefix(mod, prefix):
                        violations.append(
                            {"file": str(p), "import": mod, "package": rule["package"], "forbidden": prefix}
                        )
    return violations


def find_duplicate_files(root, exts=(".py",)):
    """Group byte-identical (non-empty) files. Returns list of groups (each a sorted list of path strs)."""
    by_hash: dict[str, list[str]] = {}
    for p in _walk_files(Path(root), exts):
        try:
            data = p.read_bytes()
        except OSError:
            continue
        if not data.strip():
            continue
        h = hashlib.sha256(data).hexdigest()
        by_hash.setdefault(h, []).append(str(p))
    return [sorted(g) for g in by_hash.values() if len(g) >= 2]


def scan(root, max_lines: int = 400, rules=None, exts=(".py",)):
    return {
        "root": str(root),
        "god_files": [{"file": str(p), "lines": n} for p, n in find_god_files(root, max_lines, exts)],
        "import_boundary_violations": find_import_boundary_violations(root, rules or []),
        "duplicate_files": find_duplicate_files(root, exts),
    }


def _print_human(report) -> None:
    g, v, d = report["god_files"], report["import_boundary_violations"], report["duplicate_files"]
    print(f"architecture_scan: {report['root']}\n")
    print(f"god files ({len(g)}):")
    for item in g:
        print(f"  {item['lines']:>6}  {item['file']}")
    print(f"\nimport-boundary violations ({len(v)}):")
    for item in v:
        print(f"  {item['file']}  imports  {item['import']}  (forbidden in {item['package']})")
    print(f"\nduplicate-content groups ({len(d)}):")
    for group in d:
        print("  " + " == ".join(group))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Deterministic architecture-review facts.")
    ap.add_argument("root", type=Path)
    ap.add_argument("--max-lines", type=int, default=400)
    ap.add_argument("--config", type=Path, help="JSON: {max_lines, exts, rules}")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of a summary")
    args = ap.parse_args(argv)

    max_lines, exts, rules = args.max_lines, (".py",), []
    if args.config:
        cfg = json.loads(args.config.read_text())
        max_lines = cfg.get("max_lines", max_lines)
        exts = tuple(cfg.get("exts", exts))
        rules = cfg.get("rules", [])

    report = scan(args.root, max_lines=max_lines, rules=rules, exts=exts)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        _print_human(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
