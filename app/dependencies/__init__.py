"""
Module for application dependencies in FastAPI.
"""
from .auth import get_current_user

from fastapi import Depends
from fastapi_limiter.depends import RateLimiter
from app.config import app_config

IS_NOT_TESTING = not app_config.is_testing

# set up dependency map
dependency_map = {
    "ping": [
        {"func": RateLimiter(times=5, seconds=1), "conditions": [IS_NOT_TESTING]}
    ],
    "upload_pdf_file": [
        {"func": RateLimiter(times=1, seconds=2), "conditions": [IS_NOT_TESTING]}
    ],
    "chat": [
        {"func": RateLimiter(times=1, seconds=2), "conditions": [IS_NOT_TESTING]}
    ],
    "get_all_documents": [
        {"func": RateLimiter(times=5, seconds=1), "conditions": [IS_NOT_TESTING]}
    ],
    "get_chat_history": [
        {"func": RateLimiter(times=5, seconds=1), "conditions": [IS_NOT_TESTING]}
    ],
    "delete_chat_history": [
        {"func": RateLimiter(times=5, seconds=1), "conditions": [IS_NOT_TESTING]}
    ],
}


def load_route_dependencies(key):
    """
    Dynamically loads route level dependencies based on mapped conditions.
    
    Args:
        key (str): The key to load from dependency map.
    
    Returns:
        list[Dependency]: A list of Dependencies.
    """
    endpoint = dependency_map.get(key)

    if not endpoint:
        return []

    deps = []
    for dependency in endpoint:
        if all(dependency["conditions"]):
            deps.append(Depends(dependency["func"]))

    return deps

