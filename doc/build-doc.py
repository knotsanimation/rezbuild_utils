import subprocess
import sys
from pathlib import Path

THISDIR = Path(__file__).parent

SRCDIR = THISDIR / "source"
BUILDIR = THISDIR / "build"

COMMAND = [
    "sphinx-build",
    "-M",
    "html",
    str(SRCDIR),
    str(BUILDIR),
]
COMMAND += sys.argv[1:]

subprocess.check_call(COMMAND, cwd=THISDIR)
