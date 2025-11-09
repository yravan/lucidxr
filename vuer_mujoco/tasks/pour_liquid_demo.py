from pathlib import Path

import numpy as np

from vuer_mujoco.schemas.components.rigs.camera_rig_stereo import make_origin_stereo_rig
from vuer_mujoco.schemas.objects.bowl_0 import ObjaverseMujocoBowl
from vuer_mujoco.schemas.objects.cup_3 import ObjaverseMujocoCup
from vuer_mujoco.schemas.objects.mug import ObjaverseMujocoMug
from vuer_mujoco.schemas.objects.plate import ObjaverseMujoco
from vuer_mujoco.schemas.objects.spoon_7 import ObjaverseMujocoSpoon
from vuer_mujoco.schemas.room_xmls.room_components.dishwasher import KitchenDishwasher
from vuer_mujoco.schemas.room_xmls.room_components.drawer_stack import DrawerStack
from vuer_mujoco.schemas.room_xmls.room_components.granite_countertop import GraniteCountertop
from vuer_mujoco.schemas.room_xmls.room_components.refrigerator import KitchenFridge
from vuer_mujoco.schemas.room_xmls.room_components.room_wall import RoomWall
from vuer_mujoco.schemas.room_xmls.room_components.sink_wide import KitchenSinkWide
from vuer_mujoco.schemas.schema import Body, Replicate
from vuer_mujoco.tasks import add_env
from vuer_mujoco.tasks.base.lucidxr_task import get_site, init_states, get_body_id, get_geom_id, get_all_geom_ids, \
    get_all_body_ids
from vuer_mujoco.tasks.base.mocap_task import MocapTask
from vuer_mujoco.schemas.components.rigs.camera_rig import make_camera_rig
from vuer_mujoco.tasks._floating_shadowhand import FloatingShadowHand
from vuer_mujoco.tasks.entrypoint import make_env
import vuer_mujoco.schemas.se3.se3_mujoco as m

x1, y1 = 0.2, -1
origin = m.Vector3(0, -1.0, 0)
nx, ny, nz = 2, 2, 6

