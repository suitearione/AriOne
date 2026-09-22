"""Adicionar tabela de referencia CBO e vinculo opcional aos cargos."""

from alembic import op
import sqlalchemy as sa


revision = 'f1cbo_ocupacoes'
down_revision = 'e63390d0d654'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'cbo_ocupacoes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('codigo', sa.String(length=10), nullable=False),
        sa.Column('titulo', sa.String(length=255), nullable=False),
        sa.Column('sinonimos', sa.Text(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('codigo'),
    )
    op.create_index('ix_cbo_ocupacoes_codigo', 'cbo_ocupacoes', ['codigo'])
    op.create_index('ix_cbo_ocupacoes_titulo', 'cbo_ocupacoes', ['titulo'])

    with op.batch_alter_table('cargos') as batch_op:
        batch_op.add_column(sa.Column('cbo_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_cargos_cbo_id_cbo_ocupacoes', 'cbo_ocupacoes', ['cbo_id'], ['id']
        )


def downgrade():
    with op.batch_alter_table('cargos') as batch_op:
        batch_op.drop_constraint('fk_cargos_cbo_id_cbo_ocupacoes', type_='foreignkey')
        batch_op.drop_column('cbo_id')
    op.drop_index('ix_cbo_ocupacoes_titulo', table_name='cbo_ocupacoes')
    op.drop_index('ix_cbo_ocupacoes_codigo', table_name='cbo_ocupacoes')
    op.drop_table('cbo_ocupacoes')