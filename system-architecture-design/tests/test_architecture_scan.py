"""Tests for architecture_scan.py — written test-first (the skill preaches fitness functions,
so the tool ships with one). Runs under pytest OR as a plain script: `python3 test_architecture_scan.py`.
No third-party deps."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import architecture_scan as a  # noqa: E402


def _make_tree(root: Path) -> None:
    # god file (60 lines) vs small file (3 lines)
    (root / "pkg").mkdir(parents=True)
    (root / "pkg" / "big.py").write_text("x = 1\n" * 60)
    (root / "pkg" / "small.py").write_text("y = 1\n" * 3)

    # import-boundary: core/ must not import a vendor SDK
    (root / "core").mkdir()
    (root / "core" / "clean.py").write_text("import os\nfrom pkg import small\n")
    (root / "core" / "dirty.py").write_text("import os\nfrom vendor_sdk.client import Thing\n")

    # duplicate content at two paths + one unique
    dup = "def f():\n    return 42\n"
    (root / "a").mkdir()
    (root / "b").mkdir()
    (root / "a" / "dup.py").write_text(dup)
    (root / "b" / "dup_copy.py").write_text(dup)
    (root / "a" / "unique.py").write_text("def g():\n    return 7\n")


def test_god_files(tmp_path):
    _make_tree(tmp_path)
    hits = a.find_god_files(tmp_path, max_lines=40)
    names = {p.name for p, _ in hits}
    assert "big.py" in names
    assert "small.py" not in names


def test_import_boundary(tmp_path):
    _make_tree(tmp_path)
    rules = [{"package": "core", "forbid": ["vendor_sdk"]}]
    violations = a.find_import_boundary_violations(tmp_path, rules)
    files = {Path(v["file"]).name for v in violations}
    assert "dirty.py" in files
    assert "clean.py" not in files


def test_duplicate_files(tmp_path):
    _make_tree(tmp_path)
    groups = a.find_duplicate_files(tmp_path)
    # exactly one group of duplicates (dup.py + dup_copy.py); unique.py not grouped
    dup_groups = [g for g in groups if len(g) >= 2]
    assert len(dup_groups) == 1
    paths = {Path(p).name for p in dup_groups[0]}
    assert paths == {"dup.py", "dup_copy.py"}


def test_scan_report_shape(tmp_path):
    _make_tree(tmp_path)
    report = a.scan(tmp_path, max_lines=40, rules=[{"package": "core", "forbid": ["vendor_sdk"]}])
    assert set(report) >= {"god_files", "import_boundary_violations", "duplicate_files"}
    assert report["god_files"] and report["import_boundary_violations"] and report["duplicate_files"]


def _run_all():
    import tempfile
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            with tempfile.TemporaryDirectory() as d:
                try:
                    fn(Path(d))
                    print(f"PASS {name}")
                except AssertionError as e:
                    failures += 1
                    print(f"FAIL {name}: {e}")
                except Exception as e:  # noqa: BLE001
                    failures += 1
                    print(f"ERROR {name}: {type(e).__name__}: {e}")
    print(f"\n{'OK' if failures == 0 else f'{failures} FAILED'}")
    return failures


if __name__ == "__main__":
    sys.exit(1 if _run_all() else 0)
