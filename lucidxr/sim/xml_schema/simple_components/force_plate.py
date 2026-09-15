from lucidxr.sim.xml_schema.base import Xml
from lucidxr.sim.xml_schema.schema import Body, MjNode


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


class ForcePlate(Body):
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
        geom_type = kwargs.pop("type", geom_type)
        super().__init__(
            Xml(tag="geom", name=f"{name}-geom", type=geom_type, size=size, rgba=rgba),
            Xml(tag="site", name=f"{name}-site", type=geom_type, size=size, rgba=rgba),
            name=name,
            pos=pos,
            quat=quat,
            **kwargs,
        )

    # note: we moved this from the post-amble to the preamble, so that the last n sites
    #   are the end-effector/hand landmarks. This is subject to change. - Ge
    _preamble = """
    <sensor>
        <touch site="{name}-site" name="{name}-force"/>
    </sensor>
    """
