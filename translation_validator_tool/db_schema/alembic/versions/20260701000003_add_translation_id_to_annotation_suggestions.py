"""Add translation id to annotation suggestions

Revision ID: 20260701000003
Revises: 20260701000002
Create Date: 2026-07-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260701000003'
down_revision = '20260701000002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('annotation_suggestions', sa.Column('translation_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_annotation_suggestions_translation_id',
        'annotation_suggestions',
        'annotation_translations',
        ['translation_id'],
        ['id'],
    )
    op.create_index(
        'ix_annotation_suggestions_translation_id',
        'annotation_suggestions',
        ['translation_id'],
    )


def downgrade() -> None:
    op.drop_index('ix_annotation_suggestions_translation_id', table_name='annotation_suggestions')
    op.drop_constraint('fk_annotation_suggestions_translation_id', 'annotation_suggestions', type_='foreignkey')
    op.drop_column('annotation_suggestions', 'translation_id')
