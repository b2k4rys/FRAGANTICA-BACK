"""add url field

Revision ID: a630af215cf4
Revises: b080a7c96212
Create Date: 2025-05-11 21:14:05.040164

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a630af215cf4'
down_revision: Union[str, None] = 'b080a7c96212'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
