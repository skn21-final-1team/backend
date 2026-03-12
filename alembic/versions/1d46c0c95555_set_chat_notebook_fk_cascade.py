"""set chat notebook fk cascade

Revision ID: 1d46c0c95555
Revises: b929b4c1090b
Create Date: 2026-03-12 11:30:05.458759

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '1d46c0c95555'
down_revision: Union[str, Sequence[str], None] = 'b929b4c1090b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint("chat_notebook_id_fkey", "chat", type_="foreignkey")
    op.create_foreign_key(
        "chat_notebook_id_fkey",
        "chat",
        "notebook",
        ["notebook_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("chat_notebook_id_fkey", "chat", type_="foreignkey")
    op.create_foreign_key(
        "chat_notebook_id_fkey",
        "chat",
        "notebook",
        ["notebook_id"],
        ["id"],
    )
