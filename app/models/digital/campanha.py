# =============================================================================
# Caminho  : app/models/digital/campanha.py
# Arquivo  : campanha.py
# Função   : Entidade de Campanhas (LeadOne)
# =============================================================================

from app import db
from datetime import datetime

class Campanha(db.Model):
    __tablename__ = 'campanhas'

    id = db.Column(db.Integer, primary_key=True)

    # ── Identificação ──────────────────────────────────────────────────────
    nome_campanha = db.Column(db.String(150), nullable=False)
    identificador_webhook = db.Column(db.String(150), nullable=False, unique=True)
    status = db.Column(db.Boolean, default=True)

    # ── Relacionamentos ──────────────────────────────────────────────────
    vendedor_id = db.Column(db.Integer, db.ForeignKey('comercial_vendedores.id'))
    vendedor = db.relationship('Vendedor', backref='campanhas')

    # ── Detalhes ─────────────────────────────────────────────────────────
    investimento_estimado = db.Column(db.Numeric(16, 2), default=0.0)
    data_inicio = db.Column(db.Date)

    # ── Metadados ─────────────────────────────────────────────────────────
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Campanha {self.nome_campanha}>'
