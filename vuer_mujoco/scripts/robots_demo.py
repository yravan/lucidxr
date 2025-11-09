from vuer_mujoco.schemas import Mjcf, Xml
from vuer_mujoco.schemas.robots.franka_panda import Panda

def spawn_panda_scene():

    panda1 = Panda(name="panda_left", pos="1 0 0")
    panda2 = Panda(name="panda_right", pos="-1 0 0")
    compiler = Xml(tag='body') # placeolder for compiler, which should be passed into room
    setattr(compiler, 'preamble', '<compiler angle="radian" meshdir="./assets/robots/assets/robots"/>')
    scene = Mjcf(model="panda_demo", children=[panda1, panda2, compiler])

    with open("panda_demo.xml", "w") as f:
        f.write(scene._xml)
        f.close()

        
if __name__ == "__main__":
    spawn_panda_scene()