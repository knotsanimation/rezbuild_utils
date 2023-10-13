import os

import rezbuild_utils
from rezbuild_utils._download import download_file
from rezbuild_utils._download import _DOWNLOAD_CACHE_ROOT


def _is_cache_empty() -> bool:
    if not _DOWNLOAD_CACHE_ROOT.exists():
        return True
    return not next(os.scandir(_DOWNLOAD_CACHE_ROOT), None)


def test_download_file(tmp_path):
    # we unfortunately need to clear the cache before running the tests
    rezbuild_utils.clear_download_cache()
    assert _is_cache_empty()

    target_file = tmp_path / "githubavatar1"
    assert not target_file.exists()
    assert _is_cache_empty()
    download_file(
        # one day those tests will probably fail because github will change their url :^)
        "https://avatars.githubusercontent.com/u/64362465",
        target_file,
        use_cache=False,
    )
    assert target_file.exists()
    assert _is_cache_empty()

    target_file = tmp_path / "githubavatar2"
    assert not target_file.exists()
    download_file(
        "https://avatars.githubusercontent.com/u/64362465",
        target_file,
        use_cache=True,
    )
    assert target_file.exists()
    assert not _is_cache_empty()

    target_file = tmp_path / "githubavatar3"
    assert not target_file.exists()
    download_file(
        "https://avatars.githubusercontent.com/u/64362465",
        target_file,
        use_cache=True,
    )
    assert target_file.exists()
    assert not _is_cache_empty()

    rezbuild_utils.clear_download_cache()
    assert _is_cache_empty()
