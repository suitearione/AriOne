# =============================================================================
# Caminho  : app/models/cadastros/investidor.py
# Arquivo  : investidor.py
# Função   : Models de Investidor com suporte multi-empresa.
# Descrição:
#   Investidor         → dados pessoais PF/PJ (únicos, independente de empresa)
#   InvestidorEmpresa  → vínculo com empresa: acordo, rentabilidade, movimentações,
#                        contas bancárias e documentos por empresa.
#   Tabelas filhas de InvestidorEmpresa:
#     MovimentacaoInvestidor    → aportes, resgates e rendimentos por empresa
#     ContaBancariaInvestidor   → conta para recebimento por empresa
#     DocumentoInvestidor       → documentos por empresa
# =============================================================================

from datetime import datetime, date
from app import db


# ─────────────────────────────────────────────────────────────────────────────
#  INVESTIDOR — dados pessoais globais (PF ou PJ)
# ─────────────────────────────────────────────────────────────────────────────

class Investidor(db.Model):
    __tablename__ = 'investidores'

    id            = db.Column(db.Integer, primary_key=True)
    criado_em     = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow,
                              onupdate=datetime.utcnow, nullable=False)

    # ═══════════════════════════════════════════════════════════════════════
    # TIPO PF / PJ
    # ═══════════════════════════════════════════════════════════════════════
    tipo_pessoa = db.Column(db.String(2), default='pf')   # 'pf' | 'pj'

    # ═══════════════════════════════════════════════════════════════════════
    # IDENTIFICAÇÃO — PESSOA FÍSICA
    # ═══════════════════════════════════════════════════════════════════════
    nome            = db.Column(db.String(150))
    cpf             = db.Column(db.String(14),  unique=True)
    rg              = db.Column(db.String(20))
    data_nascimento = db.Column(db.Date)
    nacionalidade   = db.Column(db.String(50), default='Brasileira')
    profissao       = db.Column(db.String(100))
    estado_civil    = db.Column(db.String(30))

    # ═══════════════════════════════════════════════════════════════════════
    # IDENTIFICAÇÃO — PESSOA JURÍDICA
    # ═══════════════════════════════════════════════════════════════════════
    razao_social    = db.Column(db.String(150))
    nome_fantasia   = db.Column(db.String(150))
    cnpj            = db.Column(db.String(18),  unique=True)
    ie              = db.Column(db.String(30))    # Inscrição Estadual
    responsavel     = db.Column(db.String(150))   # Representante legal
    cpf_responsavel = db.Column(db.String(14))

    # ═══════════════════════════════════════════════════════════════════════
    # CONTATO
    # ═══════════════════════════════════════════════════════════════════════
    telefone = db.Column(db.String(20))
    whatsapp = db.Column(db.String(20))
    email    = db.Column(db.String(120))
    email2   = db.Column(db.String(120))          # e-mail alternativo

    # ═══════════════════════════════════════════════════════════════════════
    # ENDEREÇO
    # ═══════════════════════════════════════════════════════════════════════
    cep         = db.Column(db.String(9))
    logradouro  = db.Column(db.String(150))
    numero      = db.Column(db.String(10))
    complemento = db.Column(db.String(60))
    bairro      = db.Column(db.String(80))
    cidade      = db.Column(db.String(80))
    uf          = db.Column(db.String(2))
    pais        = db.Column(db.String(50), default='Brasil')

    # ═══════════════════════════════════════════════════════════════════════
    # RELACIONAMENTOS
    # ═══════════════════════════════════════════════════════════════════════
    empresas = db.relationship('InvestidorEmpresa', back_populates='investidor',
                               cascade='all, delete-orphan')

    def __repr__(self):
        label = self.nome or self.razao_social
        return f'<Investidor {label}>'

    # ═══════════════════════════════════════════════════════════════════════
    # MÉTODOS AUXILIARES
    # ═══════════════════════════════════════════════════════════════════════

    @property
    def nome_exibicao(self):
        """Retorna nome independente do tipo PF/PJ."""
        return self.nome if self.tipo_pessoa == 'pf' else (self.nome_fantasia or self.razao_social)

    @property
    def total_empresas_ativas(self):
        return len([e for e in self.empresas if e.status_investimento == 'ativo'])

    @classmethod
    def get_todos(cls):
        return cls.query.order_by(cls.nome, cls.razao_social).all()

    @classmethod
    def buscar_por_cpf_cnpj(cls, documento):
        doc_limpo = ''.join(c for c in documento if c.isdigit())
        return cls.query.filter(
            db.or_(
                cls.cpf.like(f'%{doc_limpo}%'),
                cls.cnpj.like(f'%{doc_limpo}%')
            )
        ).first()


