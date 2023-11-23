import uuid
from typing import Dict, Optional

import sqlalchemy.exc

from user_management.api.users.schemas import UserUpdateModel
from user_management.api.utils.exceptions import (
    AlreadyExistsHTTPException,
    NotFoundHTTPException,
    PermissionHTTPException,
)
from user_management.database.models import User
from user_management.managers.user_manager import UserManager


class UserService:
    manager = UserManager()

    async def read_one_user(self, user_id: uuid.UUID, authorized_user: User) -> User:
        user: User = await self.manager.get_by_id(user_id)
        if authorized_user.role.role_name == "MODERATOR" and authorized_user.group_id != user.group_id:
            raise PermissionHTTPException()

        if not user:
            raise NotFoundHTTPException()

        return user

    async def update_user(self, user_id: uuid.UUID, user_data: UserUpdateModel) -> User:
        try:
            updated_user: User = await self.manager.update_user(
                user_id=user_id, user_data=user_data.model_dump(exclude_unset=True)
            )

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

        moderator: Optional[User] = authorized_user if authorized_user.role.role_name == "MODERATOR" else None

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
