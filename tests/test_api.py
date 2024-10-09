import os
import shutil
import pytest
from fastapi.testclient import TestClient
from app.config import app_config
from unittest.mock import patch


@pytest.fixture(scope="function")
def client():
    from app.main import app, init_dirs
    init_dirs(
        app_config.chroma_path,
        app_config.history_path,
        app_config.tmp_path,
        app_config.pdf_path,
        app_config.log_path,
    )
    yield TestClient(app)
    if os.path.exists(app_config.data_path):
        shutil.rmtree(app_config.data_path)

@pytest.fixture(scope="module")
def valid_pdf_path():
    return os.path.join("tests/mock/pdf", "bc466009-0aea-25e2-8e58-f5ccdc717e74.pdf")

@pytest.fixture(scope="module")
def valid_pdf_id():
    return "bc466009-0aea-25e2-8e58-f5ccdc717e74"

class TestAPISuite:
    
    @patch('app.tasks.process_pdf_task.delay')  # Adjust the import path as necessary
    def test_upload_same_pdf(self, mock_process_pdf_task, client: TestClient, valid_pdf_path):
        mock_process_pdf_task.return_value.id = 'mock_task_id'  # Mock task ID
        
        os.system(f"cp {valid_pdf_path} {app_config.pdf_path}")
        
        response = client.post("/v1/pdf/", files={"file": open(valid_pdf_path, "rb")})
        assert response.status_code == 409

    @patch('app.tasks.process_pdf_task.delay')  # Mock in all relevant tests
    def test_upload_invalid_pdf(self, mock_process_pdf_task, client: TestClient):
        mock_process_pdf_task.return_value.id = 'mock_task_id'
        
        response = client.post("/v1/pdf/", files={"file": ("invalid", b"Invalid file content")})
        assert response.status_code == 422

    @patch('app.tasks.process_pdf_task.delay')
    def test_upload_empty_pdf(self, mock_process_pdf_task, client: TestClient):
        mock_process_pdf_task.return_value.id = 'mock_task_id'
        
        response = client.post("/v1/pdf/", files={"file": (None, b"")})
        assert response.status_code == 422
    
    def test_get_all_documents(self, client: TestClient):
        response = client.get("/v1/pdf/all")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_chat_with_empty_message(self, client: TestClient, valid_pdf_id):
        response = client.post(f"/v1/chat/{valid_pdf_id}", json={"message": None})
        assert response.status_code == 422

    def test_get_chat_history(self, client: TestClient, valid_pdf_id):
        response = client.get(f"/v1/history/{valid_pdf_id}")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_delete_chat_history(self, client: TestClient, valid_pdf_path, valid_pdf_id):
        os.system(f"cp {valid_pdf_path} {app_config.history_path}/{valid_pdf_id}")
        
        response = client.delete(f"/v1/history/{valid_pdf_id}")
        assert response.status_code == 206
    
    @patch('app.tasks.process_pdf_task.delay') 
    def test_pdf_upload(self, mock_process_pdf_task, client: TestClient, valid_pdf_path):
        mock_process_pdf_task.return_value.id = 'mock_task_id'

        response = client.post("/v1/pdf/", files={"file": open(valid_pdf_path, "rb")})
        assert response.status_code == 202
        json_response = response.json()
        assert json_response['task_id'] == 'mock_task_id'
