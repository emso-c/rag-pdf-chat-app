import os
import shutil
import pytest
from unittest.mock import patch
from app.tasks import process_pdf_task
from app.config import app_config
from app.main import init_dirs

@pytest.fixture(scope="function")
def setup_pdf_file(valid_pdf_path):
    init_dirs(
        app_config.chroma_path,
        app_config.history_path,
        app_config.tmp_path,
        app_config.pdf_path,
        app_config.log_path,
    )
    test_pdf_path = os.path.join(app_config.pdf_path, os.path.basename(valid_pdf_path))
    os.system(f"cp {valid_pdf_path} {test_pdf_path}")
    yield test_pdf_path
    if os.path.exists(app_config.data_path):
        shutil.rmtree(app_config.data_path)

@pytest.fixture(scope="module")
def valid_pdf_path():
    return os.path.join("tests/mock/pdf", "4a564e8b-bd2c-52e5-3a81-16845a19e107.pdf")

@pytest.fixture(scope="module")
def valid_pdf_id():
    return "4a564e8b-bd2c-52e5-3a81-16845a19e107"

class TestCeleryTasks:

    @patch('app.tasks.process_pdf') 
    def test_process_pdf_task(self, mock_process_pdf, valid_pdf_id, setup_pdf_file):
        mock_process_pdf.return_value = None
        
        result = process_pdf_task.apply(args=[valid_pdf_id])

        result.wait()

        assert result.successful()
        assert result.result is None  # No return value expected

        invalid_pdf_id = "invalid-pdf-id"
        
        mock_process_pdf.side_effect = FileNotFoundError  # Simulate FileNotFoundError for an invalid ID
        
        with pytest.raises(FileNotFoundError):
            result = process_pdf_task.apply(args=[invalid_pdf_id])
            result.wait()

            assert not result.successful()
