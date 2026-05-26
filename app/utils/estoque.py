from app import db
from datetime import datetime

class LocalEstoque(db.Model):
    __tablename__ = 'LOCAL_ESTOQUE'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False) # Ex: ALMOXARIFADO, OFICINA SÃO JOSÉ
    tipo = db.Column(db.String(20)) # INTERNO / EXTERNO

class Produto(db.Model):
    __tablename__ = 'PRODUTO'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(10)) # MP (Materia Prima) / PA (Produto Acabado)
    origem = db.Column(db.String(1), default='C') # 'C': Compra/Revenda, 'P': Produção
    saldo_fisico = db.Column(db.Numeric(12, 4), default=0.0)
    preco_venda = db.Column(db.Numeric(12, 2), default=0.0)
    custo_medio = db.Column(db.Numeric(12, 2), default=0.0)

class MovimentacaoEstoque(db.Model):
    __tablename__ = 'ESTOQUE_MOV'
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('PRODUTO.id'))
    local_id = db.Column(db.Integer, db.ForeignKey('LOCAL_ESTOQUE.id'))
    quantidade = db.Column(db.Numeric(12, 4), nullable=False)
    tipo_operacao = db.Column(db.String(30)) # ENTRADA_PRODUCAO / CONSUMO_OFICINA
    documento_origem = db.Column(db.String(50)) # ID da Ordem de Produção
    data_evento = db.Column(db.DateTime, default=datetime.utcnow)

class OrdemProducao(db.Model):
    __tablename__ = 'ORDEM_PRODUCAO'
    id = db.Column(db.Integer, primary_key=True)
    produto_pa_id = db.Column(db.Integer, db.ForeignKey('PRODUTO.id'))
    quantidade_planejada = db.Column(db.Numeric(12, 4))
    quantidade_real_produzida = db.Column(db.Numeric(12, 4)) # Novo campo para a quantidade efetivamente produzida
    status = db.Column(db.String(20), default='ABERTA') # ABERTA, EM_OFICINA, CONCLUIDA
    
    # Relacionamento com itens de consumo (Matéria-prima)
    materiais = db.relationship('ItemOrdemProducao', backref='op')

class ItemOrdemProducao(db.Model):
    __tablename__ = 'OP_ITENS_CONSUMO'
    id = db.Column(db.Integer, primary_key=True)
    op_id = db.Column(db.Integer, db.ForeignKey('ORDEM_PRODUCAO.id'))
    produto_mp_id = db.Column(db.Integer, db.ForeignKey('PRODUTO.id'))
    quantidade_estimada = db.Column(db.Numeric(12, 4))
    quantidade_real_consumida = db.Column(db.Numeric(12, 4))

class FichaTecnica(db.Model):
    __tablename__ = 'FICHA_TECNICA'
    id = db.Column(db.Integer, primary_key=True)
    produto_pa_id = db.Column(db.Integer, db.ForeignKey('PRODUTO.id'), nullable=False)
    produto_mp_id = db.Column(db.Integer, db.ForeignKey('PRODUTO.id'), nullable=False)
    quantidade_necessaria = db.Column(db.Numeric(12, 4), nullable=False) # Qtd de MP para fazer 1 unidade de PA

class PedidoVenda(db.Model):
    __tablename__ = 'PEDIDO_VENDA'
    id = db.Column(db.Integer, primary_key=True)
    cliente_nome = db.Column(db.String(100))
    data_pedido = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='ORCAMENTO') 
    vendedor_id = db.Column(db.Integer)
    tipo_venda = db.Column(db.String(50), default="Produtos")
    valor_desconto = db.Column(db.Numeric(12, 2), default=0.0)
    outros_custos = db.Column(db.Numeric(12, 2), default=0.0)
    total_frete = db.Column(db.Numeric(12, 2), default=0.0)
    total_bruto = db.Column(db.Numeric(12, 2), default=0.0)
    total_liquido = db.Column(db.Numeric(12, 2), default=0.0)
    
    # Campos de Logística de Entrega
    ent_cep = db.Column(db.String(10))
    ent_logradouro = db.Column(db.String(100))
    ent_numero = db.Column(db.String(10))
    ent_bairro = db.Column(db.String(50))
    ent_cidade = db.Column(db.String(50))
    ent_uf = db.Column(db.String(2))
    forma_envio = db.Column(db.String(50))

    valor_total = db.Column(db.Numeric(12, 2), default=0.0)
    itens = db.relationship('ItemPedidoVenda', backref='pedido')
    financeiro = db.relationship('FinanceiroLancamento', backref='pedido_origem')

class ItemPedidoVenda(db.Model):
    __tablename__ = 'PEDIDO_VENDA_ITEM'
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('PEDIDO_VENDA.id'))
    produto_id = db.Column(db.Integer, db.ForeignKey('PRODUTO.id'))
    # Detalhamento para personalização
    observacao_item = db.Column(db.Text)
    requer_imagem = db.Column(db.Boolean, default=False)
    quantidade = db.Column(db.Numeric(12, 4))
    preco_unitario = db.Column(db.Numeric(12, 2))
    anexos = db.relationship('AnexoItemPedido', backref='item')

class AnexoItemPedido(db.Model):
    __tablename__ = 'PEDIDO_ITEM_ANEXO'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('PEDIDO_VENDA_ITEM.id'))
    tipo_posicao = db.Column(db.String(20)) # FRENTE, COSTAS, MANGA_ESQ, MANGA_DIR
    url_arquivo = db.Column(db.String(255)) # Caminho para o PDF, PNG, etc
    extensao = db.Column(db.String(10)) # PDF, PNG, CDR

class OrdemCompra(db.Model):
    __tablename__ = 'ORDEM_COMPRA'
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('PRODUTO.id'))
    quantidade = db.Column(db.Numeric(12, 4))
    status = db.Column(db.String(20), default='ABERTA')
    pedido_origem_id = db.Column(db.Integer, db.ForeignKey('PEDIDO_VENDA.id'))

class FinanceiroLancamento(db.Model):
    __tablename__ = 'FINANCEIRO_LANCAMENTO'
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('PEDIDO_VENDA.id'))
    tipo = db.Column(db.String(1), default='R') # R: Receber, P: Pagar
    valor = db.Column(db.Numeric(12, 2))
    data_vencimento = db.Column(db.Date)
    status = db.Column(db.String(20), default='PENDENTE') # PENDENTE, PAGO

class PosVenda(db.Model):
    __tablename__ = 'POS_VENDA'
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('PEDIDO_VENDA.id'))
    feedback_cliente = db.Column(db.Text)
    data_contato = db.Column(db.DateTime, default=datetime.utcnow)

class ParametroSistema(db.Model):
    __tablename__ = 'PARAMETRO_SISTEMA'
    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(50), unique=True)
    valor = db.Column(db.String(100))
    permitir_cdr_em_orcamento = db.Column(db.Boolean, default=True)