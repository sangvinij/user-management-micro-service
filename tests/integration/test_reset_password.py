import secrets
import string
from typing import Dict

import httpx
import pytest
from fastapi import status
from pydantic import EmailStr

from tests.test_client import AuthTestClient


class TestResetPassword:
    auth_client = AuthTestClient()

    @pytest.mark.asyncio
    async def test_send_reset_url(self, user_data: Dict, client: httpx.AsyncClient):
        user: Dict = user_data["user"]

        response: httpx.Response = await self.auth_client.reset_password(email=user["email"], client=client)

        assert response.status_code == status.HTTP_200_OK
        assert "url" in response.json()

    @pytest.mark.asyncio
    async def test_send_reset_url_with_non_existing_email(self, client: httpx.AsyncClient):
        email: EmailStr = "email@example.com"
        response: httpx.Response = await self.auth_client.reset_password(email=email, client=client)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "User not found"}

    @pytest.mark.asyncio
    async def test_reset_password(self, user_data: Dict, client: httpx.AsyncClient):
        user: Dict = user_data["user"]

        get_url_response: httpx.Response = await self.auth_client.reset_password(email=user["email"], client=client)

        assert get_url_response.status_code == status.HTTP_200_OK

        token: str = get_url_response.json()["url"].split("/")[-1]

        new_password: str = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(5))

        reset_password_response: httpx.Response = await self.auth_client.reset_password_confirm(
            token=token, password=new_password, password_retype=new_password, client=client
        )

        assert reset_password_response.status_code == status.HTTP_200_OK
        assert reset_password_response.json() == {"detail": "password changed successfully"}

        get_token_response: httpx.Response = await self.auth_client.authenticate(
            username=user["username"], password=new_password, client=client
        )

        assert get_token_response.status_code == status.HTTP_200_OK
        assert "access_token" in get_token_response.json()
        assert "refresh_token" in get_token_response.json()

    @pytest.mark.asyncio
    async def test_reset_password_mismatched(self, user_data: Dict, client: httpx.AsyncClient):
        user: Dict = user_data["user"]

        get_url_response: httpx.Response = await self.auth_client.reset_password(email=user["email"], client=client)

        assert get_url_response.status_code == status.HTTP_200_OK

        token: str = get_url_response.json()["url"].split("/")[-1]

        new_password: str = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(5))

        reset_password_response: httpx.Response = await self.auth_client.reset_password_confirm(
            token=token, password=new_password, password_retype="new_password", client=client
        )

        assert reset_password_response.status_code == status.HTTP_400_BAD_REQUEST
        assert reset_password_response.json() == {"detail": "Passwords do not match"}

    @pytest.mark.asyncio
    async def test_reset_password_with_wrong_token(self, client: httpx.AsyncClient):
        new_password: str = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(5))
        response: httpx.Response = await self.auth_client.reset_password_confirm(
            token="wrong", password=new_password, password_retype=new_password, client=client
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "user not found"}
