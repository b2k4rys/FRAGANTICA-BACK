"""add url field

Revision ID: d4824f422e23
Revises: a630af215cf4
Create Date: 2025-05-11 21:14:42.830219

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4824f422e23'
down_revision: Union[str, None] = 'a630af215cf4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
