# =============================================================================
# Caminho  : app/models/gestao/centro_custo.py
# Arquivo  : centro_custo.py
# Função   : Model para Centros de Custo (Estrutura Financeira/Gerencial)
# =============================================================================

from app import db
from datetime import datetime

class CentroCusto(db.Model):
    __tablename__ = 'centros_custo'
    
    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), index=True)
    pai_id = db.Column(db.Integer, db.ForeignKey('centros_custo.id'), nullable=True) # Hierarquia
    
    codigo = db.Column(db.String(20), unique=True, nullable=False) # Ex: 01.001
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20), default='Operacional') # Operacional, Administrativo, Comercial
    
    orcamento_mensal = db.Column(db.Numeric(15, 2), default=0.0)
    ativo = db.Column(db.Boolean, default=True)
    contabil_cod = db.Column(db.String(50)) # Código no plano de contas se houver
    pix = db.Column(db.String(100)) # Chave Pix do responsável ou rateio
    
    # Metadados
    criado_em = db.Column(db.DateTime, default=datetime.now)
    atualizado_em = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relacionamentos
    subcentros = db.relationship('CentroCusto', backref=db.backref('pai', remote_side=[id]), lazy=True)
    empresa = db.relationship('Empresa', backref='centros_custo_lista')

    def to_dict(self):
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nome': self.nome,
            'tipo': self.tipo,
            'pai_id': self.pai_id,
            'orcamento_mensal': float(self.orcamento_mensal or 0),
            'contabil_cod': self.contabil_cod,
            'pix': self.pix,
            'ativo': self.ativo
        }

    def __repr__(self):
        return f'<CentroCusto {self.codigo} - {self.nome}>'
