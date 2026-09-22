"""add cat categorias fields

Revision ID: 20260919_cat_categorias_fields
Revises: 20260919_transportadoras_fields
Create Date: 2026-09-19

"""
from alembic import op
import sqlalchemy as sa


revision = "20260919_cat_categorias_fields"
down_revision = "20260919_transportadoras_fields"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("cat_categorias", schema=None) as batch_op:
        batch_op.add_column(sa.Column("descricao", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("cor", sa.String(length=20), nullable=True, server_default="#27AE60"))
        batch_op.add_column(sa.Column("icone", sa.String(length=50), nullable=True, server_default="fa-layer-group"))


def downgrade():
    with op.batch_alter_table("cat_categorias", schema=None) as batch_op:
        batch_op.drop_column("icone")
        batch_op.drop_column("cor")
        batch_op.drop_column("descricao")
