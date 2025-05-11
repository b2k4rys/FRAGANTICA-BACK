"""add url

Revision ID: 7f3d2c07fddd
Revises: d4824f422e23
Create Date: 2025-05-11 21:16:16.115285

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7f3d2c07fddd'
down_revision: Union[str, None] = 'd4824f422e23'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
