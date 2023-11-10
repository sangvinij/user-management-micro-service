from typing import Optional

import httpx


class AuthTestClient:
    auth_endpoint = r"/auth/login"
    refresh_endpoint = r"auth/refresh-token"
    timeout = 20

    async def authenticate(self, username: str, password: str, client: httpx.AsyncClient) -> httpx.Response:
        response = await client.post(
            url=self.auth_endpoint, data={"username": username, "password": password}, timeout=self.timeout
        )
        return response

    async def refresh(self, refresh_token: Optional[str], client: httpx.AsyncClient) -> httpx.Response:
        headers = {"Authorization": f"Bearer {refresh_token}"} if refresh_token else None
        response = await client.post(url=self.refresh_endpoint, headers=headers, timeout=self.timeout)
        return response
