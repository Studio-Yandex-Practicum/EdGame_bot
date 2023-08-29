"""New Users' field

Revision ID: f277b59882ea
Revises: fb15e58aa783
Create Date: 2023-08-29 17:30:44.690524

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f277b59882ea"
down_revision: Union[str, None] = "fb15e58aa783"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "users",
        sa.Column("group", sa.Integer(), nullable=False, server_default="1"),
    )
    op.drop_column("users", "group_id")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "users",
        sa.Column(
            "group_id", sa.INTEGER(), autoincrement=False, nullable=False
        ),
    )
    op.drop_column("users", "group")
    # ### end Alembic commands ###
