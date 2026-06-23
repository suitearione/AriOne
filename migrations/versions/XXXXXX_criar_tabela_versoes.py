# =============================================================================
# Caminho  : migrations/versions/XXXXXX_criar_tabela_versoes.py
# Arquivo  : criar_tabela_versoes.py
# Função   : Migração para criar tabela de versionamento do sistema.
# Descrição: Cria tabela 'versoes' com campos para número, título, status,
#            datas, changelog, arquivos modificados e observações.
# =============================================================================

"""Criar tabela versoes

Revision ID: criar_tabela_versoes
Revises: 1f268e9fc294
Create Date: 2026-01-04

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'criar_tabela_versoes'
down_revision = '1f268e9fc294'
branch_labels = None
depends_on = None


def upgrade():
    # Criar tabela versoes
    op.create_table(
        'versoes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero', sa.String(length=20), nullable=False),
        sa.Column('titulo', sa.String(length=200), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('data_inicio', sa.Date(), nullable=True),
        sa.Column('data_publicacao', sa.Date(), nullable=True),
        sa.Column('changelog', sa.Text(), nullable=True),
        sa.Column('arquivos', sa.Text(), nullable=True),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('autor', sa.String(length=100), nullable=True),
        sa.Column('criado_em', sa.DateTime(), nullable=True),
        sa.Column('atualizado_em', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero')
    )


def downgrade():
    # Remover tabela versoes
    op.drop_table('versoes')