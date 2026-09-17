"""Freeze tracked working-tree edits without changing the user's index or branch."""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path


def code_tree(repo):
    """A git tree is the snapshot version; newly created files must be git-added first."""
    repo = Path(repo).resolve()

    def git(*args, **kwargs):
        return subprocess.check_output(["git", "-C", str(repo), *args], **kwargs).decode().strip()

    index = Path(git("rev-parse", "--path-format=absolute", "--git-path", "index"))
    with tempfile.TemporaryDirectory(prefix="lucidxr-index-") as temporary:
        copied = Path(temporary) / "index"
        shutil.copyfile(index, copied)
        env = {**os.environ, "GIT_INDEX_FILE": str(copied)}
        git("add", "-u", env=env)
        return git("write-tree", env=env)
