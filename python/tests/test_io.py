import logging
import shutil
from pathlib import Path

import pytest

from rezbuild_utils._io import copy_build_files
from rezbuild_utils._io import set_installed_path_read_only


LOGGER = logging.getLogger(__name__)


def test_copy_build_files(tmp_path: Path, data_root_dir: Path, monkeypatch):
    build_dir = tmp_path / "build"
    build_dir.mkdir()
    monkeypatch.setenv("REZ_BUILD_SOURCE_PATH", str(data_root_dir / "copybuildfiles01"))
    monkeypatch.setenv("REZ_BUILD_INSTALL_PATH", str(build_dir))

    copy_build_files([Path("./somedir/"), Path("./foo.py")])

    assert Path(build_dir / "somedir").exists()
    assert Path(build_dir / "somedir" / "file.py").exists()
    assert Path(build_dir / "foo.py").exists()

    with pytest.raises(FileExistsError):
        copy_build_files([Path("./somedir/"), Path("./foo.py")])


def test_set_installed_files_read_only(
    tmp_path: Path,
    data_root_dir: Path,
    monkeypatch,
):
    install_dir = tmp_path / "install"

    monkeypatch.setenv("REZ_BUILD_INSTALL_PATH", str(install_dir))

    src_dir = data_root_dir / "setreadonly01"
    shutil.copytree(src_dir, install_dir)

    set_installed_path_read_only()

    test_file1 = install_dir / "foo.py"
    with pytest.raises(PermissionError):
        test_file1.unlink()

    test_file2 = install_dir / "somedir" / "file.py"
    with pytest.raises(PermissionError):
        test_file2.unlink()
