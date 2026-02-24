"""add dynamic refresh fields to manual_map_pins (profile_url, latest_content_*)

Revision ID: ref004
Revises: ref003
Create Date: 2026-02-21

"""
from alembic import op
import sqlalchemy as sa

revision = 'ref004'
down_revision = 'ref003'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('manual_map_pins', sa.Column('profile_url', sa.String(1024), nullable=True))
    op.add_column('manual_map_pins', sa.Column('latest_content_url', sa.String(1024), nullable=True))
    op.add_column('manual_map_pins', sa.Column('latest_content_thumbnail', sa.String(1024), nullable=True))
    op.add_column('manual_map_pins', sa.Column('latest_content_title', sa.String(512), nullable=True))
    op.add_column('manual_map_pins', sa.Column('content_fetched_at', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('manual_map_pins', 'content_fetched_at')
    op.drop_column('manual_map_pins', 'latest_content_title')
    op.drop_column('manual_map_pins', 'latest_content_thumbnail')
    op.drop_column('manual_map_pins', 'latest_content_url')
    op.drop_column('manual_map_pins', 'profile_url')
