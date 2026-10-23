"""Make all non-admin users both translator and validator

Revision ID: 20260714000000
Revises: 20260708000000
Create Date: 2026-07-14 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260714000000'
down_revision = '20260708000000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE users SET role = 'ambos' WHERE is_superuser = false AND role <> 'admin'")
    op.alter_column(
        'users',
        'role',
        existing_type=sa.String(length=20),
        server_default='ambos',
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        'users',
        'role',
        existing_type=sa.String(length=20),
        server_default='ambos',
        existing_nullable=False,
    )
