"""add auth_provider to users and create refresh_tokens table

Revision ID: 001
Revises:
Create Date: 2026-02-11 11:28:00

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("users", "password", existing_type=sa.String(), nullable=True)
    op.add_column("users", sa.Column("auth_provider", sa.String(), nullable=False, server_default="local"))

    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("token_hash", sa.String(), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("refresh_tokens")
    op.drop_column("users", "auth_provider")
    op.alter_column("users", "password", existing_type=sa.String(), nullable=False)
