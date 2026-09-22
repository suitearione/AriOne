"""add manual purchase cost to products"""

from alembic import op
import sqlalchemy as sa

revision = "20260921_custo_compra_produtos"
down_revision = "20260919_cat_categorias_fields"
branch_labels = None
depends_on = None


def upgrade():
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("cat_produtos")}
    if "custo_compra" not in columns:
        with op.batch_alter_table("cat_produtos", schema=None) as batch_op:
            batch_op.add_column(sa.Column("custo_compra", sa.Float(), nullable=True, server_default="0"))


def downgrade():
    with op.batch_alter_table("cat_produtos", schema=None) as batch_op:
        batch_op.drop_column("custo_compra")