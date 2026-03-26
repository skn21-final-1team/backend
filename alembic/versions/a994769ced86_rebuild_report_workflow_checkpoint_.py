"""rebuild report workflow checkpoint schema

Revision ID: a994769ced86
Revises: d71e9c926cb3
Create Date: 2026-03-26 14:12:45.054637

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "a994769ced86"
down_revision: Union[str, Sequence[str], None] = "d71e9c926cb3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Legacy checkpoint migration was removed; keep this revision only for chain continuity.
    pass


def downgrade() -> None:
    """Downgrade schema."""
    # The schema now belongs to d71e9c926cb3, so this revision intentionally does nothing.
    pass
