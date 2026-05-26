# =============================================================================
# Caminho  : app/models/catalogos.py
# Arquivo  : catalogos.py
# Função   : Modelos de dados para o módulo de Catálogo AriOne
# =============================================================================

from app.extensions import db
from datetime import datetime

class Marca(db.Model):
    __tablename__ = 'cat_marcas'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    pais_origem = db.Column(db.String(50))
    website = db.Column(db.String(255))
    origem_comercial = db.Column(db.String(20), default='NACIONAL') # NACIONAL, IMPORTADO
    logo = db.Column(db.String(255))
    ativa = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

class Categoria(db.Model):
    __tablename__ = 'cat_categorias'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    departamento = db.Column(db.String(50))
    descricao = db.Column(db.Text)
    cor = db.Column(db.String(20), default='#27AE60')
    icone = db.Column(db.String(50), default='fa-layer-group')
    slug = db.Column(db.String(100), unique=True)
    ativa = db.Column(db.Boolean, default=True)
    subcategorias = db.relationship('Subcategoria', backref='categoria', lazy=True, cascade="all, delete-orphan")

class Subcategoria(db.Model):
    __tablename__ = 'cat_subcategorias'
    id = db.Column(db.Integer, primary_key=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('cat_categorias.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    margem_sugerida = db.Column(db.Float, default=0.0)
    ativa = db.Column(db.Boolean, default=True)

class UnidadeMedida(db.Model):
    __tablename__ = 'cat_unidades'
    id = db.Column(db.Integer, primary_key=True)
    sigla = db.Column(db.String(5), nullable=False, unique=True)
    nome_extenso = db.Column(db.String(50), nullable=False)
    decimais = db.Column(db.Integer, default=0)
    permite_fracionamento = db.Column(db.Boolean, default=True)
    padrao_estoque = db.Column(db.Boolean, default=False)

class Etiqueta(db.Model):
    __tablename__ = 'cat_etiquetas'
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(50), nullable=False)
    cor_hex = db.Column(db.String(7), default='#8E44AD')
    prioridade = db.Column(db.Integer, default=1)
    escopo = db.Column(db.String(255)) # JSON ou String separada por vírgula (PRODUTO, PEDIDO...)
    foto = db.Column(db.String(255))
    ativa = db.Column(db.Boolean, default=True)

class Insumo(db.Model):
    __tablename__ = 'cat_insumos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    unidade_id = db.Column(db.Integer, db.ForeignKey('cat_unidades.id'))
    sku = db.Column(db.String(50), unique=True)
    preco_custo = db.Column(db.Float, default=0.0)
    estoque_minimo = db.Column(db.Float, default=0.0)
    ponto_pedido = db.Column(db.Float, default=0.0)
    fornecedor_id = db.Column(db.Integer) # FK para Fornecedor
    conta_contabil = db.Column(db.String(20))
    centro_custo = db.Column(db.String(50))
    foto = db.Column(db.String(255))
    ativa = db.Column(db.Boolean, default=True)
    unidade = db.relationship('UnidadeMedida', backref='insumos', lazy=True)

class ClassificacaoAcessorio(db.Model):
    __tablename__ = 'cat_acessorios_classificacoes'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    ativa = db.Column(db.Boolean, default=True)

    @property
    def em_uso(self):
        return Acessorio.query.filter_by(classificacao_id=self.id).first() is not None

class Acessorio(db.Model):
    __tablename__ = 'cat_acessorios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    classificacao_id = db.Column(db.Integer, db.ForeignKey('cat_acessorios_classificacoes.id'))
    referencia = db.Column(db.String(50))
    unidade_id = db.Column(db.Integer, db.ForeignKey('cat_unidades.id'))
    peso_g = db.Column(db.Float, default=0.0)
    custo_unitario = db.Column(db.Float, default=0.0)
    foto = db.Column(db.String(255))
    ativa = db.Column(db.Boolean, default=True)

    # Relacionamentos
    classificacao = db.relationship('ClassificacaoAcessorio', backref='acessorios', lazy=True)
    unidade = db.relationship('UnidadeMedida', backref='acessorios', lazy=True)
    fornecedores_alternativos = db.relationship('FornecedorAcessorio', backref='acessorio', lazy=True, cascade="all, delete-orphan")

class FornecedorAcessorio(db.Model):
    __tablename__ = 'cat_acessorios_fornecedores'
    id = db.Column(db.Integer, primary_key=True)
    acessorio_id = db.Column(db.Integer, db.ForeignKey('cat_acessorios.id'), nullable=False)
    fornecedor_id = db.Column(db.Integer, db.ForeignKey('fornecedores.id'), nullable=False)
    preco_compra = db.Column(db.Float, default=0.0)
    prazo_entrega = db.Column(db.Integer, default=1) # Dias
    modalidade = db.Column(db.String(20), default='PRESENCIAL') # INTERNET, PRESENCIAL

    @property
    def fornecedor_obj(self):
        from app.models.cadastros.fornecedor import Fornecedor
        return Fornecedor.query.get(self.fornecedor_id)


class ClassificacaoEmbalagem(db.Model):
    __tablename__ = 'cat_embalagens_classificacoes'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)

    @property
    def em_uso(self):
        return Embalagem.query.filter_by(classificacao_id=self.id).first() is not None

