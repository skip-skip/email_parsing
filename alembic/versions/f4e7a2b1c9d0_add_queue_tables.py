"""add queue tables

Revision ID: f4e7a2b1c9d0
Revises: b7c8d9e0f1a2
Create Date: 2026-07-13 15:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f4e7a2b1c9d0"
down_revision: str | Sequence[str] | None = "b7c8d9e0f1a2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "missing_info_queue",
        sa.Column("ticket_id", sa.Uuid(), nullable=False),
        sa.Column("draft_json", sa.JSON(), nullable=False),
        sa.Column("missing_fields", sa.JSON(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("ticket_id"),
    )
    with op.batch_alter_table("missing_info_queue", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_missing_info_queue_status"), ["status"], unique=False
        )

    op.create_table(
        "scheduling_queue",
        sa.Column("ticket_id", sa.Uuid(), nullable=False),
        sa.Column("suggestion_json", sa.JSON(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("ticket_id"),
    )
    with op.batch_alter_table("scheduling_queue", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_scheduling_queue_status"), ["status"], unique=False
        )


def downgrade() -> None:
    with op.batch_alter_table("scheduling_queue", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_scheduling_queue_status"))
    op.drop_table("scheduling_queue")

    with op.batch_alter_table("missing_info_queue", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_missing_info_queue_status"))
    op.drop_table("missing_info_queue")
