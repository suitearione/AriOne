# =============================================================================
# Caminho: app/models/sistema/status.py
# Função : Centraliza todos os Status de documentos do AriOne (Quiet Luxury)
# =============================================================================

from app.extensions import db
from datetime import datetime

class StatusWorkflow(db.Model):
    __tablename__ = 'sistema_status'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    tipo = db.Column(db.String(50), nullable=False) # Orçamento Venda, Pedido Venda, Ordem Produção, etc.
    cor = db.Column(db.String(20), default='#2980B9') # Cor Hex do Badge
    icone = db.Column(db.String(50), default='fas fa-circle')
    ordem = db.Column(db.Integer, default=0) # Ordem de exibição no fluxo
    ativa = db.Column(db.Boolean, default=True)
    
    # 📊 Integração com Dashboard
    dashboard_conta = db.Column(db.Boolean, default=False)
    dashboard_modulo = db.Column(db.String(50))    # 'ORCAMENTOS', 'VENDAS', 'COMPRAS', 'PRODUCAO'
    dashboard_indicador = db.Column(db.String(50)) # 'Ag. Aprovação', 'Finalizados', etc.
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'tipo': self.tipo,
            'cor': self.cor,
            'icone': self.icone,
            'ordem': self.ordem,
            'ativa': self.ativa,
            'dashboard_conta': self.dashboard_conta,
            'dashboard_modulo': self.dashboard_modulo,
            'dashboard_indicador': self.dashboard_indicador
        }
