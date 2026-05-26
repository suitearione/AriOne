# =============================================================================
# Script de Migração SQLite -> PostgreSQL
# =============================================================================
import sqlite3
import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

load_dotenv()

# Configurações
SQLITE_DB = 'instance/arione.db'
POSTGRES_URL = os.getenv('DATABASE_URL')

def migrate_table(sqlite_conn, pg_conn, table_name):
    """Migra uma tabela do SQLite para PostgreSQL"""
    print(f"Migrando tabela: {table_name}")

    # Obtém dados do SQLite
    sqlite_cur = sqlite_conn.cursor()
    sqlite_cur.execute(f"SELECT * FROM {table_name}")
    columns = [description[0] for description in sqlite_cur.description]
    rows = sqlite_cur.fetchall()

    if not rows:
        print(f"  Tabela vazia, pulando...")
        return

    # Insere no PostgreSQL
    pg_cur = pg_conn.cursor()
    for row in rows:
        columns_str = ', '.join(columns)
        placeholders = ', '.join(['%s'] * len(columns))
        query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            sql.Identifier(table_name),
            sql.SQL(columns_str),
            sql.SQL(placeholders)
        )
        try:
            pg_cur.execute(query, row)
        except Exception as e:
            print(f"  Erro ao inserir linha: {e}")
            continue

    pg_conn.commit()
    print(f"  {len(rows)} linhas migradas")

def main():
    if not os.path.exists(SQLITE_DB):
        print(f"Erro: Banco SQLite não encontrado em {SQLITE_DB}")
        return

    if not POSTGRES_URL:
        print("Erro: DATABASE_URL não configurado no .env")
        return

    # Conecta ao SQLite
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    sqlite_conn.row_factory = sqlite3.Row

    # Conecta ao PostgreSQL
    pg_conn = psycopg2.connect(POSTGRES_URL)

    # Obtém lista de tabelas
    sqlite_cur = sqlite_conn.cursor()
    sqlite_cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in sqlite_cur.fetchall()]

    print(f"Tabelas encontradas: {len(tables)}")
    print("-" * 50)

    # Migra cada tabela
    for table in tables:
        if table != 'sqlite_sequence':  # Ignora tabela interna
            try:
                migrate_table(sqlite_conn, pg_conn, table)
            except Exception as e:
                print(f"Erro ao migrar {table}: {e}")

    # Fecha conexões
    sqlite_conn.close()
    pg_conn.close()

    print("-" * 50)
    print("Migração concluída!")

if __name__ == '__main__':
    main()
