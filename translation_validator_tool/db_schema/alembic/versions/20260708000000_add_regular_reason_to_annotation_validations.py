"""Add regular reason to annotation validations

Revision ID: 20260708000000
Revises: 20260701000003
Create Date: 2026-07-08 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260708000000'
down_revision = '20260701000003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('annotation_validations', sa.Column('regular_reason', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('annotation_validations', 'regular_reason')
