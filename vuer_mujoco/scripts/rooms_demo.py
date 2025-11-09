from vuer_mujoco.schemas import Xml
from vuer_mujoco.schemas.room_xmls.room_1 import Room
from vuer_mujoco.schemas.schema import MjcfNode


def spawn_room():

    compiler = Xml(tag="body")  # placeolder for compiler, which should be passed into room
    hospital_bed = MjcfNode(
        tag="body",
        attributes="""name="hospital_bed" pos="1 -1.5 0" quat="0.5 0.5 -0.5 -0.5" """,
        children=[
            """
            <geom 
                mesh="HOSPITAL_BED"
                type="mesh"
                group="2"
                contype="1"
                conaffinity="1"
                rgba="1 1 1 1"
            />
        """
        ],
        preamble="""
            <asset>
                <mesh name="HOSPITAL_BED" file="rooms/objects/hospital_bed.obj" scale="0.1 0.1 0.1" />
            </asset>
            """,
    )

    setattr(compiler, "preamble", '<compiler angle="radian" texturedir="./assets" meshdir="./assets" />')
    room = Room(model="room1", children=[compiler, hospital_bed])
    with open("../../room_demo.xml", "w") as f:
        f.write(room._xml)
        f.close()


if __name__ == "__main__":
    spawn_room()
