"""add transportadoras model fields

Revision ID: 20260919_transportadoras_fields
Revises: c714416a5fed
Create Date: 2026-09-19

"""
from alembic import op
import sqlalchemy as sa


revision = "20260919_transportadoras_fields"
down_revision = "c714416a5fed"
branch_labels = None
depends_on = None


TRANSPORTADORAS_COLUMNS = (
    ("modal_transporte", sa.String(length=100)),
    ("tipo_servico", sa.String(length=100)),
    ("avaliacao", sa.String(length=1)),
    ("contato_nome", sa.String(length=100)),
    ("contato_cargo", sa.String(length=100)),
    ("parceira_desde", sa.Date()),
    ("end_com_cep", sa.String(length=9)),
    ("end_com_logradouro", sa.String(length=150)),
    ("end_com_numero", sa.String(length=20)),
    ("end_com_complemento", sa.String(length=100)),
    ("end_com_bairro", sa.String(length=80)),
    ("end_com_cidade", sa.String(length=80)),
    ("end_com_uf", sa.String(length=2)),
    ("end_ent_cep", sa.String(length=9)),
    ("end_ent_logradouro", sa.String(length=150)),
    ("end_ent_numero", sa.String(length=20)),
    ("end_ent_complemento", sa.String(length=100)),
    ("end_ent_bairro", sa.String(length=80)),
    ("end_ent_cidade", sa.String(length=80)),
    ("end_ent_uf", sa.String(length=2)),
    ("prazo_pagamento", sa.String(length=50)),
    ("forma_pagamento", sa.String(length=50)),
    ("tabela_frete", sa.String(length=100)),
    ("banco_nome", sa.String(length=100)),
    ("banco_codigo", sa.String(length=10)),
    ("banco_agencia", sa.String(length=20)),
    ("banco_conta", sa.String(length=20)),
    ("pix_chave", sa.String(length=100)),
    ("coleta_origem", sa.String(length=3)),
    ("entrega_final", sa.String(length=3)),
    ("entregador_final", sa.String(length=50)),
    ("coleta_veiculos", sa.String(length=100)),
    ("entrega_veiculos", sa.String(length=100)),
    ("rotas_data", sa.Text()),
)


def upgrade():
    with op.batch_alter_table("transportadoras", schema=None) as batch_op:
        for column_name, column_type in TRANSPORTADORAS_COLUMNS:
            batch_op.add_column(sa.Column(column_name, column_type, nullable=True))


def downgrade():
    with op.batch_alter_table("transportadoras", schema=None) as batch_op:
        for column_name, _column_type in reversed(TRANSPORTADORAS_COLUMNS):
            batch_op.drop_column(column_name)
