"""add constraints correct 

Revision ID: 893d8af53916
Revises: 9497bdad2952
Create Date: 2025-06-09 17:40:42.316040

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '893d8af53916'
down_revision: Union[str, None] = '9497bdad2952'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('fragrance_similar_fragrance_constraint', 'similar_fragrance', ['fragrance_id', 'fragrance_that_similar_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fragrance_similar_fragrance_constraint', 'similar_fragrance', type_='unique')
    # ### end Alembic commands ###
