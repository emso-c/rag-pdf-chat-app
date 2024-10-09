"""
Module for file level utilities.
"""

import pathlib
from app.utils.logger import logger


def init_dirs(*paths: tuple[pathlib.Path]) -> None:
    """Create directories if they do not already exist.

    Args:
        paths (tuple[pathlib.Path]): A variable number of `Path` objects representing
        the directories to create.

    Returns:
        None: This function does not return any value.
    """
    try:
        for path in paths:
            path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.exception(e)
