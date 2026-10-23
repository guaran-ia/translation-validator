"""make spanish_text required

Revision ID: c2d3e4f5a6b7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-23 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c2d3e4f5a6b7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Change spanish_text from nullable to NOT NULL
    op.alter_column('translations', 'spanish_text',
               existing_type=sa.Text(),
               nullable=False)


def downgrade() -> None:
    # Change spanish_text back to nullable
    op.alter_column('translations', 'spanish_text',
               existing_type=sa.Text(),
               nullable=True)
