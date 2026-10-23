"""Add validated flag to annotations

Revision ID: 20260701000001
Revises: 20260701000000
Create Date: 2026-07-01 00:00:01.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260701000001'
down_revision = '20260701000000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'annotations',
        sa.Column('validated', sa.Boolean(), nullable=False, server_default=sa.text('false')),
    )


def downgrade() -> None:
    op.drop_column('annotations', 'validated')
