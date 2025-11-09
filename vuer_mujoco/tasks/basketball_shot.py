import warnings
from pathlib import Path

import numpy as np

from vuer_mujoco.schemas.objects.decomposed_obj import ObjMujocoObject
from vuer_mujoco.tasks.base.lucidxr_task import get_site
from vuer_mujoco.tasks.base.mocap_task import MocapTask
from vuer_mujoco.schemas.components.rigs.camera_rig import make_camera_rig
from vuer_mujoco.schemas.components.concrete_slab import ConcreteSlab
# from vuer_mujoco.schemas.components.rigs.camera_rig import make_camera_rig
from vuer_mujoco.schemas.components.rigs.camera_rig_zoomed_out import make_camera_rig
from vuer_mujoco.schemas.components.concrete_slab import ConcreteSlab
from vuer_mujoco.tasks._floating_shadowhand import FloatingShadowHand
from vuer_mujoco.schemas.components.rigs.lighting_rig import make_lighting_rig
from vuer_mujoco.schemas.objects.orbit_table import OpticalTable


def make_schema(**_):
    from vuer_mujoco.schemas.utils.file import Prettify

    optical_table = OpticalTable(
        pos=[-0.2, 0, 0.79],
        assets="model",
        _attributes={"name": "table_optical"},
    )
    # camera_rig = make_camera_rig(optical_table._pos)

    table_slab = ConcreteSlab(
        assets="model",
        pos=[0, 0, 0.777],
        group=4,
        rgba="0.8 0 0 0.9",
        _attributes={
            "name": "table",
        },
    )
    lighting = make_lighting_rig(optical_table._pos)
    camera_rig = make_camera_rig(table_slab.surface_origin)

    basketball_hoop = ObjMujocoObject(
        name="basketball_hoop",
        assets="basketball_hoop",
        prefix="hoop",
        visual_count=1,
        pos=[-0.7, 0, 0.85],
        quat=[0.7071068, 0.7071068, 0, 0],
        scale=0.5,
        collision_count=12,
        textures=["DefaultMaterial_baseColor"],
        free=False,
        randomize_colors=True,
        _additional_children_raw = """
        <site name="{prefix}_corner1" pos="0.425 0.45 -0.09" size="0.01" rgba="1 1 0 0"/>
        <site name="{prefix}_corner2" pos="0.605 0.45 -0.09" size="0.01" rgba="1 1 0 0"/>
        <site name="{prefix}_corner3" pos="0.605 0.45  0.09" size="0.01" rgba="1 1 0 0"/>
        <site name="{prefix}_corner4" pos="0.425 0.45  0.09" size="0.01" rgba="1 1 0 0"/>
        """
    )
    basketball = ObjMujocoObject(
        name="basketball",
        assets="basketball",
        visual_count=1,
        pos=[0, 0, 0.85],
        scale=0.0215,
        collision_count=1,
        textures=["Basketball_size6_baseColor"],
        randomize_colors=True,
        _additional_children_raw = """
        <site name="{name}" pos="0 0.07 0" size="0.0215" rgba="1 1 0 0"/>
        """
    )

    scene = FloatingShadowHand(
        optical_table,
        table_slab,
        *camera_rig.get_cameras(),
        basketball_hoop,
        basketball,
        pos=[0, 0, 0.8],
    )

    return scene._xml | Prettify()

class Shoot(MocapTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.basketball = get_site(self.physics, "basketball")
        # Using list comprehension to get the 4 hoop corner sites
        self.hoop_corners = [
            get_site(self.physics, f"hoop_corner{i+1}") for i in range(4)
        ]

    def get_reward(self, physics):
        reward = 0.0
        basketball_pos = physics.data.site_xpos[self.basketball.id]

        # Extract x, y positions of the corners to form a bounding box in the xy-plane
        hoop_x_min = min(physics.data.site_xpos[corner.id][0] for corner in self.hoop_corners)
        hoop_x_max = max(physics.data.site_xpos[corner.id][0] for corner in self.hoop_corners)
        hoop_y_min = min(physics.data.site_xpos[corner.id][1] for corner in self.hoop_corners)
        hoop_y_max = max(physics.data.site_xpos[corner.id][1] for corner in self.hoop_corners)

        # Extract z positions of the corners to check the tolerance
        hoop_z_min = min(physics.data.site_xpos[corner.id][2] for corner in self.hoop_corners)

        # Check if the basketball is within the bounding box in the xy-plane and within z tolerance of 1 cm
        if (
            hoop_x_min <= basketball_pos[0] <= hoop_x_max and
            hoop_y_min <= basketball_pos[1] <= hoop_y_max and
            abs(basketball_pos[2] - hoop_z_min) <= 0.01
        ):
            reward = 1.0  # Ball is inside the bounding box and within z tolerance
        warnings.warn("Reward is untested for this env, bc we had no working policy")

        return reward

def register():
    from vuer_mujoco.tasks import add_env
    from vuer_mujoco.tasks.entrypoint import make_env

    add_env(
        env_id="BasketballShot-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=Shoot,
            camera_names=["right", "right_r", "wrist", "front"],
            xml_path="basketball_shot.mjcf.xml",
            workdir=Path(__file__).parent,
        ),
    )


if __name__ == "__main__":
    from vuer_mujoco.schemas.utils.file import Save

    make_schema() | Save(__file__.replace(".py", ".mjcf.xml"))
