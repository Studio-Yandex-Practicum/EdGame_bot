"""New Users' fields

Revision ID: fb15e58aa783
Revises: 7a548d27b121
Create Date: 2023-08-29 17:24:02.429715

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "fb15e58aa783"
down_revision: Union[str, None] = "7a548d27b121"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "users",
        sa.Column("group", sa.Integer(), nullable=False, server_default="1"),
    )


def downgrade():
    op.drop_column("users", "group")
