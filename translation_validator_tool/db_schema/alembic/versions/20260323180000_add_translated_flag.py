"""Add translated flag to annotations.

Revision ID: 20260323180000
Revises: 20260323172407
Create Date: 2026-03-23 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '20260323180000'
down_revision = '20260323172407'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add translated column - simple boolean (if not exists)
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('annotations')]
    
    if 'translated' not in columns:
        op.add_column('annotations', sa.Column('translated', sa.Boolean(), server_default='false'))


def downgrade() -> None:
    # Remove translated column
    op.drop_column('annotations', 'translated')
