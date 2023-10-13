import distutils.dir_util
import logging
import os
import shutil
from pathlib import Path


LOGGER = logging.getLogger(__name__)


def copy_build_files(files: list[Path]):
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
            distutils.dir_util.copy_tree(
                str(file),
                str(target_dir / file.name),
            )
