import logging
from pathlib import Path

import pytest

from rezbuild_utils._io import copy_build_files


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
