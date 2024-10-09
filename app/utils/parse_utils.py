"""
Module for handling parsing logics.
"""

import re


def generate_safe_key(chat_id: str, user_query: str) -> str:
    """Generates a safe Redis key based on the chat ID and user query.

    This function normalizes whitespace in the user query, sanitizes it
    by removing unwanted characters, limits the length of both the
    chat ID and user query, and constructs a formatted Redis key.

    Args:
        chat_id (str): The unique identifier for the chat, limited to 50 characters.
        user_query (str): The user's query, which is sanitized and limited to 100 characters.

    Returns:
        str: A formatted Redis key in the form of "app:{chat_id}:{user_query}".
    """

    # Normalize whitespace
    user_query = " ".join(user_query.split()).strip().replace(" ", "_")

    # Sanitize user_query: Remove unwanted characters and limit length
    user_query = re.sub(
        r"[^a-zA-Z0-9\s:_-]", "", user_query
    )  # Replace invalid chars with '_'
    user_query = user_query[:100]  # Limit user query length

    # Limit chat_id length if necessary
    chat_id = chat_id[:50]  # Limit chat_id length

    # Create the Redis key
    redis_key = f"app:{chat_id}:{user_query}"

    return redis_key
