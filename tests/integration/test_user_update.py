import datetime
from typing import Dict

import httpx
import pytest
import pytz
from fastapi import status
from httpx import AsyncClient

from tests.integration.conftest import generate_user_data
from tests.test_client import UserTestClient
from user_management.api.users.schemas import UserReadModel


class TestUserUpdate:
    user_client = UserTestClient()

    @pytest.mark.asyncio
    async def test_user_id_update_endpoint_inaccessible_for_unauthorized(self, user_data: Dict, client: AsyncClient):
        user: Dict = user_data["user"]
        email: str = "updated_email@example.com"
        failed_response: httpx.Response = await self.user_client.rud_specific_user(
            action="update",
            user_id=user["user_id"],
            superuser_token=None,
            email=email,
            client=client,
        )

        assert failed_response.status_code == status.HTTP_401_UNAUTHORIZED
        assert failed_response.json() == {"detail": "Not authenticated"}

    @pytest.mark.asyncio
    async def test_user_id_update_endpoint_inaccessible_for_non_admin(self, user_data: Dict, client: AsyncClient):
        user: Dict = user_data["user"]
        access_token = user_data["access_token"]
        email: str = "updated_email@example.com"
        failed_response: httpx.Response = await self.user_client.rud_specific_user(
            action="update",
            user_id=user["user_id"],
            superuser_token=None,
            email=email,
            client=client,
            token=access_token,
        )

        assert failed_response.status_code == status.HTTP_403_FORBIDDEN
        assert failed_response.json() == {"detail": "insufficient permissions"}

    @pytest.mark.asyncio
    async def test_update_user(self, user_data: Dict, groups: Dict, client: AsyncClient, admin_data: Dict):
        admin_token: str = admin_data["admin_token"]

        user = user_data["user"]

        update_data: Dict = generate_user_data(name="test_updated_user", group_id=groups["test_group2"].group_id)
        file: bytes = update_data.pop("file")

        response: httpx.Response = await self.user_client.rud_specific_user(
            action="update", user_id=user["user_id"], file=file, token=admin_token, client=client, **update_data
        )

        assert response.status_code == status.HTTP_200_OK

        updated_user: UserReadModel = UserReadModel(**response.json())

        assert str(updated_user.user_id) == user["user_id"]
        assert updated_user.email == update_data["email"]
        assert updated_user.username == update_data["username"]
        assert updated_user.surname == update_data["surname"]
        assert updated_user.is_blocked == update_data["is_blocked"]
        assert updated_user.image_s3_path.split("/")[-1] == update_data["username"]

        assert updated_user.created_at == datetime.datetime.strptime(
            user["created_at"], "%Y-%m-%dT%H:%M:%S.%f%z"
        ).astimezone(pytz.utc)
        assert updated_user.modified_at != datetime.datetime.strptime(
            user["modified_at"], "%Y-%m-%dT%H:%M:%S.%f%z"
        ).astimezone(pytz.utc)

    @pytest.mark.asyncio
    async def test_update_one_field(self, user_data: Dict, client: AsyncClient, admin_data: Dict):
        admin_token: str = admin_data["admin_token"]

        user: Dict = user_data["user"]

        update_name: str = "test_updated_user"

        response: httpx.Response = await self.user_client.rud_specific_user(
            action="update", user_id=user["user_id"], token=admin_token, client=client, name=update_name
        )

        assert response.status_code == status.HTTP_200_OK

        updated_user: UserReadModel = UserReadModel(**response.json())

        assert updated_user.name == update_name

        assert str(updated_user.user_id) == user["user_id"]
        assert updated_user.email == user["email"]
        assert updated_user.username == user["username"]
        assert updated_user.surname == user["surname"]
        assert updated_user.is_blocked == user["is_blocked"]
        assert updated_user.image_s3_path.split("/")[-1] == user["username"]

        assert updated_user.created_at == datetime.datetime.strptime(
            user["created_at"], "%Y-%m-%dT%H:%M:%S.%f%z"
        ).astimezone(pytz.utc)
        assert updated_user.modified_at != datetime.datetime.strptime(
            user["modified_at"], "%Y-%m-%dT%H:%M:%S.%f%z"
        ).astimezone(pytz.utc)

    @pytest.mark.asyncio
    async def test_update_current_user(self, user_data: Dict, groups: Dict, client: AsyncClient, admin_data: Dict):
        access_token: str = user_data["access_token"]
        user = user_data["user"]

        update_data: Dict = generate_user_data(name="test_updated_user", group_id=groups["test_group2"].group_id)

        file: bytes = update_data.pop("file")

        response: httpx.Response = await self.user_client.rud_current_user(
            action="update", file=file, token=access_token, client=client, **update_data
        )

        assert response.status_code == status.HTTP_200_OK

        updated_user: UserReadModel = UserReadModel(**response.json())

        assert str(updated_user.user_id) == user["user_id"]
        assert updated_user.email == update_data["email"]
        assert updated_user.username == update_data["username"]
        assert updated_user.surname == update_data["surname"]
        assert updated_user.is_blocked == update_data["is_blocked"]
        assert updated_user.image_s3_path.split("/")[-1] == update_data["username"]

        assert updated_user.created_at == datetime.datetime.strptime(
            user["created_at"], "%Y-%m-%dT%H:%M:%S.%f%z"
        ).astimezone(pytz.utc)
        assert updated_user.modified_at != datetime.datetime.strptime(
            user["modified_at"], "%Y-%m-%dT%H:%M:%S.%f%z"
        ).astimezone(pytz.utc)

    @pytest.mark.asyncio
    async def test_update_role_to_current_user(self, user_data: Dict, client: AsyncClient):
        access_token: str = user_data["access_token"]

        response: httpx.Response = await self.user_client.rud_current_user(
            action="update", token=access_token, client=client, role="ADMIN"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["role"] == "USER"

    @pytest.mark.asyncio
    async def test_update_role_by_admin(self, user_data: Dict, admin_data: Dict, client: AsyncClient):
        access_token: str = admin_data["admin_token"]

        response: httpx.Response = await self.user_client.rud_specific_user(
            user_id=user_data["user"]["user_id"], action="update", token=access_token, client=client, role="ADMIN"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["role"] == "ADMIN"

    @pytest.mark.asyncio
    async def test_block_current_user(self, user_data: Dict, client: AsyncClient):
        access_token: str = user_data["access_token"]

        response: httpx.Response = await self.user_client.rud_current_user(
            action="update", token=access_token, client=client, is_blocked=True
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["is_blocked"] is False

    @pytest.mark.asyncio
    async def test_block_user_by_admin(self, user_data: Dict, admin_data: Dict, client: AsyncClient):
        access_token: str = admin_data["admin_token"]

        response: httpx.Response = await self.user_client.rud_specific_user(
            user_id=user_data["user"]["user_id"], action="update", token=access_token, client=client, is_blocked=True
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["is_blocked"]
