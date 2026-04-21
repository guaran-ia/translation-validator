"""Add nombre_completo and contacto columns to users table.

Revision ID: 20260421000000
Revises: 20260416000000
Create Date: 2026-04-21 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '20260421000000'
down_revision = '20260416000000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add nombre_completo and contacto columns to users table
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('users')]
    
    if 'nombre_completo' not in columns:
        op.add_column('users', sa.Column('nombre_completo', sa.String(255), nullable=True))
    
    if 'contacto' not in columns:
        op.add_column('users', sa.Column('contacto', sa.String(255), nullable=True))


def downgrade() -> None:
    # Drop columns if they exist
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('users')]
    
    if 'contacto' in columns:
        op.drop_column('users', 'contacto')
    
    if 'nombre_completo' in columns:
        op.drop_column('users', 'nombre_completo')
