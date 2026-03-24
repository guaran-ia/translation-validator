"""Make question_es and answer_es nullable in annotations table.

Revision ID: 20260324100000
Revises: 20260323180000
Create Date: 2026-03-24 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260324100000'
down_revision = '20260323180000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Make question_es and answer_es nullable
    op.alter_column('annotations', 'question_es',
               existing_type=sa.Text(),
               nullable=True)
    op.alter_column('annotations', 'answer_es',
               existing_type=sa.Text(),
               nullable=True)


def downgrade() -> None:
    # Revert to NOT NULL
    op.alter_column('annotations', 'question_es',
               existing_type=sa.Text(),
               nullable=False)
    op.alter_column('annotations', 'answer_es',
               existing_type=sa.Text(),
               nullable=False)
