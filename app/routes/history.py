"""
Module handling routes for managing chat history related to PDF documents.

This module provides endpoints for retrieving and deleting chat history associated 
with specific PDF documents.
"""

from fastapi import APIRouter, Depends, Response
from app.dependencies import get_current_user, load_route_dependencies
from app.config import app_config
from app.services.history_service import delete_history, load_history


router = APIRouter(prefix="/history", tags=["history"])


@router.get("/{pdf_id}", dependencies=load_route_dependencies("get_chat_history"))
async def get_chat_history(pdf_id: str, current_user: str = Depends(get_current_user)):
    """Retrieves chat history for a specified PDF document.

    Args:
        pdf_id (str): The ID of the PDF document whose history is to be retrieved.
        current_user (str, optional): The current user making the request.

    Returns:
        list: The chat history for the specified PDF document, excluding system messages.
    """

    history = load_history(pdf_id, current_user) or app_config.default_history
    return history[1:-1]  # only return the relevant fields


@router.delete("/{pdf_id}", dependencies=load_route_dependencies("delete_chat_history"))
async def delete_chat_history(
    pdf_id: str, current_user: str = Depends(get_current_user)
):
    """Deletes chat history for a specified PDF document.

    Args:
        pdf_id (str): The ID of the PDF document whose history is to be deleted.
        current_user (str, optional): The current user making the request.

    Returns:
        Response: HTTP response indicating the status of the deletion.
    """
    delete_history(pdf_id, current_user)
    return Response(status_code=206)
