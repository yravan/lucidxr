from dotvar import auto_load  # noqa

from vuer_mujoco import tasks

def test_seg_wrapper():
    env = tasks.make("Pick_sphere-segmentation-v1")
    obs = env.reset()

    assert True