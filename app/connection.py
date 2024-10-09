"""
This module handles database connections
"""

import redis.asyncio as redis
from app.config import env_config


redis_connection: redis.Redis = redis.from_url(
    str(env_config.redis_url), encoding="utf8"
)
