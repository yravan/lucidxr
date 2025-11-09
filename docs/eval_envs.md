# Evaluation Enviornments

### Setup

We build all the environments with `neverwhere`, and they are located in the `lucid-xr` Dropbox under
`lucid-xr/eval_envs`.

[//]: # (You should setup `rclone` to sync your dropbox with your host machine. See [here]&#40;https://rclone.org/install/&#41; for instructions for doing so. )

[//]: # ()
[//]: # (Set your `LUCIDXR_EVAL_ENVS` environment variable to point to the where `lucid-xr/eval_envs` is stored locally.)

You can drag + drop this folder under the `vuer_mujoco/tasks/assets`.

Additionally, make sure to use Ziyu's fork of gsplat -- there are some slight modifications to the rendering CUDA kernel that are helpful for reducing massive blobs:
```bash
pip install git+https://github.com/ziyc/gsplat.git@ziyu/dev
```
