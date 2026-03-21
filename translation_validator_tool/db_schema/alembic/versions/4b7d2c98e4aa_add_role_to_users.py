"""add role to users

Revision ID: 4b7d2c98e4aa
Revises: 96913a82204b
Create Date: 2026-03-21 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4b7d2c98e4aa'
down_revision = '96913a82204b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('role', sa.String(length=20), nullable=True, server_default='validador'))

    # Preserve admin users in existing datasets.
    op.execute("UPDATE users SET role = 'admin' WHERE is_superuser = true")
    op.execute("UPDATE users SET role = 'validador' WHERE role IS NULL")

    op.alter_column('users', 'role', nullable=False, server_default='validador')


def downgrade() -> None:
    op.drop_column('users', 'role')
