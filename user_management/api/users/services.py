import uuid
from typing import Annotated, Dict, Optional

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

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="page not found")

        return user

    async def update_user(self, user_id: uuid.UUID, user_data: UserUpdateModel) -> User:
        updated_user: User = await self.manager.update_user(
            user_id=user_id, user_data=user_data.model_dump(exclude_unset=True)
        )

        return updated_user

    async def delete_user(self, user_id: uuid.UUID) -> uuid.UUID:
        deleted_user_id: uuid.UUID = await self.manager.delete_user(user_id=user_id)

        return deleted_user_id

    async def get_list(
        self,
        authorized_user: User = Depends(admin_or_moderator),
        page: int = 1,
        limit: int = 50,
        name: Optional[str] = None,
        sort_field: Optional[str] = None,
        ord_direction: str = "asc",
    ):
        offset: int = (page - 1) * limit

        result: Dict = await self.manager.get_all(
            limit=limit,
            offset=offset,
            name=name,
            sort_field=sort_field,
            ord_direction=ord_direction,
            authorized_user=authorized_user,
        )

        total_pages = (result["total_count"] + limit - 1) // limit

        if page > total_pages:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="page not found")

        result.update({"page": page, "limit": limit, "total_pages": total_pages})

        return result
