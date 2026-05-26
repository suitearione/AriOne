# =============================================================================
# Caminho  : app/models/operacoes/producao.py
# Arquivo  : producao.py
# Função   : Modelo de Ordem de Produção (PLM).
# Padrão   : Testes_de_Integridades.md (Seção 3, 6, 10)
# =============================================================================

from app.extensions import db
from datetime import datetime

class OrdemProducao(db.Model):
    __tablename__ = 'op_producao_ordens'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    pedido_venda_id = db.Column(db.Integer, db.ForeignKey('op_vendas_pedidos.id'))
    numero          = db.Column(db.String(20)) # Número operacional (ex: OP-5349)
    
    produto_final_id = db.Column(db.Integer, db.ForeignKey('cat_produtos.id'), nullable=False)
    variacao_id = db.Column(db.Integer, db.ForeignKey('cat_produtos_variacoes.id')) # SKU Alvo
    
    quantidade_planejada = db.Column(db.Numeric(12, 3), nullable=False)
    quantidade_produzida = db.Column(db.Numeric(12, 3), default=0.000)
    
    # Datas de Cronograma (Backward Scheduling)
    data_inicio = db.Column(db.Date)
    data_termino = db.Column(db.Date)
    
    # 🏗️ Engenharia de Produção (JSON para Roteiros Complexos)
    roteiro_corte_json = db.Column(db.JSON) 
    insumos_necessarios_json = db.Column(db.JSON) # Explosão de Materiais (BOM)
    
    status = db.Column(db.String(20), default='Planejada') # Planejada, Em Corte, Em Costura, Acabamento, Finalizada, Cancelada
    
    prioridade = db.Column(db.Integer, default=1) # 1-Baixa, 2-Media, 3-Alta, 4-Urgente
    
    # Relacionamentos
    eventos = db.relationship('OrdemProducaoEvento', backref='op', cascade='all, delete-orphan')

class OrdemProducaoEvento(db.Model):
    """Log de Auditoria e Progressão da OP (Seção 6)"""
    __tablename__ = 'op_producao_eventos'
    id = db.Column(db.Integer, primary_key=True)
    op_id = db.Column(db.Integer, db.ForeignKey('op_producao_ordens.id'), nullable=False)
    data_evento = db.Column(db.DateTime, default=datetime.now)
    
    setor = db.Column(db.String(50)) # Corte, Costura, etc.
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    descricao = db.Column(db.String(255))
    tipo = db.Column(db.String(20)) # INFO, ALERTA, ERRO
