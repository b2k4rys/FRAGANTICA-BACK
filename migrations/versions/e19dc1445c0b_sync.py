"""sync

Revision ID: e19dc1445c0b
Revises: 
Create Date: 2025-05-16 00:38:30.756310

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e19dc1445c0b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    # Check if role enum exists to avoid duplication
    role_enum = sa.Enum('admin', 'user', name='role')
    if not op.get_bind().dialect.has_type(op.get_bind(), 'role'):
        role_enum.create(op.get_bind())
    # Add role column if not exists
    op.add_column('users', sa.Column('role', role_enum, nullable=False, server_default='user'))

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'role')
    sa.Enum('admin', 'user', name='role').drop(op.get_bind())