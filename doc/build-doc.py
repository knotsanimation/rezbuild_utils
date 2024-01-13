import subprocess
import sys
from pathlib import Path

THISDIR = Path(__file__).parent

COMMAND = [
    "sphinx-build",
    "-M",
    "html",
    str(THISDIR / "source"),
    str(THISDIR / "build"),
]
COMMAND += sys.argv[1:]

subprocess.check_call(COMMAND, cwd=THISDIR)
