import pytest
from httpx import AsyncClient

from user_management.config import config


@pytest.mark.asyncio
@pytest.mark.skip
async def test_healthcheck():
    async with AsyncClient() as client:
        response = await client.get(url=f"{config.WEBAPP_TEST_HOST}/healthcheck", timeout=20)

        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
