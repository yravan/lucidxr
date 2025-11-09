from vuer_mujoco.schemas.utils.file import Prettify
from vuer_mujoco.schemas.schema import MjNode
from vuer_mujoco.schemas.se3.se3_mujoco import WXYZ, Vector3


class ForceSensor(MjNode):
    tag = "site"

    _attributes = {
        "name": "sensor-1",
    }

    _postamble = """
    <sensor>
        <force site="{name}" name="{name}-force"/>
    </sensor>
    """


def omit(dictionary, keys_to_exclude):
    """Return a new dictionary excluding specified keys."""
    return {key: value for key, value in dictionary.items() if key not in keys_to_exclude}


class ForcePlate(MjNode):
    tag = "body"

    def __init__(
        self,
        name="plate-1",
        pos=(0, 0, 0),
        quat=(1, 0, 0, 0),
        geom_type="box",
        size="0.15 0.15 0.001",
        rgba="1 0 0 0.4",
        **kwargs,
    ):
        super().__init__(name=name, pos=Vector3(*pos), quat=WXYZ(*quat))

        attr_string = " ".join([f'{k}="{v}"' for k, v in kwargs.items()])

        self.template = f"""
        <{self.tag} name="{name}" pos="{self.pos}" quat="{self.quat}">
            <geom name="{name}-geom" type="{geom_type}" size="{size}" rgba="{rgba}"/>
            <site name="{name}-site" type="{geom_type}" size="{size}" rgba="{rgba}"/>
        </{self.tag}>
        """

    # note: we moved this from the post-amble to the preamble, so that the last n sites
    #   are the end-effector/hand landmarks. This is subject to change. - Ge
    _preamble = """
    <sensor>
        <touch site="{name}-site" name="{name}-force"/>
    </sensor>
    """


if __name__ == "__main__":
    string = ForceSensor(name="yey")._xml | Prettify()
    print(string)

    string = (
        ForcePlate(
            name="yey",
            pos=Vector3(0, 0, 1),
            quat=WXYZ(0, 1, 0, 0),
            type="box",
            size="0.1 0.2 0.3",
            rgba="1 0 0 1",
        )._xml
        | Prettify()
    )

    print(string)
