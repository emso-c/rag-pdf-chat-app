import pytest
from unittest.mock import patch, MagicMock
from langchain.schema import Document
from app.services.vector_service import save_vectorstore, load_vectorstore

@pytest.fixture
def mock_embeddings():
    """Fixture to create a mock embeddings object."""
    return MagicMock()

@pytest.fixture
def mock_documents():
    """Fixture to create a list of mock Document objects."""
    return [Document(page_content="Test content", metadata={"key": "value"})]

@pytest.fixture
def mock_chroma():
    """Fixture to mock the Chroma class."""
    with patch('app.services.vector_service.Chroma') as mock:
        yield mock

def test_save_vectorstore(mock_chroma, mock_documents, mock_embeddings):
    """Test the save_vectorstore function."""
    col_name = "test_collection"
    dir_path = "tests/mock/vectorstore"

    mock_instance = MagicMock()
    mock_chroma.from_documents.return_value = mock_instance

    result = save_vectorstore(col_name, mock_documents, mock_embeddings, dir_path)

    mock_chroma.from_documents.assert_called_once_with(
        collection_name=col_name,
        documents=mock_documents,
        embedding=mock_embeddings,
        persist_directory=str(dir_path),
    )
    assert result == mock_instance

def test_load_vectorstore(mock_chroma, mock_embeddings):
    """Test the load_vectorstore function."""
    col_name = "test_collection"
    from_dir = "tests/mock/vectorstore"

    mock_instance = MagicMock()
    mock_chroma.return_value = mock_instance

    result = load_vectorstore(col_name, from_dir, mock_embeddings)

    mock_chroma.assert_called_once_with(
        collection_name=col_name,
        embedding_function=mock_embeddings,
        persist_directory=str(from_dir),
    )
    assert result == mock_instance
