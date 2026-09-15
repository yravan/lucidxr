from lucidxr.sim.xml_schema.schema import Body


class PlanarPusher(Body):
    name = "cylinder"
    _attributes = {
        "name": name,
    }

    _mocaps_raw = """
    <body mocap="true" name="{name}-mocap" pos="{mocap_pos}" quat="0 0 1 0">
      <site name="{name}-mocap-site" size="0.002" type="sphere" rgba="0.13 0.3 0.2 1"/>
    </body>
    """

    _preamble = """
    <asset>
    <material name="{name}-mat" rgba="0 0 1 1" shininess="0.1"/>
    </asset>
    """

    _children_raw = """
                    <geom name="{name}-geom" material="{name}-mat" type="cylinder" group="2" contype="1" conaffinity="1" size="0.02 0.05"
                    pos="0 0 0" friction="5.0 0.005 0.0001" solref="0.005 0.01" solimp="0.95 0.99 0.001"/>
                    <inertial pos="0 0 0.025" mass="0.5" diaginertia="0.001 0.001 0.001"/>
                    <joint name="{name}-cylinder_x" type="slide" axis="1 0 0"/>
                    <joint name="{name}-cylinder_y" type="slide" axis="0 1 0"/>
                   
                    <site name="{name}-site" pos="0 0 0.05" type="sphere" size="0.002"/>
                   
                """

    _postamble = """
        <equality>
      
      <weld site1="{name}-mocap-site" site2="{name}-site"/>
    </equality>
    """

    def __init__(self, *_children, mocap_pos=None, **kwargs):
        super().__init__(*_children, **kwargs)
        if mocap_pos is None:
            self.mocap_pos = self._pos + [0, 0, 0.01]
        else:
            self.mocap_pos = mocap_pos

        values = self._format_dict()
        self._mocaps = self._mocaps_raw.format(**values)
