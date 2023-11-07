import logging
import shutil
from pathlib import Path

import pytest

from rezbuild_utils._io import copy_build_files
from rezbuild_utils._io import move_directory_content


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


def test_move_directory_content(tmp_path: Path, data_root_dir: Path):
    src_copy_dir = data_root_dir / "movedircontent01"
    dst_copy_dir = tmp_path / "src"
    shutil.copytree(src_copy_dir, dst_copy_dir)

    test_src_dir = dst_copy_dir
    test_dst_dir = tmp_path / "dst"

    with pytest.raises(FileNotFoundError):
        move_directory_content(
            test_src_dir, test_dst_dir, exists_ok=False, recursive=False
        )

    test_dst_dir.mkdir()

    move_directory_content(test_src_dir, test_dst_dir, exists_ok=False, recursive=False)
    assert not len(list(test_src_dir.glob("*")))
    assert len(list(test_dst_dir.glob("*"))) == 2
    assert Path(test_dst_dir / "foo.py").exists()
    assert Path(test_dst_dir / "somedir").exists()
    assert Path(test_dst_dir / "somedir" / "file.py").exists()
    assert Path(test_dst_dir / "somedir" / "file.sh").exists()

    dst_copy_dir.rmdir()
    shutil.copytree(src_copy_dir, dst_copy_dir)
    with pytest.raises(FileExistsError):
        move_directory_content(
            test_src_dir, test_dst_dir, exists_ok=False, recursive=False
        )
    assert len(list(test_dst_dir.glob("*"))) == 2

    move_directory_content(test_src_dir, test_dst_dir, exists_ok=True, recursive=False)
    assert len(list(test_dst_dir.glob("*"))) == 2
    assert Path(test_dst_dir / "foo.py").exists()
    assert Path(test_dst_dir / "somedir").exists()
    assert len(list(Path(test_dst_dir / "somedir").glob("*"))) == 2
    assert Path(test_dst_dir / "somedir" / "file.py").exists()
    assert Path(test_dst_dir / "somedir" / "file.sh").exists()


def test_move_directory_content_recursive(tmp_path: Path, data_root_dir: Path):
    src_copy01_dir = data_root_dir / "movedircontent01"
    dst_copy01_dir = tmp_path / "src01"
    shutil.copytree(src_copy01_dir, dst_copy01_dir)

    src_copy02_dir = data_root_dir / "movedircontent02"
    dst_copy02_dir = tmp_path / "src02"
    shutil.copytree(src_copy02_dir, dst_copy02_dir)

    test_src_dir = dst_copy01_dir
    test_dst_dir = tmp_path / "dst"
    test_dst_dir.mkdir()

    move_directory_content(test_src_dir, test_dst_dir, exists_ok=False, recursive=False)

    test_src_dir = dst_copy02_dir
    move_directory_content(test_src_dir, test_dst_dir, exists_ok=True, recursive=False)
    assert len(list(test_dst_dir.glob("*"))) == 2
    assert Path(test_dst_dir / "foo.py").exists()
    assert Path(test_dst_dir / "somedir").exists()
    assert len(list(Path(test_dst_dir / "somedir").glob("*"))) == 2
    assert Path(test_dst_dir / "somedir" / "file.py").exists()
    assert Path(test_dst_dir / "somedir" / "file.sh").exists()

    # directory is not empty because we didnt use recursive=True
    with pytest.raises(OSError):
        dst_copy02_dir.rmdir()

    dst_copy03_dir = tmp_path / "src03"
    shutil.copytree(src_copy02_dir, dst_copy03_dir)
    test_src_dir = dst_copy03_dir
    move_directory_content(test_src_dir, test_dst_dir, exists_ok=True, recursive=True)
    assert len(list(test_dst_dir.glob("*"))) == 2
    assert Path(test_dst_dir / "foo.py").exists()
    assert Path(test_dst_dir / "somedir").exists()
    assert len(list(Path(test_dst_dir / "somedir").glob("*"))) == 3
    assert Path(test_dst_dir / "somedir" / "file.py").exists()
    assert Path(test_dst_dir / "somedir" / "file.sh").exists()
    assert Path(test_dst_dir / "somedir" / "NEWFILE").exists()
