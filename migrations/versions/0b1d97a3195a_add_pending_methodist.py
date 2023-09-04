"""add pending_methodist

Revision ID: 0b1d97a3195a
Revises: adc94bc15d30
Create Date: 2023-08-17 14:09:43.943649

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '0b1d97a3195a'
down_revision: Union[str, None] = 'adc94bc15d30'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
