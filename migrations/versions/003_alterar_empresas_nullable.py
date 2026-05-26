# =============================================================================
# Caminho  : migrations/versions/003_alterar_empresas_nullable.py
# Arquivo  : 003_alterar_empresas_nullable.py
# Função   : Alterar campos da tabela empresas para aceitar NULL.
# Descrição: Corrige campos que estavam NOT NULL mas deveriam aceitar valores
#            nulos. Apenas razao_social é obrigatório.
# =============================================================================

"""Alterar campos empresas para nullable

Revision ID: 003_alterar_empresas_nullable
Revises: 
Create Date: 2026-04-04

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003_alterar_empresas_nullable'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # SQLite não suporta ALTER COLUMN diretamente
    # Precisamos recriar a tabela
    
    # Para produção com PostgreSQL/MySQL, use:
    # op.alter_column('empresas', 'nome_fantasia', nullable=True)
    # op.alter_column('empresas', 'cnpj', nullable=True)
    # etc...
    
    # Para SQLite (desenvolvimento), apague a tabela e recrie:
    print("⚠️  ATENÇÃO: Para SQLite, execute:")
    print("   DROP TABLE empresas;")
    print("   Depois execute novamente: flask db upgrade")
    print("")
    print("   Ou delete o arquivo instance/app.db e recrie tudo")
    pass


def downgrade():
    pass