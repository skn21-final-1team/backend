"""add report workflow checkpoint tables

Revision ID: d71e9c926cb3
Revises: a3f2b1c4d5e6
Create Date: 2026-03-26 13:53:24.748651

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d71e9c926cb3"
down_revision: Union[str, Sequence[str], None] = "a3f2b1c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "report_workflow_checkpoint",
        sa.Column("thread_id", sa.String(), nullable=False),
        sa.Column("checkpoint_ns", sa.String(), nullable=False),
        sa.Column("checkpoint_id", sa.String(), nullable=False),
        sa.Column("parent_checkpoint_id", sa.String(), nullable=True),
        sa.Column("checkpoint_type", sa.String(), nullable=False),
        sa.Column("checkpoint_data", sa.LargeBinary(), nullable=False),
        sa.Column("metadata_type", sa.String(), nullable=False),
        sa.Column("metadata_data", sa.LargeBinary(), nullable=False),
        sa.PrimaryKeyConstraint(
            "thread_id",
            "checkpoint_ns",
            "checkpoint_id",
            name=op.f("report_workflow_checkpoint_pkey"),
        ),
    )

    op.create_table(
        "report_workflow_checkpoint_blob",
        sa.Column("thread_id", sa.String(), nullable=False),
        sa.Column("checkpoint_ns", sa.String(), nullable=False),
        sa.Column("channel", sa.String(), nullable=False),
        sa.Column("version", sa.String(), nullable=False),
        sa.Column("value_type", sa.String(), nullable=False),
        sa.Column("value", sa.LargeBinary(), nullable=False),
        sa.PrimaryKeyConstraint(
            "thread_id",
            "checkpoint_ns",
            "channel",
            "version",
            name=op.f("report_workflow_checkpoint_blob_pkey"),
        ),
    )

    op.create_table(
        "report_workflow_checkpoint_write",
        sa.Column("thread_id", sa.String(), nullable=False),
        sa.Column("checkpoint_ns", sa.String(), nullable=False),
        sa.Column("checkpoint_id", sa.String(), nullable=False),
        sa.Column("task_id", sa.String(), nullable=False),
        sa.Column("idx", sa.Integer(), nullable=False),
        sa.Column("channel", sa.String(), nullable=False),
        sa.Column("value_type", sa.String(), nullable=False),
        sa.Column("value", sa.LargeBinary(), nullable=False),
        sa.Column("task_path", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint(
            "thread_id",
            "checkpoint_ns",
            "checkpoint_id",
            "task_id",
            "idx",
            name=op.f("report_workflow_checkpoint_write_pkey"),
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("report_workflow_checkpoint_write")
    op.drop_table("report_workflow_checkpoint_blob")
    op.drop_table("report_workflow_checkpoint")
