import uuid
from typing import Annotated, Dict, Optional

import aioboto3
from fastapi import APIRouter, Depends, File, Path, Query, UploadFile, status

from user_management.api.utils.dependencies import admin_or_moderator, admin_user, authenticated_user
from user_management.database.models import User

from ...aws.settings import get_aws_s3_client
from .schemas import CurrentUserUpdateModel, UserListReadModel, UserReadModel, UserUpdateModel
from .services import UserService

user_router: APIRouter = APIRouter(prefix="/user", tags=["User"])


@user_router.get("/me", response_model=UserReadModel, status_code=status.HTTP_200_OK)
async def me(user: Annotated[User, Depends(authenticated_user)]):
    return user


@user_router.patch("/me", response_model=UserReadModel, status_code=status.HTTP_200_OK)
async def update_me(
    user: Annotated[User, Depends(authenticated_user)],
    service: Annotated[UserService, Depends(UserService)],
    s3: Annotated[aioboto3.Session.client, Depends(get_aws_s3_client)],
    data: Annotated[CurrentUserUpdateModel, Depends(CurrentUserUpdateModel.as_form)],
    file: UploadFile = File(default=None),
):
    updated_user: User = await service.update_user(
        user_id=user.user_id, file=file, user_data=data.model_dump(exclude_none=True), s3=s3
    )
    return updated_user


@user_router.delete("/me", status_code=status.HTTP_200_OK)
async def delete_me(
    user: Annotated[User, Depends(authenticated_user)], service: Annotated[UserService, Depends(UserService)]
):
    deleted_user_id: uuid.UUID = await service.delete_user(user_id=user.user_id)
    return {"user_id": deleted_user_id}


@user_router.get("/{user_id}", response_model=UserReadModel, status_code=status.HTTP_200_OK)
async def one_user(
    user_id: Annotated[uuid.UUID, Path()],
    service: Annotated[UserService, Depends(UserService)],
    authorized_user: Annotated[User, Depends(admin_or_moderator)],
):
    user: User = await service.read_one_user(user_id=user_id, authorized_user=authorized_user)

    return user


@user_router.patch(
    "/{user_id}", response_model=UserReadModel, dependencies=[Depends(admin_user)], status_code=status.HTTP_200_OK
)
async def update_one_user(
    user_id: Annotated[uuid.UUID, Path()],
    service: Annotated[UserService, Depends(UserService)],
    s3: Annotated[aioboto3.Session.client, Depends(get_aws_s3_client)],
    data: Annotated[UserUpdateModel, Depends(UserUpdateModel.as_form)],
    file: UploadFile = File(default=None),
):
    user: User = await service.update_user(
        user_id=user_id, file=file, user_data=data.model_dump(exclude_none=True), s3=s3
    )

    return user


@user_router.delete("/{user_id}", dependencies=[Depends(admin_user)], status_code=status.HTTP_200_OK)
async def delete_one_user(
    user_id: uuid.UUID,
    service: Annotated[UserService, Depends(UserService)],
):
    deleted_user_id = await service.delete_user(user_id=user_id)

    return {"user_id": deleted_user_id}


@user_router.get("s", response_model=UserListReadModel, status_code=status.HTTP_200_OK)
async def user_list(
    service: Annotated[UserService, Depends(UserService)],
    authorized_user: Annotated[User, Depends(admin_or_moderator)],
    page: int = Query(ge=1, default=1),
    limit: int = Query(ge=1, default=50),
    sort_by: str = Query(default="username"),
    filter_by_name: Optional[str] = Query(default=None),
    order_by: str = Query(default="asc"),
):
    """Endpoint '/users'"""
    response: Dict = await service.read_user_list(
        page=page,
        limit=limit,
        sort_field=sort_by,
        name=filter_by_name,
        ord_direction=order_by,
        authorized_user=authorized_user,
    )

    return response
