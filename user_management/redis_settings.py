from redis import asyncio as aioredis

from user_management.config import config


async def get_redis_client():
    redis_client: aioredis.Redis = await aioredis.from_url(config.redis_url)
    try:
        yield redis_client
    finally:
        await redis_client.aclose()
