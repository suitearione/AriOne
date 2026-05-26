# =============================================================================
# Caminho  : app/models/sistema/perfil.py
# Arquivo  : perfil.py
# Função   : Model da entidade Perfil, gerenciando regras e matriz de acesso.
# =============================================================================

from app.extensions import db
from datetime import datetime

class Perfil(db.Model):
    __tablename__ = 'perfis'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    descricao = db.Column(db.String(255))
    permissoes = db.Column(db.JSON, default=dict) # Estrutura: {"Modulo1": {"visualizar": True, "criar": False...}, ...}
    
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    # usuários vinculados
    usuarios = db.relationship('Usuario', backref='perfil_obj', lazy='dynamic')

    def __repr__(self):
        return f'<Perfil {self.nome}>'
