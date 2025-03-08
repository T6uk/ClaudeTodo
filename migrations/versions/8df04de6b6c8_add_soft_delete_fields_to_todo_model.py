"""Add soft delete fields to Todo model

Revision ID: add_soft_delete_to_todo
Revises: previous_revision_id
Create Date: 2025-03-08

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_soft_delete_to_todo'
down_revision = 'previous_revision_id'  # Replace with your previous migration ID
branch_labels = None
depends_on = None


def upgrade():
    # Add deleted and deleted_at columns to todos table
    op.add_column('todos', sa.Column('deleted', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('todos', sa.Column('deleted_at', sa.DateTime(), nullable=True))


def downgrade():
    # Drop the added columns
    op.drop_column('todos', 'deleted_at')
    op.drop_column('todos', 'deleted')