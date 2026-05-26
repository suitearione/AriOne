from app.extensions import db
from datetime import datetime

# ── Vendedores ──────────────────────────────────────────────────────────────
class Vendedor(db.Model):
    __tablename__ = 'comercial_vendedores'
    id = db.Column(db.Integer, primary_key=True)
    funcionario_id = db.Column(db.Integer, db.ForeignKey('funcionarios.id'), unique=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'))
    
    nome_exibivel = db.Column(db.String(100)) # Nome Comercial / Consultor
    
    comissao_padrao = db.Column(db.Float, default=0.0)
    meta_mensal = db.Column(db.Float, default=0.0)
    canais_venda = db.Column(db.String(255)) # Canais autorizados (ex: "WHATSAPP SUPORTE OFICIAL, WEBCHAT")
    
    # Visual
    cor_identidade = db.Column(db.String(20), default='#2980B9') # Cor para gráficos
    
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relacionamentos
    funcionario = db.relationship('Funcionario', backref=db.backref('vendedor_perfil', uselist=False))
    empresa = db.relationship('Empresa', backref='vendedores_lista')

# ── Rede de Revendas ────────────────────────────────────────────────────────
class RedeRevenda(db.Model):
    __tablename__ = 'comercial_redes_revendas'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    sigla = db.Column(db.String(20))
    ativa = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    revendedores = db.relationship('Revendedor', backref='rede', lazy=True)

# ── Revendedores ────────────────────────────────────────────────────────────
class Revendedor(db.Model):
    __tablename__ = 'comercial_revendedores'
    id = db.Column(db.Integer, primary_key=True)
    rede_id = db.Column(db.Integer, db.ForeignKey('comercial_redes_revendas.id'))
    nome = db.Column(db.String(100), nullable=False)
    cpf_cnpj = db.Column(db.String(20))
    email = db.Column(db.String(100))
    telefone = db.Column(db.String(20))
    whatsapp = db.Column(db.String(20))
    foto = db.Column(db.String(255))
    categoria = db.Column(db.String(50))
    tipo_revenda = db.Column(db.String(50))
    regiao = db.Column(db.String(100))
    rating = db.Column(db.String(10))
    limite_credito = db.Column(db.Float, default=0.0)
    end_cep = db.Column(db.String(10))
    end_logradouro = db.Column(db.String(150))
    end_numero = db.Column(db.String(10))
    observacoes = db.Column(db.Text)
    comissao = db.Column(db.Float, default=0.0)
    ativa = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

# ── Ministérios ─────────────────────────────────────────────────────────────
class Ministerio(db.Model):
    __tablename__ = 'comercial_ministerios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    lider = db.Column(db.String(100))
    email = db.Column(db.String(100))
    whatsapp = db.Column(db.String(20))
    registro = db.Column(db.String(50)) # CNPJ / Registro
    foto = db.Column(db.String(255))
    tipo = db.Column(db.String(50)) # Local, Regional, Global
    ativa = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

# ── Parcerias Ministeriais ────────────────────────────────────────────────
class ParceriaMinisterial(db.Model):
    __tablename__ = 'comercial_parcerias_ministeriais'
    id = db.Column(db.Integer, primary_key=True)
    ministerio_id = db.Column(db.Integer, db.ForeignKey('comercial_ministerios.id'))
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    valor = db.Column(db.Float, default=0.0)
    frequencia = db.Column(db.String(50)) # Semanal, Quinzenal, etc.
    tipo_cobranca = db.Column(db.String(50)) # Boleto, Cartão, etc.
    data_assinatura = db.Column(db.Date)
    data_inicio = db.Column(db.Date)
    data_fim = db.Column(db.Date)
    anexos_json = db.Column(db.Text) # Lista de caminhos em JSON
    created_at = db.Column(db.DateTime, default=datetime.now)

# ── Redes de Influência ────────────────────────────────────────────────────
class RedeInfluencia(db.Model):
    __tablename__ = 'comercial_redes_influencia'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    ativa = db.Column(db.Boolean, default=True)

# ── Influenciadores ────────────────────────────────────────────────────────
class Influenciador(db.Model):
    __tablename__ = 'comercial_influenciadores'
    id = db.Column(db.Integer, primary_key=True)
    rede_id = db.Column(db.Integer, db.ForeignKey('comercial_redes_influencia.id'))
    nome = db.Column(db.String(100), nullable=False)
    handle = db.Column(db.String(50)) # @username
    nicho = db.Column(db.String(50))
    alcance = db.Column(db.Integer) # Seguidores
    seguidores = db.Column(db.String(20))
    whatsapp = db.Column(db.String(20))
    email = db.Column(db.String(100))
    instagram = db.Column(db.String(100))
    plataforma = db.Column(db.String(50))
    foto = db.Column(db.String(255))
    status_contrato = db.Column(db.String(20), default='ATIVO')
    observacoes = db.Column(db.Text)
    ativa = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

# ── Parcerias Gerais ───────────────────────────────────────────────────────
class Parceria(db.Model):
    __tablename__ = 'comercial_parcerias'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50))
    status = db.Column(db.String(20), default='Ativo')

