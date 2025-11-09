
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
    "chunksize-50/v2",
    "chunksize-100/v2",
    "chunksize-150/v2",
]

prefix = "lucidxr/lucidxr/corl_2025/flip_mug/mujoco_kai/eval/FlipMug-random-v1/"
loader = ML_Logger(prefix=prefix)
```

**Performance**

| Checkpoint | Success | Num Trials
| ------- | ------------- | ---------- |
| chunksize-50/v2 | 68.4% | 95 |
| chunksize-100/v2 | 65.2% | 92 |
| chunksize-150/v2 | 17.6% | 85 |