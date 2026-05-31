"""Adicionar colunas valor_diario e data_final na tabela campanhas

Revision ID: 005_add_valor_diario_data_final_campanhas
Revises: 004_add_unidade_empresa
Create Date: 2026-05-30

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '005_add_valor_diario_data_final_campanhas'
down_revision = '004_add_unidade_empresa'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'campanhas',
        sa.Column('valor_diario', sa.Numeric(16, 2), nullable=False, server_default='0.0')
    )
    op.add_column(
        'campanhas',
        sa.Column('data_final', sa.Date(), nullable=True)
    )


def downgrade():
    op.drop_column('campanhas', 'data_final')
    op.drop_column('campanhas', 'valor_diario')
