"""Explicit scene catalogue and convenience functions."""

from importlib import import_module

from .base import Scene

_SCENE_CLASSES = {
    "ball_sorting": "BallSorting",
    "basketball_shot": "BasketballShot",
    "fishing_toy": "FishingToy",
    "flip_mug": "FlipMug",
    "insert_shapes": "InsertShapes",
    "juggle_cubes": "JuggleCubes",
    "kitchen_room": "KitchenRoom",
    "microwave_muffin": "MicrowaveMuffin",
    "move_plate": "MovePlate",
    "mug_drawer": "MugDrawer",
    "mug_tree": "MugTree",
    "object_permanence": "ObjectPermanence",
    "orbit_table": "OrbitTable",
    "particle_pour": "ParticlePour",
    "particle_sweep": "ParticleSweep",
    "pick_block": "PickBlock",
    "pick_place": "PickPlace",
    "pick_sphere": "PickSphere",
    "poncho_table": "PonchoTable",
    "pour_liquid": "PourLiquid",
    "push_t": "PushT",
    "robosuite_door": "RobosuiteDoor",
    "robosuite_lift": "RobosuiteLift",
    "robosuite_nutassembly": "RobosuiteNutAssembly",
    "robosuite_pickplace": "RobosuitePickPlace",
    "robosuite_stack": "RobosuiteStack",
    "sort_shapes": "SortShapes",
    "stack_blocks": "StackBlocks",
    "teddy_bear_table": "TeddyBearTable",
    "tie_knot": "TieKnot",
    "utensil_drawer": "UtensilDrawer",
    "weighted_cubes": "WeightedCubes",
}
SCENES = tuple(_SCENE_CLASSES)


def make_scene(name: str, **options) -> Scene:
    try:
        classname = _SCENE_CLASSES[name]
    except KeyError:
        raise ValueError(f"Unknown scene {name!r}. Available scenes: {', '.join(SCENES)}") from None
    cls = getattr(import_module(f"lucidxr.sim.scenes.{name}"), classname)
    return cls(**options)


def build_xml(name: str, **options) -> str:
    return make_scene(name, **options).to_xml()


def compile_model(name: str, **options):
    return make_scene(name, **options).compile()


__all__ = ["Scene", "SCENES", "make_scene", "build_xml", "compile_model"]
