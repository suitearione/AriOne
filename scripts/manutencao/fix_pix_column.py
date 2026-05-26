import sqlite3
import os

db_path = os.path.join('instance', 'arione.db')

if not os.path.exists(db_path):
    print(f"Banco de dados não encontrado em {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("Tentando adicionar coluna 'pix' em 'centros_custo'...")
    cursor.execute("ALTER TABLE centros_custo ADD COLUMN pix TEXT")
    print("Coluna 'pix' adicionada com sucesso!")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("Coluna 'pix' já existe.")
    else:
        print(f"Erro ao adicionar coluna: {e}")

try:
    print("Tentando adicionar colunas em 'funcionarios' se necessário...")
    # Verificar se as novas colunas existem
    cursor.execute("PRAGMA table_info(funcionarios)")
    cols = [c[1] for c in cursor.fetchall()]
    
    updates = [
        ('rg_orgao', 'TEXT'),
        ('rg_data_emissao', 'DATE'),
        ('pis_pasep', 'TEXT'),
        ('nome_mae', 'TEXT'),
        ('nome_pai', 'TEXT'),
        ('titulo_eleitor', 'TEXT'),
        ('reservista', 'TEXT'),
        ('tipo_sanguineo', 'TEXT'),
        ('alergias', 'TEXT'),
        ('email_corporativo', 'TEXT'),
        ('whatsapp', 'TEXT'),
        ('matricula', 'TEXT'),
        ('tipo_contrato', 'TEXT'),
        ('status', 'TEXT'),
        ('gestor_id', 'INTEGER'),
        ('nivel_hierarquico', 'TEXT'),
        ('unidade_negocio', 'TEXT'),
        ('turno', 'TEXT'),
        ('regime_escala', 'TEXT'),
        ('ponto_tolerancia', 'INTEGER'),
        ('centro_custo_id', 'INTEGER'),
        ('aso_data', 'DATE'),
        ('aso_validade', 'DATE'),
        ('epi_entregues', 'TEXT'),
        ('salario_base', 'NUMERIC'),
        ('peridiocidade', 'TEXT'),
        ('banco', 'TEXT'),
        ('tipo_conta', 'TEXT'),
        ('agencia', 'TEXT'),
        ('conta', 'TEXT'),
        ('pix', 'TEXT'),
        ('foto', 'TEXT'),
        ('path_documentos', 'TEXT'),
        ('usuario_id', 'INTEGER')
    ]
    
    for col_name, col_type in updates:
        if col_name not in cols:
            cursor.execute(f"ALTER TABLE funcionarios ADD COLUMN {col_name} {col_type}")
            print(f"Coluna '{col_name}' adicionada em 'funcionarios'.")

except Exception as e:
    print(f"Erro ao atualizar funcionarios: {e}")

conn.commit()
conn.close()
print("Processo concluído.")
