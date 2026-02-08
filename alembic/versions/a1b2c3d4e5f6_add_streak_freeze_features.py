"""Add streak and freeze features

Revision ID: a1b2c3d4e5f6
Revises: f2a1e857e2aa
Create Date: 2026-02-08 10:15:30.123456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'f2a1e857e2aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add columns to users table
    op.add_column('users', sa.Column('freeze_balance', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('freeze_used_in_row', sa.Integer(), nullable=False, server_default='0'))
    
    # Add columns to habits table
    op.add_column('habits', sa.Column('is_freezable', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('habits', sa.Column('danger_start_pct', sa.Float(), nullable=False, server_default='0.7'))
    op.add_column('habits', sa.Column('current_streak', sa.Integer(), nullable=False, server_default='0'))
    
    # Add column to habit_logs table
    op.add_column('habit_logs', sa.Column('status', sa.String(), nullable=False, server_default='pending'))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove columns from habit_logs table
    op.drop_column('habit_logs', 'status')
    
    # Remove columns from habits table
    op.drop_column('habits', 'current_streak')
    op.drop_column('habits', 'danger_start_pct')
    op.drop_column('habits', 'is_freezable')
    
    # Remove columns from users table
    op.drop_column('users', 'freeze_used_in_row')
    op.drop_column('users', 'freeze_balance')
