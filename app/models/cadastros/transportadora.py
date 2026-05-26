# =============================================================================
# Caminho  : app/models/cadastros/transportadora.py
# Arquivo  : transportadora.py
# Função   : Entidade de Transportadoras (Parceiros Logísticos)
# =============================================================================

from app import db
from datetime import datetime

class Transportadora(db.Model):
    __tablename__ = 'transportadoras'

    id = db.Column(db.Integer, primary_key=True)
    
    # ── Identificação ──────────────────────────────────────────────────────
    tipo_pessoa   = db.Column(db.String(2), default='J')
    razao_social  = db.Column(db.String(150), nullable=False)
    nome_fantasia = db.Column(db.String(150))
    cnpj_cpf      = db.Column(db.String(20), unique=True, nullable=True)
    ie_rg         = db.Column(db.String(30))
    rntrc         = db.Column(db.String(20)) # Registro Nacional de Transportadores Rodoviários de Carga
    
    # ── Contato ────────────────────────────────────────────────────────────
    whatsapp = db.Column(db.String(20))
    telefone = db.Column(db.String(20))
    email    = db.Column(db.String(120))
    website  = db.Column(db.String(150))
    
    # ── Endereço ───────────────────────────────────────────────────────────
    end_cep         = db.Column(db.String(9))
    end_logradouro  = db.Column(db.String(150))
    end_numero      = db.Column(db.String(20))
    end_complemento = db.Column(db.String(100))
    end_bairro      = db.Column(db.String(80))
    end_cidade      = db.Column(db.String(80))
    end_uf          = db.Column(db.String(2))
    
    # ── Logística & Operacional ───────────────────────────────────────────
    modal_transporte = db.Column(db.String(100)) # Aéreo, Terrestre, etc. (CSV)
    tipo_servico     = db.Column(db.String(100)) # Rodoviário, Excursão, etc. (CSV)
    prazo_entrega    = db.Column(db.Integer)    # Prazo médio em dias
    avaliacao        = db.Column(db.String(1))  # A, B, C, D
    coleta_origem    = db.Column(db.String(3))  # SIM ou NAO
    entrega_final    = db.Column(db.String(3))  # SIM ou NAO
    entregador_final = db.Column(db.String(50)) # Não se Aplica ou Entregador
    coleta_veiculos  = db.Column(db.String(100)) # Moto, Carro Leve, Carro Pesado (CSV)
    entrega_veiculos = db.Column(db.String(100)) # Moto, Carro Leve, Carro Pesado (CSV)
    
    # ── Contato Adicional ─────────────────────────────────────────────────
    contato_nome     = db.Column(db.String(100))
    contato_cargo    = db.Column(db.String(100))
    parceira_desde   = db.Column(db.Date)
    rotas_data       = db.Column(db.Text) # JSON string of routes
    logo             = db.Column(db.String(255)) # URL ou caminho da logo
    
    # ── Endereço Comercial (Sede) ──────────────────────────────────────────
    end_com_cep         = db.Column(db.String(9))
    end_com_logradouro  = db.Column(db.String(150))
    end_com_numero      = db.Column(db.String(20))
    end_com_complemento = db.Column(db.String(100))
    end_com_bairro      = db.Column(db.String(80))
    end_com_cidade      = db.Column(db.String(80))
    end_com_uf          = db.Column(db.String(2))

    # ── Endereço Entrega (Coleta) ─────────────────────────────────────────
    end_ent_cep         = db.Column(db.String(9))
    end_ent_logradouro  = db.Column(db.String(150))
    end_ent_numero      = db.Column(db.String(20))
    end_ent_complemento = db.Column(db.String(100))
    end_ent_bairro      = db.Column(db.String(80))
    end_ent_cidade      = db.Column(db.String(80))
    end_ent_uf          = db.Column(db.String(2))
    
    # ── Financeiro ────────────────────────────────────────────────────────
    prazo_pagamento  = db.Column(db.String(50))
    forma_pagamento  = db.Column(db.String(50))
    tabela_frete     = db.Column(db.String(100))
    banco_nome       = db.Column(db.String(100))
    banco_codigo     = db.Column(db.String(10))
    banco_agencia    = db.Column(db.String(20))
    banco_conta      = db.Column(db.String(20))
    pix_chave        = db.Column(db.String(100))

    # ── Metadados ───────────────────────────────────────────────────────────
    observacoes   = db.Column(db.Text)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    ativo         = db.Column(db.Boolean, default=True)

    # Relacionamento
    motoristas = db.relationship('Motorista', backref='transportadora', lazy=True)

    def __repr__(self):
        return f'<Transportadora {self.razao_social}>'
