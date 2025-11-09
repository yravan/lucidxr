# vuer MuJoCo Environments for Lucid-XR

## Setting Up

```shell
# place it directly under home.
mkdir ~/fortyfive
cd fortyfive
git clone https://github.com/vuer-ai/lucidxr.git
```

Now you can go into this repo and install it (and dependencies)

```shell
conda create -n lucidxr python=3.11
pip install -e '.[dev]'
```

The key things to note are: dm_control version needs to be up to date.
MuJoCo should be `3.3.4`. cloudpickle should be `3.1.1`.

### Downloading Assets

> Need to write this up when we onboard new people.

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
- **`lucidxr-launch`**: This one launches on the cluster. You can call via

    ```shell
    lucidxr-launch --sweep some_exp.jsonl 
    ```

Training life-cycle

1. run render worker
2. run h5_worker
3. now you can run train. This is a bit too much.
