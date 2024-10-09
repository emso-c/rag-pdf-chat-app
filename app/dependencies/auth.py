"""
Module for authentication dependencies in FastAPI.
"""

from fastapi import Request


def get_current_user(request: Request):
    """Retrieve the current user's token from the request state.

    Args:
        request (Request): The incoming request object.

    Returns:
        str: The token associated with the current user.
    """
    return request.state.token
