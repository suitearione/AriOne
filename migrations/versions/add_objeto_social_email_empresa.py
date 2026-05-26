"""add objeto_social and email to empresas

Revision ID: add_objeto_social_email
Revises: 38f5ca33d12a
Create Date: 2024-05-22

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_objeto_social_email'
down_revision = '38f5ca33d12a'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('empresas', sa.Column('objeto_social', sa.String(50), nullable=True))
    op.add_column('empresas', sa.Column('email', sa.String(200), nullable=True))


def downgrade():
    op.drop_column('empresas', 'email')
    op.drop_column('empresas', 'objeto_social')
