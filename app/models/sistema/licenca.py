# =============================================================================
# Caminho  : app/models/sistema/licenca.py
# Arquivo  : licenca.py
# Função   : Entidade mestre para gestão de licenciamento (Tenants AriOne).
# Descrição: Armazena dados de governança, contratos e a matriz de permissões
#            habilitadas para cada parceiro do ecossistema AriOne.
# =============================================================================

from datetime import datetime
from app import db

class Licenca(db.Model):
    __tablename__ = 'sistema_licencas'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # ── IDENTIFICAÇÃO & CONTATO ──────────────────────────────────────────────
    nome_parceiro  = db.Column(db.String(200), nullable=False)
    cnpj_cpf       = db.Column(db.String(20), nullable=True)
    contato_master = db.Column(db.String(100), nullable=True)
    email_gestao   = db.Column(db.String(200), nullable=True)
    whatsapp_gestor = db.Column(db.String(20), nullable=True)
    
    # ── GEOPOLÍTICA ──────────────────────────────────────────────────────────
    cidade = db.Column(db.String(100), nullable=True)
    uf     = db.Column(db.String(2), nullable=True)
    pais   = db.Column(db.String(100), default='Brasil')
    
    # ── GOVERNANÇA & CONTRATO ────────────────────────────────────────────────
    status          = db.Column(db.String(50), default='ATIVO') # ATIVO, NEGOCIACAO, SUSPENSO, etc
    tipo_cobranca   = db.Column(db.String(50), nullable=True)    # MENSAL, ANUAL, VITALICIA
    inicio_cobranca = db.Column(db.Date, nullable=True)
    assinatura_url  = db.Column(db.String(500), nullable=True)
    anexos_json     = db.Column(db.Text, nullable=True)          # Lista de arquivos
    
    # ── SINCRONIZAÇÃO DE ENGENHARIA ──────────────────────────────────────────
    # Matriz de permissões licenciadas (ex: {"permissao_cadastros_geral": true, ...})
    matriz_licenciamento = db.Column(db.JSON, nullable=True)
    
    # ── METADADOS ────────────────────────────────────────────────────────────
    criado_em     = db.Column(db.DateTime, default=datetime.now)
    atualizado_em = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<Licenca {self.nome_parceiro} - {self.status}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome_parceiro,
            'cnpj': self.cnpj_cpf,
            'contato': self.contato_master,
            'cidade': self.cidade,
            'uf': self.uf,
            'status': self.status,
            'inicio_cobranca': self.inicio_cobranca.isoformat() if self.inicio_cobranca else None,
            'matriz': self.matriz_licenciamento
        }
