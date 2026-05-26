# =============================================================================
# Caminho  : app/models/gestao/patrimonio.py
# Arquivo  : patrimonio.py
# Função   : Model para Gestão de Patrimônio (Ativo Imobilizado)
# =============================================================================

from app import db
from datetime import datetime

class Patrimonio(db.Model):
    __tablename__ = 'financeiro_patrimonio'
    
    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), index=True)
    
    # Vinculação com o Plano de Contas (Ex: 1.4.001 - Máquinas)
    plano_contas_id = db.Column(db.Integer, db.ForeignKey('financeiro_plano_contas.id'))
    
    categoria = db.Column(db.String(50), default='OUTROS') # IMOVEL, VEICULO, MAQUINA, SOFTWARE, ETC
    descricao = db.Column(db.String(150), nullable=False)
    tag_patrimonial = db.Column(db.String(50), unique=True) # Etiqueta/Série
    
    detalhes = db.Column(db.Text) # JSON com atributos flexíveis (placa, chassi, área, etc)
    
    valor_aquisicao = db.Column(db.Float, default=0.0)
    valor_residual = db.Column(db.Float, default=0.0)
    data_aquisicao = db.Column(db.DateTime, default=datetime.utcnow)
    
    vida_util_meses = db.Column(db.Integer, default=60)
    
    # Depreciação Acumulada (Valor que já foi "gasto" contabilmente)
    depreciacao_acumulada = db.Column(db.Float, default=0.0)
    
    # Status: ATIVO, BAIXADO, VENDIDO
    status = db.Column(db.String(20), default='ATIVO')
    
    observacoes = db.Column(db.Text)
    
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def valor_contabil_atual(self):
        """Retorna o valor do bem hoje (Aquisição - Depreciação Acumulada)"""
        return max(self.valor_aquisicao - self.depreciacao_acumulada, self.valor_residual)

    def to_dict(self):
        return {
            'id': self.id,
            'descricao': self.descricao,
            'tag_patrimonial': self.tag_patrimonial,
            'valor_aquisicao': self.valor_aquisicao,
            'valor_contabil': self.valor_contabil_atual(),
            'data_aquisicao': self.data_aquisicao.strftime('%Y-%m-%d'),
            'status': self.status
        }
