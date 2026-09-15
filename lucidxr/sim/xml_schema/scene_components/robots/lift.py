from lucidxr.sim.xml_schema.robots.arms.lift import Lift
from lucidxr.sim.xml_schema.schema import Group


class LiftRobot(Group):
    name = "lift_robot"

    def __init__(
        self,
        camera_rig=None,
        quat=None,
        right_hand=True,
        left_hand=True,
        head=True,
        **kwargs,
    ):
        """
        right_hand, left_hand, and base determine whether those mocaps are included or not.
        """
        super().__init__(**kwargs)
        robot = Lift(
            name="lift",
            pos=self._pos,
            quat=[1, 0, 0, 0],  # Aligned with table scene
            assets="robots/lift",
        )
        robot._add_mocaps(left_hand=left_hand, right_hand=right_hand, head=head)

        _children = [
            robot,
        ]

        self._children = tuple(_children)
