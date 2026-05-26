# create_user_minimo.py
from app import create_app
from app.extensions import db
from werkzeug.security import generate_password_hash
from sqlalchemy import text

app = create_app()

with app.app_context():
    db.session.execute(
        text("""
        INSERT INTO usuarios (nome_completo, email, login, senha_hash, status)
        VALUES (:nome, :email, :login, :senha, :status)
        """),
        {
            "nome": "Administrador",
            "email": "adm@arione.com",
            "login": "adm@arione.com",
            "senha": generate_password_hash("123456"),
            "status": "ATIVO"
        }
    )
    db.session.commit()

print("Usuário criado com sucesso.")
