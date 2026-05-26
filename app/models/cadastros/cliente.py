# =============================================================================
# Caminho  : app/models/cadastros/cliente.py
# Arquivo  : cliente.py
# Função   : Entidade de Clientes (Pessoa Física ou Jurídica)
# =============================================================================

from app import db
from datetime import datetime

class Cliente(db.Model):
    __tablename__ = 'clientes'

    id = db.Column(db.Integer, primary_key=True)
    
    # ── Identificação ──────────────────────────────────────────────────────
    tipo_pessoa     = db.Column(db.String(2), default='F') # F=Física, J=Jurídica
    nome            = db.Column(db.String(150), nullable=False)
    apelido         = db.Column(db.String(150)) # Nome Fantasia
    cpf_cnpj        = db.Column(db.String(20), unique=True, nullable=False)
    rg_ie           = db.Column(db.String(30)) # RG ou Inscrição Estadual
    data_nascimento = db.Column(db.Date)
    genero          = db.Column(db.String(50))
    
    # ── Contato ────────────────────────────────────────────────────────────
    whatsapp = db.Column(db.String(20))
    telefone = db.Column(db.String(20))
    email    = db.Column(db.String(120))
    instagram = db.Column(db.String(100))
    
    # ── Perfil Comercial ───────────────────────────────────────────────────
    origem         = db.Column(db.String(50))   # Instagram, Indicação, etc.
    categoria      = db.Column(db.String(50))   # Varejo, Atacado, etc.
    rating         = db.Column(db.String(10))   # A, B, C, D
    limite_credito = db.Column(db.Numeric(16, 2), default=0.0)
    cliente_desde  = db.Column(db.Date)
    
    # ── Endereço Residencial/Principal ─────────────────────────────────────
    end_res_cep         = db.Column(db.String(9))
    end_res_logradouro  = db.Column(db.String(150))
    end_res_numero      = db.Column(db.String(20))
    end_res_complemento = db.Column(db.String(100))
    end_res_bairro      = db.Column(db.String(80))
    end_res_cidade      = db.Column(db.String(80))
    end_res_uf          = db.Column(db.String(2))
    end_res_obs         = db.Column(db.String(255))
    
    # ── Endereço Entrega ───────────────────────────────────────────────────
    end_ent_cep         = db.Column(db.String(9))
    end_ent_logradouro  = db.Column(db.String(150))
    end_ent_numero      = db.Column(db.String(20))
    end_ent_complemento = db.Column(db.String(100))
    end_ent_bairro      = db.Column(db.String(80))
    end_ent_cidade      = db.Column(db.String(80))
    end_ent_uf          = db.Column(db.String(2))
    end_ent_obs         = db.Column(db.String(255))
    
    # ── Dados Financeiros ──────────────────────────────────────────────────
    prazo_pagamento = db.Column(db.String(50))
    forma_pagamento = db.Column(db.String(50))
    desconto_padrao = db.Column(db.Numeric(5, 2), default=0.0)
    limite_compras  = db.Column(db.Numeric(16, 2), default=0.0)
    tabela_preco    = db.Column(db.String(10), default='Padrão')
    
    # ── Dados Bancários ─────────────────────────────────────────────────────
    banco         = db.Column(db.String(150)) # Padrão FEBRABAN
    banco_nome    = db.Column(db.String(100))
    banco_codigo  = db.Column(db.String(10))
    banco_agencia = db.Column(db.String(20))
    banco_conta   = db.Column(db.String(30))
    banco_tipo    = db.Column(db.String(20))
    pix_chave     = db.Column(db.String(150))
    
    # ── Metadados & Alertas ─────────────────────────────────────────────────
    observacoes      = db.Column(db.Text)
    bloqueio_credito = db.Column(db.Boolean, default=False)
    motivo_bloqueio  = db.Column(db.String(255))
    data_cadastro    = db.Column(db.DateTime, default=datetime.utcnow)
    foto             = db.Column(db.String(255))
    ativo            = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Cliente {self.nome}>'
