# =============================================================================
# Caminho  : app/models/cadastros/socio.py
# Arquivo  : socio.py
# Função   : Models de Sócio com suporte multi-empresa.
# Descrição:
#   Socio         → dados pessoais e de contato (únicos, independente de empresa)
#   SocioEmpresa  → vínculo com empresa: participação, cargo, poderes, contas,
#                   procuração, histórico e documentos por empresa.
#   Tabelas filhas de SocioEmpresa:
#     ContaBancariaSocio  → conta bancária por empresa (pró-labore, dividendos)
#     DocumentoSocio      → documentos por empresa
#     HistoricoSocio      → histórico de alterações societárias por empresa
# =============================================================================

from datetime import datetime, date
from app import db


# ─────────────────────────────────────────────────────────────────────────────
#  SOCIO — dados pessoais globais
# ─────────────────────────────────────────────────────────────────────────────

class Socio(db.Model):
    __tablename__ = 'socios'

    id            = db.Column(db.Integer, primary_key=True)
    criado_em     = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow,
                              onupdate=datetime.utcnow, nullable=False)

    # ═══════════════════════════════════════════════════════════════════════
    # DADOS PESSOAIS
    # ═══════════════════════════════════════════════════════════════════════
    foto            = db.Column(db.String(255))           # caminho do upload
    nome            = db.Column(db.String(150), nullable=False)
    cpf             = db.Column(db.String(14),  nullable=False, unique=True)
    rg              = db.Column(db.String(20))
    data_nascimento = db.Column(db.Date)
    estado_civil    = db.Column(db.String(30))            # Solteiro(a), Casado(a)...
    nacionalidade   = db.Column(db.String(50), default='Brasileira')
    profissao       = db.Column(db.String(100))

    # ═══════════════════════════════════════════════════════════════════════
    # CONTATO
    # ═══════════════════════════════════════════════════════════════════════
    telefone          = db.Column(db.String(20))
    whatsapp          = db.Column(db.String(20))
    email             = db.Column(db.String(120))         # e-mail pessoal
    email_corporativo = db.Column(db.String(120))

    # ═══════════════════════════════════════════════════════════════════════
    # ENDEREÇO RESIDENCIAL
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
    empresas = db.relationship('SocioEmpresa', back_populates='socio',
                               cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Socio {self.nome} ({self.cpf})>'

    # ═══════════════════════════════════════════════════════════════════════
    # MÉTODOS AUXILIARES
    # ═══════════════════════════════════════════════════════════════════════

    @property
    def cpf_formatado(self):
        if not self.cpf:
            return None
        d = ''.join(c for c in self.cpf if c.isdigit())
        if len(d) != 11:
            return self.cpf
        return f'{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}'

    @property
    def total_empresas_ativas(self):
        """Quantas empresas este sócio está vinculado ativamente."""
        return len([e for e in self.empresas if e.status_socio == 'ativo'])

    @classmethod
    def get_todos(cls):
        return cls.query.order_by(cls.nome).all()

    @classmethod
    def buscar_por_cpf(cls, cpf):
        cpf_limpo = ''.join(c for c in cpf if c.isdigit())
        return cls.query.filter(cls.cpf.like(f'%{cpf_limpo}%')).first()


# ─────────────────────────────────────────────────────────────────────────────
#  SOCIO EMPRESA — vínculo e dados por empresa
# ─────────────────────────────────────────────────────────────────────────────

class SocioEmpresa(db.Model):
    __tablename__ = 'socio_empresa'

    id         = db.Column(db.Integer, primary_key=True)
    socio_id   = db.Column(db.Integer, db.ForeignKey('socios.id'),   nullable=False)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)

    criado_em     = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow,
                              onupdate=datetime.utcnow, nullable=False)

    # ═══════════════════════════════════════════════════════════════════════
    # SOCIETÁRIO
    # ═══════════════════════════════════════════════════════════════════════
    tipo_socio            = db.Column(db.String(40))      # Sócio Administrador, Cotista...
    participacao          = db.Column(db.Numeric(6, 4))   # % ex: 33.3333
    data_entrada          = db.Column(db.Date)
    data_saida            = db.Column(db.Date)
    capital_integralizado = db.Column(db.Numeric(14, 2))

    # ═══════════════════════════════════════════════════════════════════════
    # CARGO & ATUAÇÃO
    # ═══════════════════════════════════════════════════════════════════════
    cargo        = db.Column(db.String(100))
    area_atuacao = db.Column(db.String(40))               # Administração, Comercial...
    status_socio = db.Column(db.String(20), default='ativo')  # ativo, inativo, licenca, retirado

    # ═══════════════════════════════════════════════════════════════════════
    # PROCURAÇÃO
    # ═══════════════════════════════════════════════════════════════════════
    tem_procuracao      = db.Column(db.Boolean, default=False)
    tipo_procuracao     = db.Column(db.String(30))        # Pública, Particular, Ad Negotia...
    procuracao_validade = db.Column(db.Date)
    procuracao_obs      = db.Column(db.Text)

    # ═══════════════════════════════════════════════════════════════════════
    # PODERES NA EMPRESA
    # ═══════════════════════════════════════════════════════════════════════
    poder_cheques       = db.Column(db.Boolean, default=False)  # Assinar Cheques
    poder_contratos     = db.Column(db.Boolean, default=False)  # Assinar Contratos
    poder_representacao = db.Column(db.Boolean, default=False)  # Representar Legalmente
    poder_bancario      = db.Column(db.Boolean, default=False)  # Movimentarmovimentcao
    # ═══════════════════════════════════════════════════════════════════════
    # RELACIONAMENTOS
    # ═══════════════════════════════════════════════════════════════════════
    socio   = db.relationship('Socio',   back_populates='empresas')
    empresa = db.relationship('Empresa', back_populates='socios')

    contas_bancarias = db.relationship('ContaBancariaSocio', back_populates='socio_empresa',
                                       cascade='all, delete-orphan')
    documentos       = db.relationship('DocumentoSocio',     back_populates='socio_empresa',
                                       cascade='all, delete-orphan')
    historico        = db.relationship('HistoricoSocio',     back_populates='socio_empresa',
                                       cascade='all, delete-orphan',
                                       order_by='HistoricoSocio.data.desc()')

    def __repr__(self):
        return f'<SocioEmpresa socio={self.socio_id} empresa={self.empresa_id}>'

    # ═══════════════════════════════════════════════════════════════════════
    # MÉTODOS AUXILIARES
    # ═══════════════════════════════════════════════════════════════════════

    @property
    def status_label(self):
        labels = {
            'ativo':    'Ativo',
            'inativo':  'Inativo',
            'licenca':  'Em Licença',
            'retirado': 'Retirado',
        }
        return labels.get(self.status_socio, self.status_socio)

    @property
    def participacao_formatada(self):
        if self.participacao is None:
            return '—'
        return f'{self.participacao:.2f}%'

    def retirar(self):
        self.status_socio = 'retirado'
        if not self.data_saida:
            self.data_saida = date.today()

    @classmethod
    def get_por_empresa(cls, empresa_id):
        """Retorna todos os sócios ativos de uma empresa."""
        return (cls.query
                .filter_by(empresa_id=empresa_id, status_socio='ativo')
                .order_by(cls.participacao.desc())
                .all())

    @classmethod
    def get_por_socio(cls, socio_id):
        """Retorna todos os vínculos de um sócio (todas as empresas)."""
        return cls.query.filter_by(socio_id=socio_id).all()


