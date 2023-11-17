import uuid
from typing import Optional, Dict

import httpx


class AuthTestClient:
    """A class for handling authentication requests using HTTP."""

    auth_endpoint = r"/auth/login"
    refresh_endpoint = r"auth/refresh-token"
    signup_endpoint = r"auth/signup"

    timeout = 20

    async def authenticate(self, username: str, password: str, client: httpx.AsyncClient) -> httpx.Response:
        """Authenticate the user by sending a POST request to the authentication endpoint."""
        response = await client.post(
            url=self.auth_endpoint, data={"username": username, "password": password}, timeout=self.timeout
        )
        return response

    async def refresh(self, refresh_token: Optional[str], client: httpx.AsyncClient) -> httpx.Response:
        """Refresh the access token by sending a POST request to the refresh endpoint."""
        headers = {"Authorization": f"Bearer {refresh_token}"} if refresh_token else None
        response = await client.post(url=self.refresh_endpoint, headers=headers, timeout=self.timeout)
        return response

    async def signup(self, data: Dict, client: httpx.AsyncClient) -> httpx.Response:
        response: httpx.Response = await client.post(url=self.signup_endpoint, json=data, timeout=self.timeout)

        return response


class UserTestClient:
    """A class for handling user CRUD requests using HTTP."""

    base_endpoint = r"/user"

    async def delete(self, user_id: uuid.UUID, admin_token: str, client: httpx.AsyncClient) -> httpx.Response:
        response: httpx.Response = await client.delete(
            url=f"{self.base_endpoint}/{user_id}", headers={"Authorization": f"Bearer {admin_token}"}
        )
        return response
