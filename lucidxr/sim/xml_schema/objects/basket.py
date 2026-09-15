from lucidxr.sim.xml_schema.schema import Body, Xml


class Basket(Body):
    ## relative path from `lucidxr/docs/robots/` where the `ur5e_table_scene.py` is located
    # assets: str = join("../..", asset_rel_path, 'table_white_modern')
    assets: str = "objects/basket"
    end_effector: Xml

    def __init__(self, name: str = "basket", **kwargs):
        super().__init__(name=name, **kwargs)

    _attributes = {
        "name": "basket",
        "childclass": "basket",
        "pos": "0 0 0",
        "quat": "0 0 0.707 0.707",
    }

    _preamble = """
    <default>
      <default class="{childclass}">
        <default class="{childclass}-visual">
          <geom type="mesh" contype="0" conaffinity="0" group="2"/>
        </default>
        <default class="{childclass}-collision">
          <geom type="box" group="3" contype="1" conaffinity="1"/>
        </default>
      </default>
    </default>

    <asset>
      <mesh file="{assets}/basket_0.obj" scale="0.4 0.1 0.4"/>
    </asset>
    """

    template = """
    <body {attributes}>
      <inertial mass="4.0" pos="0 0 0" diaginertia="0.00443333156 0.00443333156 0.0072"/>
      <body name="{name}-base">
        <inertial mass="3.7" pos="0 0 0" diaginertia="0.0102675 0.0102675 0.00666"/>
        <geom mesh="basket_0" class="{childclass}-visual"/>
        <!--geom class="{childclass}-collision" mesh="basket_0"/-->
        <geom class="basket-collision" type="box" size="0.216 0.05 0.02" rgba="0 1 0 0.4" pos="0 0 -0.24" quat="1 0 0 0"/>
        <geom class="basket-collision" type="box" size="0.216 0.05 0.02" rgba="0 1 0 0.4" pos="0 0 0.24" quat="1 0 0 0"/>
        <geom class="basket-collision" type="box" size="0.02 0.05 0.24" rgba="0 1 0 0.4" pos="-0.24 0 0" quat="1 0 0 0"/>
        <geom class="basket-collision" type="box" size="0.02 0.05 0.24" rgba="0 1 0 0.4" pos="0.24 0 0" quat="1 0 0 0"/>
      </body>
    </body>
    """
