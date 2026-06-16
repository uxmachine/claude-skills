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
