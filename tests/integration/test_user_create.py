from typing import Dict

import httpx
import pytest
from fastapi import status
from httpx import AsyncClient

from user_management.api.auth.schemas import SignupResponseModel

from ..test_client import AuthTestClient, UserTestClient
from .conftest import generate_user_data


class TestUserCreate:
    auth_client = AuthTestClient()
    user_client = UserTestClient()

    @pytest.mark.asyncio
    async def test_create_user(self, client: AsyncClient, groups: Dict, admin_data: Dict):
        group_id: int = groups["test_group"].group_id
        user_data: Dict = generate_user_data(name="test_created_user", group_id=group_id)
        file = user_data.pop("file")

        response: httpx.Response = await self.auth_client.signup(client=client, file=file, **user_data)

        assert response.status_code == status.HTTP_201_CREATED

        created_user: SignupResponseModel = SignupResponseModel(**response.json())

        assert created_user.email == user_data["email"]
        assert created_user.username == user_data["username"]
        assert created_user.surname == user_data["surname"]
        assert created_user.is_blocked == user_data["is_blocked"]
        assert created_user.role == "USER"
        assert created_user.group_id == user_data["group_id"]
        assert created_user.image_s3_path.split("/")[-1] == user_data["username"]

        await self.user_client.rud_specific_user(
            action="delete", token=admin_data["admin_token"], user_id=created_user.user_id, client=client
        )

    @pytest.mark.asyncio
    async def test_create_user_already_exists(self, client: AsyncClient, groups: Dict, admin_data: Dict):
        group_id: int = groups["test_group"].group_id
        user_data: Dict = generate_user_data(name="test_created_user", group_id=group_id)

        file = user_data.pop("file")
        response: httpx.Response = await self.auth_client.signup(client=client, file=file, **user_data)

        assert response.status_code == status.HTTP_201_CREATED
        created_user: SignupResponseModel = SignupResponseModel(**response.json())

        failed_response: httpx.Response = await self.auth_client.signup(client=client, file=file, **user_data)
        assert failed_response.status_code == status.HTTP_409_CONFLICT
        assert failed_response.json() == {"detail": "user with such credentials already exists"}

        await self.user_client.rud_specific_user(
            action="delete", token=admin_data["admin_token"], user_id=created_user.user_id, client=client
        )

    @pytest.mark.asyncio
    async def test_create_user_with_wrong_role(self, client: AsyncClient, groups: Dict, admin_data: Dict):
        group_id: int = groups["test_group"].group_id
        user_data: Dict = generate_user_data(name="test_created_user", group_id=group_id)
        user_data.update({"role": "ADMIN"})
        file = user_data.pop("file")

        response: httpx.Response = await self.auth_client.signup(client=client, file=file, **user_data)

        assert response.status_code == status.HTTP_201_CREATED

        created_user: SignupResponseModel = SignupResponseModel(**response.json())

        assert created_user.role == "USER"

        await self.user_client.rud_specific_user(
            action="delete", token=admin_data["admin_token"], user_id=created_user.user_id, client=client
        )
