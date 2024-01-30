import asyncio
import io
import secrets
import string
from typing import AsyncGenerator, Dict

import httpx
import pytest
import pytest_asyncio
from httpx import AsyncClient
from PIL import Image
from sqlalchemy import delete, or_

from tests.test_client import AuthTestClient, UserTestClient
from user_management.config import config
from user_management.database.db_settings import async_session_maker
from user_management.database.models import Group


@pytest.fixture(scope="package")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="package")
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(base_url=config.WEBAPP_TEST_HOST) as ac:
        yield ac


@pytest_asyncio.fixture(scope="package")
async def groups():
    """create two test groups"""
    test_group: Group = Group(name="test group")
    test_group2: Group = Group(name="test group2")

    async with async_session_maker() as session:
        session.add(test_group)
        session.add(test_group2)
        await session.commit()

    yield {"test_group": test_group, "test_group2": test_group2}

    async with async_session_maker() as session:
        stmt = delete(Group).filter(or_(Group.group_id == test_group.group_id, Group.group_id == test_group2.group_id))
        await session.execute(stmt)
        await session.commit()


def generate_user_data(name: str, group_id: int, is_blocked: bool = False) -> Dict:
    surname: str = "test_" + "".join(secrets.choice(string.ascii_lowercase) for _ in range(6))
    email: str = "test." + "".join(secrets.choice(string.ascii_lowercase) for _ in range(6)) + "@example.com"
    password: str = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
    username: str = "test_".join(secrets.choice(string.ascii_lowercase) for _ in range(8))
    phone_number: str = "+37529" + "".join(secrets.choice(string.digits) for _ in range(7))

    file: Image = Image.new("RGB", (100, 100), color="white")
    file_stream: io.BytesIO = io.BytesIO()
    file.save(file_stream, format="JPEG")
    file_stream.seek(0)

    file_bytes: bytes = file_stream.getvalue()

    return {
        "name": name,
        "surname": surname,
        "email": email,
        "password": password,
        "username": username,
        "phone_number": phone_number,
        "file": file_bytes,
        "group_id": group_id,
        "is_blocked": is_blocked,
    }


@pytest_asyncio.fixture(scope="package")
async def admin_data(groups: Dict, client: AsyncClient) -> Dict:
    auth_client: AuthTestClient = AuthTestClient()
    user_client: UserTestClient = UserTestClient()

    login_response = await auth_client.authenticate(
        username=config.ADMIN_USERNAME, password=config.ADMIN_PASSWORD, client=client
    )
    admin_access_token = login_response.json()["access_token"]
    admin_data = await user_client.rud_current_user(action="read", token=admin_access_token, client=client)

    return {"admin": admin_data.json(), "admin_token": admin_access_token}


@pytest_asyncio.fixture(scope="package")
async def moderator_data(groups: Dict, admin_data: Dict, client: AsyncClient) -> Dict:
    auth_client: AuthTestClient = AuthTestClient()
    user_client: UserTestClient = UserTestClient()

    group_id = groups["test_group"].group_id

    moderator_data: Dict = generate_user_data(name="test_moderator", group_id=group_id)
    file = moderator_data.pop("file")

    signup_response: httpx.Response = await auth_client.signup(client=client, file=file, **moderator_data)

    change_role_response: httpx.Response = await user_client.rud_specific_user(
        action="update",
        user_id=signup_response.json()["user_id"],
        token=admin_data["admin_token"],
        client=client,
        role="MODERATOR",
    )
    test_moderator = change_role_response.json()

    login_response: httpx.Response = await auth_client.authenticate(
        username=moderator_data["username"], password=moderator_data["password"], client=client
    )
    moderator_access_token: str = login_response.json()["access_token"]

    yield {"moderator": test_moderator, "moderator_token": moderator_access_token}

    await user_client.rud_current_user(action="delete", token=moderator_access_token, client=client)


@pytest_asyncio.fixture
async def user_data(groups: Dict, client: AsyncClient, admin_data: Dict) -> Dict:
    auth_client = AuthTestClient()
    user_client = UserTestClient()

    group_id = groups["test_group"].group_id

    data = generate_user_data(name="test_user", group_id=group_id)

    file = data.pop("file")

    signup_response: httpx.Response = await auth_client.signup(client=client, file=file, **data)
    test_user: Dict = signup_response.json()

    login_response: httpx.Response = await auth_client.authenticate(
        username=test_user["username"], password=data["password"], client=client
    )

    user_access_token: str = login_response.json()["access_token"]
    user_refresh_token: str = login_response.json()["refresh_token"]

    yield {
        "user": test_user,
        "access_token": user_access_token,
        "refresh_token": user_refresh_token,
        "password": data["password"],
    }

    await user_client.rud_specific_user(
        action="delete", user_id=test_user["user_id"], token=admin_data["admin_token"], client=client
    )
