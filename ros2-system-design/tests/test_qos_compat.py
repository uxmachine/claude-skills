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
