# /app/scripts/reset_system.py
# Bloco: Criacao de Usuario com campo senha_hash

from app import create_app
from app.extensions import db
from app.models.usuario import Usuario
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Recria as tabelas
    db.create_all()
    
    # Busca o admin com a credencial canônica do sistema
    admin = Usuario.query.filter_by(email='admin@arione.com.br').first()
    
    if not admin:
        print("Criando Administrador com campo senha_hash...")
        novo_admin = Usuario(
            nome='Administrador AriOne',
            email='admin@arione.com.br',
            senha_hash=generate_password_hash('admin123', method='pbkdf2:sha256'),
            perfil='admin'
        )
        db.session.add(novo_admin)
        db.session.commit()
        print("------------------------------------------")
        print("SUCESSO: Usuario criado!")
        print("Login: admin@arione.com.br")
        print("Senha: admin123")
        print("------------------------------------------")
    else:
        print("O usuario ja existe.")