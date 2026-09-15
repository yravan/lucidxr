from lucidxr.sim.xml_schema.base import chain
from lucidxr.sim.xml_schema.schema import Body


class PandaLink7(Body):
    """Link 7 of the Panda robot."""

    _attributes = {
        "name": "link7",
        "childclass": "panda",
        "pos": "0.088 0 0",
        "quat": "0.707107 0.707107 0 0",
    }

    _preamble = """
    <asset>
    <mesh name="link7_c" file="{assets}/link7.stl"/>
    <mesh file="{assets}/link7_0.obj"/>
    <mesh file="{assets}/link7_1.obj"/>
    <mesh file="{assets}/link7_2.obj"/>
    <mesh file="{assets}/link7_3.obj"/>
    <mesh file="{assets}/link7_4.obj"/>
    <mesh file="{assets}/link7_5.obj"/>
    <mesh file="{assets}/link7_6.obj"/>
    <mesh file="{assets}/link7_7.obj"/>
    </asset>
    """

    _children_raw = """
    <inertial mass="7.35522e-01" pos="1.0517e-2 -4.252e-3 6.1597e-2"
      fullinertia="1.2516e-2 1.0027e-2 4.815e-3 -4.28e-4 -1.196e-3 -7.41e-4"/>
    <joint name="{name}-joint"/>
    <geom mesh="link7_0" material="{childclass}-white" class="{childclass}-visual"/>
    <geom mesh="link7_1" material="{childclass}-black" class="{childclass}-visual"/>
    <geom mesh="link7_2" material="{childclass}-black" class="{childclass}-visual"/>
    <geom mesh="link7_3" material="{childclass}-black" class="{childclass}-visual"/>
    <geom mesh="link7_4" material="{childclass}-black" class="{childclass}-visual"/>
    <geom mesh="link7_5" material="{childclass}-black" class="{childclass}-visual"/>
    <geom mesh="link7_6" material="{childclass}-black" class="{childclass}-visual"/>
    <geom mesh="link7_7" material="{childclass}-white" class="{childclass}-visual"/>
    <geom mesh="link7_c" class="{childclass}-collision"/>
    """

    _postamble = """
    <actuator>
    <general class="{childclass}" name="{name}-actuator" joint="{name}-joint" gainprm="2000" biasprm="0 -2000 -200" forcerange="-12 12"/>
    </actuator>
    """



class PandaLink6(Body):
    """Link 6 of the Panda robot."""

    name: str

    _attributes = {
        "name": "link6",
        "childclass": "panda",
        "pos": "0 0 0",
        "quat": "0.707107 0.707107 0 0",
    }

    _preamble = """
    <asset>
    <mesh name="link6_c" file="{assets}/link6.stl"/>
    <mesh file="{assets}/link6_0.obj"/>
    <mesh file="{assets}/link6_1.obj"/>
    <mesh file="{assets}/link6_2.obj"/>
    <mesh file="{assets}/link6_3.obj"/>
    <mesh file="{assets}/link6_4.obj"/>
    <mesh file="{assets}/link6_5.obj"/>
    <mesh file="{assets}/link6_6.obj"/>
    <mesh file="{assets}/link6_7.obj"/>
    <mesh file="{assets}/link6_8.obj"/>
    <mesh file="{assets}/link6_9.obj"/>
    <mesh file="{assets}/link6_10.obj"/>
    <mesh file="{assets}/link6_11.obj"/>
    <mesh file="{assets}/link6_12.obj"/>
    <mesh file="{assets}/link6_13.obj"/>
    <mesh file="{assets}/link6_14.obj"/>
    <mesh file="{assets}/link6_15.obj"/>
    <mesh file="{assets}/link6_16.obj"/>
    </asset>
    """

    _children_raw = """
    <inertial mass="1.666555" pos="6.0149e-2 -1.4117e-2 -1.0517e-2" fullinertia="1.964e-3 4.354e-3 5.433e-3 1.09e-4 -1.158e-3 3.41e-4"/>
    <joint name="{name}-joint" range="-0.0175 3.7525"/>
    <geom mesh="link6_0" material="{childclass}-off_white" class="{childclass}-visual"/>
    <geom mesh="link6_1" material="{childclass}-white" class="{childclass}-visual"/>
    <geom mesh="link6_2" material="{childclass}-black" class="{childclass}-visual"/>
    <geom mesh="link6_3" material="{childclass}-white" class="{childclass}-visual"/>
    <geom mesh="link6_4" material="{childclass}-white" class="{childclass}-visual"/>
    <geom mesh="link6_5" material="{childclass}-white" class="{childclass}-visual"/>
    <geom mesh="link6_6" material="{childclass}-white" class="{childclass}-visual"/>
    <geom mesh="link6_7" material="{childclass}-light_blue" class="{childclass}-visual"/>
    <geom mesh="link6_8" material="{childclass}-light_blue" class="{childclass}-visual"/>
    <geom mesh="link6_9" material="{childclass}-black" class="{childclass}-visual"/>
    <geom mesh="link6_10" material="{childclass}-black" class="{childclass}-visual"/>
    <geom mesh="link6_11" material="{childclass}-white" class="{childclass}-visual"/>
    <geom mesh="link6_12" material="{childclass}-green" class="{childclass}-visual"/>
    <geom mesh="link6_13" material="{childclass}-white" class="{childclass}-visual"/>
    <geom mesh="link6_14" material="{childclass}-black" class="{childclass}-visual"/>
    <geom mesh="link6_15" material="{childclass}-black" class="{childclass}-visual"/>
    <geom mesh="link6_16" material="{childclass}-white" class="{childclass}-visual"/>
    <geom mesh="link6_c" class="{childclass}-collision"/>
    """

    _postamble = """
    <actuator>
    <general class="{childclass}" name="{name}-actuator" joint="{name}-joint" gainprm="2000" biasprm="0 -2000 -200" forcerange="-12 12"
      ctrlrange="-0.0175 3.7525"/>
    </actuator>
    """