# ─────────────────────────────────────────────────────────────────────────────
#  INVESTIDOR EMPRESA — acordo e dados por empresa
# ─────────────────────────────────────────────────────────────────────────────

class InvestidorEmpresa(db.Model):
    __tablename__ = 'investidor_empresa'

    id            = db.Column(db.Integer, primary_key=True)
    investidor_id = db.Column(db.Integer, db.ForeignKey('investidores.id'), nullable=False)
    empresa_id    = db.Column(db.Integer, db.ForeignKey('empresas.id'),     nullable=False)

    criado_em     = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow,
                              onupdate=datetime.utcnow, nullable=False)

    # ═══════════════════════════════════════════════════════════════════════
    # ACORDO DE INVESTIMENTO
    # ═══════════════════════════════════════════════════════════════════════
    participacao        = db.Column(db.Numeric(6, 4))    # % na empresa
    tipo_investimento   = db.Column(db.String(40))       # Mútuo, Equity, Debênture...
    data_inicio         = db.Column(db.Date)
    data_vencimento     = db.Column(db.Date)
    status_investimento = db.Column(db.String(20), default='ativo')  # ativo, encerrado, inadimplente, renegociado
    obs_investimento    = db.Column(db.Text)

    # ═══════════════════════════════════════════════════════════════════════
    # RENTABILIDADE ACORDADA
    # ═══════════════════════════════════════════════════════════════════════
    indexador       = db.Column(db.String(20))           # fixo, cdi, ipca, igpm, selic, dolar, livre
    taxa_mensal     = db.Column(db.Numeric(8, 4))        # % a.m.
    taxa_anual      = db.Column(db.Numeric(8, 4))        # % a.a. (calculado no form)
    forma_pagamento = db.Column(db.String(20))           # mensal, trimestral, semestral, anual, vencimento

    # ═══════════════════════════════════════════════════════════════════════
    # RELACIONAMENTOS
    # ═══════════════════════════════════════════════════════════════════════
    investidor = db.relationship('Investidor', back_populates='empresas')
    empresa    = db.relationship('Empresa',    back_populates='investidores')

    movimentacoes    = db.relationship('MovimentacaoInvestidor',  back_populates='investidor_empresa',
                                       cascade='all, delete-orphan',
                                       order_by='MovimentacaoInvestidor.data.desc()')
    contas_bancarias = db.relationship('ContaBancariaInvestidor', back_populates='investidor_empresa',
                                       cascade='all, delete-orphan')
    documentos       = db.relationship('DocumentoInvestidor',     back_populates='investidor_empresa',
                                       cascade='all, delete-orphan')

    def __repr__(self):
        return f'<InvestidorEmpresa investidor={self.investidor_id} empresa={self.empresa_id}>'

    # ═══════════════════════════════════════════════════════════════════════
    # MÉTODOS AUXILIARES
    # ═══════════════════════════════════════════════════════════════════════

    @property
    def saldo_atual(self):
        """Saldo em R$: aportes − resgates + rendimentos nesta empresa."""
        return sum(m.valor_em_reais for m in self.movimentacoes)

    @property
    def total_aportado(self):
        return sum(m.valor_em_reais for m in self.movimentacoes if m.tipo == 'aporte')

    @property
    def status_label(self):
        labels = {
            'ativo':        'Ativo',
            'encerrado':    'Encerrado',
            'inadimplente': 'Inadimplente',
            'renegociado':  'Renegociado',
        }
        return labels.get(self.status_investimento, self.status_investimento)

    @property
    def participacao_formatada(self):
        if self.participacao is None:
            return '—'
        return f'{self.participacao:.2f}%'

    @classmethod
    def get_por_empresa(cls, empresa_id):
        """Retorna todos os investidores ativos de uma empresa."""
        return (cls.query
                .filter_by(empresa_id=empresa_id, status_investimento='ativo')
                .order_by(cls.data_inicio.desc())
                .all())

    @classmethod
    def get_por_investidor(cls, investidor_id):
        """Retorna todos os vínculos de um investidor (todas as empresas)."""
        return cls.query.filter_by(investidor_id=investidor_id).all()


