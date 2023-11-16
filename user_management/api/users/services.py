import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status

from user_management.api.dependencies import admin_or_moderator
from user_management.api.users.schemas import UserUpdateModel
from user_management.database.models import User
from user_management.managers.user_manager import UserManager


class UserService:
    manager = UserManager()

    async def get_one_user_info(
        self, user_id: uuid.UUID, authorized_user: Annotated[User, Depends(admin_or_moderator)]
    ) -> User:
        user: User = await self.manager.get_by_id(user_id)
        if authorized_user.role.role_name == "MODERATOR" and authorized_user.group_id != user.group_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid role")

        return user

    async def update_user(self, user_id: uuid.UUID, user_data: UserUpdateModel) -> User:
        updated_user: User = await self.manager.update_user(
            user_id=user_id, user_data=user_data.model_dump(exclude_unset=True)
        )

        return updated_user

    async def delete_user(self, user_id: uuid.UUID) -> uuid.UUID:
        deleted_user_id: uuid.UUID = await self.manager.delete_user(user_id=user_id)

        return deleted_user_id
