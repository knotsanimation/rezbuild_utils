import logging
import os
import shutil
import tempfile
from pathlib import Path

from pythonning.web import download_file
from pythonning.filesystem import extract_zip
from pythonning.progress import ProgressBar


LOGGER = logging.getLogger(__name__)


class DownloadProgressBar(ProgressBar):
    """
    A progress bar for download, expressed in MB units.
    """

    byte_to_MB = 9.5367e-7

    def __init__(self):
        super().__init__(
            prefix="downloading",
            suffix="[{bar_index:<2.1f}MB/{bar_max:.1f}MB] elapsed {elapsed_time:.2f}s",
        )

    def show_progress(self, block_number, block_size, total_size):
        """
        To be used as callback during a download operation.

        Args:
            block_number: current block being downloaded, variable over time.
            block_size: size of each download block, static over time.
            total_size:
                total size of all the block to download, static over time.
                might not be provided which correspond to a value < 1.
        """
        if total_size < 1:
            self.update()
        else:
            downloaded = block_number * block_size
            self.set_progress(
                total_progress=downloaded * self.byte_to_MB,
                new_maximum=total_size * self.byte_to_MB,
            )


def download_and_install_build(
    url: str,
    install_dir_name: str,
    extract_if_zip: bool = True,
    use_cache: bool = False,
) -> Path:
    """
    Download the given url

    Can only be called during rez build.

    Args:
        url: url to download from, ensure it's a file.
        install_dir_name:
           name of the directory to put the extracted file in.
        extract_if_zip: if True automatically extract the file if it is a .zip
        use_cache: True to use the cached downloaded file. Will create it the first time.

    Returns:
        directory path where the files have been installed.
    """
    project_name = os.environ["REZ_BUILD_PROJECT_NAME"]
    project_version = os.environ["REZ_BUILD_PROJECT_VERSION"]
    project_install = Path(os.environ["REZ_BUILD_INSTALL_PATH"])

    prefix = f"{project_name}-{project_version}-"
    temp_folder = Path(tempfile.mkdtemp(prefix=prefix))

    download_path = temp_folder / "downloaded.zip"

    zip_install_dir = project_install / install_dir_name
    zip_install_dir.mkdir()

    try:
        progress = DownloadProgressBar()
        progress.start()
        LOGGER.info(f"downloading {url} to {download_path} ...")
        download_file(
            url,
            download_path,
            use_cache=use_cache,
            step_callback=progress.show_progress,
        )
        progress.end()

        # transfer from local machine to build target path
        LOGGER.info(f"copying {download_path.name} to {project_install} ...")
        shutil.copy2(download_path, zip_install_dir)

    except Exception as error:
        # XXX: hack as progress bar doesn't add a new line if not finished
        print("")
        raise
    finally:
        LOGGER.info(f"removing temporary directory {temp_folder}")
        shutil.rmtree(temp_folder)

    zip_path = zip_install_dir / download_path.name

    if extract_if_zip and zip_path.suffix == ".zip":
        LOGGER.info(f"extracting {zip_path} ...")
        extract_zip(zip_path)

    return zip_install_dir
