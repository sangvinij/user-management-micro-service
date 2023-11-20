import uuid
from typing import Dict, List

import httpx
import pytest
from fastapi import status
from httpx import AsyncClient

from tests.test_client import UserTestClient


class TestUserRead:
    user_client: UserTestClient = UserTestClient()

    @pytest.mark.asyncio
    async def test_user_id_read_endpoint_inaccessible_for_unauthorized(self, user_data: Dict, client: AsyncClient):
        user_id = user_data["user"]["user_id"]

        response: httpx.Response = await self.user_client.rud_specific_user(
            action="read", user_id=user_id, client=client
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Not authenticated"}

    @pytest.mark.asyncio
    async def test_user_read_by_admin(self, user_data: Dict, admin_data: Dict, client: AsyncClient):
        user_id: uuid.UUID = user_data["user"]["user_id"]
        admin_token: str = admin_data["admin_token"]

        response = await self.user_client.rud_specific_user(
            action="read", user_id=user_id, client=client, token=admin_token
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["user_id"] == user_id

    @pytest.mark.asyncio
    async def test_user_read_by_moderator(self, user_data: Dict, moderator_data: Dict, client: AsyncClient):
        user_id: uuid.UUID = user_data["user"]["user_id"]
        moderator_token: str = moderator_data["moderator_token"]

        response: httpx.Response = await self.user_client.rud_specific_user(
            action="read", user_id=user_id, client=client, token=moderator_token
        )

        assert moderator_data["moderator"]["group_id"] == user_data["user"]["group_id"]
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["user_id"] == user_id

    @pytest.mark.asyncio
    async def test_user_read_by_moderator_with_wrong_group(
        self, user_data: Dict, moderator_data: Dict, client: AsyncClient, groups: Dict
    ):
        user: Dict = user_data["user"]

        group_1_id: int = groups["test_group"].group_id
        group_2_id: int = groups["test_group2"].group_id

        moderator_token = moderator_data["moderator_token"]

        await self.user_client.rud_current_user(
            action="update", token=moderator_token, client=client, group_id=group_2_id
        )

        response = await self.user_client.rud_specific_user(
            action="read", user_id=user["user_id"], token=moderator_token, client=client
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": "invalid role"}

        await self.user_client.rud_current_user(
            action="update", token=moderator_token, client=client, group_id=group_1_id
        )

    @pytest.mark.asyncio
    async def test_read_current_user(self, user_data: Dict, client: AsyncClient):
        access_token = user_data["access_token"]

        response = await self.user_client.rud_current_user(action="read", client=client, token=access_token)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["user_id"] == user_data["user"]["user_id"]


class TestUserListRead:
    user_client: UserTestClient = UserTestClient()

    @pytest.mark.asyncio
    async def test_user_list_endpoint_inaccessible_for_unauthorized(self, client: AsyncClient):
        response: httpx.Response = await self.user_client.get_users_list(client=client)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Not authenticated"}

    @pytest.mark.asyncio
    async def test_read_user_list_by_admin(self, admin_data: Dict, client: AsyncClient):
        admin_token: str = admin_data["admin_token"]

        response: httpx.Response = await self.user_client.get_users_list(client=client, token=admin_token)

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_read_user_list_by_moderator(
        self, moderator_data: Dict, user_data: Dict, groups: Dict, client: AsyncClient
    ):
        user_token = user_data["access_token"]

        group_1_id: int = groups["test_group"].group_id
        group_2_id: int = groups["test_group2"].group_id

        moderator: Dict = moderator_data["moderator"]
        moderator_token: str = moderator_data["moderator_token"]

        await self.user_client.rud_current_user(action="update", token=user_token, group_id=group_2_id, client=client)

        response: httpx.Response = await self.user_client.get_users_list(token=moderator_token, client=client)

        assert response.status_code == status.HTTP_200_OK

        assert moderator["group_id"] == group_1_id
        for user in response.json()["users"]:
            assert user["group"]["group_id"] == group_1_id

    @pytest.mark.asyncio
    async def test_pagination(self, user_data: Dict, admin_data: Dict, client: AsyncClient):
        admin_token = admin_data["admin_token"]
        response = await self.user_client.get_users_list(token=admin_token, client=client, limit=1, page=2)

        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()

        assert response_data["limit"] == 1
        assert response_data["total_pages"] == 3
        assert response_data["total_count"] == 3
        assert len(response_data["users"]) == 1

    @pytest.mark.asyncio
    async def test_filter_by_name(self, user_data: Dict, admin_data: Dict, client: AsyncClient):
        admin_token = admin_data["admin_token"]
        user = user_data["user"]

        response = await self.user_client.get_users_list(token=admin_token, client=client, filter_by_name=user["name"])

        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()
        assert len(response_data["users"]) == 1
        assert response_data["users"][0]["name"] == user["name"]

    @pytest.mark.asyncio
    async def test_sorting(self, user_data: Dict, admin_data: Dict, moderator_data: Dict, client: AsyncClient):
        admin_token = admin_data["admin_token"]
        user = user_data["user"]
        moderator = moderator_data["moderator"]
        admin = admin_data["admin"]

        sorted_list_of_names: List = sorted([user["name"], moderator["name"], admin["name"]])

        response = await self.user_client.get_users_list(token=admin_token, client=client, sort_by="name")

        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()

        result_names = [user["name"] for user in response_data["users"]]

        assert result_names == sorted_list_of_names

        response2 = await self.user_client.get_users_list(
            token=admin_token, client=client, sort_by="name", order_by="desc"
        )

        assert response2.status_code == status.HTTP_200_OK

        response2_data = response2.json()
        second_result_names = [user["name"] for user in response2_data["users"]]

        assert second_result_names == sorted_list_of_names[::-1]
