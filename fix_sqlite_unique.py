import sqlite3
import os

db_path = r"c:\AriOneDEV\instance\arione.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute("DROP TABLE IF EXISTS financeiro_plano_contas;")
        print("Tabela financeiro_plano_contas deletada.")
    except Exception as e:
        print("Erro financeiro_plano_contas:", e)

    try:
        cur.execute("DROP TABLE IF EXISTS centros_custo;")
        print("Tabela centros_custo deletada.")
    except Exception as e:
        print("Erro centros_custo:", e)

    conn.commit()
    conn.close()
else:
    print("DB não encontrado em", db_path)
