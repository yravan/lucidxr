"""Ortho camera rig preset."""

from functools import partial

from .rig import make_camera_rig as _make_camera_rig

make_camera_rig = partial(_make_camera_rig, preset="ortho")
