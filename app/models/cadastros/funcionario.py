# =============================================================================
# Caminho  : app/models/cadastros/funcionario.py
# Arquivo  : funcionario.py
# Função   : Entidade de Funcionários e Estrutura Organizacional (HCM)
# =============================================================================

from app import db
from datetime import date, datetime

class Setor(db.Model):
    __tablename__ = 'setores'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True) # Ex: ADM-001
    nome = db.Column(db.String(100), nullable=False)
    sigla = db.Column(db.String(10)) # Ex: ADM
    
    # Hierarquia (Self-referential)
    parent_id = db.Column(db.Integer, db.ForeignKey('setores.id'), nullable=True)
    
    descricao = db.Column(db.String(255))
    ativo = db.Column(db.Boolean, default=True)

    # Relacionamento para navegar na árvore
    subsetores = db.relationship('Setor', backref=db.backref('pai', remote_side=[id]))

    def __repr__(self):
        return f'<Setor {self.nome} ({self.sigla or ""})>'

class Cargo(db.Model):
    __tablename__ = 'cargos'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True) # Ex: CAR-010
    nome = db.Column(db.String(100), unique=True, nullable=False)
    descricao = db.Column(db.String(255))
    cbo = db.Column(db.String(10))  # Classificação Brasileira de Ocupações
    ativo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Cargo {self.nome}>'

class Funcionario(db.Model):
    __tablename__ = 'funcionarios'

    id = db.Column(db.Integer, primary_key=True)
    
    # ── Identificação ──────────────────────────────────────────────────────
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    rg  = db.Column(db.String(20))
    rg_orgao = db.Column(db.String(20))
    rg_data_emissao = db.Column(db.Date)
    
    pis_pasep = db.Column(db.String(20))
    nome_mae  = db.Column(db.String(100))
    nome_pai  = db.Column(db.String(100))
    titulo_eleitor = db.Column(db.String(20)) # Mask: 0000 0000 0000
    reservista     = db.Column(db.String(20))
    cnh            = db.Column(db.String(20))
    cnh_categoria  = db.Column(db.String(10))
    
    tipo_sanguineo = db.Column(db.String(5))
    alergias       = db.Column(db.String(255))
    
    data_nascimento = db.Column(db.Date)
    genero = db.Column(db.String(20)) # M, F, N, O, P
    estado_civil = db.Column(db.String(20)) # solteiro, casado, divorciado, viuvo, separado, uniao_estavel
    
    # ── Contato ────────────────────────────────────────────────────────────
    email_pessoal = db.Column(db.String(100))
    email_corporativo = db.Column(db.String(100))
    telefone = db.Column(db.String(20))
    whatsapp = db.Column(db.String(20))
    
    # ── Endereço ───────────────────────────────────────────────────────────
    cep = db.Column(db.String(9))
    logradouro = db.Column(db.String(100))
    numero = db.Column(db.String(10))
    complemento = db.Column(db.String(100))
    bairro = db.Column(db.String(50))
    cidade = db.Column(db.String(50))
    uf = db.Column(db.String(2))
    
    # ── Vínculo Empregatício (HCM) ──────────────────────────────────────────
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'))
    matricula = db.Column(db.String(20), unique=True)
    
    cargo_id = db.Column(db.Integer, db.ForeignKey('cargos.id'))
    setor_id = db.Column(db.Integer, db.ForeignKey('setores.id'))
    
    data_admissao = db.Column(db.Date, default=date.today)
    data_demissao = db.Column(db.Date)
    
    tipo_contrato = db.Column(db.String(50), default='CLT (Indeterminado)') 
    status = db.Column(db.String(20), default='Ativo')       
    
    # ── Hierarquia & Org ───────────────────────────────────────────────────
    gestor_id = db.Column(db.Integer, db.ForeignKey('funcionarios.id'), nullable=True)
    nivel_hierarquico = db.Column(db.String(50), default='08 - Operacional') 
    unidade_negocio = db.Column(db.String(100))
    
    # ── Jornada & Escalas ──────────────────────────────────────────────────
    turno             = db.Column(db.String(50), nullable=False, default='Comercial') 
    regime_escala     = db.Column(db.String(20), default='5x2') 
    ponto_tolerancia  = db.Column(db.Integer, default=5) 
    
    centro_custo_id   = db.Column(db.Integer, db.ForeignKey('centros_custo.id'), nullable=True)
    
    # ── Saúde & Segurança (SESMT) ──────────────────────────────────────────
    aso_data      = db.Column(db.Date)
    aso_validade  = db.Column(db.Date)
    epi_entregues = db.Column(db.Text) 
    
    # ── Remuneração ────────────────────────────────────────────────────────
    salario_base = db.Column(db.Numeric(12, 2), default=0.0)
    peridiocidade = db.Column(db.String(20), default='Mensal') 
    
    # ── Dados Bancários ─────────────────────────────────────────────────────
    banco = db.Column(db.String(100))
    tipo_conta = db.Column(db.String(50)) 
    agencia = db.Column(db.String(10))
    conta = db.Column(db.String(20))
    pix = db.Column(db.String(100))
    
    # ── Documentação Digital ────────────────────────────────────────────────
    foto = db.Column(db.String(255))
    path_documentos = db.Column(db.String(255)) 
    
    # ── Metadados e Login ───────────────────────────────────────────────────
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True) 
    data_cadastro = db.Column(db.DateTime, default=datetime.now)
    ativo = db.Column(db.Boolean, default=True)
    
    # ── Relacionamentos ─────────────────────────────────────────────────────
    empresa = db.relationship('Empresa', backref='funcionarios_lista')
    cargo   = db.relationship('Cargo', backref='funcionarios_lista')
    setor   = db.relationship('Setor', backref='funcionarios_lista')
    usuario = db.relationship('Usuario', backref='funcionario_perfil', uselist=False)
    centro_custo = db.relationship('CentroCusto', backref='funcionarios')

    def __repr__(self):
        return f'<Funcionario {self.nome} - {self.matricula}>'
