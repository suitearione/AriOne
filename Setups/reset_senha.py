# reset_senha.py (RAIZ do projeto)
# Execute: python reset_senha.py

from app import create_app
from app.extensions import db
from app.models.usuario import Usuario

app = create_app()

with app.app_context():
    # Lista todos os usuários cadastrados
    usuarios = Usuario.query.all()
    
    if not usuarios:
        print("Nenhum usuário encontrado. Criando usuário admin...")
        novo = Usuario(nome="Admin", email="admin@arione.com")
        novo.set_password("admin123")
        db.session.add(novo)
        db.session.commit()
        print("✅ Usuário criado!")
        print("   E-mail: admin@arione.com")
        print("   Senha:  admin123")
    else:
        print("Usuários encontrados:")
        for u in usuarios:
            print(f"  [{u.id}] {u.nome} — {u.email}")
        
        print("\nDigite o ID do usuário para resetar a senha:")
        uid = int(input("> "))
        
        usuario = Usuario.query.get(uid)
        if usuario:
            nova_senha = input(f"Nova senha para '{usuario.nome}': ")
            usuario.set_password(nova_senha)
            db.session.commit()
            print(f"✅ Senha de '{usuario.nome}' resetada com sucesso!")
        else:
            print("❌ Usuário não encontrado.")