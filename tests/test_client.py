import uuid
from typing import Dict, Optional

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

    async def signup(self, client: httpx.AsyncClient, **kwargs) -> httpx.Response:
        response: httpx.Response = await client.post(url=self.signup_endpoint, json=kwargs, timeout=self.timeout)

        return response


class UserTestClient:
    """A class for handling user CRUD requests using HTTP."""

    base_endpoint = r"/user"
    timeout = 20

    async def _handle_action(
        self, url: str, action: str, token: str, client: httpx.AsyncClient, **kwargs
    ) -> httpx.Response:
        headers = {"Authorization": f"Bearer {token}"}

        match action:
            case "read":
                response = await client.get(url=url, headers=headers, timeout=self.timeout)
            case "update":
                response = await client.patch(url=url, headers=headers, timeout=self.timeout, json=kwargs)
            case "delete":
                response = await client.delete(url=url, headers=headers, timeout=self.timeout)
            case _:
                raise TypeError("wrong action")

        return response

    async def rud_current_user(self, action: str, token: str, client: httpx.AsyncClient, **kwargs) -> httpx.Response:
        url = f"{self.base_endpoint}/me"
        return await self._handle_action(url=url, action=action, token=token, client=client, **kwargs)

    async def rud_specific_user(
        self, user_id: uuid.UUID, action: str, token: str, client: httpx.AsyncClient, **kwargs
    ) -> httpx.Response:
        url = f"{self.base_endpoint}/{user_id}"
        return await self._handle_action(url=url, action=action, token=token, client=client, **kwargs)

    async def get_users_list(self, access_token: str, client: httpx.AsyncClient, **params) -> httpx.Response:
        response: httpx.Response = await client.get(
            f"{self.base_endpoint}s",
            params=params,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=self.timeout,
        )
        return response
