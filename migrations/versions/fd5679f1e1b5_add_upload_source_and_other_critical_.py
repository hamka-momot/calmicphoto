"""Add upload_source and other critical missing columns to photo table

Revision ID: fd5679f1e1b5
Revises: a40d6bb31053
Create Date: 2025-09-20 16:27:36.227664

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fd5679f1e1b5'
down_revision = 'a40d6bb31053'
branch_labels = None
depends_on = None


def upgrade():
    # Add upload_source column (critical for dashboard)
    op.add_column('photo', sa.Column('upload_source', sa.String(50), nullable=True, server_default='file'))
    
    # Add edited_path column for edited photo versions
    op.add_column('photo', sa.Column('edited_path', sa.String(500), nullable=True))


def downgrade():
    # Remove the added columns in reverse order
    op.drop_column('photo', 'edited_path')
    op.drop_column('photo', 'upload_source')
