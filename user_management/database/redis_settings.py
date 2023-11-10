from redis import asyncio as aioredis

from ..config import config


async def create_redis_pool():
    redis_client = await aioredis.from_url(config.redis_url)
    try:
        yield redis_client
    finally:
        await redis_client.aclose()
