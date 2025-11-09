from params_proto.hyper import Sweep
from lucidxr.learning.train import TrainArgs, ACT_Config, main
import jaynes

jobs = Sweep.read("learn.jsonl")

for jid, job in enumerate(jobs):
    print(f"running {job}")
    jaynes.config(mode="default", runner=dict(name=f"trainer-{jid}"))
    # jaynes.config(mode="local")
    jaynes.add(
        main,
        job,
    )
    # jaynes.listen()

jaynes.execute()
jaynes.listen()