class Embalagem(db.Model):
    __tablename__ = 'cat_embalagens'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(50), unique=True)
    tipo = db.Column(db.String(50)) # Saco, Caixa, Envelope... (Legado)
    classificacao_id = db.Column(db.Integer, db.ForeignKey('cat_embalagens_classificacoes.id'))
    unidade_id = db.Column(db.Integer, db.ForeignKey('cat_unidades.id'))
    
    classificacao = db.relationship(ClassificacaoEmbalagem, backref='embalagens', lazy=True)
    custo_compra = db.Column(db.Float, default=0.0)
    fator_conversao = db.Column(db.Float, default=1.0) # Ex: 195 saquinhos por KG
    custo_unitario = db.Column(db.Float, default=0.0) # Custo calculado (custo_compra / fator)
    estoque_atual = db.Column(db.Integer, default=0)
    altura_mm = db.Column(db.Float)
    largura_mm = db.Column(db.Float)
    profundidade_mm = db.Column(db.Float)
    peso_proprio_g = db.Column(db.Float, default=0.0)
    foto = db.Column(db.String(255))
    ativa = db.Column(db.Boolean, default=True)

    # Relacionamento com fornecedores alternativos
    fornecedores_alternativos = db.relationship('FornecedorEmbalagem', backref='embalagem', lazy=True, cascade="all, delete-orphan")

class FornecedorEmbalagem(db.Model):
    __tablename__ = 'cat_embalagens_fornecedores'
    id = db.Column(db.Integer, primary_key=True)
    embalagem_id = db.Column(db.Integer, db.ForeignKey('cat_embalagens.id'), nullable=False)
    fornecedor_id = db.Column(db.Integer, db.ForeignKey('fornecedores.id'), nullable=False)
    preco_compra = db.Column(db.Float, default=0.0)
    prazo_entrega = db.Column(db.Integer, default=1) # Dias
    modalidade = db.Column(db.String(20), default='PRESENCIAL') # INTERNET, PRESENCIAL
    link_compra = db.Column(db.String(255))
    
    @property
    def fornecedor_obj(self):
        from app.models.cadastros.fornecedor import Fornecedor
        return Fornecedor.query.get(self.fornecedor_id)

class TipoMateriaPrima(db.Model):
    __tablename__ = 'cat_materiaprima_tipos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    ativa = db.Column(db.Boolean, default=True)

    @property
    def em_uso(self):
        """Verifica se este tipo está vinculado a alguma matéria-prima ou produto."""
        tem_mp = MateriaPrima.query.filter_by(tipo_id=self.id).first() is not None
        tem_prod = Produto.query.filter_by(tipo_material_id=self.id).first() is not None
        return tem_mp or tem_prod

