# =============================================================================
# Caminho  : app/models/digital/automacao.py
# Arquivo  : automacao.py
# Função   : Entidade de Automações (LeadOne)
# =============================================================================

from app import db
from datetime import datetime

automacao_leads = db.Table('automacao_leads',
    db.Column('automacao_id', db.Integer, db.ForeignKey('automacoes.id'), primary_key=True),
    db.Column('lead_id', db.Integer, db.ForeignKey('leads.id'), primary_key=True)
)

class Automacao(db.Model):
    __tablename__ = 'automacoes'

    id = db.Column(db.Integer, primary_key=True)

    # ── Identificação ──────────────────────────────────────────────────────
    nome = db.Column(db.String(150), nullable=False)
    gatilho = db.Column(db.String(100))  # Lead cadastrado, Etapa alterada, etc.
    acao = db.Column(db.String(100))  # Enviar WhatsApp, Email, etc.
    delay_horas = db.Column(db.Integer, default=0)  # Delay em horas

    # ── Metadados ─────────────────────────────────────────────────────────
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)

    leads = db.relationship('Lead', secondary=automacao_leads, lazy='subquery',
                            backref=db.backref('automacoes', lazy=True))

    def __repr__(self):
        return f'<Automacao {self.nome}>'
