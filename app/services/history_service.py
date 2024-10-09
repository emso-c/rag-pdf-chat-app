"""
Module for managing chat history for the PDF documents.

This module provides functions to load, save, and delete chat history 
associated with specific PDF documents and the user ID. If no user
ID is provided, default user will be assumed. The storage of chat history
is handled in JSON format.
"""

import os
import json
from pathlib import Path
from typing import Optional, List, Tuple
from app.config import app_config
from app.utils.logger import logger


def load_history(pdf_id: str, user_id: str = None) -> List[Optional[Tuple]]:
    """Loads the chat history for a given PDF document and user.

    Args:
        pdf_id (str): The ID of the PDF document for which to load history.
        user_id (str, optional): The ID of the user associated with the history.

    Returns:
        List[Optional[Tuple]]: A list of tuples representing the chat history,
        or an empty list if no history exists.
    """
    history_path = _get_history_path(pdf_id, user_id)
    logger.debug(f"attempting to load the chat history: {history_path}")

    try:
        with open(history_path, "r") as file:
            content = json.load(file)

            if not (content or len(content) > 0):
                return []

            # Convert lists to tuples
            content = [tuple(entry) for entry in content]

            # Update the system prompt if necessary
            old_system_prompt = content[0][1]
            system_prompt = app_config.default_history[0][1]

            if old_system_prompt != system_prompt:
                # Can not update tuples, replace instead
                content[0] = tuple(app_config.default_history[0])
                logger.debug("system prompt has been updated")

            return content
    except FileNotFoundError:
        logger.warning(f"Chat history file not found: {history_path}")
        return []
    except Exception as e:
        logger.error(
            f"There was an error loading the chat history. {e.__class__.__name__}: {e}"
        )
        raise Exception(e)


def save_history(pdf_id: str, history: List[Tuple], user_id: str = None):
    """Saves the chat history for a given PDF document and user.

    Args:
        pdf_id (str): The ID of the PDF document for which to save history.
        history (List[Tuple]): The chat history to save.
        user_id (str, optional): The ID of the user associated with the history.

    Returns:
        None: This function does not return any value.
    """
    history_path = _get_history_path(pdf_id, user_id)
    logger.debug(f"saving the chat history to: {history_path}")

    # Convert tuples back to lists for JSON serialization
    history_as_lists = [list(entry) for entry in history]
    with open(history_path, "w") as file:
        json.dump(history_as_lists, file)


def delete_history(pdf_id: str, user_id: str = None):
    """Deletes the chat history for a given PDF document and user.

    Args:
        pdf_id (str): The ID of the PDF document for which to delete history.
        user_id (str, optional): The ID of the user associated with the history.

    Returns:
        None: This function does not return any value.
    """
    history_path = _get_history_path(pdf_id, user_id)

    if os.path.isfile(history_path):
        logger.debug(f"deleting the chat history from: {history_path}")
        os.remove(history_path)


def _get_history_path(pdf_id: str, user_id: str = None) -> str:
    """Constructs the file path for the chat history. Default
    path format is {user_id}_{file_uuid}. If user ID is not provided,
    assumes default history: {file_uuid}

    Args:
        pdf_id (str): The ID of the PDF document.
        user_id (str, optional): The ID of the user associated with the history.

    Returns:
        str: The file path for the chat history.
    """
    file_prefix = f"{user_id}_" if user_id else ""
    return app_config.history_path / Path(file_prefix + pdf_id)
