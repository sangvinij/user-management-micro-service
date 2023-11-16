import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class GroupModel(BaseModel):
    group_id: int
    name: str
    created_at: datetime


class RoleModel(BaseModel):
    role_id: int
    role_name: str


class UserReadModel(BaseModel):
    user_id: uuid.UUID
    name: str
    surname: str
    username: str
    phone_number: str
    email: EmailStr
    image_s3_path: str
    is_blocked: bool
    created_at: datetime
    modified_at: datetime
    role: RoleModel
    group: GroupModel


class UserUpdateModel(BaseModel):
    name: Optional[str] = Field(min_length=1, default=None)
    surname: Optional[str] = Field(min_length=1, default=None)
    username: Optional[str] = Field(min_length=1, default=None)
    phone_number: Optional[str] = Field(min_length=1, default=None)
    email: Optional[EmailStr] = None
    image_s3_path: Optional[str] = Field(min_length=1, default=None)
    is_blocked: Optional[bool] = None
    role_id: Optional[int] = None
    group_id: Optional[int] = None


class UserDeleteModel(BaseModel):
    user_id: uuid.UUID
