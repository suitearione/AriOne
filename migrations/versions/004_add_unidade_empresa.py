"""Adicionar coluna unidade na tabela empresas

Revision ID: 004_add_unidade_empresa
Revises: 003_alterar_empresas_nullable
Create Date: 2026-05-20

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004_add_unidade_empresa'
down_revision = '003_alterar_empresas_nullable'
branch_labels = None
depends_on = None


def upgrade():
    # Adicionar coluna unidade na tabela empresas
    op.add_column('empresas', sa.Column('unidade', sa.String(10), nullable=False, server_default='MATRIZ'))


def downgrade():
    # Remover coluna unidade da tabela empresas
    op.drop_column('empresas', 'unidade')
