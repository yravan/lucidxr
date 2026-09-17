"""Shared playback arguments for the viewer, local renderer and cluster launcher."""

import json

from lucidxr.sim.playback import ReplaySpec


def add_replay_arguments(parser):
    parser.add_argument("--mode", choices=("state", "commands"), default="state")
    parser.add_argument("--scene", help="Target scene for command replay; defaults to the recorded scene")
    parser.add_argument("--seed", type=int, default=0, help="Target scene seed")
    parser.add_argument("--scene-options", type=json.loads, default={})


def replay_spec(args):
    return ReplaySpec(args.mode, args.scene, args.seed, args.scene_options)
