from vuer_mujoco.schemas.base import Raw
from vuer_mujoco.schemas.schema import Mjcf, Body


class Room(Mjcf):

    def __init__(self, *_children, tag=None, children=[], **attributes):
        wall_main = Body(
            tag="body",
            name="wall_room_main",
            pos="2.75 0.02 1.5",
            quat="-0.707107 0.707107 0 0",
            children= Raw @ """
                <geom name="wall_room_g0" size="2.79 1.5 0.02" type="box" rgba="0.5 0 0 1"/>
                <geom name="wall_room_g0_vis" size="2.79 1.5 0.02" type="box" contype="0" conaffinity="0" 
                      group="1" mass="0" material="wall_room_wall_mat"/>
                <site name="wall_room_default_site" pos="0 0 0" size="0.002" rgba="1 0 0 -1"/>
            """,
            preamble="""
                <asset>
                    <texture type="skybox" builtin="flat" rgb1="1 1 1" rgb2="1 1 1" width="256" height="1536"/>
                    <texture type="2d" name="wall_room_wall" file="rooms/assets/textures/bricks/red_bricks.png"/>
                    <material name="wall_room_wall_mat" texture="wall_room_wall" texuniform="true" texrepeat="3 3" shininess="0.01" reflectance="0.1"/>
                </asset>
            """,
        )

        wall_main_backing = Body(
            tag="body",
            name="wall_backing_room_main",
            pos="2.75 0.14 1.38",
            quat="-0.707107 0.707107 0 0",
            children=Raw @ """
                <geom name="wall_backing_room_g0" size="2.99 1.62 0.1" type="box" rgba="0.5 0 0 1"/>
                <geom name="wall_backing_room_g0_vis" size="2.99 1.62 0.1" type="box" contype="0" conaffinity="0" 
                      group="1" mass="0" material="wall_backing_room_wall_mat"/>
                <site name="wall_backing_room_default_site" pos="0 0 0" size="0.002" rgba="1 0 0 -1"/>
            """,
            preamble="""
                <asset>
                    <texture type="2d" name="wall_backing_room_wall" file="rooms/assets/textures/flat/light_gray.png"/>
                    <material name="wall_backing_room_wall_mat" texture="wall_backing_room_wall" texuniform="true" texrepeat="3 3" shininess="0.01" reflectance="0.1"/>
                </asset>
            """,
        )

        wall_left = Body(
            tag="body",
            name="wall_left_room_main",
            pos="-0.02 -1.5 1.5",
            quat="0.5 0.5 -0.5 -0.5",
            children= Raw @ """
            <geom name="wall_left_room_g0" size="1.54 1.5 0.02" type="box" rgba="0.5 0 0 1"/>
            <geom name="wall_left_room_g0_vis" size="1.54 1.5 0.02" type="box" contype="0" conaffinity="0" 
                  group="1" mass="0" material="wall_left_room_wall_mat"/>
            <site name="wall_left_room_default_site" pos="0 0 0" size="0.002" rgba="1 0 0 -1"/>
            """,
            preamble="""
                <asset>
                    <texture type="2d" name="wall_left_room_wall" file="rooms/assets/textures/bricks/red_bricks.png"/>
                    <material name="wall_left_room_wall_mat" texture="wall_left_room_wall" texuniform="true" texrepeat="3 3" shininess="0.01" reflectance="0.1"/>
                </asset>
            """,
        )

        wall_left_backing = Body(
            tag="body",
            name="wall_left_backing_room_main",
            pos="-0.14 -1.5 1.38",
            quat="0.5 0.5 -0.5 -0.5",
            children= Raw @ """
                <geom name="wall_left_backing_room_g0" size="1.54 1.62 0.1" type="box" rgba="0.5 0 0 1"/>
                <geom name="wall_left_backing_room_g0_vis" size="1.54 1.62 0.1" type="box" contype="0" conaffinity="0" 
                      group="1" mass="0" material="wall_left_backing_room_wall_mat"/>
                <site name="wall_left_backing_room_default_site" pos="0 0 0" size="0.002" rgba="1 0 0 -1"/>
            """,
            preamble="""
                <asset>
                    <texture type="2d" name="wall_left_backing_room_wall" file="rooms/assets/textures/flat/light_gray.png"/>
                    <material name="wall_left_backing_room_wall_mat" texture="wall_left_backing_room_wall" texuniform="true" texrepeat="3 3" shininess="0.01" reflectance="0.1"/>
                </asset>
            """,
        )

        wall_right = Body(
            tag="body",
            name="wall_right_room_main",
            pos="5.52 -1.5 1.5",
            quat="0.5 -0.5 -0.5 0.5",
            children= Raw @ """
            <geom name="wall_right_room_g0" size="1.54 1.5 0.02" type="box" rgba="0.5 0 0 1"/>
            <geom name="wall_right_room_g0_vis" size="1.54 1.5 0.02" type="box" contype="0" conaffinity="0" 
                  group="1" mass="0" material="wall_right_room_wall_mat"/>
            <site name="wall_right_room_default_site" pos="0 0 0" size="0.002" rgba="1 0 0 -1"/>
            """,
            preamble="""
                <asset>
                    <texture type="2d" name="wall_right_room_wall" file="rooms/assets/textures/bricks/red_bricks.png"/>
                    <material name="wall_right_room_wall_mat" texture="wall_right_room_wall" texuniform="true" texrepeat="3 3" shininess="0.01" reflectance="0.1"/>
                </asset>
            """,
        )

        wall_right_backing = Body(
            tag="body",
            name="wall_right_backing_room_main",
            pos="5.64 -1.5 1.38",
            quat="0.5 -0.5 -0.5 0.5",
            children= Raw @ """
                <geom name="wall_right_backing_room_g0" size="1.54 1.62 0.1" type="box" rgba="0.5 0 0 1"/>
                <geom name="wall_right_backing_room_g0_vis" size="1.54 1.62 0.1" type="box" contype="0" conaffinity="0" group="1" mass="0" material="wall_right_backing_room_wall_mat"/>
                <site name="wall_right_backing_room_default_site" pos="0 0 0" size="0.002" rgba="1 0 0 -1"/>
            """,
            preamble="""
                <asset>
                    <texture type="2d" name="wall_right_backing_room_wall" file="rooms/assets/textures/flat/light_gray.png"/>
                    <material name="wall_right_backing_room_wall_mat" texture="wall_right_backing_room_wall" texuniform="true" texrepeat="3 3" shininess="0.01" reflectance="0.1"/>
                </asset>
            """,
        )

        floor_main = Body(
            tag="body",
            name="floor_room_main",
            pos="2.75 -1.5 -0.02",
            quat="0.707107 0 0 0.707107",
            children= Raw @ """
                <geom name="floor_room_g0" size="1.54 2.79 0.02" type="box" rgba="0.5 0 0 1"/>
                <geom name="floor_room_g0_vis" size="1.54 2.79 0.02" type="box" contype="0" conaffinity="0" 
                      group="1" mass="0" material="floor_room_wall_mat"/>
                <site name="floor_room_default_site" pos="0 0 0" size="0.002" rgba="1 0 0 -1"/>
            """,
            preamble="""
                <asset>
                    <texture type="2d" name="floor_room_wall" file="rooms/assets/textures/tiles/concrete_tiles.png"/>
                    <material name="floor_room_wall_mat" texture="floor_room_wall" texuniform="true" texrepeat="0.5 0.5"/>
                </asset>
            """,
        )

        floor_main_backing = Body(
            tag="body",
            name="floor_backing_room_main",
            pos="2.75 -1.5 -0.14",
            quat="0.707107 0 0 0.707107",
            children= Raw @ """
                <geom name="floor_backing_room_g0" size="1.54 2.79 0.1" type="box" rgba="0.5 0 0 1"/>
                <geom name="floor_backing_room_g0_vis" size="1.54 2.79 0.1" type="box" contype="0" conaffinity="0" 
                      group="1" mass="0" material="floor_backing_room_wall_mat"/>
                <site name="floor_backing_room_default_site" pos="0 0 0" size="0.002" rgba="1 0 0 -1"/>
            """,
            preamble="""
                <asset>
                    <texture type="2d" name="floor_backing_room_wall" file="rooms/assets/textures/flat/light_gray.png"/>
                    <material name="floor_backing_room_wall_mat" texture="floor_backing_room_wall" texuniform="true" texrepeat="0.5 0.5"/>
                </asset>
            """,
        )

        # Collect these nodes in children
        children.extend([
            wall_main,
            wall_main_backing,
            wall_left,
            wall_left_backing,
            wall_right,
            wall_right_backing,
            floor_main,
            floor_main_backing,
        ])

        # Call the Mjcf constructor
        super().__init__(*_children, tag=tag, children=children, **attributes)
