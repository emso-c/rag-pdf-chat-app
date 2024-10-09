import pytest
from unittest.mock import AsyncMock, patch
from app.services.qa_cache_service import save_qa, load_qa
from app.config import app_config

# Test data
pdf_id = "test_pdf"
query = "What is the test?"
formatted_query = "what_is_this_test"
answer = "This is a test answer."
expected_key = f"app:{pdf_id}:{formatted_query}"

@pytest.mark.asyncio
@patch('app.services.qa_cache_service.generate_safe_key')
async def test_save_qa(mock_generate_safe_key):
    mock_generate_safe_key.return_value = expected_key
    mock_redis = AsyncMock()
    
    await save_qa(pdf_id, query, answer, redis_conn=mock_redis)

    mock_generate_safe_key.assert_called_once_with(pdf_id, query)
    mock_redis.set.assert_called_once_with(expected_key, answer, ex=app_config.cache_expiry)

@pytest.mark.asyncio
@patch('app.services.qa_cache_service.generate_safe_key')
async def test_load_qa_hit(mock_generate_safe_key):
    mock_generate_safe_key.return_value = expected_key
    mock_redis = AsyncMock()
    mock_redis.get.return_value = answer
    
    result = await load_qa(pdf_id, query, redis_conn=mock_redis)

    mock_generate_safe_key.assert_called_once_with(pdf_id, query)
    mock_redis.get.assert_called_once_with(expected_key)
    mock_redis.expire.assert_called_once_with(expected_key, app_config.cache_expiry)
    assert result == answer

@pytest.mark.asyncio
@patch('app.services.qa_cache_service.generate_safe_key')
async def test_load_qa_miss(mock_generate_safe_key):
    mock_generate_safe_key.return_value = expected_key
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    
    result = await load_qa(pdf_id, query, redis_conn=mock_redis)

    mock_generate_safe_key.assert_called_once_with(pdf_id, query)
    mock_redis.get.assert_called_once_with(expected_key)
    mock_redis.expire.assert_not_called()
    assert result is None
