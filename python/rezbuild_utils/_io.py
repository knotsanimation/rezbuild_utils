import logging
import os
import shutil
from pathlib import Path
from typing import List

from pythonning.filesystem import set_path_read_only


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


def set_installed_path_read_only() -> list[Path]:
    """
    Set recursively all path in the rez build install dir to read-only (including directories).

    Returns:
        list of path that have been set to read-only
    """
    install_dir = Path(os.environ["REZ_BUILD_INSTALL_PATH"])
    installed_files = list(install_dir.rglob("*"))

    for file_path in installed_files:
        set_path_read_only(file_path)

    return installed_files
