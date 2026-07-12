"""add enhanced ai log fields

Revision ID: a1b2c3d4e5f6
Revises: 213eea8e6750
Create Date: 2026-07-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '213eea8e6750'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('ai_logs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('input_tokens', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('output_tokens', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('success', sa.Boolean(), nullable=False, server_default=sa.text('1')))
        batch_op.add_column(sa.Column('error_message', sa.Text(), nullable=True))
        batch_op.create_index(batch_op.f('ix_ai_logs_success'), ['success'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('ai_logs', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_ai_logs_success'))
        batch_op.drop_column('error_message')
        batch_op.drop_column('success')
        batch_op.drop_column('output_tokens')
        batch_op.drop_column('input_tokens')
