import distutils.dir_util
import logging
import os
import shutil
import sys
from pathlib import Path


LOGGER = logging.getLogger(__name__)


def build():
    if not os.getenv("REZ_BUILD_INSTALL") == "1":
        LOGGER.info(f"skipped")
        return

    # unfortunately the package can't use itself while being built,
    # so we have to copy code.

    source_dir = Path(os.environ["REZ_BUILD_SOURCE_PATH"])
    target_dir = Path(os.environ["REZ_BUILD_INSTALL_PATH"])

    frompath = source_dir / "python"
    topath = target_dir / frompath.name
    LOGGER.debug(f"copying {frompath} to {topath} ...")
    distutils.dir_util.copy_tree(str(frompath), str(topath))

    frompath = source_dir / "README.md"
    topath = target_dir
    LOGGER.debug(f"copying {frompath} to {topath} ...")
    shutil.copy2(frompath, topath)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="{levelname: <7} | {asctime} [{name}] {message}",
        style="{",
        stream=sys.stdout,
    )
    build()
