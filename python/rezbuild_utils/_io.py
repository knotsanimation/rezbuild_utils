import logging
import os
import shutil
from pathlib import Path
from typing import List
from typing import Optional

from pythonning.filesystem import set_path_read_only
from pythonning.filesystem import copytree
from pythonning.filesystem import copyfile
from pythonning.filesystem import extract_zip
from pythonning.progress import ProgressBar


LOGGER = logging.getLogger(__name__)

byte_to_MB = 9.5367e-7


def copy_build_files(files: List[Path], target_directory: Optional[list[str]] = None):
    """
    Copy individual file/directories from the source build directory to the build install path.

    Each path in file is copied individually so hierachy are not preserved.

    Examples:

        The following::

            (file=["./python/myModule.py"], sub_directories=None)

        correspond to::

            {REZ_BUILD_SOURCE_PATH}/python/myModule.py > {REZ_BUILD_INSTALL_PATH}/myModule.py

        The following::

            (file=["./python/myModule.py"], sub_directories=["src", "demo"])

        correspond to::

            {REZ_BUILD_SOURCE_PATH}/python/myModule.py > {REZ_BUILD_INSTALL_PATH}/src/demo/myModule.py


    Args:
        files:
            list of absolute paths or paths relative to the build source directory, to copy.
            can be files or directory
        target_directory:
            destination directory to copy the file to relative to the build directory.
            Expressed as list of directory names combined to a single path where the root is the left-most
            name in the list.
    """
    source_dir = Path(os.environ["REZ_BUILD_SOURCE_PATH"])
    target_dir = Path(os.environ["REZ_BUILD_INSTALL_PATH"])
    if target_directory:
        target_dir = target_dir.joinpath(*target_directory)
        os.makedirs(target_dir, exist_ok=True)

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


def copy_and_install_zip(
    zip_path: Path,
    dir_name: Optional[str],
    show_progress: bool = True,
    use_cache: bool = True,
) -> Path:
    """
    Copy the given zip to the build directory and extract it to the given directory name.

    A progress bar can be displayed for the copy operation (and not the extraction).

    Args:
        zip_path: filesystem path to an existing .zip file
        dir_name:
            name of the directory to extract the zip content in.
            If None just extracts at the root of the build dir.
        show_progress: True to show a progress bar in the console.
        use_cache:
            True to cache the source zip locally. This might reduce build time
            when the zip is stored on slow network drives and you need to trigger
            the build multiple times in a short period.


    Returns:
        the path of the directory that contain the extracted zip content
        filesystem path to an existing directory.
    """
    build_dir = Path(os.environ["REZ_BUILD_INSTALL_PATH"])
    target_dir = build_dir / dir_name if dir_name else build_dir
    if not target_dir.exists():
        target_dir.mkdir()

    target_path = target_dir / zip_path.name

    progress = None
    if show_progress:
        progress = ProgressBar(
            prefix=f"copying {zip_path.name}",
            suffix="[{bar_index:.2f}MB/{bar_max:.2f}MB] elapsed {elapsed_time:.2f}s",
        )

    def _callback(_chunk: int, _chunk_size: int, _total: int):
        if show_progress:
            progress.set_progress(_chunk * byte_to_MB, new_maximum=_total * byte_to_MB)

    LOGGER.info(f"copying <{zip_path}> to <{target_path}> ...")
    progress.start() if progress else None
    copyfile(
        zip_path,
        target_path,
        callback=_callback,
        use_cache=use_cache,
    )
    progress.end() if progress else None

    LOGGER.info(f"extracting <{target_path}>")
    extract_zip(target_path, remove_zip=True)
    return target_dir
