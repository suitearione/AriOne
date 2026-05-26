
import sqlite3
import os

db_path = r'c:\AriOneDEV\instance\arione.db'

if not os.path.exists(db_path):
    print(f"Banco não encontrado em {db_path}")
    exit()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Iniciando sincronização manual de colunas...")

# Colunas para financeiro_plano_contas
cols_pc = [
    ('grupo_gerencial', 'VARCHAR(1)'),
    ('vida_util_meses', 'INTEGER DEFAULT 0'),
    ('valor_residual_percent', 'FLOAT DEFAULT 0.0')
]

for col, tipo in cols_pc:
    try:
        cursor.execute(f"ALTER TABLE financeiro_plano_contas ADD COLUMN {col} {tipo}")
        print(f"✅ Coluna {col} adicionada em financeiro_plano_contas")
    except sqlite3.OperationalError as e:
        print(f"ℹ️ Coluna {col} já existe ou erro: {e}")

conn.commit()
conn.close()
print("Sincronização concluída!")
