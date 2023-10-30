"""01_initial

Revision ID: 659a17349c0d
Revises:
Create Date: 2023-10-30 13:32:26.545108+03:00

"""
from typing import Optional, Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "659a17349c0d"
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
        sa.Column("role_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("role_name", sa.Enum("USER", "ADMIN", "MODERATOR", name="user_role"), nullable=False),
        sa.PrimaryKeyConstraint("role_id"),
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
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["group.group_id"],
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["role.role_id"],
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
