import pytest
from httpx import AsyncClient
from starlette import status

from testlib.client.auth_client import AuthTestClient
from user_management.database.models import User


class TestAuth:
    auth_client = AuthTestClient()

    @pytest.mark.parametrize("login_field", ["username", "phone_number", "email"])
    @pytest.mark.asyncio
    async def test_auth(self, client: AsyncClient, user: User, login_field):
        login_fields = {"username": user.username, "phone_number": user.phone_number, "email": user.email}

        response = await self.auth_client.authenticate(
            username=login_fields.get(login_field), password=user.password, client=client
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()

    @pytest.mark.parametrize("login_field", ["username", "phone_number", "email"])
    @pytest.mark.asyncio
    async def test_auth_with_wrong_password(self, client: AsyncClient, user: User, login_field: str):
        login_fields = {"username": user.username, "phone_number": user.phone_number, "email": user.email}

        response = await self.auth_client.authenticate(
            username=login_fields.get(login_field), password="wrong", client=client
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "invalid credentials"}

    @pytest.mark.asyncio
    async def test_auth_with_wrong_login(self, client: AsyncClient, user: User):
        response = await self.auth_client.authenticate(
            username=user.image_s3_path, password=user.password, client=client
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "invalid credentials"}

    @pytest.mark.asyncio
    async def test_refresh_endpoint(self, client: AsyncClient, user: User):
        token_response = await self.auth_client.authenticate(
            username=user.username, password=user.password, client=client
        )
        refresh_token = token_response.json()["refresh_token"]
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
    async def test_refresh_endpoint_inaccessible_with_wrong_token_type(self, client: AsyncClient, user: User):
        token_response = await self.auth_client.authenticate(
            username=user.username, password=user.password, client=client
        )
        access_token = token_response.json()["access_token"]

        response = await self.auth_client.refresh(refresh_token=access_token, client=client)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "invalid token type"}

    @pytest.mark.asyncio
    async def test_refresh_with_blacklisted_token(self, client: AsyncClient, user: User):
        token_response = await self.auth_client.authenticate(
            username=user.username, password=user.password, client=client
        )
        refresh_token = token_response.json()["refresh_token"]

        response = await self.auth_client.refresh(refresh_token=refresh_token, client=client)

        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()

        response2 = await self.auth_client.refresh(refresh_token=refresh_token, client=client)

        assert response2.status_code == 400
        assert response2.json() == {"detail": "token in blacklist"}
