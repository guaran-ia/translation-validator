"""make guarani_text nullable

Revision ID: a1b2c3d4e5f6
Revises: 4b7d2c98e4aa
Create Date: 2026-03-23 11:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '4b7d2c98e4aa'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Change guarani_text from NOT NULL to nullable
    op.alter_column('translations', 'guarani_text',
               existing_type=sa.Text(),
               nullable=True)


def downgrade() -> None:
    # Change guarani_text back to NOT NULL
    op.alter_column('translations', 'guarani_text',
               existing_type=sa.Text(),
               nullable=False)
