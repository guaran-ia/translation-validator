"""Add assigned_to_user_id to annotations table

Revision ID: 20260323172407
Revises: d3e4f5a6b7c8
Create Date: 2026-03-23 17:24:07.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260323172407'
down_revision = 'd3e4f5a6b7c8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add assigned_to_user_id column to annotations table
    op.add_column('annotations', sa.Column('assigned_to_user_id', sa.Integer(), nullable=True))
    
    # Create foreign key constraint
    op.create_foreign_key(
        'fk_annotations_assigned_to_user_id',
        'annotations',
        'users',
        ['assigned_to_user_id'],
        ['id']
    )


def downgrade() -> None:
    # Drop foreign key constraint
    op.drop_constraint('fk_annotations_assigned_to_user_id', 'annotations', type_='foreignkey')
    
    # Drop column
    op.drop_column('annotations', 'assigned_to_user_id')
