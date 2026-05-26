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
    data_emissao = db.Column(db.DateTime, default=datetime.now)
    data_limite_compra = db.Column(db.Date) # Crucial para Backward Scheduling
    
    status = db.Column(db.String(20), default='Cotacao') # Cotacao, Aprovado, Rejeitado
    total_orcamento = db.Column(db.Numeric(12, 2), default=0.00)
    
    # Itens Relacionais (Seção 10)
    itens = db.relationship('OrcamentoCompraItem', backref='orcamento', cascade='all, delete-orphan')
    pedidos = db.relationship('PedidoCompra', backref='orcamento', lazy=True)

class OrcamentoCompraItem(db.Model):
    __tablename__ = 'op_compras_orcamentos_itens'
    id = db.Column(db.Integer, primary_key=True)
    orcamento_id = db.Column(db.Integer, db.ForeignKey('op_compras_orcamentos.id'), nullable=False)
    insumo_id = db.Column(db.Integer, db.ForeignKey('cat_insumos.id'), nullable=False)
    
    quantidade = db.Column(db.Numeric(12, 3), nullable=False)
    valor_cotado = db.Column(db.Numeric(12, 2))
    total_item = db.Column(db.Numeric(12, 2))

class PedidoCompra(db.Model):
    __tablename__ = 'op_compras_pedidos'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    orcamento_compra_id = db.Column(db.Integer, db.ForeignKey('op_compras_orcamentos.id'))
    
    data_pedido = db.Column(db.DateTime, default=datetime.now)
    data_entrega = db.Column(db.Date, nullable=False)
    
    rastreamento_api = db.Column(db.String(100)) # Logística de Entrada
    
    # 🛡️ Status de Fluxo
    status = db.Column(db.String(20), default='Enviado') # Enviado, Transito, Recebido, Cancelado
    
    itens = db.relationship('PedidoCompraItem', backref='pedido', cascade='all, delete-orphan')

class PedidoCompraItem(db.Model):
    __tablename__ = 'op_compras_pedidos_itens'
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('op_compras_pedidos.id'), nullable=False)
    insumo_id = db.Column(db.Integer, db.ForeignKey('cat_insumos.id'), nullable=False)
    
    quantidade = db.Column(db.Numeric(12, 3), nullable=False)
    valor_unitario = db.Column(db.Numeric(12, 2))
    total_item = db.Column(db.Numeric(12, 2))
