import logging
import os
import shutil
import zipfile
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


def extract_zip(zip_path: Path):
    """
    Exract the given zip archive content in the directory it is in.

    Args:
        zip_path: path to an existing zip file on disk.

    Returns:
        root directory the extracted file can be found at
    """
    extract_root = zip_path.parent
    with zipfile.ZipFile(zip_path, "r") as zip_file:
        zip_file.extractall(extract_root)
    zip_path.unlink()
    return extract_root


def move_directory_content(src_directory: Path, target_directory: Path):
    """
    Move (NOT copy) all the files and directories in the source to the target.

    Args:
        src_directory: filesystem path to an existing directory
        target_directory: filesystem path to an existing directory
    """
    for src_path in src_directory.glob("*"):
        src_path.rename(target_directory / src_path.name)
