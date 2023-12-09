"""admin role

Revision ID: 3e47189e1d61
Revises: 539226c89111
Create Date: 2023-12-05 17:31:02.627923

"""
import hashlib
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '3e47189e1d61'
down_revision: Union[str, None] = '539226c89111'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('season',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('open_season', sa.DateTime(timezone=True),
                              nullable=True),
                    sa.Column('close_season', sa.DateTime(timezone=True),
                              nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.add_column('passwords', sa.Column('kid_pass', sa.String(length=256), nullable=True))
    data_upgrade()
    op.alter_column('passwords', 'kid_pass', type_=sa.String(length=256), nullable=False)

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('passwords', 'kid_pass')
    op.drop_table('season')
    # ### end Alembic commands ###


def data_upgrade():
    t_passwords = sa.Table(
        'passwords',
        sa.MetaData(),
        sa.Column('id', sa.Integer()),
        sa.Column('master_pass', sa.String(length=256)),
        sa.Column('counsellor_pass', sa.String(length=256)),
        sa.Column('methodist_pass', sa.String(length=256)),
        sa.Column('kid_pass', sa.String(length=256)),
    )
    connection = op.get_bind()

    psw_kid_hash = hashlib.sha256('student'.encode())
    psw = psw_kid_hash.hexdigest()

    connection.execute(
        t_passwords.update()
        .values(kid_pass=psw)
    )
