"""add performance indexes

Revision ID: b7c8d9e0f1a2
Revises: a1b2c3d4e5f6
Create Date: 2026-07-12 10:00:00.000000

"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'b7c8d9e0f1a2'
down_revision: str | Sequence[str] | None = 'a1b2c3d4e5f6'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table('tickets', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_tickets_client'), ['client'], unique=False)
        batch_op.create_index(batch_op.f('ix_tickets_deadline'), ['deadline'], unique=False)
        batch_op.create_index(batch_op.f('ix_tickets_priority'), ['priority'], unique=False)

    with op.batch_alter_table('emails', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_emails_sender'), ['sender'], unique=False)
        batch_op.create_index(batch_op.f('ix_emails_received_time'), ['received_time'], unique=False)

    with op.batch_alter_table('calendar_events', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_calendar_events_status'), ['status'], unique=False)
        batch_op.create_index(batch_op.f('ix_calendar_events_start_time'), ['start_time'], unique=False)

    with op.batch_alter_table('ai_logs', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_ai_logs_model'), ['model'], unique=False)
        batch_op.create_index(batch_op.f('ix_ai_logs_confidence'), ['confidence'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('ai_logs', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_ai_logs_confidence'))
        batch_op.drop_index(batch_op.f('ix_ai_logs_model'))

    with op.batch_alter_table('calendar_events', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_calendar_events_start_time'))
        batch_op.drop_index(batch_op.f('ix_calendar_events_status'))

    with op.batch_alter_table('emails', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_emails_received_time'))
        batch_op.drop_index(batch_op.f('ix_emails_sender'))

    with op.batch_alter_table('tickets', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_tickets_priority'))
        batch_op.drop_index(batch_op.f('ix_tickets_deadline'))
        batch_op.drop_index(batch_op.f('ix_tickets_client'))
