# =============================================================================
# Caminho  : app/models/cadastros/motorista.py
# Arquivo  : motorista.py
# Função   : Entidade de Motoristas (Próprios ou Terceiros)
# =============================================================================

from app import db
from datetime import datetime

class Motorista(db.Model):
    __tablename__ = 'motoristas'

    id = db.Column(db.Integer, primary_key=True)
    
    # ── Identificação ──────────────────────────────────────────────────────
    nome            = db.Column(db.String(150), nullable=False)
    cpf             = db.Column(db.String(14), unique=True, nullable=False)
    rg              = db.Column(db.String(20))
    data_nascimento = db.Column(db.Date)
    
    # ── Habilitação (CNH) ──────────────────────────────────────────────────
    cnh_numero    = db.Column(db.String(20))
    cnh_categoria = db.Column(db.String(5))
    cnh_validade  = db.Column(db.Date)
    mopp          = db.Column(db.Boolean, default=False) # Movimentação de Prod. Perigosos
    
    # ── Vínculo ────────────────────────────────────────────────────────────
    tipo_vinculo = db.Column(db.String(30)) # Próprio, Terceirizado, Agregado
    transportadora_id = db.Column(db.Integer, db.ForeignKey('transportadoras.id'), nullable=True) # Se for de transportadora
    
    # ── Contato ────────────────────────────────────────────────────────────
    whatsapp = db.Column(db.String(20))
    telefone = db.Column(db.String(20))
    email    = db.Column(db.String(120))
    
    # ── Endereço ───────────────────────────────────────────────────────────
    end_cep         = db.Column(db.String(9))
    end_logradouro  = db.Column(db.String(150))
    end_numero      = db.Column(db.String(20))
    end_complemento = db.Column(db.String(100))
    end_bairro      = db.Column(db.String(80))
    end_cidade      = db.Column(db.String(80))
    end_uf          = db.Column(db.String(2))
    
    # ── Metadados ───────────────────────────────────────────────────────────
    observacoes      = db.Column(db.Text)
    data_cadastro    = db.Column(db.DateTime, default=datetime.utcnow)
    # foto             = db.Column(db.String(255))
    ativo            = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Motorista {self.nome}>'
