from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        # Tenta adicionar as colunas
        db.session.execute(text("ALTER TABLE clientes ADD COLUMN data_abertura DATE;"))
        print("[OK] Coluna data_abertura adicionada")
    except Exception as e:
        print(f"[INFO] data_abertura ja existe ou erro: {str(e)[:60]}")
    
    try:
        db.session.execute(text("ALTER TABLE clientes ADD COLUMN site VARCHAR(255);"))
        print("[OK] Coluna site adicionada")
    except Exception as e:
        print(f"[INFO] site ja existe ou erro: {str(e)[:60]}")
    
    try:
        db.session.commit()
        print("[OK] Banco de dados atualizado!")
    except Exception as e:
        db.session.rollback()
        print(f"[ERRO] Erro ao atualizar: {e}")
