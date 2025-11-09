from vuer_mujoco.schemas.schema import Body


class MuJoCoMug(Body):
    assets = "mujoco-mug"

    _attributes = {
        "name": "mujoco-mug",
        "childclass": "m-mug",
    }
    _preamble = """
    <asset>
      <texture name="{childclass}-tex" file="{assets}/mug.png" type="2d" width="1024" height="1024"/>
      <material name="{childclass}-mat" texture="{childclass}-tex" specular="1" shininess="1"/>
      <mesh name="{childclass}-mesh" file="{assets}/mug.obj" scale=".01 .01 .01"/>
    </asset>
    
    <default>
      <default class="{childclass}">
        <geom type="box" group="3"/>
        <default class="{childclass}-cup">
          <geom size="0.0026 0.00704 0.033"/>
        </default>
        <default class="{childclass}-handle">
          <geom size="0.0025 0.00328 0.0055"/>
        </default>
      </default>
    </default>
    """

    _children_raw = """
    <freejoint name="{name}-joint"/>
    <geom name="{name}-visual" type="mesh" mesh="{childclass}-mesh" material="{childclass}-mat" euler="1.5708 0 0" group="1" contype="0" conaffinity="0"/>
    <geom name="{name}-cup" mass="0.1" class="{childclass}-cup" type="cylinder" size="0.045 0.0026" pos="0 0 0.0026" condim="4" solimp="0.95 0.99 0.001" solref="0.003 1"/>
    
    <body name="{name}-handle" pos="0.056 0 0.0395" euler="1.5708 0 0">
      <geom name="{name}-handle-0" class="{childclass}-handle" pos="0.0193 0 0" euler="0 0 0"/>
      <geom name="{name}-handle-1" class="{childclass}-handle" pos="0.0159 0.0108 0" euler="0 0 0.5981"/>
    </body>
    """
