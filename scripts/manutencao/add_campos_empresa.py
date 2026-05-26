from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Adicionar campo objeto_social
        db.session.execute(text("ALTER TABLE empresas ADD COLUMN objeto_social VARCHAR(50)"))
        print("Campo objeto_social adicionado com sucesso")
    except Exception as e:
        print(f"Erro ao adicionar campo objeto_social: {e}")
    
    try:
        # Adicionar campo email
        db.session.execute(text("ALTER TABLE empresas ADD COLUMN email VARCHAR(200)"))
        print("Campo email adicionado com sucesso")
    except Exception as e:
        print(f"Erro ao adicionar campo email: {e}")
    
    db.session.commit()
    print("Migração concluída")
