"""Recriando tabela de versoes completa

Revision ID: c612dc5e68ad
Revises: 78bb049c5bd9
Create Date: 2026-04-02 11:37:56.977575

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c612dc5e68ad'
down_revision = 'add_objeto_social_email'
branch_labels = None
depends_on = None


def upgrade():
    # NOTA: a tabela 'versoes' ja eh criada pela migration 'criar_tabela_versoes'.
    # Esta migration foi neutralizada (no-op) para evitar conflito de
    # "table already exists" quando o historico de migrations for unificado.
    # Caso a tabela 'versoes' precise de ajustes de schema, criar uma nova
    # migration especifica usando batch_alter_table em vez de recriar a tabela.
    pass


def downgrade():
    # No-op, ver upgrade()
    pass