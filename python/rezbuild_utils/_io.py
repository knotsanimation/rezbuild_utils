import logging
import os
import shutil
from pathlib import Path
from typing import List

from pythonning.filesystem import set_path_read_only
from pythonning.filesystem import copytree
from pythonning.progress import ProgressBar


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


def copytree_to_build(src_dir: Path, show_progress: bool = True):
    """
    Recursively copy the src_dir to the rez build directory.

    Args:
        src_dir: filesystem path to an existing directory
        show_progress: True to display a progress bar in the console.
    """
    target_dir = Path(os.environ["REZ_BUILD_INSTALL_PATH"])

    progress = None
    if show_progress:
        progress = ProgressBar(
            prefix="copying {bar_max} paths",
            suffix="[{bar_index:<2n}/{bar_max}] elapsed {elapsed_time:.2f}s",
        )

    def _callback(_path: Path, _index: int, _total: int):
        progress.set_progress(_index, new_maximum=_total)

    LOGGER.debug(f"copying {src_dir} to {target_dir} ...")
    if progress:
        progress.start()
        copytree(src_dir, target_dir, callback=_callback)
        progress.end()
    else:
        shutil.copytree(src_dir, target_dir)


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


def clear_build_dir():
    """
    Remove the content of the build installation directory.
    """
    build_dir = Path(os.environ["REZ_BUILD_INSTALL_PATH"])
    if not list(build_dir.glob("*")):
        return

    LOGGER.debug(f"removing {build_dir}")
    shutil.rmtree(build_dir, ignore_errors=True)
    LOGGER.debug(f"creating {build_dir} again")
    build_dir.mkdir()
