"""
Module for handling routes for chat interactions with PDF documents.

This module defines API endpoints for chatting with PDF documents, utilizing 
Retrieval-Augmented Generation (RAG) to provide context-aware responses. 
It handles rate limiting, checks for existing documents, and caches question-answer 
pairs for efficient retrieval.
"""

import os
from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_user, load_route_dependencies
from app.exceptions import NoDocumentsException
from app.models import ChatResponse
from app.tasks import process_pdf
from app.services.rag_service import invoke_rag_chain
from app.services.qa_cache_service import load_qa, save_qa
from app.config import app_config
from app.models import ChatRequest
from app.utils.hash_utils import generate_uuid_from_file
from app.utils.logger import logger


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/{pdf_id}", dependencies=load_route_dependencies("chat"))
async def chat_with_pdf(
    pdf_id: str,
    chat_request: ChatRequest,
    current_user: str = Depends(get_current_user),
):
    """Handles chat interactions with a specified PDF document.

    Args:
        pdf_id (str): The ID of the PDF document to chat with.
        chat_request (ChatRequest): The request object containing the user's message.
        current_user (str, optional): The current user making the request. If not provided,
            default user will be assumed.

    Returns:
        ChatResponse: The AI-generated response to the user's query.

    Raises:
        HTTPException: If the provided PDF ID is invalid or if no documents are found.
    """
    pdf_id = pdf_id.strip()
    if not pdf_id:
        raise HTTPException(status_code=400, detail="Please provide an id.")

    if not os.path.isfile(app_config.pdf_path / f"{pdf_id}.pdf"):
        raise HTTPException(status_code=404)  # message is auto handled

    # check for cached response
    answer = await load_qa(pdf_id, chat_request.message)
    if answer:
        logger.info(f"QA cache hit for: {pdf_id}")
        return ChatResponse(response=answer)

    try:
        output = invoke_rag_chain(
            pdf_id=pdf_id, query=chat_request.message, user_id=current_user
        )
    except NoDocumentsException:
        # handle no documents issue, arises when documents are not properly saved to the vectorstore
        # for some reason (most likely NFS related issue, see the Dockerfile for the fix).
        logger.error(
            f"Could not find any vector data for '{pdf_id}'. attempting to reload the documents."
        )
        file_uuid = str(generate_uuid_from_file(app_config.pdf_path / f"{pdf_id}.pdf"))

        # causes bottleneck, but better than throwing an error.
        process_pdf(file_uuid)

        # run again
        output = invoke_rag_chain(
            pdf_id=pdf_id,
            query=chat_request.message,
        )

    # cache response
    # TODO check if the answer is not a refusal and only cache if so.
    await save_qa(pdf_id, chat_request.message, output.get("answer"))
    logger.info(f"Succesfully cached QA pair for {pdf_id}")
    return ChatResponse(response=output.get("answer"))
