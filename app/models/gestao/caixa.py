# =============================================================================
# Caminho  : app/models/gestao/caixa.py
# Arquivo  : caixa.py
# Função   : Entidades de Gestão de Caixas (PDV/Tesouraria) e Movimentações
# =============================================================================

import json
from app import db
from datetime import datetime

class Caixa(db.Model):
    __tablename__ = 'financeiro_caixas'

    id = db.Column(db.Integer, primary_key=True)
    formas_pagamento_ids = db.Column(db.Text, nullable=True)
    _formas_pagamento_detalhes = db.Column('formas_pagamento_detalhes', db.Text, nullable=True)
    bancos_ids = db.Column(db.Text, nullable=True)
    operadoras_ids = db.Column(db.Text, nullable=True)
    empresa_id = db.Column(db.Integer, nullable=True, index=True)
    nome = db.Column(db.String(100), nullable=False)
    responsavel = db.Column(db.String(100))
    saldo_inicial = db.Column(db.Numeric(16, 2), default=0.00)
    saldo_atual = db.Column(db.Numeric(16, 2), default=0.00)
    status = db.Column(db.String(20), default='ABERTO') # ABERTO / FECHADO
    data_abertura = db.Column(db.DateTime, default=datetime.utcnow)
    data_fechamento = db.Column(db.DateTime, nullable=True)
    observacoes = db.Column(db.Text)

    @property
    def formas_pagamento_aceitas(self):
        try:
            return json.loads(self.formas_pagamento_ids or '[]') if self.formas_pagamento_ids else []
        except Exception:
            return []

    @formas_pagamento_aceitas.setter
    def formas_pagamento_aceitas(self, value):
        if value is None:
            self.formas_pagamento_ids = None
        else:
            try:
                self.formas_pagamento_ids = json.dumps([int(v) for v in value if v is not None])
            except Exception:
                self.formas_pagamento_ids = json.dumps(value)

    @property
    def formas_pagamento_detalhes(self):
        try:
            data = json.loads(self._formas_pagamento_detalhes or '{}') if self._formas_pagamento_detalhes else {}
            if isinstance(data, dict):
                return {int(k) if isinstance(k, str) and k.isdigit() else k: v for k, v in data.items()}
            return {}
        except Exception:
            return {}

    @formas_pagamento_detalhes.setter
    def formas_pagamento_detalhes(self, value):
        if value is None or value == '':
            self._formas_pagamento_detalhes = None
        else:
            try:
                self._formas_pagamento_detalhes = json.dumps(json.loads(value))
            except Exception:
                try:
                    self._formas_pagamento_detalhes = json.dumps(value)
                except Exception:
                    self._formas_pagamento_detalhes = None

    @property
    def bancos_aceitos(self):
        try:
            return json.loads(self.bancos_ids or '[]') if self.bancos_ids else []
        except Exception:
            return []

    @bancos_aceitos.setter
    def bancos_aceitos(self, value):
        if value is None:
            self.bancos_ids = None
        else:
            try:
                self.bancos_ids = json.dumps([int(v) for v in value if v is not None])
            except Exception:
                self.bancos_ids = json.dumps(value)

    @property
    def operadoras_aceitas(self):
        try:
            return json.loads(self.operadoras_ids or '[]') if self.operadoras_ids else []
        except Exception:
            return []

    @operadoras_aceitas.setter
    def operadoras_aceitas(self, value):
        if value is None:
            self.operadoras_ids = None
        else:
            try:
                self.operadoras_ids = json.dumps([int(v) for v in value if v is not None])
            except Exception:
                self.operadoras_ids = json.dumps(value)

    # Relacionamento com as movimentações
    movimentacoes = db.relationship('MovimentacaoCaixa', backref='caixa', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Caixa {self.nome} - Saldo: {self.saldo_atual}>'


class MovimentacaoCaixa(db.Model):
    __tablename__ = 'financeiro_movimentacoes_caixa'

    id = db.Column(db.Integer, primary_key=True)
    caixa_id = db.Column(db.Integer, db.ForeignKey('financeiro_caixas.id'), nullable=False, index=True)
    tipo = db.Column(db.String(20), nullable=False) # ENTRADA / SAIDA
    categoria = db.Column(db.String(50), nullable=False) # SUPRIMENTO, SANGRIA, PAGAMENTO, RECEBIMENTO
    descricao = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Numeric(16, 2), nullable=False)
    data_movimentacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Chaves Estrangeiras Opcionais para Integração Contábil e Gerencial
    plano_contas_id = db.Column(db.Integer, db.ForeignKey('financeiro_plano_contas.id'), nullable=True)
    centro_custo_id = db.Column(db.Integer, db.ForeignKey('centros_custo.id'), nullable=True)
    forma_pagamento_id = db.Column(db.Integer, db.ForeignKey('comercial_formas_pagamento.id'), nullable=True)
    lancamento_id = db.Column(db.Integer, db.ForeignKey('financeiro_lancamentos.id'), nullable=True)
    observacoes = db.Column(db.Text)

    # Relacionamentos
    plano_contas = db.relationship('PlanoContas', backref='movimentacoes_caixa', lazy=True)
    centro_custo = db.relationship('CentroCusto', backref='movimentacoes_caixa', lazy=True)
    forma_pagamento = db.relationship('FormaPagamento', backref='movimentacoes_caixa', lazy=True)
    lancamento = db.relationship('Lancamento', backref='movimentacoes_caixa', lazy=True)

    def __repr__(self):
        return f'<MovimentacaoCaixa {self.categoria} - {self.valor}>'
