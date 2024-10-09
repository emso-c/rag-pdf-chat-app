"""
Module for initiating the Celery tasks, using a Redis broker.
"""

import os
from typing import Any
from celery import Celery
from app.config import env_config, app_config
from app.utils.logger import logger
from app.services.document_service import load_document, split_text
from app.services.embeddings import gemini_embeddings
from app.services.vector_service import save_vectorstore

REDIS_URL = str(env_config.redis_url)

app = Celery(
    "worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
)
if app_config.is_testing:
    app.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
    )


def process_pdf(file_uuid: str, bind: Any = None) -> None:
    """Processes a PDF file by loading it, splitting it into chunks,
    and saving those chunks to a vector store. Can bind with celery
    tasks using the bind parameter.

    Args:
        file_uuid (str): The unique identifier for the PDF file.
        bind (Any, optional): An optional Celery context,
            which provides request-specific data. Defaults to None,
            which runs the task in synchoronous standalone mode.

    Raises:
        Exception: Raises an exception if an error occurs during
        processing or saving to the vector store.
    """
    task_str = "standalone"
    if bind:
        task_str = f"task-{bind.request.id}"

    logger.info(f"{task_str}: processing document - {file_uuid}")
    pdf_path = app_config.pdf_path / f"{file_uuid}.pdf"
    
    if not os.path.exists(pdf_path):
        raise FileNotFoundError

    try:
        # prepare document chunks
        docs = load_document(pdf_path, file_uuid)
        chunks = split_text(docs)

        # save chunks to vector store
        save_vectorstore(
            col_name=file_uuid,
            documents=chunks,
            embeddings=gemini_embeddings,
            dir_path=app_config.chroma_path,
        )
        logger.info(f"{task_str}: saved '{file_uuid}' to vectorstore")

    except Exception as e:
        # intercept exception to log and roll-back
        logger.error(f"{task_str}: error processing the document, removing the file...")
        if os.path.isfile(pdf_path):
            os.remove(pdf_path)

        # reraise the exception
        raise e


@app.task(bind=True)
def process_pdf_task(self, file_uuid: str):
    """Celery task wrapper for processing a PDF file.

    Args:
        self: The current task instance.
        file_uuid (str): The unique identifier for the PDF file.
    """
    process_pdf(file_uuid, bind=self)
