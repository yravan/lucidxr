from cmx import doc
from ml_logger import ML_Logger
import numpy as np

doc @ """
# LucidXR Experiment Metrics

"""
with doc:

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


with doc:
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

with doc.hide:
    doc @ """
    **Performance**

    | Checkpoint | Success | Num Trials
    | ------- | ------------- | ---------- |"""

    for ckpt in checkpoint_meta:
        try:
            get_metrics(ckpt)
        except:
            print("Error:", ckpt)

doc.flush()
