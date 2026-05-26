import sqlite3
import os

db_path = 'instance/arione.db'
if not os.path.exists(db_path):
    print("Banco de dados não encontrado em instance/arione.db")
    exit()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("🚀 Iniciando atualização do esquema de Versões...")

# 1. Adiciona coluna 'sinopse' na tabela 'versoes'
try:
    cursor.execute("ALTER TABLE versoes ADD COLUMN sinopse TEXT")
    print("✅ Coluna 'sinopse' adicionada na tabela 'versoes'.")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("ℹ️ Coluna 'sinopse' já existe.")
    else:
        print(f"❌ Erro ao adicionar 'sinopse': {e}")

# 2. Cria tabela 'versoes_atividades'
try:
    cursor.execute("""
        CREATE TABLE versoes_atividades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            versao_id INTEGER NOT NULL,
            data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
            tipo TEXT DEFAULT 'info',
            descricao TEXT NOT NULL,
            FOREIGN KEY (versao_id) REFERENCES versoes (id)
        )
    """)
    print("✅ Tabela 'versoes_atividades' criada com sucesso.")
except sqlite3.OperationalError as e:
    if "already exists" in str(e).lower():
        print("ℹ️ Tabela 'versoes_atividades' já existe.")
    else:
        print(f"❌ Erro ao criar tabela: {e}")

conn.commit()
conn.close()
print("\n💎 Banco de Dados sincronizado com as novas ferramentas de Engenharia!")
