from pathlib import Path

from dotvar import auto_load  # noqa

from ml_logger.job import RUN, instr  # noqa

RUN.job_name = "{now:%Y/%m-%d}"
RUN.prefix = "lucidxr/lucidxr/{file_stem}/{job_name}"
# this sets the root for calculating the prefix
RUN.script_root = Path(__file__).parent

assert RUN and instr, "use this RUN object and the instr wrapper."
