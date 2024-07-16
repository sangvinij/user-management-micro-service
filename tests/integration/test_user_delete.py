from typing import Dict

import httpx
import pytest
from fastapi import status
from httpx import AsyncClient

from tests.test_client import UserTestClient


class TestUserDelete:
    user_client = UserTestClient()

    @pytest.mark.asyncio
    async def test_user_id_delete_endpoint_inaccessible_for_unauthorized(self, user_data: Dict, client: AsyncClient):
        user: Dict = user_data["user"]
        response: httpx.Response = await self.user_client.rud_specific_user(
            action="delete", user_id=user["user_id"], superuser_token=None, client=client
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Not authenticated"}

    @pytest.mark.asyncio
    async def test_user_id_delete_endpoint_inaccessible_for_non_admin(self, user_data: Dict, client: AsyncClient):
        user: Dict = user_data["user"]
        access_token: str = user_data["access_token"]
        failed_response: httpx.Response = await self.user_client.rud_specific_user(
            action="delete",
            user_id=user["user_id"],
            superuser_token=None,
            client=client,
            token=access_token,
        )

        assert failed_response.status_code == status.HTTP_403_FORBIDDEN
        assert failed_response.json() == {"detail": "insufficient permissions"}

    @pytest.mark.asyncio
    async def test_delete_user(self, user_data: Dict, client: AsyncClient, admin_data: Dict):
        admin_token: str = admin_data["admin_token"]

        user: Dict = user_data["user"]

        response: httpx.Response = await self.user_client.rud_specific_user(
            action="delete",
            user_id=user["user_id"],
            token=admin_token,
            client=client,
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["user_id"] == user["user_id"]

    @pytest.mark.asyncio
    async def test_delete_current_user(self, user_data: Dict, client: AsyncClient):
        access_token: str = user_data["access_token"]

        user: Dict = user_data["user"]

        response: httpx.Response = await self.user_client.rud_current_user(
            action="delete",
            token=access_token,
            client=client,
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["user_id"] == user["user_id"]
