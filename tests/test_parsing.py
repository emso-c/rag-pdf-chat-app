import pytest
from app.utils.parse_utils import generate_safe_key

def test_generate_safe_key():
    chat_id = "chat1234"
    user_query = "Hello, World! This is a test query with invalid chars @#$%&*"
    
    expected_key = "app:chat1234:Hello_World_This_is_a_test_query_with_invalid_chars_"
    assert generate_safe_key(chat_id, user_query) == expected_key

def test_generate_safe_key_trims_query_length():
    chat_id = "chat123"
    user_query = "a" * 200
    
    expected_key = "app:chat123:" + "a" * 100  # Should trim to 100 chars
    assert generate_safe_key(chat_id, user_query) == expected_key
