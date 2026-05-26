# =============================================================================
# Caminho  : app/models/gestao/ponto.py
# Arquivo  : ponto.py
# Função   : Model SQLAlchemy para registro de ponto eletrônico.
# Descrição: Armazena as batidas de ponto dos usuários, com suporte a
#            intervalo e geolocalização.
# =============================================================================

from app.extensions import db
from datetime import datetime

class Ponto(db.Model):
    __tablename__ = 'pontos'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=True)
    
    data = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    
    entrada = db.Column(db.Time, nullable=True)
    saida_intervalo = db.Column(db.Time, nullable=True)
    retorno_intervalo = db.Column(db.Time, nullable=True)
    saida = db.Column(db.Time, nullable=True)
    
    geolocalizacao = db.Column(db.String(100), nullable=True)
    observacao = db.Column(db.Text, nullable=True)
    
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    usuario = db.relationship('Usuario', backref=db.backref('pontos', lazy=True))

    def __repr__(self):
        return f'<Ponto {self.usuario_id} - {self.data}>'
