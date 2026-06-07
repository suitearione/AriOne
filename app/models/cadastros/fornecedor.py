# =============================================================================
# Caminho  : app/models/cadastros/fornecedor.py
# Arquivo  : fornecedor.py
# Função   : Entidade de Fornecedores (Pessoa Física ou Jurídica)
# =============================================================================

from app import db
from datetime import datetime

class Fornecedor(db.Model):
    __tablename__ = 'fornecedores'

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False, index=True)

    # ── Identificação ──────────────────────────────────────────────────────
    tipo_pessoa     = db.Column(db.String(2), default='J') # F=Física, J=Jurídica
    razao_social    = db.Column(db.String(150), nullable=False)
    nome_fantasia   = db.Column(db.String(150))
    cnpj_cpf        = db.Column(db.String(20), unique=True, nullable=False)
    ie_rg           = db.Column(db.String(30)) 
    data_abertura   = db.Column(db.Date)
    
    # ── Contato ────────────────────────────────────────────────────────────
    contato_nome = db.Column(db.String(100))
    contato_cargo = db.Column(db.String(100))
    whatsapp     = db.Column(db.String(20))
    telefone     = db.Column(db.String(20))
    email        = db.Column(db.String(120))
    website      = db.Column(db.String(150))
    
    # ── Perfil Comercial ───────────────────────────────────────────────────
    categoria      = db.Column(db.String(50))   # Matéria-prima, Serviços, etc.
    avaliacao      = db.Column(db.String(10))   # A, B, C (Rating do fornecedor)
    prazo_entrega  = db.Column(db.Integer)      # Lead time em dias
    
    # ── Endereço ───────────────────────────────────────────────────────────
    end_cep         = db.Column(db.String(9))
    end_logradouro  = db.Column(db.String(150))
    end_numero      = db.Column(db.String(20))
    end_complemento = db.Column(db.String(100))
    end_bairro      = db.Column(db.String(80))
    end_cidade      = db.Column(db.String(80))
    end_uf          = db.Column(db.String(2))
    
    # ── Dados Financeiros ──────────────────────────────────────────────────
    prazo_pagamento = db.Column(db.String(50))
    forma_pagamento = db.Column(db.String(50))
    moeda           = db.Column(db.String(10), default='BRL')
    
    # ── Dados Bancários ─────────────────────────────────────────────────────
    banco_nome    = db.Column(db.String(100))
    banco_codigo  = db.Column(db.String(10))
    banco_agencia = db.Column(db.String(20))
    banco_conta   = db.Column(db.String(30))
    banco_tipo    = db.Column(db.String(20))
    pix_tipo      = db.Column(db.String(20)) # CPF, CNPJ, Email, Celular, Aleatorio
    pix_chave     = db.Column(db.String(150))
    
    # ── Metadados ───────────────────────────────────────────────────────────
    observacoes      = db.Column(db.Text)
    data_cadastro    = db.Column(db.DateTime, default=datetime.utcnow)
    # foto             = db.Column(db.String(255))
    is_fp            = db.Column(db.Boolean, default=False)
    ativo            = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Fornecedor {self.razao_social}>'
