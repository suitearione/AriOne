# =============================================================================
# Caminho  : app/models/operacoes/compras.py
# Arquivo  : compras.py
# Função   : Modelos de Orçamentos e Pedidos de Compra.
# Padrão   : Testes_de_Integridades.md (Seção 3, 6, 10)
# =============================================================================

from app.extensions import db
from datetime import datetime

class OrcamentoCompra(db.Model):
    __tablename__ = 'op_compras_orcamentos'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    pedido_venda_id = db.Column(db.Integer, db.ForeignKey('op_vendas_pedidos.id')) # Rastreabilidade
    
    fornecedor_id = db.Column(db.Integer, db.ForeignKey('fornecedores.id'), nullable=False)
    comprador_id = db.Column(db.Integer, db.ForeignKey('funcionarios.id'))
    perfil_compra = db.Column(db.String(50), default='padrao')
    numero = db.Column(db.String(20))
    data_emissao = db.Column(db.DateTime, default=datetime.now)
    data_limite_compra = db.Column(db.Date) # Crucial para Backward Scheduling
    
    condicao_pagamento = db.Column(db.String(100))
    forma_pagamento_id = db.Column(db.Integer) # Integrar futuramente com Contas a Pagar
    
    # Resumo Financeiro
    valor_desconto = db.Column(db.Numeric(12, 2), default=0.00)
    outros_custos = db.Column(db.Numeric(12, 2), default=0.00)
    total_frete = db.Column(db.Numeric(12, 2), default=0.00)
    total_bruto = db.Column(db.Numeric(12, 2), default=0.00)
    total_liquido = db.Column(db.Numeric(12, 2), default=0.00)
    total_orcamento = db.Column(db.Numeric(12, 2), default=0.00) # Backward compatibility
    
    # Logística
    forma_envio = db.Column(db.String(50))
    ent_cep = db.Column(db.String(10))
    ent_logradouro = db.Column(db.String(150))
    ent_numero = db.Column(db.String(20))
    ent_bairro = db.Column(db.String(100))
    ent_cidade = db.Column(db.String(100))
    ent_uf = db.Column(db.String(2))
    ent_complemento = db.Column(db.String(150))
    
    observacoes = db.Column(db.Text)
    
    status = db.Column(db.String(20), default='Cotacao') # Cotacao, Aprovado, Rejeitado
    
    # Itens Relacionais (Seção 10)
    itens = db.relationship('OrcamentoCompraItem', backref='orcamento', cascade='all, delete-orphan')
    pedidos = db.relationship('PedidoCompra', backref='orcamento', lazy=True)
    comprador = db.relationship('Funcionario', foreign_keys=[comprador_id])

class OrcamentoCompraItem(db.Model):
    __tablename__ = 'op_compras_orcamentos_itens'
    id = db.Column(db.Integer, primary_key=True)
    orcamento_id = db.Column(db.Integer, db.ForeignKey('op_compras_orcamentos.id'), nullable=False)
    insumo_id = db.Column(db.Integer, db.ForeignKey('cat_insumos.id'), nullable=False)
    
    quantidade = db.Column(db.Numeric(12, 3), nullable=False)
    valor_cotado = db.Column(db.Numeric(12, 2))
    total_item = db.Column(db.Numeric(12, 2))
    
    insumo = db.relationship('Insumo', foreign_keys=[insumo_id])

class PedidoCompra(db.Model):
    __tablename__ = 'op_compras_pedidos'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    orcamento_compra_id = db.Column(db.Integer, db.ForeignKey('op_compras_orcamentos.id'))
    
    fornecedor_id = db.Column(db.Integer, db.ForeignKey('fornecedores.id'))
    comprador_id = db.Column(db.Integer, db.ForeignKey('funcionarios.id'))
    perfil_compra = db.Column(db.String(50), default='padrao')
    numero = db.Column(db.String(20))
    
    data_pedido = db.Column(db.DateTime, default=datetime.now)
    data_entrega = db.Column(db.Date, nullable=False)
    
    condicao_pagamento = db.Column('condicoes_pagamento', db.String(100))
    forma_pagamento_id = db.Column(db.Integer)
    
    # Resumo Financeiro
    valor_desconto = db.Column(db.Numeric(12, 2), default=0.00)
    outros_custos = db.Column(db.Numeric(12, 2), default=0.00)
    total_frete = db.Column(db.Numeric(12, 2), default=0.00)
    total_bruto = db.Column(db.Numeric(12, 2), default=0.00)
    total_liquido = db.Column(db.Numeric(12, 2), default=0.00)
    
    # Logística
    forma_envio = db.Column(db.String(50))
    ent_cep = db.Column(db.String(10))
    ent_logradouro = db.Column(db.String(150))
    ent_numero = db.Column(db.String(20))
    ent_bairro = db.Column(db.String(100))
    ent_cidade = db.Column(db.String(100))
    ent_uf = db.Column(db.String(2))
    ent_complemento = db.Column(db.String(150))
    
    rastreamento_api = db.Column(db.String(100)) # Logística de Entrada
    observacoes = db.Column(db.Text)
    
    # 🛡️ Status de Fluxo
    status = db.Column(db.String(20), default='Enviado') # Enviado, Transito, Recebido, Cancelado
    
    itens = db.relationship('PedidoCompraItem', backref='pedido', cascade='all, delete-orphan')
    comprador = db.relationship('Funcionario', foreign_keys=[comprador_id])

class PedidoCompraItem(db.Model):
    __tablename__ = 'op_compras_pedidos_itens'
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('op_compras_pedidos.id'), nullable=False)
    insumo_id = db.Column(db.Integer, db.ForeignKey('cat_insumos.id'), nullable=False)
    
    quantidade = db.Column(db.Numeric(12, 3), nullable=False)
    valor_unitario = db.Column(db.Numeric(12, 2))
    total_item = db.Column(db.Numeric(12, 2))

    insumo = db.relationship('Insumo', foreign_keys=[insumo_id])