class PandaLink5(Body):
    """Link 5 of the Panda robot."""

    assets: str

    _attributes = {
        "name": "link5",
        "childclass": "panda",
        "pos": "-0.0825 0.384 0",
        "quat": "0.707107 -0.707107 0 0",
    }

    _preamble = """
    <asset>
    <mesh name="link5_c0" file="{assets}/link5_collision_0.obj"/>
    <mesh name="link5_c1" file="{assets}/link5_collision_1.obj"/>
    <mesh name="link5_c2" file="{assets}/link5_collision_2.obj"/>
    <mesh file="{assets}/link5_0.obj"/>
    <mesh file="{assets}/link5_1.obj"/>
    <mesh file="{assets}/link5_2.obj"/>
    </asset>
    """

    _children_raw = """
    <inertial mass="1.225946" pos="-1.1953e-2 4.1065e-2 -3.8437e-2" fullinertia="3.5549e-2 2.9474e-2 8.627e-3 -2.117e-3 -4.037e-3 2.29e-4"/>
    <joint name="{name}-joint"/>
    <geom mesh="link5_0" material="{childclass}-black" class="{childclass}-visual"/>
    <geom mesh="link5_1" material="{childclass}-white" class="{childclass}-visual"/>
    <geom mesh="link5_2" material="{childclass}-white" class="{childclass}-visual"/>
    <geom mesh="link5_c0" class="{childclass}-collision"/>
    <geom mesh="link5_c1" class="{childclass}-collision"/>
    <geom mesh="link5_c2" class="{childclass}-collision"/>
    """

    _postamble = """
    <actuator>
    <general class="{childclass}" name="{name}-actuator" joint="{name}-joint" gainprm="2000" biasprm="0 -2000 -200" forcerange="-12 12"/>
    </actuator>
    """



class PandaLink4(Body):
    """Link 4 of the Panda robot."""

    assets: str

    _attributes = {
        "name": "link4",
        "childclass": "panda",
        "pos": "0.0825 0 0",
        "quat": "0.707107 0.707107 0 0",
    }

    _preamble = """
    <asset>
    <mesh name="link4_c" file="{assets}/link4.stl"/>
    <mesh file="{assets}/link4_0.obj"/>
    <mesh file="{assets}/link4_1.obj"/>
    <mesh file="{assets}/link4_2.obj"/>
    <mesh file="{assets}/link4_3.obj"/>
    </asset>
    """

    _children_raw = """
    <inertial mass="3.587895" pos="-5.317e-2 1.04419e-1 2.7454e-2"
      fullinertia="2.5853e-2 1.9552e-2 2.8323e-2 7.796e-3 -1.332e-3 8.641e-3"/>
    <joint name="{name}-joint" range="-3.0718 -0.0698"/>
    <geom mesh="link4_0" material="{childclass}-white" class="{childclass}-visual"/>
    <geom mesh="link4_1" material="{childclass}-white" class="{childclass}-visual"/>
    <geom mesh="link4_2" material="{childclass}-black" class="{childclass}-visual"/>
    <geom mesh="link4_3" material="{childclass}-white" class="{childclass}-visual"/>
    <geom mesh="link4_c" class="{childclass}-collision"/>
    """

    _postamble = """
    <actuator>
    <general class="{childclass}" name="{name}-actuator" joint="{name}-joint" gainprm="3500" biasprm="0 -3500 -350"
      ctrlrange="-3.0718 -0.0698"/>
    </actuator>
    """



