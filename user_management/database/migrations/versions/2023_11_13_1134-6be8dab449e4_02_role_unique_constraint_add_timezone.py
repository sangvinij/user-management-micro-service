"""02_role_unique_constraint_add_timezone

Revision ID: 6be8dab449e4
Revises: 659a17349c0d
Create Date: 2023-11-13 11:34:37.816733+03:00

"""
from typing import Optional, Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "6be8dab449e4"
down_revision: Optional[str] = "659a17349c0d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "group",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.TIMESTAMP(timezone=True),
        existing_nullable=False,
    )
    op.create_unique_constraint(None, "role", ["role_name"])
    op.alter_column(
        "user",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.TIMESTAMP(timezone=True),
        existing_nullable=False,
    )
    op.alter_column(
        "user",
        "modified_at",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.TIMESTAMP(timezone=True),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "user",
        "modified_at",
        existing_type=sa.TIMESTAMP(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False,
    )
    op.alter_column(
        "user",
        "created_at",
        existing_type=sa.TIMESTAMP(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False,
    )
    op.drop_constraint("", "role", type_="unique")
    op.alter_column(
        "group",
        "created_at",
        existing_type=sa.TIMESTAMP(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False,
    )
