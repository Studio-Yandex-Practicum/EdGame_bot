"""change counselor -> counsellor

Revision ID: 539226c89111
Revises: b44a11bc64cf
Create Date: 2023-11-22 12:59:55.821679

"""
import hashlib
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '539226c89111'
down_revision: Union[str, None] = 'b44a11bc64cf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('passwords', sa.Column('counsellor_pass', sa.String(length=256), nullable=True))
    data_upgrades()
    op.alter_column('passwords', 'counsellor_pass', type_=sa.String(length=256), nullable=False)
    op.drop_column('passwords', 'counselor_pass')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('passwords', sa.Column('counselor_pass', sa.VARCHAR(length=256), autoincrement=False, nullable=True))
    data_downgrades()
    op.alter_column('passwords', 'counselor_pass', type_=sa.String(length=256), nullable=False)
    op.drop_column('passwords', 'counsellor_pass')
    # ### end Alembic commands ###


def data_upgrades():
    t_passwords = sa.Table(
        'passwords',
        sa.MetaData(),
        sa.Column('id', sa.Integer()),
        sa.Column('master_pass', sa.String(length=256)),
        sa.Column('counselor_pass', sa.String(length=256)),
        sa.Column('counsellor_pass', sa.String(length=256)),
        sa.Column('methodist_pass', sa.String(length=256)),
    )

    t_users = sa.Table(
        'users',
        sa.MetaData(),
        sa.Column('user_id', sa.BigInteger()),
        sa.Column('name', sa.String(length=50)),
        sa.Column('role', sa.String()),
        sa.Column('language', sa.String()),
        sa.Column('user_score', sa.Integer()),
        sa.Column('group', sa.Integer()),
        sa.Column('team_id', sa.Integer()),
        sa.Column('captain_of_team_id', sa.Integer()),
    )

    connection = op.get_bind()

    psw_counsellor_hash = hashlib.sha256('counsellor'.encode())
    psw = psw_counsellor_hash.hexdigest()

    connection.execute(
        t_passwords.update()
        .values(counsellor_pass=psw)
    )

    connection.execute(
        t_users.update()
        .where(t_users.c.role == 'counselor')
        .values(role='counsellor')
    )


def data_downgrades():
    t_passwords = sa.Table(
        'passwords',
        sa.MetaData(),
        sa.Column('id', sa.Integer()),
        sa.Column('master_pass', sa.String(length=256)),
        sa.Column('counselor_pass', sa.String(length=256)),
        sa.Column('counsellor_pass', sa.String(length=256)),
        sa.Column('methodist_pass', sa.String(length=256)),
    )

    t_users = sa.Table(
        'users',
        sa.MetaData(),
        sa.Column('user_id', sa.BigInteger()),
        sa.Column('name', sa.String(length=50)),
        sa.Column('role', sa.String()),
        sa.Column('language', sa.String()),
        sa.Column('user_score', sa.Integer()),
        sa.Column('group', sa.Integer()),
        sa.Column('team_id', sa.Integer()),
        sa.Column('captain_of_team_id', sa.Integer()),
    )

    connection = op.get_bind()

    psw_counsellor_hash = hashlib.sha256('counselor'.encode())
    psw = psw_counsellor_hash.hexdigest()

    connection.execute(
        t_passwords.update()
        .values(counselor_pass=psw)
    )

    connection.execute(
        t_users.update()
        .where(t_users.c.role == 'counsellor')
        .values(role='counselor')
    )