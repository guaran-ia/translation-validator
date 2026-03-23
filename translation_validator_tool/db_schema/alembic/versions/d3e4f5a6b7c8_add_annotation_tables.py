"""Add annotation tables for question-answer translation

Revision ID: d3e4f5a6b7c8
Revises: c2d3e4f5a6b7
Create Date: 2026-03-23 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd3e4f5a6b7c8'
down_revision = 'c2d3e4f5a6b7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create annotations table
    op.create_table(
        'annotations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('question_es', sa.Text(), nullable=False),
        sa.Column('question_gn', sa.Text(), nullable=True),
        sa.Column('answer_es', sa.Text(), nullable=False),
        sa.Column('answer_gn', sa.Text(), nullable=True),
        sa.Column('answer_number', sa.Integer(), nullable=True),
        sa.Column('equation_solution', sa.Text(), nullable=True),
        sa.Column('source', sa.String(255), nullable=False, server_default='GuaranIA'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_annotations_id'), 'annotations', ['id'], unique=False)

    # Create annotation_suggestions table FIRST (before annotation_validations since it references it)
    op.create_table(
        'annotation_suggestions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('annotation_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('part_type', sa.String(20), nullable=False, server_default='both'),
        sa.Column('suggested_question_gn', sa.Text(), nullable=True),
        sa.Column('suggested_answer_gn', sa.Text(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('is_promoted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['annotation_id'], ['annotations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_annotation_suggestions_id'), 'annotation_suggestions', ['id'], unique=False)

    # Create annotation_validations table
    op.create_table(
        'annotation_validations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('annotation_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('part_type', sa.String(20), nullable=False, server_default='both'),
        sa.Column('correctness', sa.String(20), nullable=False),
        sa.Column('fluency_score', sa.Integer(), nullable=False),
        sa.Column('accuracy_score', sa.Integer(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('suggestion_id', sa.Integer(), nullable=True),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['annotation_id'], ['annotations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['suggestion_id'], ['annotation_suggestions.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('annotation_id', 'user_id', 'part_type', name='unique_user_annotation_part')
    )
    op.create_index(op.f('ix_annotation_validations_id'), 'annotation_validations', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_annotation_validations_id'), table_name='annotation_validations')
    op.drop_table('annotation_validations')
    op.drop_index(op.f('ix_annotation_suggestions_id'), table_name='annotation_suggestions')
    op.drop_table('annotation_suggestions')
    op.drop_index(op.f('ix_annotations_id'), table_name='annotations')
    op.drop_table('annotations')
