# =============================================================================
# Caminho  : app/models/digital/lead.py
# Arquivo  : lead.py
# Função   : Entidade de Leads (LeadOne - Pipeline de Vendas)
# =============================================================================

from app import db
from datetime import datetime

class Lead(db.Model):
    __tablename__ = 'leads'

    id = db.Column(db.Integer, primary_key=True)

    # ── Identificação ──────────────────────────────────────────────────────
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120))
    telefone = db.Column(db.String(20))

    # ── Pipeline ───────────────────────────────────────────────────────────
    # Etapas: Novo, Contato Feito, Em Negociação, Orçamento Enviado,
    #         Venda Efetuada, Perdido
    etapa = db.Column(db.String(50), default='Novo')
    origem = db.Column(db.String(50))  # Instagram, Site, Indicação, CSV, etc.

    # ── Metadados ─────────────────────────────────────────────────────────
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    observacoes = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Lead {self.nome}>'