def make_schema(**kwargs):
    from vuer_mujoco.schemas.utils.file import Prettify

    quat = m.WXYZ(0.7071068, 0, 0, -0.7071068)

    front_wall = RoomWall(
        panel_sz=(1.8, 0.5425, 0.02),
        pos=(0.65, 0.02, 0.5425),
        quat=(-0.707107, 0.707107, 0, 0),
        name="wall_room",
        assets="kitchen/wall",
        backing=False,
    )
    stack_B = DrawerStack(base_pos="0.51 -0.3 0.00", name="stack_B", assets="kitchen", visual=True)
    stack_C = DrawerStack(base_pos="1.02 -0.3 0.00", name="stack_C", assets="kitchen", visual=True)

    table_A = GraniteCountertop(
        assets="kitchen/counter", size="0.35 0.325 0.015", attributes={"pos": "0.075 -0.325 0.905", "name": "table_A"}
    )
    table_B = GraniteCountertop(
        assets="kitchen/counter", size="0.36 0.0345 0.015", attributes={"pos": "0.77 -0.616 0.905", "name": "table_B"}
    )
    table_C = GraniteCountertop(
        assets="kitchen/counter", size="0.36 0.0345 0.015", attributes={"pos": "0.77 -0.01 0.905", "name": "table_C"}
    )
    table_D = GraniteCountertop(
        assets="kitchen/counter", size="0.35 0.325 0.015", attributes={"pos": "1.41 -0.325 0.905", "name": "table_D"}
    )

    countertop = GraniteCountertop(
        assets="kitchen/counter", size="1.06 0.325 0.015", attributes={"pos": "0.75 0.325 1.1", "name": "countertop"}
    )
    sink = KitchenSinkWide(assets="kitchen/sink_wide", attributes={"pos": "0.75 -0.31 0.94"})

    dw = KitchenDishwasher(assets="kitchen/dishwasher", attributes={"pos": "-0.1 -0.075 0.00", "name": "dishwasher", "childclass": "dw"})
    dw2 = KitchenDishwasher(assets="kitchen/dishwasher", prefix="dw2", attributes={"pos": "1.6 -0.075 0.00", "name": "dishwasher2", "childclass": "dw"})
    fridge = KitchenFridge(assets="kitchen/fridge", attributes={"pos": "-1.4 -0.45 0.95"})

    plate = ObjaverseMujoco(assets="kitchen/plate", pos=[0, -0.5, 0.95], name="plate", collision_count=32, randomize_colors=False)
    mug_pos = list(np.array([-0.4, -1.25, 1]) - origin)
    mug = ObjaverseMujocoMug(assets="kitchen/mug", pos=mug_pos, collision_count=32, visual_count=2)
    bowl_pos = list(np.array([-0.2, -1.25, 1]) - origin)
    bowl = ObjaverseMujocoBowl(assets="kitchen/bowl", collision_count=32, scale=0.2, pos=bowl_pos, name="bowl")
    spoon_pos = list(np.array([-0.4, -1.45, 1.2]) - origin)
    spoon = ObjaverseMujocoSpoon(assets="kitchen/spoon", pos=spoon_pos, name="spoon", scale=0.3, collision_count=32, randomize_colors=False)


    cup_pos = list(np.array([x1, y1, 1.2]) - origin)
    cup = ObjaverseMujocoCup(assets="kitchen/cup", pos=cup_pos, name="cup", collision_count=32, randomize_colors=False)

    particles_pos = list(np.array([x1 - 0.01, y1 - 0.01, 1.18]) - origin)
    particles = Replicate(
        Replicate(
            Replicate(
                Body(
                    pos=particles_pos,
                    _attributes={
                        "name": "particle",
                    },
                    _children_raw="""
                            <freejoint/>
                            <geom size=".007" rgba=".8 .2 .1 1" condim="1" solref="0.001 1" solimp="0.99 0.99 0.001"/>
                        """,

                ),
                _attributes=dict(
                    count=nz,
                    offset="0.0 0.0 0.014",
                )
            ),
            _attributes=dict(
                count=ny,
                offset="0.0 0.014 0.0",
            ),
        ),
        _attributes=dict(
            count=nx,
            offset="0.014 0.0 0.0",
        )
    )

    cameras = make_camera_rig(pos=[x1 - 0.6, y1 , 1.2])
    stereo_cameras = make_origin_stereo_rig(pos=[x1 - 0.8, y1 , 1.0])

    # scene = FloatingShadowHand(
    scene = FloatingShadowHand(
        Body(
            front_wall,
            stack_B,
            stack_C,
            table_A,
            table_B,
            table_C,
            table_D,
            countertop,
            sink,
            # oven,
            # microwave,
            dw,
            dw2,
            # fridge,
            attributes=dict(name="room", pos=-1 * origin, quat=quat),
        ),
        mug,
        bowl,
        spoon,
        cup,
        particles,
        *cameras.get_cameras(),
        *stereo_cameras.get_cameras(),
        pos=(np.array([-0.8, -1.15, 1.1]) - origin).tolist(),
        # dual_gripper=True,
    )

    return scene._xml | Prettify()

