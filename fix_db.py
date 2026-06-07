# fix_db.py — Rodar na raiz do projeto: python fix_db.py
# Adiciona colunas faltantes na tabela clientes sem apagar dados

from app import create_app, db
from sqlalchemy import text

app = create_app()

COLUNAS = [
    ("empresa_id", "INTEGER REFERENCES empresas(id)"),
]

with app.app_context():
    with db.engine.connect() as conn:
        # Descobre as colunas que já existem
        resultado = conn.execute(text("PRAGMA table_info(clientes)"))
        existentes = {row[1] for row in resultado}

        adicionadas = []
        ja_existiam = []

        for coluna, tipo in COLUNAS:
            if coluna not in existentes:
                conn.execute(text(f"ALTER TABLE clientes ADD COLUMN {coluna} {tipo}"))
                adicionadas.append(coluna)
            else:
                ja_existiam.append(coluna)

        conn.commit()

    print("=" * 50)
    if adicionadas:
        print(f"✅ Colunas adicionadas: {', '.join(adicionadas)}")
    if ja_existiam:
        print(f"ℹ️  Já existiam: {', '.join(ja_existiam)}")
    print("✅ Banco atualizado com sucesso!")
    print("=" * 50)