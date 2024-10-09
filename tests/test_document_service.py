import os
import shutil
from fastapi import UploadFile
import pytest
from app.services.document_service import validate_pdf, handle_file_upload, load_document, split_text, list_all
from app.config import app_config

pytest_plugins = ('pytest_asyncio',)


@pytest.fixture(scope="function")
def setup_dirs(valid_pdf_path, valid_pdf_id):
    from app.main import app, init_dirs
    init_dirs(
        app_config.chroma_path,
        app_config.history_path,
        app_config.tmp_path,
        app_config.pdf_path,
        app_config.log_path,
    )
    os.system(f"cp {valid_pdf_path} {app_config.tmp_path}/{valid_pdf_id}.pdf")

    yield
    if os.path.exists(app_config.data_path):
        shutil.rmtree(app_config.data_path)


@pytest.fixture(scope="module")
def valid_pdf_path():
    return os.path.join("tests/mock/pdf", "4a564e8b-bd2c-52e5-3a81-16845a19e107.pdf")


@pytest.fixture(scope="module")
def valid_pdf_id():
    return "4a564e8b-bd2c-52e5-3a81-16845a19e107"


@pytest.mark.asyncio
async def test_validate_pdf_success(valid_pdf_path, setup_dirs):
    file = UploadFile(
        filename='test.pdf',
        file=open(valid_pdf_path, 'rb'),
        size=1,
        headers={'content-type': 'application/pdf'}
    )
    
    error = await validate_pdf(file)
    assert error is None


@pytest.mark.asyncio
async def test_validate_pdf_invalid_filename(valid_pdf_path, setup_dirs):
    file = UploadFile(
        filename='test',
        file=open(valid_pdf_path, 'rb'),
        size=1,
        headers={'content-type': 'application/pdf'}
    )
    
    error = await validate_pdf(file)
    assert error == 'Invalid file type. Only PDF files are allowed.'


@pytest.mark.asyncio
async def test_validate_pdf_empty_file(valid_pdf_path, setup_dirs):
    file = UploadFile(
        filename='test.pdf',
        file=open(valid_pdf_path, 'rb'),
        size=0,
        headers={'content-type': 'application/pdf'}
    )
    
    error = await validate_pdf(file)
    assert error == 'Empty file'


@pytest.mark.asyncio
async def test_validate_pdf_invalid_content_type(valid_pdf_path, setup_dirs):
    file = UploadFile(
        filename='test.pdf',
        file=open(valid_pdf_path, 'rb'),
        size=1,
        headers={'content-type': 'application/json'}
    )
    
    error = await validate_pdf(file)
    assert error == 'Invalid file type. Only PDF files are allowed.'


@pytest.mark.asyncio
async def test_validate_pdf_exceeds_size_limit(valid_pdf_path, setup_dirs):
    file = UploadFile(
        filename='test.pdf',
        file=open(valid_pdf_path, 'rb'),
        size=100000000,
        headers={'content-type': 'application/pdf'}
    )
    
    error = await validate_pdf(file)
    assert error == 'File size exceeds the limit of 10 MB.'


@pytest.mark.asyncio
async def test_upload_file(valid_pdf_path, valid_pdf_id, setup_dirs):
    file = UploadFile(
        filename=f'{valid_pdf_id}.pdf',
        file=open(valid_pdf_path, 'rb'),
        size=1,
        headers={'content-type': 'application/pdf'}
    )
    
    res = await handle_file_upload(file)
    
    assert res == valid_pdf_id

@pytest.mark.asyncio
async def test_upload_same_file(valid_pdf_path, valid_pdf_id, setup_dirs):
    os.system(f"cp {valid_pdf_path} {app_config.pdf_path}/{valid_pdf_id}.pdf")
    file = UploadFile(
        filename=f'{valid_pdf_id}.pdf',
        file=open(valid_pdf_path, 'rb'),
        size=1,
        headers={'content-type': 'application/pdf'}
    )
    
    with pytest.raises(FileExistsError):
        await handle_file_upload(file)


def test_load_document(valid_pdf_path, valid_pdf_id, setup_dirs):
    uploaded_pdf_path = f"{app_config.pdf_path}/{valid_pdf_id}.pdf"
    os.system(f"cp {valid_pdf_path} {uploaded_pdf_path}")
    
    docs = load_document(file_path=uploaded_pdf_path)
    
    assert docs[0].metadata['filename'] == f'{valid_pdf_id}.pdf'
    assert docs[0].metadata['page_count'] == 3


def test_split_text():
    from langchain.schema import Document
    
    docs = [Document('longdocument'*1000)]
    chunks = split_text(docs)
    
    assert len(chunks) == 15


def test_list_all(valid_pdf_path, valid_pdf_id, setup_dirs):
    uploaded_pdf_path = f"{app_config.pdf_path}/{valid_pdf_id}.pdf"
    os.system(f"cp {valid_pdf_path} {uploaded_pdf_path}")
    
    ids = list_all()
    assert ids[0] == valid_pdf_id
    assert len(ids) == 1

 