# ─────────────────────────────────────────────────────────────────────────────
#  TABELAS FILHAS DE InvestidorEmpresa
# ─────────────────────────────────────────────────────────────────────────────

class MovimentacaoInvestidor(db.Model):
    """Aportes, resgates e rendimentos por empresa — suporta múltiplas moedas."""
    __tablename__ = 'movimentacoes_investidor'

    id                   = db.Column(db.Integer, primary_key=True)
    investidor_empresa_id = db.Column(db.Integer, db.ForeignKey('investidor_empresa.id'), nullable=False)

    data           = db.Column(db.Date,    nullable=False)
    tipo           = db.Column(db.String(15), nullable=False)  # aporte | resgate | rendimento
    moeda          = db.Column(db.String(10), default='BRL')   # BRL, USD, EUR, BTC, OUTRO
    valor          = db.Column(db.Numeric(16, 4), nullable=False)  # valor na moeda original
    cotacao        = db.Column(db.Numeric(16, 4), default=1)       # cotação em R$ no dia
    valor_em_reais = db.Column(db.Numeric(16, 2))                  # valor * cotacao (± sinal)
    descricao      = db.Column(db.String(200))
    comprovante    = db.Column(db.String(100))    # nº TED / referência
    registrado_em  = db.Column(db.DateTime, default=datetime.utcnow)

    investidor_empresa = db.relationship('InvestidorEmpresa', back_populates='movimentacoes')

    def __repr__(self):
        return f'<Movimentacao {self.tipo} R${self.valor_em_reais} em {self.data}>'


class ContaBancariaInvestidor(db.Model):
    """Conta bancária por empresa — ex: recebe retorno da Empresa A no Itaú,
       retorno da Empresa B no Nubank."""
    __tablename__ = 'contas_bancarias_investidor'

    id                    = db.Column(db.Integer, primary_key=True)
    investidor_empresa_id = db.Column(db.Integer, db.ForeignKey('investidor_empresa.id'), nullable=False)

    banco     = db.Column(db.String(10))    # código ex: '341'
    tipo      = db.Column(db.String(20))    # corrente, poupanca, pagamento, salario
    agencia   = db.Column(db.String(10))
    conta     = db.Column(db.String(20))
    pix       = db.Column(db.String(100))
    principal = db.Column(db.Boolean, default=False)

    investidor_empresa = db.relationship('InvestidorEmpresa', back_populates='contas_bancarias')

    def __repr__(self):
        return f'<ContaBancariaInvestidor {self.banco} ag:{self.agencia} cc:{self.conta}>'


class DocumentoInvestidor(db.Model):
    """Documentos do investidor por empresa — ex: contrato de mútuo, comprovantes."""
    __tablename__ = 'documentos_investidor'

    id                    = db.Column(db.Integer, primary_key=True)
    investidor_empresa_id = db.Column(db.Integer, db.ForeignKey('investidor_empresa.id'), nullable=False)

    nome_arquivo = db.Column(db.String(255), nullable=False)
    caminho      = db.Column(db.String(255), nullable=False)   # path físico / storage key
    tamanho_kb   = db.Column(db.Integer)
    enviado_em   = db.Column(db.DateTime, default=datetime.utcnow)

    investidor_empresa = db.relationship('InvestidorEmpresa', back_populates='documentos')

    def __repr__(self):
        return f'<DocumentoInvestidor {self.nome_arquivo}>'