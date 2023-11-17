from typing import Dict

import pytest
from httpx import AsyncClient
from starlette import status

from tests.test_client import AuthTestClient


class TestAuth:
    auth_client = AuthTestClient()

    @pytest.mark.parametrize("login_field", ["username", "phone_number", "email"])
    @pytest.mark.asyncio
    async def test_auth(self, client: AsyncClient, user_data: Dict, login_field):
        user = user_data["user"]
        password = user_data["password"]

        login_fields = {"username": user["username"], "phone_number": user["phone_number"], "email": user["email"]}

        response = await self.auth_client.authenticate(
            username=login_fields.get(login_field), password=password, client=client
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()

    @pytest.mark.parametrize("login_field", ["username", "phone_number", "email"])
    @pytest.mark.asyncio
    async def test_auth_with_wrong_password(self, client: AsyncClient, user_data: Dict, login_field: str):
        user = user_data["user"]

        login_fields = {"username": user["username"], "phone_number": user["phone_number"], "email": user["email"]}

        response = await self.auth_client.authenticate(
            username=login_fields.get(login_field), password="wrong", client=client
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "invalid credentials"}

    @pytest.mark.asyncio
    async def test_auth_with_wrong_login(self, client: AsyncClient, user_data: Dict):
        password = user_data["password"]
        response = await self.auth_client.authenticate(username="wrong_username", password=password, client=client)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "invalid credentials"}

    @pytest.mark.asyncio
    async def test_refresh_endpoint(self, client: AsyncClient, user_data: Dict):
        refresh_token = user_data["refresh_token"]

        response = await self.auth_client.refresh(refresh_token=refresh_token, client=client)

        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()

    @pytest.mark.asyncio
    async def test_refresh_endpoint_inaccessible_for_non_authorized(self, client: AsyncClient):
        response = await self.auth_client.refresh(refresh_token=None, client=client)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Not authenticated"}

    @pytest.mark.asyncio
    async def test_refresh_endpoint_inaccessible_with_wrong_token(self, client: AsyncClient):
        response = await self.auth_client.refresh(refresh_token="token", client=client)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "invalid token"}

    @pytest.mark.asyncio
    async def test_refresh_endpoint_inaccessible_with_wrong_token_type(self, client: AsyncClient, user_data: Dict):
        access_token = user_data["access_token"]

        response = await self.auth_client.refresh(refresh_token=access_token, client=client)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "invalid token type"}

    @pytest.mark.asyncio
    async def test_refresh_with_blacklisted_token(self, client: AsyncClient, user_data: Dict):
        refresh_token = user_data["refresh_token"]

        response = await self.auth_client.refresh(refresh_token=refresh_token, client=client)

        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()

        response2 = await self.auth_client.refresh(refresh_token=refresh_token, client=client)

        assert response2.status_code == 400
        assert response2.json() == {"detail": "token in blacklist"}
