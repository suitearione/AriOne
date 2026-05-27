# =============================================================================
# Caminho  : app/models/usuario.py
# Arquivo  : usuario.py
# Função   : Model SQLAlchemy da entidade Usuario.
# Descrição: Gerencia autenticação via Flask-Login e Werkzeug. Vincula o
#            usuário a uma Empresa pela FK empresa_id → empresas.id.
#            Expõe properties nome_exibicao e foto_url para uso nos templates.
# =============================================================================

from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'

    id         = db.Column(db.Integer, primary_key=True)
    usuario    = db.Column(db.String(50), unique=True, nullable=True) # Nome de login personalizado
    nome       = db.Column(db.String(100), nullable=False)
    apelido    = db.Column(db.String(60))
    email      = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(256), nullable=False)
    foto       = db.Column(db.String(255))
    perfil     = db.Column(db.String(20), default='operador') # Legado, manter para não quebrar compatibilidade
    
    perfil_id  = db.Column(db.Integer, db.ForeignKey('perfis.id'), nullable=True)
    cpf        = db.Column(db.String(20), nullable=True)
    expiracao_senha = db.Column(db.Date, nullable=True)
    ativo      = db.Column(db.Boolean, default=True)
    habilitar_2fa = db.Column(db.Boolean, default=False)
    empresas_acesso = db.Column(db.String(255), nullable=True) # Ex: "1,2,3" ids das empresas permitidas

    # ✅ FK correta: Integer apontando para empresas.id
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=True)
    empresa    = db.relationship('Empresa', backref='usuarios', foreign_keys=[empresa_id])

    # ── Senha ──────────────────────────────────────────────────────────────
    def set_password(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_password(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def check_senha(self, senha):
        """Alias para compatibilidade com código legado."""
        return self.check_password(senha)

    # ── Properties ─────────────────────────────────────────────────────────
    @property
    def nome_exibicao(self):
        """Retorna apelido se cadastrado, senão o primeiro nome."""
        if self.apelido and self.apelido.strip():
            return self.apelido.strip()
        return self.nome.split()[0]

    @property
    def foto_url(self):
        """Retorna o caminho da foto ou o avatar padrão."""
        if self.foto and self.foto.strip():
            return self.foto.strip()
        return 'usuarios/avatar.png'