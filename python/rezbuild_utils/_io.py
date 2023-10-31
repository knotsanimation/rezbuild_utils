import distutils.dir_util
import logging
import os
import shutil
import zipfile
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


def extract_zip(zip_path: Path, reference_file_expression: str):
    """
    Exract the given zip archive at its root, and move its content up at the root too.

    As an archive can have an arbitrary number of folder nested before finding the actual
    content, you can provide a reference_file_name to find where the content lives ::

        myarchive.zip
        myarchive/
            subfolder/
                bin/
                license.txt
                app.exe

    In the above example, you can use ``**/app.exe`` as reference file name.

    Args:
        zip_path: path to an existing zip file on disk.
        reference_file_expression: glob pattern that must match a file or a dir.

    Returns:
        root direcvtory the file can be found at
    """
    extract_root = zip_path.parent
    with zipfile.ZipFile(zip_path, "r") as zip_file:
        zip_file.extractall(extract_root)
    zip_path.unlink()

    reference_file = list(extract_root.glob(f"**/{reference_file_expression}"))[0]
    for file in reference_file.parent.glob("*"):
        file.rename(extract_root / file.name)
    # this will raise if not everything was moved
    reference_file.parent.rmdir()
    return extract_root
