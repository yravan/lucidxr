# Collecting Demo Data Locally

First install the codebase --- you should be able to see the `collect-demo` & `playback-demo` commandline programs after installation.
**note:** you might want to install dependencies.

```shell
pip install -e .
```

To see the full set of command options, do the following. The options are the same for both
```shell
collect-demo --help
```

1. **To visualize mujoco examples, do**
```shell
collect-demo --wd <root-path> --scene-folder adhesion --scene-name active_adhesion --port 8012
```

```shell
collect-demo --wd "/Users/ge/Library/CloudStorage/GoogleDrive-ge.ike.yang@gmail.com/My Drive/lucidxr-assets/third_party/mujoco_models" --scene-name adhesion/active_adhesion --port 8012
```

The script assumes the following file structure:

```markdown
wd
├── scene-folder
│   ├── {scene-name}.mjcf.xml
```
2. **Set the save path (under `wd`) using the `--demo-prefix` flag. The default is `{wd}/lucidxr/lucidxr/datasets/lucidxr/poc/demos/ability/yyyy/mm/dd/hh.ss.ff/`**

```shell
collect-demo --wd <root-path> --scene-folder adhesion --scene-name active_adhesion --port 8012 --demo-prefix <path-to-save-data>
```

3. **To playback the demos, use the same arguments with**
```shell
playback-demo --wd <root-path> --scene-folder adhesion --scene-name active_adhesion --port 8012 --demo-prefix <path-to-save-data>
```
Demo show the camera positions (with markers) and follows the recorded the mocap trajectory.

![](figures/playback_example.png)


