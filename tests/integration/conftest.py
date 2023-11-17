import asyncio
import secrets
import string
from typing import AsyncGenerator, Dict

import httpx
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import delete

from tests.test_client import AuthTestClient, UserTestClient
from user_management.config import config
from user_management.database.db_settings import async_session_maker
from user_management.database.models import Group, Role, User


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
async def roles():
    admin_role = Role(role_name="ADMIN")
    moderator_role = Role(role_name="MODERATOR")
    user_role = Role(role_name="USER")

    async with async_session_maker() as session:
        session.add_all((admin_role, moderator_role, user_role))
        await session.commit()

    yield {"admin_role": admin_role, "moderator_role": moderator_role, "user_role": user_role}

    async with async_session_maker() as session:
        stmt = delete(Role)
        await session.execute(stmt)
        await session.commit()


@pytest_asyncio.fixture(scope="package")
async def group():
    test_group = Group(name="test group")

    async with async_session_maker() as session:
        session.add(test_group)
        await session.commit()

    yield test_group

    async with async_session_maker() as session:
        stmt = delete(Group).filter(Group.group_id == test_group.group_id)
        await session.execute(stmt)
        await session.commit()


def generate_credentials():
    email = "test." + "".join(secrets.choice(string.ascii_lowercase) for _ in range(6)) + "@example.com"
    password = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
    username = "test_".join(secrets.choice(string.ascii_lowercase) for _ in range(8))
    phone_number = "+37529" + "".join(secrets.choice(string.digits) for _ in range(7))
    return {"email": email, "password": password, "username": username, "phone_number": phone_number}


@pytest_asyncio.fixture(scope="package")
async def admin(roles: Dict, group: Group, client: AsyncClient) -> Dict:
    auth_client = AuthTestClient()
    user_client = UserTestClient()

    role_id = roles["admin_role"].role_id

    admin_data = generate_credentials()
    admin_data.update(
        {
            "name": "test_admin",
            "surname": "test_surname",
            "is_blocked": False,
            "image_s3_path": "stub_path",
            "role_id": role_id,
            "group_id": group.group_id,
        }
    )
    signup_response: httpx.Response = await auth_client.signup(data=admin_data, client=client)
    test_admin = signup_response.json()

    login_response = await auth_client.authenticate(
        username=admin_data["username"], password=admin_data["password"], client=client
    )

    admin_access_token = login_response.json()["access_token"]

    yield {"admin": test_admin, "admin_token": admin_access_token}

    await user_client.delete(user_id=test_admin["user_id"], admin_token=admin_access_token, client=client)


@pytest_asyncio.fixture(scope="package")
async def moderator(roles: Dict, group: Group, client: AsyncClient) -> Dict:
    auth_client: AuthTestClient = AuthTestClient()
    user_client: UserTestClient = UserTestClient()

    role_id: int = roles["moderator_role"].role_id

    moderator_data: Dict = generate_credentials()
    moderator_data.update(
        {
            "name": "test_admin",
            "surname": "test_surname",
            "is_blocked": False,
            "image_s3_path": "stub_path",
            "role_id": role_id,
            "group_id": group.group_id,
        }
    )
    signup_response: httpx.Response = await auth_client.signup(data=moderator_data, client=client)
    test_moderator = signup_response.json()

    login_response: httpx.Response = await auth_client.authenticate(
        username=moderator_data["username"], password=moderator_data["password"], client=client
    )
    moderator_access_token: str = login_response.json()["access_token"]

    yield {"moderator": test_moderator, "moderator_token": moderator_access_token}

    await user_client.delete(user_id=test_moderator["user_id"], admin_token=admin["admin_token"], client=client)


@pytest_asyncio.fixture
async def user_data(roles: Dict, group: Group, client: AsyncClient, admin: Dict) -> Dict:
    auth_client = AuthTestClient()
    user_client = UserTestClient()

    role_id = roles["user_role"].role_id
    user_data = generate_credentials()
    user_data.update(
        {
            "name": "test_user",
            "surname": "test_surname",
            "is_blocked": False,
            "image_s3_path": "stub_path",
            "role_id": role_id,
            "group_id": group.group_id,
        }
    )

    signup_response: httpx.Response = await auth_client.signup(data=user_data, client=client)
    test_user: Dict = signup_response.json()

    login_response: httpx.Response = await auth_client.authenticate(
        username=test_user["username"], password=test_user["password"], client=client
    )

    user_access_token: str = login_response.json()["access_token"]
    user_refresh_token: str = login_response.json()["refresh_token"]

    signup_response: httpx.Response = await auth_client.signup(data=user_data, client=client)
    test_user: signup_response.json()

    yield {
        "test_user": test_user,
        "access_token": user_access_token,
        "refresh_token": user_refresh_token,
        "password": user_data["password"],
    }

    await user_client.delete(user_id=test_user["user_id"], admin_token=admin["admin_token"], client=client)
