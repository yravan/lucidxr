from dotvar import auto_load
from cmx import doc
from ml_logger import ML_Logger
import numpy as np

doc @ """
# LucidXR Experiment Metrics
"""

files = [
    "episode_metrics_no_tagg.pkl",
]

checkpoint_meta = [
    "chunk_size-25",
    "chunk_size-50",
]

envs = [
    "PickPlaceRobotRoom-single_random-v1",
]

def get_metrics(loader, ckpt, file='episode_metrics.pkl'):
    with loader.Prefix(ckpt):
        print(loader.get_dash_url())
        metrics = loader.read_metrics(
            "success",
            path=file,
            num_bins=1,
        )

        succ = np.array(metrics.str[0].tolist())
        return succ.mean(), succ.std(), len(succ)

for file in files:
    doc @ f"## File: `{file}`"
    for env in envs:
        doc @ f"""
        ## Environment: `{env}`
    
        | Checkpoint | Success | Num Trials |
        |------------|---------|------------| """

        prefix = f"lucidxr/lucidxr/post_corl_2025/yajvan/7-31-25/adam_real_v2/eval/{env}/"
        loader = ML_Logger(prefix=prefix)


        for ckpt in checkpoint_meta:
            try:
                succ_mean, succ_std, n_trials = get_metrics(loader, ckpt, file)
                doc @ f"| {ckpt} | {succ_mean:.1%} ± {succ_std:.1%} | {n_trials} |"
            except Exception as e:
                print("Error:", ckpt, e)

doc.flush()