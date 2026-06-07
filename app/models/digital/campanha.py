# app/models/digital/campanha.py
from datetime import datetime
from app.extensions import db

class Campanha(db.Model):
    __tablename__ = 'campanha'

    id                    = db.Column(db.Integer, primary_key=True)
    nome_campanha         = db.Column(db.String(120), nullable=False)
    identificador_webhook = db.Column(db.String(120), nullable=False, unique=True)
    status                = db.Column(db.String(20), default='Ativa')
    vendedor_id           = db.Column(db.Integer, db.ForeignKey('comercial_vendedores.id'), nullable=True)
    investimento_estimado = db.Column(db.Float, default=0.0)
    valor_diario          = db.Column(db.Float, default=0.0)
    data_inicio           = db.Column(db.Date, nullable=True)
    data_final            = db.Column(db.Date, nullable=True)
    data_cadastro         = db.Column(db.DateTime, default=datetime.utcnow)

    vendedor = db.relationship('Vendedor', backref='campanhas', lazy=True)

    def __repr__(self):
        return f'<Campanha {self.nome_campanha}>'