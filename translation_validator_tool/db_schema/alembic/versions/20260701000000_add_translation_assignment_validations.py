"""Add concrete translation assignments to annotation validations

Revision ID: 20260701000000
Revises: 4a4d65260082
Create Date: 2026-07-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260701000000'
down_revision = '4a4d65260082'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint('unique_user_annotation_part', 'annotation_validations', type_='unique')

    op.add_column('annotation_validations', sa.Column('translation_id', sa.Integer(), nullable=False))
    op.add_column(
        'annotation_validations',
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
    )
    op.create_foreign_key(
        'fk_annotation_validations_translation_id',
        'annotation_validations',
        'annotation_translations',
        ['translation_id'],
        ['id'],
    )
    op.create_unique_constraint(
        'unique_user_translation_part',
        'annotation_validations',
        ['translation_id', 'user_id', 'part_type'],
    )
    op.create_index(
        'ix_annotation_validations_user_status_part',
        'annotation_validations',
        ['user_id', 'status', 'part_type'],
    )
    op.create_index(
        'ix_annotation_validations_translation_status_part',
        'annotation_validations',
        ['translation_id', 'status', 'part_type'],
    )

    op.alter_column(
        'annotation_validations',
        'correctness',
        existing_type=sa.String(length=20),
        nullable=True,
    )
    op.alter_column(
        'annotation_validations',
        'fluency_score',
        existing_type=sa.Integer(),
        nullable=True,
    )
    op.alter_column(
        'annotation_validations',
        'accuracy_score',
        existing_type=sa.Integer(),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        'annotation_validations',
        'accuracy_score',
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.alter_column(
        'annotation_validations',
        'fluency_score',
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.alter_column(
        'annotation_validations',
        'correctness',
        existing_type=sa.String(length=20),
        nullable=False,
    )

    op.drop_index('ix_annotation_validations_translation_status_part', table_name='annotation_validations')
    op.drop_index('ix_annotation_validations_user_status_part', table_name='annotation_validations')
    op.drop_constraint('unique_user_translation_part', 'annotation_validations', type_='unique')
    op.drop_constraint('fk_annotation_validations_translation_id', 'annotation_validations', type_='foreignkey')
    op.drop_column('annotation_validations', 'status')
    op.drop_column('annotation_validations', 'translation_id')
    op.create_unique_constraint(
        'unique_user_annotation_part',
        'annotation_validations',
        ['annotation_id', 'user_id', 'part_type'],
    )
