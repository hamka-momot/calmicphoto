"""Add missing file_path, thumbnail_path, and mime_type columns to photo table

Revision ID: a40d6bb31053
Revises: 8a4feb80f221
Create Date: 2025-09-20 16:26:16.550337

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a40d6bb31053'
down_revision = '8a4feb80f221'
branch_labels = None
depends_on = None


def upgrade():
    # Add missing file_path column (required)
    op.add_column('photo', sa.Column('file_path', sa.String(500), nullable=False))
    
    # Add missing thumbnail_path column (optional)
    op.add_column('photo', sa.Column('thumbnail_path', sa.String(500), nullable=True))
    
    # Add missing mime_type column (required)
    op.add_column('photo', sa.Column('mime_type', sa.String(50), nullable=False))


def downgrade():
    # Remove the added columns in reverse order
    op.drop_column('photo', 'mime_type')
    op.drop_column('photo', 'thumbnail_path')
    op.drop_column('photo', 'file_path')
