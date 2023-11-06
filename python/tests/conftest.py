from pathlib import Path

import pytest

DATA_ROOT_DIR = Path(__file__).parent / "data"


@pytest.fixture
def data_root_dir() -> Path:
    return DATA_ROOT_DIR
