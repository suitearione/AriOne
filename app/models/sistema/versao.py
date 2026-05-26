# =============================================================================
# Caminho: /app/models/sistema/versao.py
# Função : Entidade de versionamento e controle de changelog do AriOne.
# =============================================================================

from app.extensions import db
from datetime import datetime

class Versao(db.Model):
    # Nome da tabela no banco de dados
    __tablename__ = 'versoes'

    # Identificador único da versão
    id = db.Column(
        db.Integer, 
        primary_key=True
    )

    # ── Identificação ──────────────────────────────────────────────────────
    
    # Número da versão (ex: v1.04.05)
    numero = db.Column(
        db.String(20), 
        nullable=False, 
        unique=True
    )
    
    # Título ou resumo da atualização
    titulo = db.Column(
        db.String(200)
    )
    
    # Breve sinopse do objetivo da versão
    sinopse = db.Column(
        db.String(500)
    )
    
    # Status atual (dev, homologacao, publicada)
    status = db.Column(
        db.String(20), 
        default='dev'
    )

    # ── Datas e Auditoria ──────────────────────────────────────────────────
    
    # Data e Hora de início do desenvolvimento
    data_inicio = db.Column(
        db.DateTime
    )
    
    # Data prevista para lançamento
    data_previsao = db.Column(
        db.DateTime
    )
    
    # Data e Hora em que foi para produção
    data_publicacao = db.Column(
        db.DateTime
    )
    
    # Data de criação do registro (UTC)
    criado_em = db.Column(
        db.DateTime, 
        default=datetime.utcnow
    )
    
    # Data da última alteração no registro
    atualizado_em = db.Column(
        db.DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )

    # ── Conteúdo Técnico ───────────────────────────────────────────────────
    
    # Texto detalhado das melhorias e correções
    changelog = db.Column(
        db.Text
    )
    
    # Lista de arquivos modificados (armazenados como texto)
    arquivos = db.Column(
        db.Text
    )
    
    # Notas internas de desenvolvimento
    observacoes = db.Column(
        db.Text
    )

    # ── Responsável ────────────────────────────────────────────────────────
    
    # Nome do autor da versão
    autor = db.Column(
        db.String(100)
    )

    # ── Properties (Lógica de Interface) ───────────────────────────────────

    @property
    def status_label(self):
        """Retorna o texto amigável do status."""
        return {
            'dev': 'Em Desenvolvimento',
            'homologacao': 'Em Homologação',
            'publicada': 'Publicada',
        }.get(self.status, self.status)

    @property
    def status_cor(self):
        """Retorna a cor hexadecimal baseada no status."""
        return {
            'dev': '#E67E22',
            'homologacao': '#0072CE',
            'publicada': '#27AE60',
        }.get(self.status, '#888')

    @property
    def arquivos_lista(self):
        """Converte o texto de arquivos em uma lista real para o template."""
        if not self.arquivos:
            return []
        # Quebra o texto por linha e remove espaços vazios
        return [
            a.strip() 
            for a in self.arquivos.split('\n') 
            if a.strip()
        ]

class VersaoAtividade(db.Model):
    """Logs de atividades específicas dentro de uma versão (Timeline de Engenharia)"""
    __tablename__ = 'versoes_atividades'

    id = db.Column(db.Integer, primary_key=True)
    versao_id = db.Column(db.Integer, db.ForeignKey('versoes.id'), nullable=False)
    
    data_hora = db.Column(db.DateTime, default=datetime.now)
    tipo = db.Column(db.String(20), default='info') # feature, bugfix, refactor, ui
    descricao = db.Column(db.Text, nullable=False)

    # Relacionamento
    versao = db.relationship('Versao', backref=db.backref('atividades', lazy=True, cascade="all, delete-orphan"))

    @property
    def tipo_icon(self):
        return {
            'feature': 'fa-rocket',
            'bugfix': 'fa-bug',
            'refactor': 'fa-tools',
            'ui': 'fa-paint-brush',
            'info': 'fa-info-circle'
        }.get(self.tipo, 'fa-circle')

    @property
    def tipo_cor(self):
        return {
            'feature': '#27ae60',
            'bugfix': '#e74c3c',
            'refactor': '#f39c12',
            'ui': '#9b59b6',
            'info': '#3498db'
        }.get(self.tipo, '#888')