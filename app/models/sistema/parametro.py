# =============================================================================
# Caminho: app/models/sistema/parametro.py
# Função : Armazena configurações globais do sistema AriOne.
# =============================================================================

from app.extensions import db

class ParametroSistema(db.Model):
    __tablename__ = 'sistema_parametros'
    
    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(50), unique=True, nullable=False)
    valor = db.Column(db.String(255))
    descricao = db.Column(db.Text)
    grupo = db.Column(db.String(50)) # comercial, fiscal, etc.

    @staticmethod
    def get_valor(chave, default=None):
        param = ParametroSistema.query.filter_by(chave=chave).first()
        return param.valor if param else default

    @staticmethod
    def set_valor(chave, valor, descricao=None, grupo=None):
        param = ParametroSistema.query.filter_by(chave=chave).first()
        if not param:
            param = ParametroSistema(chave=chave)
        param.valor = str(valor)
        if descricao: param.descricao = descricao
        if grupo: param.grupo = grupo
        db.session.add(param)
        db.session.commit()
