# =============================================================================
# Caminho  : app/models/gestao/plano_contas.py
# Arquivo  : plano_contas.py
# Função   : Model para Plano de Contas (Estrutura Contábil/Financeira)
# =============================================================================

from app import db
from datetime import datetime

class PlanoContas(db.Model):
    __tablename__ = 'financeiro_plano_contas'
    
    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), index=True)
    
    __table_args__ = (
        db.UniqueConstraint('empresa_id', 'codigo', name='uix_empresa_codigo_pc'),
    )
    
    codigo = db.Column(db.String(30), nullable=False) # Ex: 1.01.001
    descricao = db.Column(db.String(150), nullable=False)
    
    # Tipo: RECEITA, DESPESA, ATIVO, PASSIVO
    tipo = db.Column(db.String(20), default='DESPESA')
    
    # Grupo: A (Ativo), P (Passivo), R (Receita), D (Despesa)
    grupo_gerencial = db.Column(db.String(1), index=True)
    
    # Natureza: ANALITICA (recebe lançamentos), SINTETICA (totalizadora)
    natureza = db.Column(db.String(20), default='ANALITICA')
    
    # Parâmetros de Depreciação (para contas do Imobilizado)
    vida_util_meses = db.Column(db.Integer, default=0)
    valor_residual_percent = db.Column(db.Float, default=0.0)
    
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'codigo': self.codigo,
            'descricao': self.descricao,
            'tipo': self.tipo,
            'grupo_gerencial': self.grupo_gerencial,
            'natureza': self.natureza,
            'vida_util_meses': self.vida_util_meses,
            'valor_residual_percent': self.valor_residual_percent,
            'ativo': self.ativo
        }

    def __repr__(self):
        return f'<PlanoContas {self.codigo} - {self.descricao}>'
