import pytest
from fakeredis.aioredis import FakeRedis


@pytest.fixture
def fake_redis_client():
    fake_redis = FakeRedis()
    return fake_redis
