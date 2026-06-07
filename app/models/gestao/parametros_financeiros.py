# =============================================================================
# Caminho  : app/models/gestao/parametros_financeiros.py
# Arquivo  : parametros_financeiros.py
# Função   : Model para Parâmetros Financeiros Globais da Empresa (Caixa, etc)
# =============================================================================

from app import db

class ParametrosFinanceiros(db.Model):
    __tablename__ = 'financeiro_parametros'
    
    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), unique=True, index=True)
    
    # ── Parâmetros de Frente de Caixa ──
    conta_suprimento_id = db.Column(db.Integer, db.ForeignKey('financeiro_plano_contas.id'), nullable=True)
    cc_suprimento_id = db.Column(db.Integer, db.ForeignKey('centros_custo.id'), nullable=True)
    
    conta_sangria_id = db.Column(db.Integer, db.ForeignKey('financeiro_plano_contas.id'), nullable=True)
    cc_sangria_id = db.Column(db.Integer, db.ForeignKey('centros_custo.id'), nullable=True)
    
    conta_avulso_id = db.Column(db.Integer, db.ForeignKey('financeiro_plano_contas.id'), nullable=True)
    cc_avulso_id = db.Column(db.Integer, db.ForeignKey('centros_custo.id'), nullable=True)
    
    # Relacionamentos para facilitar acesso aos objetos vinculados
    conta_suprimento = db.relationship('PlanoContas', foreign_keys=[conta_suprimento_id])
    cc_suprimento = db.relationship('CentroCusto', foreign_keys=[cc_suprimento_id])
    
    conta_sangria = db.relationship('PlanoContas', foreign_keys=[conta_sangria_id])
    cc_sangria = db.relationship('CentroCusto', foreign_keys=[cc_sangria_id])
    
    conta_avulso = db.relationship('PlanoContas', foreign_keys=[conta_avulso_id])
    cc_avulso = db.relationship('CentroCusto', foreign_keys=[cc_avulso_id])

    def __repr__(self):
        return f'<ParametrosFinanceiros Empresa {self.empresa_id}>'
