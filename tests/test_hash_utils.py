import os
import uuid
import pytest
from app.utils.hash_utils import get_file_hash, generate_uuid_from_file 

@pytest.fixture(scope="function")
def sample_file():
    file_path = "tests/test_file.pdf"
    with open(file_path, 'w') as f:
        f.write("test")

    yield str(file_path)
    
    os.remove(file_path)

@pytest.fixture(scope="function")
def sample_file_2():
    file_path = "tests/test_file_2.pdf"
    with open(file_path, 'w') as f:
        f.write("test")

    yield str(file_path)
    
    os.remove(file_path)

def test_get_file_hash(sample_file):
    expected_hash = b'\x9f\x86\xd0\x81\x88L}e\x9a/\xea\xa0\xc5Z\xd0\x15\xa3\xbfO\x1b+\x0b\x82,\xd1]l\x15\xb0\xf0\n\x08'
    assert get_file_hash(sample_file) == expected_hash

def test_generate_uuid_from_file(sample_file, sample_file_2):
    file_uuid_1 = generate_uuid_from_file(sample_file)
    file_uuid_2 = generate_uuid_from_file(sample_file)
    
    assert isinstance(file_uuid_1, uuid.UUID)
    assert isinstance(file_uuid_1, uuid.UUID)
    assert file_uuid_1 == file_uuid_2
