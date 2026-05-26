from app import db
from datetime import datetime

class Entregador(db.Model):
    __tablename__ = 'entregadores'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    whatsapp = db.Column(db.String(20))
    tipo_veiculo = db.Column(db.String(20)) # MOTO, CARRO
    placa = db.Column(db.String(10))
    ativo = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Entregador {self.nome}>'