class PandaLink3(Body):
    """Link 3 of the Panda robot."""

    assets: str

    _attributes = {
        "name": "link3",
        "childclass": "panda",
        "pos": "0 -0.316 0",
        "quat": "0.707107 0.707107 0 0",
    }

    _preamble = """
    <asset>
    <mesh name="link3_c" file="{assets}/link3.stl"/>
    <mesh file="{assets}/link3_0.obj"/>
    <mesh file="{assets}/link3_1.obj"/>
    <mesh file="{assets}/link3_2.obj"/>
    <mesh file="{assets}/link3_3.obj"/>
    </asset>
    """

    _children_raw = """
    <joint name="{name}-joint"/>
    <inertial mass="3.228604" pos="2.7518e-2 3.9252e-2 -6.6502e-2" fullinertia="3.7242e-2 3.6155e-2 1.083e-2 -4.761e-3 -1.1396e-2 -1.2805e-2"/>
    <geom mesh="link3_0" material="{childclass}-white" class="{childclass}-visual"/>
    <geom mesh="link3_1" material="{childclass}-white" class="{childclass}-visual"/>
    <geom mesh="link3_2" material="{childclass}-white" class="{childclass}-visual"/>
    <geom mesh="link3_3" material="{childclass}-black" class="{childclass}-visual"/>
    <geom mesh="link3_c" class="{childclass}-collision"/>
    """

    _postamble = """
    <actuator>
    <general class="{childclass}" name="{name}-actuator" joint="{name}-joint" gainprm="3500" biasprm="0 -3500 -350"/>
    </actuator>
    """



class PandaLink2(Body):
    """Link 2 of the Panda robot."""

    assets: str

    _attributes = {"name": "link2", "childclass": "panda", "pos": "0 0 0", "quat": "0.707107 -0.707107 0 0"}

    _preamble = """
    <asset>
    <mesh name="link2_c" file="{assets}/link2.stl"/>
    <mesh file="{assets}/link2.obj"/>
    </asset>
    """

    _children_raw = """
    <inertial mass="0.646926" pos="-0.003141 -0.02872 0.003495"
    fullinertia="0.0079620 2.8110e-2 2.5995e-2 -3.925e-3 1.0254e-2 7.04e-4"/>
    <joint name="{name}-joint" range="-1.7628 1.7628"/>
    <geom material="{childclass}-white" mesh="link2" class="{childclass}-visual"/>
    <geom mesh="link2_c" class="{childclass}-collision"/>
    """

    _postamble = """
    <actuator>
    <general class="{childclass}" name="{name}-actuator" joint="{name}-joint" gainprm="4500" biasprm="0 -4500 -450" ctrlrange="-1.7628 1.7628"/>
    </actuator>
    """



class PandaLink1(Body):
    """Link 1 of the Panda robot."""

    assets: str

    _attributes = {"name": "link1", "childclass": "panda", "pos": "0 0 0.333"}

    _preamble = """
    <asset>
    <mesh name="link1_c" file="{assets}/link1.stl"/>
    <mesh file="{assets}/link1.obj"/>
    </asset>
    """

    _children_raw = """
    <inertial mass="4.970684" pos="0.003875 0.002081 -0.04762" fullinertia="0.70337 0.70661 0.0091170 -0.00013900 0.0067720 0.019169"/>
    <joint name="{name}-joint"/>
    <geom material="{childclass}-white" mesh="link1" class="{childclass}-visual"/>
    <geom mesh="link1_c" class="{childclass}-collision"/>
    """

    _postamble = """
    <actuator>
        <general class="{childclass}" name="{name}-actuator" joint="{name}-joint" gainprm="4500" biasprm="0 -4500 -450"/>
    </actuator>
    """



