import os
import pathlib
import pytest
from app.utils.file_utils import init_dirs

@pytest.fixture(scope="function")
def temp_dir():
    temp_path = pathlib.Path("tests/temp")
    yield temp_path
    if temp_path.exists():
        for item in temp_path.iterdir():
            item.rmdir()
        temp_path.rmdir()

def test_init_dirs_creates_directories(temp_dir):
    dir1 = temp_dir / "dir1"
    dir2 = temp_dir / "dir2"
    
    init_dirs(dir1, dir2)
    
    assert dir1.exists()
    assert dir2.exists()

def test_init_dirs_existing_directories(temp_dir):
    existing_dir = temp_dir / "existing_dir"
    existing_dir.mkdir(parents=True, exist_ok=True)

    init_dirs(existing_dir)

    # Ensure it doesn't raise any errors and exists
    assert existing_dir.exists()
