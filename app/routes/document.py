"""
Module for handling routes for PDF file uploads and retrievals.

This module provides endpoints for uploading PDF files and listing all uploaded 
documents. It includes rate limiting to control the frequency of requests, ensuring 
efficient resource usage.
"""

from fastapi import APIRouter, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from app.dependencies import load_route_dependencies
from app.tasks import process_pdf_task
from app.services.document_service import (
    handle_file_upload,
    list_all,
    validate_pdf,
)

router = APIRouter(prefix="/pdf", tags=["pdf"])


@router.post(
    "/", status_code=202, dependencies=load_route_dependencies("upload_pdf_file")
)
async def upload_pdf_file(file: UploadFile):
    """Uploads a PDF file for processing.

    Validates the PDF file, handles the file upload, and initiates background processing
    through Celery for saving document chunks to the vector store for later use. If the
    file already exists, it returns the file uuid.

    Args:
        file (UploadFile): The PDF file to be uploaded.

    Raises:
        HTTPException: If the file is invalid, already exists, or processing fails.

    Returns:
        JSONResponse: A response indicating the status of the upload and processing task.
    """
    error_message = await validate_pdf(file)
    if error_message:
        raise HTTPException(status_code=422, detail=error_message)
    try:
        file_uuid = await handle_file_upload(file)
    except FileExistsError as e:
        raise HTTPException(
            status_code=409, detail=f"File already exists with the id: {e}"
        )

    task = process_pdf_task.delay(file_uuid)

    return JSONResponse(
        status_code=202,
        content={
            "pdf_id": file_uuid,
            "message": "Your document is being processed in the background.",
            "task_id": task.id,
            "monitor_url": "Not implemented",
        },
    )


@router.get("/all", dependencies=load_route_dependencies("get_all_documents"))
async def get_all_documents():
    """Retrieves a list of all uploaded PDF documents.

    Returns:
        list: A list of identifiers for all uploaded PDF documents.
    """
    return list_all()