# ── Acordos Comerciais ────────────────────────────────────────────────────
class AcordoComercial(db.Model):
    __tablename__ = 'comercial_acordos'
    id = db.Column(db.Integer, primary_key=True)
    parceria_id = db.Column(db.Integer, db.ForeignKey('comercial_parcerias.id'))
    numero_contrato = db.Column(db.String(50))
    valor = db.Column(db.Float)
    comissao_fixa = db.Column(db.Float)

# ── Estilistas ──────────────────────────────────────────────────────────────
class Estilista(db.Model):
    __tablename__ = 'comercial_estilistas'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    especialidade = db.Column(db.String(100))
    portfólio_url = db.Column(db.String(255))
    whatsapp = db.Column(db.String(20))
    email = db.Column(db.String(100))
    foto = db.Column(db.String(255))
    disponibilidade = db.Column(db.String(50))
    observacoes = db.Column(db.Text)
    ativa = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

# ── Parceiros Criativos ────────────────────────────────────────────────────
class ParceiroCriativo(db.Model):
    __tablename__ = 'comercial_parceiros_criativos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    area_atuacao = db.Column(db.String(100)) # Foto, Vídeo, Design
    ativa = db.Column(db.Boolean, default=True)

# ── Tabelas de Preços (ESTRUTURA ERP MODERNA) ──────────────────────────────
class TabelaPreco(db.Model):
    __tablename__ = 'comercial_tabelas_precos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(255))
    
    # Lógica de Cálculo Padrão
    base_calculo = db.Column(db.String(50), default='venda_base') # venda_base, custo_base
    ajuste_tipo = db.Column(db.String(20), default='fixo') # porcentagem, fixo
    ajuste_valor = db.Column(db.Float, default=0.0) # Ex: 10.0 (pode ser + ou -)
    
    data_inicio = db.Column(db.Date)
    data_fim = db.Column(db.Date)
    
    # Segmentação
    perfil_cliente = db.Column(db.String(50)) # Consumidor, Revenda, Distribuidor
    exclusiva_rede_id = db.Column(db.Integer, db.ForeignKey('comercial_redes_revendas.id'))
    
    ativa = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    itens = db.relationship('TabelaPrecoItem', backref='tabela', lazy=True, cascade="all, delete-orphan")