class MateriaPrima(db.Model):
    __tablename__ = 'cat_materiaprima'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    tipo_id = db.Column(db.Integer, db.ForeignKey('cat_materiaprima_tipos.id'))
    sku = db.Column(db.String(50), unique=True)
    unidade_id = db.Column(db.Integer, db.ForeignKey('cat_unidades.id'))
    preco_custo = db.Column(db.Float, default=0.0)
    estoque_minimo = db.Column(db.Float, default=0.0)
    composicao = db.Column(db.String(255))
    fornecedor_id = db.Column(db.Integer)
    ncm = db.Column(db.String(10))
    cst = db.Column(db.String(3))
    foto = db.Column(db.String(255))
    ativa = db.Column(db.Boolean, default=True)

    # Relacionamentos
    tipo = db.relationship('TipoMateriaPrima', backref='materias', lazy=True)
    unidade = db.relationship('UnidadeMedida', backref='materias', lazy=True)

class ModeloCatalogo(db.Model):
    __tablename__ = 'cat_modelos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    sigla = db.Column(db.String(20)) # Opcional: Sigla do modelo
    ativa = db.Column(db.Boolean, default=True)

class Produto(db.Model):
    __tablename__ = 'cat_produtos'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    tipo_item = db.Column(db.String(50))
    cod_barras = db.Column(db.String(14))
    cod_interno = db.Column(db.String(50)) # O código de controle (ex: CIP-S1)
    referencia = db.Column(db.String(50))  # A referência/SKU base
    unidade = db.Column(db.String(10))
    peso = db.Column(db.Float, default=0.0)
    categoria = db.Column(db.String(100))
    subcategoria = db.Column(db.String(100))
    categoria_id = db.Column(db.Integer, db.ForeignKey('cat_categorias.id'))
    subcategoria_id = db.Column(db.Integer, db.ForeignKey('cat_subcategorias.id'))
    marca = db.Column(db.String(100))
    modelo = db.Column(db.String(100))
    fornecedor = db.Column(db.String(100))
    fornecedor_id = db.Column(db.Integer, db.ForeignKey('fornecedores.id'))
    origem_produto = db.Column(db.String(50)) # propria, terceiros
    regra_cod_interno = db.Column(db.String(20)) # automatico, livre, fornecedor
    tipo_material_id = db.Column(db.Integer, db.ForeignKey('cat_materiaprima_tipos.id'))
    dim_comprimento = db.Column(db.Float, default=0.0)
    dim_largura = db.Column(db.Float, default=0.0)
    dim_altura = db.Column(db.Float, default=0.0)
    tags = db.Column(db.String(255))
    
    # Relacionamento para acesso fácil ao nome do tipo de material
    tipo_material = db.relationship('TipoMateriaPrima', backref='produtos', lazy=True)
    
    # Preços
    preco_custo = db.Column(db.Float, default=0.0)
    preco_varejo = db.Column(db.Float, default=0.0)
    preco_atacado = db.Column(db.Float, default=0.0)
    preco_promocional = db.Column(db.Float, default=0.0)
    
    # Estoque
    tipo_estoque = db.Column(db.String(20), default='unico') # unico, grade
    estoque_atual = db.Column(db.Float, default=0.0) # Saldo físico atual no estoque
    estoque_minimo = db.Column(db.Float, default=0.0)
    saldo_reservado = db.Column(db.Float, default=0.0) # Reservado em pedidos de venda/OPs
    saldo_previsto = db.Column(db.Float, default=0.0) # Previsto em pedidos de compra
    qtd_min_varejo = db.Column(db.Integer, default=1)
    qtd_min_atacado = db.Column(db.Integer, default=10)
    deposito = db.Column(db.String(100))
    prateleira = db.Column(db.String(100))
    mov_estoque = db.Column(db.Boolean, default=True)
    has_composicao = db.Column(db.Boolean, default=False)
    mov_estoque_composicao = db.Column(db.Boolean, default=False)
    
    # Fiscal
    ncm = db.Column(db.String(10))
    cest = db.Column(db.String(10))
    cfop = db.Column(db.String(4))
    origem = db.Column(db.String(1), default='0')
    cst = db.Column(db.String(3))
    aliq_icms = db.Column(db.Float, default=0.0)
    aliq_pis = db.Column(db.Float, default=0.0)
    aliq_cofins = db.Column(db.Float, default=0.0)
    aliq_ipi = db.Column(db.Float, default=0.0)
    mva = db.Column(db.Float, default=0.0)
    base_st = db.Column(db.Float, default=0.0)
    
    # Regras
    permite_desconto = db.Column(db.Boolean, default=True)
    desconto_maximo = db.Column(db.Float, default=0.0)
    vender_sem_estoque = db.Column(db.Boolean, default=False)
    exige_obs_venda = db.Column(db.Boolean, default=False)
    imprimir_nfe = db.Column(db.Boolean, default=True)
    gerar_etiqueta = db.Column(db.Boolean, default=True)
    
    composicao = db.Column(db.JSON) # Armazena compBuf serializado
    grade_id = db.Column(db.Integer, db.ForeignKey('cat_grades_modelos.id'))
    grade_cores = db.Column(db.JSON) # Lista de nomes de cores selecionadas
    grade_tamanhos = db.Column(db.JSON) # Lista de nomes de tamanhos selecionados
    grade_label_adicional = db.Column(db.String(50)) # Ex: Manga, Tecido...
    grade_valores_adicional = db.Column(db.JSON) # Lista de valores da 3ª variação
    grade_matrix = db.Column(db.JSON) # Dados da matriz: { "COR-TAM-ATTR": { preco: 0, estoque: 0, sku: "" } }
    
    foto = db.Column(db.String(255))
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # Relacionamentos Granulares (Padrão PLM)
    variacoes = db.relationship('ProdutoVariacao', backref='produto_pai', lazy=True, cascade="all, delete-orphan")
    composicao_itens = db.relationship('ProdutoComposicao', backref='produto_pai', lazy=True, cascade="all, delete-orphan")

    @property
    def saldo_disponivel(self):
        # A regra de ouro do AriOne: (Físico + Previsto) - Reservado
        return (self.estoque_atual + (self.saldo_previsto or 0.0)) - (self.saldo_reservado or 0.0)