class PandaLink0(Body):
    """Link 0 of the Panda robot."""

    assets: str

    _attributes = {
        "name": "link0",
        "childclass": "panda",
        "pos": "0 0 0",
    }

    _preamble = """
    <asset>
    <material class="{childclass}" name="{childclass}-white" rgba="1 1 1 1"/>
    <material class="{childclass}" name="{childclass}-off_white" rgba="0.901961 0.921569 0.929412 1"/>
    <material class="{childclass}" name="{childclass}-black" rgba="0.25 0.25 0.25 1"/>
    <material class="{childclass}" name="{childclass}-green" rgba="0 1 0 1"/>
    <material class="{childclass}" name="{childclass}-light_blue" rgba="0.039216 0.541176 0.780392 1"/>
    
    <!-- collision mesh -->
    <mesh name="link0_c" file="{assets}/link0.stl"/>
    
    <!-- visual mesh -->
    <mesh file="{assets}/link0_0.obj"/>
    <mesh file="{assets}/link0_1.obj"/>
    <mesh file="{assets}/link0_2.obj"/>
    <mesh file="{assets}/link0_3.obj"/>
    <mesh file="{assets}/link0_4.obj"/>
    <mesh file="{assets}/link0_5.obj"/>
    <mesh file="{assets}/link0_7.obj"/>
    <mesh file="{assets}/link0_8.obj"/>
    <mesh file="{assets}/link0_9.obj"/>
    <mesh file="{assets}/link0_10.obj"/>
    <mesh file="{assets}/link0_11.obj"/>
    </asset>
    """

    _children_raw = """
    <inertial mass="0.629769" pos="-0.041018 -0.00014 0.049974"
    fullinertia="0.00315 0.00388 0.004285 8.2904e-7 0.00015 8.2299e-6"/>
    <geom mesh="link0_0" material="{childclass}-off_white" class="{childclass}-visual"/>
    <geom mesh="link0_1" material="{childclass}-black" class="{childclass}-visual"/>
    <geom mesh="link0_2" material="{childclass}-off_white" class="{childclass}-visual"/>
    <geom mesh="link0_3" material="{childclass}-black" class="{childclass}-visual"/>
    <geom mesh="link0_4" material="{childclass}-off_white" class="{childclass}-visual"/>
    <geom mesh="link0_5" material="{childclass}-black" class="{childclass}-visual"/>
    <geom mesh="link0_7" material="{childclass}-white" class="{childclass}-visual"/>
    <geom mesh="link0_8" material="{childclass}-white" class="{childclass}-visual"/>
    <geom mesh="link0_9" material="{childclass}-black" class="{childclass}-visual"/>
    <geom mesh="link0_10" material="{childclass}-off_white" class="{childclass}-visual"/>
    <geom mesh="link0_11" material="{childclass}-white" class="{childclass}-visual"/>
    <geom mesh="link0_c" class="{childclass}-collision"/>
    """



class Panda(Body):
    """
    This is the Panda robot.

    By default, it will use 7 links defined here.

    efChildren is optional and can be used to add end effector to the robot.
    name is optional, if provided it will be used as the name of the robot and should be unique.
    If not provided, "panada<robot_id> will be used instead, where robot_id is unique.
    """

    key = 0

    assets: str = "robots/franka_panda"

    _attributes = {
        "name": "panda",
        "childclass": "panda",
    }

    def __init__(self, *_children, end_effector: Body = None, **rest):
        # Ge: we do the super call here to reduce boilerplate code.
        super().__init__(*_children, **rest)
        from lucidxr.sim.xml_schema.transforms.mujoco import WXYZ

        self._quat = WXYZ(1, 0, 0, 0)

        name = self._attributes["name"]
        childclass = self._attributes["childclass"]

        link = chain(
            PandaLink0(assets=self.assets, attributes=dict(name=name + "_link0", childclass=childclass)),
            PandaLink1(assets=self.assets, attributes=dict(name=name + "_link1", childclass=childclass)),
            PandaLink2(assets=self.assets, attributes=dict(name=name + "_link2", childclass=childclass)),
            PandaLink3(assets=self.assets, attributes=dict(name=name + "_link3", childclass=childclass)),
            PandaLink4(assets=self.assets, attributes=dict(name=name + "_link4", childclass=childclass)),
            PandaLink5(assets=self.assets, attributes=dict(name=name + "_link5", childclass=childclass)),
            PandaLink6(assets=self.assets, attributes=dict(name=name + "_link6", childclass=childclass)),
            PandaLink7(
                assets=self.assets,
                attributes=dict(
                    name=name + "_link7",
                    childclass=childclass,
                ),
                children=end_effector,
            ),
        )
        self._children = (link, *(self._children or []))

    _preamble = """
    <compiler angle="radian" autolimits="true"/>
    
    <default>
        <default class="{childclass}">
          <material specular="0.5" shininess="0.25"/>
          <joint armature="0.1" damping="1" axis="0 0 1" range="-2.8973 2.8973"/>
          <general dyntype="none" biastype="affine" ctrlrange="-2.8973 2.8973" forcerange="-87 87"/>

          <default class="{childclass}-visual">
            <geom type="mesh" contype="0" conaffinity="0" group="2"/>
          </default>
          <default class="{childclass}-collision">
            <geom type="mesh" group="3"/>
          </default>
        </default>
    </default>
    """

    template = """
    <!-- robot view -->
    <camera mode="fixed" name="{name}_robotview" pos="1.0 0 0.4" quat="0.653 0.271 0.271 0.653"/>
    <body {attributes}>
        {children}
    </body>
    """
