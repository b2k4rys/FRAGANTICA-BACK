"""add perfumer

Revision ID: 3869256d5e83
Revises: 2a64f8f9a872
Create Date: 2025-06-10 22:02:53.189714

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3869256d5e83'
down_revision: Union[str, None] = '2a64f8f9a872'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('perfumer',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.add_column('fragrance', sa.Column('perfumer_id', sa.BigInteger(), nullable=True))
    op.create_foreign_key(None, 'fragrance', 'perfumer', ['perfumer_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'fragrance', type_='foreignkey')
    op.drop_column('fragrance', 'perfumer_id')
    op.drop_table('perfumer')
    # ### end Alembic commands ###
