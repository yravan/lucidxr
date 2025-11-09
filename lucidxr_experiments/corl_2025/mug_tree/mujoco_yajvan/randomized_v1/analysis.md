
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
    "chunksize-50",
    "chunksize-100",
    "chunksize-150",
]

prefix = "lucidxr/lucidxr/corl_2025/mug_tree/mujoco_yajvan/randomized_v1/eval/MugTree-mug_rand-v1/"
loader = ML_Logger(prefix=prefix)
```

**Performance**

| Checkpoint | Success | Num Trials
| ------- | ------------- | ---------- |
| chunksize-50 | 19.3% | 166 |
| chunksize-100 | 18.7% | 155 |
| chunksize-150 | 30.3% | 165 |