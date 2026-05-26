# =============================================================================
# Caminho  : app/models/gestao/lancamento.py
# Arquivo  : lancamento.py
# Função   : Model para Lançamentos Financeiros (Contas a Pagar/Receber) e Rateio
# =============================================================================

from app import db
from datetime import datetime

class Lancamento(db.Model):
    __tablename__ = 'financeiro_lancamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    
    # Documentação e Origem
    numero_documento = db.Column(db.String(50), nullable=True) # NF, Boleto, Fatura
    data_lancamento = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Classificação (Rateio Único Padrão)
    plano_contas_id = db.Column(db.Integer, db.ForeignKey('financeiro_plano_contas.id'), index=True)
    centro_custo_id = db.Column(db.Integer, db.ForeignKey('centros_custo.id'), nullable=True)
    rateio_multiplo = db.Column(db.Boolean, default=False)
    
    # Se for depreciação, vincula ao bem
    patrimonio_id = db.Column(db.Integer, db.ForeignKey('financeiro_patrimonio.id'), nullable=True)
    
    descricao = db.Column(db.String(255), nullable=False)
    valor = db.Column(db.Float, nullable=False, default=0.0)
    
    # Datas
    data_vencimento = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    data_pagamento = db.Column(db.DateTime, nullable=True)
    data_competencia = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Tipo: RECEITA, DESPESA
    tipo = db.Column(db.String(10), default='DESPESA')
    
    # Status: PENDENTE, PAGO, CANCELADO
    status = db.Column(db.String(20), default='PENDENTE')
    
    # Forma de Pagamento (Opcional no lançamento inicial)
    forma_pagamento_id = db.Column(db.Integer, db.ForeignKey('comercial_formas_pagamento.id'), nullable=True)
    
    # Destino/Origem Financeira na Baixa (Liquidação)
    conta_bancaria_id = db.Column(db.Integer, nullable=True) # Referência livre temporária (até consolidar modelo de ContaBancariaEmpresa)
    caixa_id = db.Column(db.Integer, db.ForeignKey('financeiro_caixas.id'), nullable=True)
    
    observacoes = db.Column(db.Text)
    
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    plano_contas = db.relationship('PlanoContas', backref='lancamentos')
    centro_custo = db.relationship('CentroCusto', backref='lancamentos')
    patrimonio = db.relationship('Patrimonio', backref='historico_depreciacao')
    forma_pagamento = db.relationship('FormaPagamento', backref='lancamentos_financeiros', lazy=True)
    rateios = db.relationship('RateioLancamento', backref='lancamento', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'numero_documento': self.numero_documento,
            'descricao': self.descricao,
            'valor': self.valor,
            'vencimento': self.data_vencimento.strftime('%Y-%m-%d'),
            'pagamento': self.data_pagamento.strftime('%Y-%m-%d') if self.data_pagamento else None,
            'lancamento': self.data_lancamento.strftime('%Y-%m-%d') if self.data_lancamento else None,
            'tipo': self.tipo,
            'status': self.status,
            'rateio_multiplo': self.rateio_multiplo,
            'plano_contas': self.plano_contas.descricao if self.plano_contas else None,
            'rateios': [{
                'id_temp': r.id,
                'plano_contas_id': r.plano_contas_id,
                'plano_contas_nome': f"{r.plano_contas.codigo} - {r.plano_contas.descricao}" if r.plano_contas else '',
                'centro_custo_id': r.centro_custo_id,
                'centro_custo_nome': f"{r.centro_custo.codigo} - {r.centro_custo.nome}" if r.centro_custo else 'SEM CENTRO DE CUSTO',
                'valor': r.valor
            } for r in self.rateios] if self.rateios else []
        }


class RateioLancamento(db.Model):
    __tablename__ = 'financeiro_lancamentos_rateio'
    
    id = db.Column(db.Integer, primary_key=True)
    lancamento_id = db.Column(db.Integer, db.ForeignKey('financeiro_lancamentos.id', ondelete='CASCADE'), nullable=False, index=True)
    plano_contas_id = db.Column(db.Integer, db.ForeignKey('financeiro_plano_contas.id'), nullable=False)
    centro_custo_id = db.Column(db.Integer, db.ForeignKey('centros_custo.id'), nullable=True)
    valor = db.Column(db.Float, nullable=False, default=0.0)
    
    # Relacionamentos
    plano_contas = db.relationship('PlanoContas', backref='rateios_lancamento')
    centro_custo = db.relationship('CentroCusto', backref='rateios_lancamento')

    def __repr__(self):
        return f'<RateioLancamento {self.plano_contas_id} - {self.valor}>'
