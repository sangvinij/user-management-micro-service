import uuid
from typing import Dict, Optional

import httpx
from pydantic import EmailStr


class AuthTestClient:
    """A class for handling authentication requests using HTTP."""

    auth_endpoint = r"/auth/login"
    refresh_endpoint = r"auth/refresh-token"
    signup_endpoint = r"auth/signup"
    reset_password_endpoint = r"auth/reset_password"
    reset_password_confirm_endpoint = r"auth/reset_password_confirm"

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
        response: httpx.Response = await client.post(url=self.signup_endpoint, data=kwargs, timeout=self.timeout)

        return response

    async def reset_password(self, client: httpx.AsyncClient, email: EmailStr) -> httpx.Response:
        response: httpx.Response = await client.post(
            url=self.reset_password_endpoint, json={"email": email}, timeout=self.timeout
        )

        return response

    async def reset_password_confirm(self, client: httpx.AsyncClient, password: str, password_retype: str, token: str):
        response: httpx.Response = await client.post(
            url=self.reset_password_confirm_endpoint,
            json={"password": password, "password_retype": password_retype, "token": token},
        )

        return response


class UserTestClient:
    """A class for handling user CRUD requests using HTTP."""

    base_endpoint = r"/user"
    timeout = 20

    async def _handle_action(
        self, url: str, action: str, client: httpx.AsyncClient, token: Optional[str] = None, **kwargs
    ) -> httpx.Response:
        """Choose the correct request method depending on the 'action' parameter."""
        headers = {"Authorization": f"Bearer {token}"} if token else None

        match action:
            case "read":
                response = await client.get(url=url, headers=headers, timeout=self.timeout)
            case "update":
                response = await client.patch(url=url, headers=headers, timeout=self.timeout, data=kwargs)
            case "delete":
                response = await client.delete(url=url, headers=headers, timeout=self.timeout)
            case _:
                raise TypeError("wrong action")

        return response

    async def rud_current_user(
        self, action: str, client: httpx.AsyncClient, token: Optional[str] = None, **kwargs
    ) -> httpx.Response:
        """Make requests to /user/me endpoint."""

        url = f"{self.base_endpoint}/me"
        return await self._handle_action(url=url, action=action, token=token, client=client, **kwargs)

    async def rud_specific_user(
        self, user_id: uuid.UUID, action: str, client: httpx.AsyncClient, token: Optional[str] = None, **kwargs
    ) -> httpx.Response:
        """Make requests to /user/{user_id} endpoint."""

        url = f"{self.base_endpoint}/{user_id}"
        return await self._handle_action(url=url, action=action, token=token, client=client, **kwargs)

    async def get_users_list(self, client: httpx.AsyncClient, token: Optional[str] = None, **kwargs) -> httpx.Response:
        """Make requests to /users endpoint"""

        headers: Optional[Dict] = {"Authorization": f"Bearer {token}"} if token else None
        response: httpx.Response = await client.get(
            f"{self.base_endpoint}s",
            params=kwargs,
            headers=headers,
            timeout=self.timeout,
        )
        return response
