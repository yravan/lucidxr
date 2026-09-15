"""Small regression checks for composition and portable task generation."""

import mujoco
from lxml import etree

from lucidxr.sim.scenes import build_xml
from lucidxr.sim.xml_schema import Body, Mjcf, Raw, Xml, XmlTemplate


def test_xml_composition_and_inherited_parameters():
    class Parent(XmlTemplate):
        scale = 2
        template = '<node scale="{scale}">{children}</node>'

    class Child(Parent):
        pass

    root = etree.fromstring(str(Child(children=[Raw("<leaf/>"), Xml(tag="label", value='a&"b')])))
    assert root.attrib["scale"] == "2"
    assert root.find("label").get("value") == 'a&"b'


def test_body_instances_do_not_share_names_or_children():
    class Block(Body):
        _attributes = {"name": "block"}

    first = Block(name="first", pos=[1, 2, 3])
    second = Block(name="second")
    root = etree.fromstring(str(Mjcf(first, second)))
    assert [node.get("name") for node in root.findall("worldbody/body")] == ["first", "second"]
    assert "pos" not in second._attributes
    assert Block._attributes == {"name": "block"}


def test_seeded_scene_loads_outside_checkout(tmp_path, monkeypatch):
    xml = build_xml("stack_blocks", seed=7)
    assert xml == build_xml("stack_blocks", seed=7)
    assert xml != build_xml("stack_blocks", seed=8)
    path = tmp_path / "scene.xml"
    path.write_text(xml)
    monkeypatch.chdir(tmp_path)
    model = mujoco.MjModel.from_xml_path(str(path))
    data = mujoco.MjData(model)
    mujoco.mj_step(model, data)
    assert data.time > 0


def test_quaternion_composition_and_half_turn_conversion():
    import numpy as np
    from scipy.spatial.transform import Rotation

    from lucidxr.sim.xml_schema.transforms.mujoco import WXYZ, quat2xmat, xmat2quat

    first = WXYZ(0.5, 0.5, 0.5, 0.5)
    second = WXYZ(0, 1, 0, 0)
    assert np.allclose(first + WXYZ(1, 0, 0, 0), first)
    assert np.allclose(first + ~first, (1, 0, 0, 0))
    expected = Rotation.from_quat([*first[1:], first[0]]) * Rotation.from_quat([*second[1:], second[0]])
    assert np.allclose(np.asarray(quat2xmat(first + second)).reshape(3, 3), expected.as_matrix())
    assert np.allclose(quat2xmat(xmat2quat(quat2xmat(second))), quat2xmat(second))
