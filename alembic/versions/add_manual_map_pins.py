"""add manual_map_pins table (admin-added store pins, no Places API)

Revision ID: ref003
Revises: ref002
Create Date: 2026-02-21

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = 'ref003'
down_revision = 'ref002'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'manual_map_pins',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )


def downgrade():
    op.drop_table('manual_map_pins')
