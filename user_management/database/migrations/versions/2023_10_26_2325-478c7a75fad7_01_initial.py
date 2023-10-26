"""01_initial

Revision ID: 478c7a75fad7
Revises:
Create Date: 2023-10-26 23:25:50.704385

"""
from typing import Optional, Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "478c7a75fad7"
down_revision: Optional[str] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "group",
        sa.Column("group_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False),
        sa.PrimaryKeyConstraint("group_id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "role",
        sa.Column("role_name", sa.Enum("USER", "ADMIN", "MODERATOR", name="user_role"), nullable=False),
        sa.PrimaryKeyConstraint("role_name"),
    )
    op.create_table(
        "user",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("surname", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("phone_number", sa.String(length=20), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("image_s3_path", sa.String(length=255), nullable=False),
        sa.Column("is_blocked", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("modified_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("role_name", sa.Enum("USER", "ADMIN", "MODERATOR", name="user_role"), nullable=False),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["group.group_id"],
        ),
        sa.ForeignKeyConstraint(
            ["role_name"],
            ["role.role_name"],
        ),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("phone_number"),
        sa.UniqueConstraint("username"),
    )


def downgrade() -> None:
    op.drop_table("user")
    op.drop_table("role")
    op.drop_table("group")
