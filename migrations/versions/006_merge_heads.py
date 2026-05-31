"""Merge migration heads

Revision ID: 006_merge_heads
Revises: c612dc5e68ad
Create Date: 2026-05-30

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006_merge_heads'
down_revision = 'c612dc5e68ad'
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