class TabelaPrecoItem(db.Model):
    __tablename__ = 'comercial_tabelas_precos_itens'
    id = db.Column(db.Integer, primary_key=True)
    tabela_id = db.Column(db.Integer, db.ForeignKey('comercial_tabelas_precos.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('cat_produtos.id'), nullable=False)
    
    # Relacionamento
    produto = db.relationship('Produto', backref='itens_em_tabelas', lazy=True)
    
    # Preço específico para este item nesta tabela
    preco_venda = db.Column(db.Float, nullable=False)
    margem_praticada = db.Column(db.Float) # Opcional: Para auditoria de rentabilidade
    
    ativa = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

# ── Perfis de Venda (Golden Standard) ──────────────────────────────────────
class PerfilVenda(db.Model):
    __tablename__ = 'comercial_perfis_venda'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    descricao = db.Column(db.Text)
    ativa = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<PerfilVenda {self.nome}>'

# ── Operadoras Financeiras (Quiet Luxury Standard) ─────────────────────────
class OperadoraFinanceira(db.Model):
    __tablename__ = 'comercial_operadoras_financeiras'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    nome_fantasia = db.Column(db.String(100))
    cnpj = db.Column(db.String(20))
    site = db.Column(db.String(255))
    email_suporte = db.Column(db.String(100))
    telefone_suporte = db.Column(db.String(20))
    
    # Configurações de Taxas (Padrão)
    taxa_debito = db.Column(db.Float, default=0.0)
    taxa_pix = db.Column(db.Float, default=0.0)
    taxa_credito_vista = db.Column(db.Float, default=0.0)
    taxa_credito_parcelado = db.Column(db.Float, default=0.0)
    taxa_antecipacao = db.Column(db.Float, default=0.0)
    taxas_parcelamento = db.Column(db.Text) # JSON string
    
    # Visual e Status
    icone = db.Column(db.String(50), default='fas fa-landmark')
    cor = db.Column(db.String(20), default='#2980B9')
    ativa = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'nome_fantasia': self.nome_fantasia,
            'cnpj': self.cnpj,
            'site': self.site,
            'email_suporte': self.email_suporte,
            'telefone_suporte': self.telefone_suporte,
            'taxa_debito': self.taxa_debito,
            'taxa_pix': self.taxa_pix,
            'taxa_credito_vista': self.taxa_credito_vista,
            'taxa_credito_parcelado': self.taxa_credito_parcelado,
            'taxa_antecipacao': self.taxa_antecipacao,
            'taxas_parcelamento': self.taxas_parcelamento,
            'icone': self.icone,
            'cor': self.cor,
            'ativa': self.ativa
        }

# ── Formas de Pagamento (Quiet Luxury Standard) ─────────────────────────────
class FormaPagamento(db.Model):
    __tablename__ = 'comercial_formas_pagamento'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    agrupador_operacional = db.Column(db.String(50), default='OUTROS') # CARTÃO, BOLETO, PIX, DINHEIRO, OUTROS
    baixa_automatica = db.Column(db.Boolean, default=False)
    tipo = db.Column(db.String(50), default='DINHEIRO') # CARTÃO, BOLETO, PIX, DINHEIRO, OUTROS
    
    # Vinculação com Operadora
    operadora_id = db.Column(db.Integer, db.ForeignKey('comercial_operadoras_financeiras.id'))
    operadora = db.relationship('OperadoraFinanceira', backref='formas_pagamento', lazy=True)
    
    # Regras de Parcelamento
    max_parcelas = db.Column(db.Integer, default=1)
    intervalo_dias = db.Column(db.Integer, default=0) # Ex: 30 para mensal
    parcela_minima = db.Column(db.Float, default=0.0)
    
    # Regras Financeiras
    taxa_juros = db.Column(db.Float, default=0.0) # Acréscimo
    percentual_desconto = db.Column(db.Float, default=0.0) # Desconto por escolher esta forma
    
    # Visual e Integração
    icone = db.Column(db.String(50), default='fas fa-money-bill-wave')
    cor = db.Column(db.String(20), default='#2ECC71')
    
    ativa = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'agrupador_operacional': self.agrupador_operacional,
            'baixa_automatica': self.baixa_automatica,
            'tipo': self.tipo,
            'operadora_id': self.operadora_id,
            'operadora_nome': self.operadora.nome if self.operadora else None,
            'max_parcelas': self.max_parcelas,
            'intervalo_dias': self.intervalo_dias,
            'parcela_minima': self.parcela_minima,
            'taxa_juros': self.taxa_juros,
            'percentual_desconto': self.percentual_desconto,
            'icone': self.icone,
            'cor': self.cor,
            'ativa': self.ativa
        }

# ── Canais de Venda (ChatOne / Omnichannel Standard) ────────────────────────
class CanalVenda(db.Model):
    __tablename__ = 'com_canais_venda'
    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, default=1)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), default='WhatsApp API')
    status = db.Column(db.String(30), default='ATIVO')
    departamento = db.Column(db.String(100), default='Suporte N1')
    identificador = db.Column(db.String(100))
    api_token = db.Column(db.String(255))
    webhook_url = db.Column(db.String(255))
    ativar_ia = db.Column(db.String(10), default='SIM')
    sla_minutos = db.Column(db.Integer, default=15)
    mensagem_ausencia = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'empresa_id': self.empresa_id,
            'nome': self.nome,
            'tipo': self.tipo,
            'status': self.status,
            'departamento': self.departamento,
            'identificador': self.identificador,
            'api_token': self.api_token,
            'webhook_url': self.webhook_url,
            'ativar_ia': self.ativar_ia,
            'sla_minutos': self.sla_minutos,
            'mensagem_ausencia': self.mensagem_ausencia
        }
