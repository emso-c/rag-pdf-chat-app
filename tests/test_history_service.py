import json
import os
import shutil
import pytest
from app.config import app_config

from app.services.history_service import load_history, delete_history, save_history


@pytest.fixture(scope="function")
def setup_dirs(valid_history_path, valid_history_id):
    from app.main import init_dirs
    init_dirs(
        app_config.chroma_path,
        app_config.history_path,
        app_config.tmp_path,
        app_config.pdf_path,
        app_config.log_path,
    )
    os.system(f"cp {valid_history_path} {app_config.history_path}/{valid_history_id}")

    yield
    if os.path.exists(app_config.data_path):
        shutil.rmtree(app_config.data_path)


@pytest.fixture(scope="module")
def valid_history_id():
    return "8999a5f1-399c-2ac8-5fbb-ad6c50463f0e"

@pytest.fixture(scope="module")
def valid_history_path(valid_history_id):
    return os.path.join("tests/mock/history", valid_history_id)


def test_load_history(valid_history_id, setup_dirs):
    history = load_history(valid_history_id)

    assert isinstance(history, list)
    assert len(history) > 0
    assert history[0][0] == 'system'
    assert history[-1][1] == '{input}'

def test_load_user_history(valid_history_id, setup_dirs):
    mock_user_id = "user123"
    
    os.system(f"cp tests/mock/history/{mock_user_id}_{valid_history_id} {app_config.history_path}/{mock_user_id}_{valid_history_id}")
    
    history = load_history(valid_history_id, user_id=mock_user_id)
    default_history = load_history(valid_history_id)

    assert len(history) > 0
    assert history[0][1] == default_history[0][1]
    assert history[-2][1] != default_history[-2][1]

def test_save_history(setup_dirs):
    mock_history = [
        ("system", "text"),
        ("ai", "text"),
        ("human", "{input}"),
    ]
    mock_pdf_id = "test_history"
    save_history(mock_pdf_id, mock_history)

    assert os.path.isfile(os.path.join(app_config.history_path, mock_pdf_id))
    with open(os.path.join(app_config.history_path, mock_pdf_id), 'r') as f:
        data = json.load(f)
        assert isinstance(data[1], list)
        assert tuple(data[1]) == mock_history[1]