from vuer_mujoco.schemas import Xml, XmlTemplate, Mjcf, Body
from vuer_mujoco.schemas.utils import minimize_many


def test_root_element():
    xml = Xml(tag="mujoco", name="base")
    assert xml.tag == "mujoco"
    assert xml._attributes == {"name": "base"}
    assert xml._children is None

    assert xml.attributes == 'name="base"'
    assert xml._minimized == '<mujoco name="base"/>'


def test_attribute_string():
    xml = Xml(
        name="base",
        position="0 0 0",
        orientation="0 0 0 1",
    )
    assert xml._minimized == '<xml name="base" position="0 0 0" orientation="0 0 0 1"/>'


def test_xml_template():
    link = Body(
        attributes=dict(
            name="LR_hip_roll",
            pos="0 0 0",
            climit="0 0",
            damping="0",
        ),
    )
    xml = Mjcf(
        attributes={"name": "base"},
        children=(link,),
    )

    assert (
        xml._minimized == '<mujoco name="base"><worldbody><body name="LR_hip_roll" '
        'pos="0 0 0" climit="0 0" damping="0"/></worldbody></mujoco>'
    )


def test_xml_preamble():
    robot = XmlTemplate(
        preamble='<asset><inertial mass="0.1"/></asset>',
    )
    assert robot.preamble == '<asset><inertial mass="0.1"/></asset>'


def test_nested_preamble():
    part_1 = XmlTemplate(
        preamble='<asset><material name="mat1" mass="10"/></asset>',
    )
    robot = XmlTemplate(
        part_1,
        preamble='<asset><material name="mat2" mass="0.1"/></asset>',
    )
    assert (
        robot.preamble | minimize_many
        == """
        <asset><material name="mat2" mass="0.1"/></asset>
        <asset><material name="mat1" mass="10"/></asset>
        """
        | minimize_many
    )
