"""Add multi-user annotation support with AnnotationAssignment and AnnotationTranslation tables

Revision ID: 20250101000001
Revises: 20260324100000
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20250101000001'
down_revision: Union[str, None] = '20260324100000'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Migration UP: Create new tables for multi-user annotation support
    """
    # 1. Create annotation_assignments table (many-to-many)
    op.create_table(
        'annotation_assignments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('annotation_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('assigned_at', sa.DateTime(), server_default=sa.func.current_timestamp(), nullable=False),
        sa.ForeignKeyConstraint(['annotation_id'], ['annotations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('annotation_id', 'user_id', name='uq_annotation_user')
    )
    op.create_index('ix_annotation_assignments_annotation_id', 'annotation_assignments', ['annotation_id'])
    op.create_index('ix_annotation_assignments_user_id', 'annotation_assignments', ['user_id'])
    
    # 2. Create annotation_translations table (one-to-many)
    op.create_table(
        'annotation_translations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('annotation_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('question_gn', sa.Text(), nullable=True),
        sa.Column('answer_gn', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.current_timestamp(), nullable=False),
        sa.ForeignKeyConstraint(['annotation_id'], ['annotations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_annotation_translations_annotation_id', 'annotation_translations', ['annotation_id'])
    op.create_index('ix_annotation_translations_user_id', 'annotation_translations', ['user_id'])
    op.create_index('ix_annotation_translations_created_at', 'annotation_translations', ['created_at'])
    
    # 3. Migrate existing data from annotations to annotation_translations and annotation_assignments
    # Insert translations - safely ignore conflicts
    try:
        op.execute("""
            INSERT INTO annotation_translations (annotation_id, user_id, question_gn, answer_gn, created_at)
            SELECT id, assigned_to_user_id, question_gn, answer_gn, updated_at
            FROM annotations
            WHERE assigned_to_user_id IS NOT NULL 
              AND (question_gn IS NOT NULL OR answer_gn IS NOT NULL)
        """)
    except Exception:
        pass  # Ignore if no data to migrate
    
    # Insert assignments - safely ignore conflicts
    try:
        op.execute("""
            INSERT INTO annotation_assignments (annotation_id, user_id, assigned_at)
            SELECT id, assigned_to_user_id, updated_at
            FROM annotations
            WHERE assigned_to_user_id IS NOT NULL
        """)
    except Exception:
        pass  # Ignore if no data to migrate
    
    # 4. Update translated flag based on translation count
    try:
        op.execute("""
            UPDATE annotations
            SET translated = (
                SELECT COUNT(*) >= 3
                FROM annotation_translations
                WHERE annotation_translations.annotation_id = annotations.id
            )
        """)
    except Exception:
        pass  # Ignore if query fails
    
    # 5. Drop old columns from annotations table
    op.drop_column('annotations', 'assigned_to_user_id')
    op.drop_column('annotations', 'question_gn')
    op.drop_column('annotations', 'answer_gn')


def downgrade() -> None:
    """
    Migration DOWN: Restore old table structure (rollback)
    """
    # 1. Add back columns to annotations table
    op.add_column('annotations', sa.Column('question_gn', sa.Text(), nullable=True))
    op.add_column('annotations', sa.Column('answer_gn', sa.Text(), nullable=True))
    op.add_column('annotations', sa.Column('assigned_to_user_id', sa.Integer(), nullable=True))
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_annotations_assigned_to_user_id',
        'annotations', 'users',
        ['assigned_to_user_id'], ['id'],
        ondelete='SET NULL'
    )
    
    # 2. Restore data from annotation_translations back to annotations
    op.execute("""
        UPDATE annotations
        SET question_gn = at.question_gn,
            answer_gn = at.answer_gn,
            assigned_to_user_id = at.user_id
        FROM annotation_translations at
        WHERE annotations.id = at.annotation_id
        AND at.created_at = (
            SELECT MAX(created_at)
            FROM annotation_translations
            WHERE annotation_id = annotations.id
        )
    """)
    
    # 3. Restore translated flag
    op.execute("""
        UPDATE annotations
        SET translated = (question_gn IS NOT NULL AND answer_gn IS NOT NULL)
    """)
    
    # 4. Drop new tables
    op.drop_index('ix_annotation_translations_created_at', table_name='annotation_translations')
    op.drop_index('ix_annotation_translations_user_id', table_name='annotation_translations')
    op.drop_index('ix_annotation_translations_annotation_id', table_name='annotation_translations')
    op.drop_table('annotation_translations')
    
    op.drop_index('ix_annotation_assignments_user_id', table_name='annotation_assignments')
    op.drop_index('ix_annotation_assignments_annotation_id', table_name='annotation_assignments')
    op.drop_table('annotation_assignments')
