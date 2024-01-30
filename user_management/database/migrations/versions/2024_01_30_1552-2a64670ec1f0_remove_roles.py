"""remove roles

Revision ID: 2a64670ec1f0
Revises: 199c5bda72b5
Create Date: 2024-01-30 15:52:08.527091+03:00

"""
from typing import Sequence, Union, Optional

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "2a64670ec1f0"
down_revision: Optional[str] = "199c5bda72b5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user",
        sa.Column(
            "role", sa.Enum("USER", "ADMIN", "MODERATOR", name="user_role"), server_default="USER", nullable=False
        ),
    )
    op.alter_column("user", "name", existing_type=sa.VARCHAR(length=255), nullable=True)
    op.alter_column("user", "surname", existing_type=sa.VARCHAR(length=255), nullable=True)
    op.alter_column("user", "image_s3_path", existing_type=sa.VARCHAR(length=255), nullable=True)
    op.alter_column("user", "group_id", existing_type=sa.INTEGER(), nullable=True)
    op.drop_constraint("user_role_id_fkey", "user", type_="foreignkey")
    op.drop_column("user", "role_id")
    op.drop_table("role")


def downgrade() -> None:
    op.create_table(
        "role",
        sa.Column("role_id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column(
            "role_name",
            postgresql.ENUM("USER", "ADMIN", "MODERATOR", name="user_role"),
            autoincrement=False,
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("role_id", name="role_pkey"),
        sa.UniqueConstraint("role_name", name="uq_role_role_name"),
    )

    op.add_column("user", sa.Column("role_id", sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key("user_role_id_fkey", "user", "role", ["role_id"], ["role_id"])
    op.alter_column("user", "group_id", existing_type=sa.INTEGER(), nullable=False)
    op.alter_column("user", "image_s3_path", existing_type=sa.VARCHAR(length=255), nullable=False)
    op.alter_column("user", "surname", existing_type=sa.VARCHAR(length=255), nullable=False)
    op.alter_column("user", "name", existing_type=sa.VARCHAR(length=255), nullable=False)
    op.drop_column("user", "role")
