import logging
import os
import shutil
from pathlib import Path
from typing import List


LOGGER = logging.getLogger(__name__)


def copy_build_files(files: List[Path]):
    """
    Copy file/directories from the source build directory to the build install path.

    Args:
        files:
            list of path relative to the build source directory to copy.
            can be files or directory
    """
    source_dir = Path(os.environ["REZ_BUILD_SOURCE_PATH"])
    target_dir = Path(os.environ["REZ_BUILD_INSTALL_PATH"])

    for file in files:
        if not file.is_absolute():
            file = source_dir / file
            file.absolute()

        LOGGER.debug(f"copying {file} to {target_dir} ...")
        if file.is_file():
            shutil.copy2(file, target_dir)
        else:
            shutil.copytree(
                file,
                target_dir / file.name,
            )
