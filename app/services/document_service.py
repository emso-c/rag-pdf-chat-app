"""
Module for handling PDF file uploads and processing.

This module provides utilities for validating, uploading, and processing 
PDF files within the application. It includes functions to validate PDF 
file properties, manage file uploads, load documents, split text into 
chunks, and retrieve metadata associated with documents and their chunks. 
"""

import os
import shutil
from fastapi import UploadFile
from langchain_chroma import Chroma
from app.config import app_config
import fitz
import aiofiles
from langchain_community.document_loaders import DirectoryLoader, UnstructuredPDFLoader

from langchain.schema import Document
from app.models import DocumentMetadata, ChunkMetadata
from app.utils.hash_utils import generate_uuid_from_file
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.utils.logger import logger


async def validate_pdf(file: UploadFile) -> str:
    """Validates the PDF file content by checking file size, name length,
    file type, and attempts to open the file to check content. After checking,
    it creates a hard copy of the file inside the temp directory. If the file
    is cached already, it raises an error.

    Args:
        file (UploadFile): The uploaded PDF file to validate.

    Returns:
        str: An error message if validation fails, otherwise None.
    """

    if file.size == 0:
        return "Empty file"

    if file.size > app_config.max_file_size:
        return "File size exceeds the limit of 10 MB."
    
    if len(file.filename) > app_config.max_filename_length:
        return "File name is too long."

    if not file.filename.endswith(".pdf") or file.content_type != "application/pdf":
        return "Invalid file type. Only PDF files are allowed."

    # Attempt to open the PDF file and check page count
    try:
        temp_path = app_config.tmp_path / file.filename
        async with aiofiles.open(temp_path, "wb") as temp_file:
            content = await file.read()
            await temp_file.write(content)
            await temp_file.flush()

        pdf_document = fitz.open(temp_path)
        if not pdf_document.is_pdf:
            raise Exception("Not a valid PDF file.")
        if pdf_document.page_count == 0:
            return "Uploaded file is not a valid PDF file (no pages)."

    except Exception as e:
        logger.exception(e)
        if os.path.isfile(temp_path):
            os.remove(temp_path)
        return e
        return "Uploaded file is not a valid PDF file."

    return None


async def handle_file_upload(file: UploadFile) -> str:
    """Handles the upload of a PDF file stores it.

    Args:
        file (UploadFile): The uploaded PDF file.

    Returns:
        str: The UUID generated for the uploaded file.

    Raises:
        FileExistsError: If a file with the same UUID already exists.
    """
    temp_path = app_config.tmp_path / file.filename
    file_uuid = str(generate_uuid_from_file(temp_path))
    pdf_path = app_config.pdf_path / f"{file_uuid}.pdf"

    if os.path.isfile(pdf_path):
        os.remove(temp_path)
        raise FileExistsError(file_uuid)

    shutil.move(temp_path, pdf_path)
    # os.remove(temp_path)

    return file_uuid


def load_multiple_documents(from_dir: str):
    """Loads multiple PDF documents from a specified directory.

    Args:
        from_dir (str): The directory path from which to load PDF documents.

    Returns:
        list[Document]: A list of loaded documents.

    Raises:
        NotImplementedError: This function is not yet implemented.
    """
    # TODO implement logic
    raise NotImplementedError
    loader = DirectoryLoader(
        from_dir,
        glob="*.pdf",
        show_progress=True,
        use_multithreading=True,
        loader_cls=UnstructuredPDFLoader,
    )
    documents = loader.load()

    return documents


def load_document(file_path, file_uuid: str = ""):
    """Loads a single PDF document and attaches metadata.

    Args:
        file_path (str): The path to the PDF file to load.
        file_uuid (str, optional): The UUID associated with the document.
            Defaults to empty string. Required to store the document uuid
            metadata to the chunk cache.

    Returns:
        list[Document]: A list of loaded documents with metadata attached.
    """
    loader = UnstructuredPDFLoader(file_path, mode="single")
    documents = loader.load()

    with fitz.open(file_path) as pdf:
        num_pages = pdf.page_count
        filename = os.path.basename(file_path)

    # Attach metadata to each document
    for doc in documents:
        doc.metadata = DocumentMetadata(
            filename=filename, document_id=file_uuid, page_count=num_pages
        ).model_dump()
    return documents


def split_text(documents: list[Document]):
    """Splits the given documents into smaller text chunks.

    Args:
        documents (list[Document]): The documents to split.

    Returns:
        list[Document]: A list of text chunks.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)

    logger.debug(f"Split {len(documents)} documents into {len(chunks)} chunks.")
    return chunks


def list_all():
    """Lists all PDF document IDs stored in the specified path.

    Returns:
        list[str]: A list of document IDs (file names without .pdf extension).
    """
    res = []

    for path in os.listdir(app_config.pdf_path):
        if os.path.isfile(app_config.pdf_path / path):
            res.append(path.rstrip(".pdf"))  # only return ids

    return res


def get_document_metadata(vectorstore: Chroma, document_id: str) -> DocumentMetadata:
    """Retrieves metadata for a specific document from the vector store.

    Args:
        vectorstore (Chroma): The vector store from which to retrieve metadata.
        document_id (str): The ID of the document to retrieve metadata for.

    Returns:
        DocumentMetadata: The metadata associated with the specified document.
    """
    metadatas = vectorstore.get(
        include=["metadatas"], where={"document_id": document_id}
    )["metadatas"]

    # processed file should have at least 1 chunk
    metadata = metadatas[0]

    # pydantic automatically omits the "start_index" key, so no filter is needed
    return DocumentMetadata(**metadata)


def get_chunk_metadatas(vectorstore: Chroma, document_id: str) -> list[ChunkMetadata]:
    """Retrieves metadata for chunks associated with a specific document.

    Args:
        vectorstore (Chroma): The vector store to query for chunk metadata.
        document_id (str): The ID of the document for which to retrieve chunk metadata.

    Returns:
        list[ChunkMetadata]: A list of chunk metadata objects.
    """
    raw_metadatas = vectorstore.get(
        include=["metadatas"], where={"document_id": document_id}
    )["metadatas"]

    metadatas = []
    for metadata in raw_metadatas:
        metadatas.append(ChunkMetadata(**metadata))
    return metadatas
