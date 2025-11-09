
# LucidXR Experiment Metrics


```python
def get_metrics(ckpt):
    with loader.Prefix(ckpt):
        print(loader.get_dash_url())
        # print(loader.)
        metrics = loader.read_metrics(
            "success",
            path="episode_metrics.pkl",
            num_bins=1,
        )

        succ = np.array(metrics.str[0].tolist())

    doc @ f"| {ckpt} | {succ.mean():0.1%} | {len(succ)} |"
```
```python
checkpoint_meta = [
    "chunksize-50/cameras-1",
    "chunksize-50/cameras-0",
    "chunksize-100/cameras-1",
    "chunksize-100/cameras-0",
]

prefix = "lucidxr/lucidxr/corl_2025/pick_place/mujoco_kai/pick_place_v1/eval/PickPlace-block_rand_more-v1/"
loader = ML_Logger(prefix=prefix)
```

**Performance**

| Checkpoint | Success | Num Trials
| ------- | ------------- | ---------- |
| chunksize-50/cameras-1 | 49.0% | 100 |
| chunksize-50/cameras-0 | 16.2% | 99 |
| chunksize-100/cameras-1 | 63.8% | 94 |
| chunksize-100/cameras-0 | 25.8% | 93 |