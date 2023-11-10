"""02_role_unique_constraint

Revision ID: cfa2955d9526
Revises: 659a17349c0d
Create Date: 2023-11-10 13:39:31.099837+03:00

"""
from typing import Sequence, Union

from alembic import op

revision: str = "cfa2955d9526"
down_revision: Union[str, None] = "659a17349c0d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(None, "role", ["role_name"])


def downgrade() -> None:
    op.drop_constraint("", "role", type_="unique")
