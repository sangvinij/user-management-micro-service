import uuid
from datetime import datetime
from typing import Optional

from black import List
from fastapi import Form
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


class UserListReadModel(BaseModel):
    page: int
    limit: int
    total_pages: int
    total_count: int
    users: List[UserReadModel]


class UserUpdateModel(BaseModel):
    name: Optional[str] = Field(min_length=1, default=None)
    surname: Optional[str] = Field(min_length=1, default=None)
    username: Optional[str] = Field(min_length=1, default=None)
    phone_number: Optional[str] = Field(min_length=1, default=None)
    email: Optional[EmailStr] = None
    is_blocked: Optional[bool] = None
    role_id: Optional[int] = None
    group_id: Optional[int] = None

    @classmethod
    def as_form(
        cls,
        name: Optional[str] = Form(min_length=1, default=None),
        surname: Optional[str] = Form(min_length=1, default=None),
        username: Optional[str] = Form(min_length=1, default=None),
        phone_number: Optional[str] = Form(default=None),
        email: Optional[EmailStr] = Form(default=None),
        is_blocked: Optional[bool] = Form(default=False),
        role_id: Optional[int] = Form(default=None),
        group_id: Optional[int] = Form(default=None),
    ):
        return cls(
            name=name,
            surname=surname,
            username=username,
            phone_number=phone_number,
            email=email,
            is_blocked=is_blocked,
            role_id=role_id,
            group_id=group_id,
        )
