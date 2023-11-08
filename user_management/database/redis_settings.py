import aioredis

from ..config import config


async def create_redis_pool():
    redis = await aioredis.from_url(config.redis_url)
    try:
        yield redis
    finally:
        await redis.close()
