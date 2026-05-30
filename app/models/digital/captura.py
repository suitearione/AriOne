# =============================================================================
# Caminho  : app/models/digital/captura.py
# Arquivo  : captura.py
# Função   : Entidade de Formulários de Captura (LeadOne)
# =============================================================================

from app import db
from datetime import datetime
import re

class Captura(db.Model):
    __tablename__ = 'capturas'

    id = db.Column(db.Integer, primary_key=True)

    # ── Identificação ──────────────────────────────────────────────────────
    nome = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(100), unique=True)  # URL amigável para link público
    campos = db.Column(db.Text)  # JSON com campos do formulário
    destino = db.Column(db.String(100))  # Email, WhatsApp, etc.
    integracao = db.Column(db.String(100))  # CRM, Planilha, etc.
    mensagem_sucesso = db.Column(db.String(250), default='Obrigado! Entraremos em contato.')

    # ── Metadados ─────────────────────────────────────────────────────────
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)

    def gerar_slug(self):
        """Gera slug a partir do nome (ex: 'Black Friday 2025' → 'black-friday-2025')"""
        s = self.nome.lower().strip()
        s = re.sub(r'[àáâãäå]', 'a', s)
        s = re.sub(r'[èéêë]', 'e', s)
        s = re.sub(r'[ìíîï]', 'i', s)
        s = re.sub(r'[òóôõö]', 'o', s)
        s = re.sub(r'[ùúûü]', 'u', s)
        s = re.sub(r'[ç]', 'c', s)
        s = re.sub(r'[^a-z0-9]+', '-', s)
        s = s.strip('-')
        self.slug = s
        return s

    def __repr__(self):
        return f'<Captura {self.nome}>'
