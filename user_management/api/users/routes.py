import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Body, Depends, Path, Query

from user_management.api.utils.dependencies import admin_or_moderator, admin_user, authenticated_user
from user_management.database.models import User

from .schemas import UserDeleteModel, UserListReadModel, UserReadModel, UserUpdateModel
from .services import UserService

user_router: APIRouter = APIRouter(prefix="/user", tags=["User"])


@user_router.get("/me", response_model=UserReadModel)
async def me(user: Annotated[User, Depends(authenticated_user)]):
    return user


@user_router.patch("/me", response_model=UserReadModel)
async def update_me(
    user: Annotated[User, Depends(authenticated_user)],
    service: Annotated[UserService, Depends(UserService)],
    data: Annotated[UserUpdateModel, Body()],
):
    updated_user = await service.update_user(user_id=user.user_id, user_data=data)
    return updated_user


@user_router.delete("/me", response_model=UserDeleteModel)
async def delete_me(
    user: Annotated[User, Depends(authenticated_user)], service: Annotated[UserService, Depends(UserService)]
):
    deleted_user_id: uuid.UUID = await service.delete_user(user_id=user.user_id)
    return {"user_id": deleted_user_id}


@user_router.get("/{user_id}", response_model=UserReadModel)
async def read_one_user(
    user_id: Annotated[uuid.UUID, Path()],
    service: Annotated[UserService, Depends(UserService)],
    authorized_user: Annotated[User, Depends(admin_or_moderator)],
):
    user: User = await service.get_one_user_info(user_id=user_id, authorized_user=authorized_user)

    return user


@user_router.patch("/{user_id}", response_model=UserReadModel, dependencies=[Depends(admin_user)])
async def update_one_user(
    user_id: Annotated[uuid.UUID, Path()],
    service: Annotated[UserService, Depends(UserService)],
    data: Annotated[UserUpdateModel, Body()],
):
    user: User = await service.update_user(user_id=user_id, user_data=data)

    return user


@user_router.delete("/{user_id}", dependencies=[Depends(admin_user)], response_model=UserDeleteModel)
async def delete_one_user(
    user_id: uuid.UUID,
    service: Annotated[UserService, Depends(UserService)],
):
    deleted_user_id = await service.delete_user(user_id=user_id)

    return {"user_id": deleted_user_id}


@user_router.get("s", response_model=UserListReadModel)
async def user_list(
    service: Annotated[UserService, Depends(UserService)],
    authorized_user: Annotated[User, Depends(admin_or_moderator)],
    page: int = Query(ge=1, default=1),
    limit: int = Query(ge=1, default=50),
    sort_by: str = Query(default="username"),
    filter_by_name: Optional[str] = Query(default=None),
    order_by: str = Query(default="asc"),
):
    """endpoint /users"""
    response = await service.get_list(
        page=page,
        limit=limit,
        sort_field=sort_by,
        name=filter_by_name,
        ord_direction=order_by,
        authorized_user=authorized_user,
    )

    return response
