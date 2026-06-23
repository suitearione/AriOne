"""merge heads

Revision ID: e63390d0d654
Revises: 006_merge_heads, 38f5ca33d12a, criar_tabela_versoes, add_empresa_id_clientes_fornecedores
Create Date: 2026-06-17 12:15:47.480562

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e63390d0d654'
down_revision = ('006_merge_heads', '38f5ca33d12a', 'criar_tabela_versoes', 'add_empresa_id_clientes_fornecedores')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
