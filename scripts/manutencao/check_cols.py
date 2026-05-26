from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    tables = ['comercial_revendedores', 'comercial_influenciadores', 'comercial_estilistas']
    for table in tables:
        print(f"\n--- {table} ---")
        try:
            result = db.session.execute(text(f"PRAGMA table_info({table})"))
            for row in result:
                print(row[1])
        except Exception as e:
            print(f"Erro ao verificar tabela {table}: {e}")
