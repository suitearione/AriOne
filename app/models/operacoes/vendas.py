# =============================================================================
# Caminho  : app/models/operacoes/vendas.py
# Arquivo  : vendas.py
# Função   : Modelos de Orçamentos e Pedidos de Venda.
# Padrão   : Testes_de_Integridades.md (Seção 3, 6, 10)
# =============================================================================

from app.extensions import db
from datetime import datetime

class OrcamentoVenda(db.Model):
    __tablename__ = 'op_vendas_orcamentos'
    
    # 🛡️ Regra 6: IDs são Imutáveis (Autoincrement)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    vendedor_id = db.Column(db.Integer, db.ForeignKey('funcionarios.id'))
    tipo_venda = db.Column(db.String(20), default='Produtos') # Produtos, Serviços
    canal_venda = db.Column(db.String(100)) # Canal Digital de Origem (ex: WhatsApp, Webchat)
    numero     = db.Column(db.String(20)) # Número operacional (ex: 5349)
    data_emissao = db.Column(db.DateTime, default=datetime.now)
    prazo_validade = db.Column(db.Date)
    data_entrega = db.Column(db.Date)
    hora_entrega = db.Column(db.String(5))
    
    tabela_preco = db.Column(db.String(50))
    condicao_pagamento = db.Column(db.String(100))
    
    # Resumo Financeiro
    valor_desconto = db.Column(db.Numeric(12, 2), default=0.00)
    outros_custos = db.Column(db.Numeric(12, 2), default=0.00)
    total_frete = db.Column(db.Numeric(12, 2), default=0.00)
    total_bruto = db.Column(db.Numeric(12, 2), default=0.00)
    total_liquido = db.Column(db.Numeric(12, 2), default=0.00)

    # Logística (Entrega Customizada)
    forma_envio     = db.Column(db.String(50))
    ent_cep         = db.Column(db.String(10))
    ent_logradouro  = db.Column(db.String(150))
    ent_numero      = db.Column(db.String(20))
    ent_bairro      = db.Column(db.String(100))
    ent_cidade      = db.Column(db.String(100))
    ent_uf          = db.Column(db.String(2))
    ent_complemento = db.Column(db.String(150))

    observacoes = db.Column(db.Text)
    
    # 🏗️ Nível 2: Relacional
    itens_json = db.Column(db.JSON) 
    
    status = db.Column(db.String(20), default='Aberto') # Aberto, Aprovado, Cancelado, Perdido
    
    # Relacionamentos
    pedido = db.relationship('PedidoVenda', backref='orcamento', uselist=False)
    itens = db.relationship('OrcamentoVendaItem', backref='orcamento', cascade='all, delete-orphan')
    cliente = db.relationship('Cliente', backref='orcamentos_venda')
    vendedor = db.relationship('Funcionario', foreign_keys=[vendedor_id])

class OrcamentoVendaItem(db.Model):
    __tablename__ = 'op_vendas_orcamentos_itens'
    id = db.Column(db.Integer, primary_key=True)
    orcamento_id = db.Column(db.Integer, db.ForeignKey('op_vendas_orcamentos.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('cat_produtos.id'), nullable=False)
    variacao_id = db.Column(db.Integer, db.ForeignKey('cat_produtos_variacoes.id')) # SKU Específico
    
    quantidade = db.Column(db.Numeric(12, 3), nullable=False)
    valor_unitario = db.Column(db.Numeric(12, 2), nullable=False)
    total_item = db.Column(db.Numeric(12, 2), nullable=False)

    # Relacionamentos
    produto = db.relationship('Produto', foreign_keys=[produto_id])
    variacao = db.relationship('ProdutoVariacao', foreign_keys=[variacao_id])

class PedidoVenda(db.Model):
    __tablename__ = 'op_vendas_pedidos'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    orcamento_id = db.Column(db.Integer, db.ForeignKey('op_vendas_orcamentos.id'), unique=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    vendedor_id = db.Column(db.Integer, db.ForeignKey('funcionarios.id'))
    tipo_venda = db.Column(db.String(20), default='Produtos') # Produtos, Serviços
    canal_venda = db.Column(db.String(100)) # Canal Digital de Origem (ex: WhatsApp, Webchat)
    numero     = db.Column(db.String(20)) # Número operacional (ex: 5349)
    
    data_pedido = db.Column(db.DateTime, default=datetime.now)
    data_entrega_prometida = db.Column(db.Date, nullable=False)
    
    frete = db.Column(db.Numeric(12, 2), default=0.00)
    transportadora_api_id = db.Column(db.String(100)) # Integração Logística

    # Logística (Entrega Customizada)
    forma_envio     = db.Column(db.String(50))
    ent_cep         = db.Column(db.String(10))
    ent_logradouro  = db.Column(db.String(150))
    ent_numero      = db.Column(db.String(20))
    ent_bairro      = db.Column(db.String(100))
    ent_cidade      = db.Column(db.String(100))
    ent_uf          = db.Column(db.String(2))
    ent_complemento = db.Column(db.String(150))

    # Resumo Financeiro (Sincronizado com Orçamento)
    valor_desconto = db.Column(db.Numeric(12, 2), default=0.00)
    outros_custos = db.Column(db.Numeric(12, 2), default=0.00)
    total_frete = db.Column(db.Numeric(12, 2), default=0.00)
    total_bruto = db.Column(db.Numeric(12, 2), default=0.00)
    total_liquido = db.Column(db.Numeric(12, 2), default=0.00)
    
    # 🛡️ Status de Fluxo (Seção 3)
    status = db.Column(db.String(20), default='Em EDIÇÃO') # Aberto, Em EDIÇÃO, Producao, Faturado, Entregue, Cancelado
    
    # Relacionamentos para Backward Scheduling
    ordens_producao = db.relationship('OrdemProducao', backref='pedido_venda', lazy=True)
    orcamentos_compra = db.relationship('OrcamentoCompra', backref='pedido_venda', lazy=True)
    itens = db.relationship('PedidoVendaItem', backref='pedido', cascade='all, delete-orphan')
    cliente = db.relationship('Cliente', backref='pedidos_venda')
    vendedor = db.relationship('Funcionario', foreign_keys=[vendedor_id])

class PedidoVendaItem(db.Model):
    __tablename__ = 'op_vendas_pedidos_itens'
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('op_vendas_pedidos.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('cat_produtos.id'), nullable=False)
    variacao_id = db.Column(db.Integer, db.ForeignKey('cat_produtos_variacoes.id'))
    
    quantidade = db.Column(db.Numeric(12, 3), nullable=False)
    valor_unitario = db.Column(db.Numeric(12, 2), nullable=False)
    total_item = db.Column(db.Numeric(12, 2), nullable=False)

    # Relacionamentos
    produto = db.relationship('Produto', foreign_keys=[produto_id])
    variacao = db.relationship('ProdutoVariacao', foreign_keys=[variacao_id])

class MetaVenda(db.Model):
    """🏆 Modelo de Gestão de Metas de Vendas (Mensal/Anual por Vendedor ou Empresa)"""
    __tablename__ = 'op_vendas_metas'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    vendedor_id = db.Column(db.Integer, db.ForeignKey('funcionarios.id'), nullable=True) # Se nulo, meta geral da empresa
    
    ano = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False) # 1 a 12
    
    valor_meta = db.Column(db.Numeric(15, 2), default=0.00)
    observacoes = db.Column(db.Text)
    
    # Relacionamento
    vendedor = db.relationship('Funcionario', foreign_keys=[vendedor_id])