class ProdutoVariacao(db.Model):
    __tablename__ = 'cat_produtos_variacoes'
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('cat_produtos.id'), nullable=False)
    
    sku = db.Column(db.String(100), unique=True)
    cor = db.Column(db.String(50))
    tamanho = db.Column(db.String(20))
    atributo = db.Column(db.String(100))
    
    estoque_atual = db.Column(db.Float, default=0.0)
    estoque_minimo = db.Column(db.Float, default=0.0)
    custo_producao = db.Column(db.Float, default=0.0) # Custo calculado preciso por SKU
    preco_venda = db.Column(db.Float, default=0.0)
    
    @property
    def nome(self):
        parts = []
        if self.cor: parts.append(self.cor)
        if self.tamanho: parts.append(self.tamanho)
        if self.atributo: parts.append(self.atributo)
        return " - ".join(parts) if parts else f"VAR#{self.id}"
    
    # Relacionamento com composição específica desta variação
    itens_composicao = db.relationship('ProdutoComposicao', backref='variacao_filha', lazy=True, cascade="all, delete-orphan")

class ProdutoComposicao(db.Model):
    __tablename__ = 'cat_produtos_composicao'
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('cat_produtos.id'), nullable=False)
    variacao_id = db.Column(db.Integer, db.ForeignKey('cat_produtos_variacoes.id'), nullable=True) # Se null, aplica-se a todos (Geral)
    
    tipo_componente = db.Column(db.String(50)) # Matéria-Prima, Acessório, Serviço, Insumo, Embalagem
    item_id = db.Column(db.Integer) # ID do registro na tabela original (cat_materiaprima, cat_acessorios, etc)
    nome = db.Column(db.String(200))
    unidade = db.Column(db.String(20))
    custo_unitario = db.Column(db.Float, default=0.0)
    quantidade = db.Column(db.Float, default=1.0)
    total_custo = db.Column(db.Float, default=0.0)

class Servico(db.Model):
    __tablename__ = 'cat_servicos'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    tipo_item = db.Column(db.String(2), default="09")
    categoria = db.Column(db.String(100))
    codigo = db.Column(db.String(50))
    observacoes = db.Column(db.String(255))
    unidade_medida = db.Column(db.String(20))
    preco_custo = db.Column(db.Float, default=0.0)
    preco_venda = db.Column(db.Float, default=0.0)
    qtd_minima = db.Column(db.Float, default=1.0)
    tempo_execucao = db.Column(db.String(100))
    comissao = db.Column(db.Float, default=0.0)
    descricao_detalhada = db.Column(db.Text)
    garantia = db.Column(db.String(100))
    validade_proposta = db.Column(db.String(100))
    forma_pagamento = db.Column(db.String(50))
    
    # Fiscal
    ncm = db.Column(db.String(10))
    cest = db.Column(db.String(10))
    codigo_servico = db.Column(db.String(20)) # LC 116
    
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

