<h1 class="full-width" style="font-size: 49px"><code style="font-size: 1.em; background-clip: text; color: mediumvioletred;">Vuer</code>-<code style="color: #28b7e6">MuJoCo</code><span style="font-size: 0.3em; margin-left: 0.15em; margin-right:-0.4em;">｣</span></h1>

<link rel="stylesheet" href="_static/title_resize.css">

This is the documentation for the `vuer-mujoco` package.

I have set up data collection, visualization and training as cli programs, that is installed as part of the
package. The scripts are located in the `scripts` module in any of the installed packages. For instance, `lucidxr`
contains the `launch.py` script, which you can call via `lucidxr-launch -h` from the command line after
installation. (Updated on 2025-02-07) 

To install:

```shell
pip install 'vuer_mujoco[all]=={VERSION}'
```
### Scripts:

For detailed notes on how to collect data and how to run experiments, refer to the notes on each of these scripts.

- **`collect-demo`**: this one fires up a vuer server, that allows you to
collect demonstrations. You can call via
    ```shell
    collect-demo --name pick_block
    ```
- **`visualize-demo`**: this one visualizes the demonstrations you have
collected. You can call via
    ```shell
    visualize-demo --name pick_block
    ```
- **`render-demo`**: This one launches on the cluster. You can call via

    ```shell
    render-demo --sweep some_exp.jsonl 
    ```
  
- **`lucidxr-launch`**: This one launches on the cluster. You can call via

    ```shell
    lucidxr-launch --sweep some_exp.jsonl 
    ```

<!-- prettier-ignore-start -->

```{eval-rst}
.. toctree::
   :hidden:
   :maxdepth: 1
   :titlesonly:

   Quick Start <quick_start>
   Report Issues <https://github.com/vuer-ai/lucidxr/issues?q=is:issue+is:closed>
   CHANGE LOG <CHANGE_LOG.md>
   Evaluation Environments <eval_envs.md>
   
.. toctree::
   :maxdepth: 3
   :caption: Examples
   :hidden:
   
   Simple Scene <examples/01_panda_army.md>
   Xarm7 <examples/02_xarm7.md>
   Collecting Demos <examples/01_collecting_demo.md>
   
.. toctree::
   :maxdepth: 3
   :caption: Python API
   :hidden:
   
   .schemas.base <api/base.md>
   .schemas.mujoco_schema <api/mujoco_schema.md>
   .schemas.robots.robot_schema <api/robot_schema.md>
   .schemas.robots.panda <api/panda.md>
  
```
