import uuid
from typing import Dict, Optional

import aioboto3
import sqlalchemy.exc
from fastapi import UploadFile

from user_management.api.utils.exceptions import (
    AlreadyExistsHTTPException,
    NotFoundHTTPException,
    PermissionHTTPException,
)
from user_management.aws.service import AWSService
from user_management.database.models import User
from user_management.logger_settings import logger
from user_management.managers.user_manager import UserManager


class UserService:
    manager = UserManager()

    async def read_one_user(self, user_id: uuid.UUID, authorized_user: User) -> User:
        user: User = await self.manager.get_by_id(user_id)
        if (
            authorized_user.role == "MODERATOR"
            and authorized_user.group_id is not None
            and authorized_user.group_id != user.group_id
        ):
            raise PermissionHTTPException()

        if not user:
            raise NotFoundHTTPException()

        return user

    async def update_user(
        self, user_id: uuid.UUID, user_data: Dict, s3: aioboto3.Session.client, file: Optional[UploadFile] = None
    ) -> User:
        if file:
            aws_service: AWSService = AWSService(aws_client=s3)
            user: User = await self.manager.get_by_id(user_id)
            key: str = user_data["username"] if "username" in user_data else user.username
            image_s3_path: str = await aws_service.upload_image(key=key, file=file)
            user_data["image_s3_path"] = image_s3_path

        try:
            updated_user: User = await self.manager.update_user(user_id=user_id, user_data=user_data)

        except sqlalchemy.exc.IntegrityError:
            raise AlreadyExistsHTTPException(
                detail="user with such credentials already exists",
            )

        if not updated_user:
            raise NotFoundHTTPException()

        return updated_user

    async def delete_user(self, user_id: uuid.UUID) -> uuid.UUID:
        deleted_user_id: uuid.UUID = await self.manager.delete_user(user_id=user_id)

        return deleted_user_id

    async def read_user_list(
        self,
        authorized_user: User,
        page: int = 1,
        limit: int = 50,
        name: Optional[str] = None,
        sort_field: Optional[str] = None,
        ord_direction: str = "asc",
    ):
        offset: int = (page - 1) * limit

        moderator: Optional[User] = authorized_user if authorized_user.role == "MODERATOR" else None

        if moderator and moderator.group_id is None:
            moderator = None

        result: Dict = await self.manager.get_all(
            limit=limit,
            offset=offset,
            name=name,
            sort_field=sort_field,
            ord_direction=ord_direction,
            moderator=moderator,
        )

        total_pages: int = (result["total_count"] + limit - 1) // limit

        if page > total_pages:
            raise NotFoundHTTPException(detail="page not found")

        result.update({"page": page, "limit": limit, "total_pages": total_pages})

        return result
