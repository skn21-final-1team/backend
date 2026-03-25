"""add reference_source to chat

Revision ID: a3f2b1c4d5e6
Revises: 8814e0cf60c9
Create Date: 2026-03-25 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a3f2b1c4d5e6'
down_revision: Union[str, Sequence[str], None] = '8814e0cf60c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('chat', sa.Column('reference_source', postgresql.JSONB(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('chat', 'reference_source')
