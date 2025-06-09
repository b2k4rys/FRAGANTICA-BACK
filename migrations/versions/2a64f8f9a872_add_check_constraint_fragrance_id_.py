"""Add check constraint: fragrance_id <> fragrance_that_similar_id

Revision ID: 2a64f8f9a872
Revises: 7feba4a28023
Create Date: 2025-06-09 17:47:31.384492

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a64f8f9a872'
down_revision: Union[str, None] = '7feba4a28023'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_check_constraint(
        constraint_name="similar_fragrances_constraint",
        table_name="similar_fragrance",
        condition="fragrance_id <> fragrance_that_similar_id"
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
