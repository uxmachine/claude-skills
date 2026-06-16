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