class Deposito(db.Model):
    __tablename__ = 'cat_depositos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    sigla = db.Column(db.String(20)) # Código interno do depósito
    endereco = db.Column(db.String(255))
    tipo = db.Column(db.String(50), default='proprio') # proprio, terceiros, virtual
    ativa = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    prateleiras = db.relationship('DepositoPrateleira', backref='deposito', lazy=True, cascade="all, delete-orphan")

class CorCatalogo(db.Model):
    __tablename__ = 'cat_cores'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False, unique=True)
    cor_hex = db.Column(db.String(7), default='#CBD5E0')
    ativa = db.Column(db.Boolean, default=True)

    @property
    def em_uso(self):
        from sqlalchemy import cast, String
        return Produto.query.filter(Produto.grade_cores.cast(String).contains(self.nome)).first() is not None

class TamanhoCatalogo(db.Model):
    __tablename__ = 'cat_tamanhos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(20), nullable=False, unique=True)
    ordem = db.Column(db.Integer, default=0)
    fator_consumo = db.Column(db.Float, default=1.0) # Multiplicador de matéria-prima (Ex: 1.2 para GG)
    ativa = db.Column(db.Boolean, default=1)

    @property
    def em_uso(self):
        from sqlalchemy import cast, String
        return Produto.query.filter(Produto.grade_tamanhos.cast(String).contains(self.nome)).first() is not None

class AtributoCatalogo(db.Model):
    __tablename__ = 'cat_atributos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    descricao = db.Column(db.String(255))
    ativa = db.Column(db.Boolean, default=True)

    @property
    def em_uso(self):
        """Verifica se o atributo está sendo usado em algum produto."""
        from sqlalchemy import cast, String
        return Produto.query.filter(Produto.grade_valores_adicional.cast(String).contains(self.nome)).first() is not None

class DepositoPrateleira(db.Model):
    __tablename__ = 'cat_depositos_prateleiras'
    id = db.Column(db.Integer, primary_key=True)
    deposito_id = db.Column(db.Integer, db.ForeignKey('cat_depositos.id'), nullable=False)
    nome = db.Column(db.String(50), nullable=False) # Ex: Corredor A, Prateleira 01
    ativa = db.Column(db.Boolean, default=True)

class GradeModelo(db.Model):
    __tablename__ = 'cat_grades_modelos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True) # Ex: Vestuário Adulto
    categoria = db.Column(db.String(50)) # Vestuário, Calçados, Elétricos...
    itens = db.Column(db.JSON) # ["PP", "P", "M", "G", "GG"]
    ativa = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    @property
    def em_uso(self):
        """Verifica se a grade está vinculada a algum produto ou tem movimentação."""
        # Verifica se algum produto usa esta grade
        return Produto.query.filter_by(grade_id=self.id).first() is not None

class MovimentoEstoque(db.Model):
    __tablename__ = 'ope_movimentos_estoque'
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('cat_produtos.id'), nullable=False)
    cor = db.Column(db.String(50))
    tamanho = db.Column(db.String(20))
    atributo = db.Column(db.String(100))
    tipo = db.Column(db.String(20)) # ENTRADA, SAIDA, AJUSTE
    tipo_operacao = db.Column(db.String(50)) # COMPRA, VENDA, PRODUCAO, OFICINA, AJUSTE_INVENTARIO
    quantidade = db.Column(db.Float, nullable=False)
    data = db.Column(db.DateTime, default=datetime.now)
    documento = db.Column(db.String(50)) # NF, Pedido, etc.
    documento_id = db.Column(db.Integer) # ID do Pedido ou OP
    local_id = db.Column(db.Integer) # Referência à localização (Almoxarifado, Oficina A, Oficina B)
    observacao = db.Column(db.Text)
