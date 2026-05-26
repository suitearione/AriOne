import sqlite3
import os

db_path = 'instance/arione.db'
if not os.path.exists(db_path):
    print("Banco de dados não encontrado em instance/arione.db")
    exit()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Lista de colunas para adicionar
columns = [
    ('tipo_pessoa', 'TEXT DEFAULT "PJ"'),
    ('cpf', 'TEXT'),
    ('rg', 'TEXT'),
    ('data_nascimento', 'DATE'),
    ('profissao', 'TEXT'),
    ('pis_pasep', 'TEXT'),
    ('regime_tributario', 'TEXT'),
    ('natureza_juridica', 'TEXT'),
    ('cnae_principal', 'TEXT'),
    ('cnae_secundario', 'TEXT'),
    ('retencao_irrf', 'TEXT'),
    ('declaracao_ir', 'TEXT')
]

for col_name, col_type in columns:
    try:
        cursor.execute(f"ALTER TABLE empresas ADD COLUMN {col_name} {col_type}")
        print(f"Coluna {col_name} adicionada com sucesso.")
    except sqlite3.OperationalError:
        print(f"Coluna {col_name} já existe (pulando).")

conn.commit()
conn.close()
print("\nSincronização concluída com sucesso!")
