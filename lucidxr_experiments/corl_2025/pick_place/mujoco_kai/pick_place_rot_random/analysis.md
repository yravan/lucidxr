
# LucidXR Experiment Metrics


```python
def get_metrics(ckpt):
    with loader.Prefix(ckpt):
        print(loader.get_dash_url())
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
    "chunksize-50/1/v3",
    "chunksize-50/2/v3",
    "chunksize-50/3/v3",
    "chunksize-100/1/v3",
    "chunksize-100/2/v3",
    "chunksize-100/3/v3",
    # "chunksize-150/cameras-1/v3",
    # "chunksize-150/cameras-0/v3",
]

prefix = "lucidxr/lucidxr/corl_2025/pick_place/mujoco_kai/pick_place_rot_random/eval/PickPlace-block_rand-v1/"
loader = ML_Logger(prefix=prefix)
```

**Performance**

| Checkpoint | Success | Num Trials
| ------- | ------------- | ---------- |
| chunksize-50/1/v3 | 56.2% | 96 |
| chunksize-50/2/v3 | 55.7% | 88 |
| chunksize-50/3/v3 | 53.8% | 91 |
| chunksize-100/1/v3 | 47.1% | 87 |
| chunksize-100/2/v3 | 44.2% | 95 |
| chunksize-100/3/v3 | 52.7% | 93 |