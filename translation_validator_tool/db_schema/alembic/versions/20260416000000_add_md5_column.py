"""Add md5 column to annotations table.

Revision ID: 20260416000000
Revises: 20250101000001
Create Date: 2026-04-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '20260416000000'
down_revision = '20250101000001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add md5 column - simple check if not exists
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('annotations')]
    
    if 'md5' not in columns:
        op.add_column('annotations', sa.Column('md5', sa.String(32), nullable=True))
        op.create_index(op.f('ix_annotations_md5'), 'annotations', ['md5'], unique=False)


def downgrade() -> None:
    # Drop index and column if they exist
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('annotations')]
    
    if 'md5' in columns:
        op.drop_index(op.f('ix_annotations_md5'), table_name='annotations')
        op.drop_column('annotations', 'md5')
