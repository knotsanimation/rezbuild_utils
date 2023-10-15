import hashlib
import logging
import os
import shutil
import tempfile
import urllib.request
from pathlib import Path
from typing import Optional

# TODO use progress package when available
from rez.vendor.progress.bar import ChargingBar

from ._io import extract_zip


LOGGER = logging.getLogger(__name__)

_DOWNLOAD_CACHE_ROOT = Path(tempfile.gettempdir()) / "rezbuild_utils-downloadcache"
_DISABLE_CACHE_ENV_VAR = "REZBUILD_UTILS_DISABLE_DOWNLOAD_CACHE"


def _hash_url(url: str) -> str:
    # we need a stable hash between python executions
    return hashlib.sha256(bytes(url, "utf-8")).hexdigest()


def _get_download_cache(source_url: str) -> Optional[Path]:
    """
    Find if the given url has already been cached.
    """
    if not _DOWNLOAD_CACHE_ROOT.exists():
        return None

    prefix = _hash_url(source_url)

    tempfolder: list[Path] = list(_DOWNLOAD_CACHE_ROOT.glob(f"{prefix}*"))
    if len(tempfolder) > 1:
        # should not happen but safety check
        LOGGER.warning(f"found multiple download cache for the same url: {tempfolder}")

    tempfolder: Optional[Path] = tempfolder[0] if tempfolder else None
    if not tempfolder:
        return None

    cache_file = list(tempfolder.glob("*"))
    # you must always have a single file inside, as defined in _create_cache
    return cache_file[0]


def _create_cache(file: Path, source_url: str) -> Path:
    """
    Create a cache for the provided file that has been downloaded from the given url.

    Path to the cached file is returned.
    """
    if not _DOWNLOAD_CACHE_ROOT.exists():
        LOGGER.debug(f"creating download cache root directory {_DOWNLOAD_CACHE_ROOT}")
        _DOWNLOAD_CACHE_ROOT.mkdir()

    build_name = os.getenv("REZ_BUILD_PROJECT_NAME", "none")
    build_version = os.getenv("REZ_BUILD_PROJECT_VERSION", "none")
    prefix = _hash_url(source_url)
    suffix = f"{build_name}-{build_version}"

    temp_folder = Path(
        tempfile.mkdtemp(
            prefix=prefix,
            suffix=suffix,
            dir=_DOWNLOAD_CACHE_ROOT,
        )
    )
    LOGGER.debug(f"creating copy in cache <{temp_folder}>")
    shutil.copy2(file, temp_folder)
    cache_file = temp_folder / file.name
    assert cache_file.exists(), cache_file
    return cache_file


def clear_download_cache():
    """
    Delete any file that might have been cached since multiple sessions.
    """
    if not _DOWNLOAD_CACHE_ROOT.exists():
        return
    LOGGER.info(f"removing download cache <{_DOWNLOAD_CACHE_ROOT}> ...")
    shutil.rmtree(_DOWNLOAD_CACHE_ROOT)


def download_file(url: str, target_file: Path, use_cache: bool = False):
    """
    Download a single file from the web at the given url and display download progress in terminal.

    You can cache the result when you know that you may call this function
    multiple time for the same url.

    Args:
        url: url to download from, ensure it's a file.
        target_file: filesytem path of the file to download
        use_cache: True to use the cached downloaded file. Will create it the first time.
    """
    if os.getenv(_DISABLE_CACHE_ENV_VAR):
        use_cache = False

    if use_cache:
        cache_file = _get_download_cache(url)
        if cache_file:
            LOGGER.info(f"cache found, copying {cache_file} to {target_file} ...")
            shutil.copy2(cache_file, target_file)
            return

    progress = ChargingBar("downloading")

    def _show_progress(block_number, block_size, total_size):
        progress.max = total_size
        downloaded = block_number * block_size
        progress.goto(downloaded)

    progress.start()
    urllib.request.urlretrieve(url, target_file, reporthook=_show_progress)
    progress.finish()

    if use_cache:
        LOGGER.info(f"creating cache from url {url} downloaded as {target_file} ...")
        cache_file = _create_cache(target_file, url)
        LOGGER.debug(f"cache file created at {cache_file}")


def download_and_install_build(
    url: str,
    extract_reference_file_name: Optional[str],
    use_cache: bool = False,
) -> Path:
    """
    Download the given url

    Can only be called during rez build.

    Args:
        url: url to download from, ensure it's a file.
        extract_reference_file_name:
            None if the file is not a zip that need extraction.
            Else a file name contained in the zip file so its content can be moved
            to the installation root.
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

    try:
        LOGGER.info(f"downloading {url} to {download_path} ...")
        download_file(url, download_path, use_cache=use_cache)

        # transfer from local machine to build target path
        LOGGER.info(f"copying {download_path.name} to {project_install} ...")
        shutil.copy2(download_path, project_install)

    except Exception as error:
        # XXX: hack as progress bar doesn't add a new line if not finished
        print("")
        raise
    finally:
        LOGGER.info(f"removing temporary directory {temp_folder}")
        shutil.rmtree(temp_folder)

    zip_path = project_install / download_path.name

    if extract_reference_file_name:
        LOGGER.info(f"extracting {zip_path} ...")
        extract_zip(zip_path, reference_file_name=extract_reference_file_name)

    return project_install