class Fixed(MocapTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.particle_ids = []
        self.cup_geom_ids = []
        self.bowl_geom_ids = []
        self.left_hand_geom_ids = []
        self.right_hand_geom_ids = []
        self.step = 0

    def check_particle_in_sink(self, physics, verbose=False):
        if not self.particle_ids:
            self.particle_ids = get_all_body_ids(Ijphysics, "particle")
        particle_pos = np.array([physics.data.xpos[id] for id in self.particle_ids])

        sink_corners = np.array([physics.data.site_xpos[get_site(physics, f"sink-wide_corner_{i}").id] for i in range(1, 9)])
        xmin = np.min(sink_corners[:, 0])
        xmax = np.max(sink_corners[:, 0])
        ymin = np.min(sink_corners[:, 1])
        ymax = np.max(sink_corners[:, 1])
        zmax = np.max(sink_corners[:, 2])
        zmin = np.min(sink_corners[:, 2])
        inside = ((particle_pos[:, 0] > xmin) & (particle_pos[:, 0] < xmax) &
                  (particle_pos[:, 1] > ymin) & (particle_pos[:, 1] < ymax) &
                  (particle_pos[:, 2] < zmax)) | (particle_pos[:, 2] < zmin)
        num_inside = np.sum(inside)
        if verbose:
            print(f"Particles inside sink: {num_inside}/{len(self.particle_ids)}")
        if num_inside == nx * ny * nz:
            return True
        return False

    def check_cup_in_left_hand(self, physics, verbose=False):
        if not self.cup_geom_ids:
            self.cup_geom_ids = get_all_geom_ids(physics, "cup")
        if not self.left_hand_geom_ids:
            left_hand_body_ids = get_all_body_ids(physics, "lh")
            left_hand_geom_ids = []
            for body_id in left_hand_body_ids:
                if physics.model.body(body_id).geomnum[0] > 0:
                    left_hand_geom_ids.extend(range(physics.model.body(body_id).geomadr[0], physics.model.body(body_id).geomadr[0] + physics.model.body(body_id).geomnum[0]))
            self.left_hand_geom_ids = left_hand_geom_ids
            # print(left_hand_geom_ids)

        cup_site = get_site(physics, "cup")
        cup_height = physics.data.site_xpos[cup_site.id][2]
        if cup_height < 1.3:
            return False

        n = physics.data.ncon
        if n == 0:
            return False
        # Iterate active contacts
        hits = 0
        min_contacts = 2
        contacts = physics.data.contact[:n]  # view of active contacts
        for c in contacts:
            g1, g2 = c.geom1, c.geom2
            if (g1 in self.cup_geom_ids and g2 in self.left_hand_geom_ids) or (g2 in self.cup_geom_ids and g1 in self.left_hand_geom_ids):
                hits += 1
                if hits >= min_contacts:
                    return True
        if verbose:
            print("hits with left hand:", hits)
        return False

    def check_cup_in_right_hand(self, physics, verbose=False):
        if not self.right_hand_geom_ids:
            right_hand_body_ids = get_all_body_ids(physics, "rh")
            right_hand_geom_ids = []
            for body_id in right_hand_body_ids:
                if physics.model.body(body_id).geomnum[0] > 0:
                    right_hand_geom_ids.extend(range(physics.model.body(body_id).geomadr[0], physics.model.body(body_id).geomadr[0] + physics.model.body(body_id).geomnum[0]))
            self.right_hand_geom_ids = right_hand_geom_ids
            # print(right_hand_geom_ids)
            # print(self.cup_geom_ids)
        n = physics.data.ncon
        if n == 0:
            return False
        # Iterate active contacts
        hits = 0
        min_contacts = 2
        contacts = physics.data.contact[:n]  # view of active contacts
        for c in contacts:
            g1, g2 = c.geom1, c.geom2
            # print("contact geoms:", g1, g2)
            if (g1 in self.cup_geom_ids and g2 in self.right_hand_geom_ids) or (g2 in self.cup_geom_ids and g1 in self.right_hand_geom_ids):
                hits += 1
                if hits >= min_contacts:
                    return True
        if verbose:
            print("hits with right hand:", hits)
        return False

    def check_cup_placed(self, physics, verbose=False):
        if not self.bowl_geom_ids:
            self.bowl_geom_ids = get_all_geom_ids(physics, "bowl")
        n = physics.data.ncon
        if n == 0:
            return False
        # Iterate active contacts
        hits = 0
        min_contacts = 2
        contacts = physics.data.contact[:n]  # view of active contacts
        for c in contacts:
            g1, g2 = c.geom1, c.geom2
            if (g1 in self.cup_geom_ids and g2 in self.bowl_geom_ids) or (g2 in self.cup_geom_ids and g1 in self.bowl_geom_ids):
                hits += 1
                if hits >= min_contacts:
                    return True
        if verbose:
            print("hits with bowl:", hits)
        return False

    def get_reward(self, physics):
        # for j in range(physics.model.njnt):
        #     adr = physics.model.jnt_qposadr[j]
        #     type = physics.model.jnt_type[j]  # 0=free, 1=ball, 2=slide, 3=hinge
        #     print(physics.model.jnt(j).name,"→ qpos", adr, "type", type)
        reward = 0.0
        if self.step == 0 and self.check_cup_in_left_hand(physics):
            self.step += 1
        if self.step == 1 and self.check_cup_in_right_hand(physics):
            self.step += 1
        if self.step == 2 and self.check_particle_in_sink(physics):
            self.step += 1
        if self.step == 3 and self.check_cup_placed(physics):
            reward = 1.0

        # print("step", self.step)

        return reward

    def print_detailed_reward(self):
        print("step:", self.step)
        print("cup in left hand:", self.check_cup_in_left_hand(self.physics, verbose=True))
        print("cup in right hand:", self.check_cup_in_right_hand(self.physics, verbose=True))
        print("particles in sink:", self.check_particle_in_sink(self.physics, verbose=True))
        print("cup placed in bowl:", self.check_cup_placed(self.physics, verbose=True))



class CupRandom(Fixed):
    cup_qpos_addr = 34
    particles_qpos_start_addr = 41
    num_particles = 6 * 2 * 2
    d = 0.01
    xy_limits = [x1 - origin.x - 0.05, x1 - origin.x + 0.05], [y1 - origin.y - 0.05, y1 - origin.y + 0.05]
    xy_reject = [x1 - origin.x, x1 - origin.x], [y1 - origin.y, y1 - origin.y]

    xy_poses = init_states(xy_limits, d, xy_reject)
    print("the length is", len(xy_poses))
    pose_buffer = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def random_state(
        cls,
        qpos=None,
        quat=None,
        addr=cup_qpos_addr,
        index=None,
        mocap_pos=None,
        **kwargs,
    ):
        import random

        if index is None:
            # if not cls.pose_buffer:
            #     cls.pose_buffer = copy(cls.xy_poses)
            #     random.shuffle(cls.pose_buffer)
            #
            # x, y = cls.pose_buffer.pop(0)
            x, y = random.choice(cls.xy_poses)
        else:
            x, y = cls.xy_poses[index]

        new_qpos = qpos.copy()

        new_qpos[addr : addr + 2] = x, y

        offset = new_qpos[addr : addr + 2] - qpos[addr : addr + 2]

        for i in range(cls.num_particles):
            qpos_ind = cls.particles_qpos_start_addr + 7 * i
            new_qpos[qpos_ind : qpos_ind + 2] += offset

        # Add Gaussian noise to mocap position
        # if mocap_pos is not None:
        #     mocap_pos = mocap_pos.copy()
        #     noise = np.random.normal(loc=0.0, scale=0.005, size=mocap_pos.shape)  # std=5mm
        #     mocap_pos += noise

        return dict(qpos=new_qpos, quat=quat, mocap_pos=mocap_pos, **kwargs)


def register(strict=False):
    add_env(
        env_id="PourLiquid-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=Fixed,
            xml_renderer=make_schema,
            camera_names=["right", "top", "back", "stereo_far_left", "stereo_far_right"],
            workdir=Path(__file__).parent,
            mode="multiview",
        ),
        strict=strict,
    )

    add_env(
        env_id="PourLiquid-cup_random-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=CupRandom,
            xml_renderer=make_schema,
            camera_names=["right", "top", "back", "stereo_far_left", "stereo_far_right"],
            workdir=Path(__file__).parent,
            mode="multiview",
        ),
        strict=strict,
    )

    add_env(
        env_id="PourLiquid-cup_random-lucid-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=CupRandom,
            xml_renderer=make_schema,
            camera_names=["right", "top", "back", "stereo_far_left", "stereo_far_right"],
            workdir=Path(__file__).parent,
            mode="lucid",
            object_keys=["particle", "cup"],
        ),
        strict=strict,
    )



if __name__ == "__main__":
    from vuer_mujoco.schemas.utils.file import Save

    make_schema() | Save(__file__.replace(".py", ".mjcf.xml"))
