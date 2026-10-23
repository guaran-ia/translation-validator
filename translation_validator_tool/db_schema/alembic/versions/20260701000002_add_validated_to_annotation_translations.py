"""Add validated flag to annotation translations

Revision ID: 20260701000002
Revises: 20260701000001
Create Date: 2026-07-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260701000002'
down_revision = '20260701000001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'annotation_translations',
        sa.Column('validated', sa.Boolean(), nullable=False, server_default=sa.text('false')),
    )


def downgrade() -> None:
    op.drop_column('annotation_translations', 'validated')
