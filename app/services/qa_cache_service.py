"""
Module for managing query-answer pairs in Redis.

This module provides functionality to cache and load query-answer 
pairs associated with PDF documents with an expire based approach.
It uses a Redis database for storage.
"""

from typing import Optional
from app.connection import redis_connection as default_connection, redis

from app.config import app_config
from app.utils.parse_utils import generate_safe_key


async def save_qa(pdf_id: str, query: str, answer: str, redis_conn: redis.Redis|None = None) -> None:
    """Saves a query-answer pair in Redis with an expiry time.

    Args:
        pdf_id (str): The ID of the PDF document associated with the query.
        query (str): The query to save.
        answer (str): The answer corresponding to the query.
        redis_conn (redis.Redis|None): Optional redis connection

    Returns:
        None: This function does not return any value.
    """
    connection = redis_conn or default_connection
    key = generate_safe_key(pdf_id, query)
    await connection.set(key, answer, ex=app_config.cache_expiry)


async def load_qa(pdf_id: str, query: str, redis_conn: redis.Redis|None = None) -> Optional[str]:
    """Loads a query-answer pair from Redis, prolonging expiry on hit.

    Args:
        pdf_id (str): The ID of the PDF document associated with the query.
        query (str): The query for which to retrieve the answer.
        redis_conn (redis.Redis|None): Optional redis connection

    Returns:
        Optional[str]: The answer corresponding to the query, or None if
        no answer is found.
    """
    connection = redis_conn or default_connection
    
    key = generate_safe_key(pdf_id, query)
    answer = await connection.get(key)

    if answer is not None:
        # Prolong expiry on hit
        await connection.expire(key, app_config.cache_expiry)

    return answer