# ─────────────────────────────────────────────────────────────────────────────
#  TABELAS FILHAS DE SocioEmpresa
# ─────────────────────────────────────────────────────────────────────────────

class ContaBancariaSocio(db.Model):
    """Conta bancária por empresa.
       Ex: pró-labore Empresa A → Itaú | dividendos Empresa B → Nubank."""
    __tablename__ = 'contas_bancarias_socio'

    id               = db.Column(db.Integer, primary_key=True)
    socio_empresa_id = db.Column(db.Integer, db.ForeignKey('socio_empresa.id'), nullable=False)

    banco     = db.Column(db.String(10))    # código ex: '341'
    tipo      = db.Column(db.String(20))    # corrente, poupanca, pagamento, salario
    agencia   = db.Column(db.String(10))
    conta     = db.Column(db.String(20))
    pix       = db.Column(db.String(100))
    principal = db.Column(db.Boolean, default=False)

    socio_empresa = db.relationship('SocioEmpresa', back_populates='contas_bancarias')

    def __repr__(self):
        return f'<ContaBancariaSocio {self.banco} ag:{self.agencia} cc:{self.conta}>'


class DocumentoSocio(db.Model):
    """Documentos do sócio por empresa.
       Ex: contrato social, procuração, RG digitalizado."""
    __tablename__ = 'documentos_socio'

    id               = db.Column(db.Integer, primary_key=True)
    socio_empresa_id = db.Column(db.Integer, db.ForeignKey('socio_empresa.id'), nullable=False)

    nome_arquivo = db.Column(db.String(255), nullable=False)
    caminho      = db.Column(db.String(255), nullable=False)   # path físico / storage key
    tamanho_kb   = db.Column(db.Integer)
    enviado_em   = db.Column(db.DateTime, default=datetime.utcnow)

    socio_empresa = db.relationship('SocioEmpresa', back_populates='documentos')

    def __repr__(self):
        return f'<DocumentoSocio {self.nome_arquivo}>'


class HistoricoSocio(db.Model):
    """Histórico de alterações societárias por empresa.
       Ex: 'Participação alterada de 30% para 40% em 01/03/2025'."""
    __tablename__ = 'historico_socio'

    id               = db.Column(db.Integer, primary_key=True)
    socio_empresa_id = db.Column(db.Integer, db.ForeignKey('socio_empresa.id'), nullable=False)

    data      = db.Column(db.Date, nullable=False, default=date.today)
    descricao = db.Column(db.Text, nullable=False)
    usuario   = db.Column(db.String(100))    # quem registrou a alteração

    socio_empresa = db.relationship('SocioEmpresa', back_populates='historico')

    def __repr__(self):
        return f'<HistoricoSocio {self.data} — {self.descricao[:40]}>'