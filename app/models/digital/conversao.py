# =============================================================================
# Caminho  : app/models/digital/conversao.py
# Arquivo  : conversao.py
# Função   : Entidade de Conversões (LeadOne)
# =============================================================================

from app import db
from datetime import datetime

class Conversao(db.Model):
    __tablename__ = 'conversoes'

    id = db.Column(db.Integer, primary_key=True)

    # ── Identificação ──────────────────────────────────────────────────────
    lead = db.Column(db.String(150), nullable=False)
    data_conversao = db.Column(db.Date)
    valor = db.Column(db.Numeric(16, 2), default=0.0)
    responsavel = db.Column(db.String(150))

    # ── Metadados ─────────────────────────────────────────────────────────
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Conversao {self.lead}>'
