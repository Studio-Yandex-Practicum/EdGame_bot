"""season class

Revision ID: 57833050f777
Revises: c4c144c103ab
Create Date: 2023-12-05 14:36:21.542255

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '57833050f777'
down_revision: Union[str, None] = 'c4c144c103ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('season',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('open_season', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('close_season', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('season')
    # ### end Alembic commands ###
