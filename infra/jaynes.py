"""A narrow compatibility correction for the pinned Jaynes batch runner."""

from jaynes.runners import Slurm


class BatchSlurm(Slurm):
    """Keep the worker in the foreground so Slurm receives its actual exit status."""

    def __init__(self, **kwargs):
        super().__init__(interactive=False, **kwargs)
        fragment = "{JYNS_main_script} & wait"
        if fragment not in self.run_script_thunk:
            raise RuntimeError("Jaynes batch template changed; review the compatibility adapter")
        self.run_script_thunk = self.run_script_thunk.replace(fragment, "{JYNS_main_script}")
        self.run_script_thunk = self.run_script_thunk.replace(
            "#!/bin/bash\n", "#!/bin/bash\nset -euo pipefail\n"
        )
