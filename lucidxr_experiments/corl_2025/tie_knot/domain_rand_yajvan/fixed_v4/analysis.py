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
        "chunksize-50",
        "chunksize-100",
        "chunksize-150",
    ]

    prefix = "lucidxr/lucidxr/corl_2025/tie_knot/mujoco_yajvan/fixed_v4/eval/TieKnot-v1/"
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
