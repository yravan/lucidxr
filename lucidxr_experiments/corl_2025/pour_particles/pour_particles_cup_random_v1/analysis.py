from cmx import doc
from ml_logger import ML_Logger
import numpy as np

doc @ """
# LucidXR Experiment Metrics
"""

checkpoint_meta = [
    "chunksize-50",
    "chunksize-100",
    "chunksize-150",
    "chunksize-200",
]

envs = [
    "ParticlePour-cup_rand-v1",
    "ParticlePour-cup_rand-dr-eval-v1",
]


def get_metrics(loader, ckpt):
    with loader.Prefix(ckpt):
        print(loader.get_dash_url())
        metrics = loader.read_metrics(
            "success",
            path="episode_metrics.pkl",
            num_bins=1,
        )

        succ = np.array(metrics.str[0].tolist())
        return succ.mean(), len(succ)


for env in envs:
    with doc:
        doc @ f"""
        ## Environment: `{env}`

        | Checkpoint | Success | Num Trials |
        |------------|---------|------------|
        """

    prefix = f"lucidxr/lucidxr/corl_2025/pour_particles/pour_particles_cup_random_v1/eval/{env}"
    loader = ML_Logger(prefix=prefix)

    for ckpt in checkpoint_meta:
        try:
            succ_mean, n_trials = get_metrics(loader, ckpt)
            doc @ f"| {ckpt} | {succ_mean:0.1%} | {n_trials} |"
        except Exception as e:
            print("Error:", ckpt, e)

doc.flush()
