
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
    "chunksize-50/cameras-1",
    "chunksize-50/cameras-0",
    "chunksize-100/cameras-1",
    "chunksize-100/cameras-0",
]

prefix = "lucidxr/lucidxr/corl_2025/pick_place/mujoco_alan/kai_debug/eval/PickPlace-block_rand_more-v1/"
loader = ML_Logger(prefix=prefix)
```

**Performance**

| Checkpoint | Success | Num Trials
| ------- | ------------- | ---------- |
| chunksize-50/cameras-1 | 83.3% | 90 |
| chunksize-50/cameras-0 | 78.2% | 87 |
| chunksize-100/cameras-1 | 100.0% | 5 |
| chunksize-100/cameras-0 | 91.7% | 84 |