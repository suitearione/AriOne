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
    
    # Busca o admin
    admin = Usuario.query.filter_by(email='adm@arione.com').first()
    
    if not admin:
        print("Criando Administrador com campo senha_hash...")
        # Criando o objeto com o nome de campo confirmado pelo erro: senha_hash
        novo_admin = Usuario(
            nome='Administrador AriOne',
            email='adm@arione.com',
            senha_hash=generate_password_hash('admin123', method='pbkdf2:sha256'),
            role='admin' # Ajustado para garantir nivel de acesso
        )
        db.session.add(novo_admin)
        db.session.commit()
        print("------------------------------------------")
        print("SUCESSO: Usuario criado!")
        print("Login: adm@arione.com")
        print("Senha: admin123")
        print("------------------------------------------")
    else:
        print("O usuario ja existe.")