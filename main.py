from app import create_app, db
import os
import sqlite3
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

app = create_app()

def patch_db_hcm():
    uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if not uri.startswith('sqlite:///'): return
    db_path = uri.replace('sqlite:///', '')
    if not os.path.isabs(db_path):
        db_path = os.path.abspath(os.path.join(os.getcwd(), db_path))

    print(f"🛠️ FORCING MASTER PATCH ON: {db_path}")
    if not os.path.exists(db_path): return

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Lote Mestre de Colunas (HCM + Operacional + Financeiro)
    cols = [
        ('rg_orgao','TEXT'),('rg_data_emissao','DATE'),('pis_pasep','TEXT'),
        ('nome_mae','TEXT'),('nome_pai','TEXT'),('titulo_eleitor','TEXT'),
        ('reservista','TEXT'),('email_pessoal','TEXT'),('email_corporativo','TEXT'),
        ('whatsapp','TEXT'),('gestor_id','INTEGER'),('nivel_hierarquico','TEXT'),
        ('turno','TEXT'),('regime_escala','TEXT'),('ponto_tolerancia','INTEGER DEFAULT 5'),
        ('unidade_negocio','TEXT'),('aso_data','DATE'),('aso_validade','DATE'),
        ('epi_entregues','TEXT'),('tipo_sanguineo','TEXT'),('alergias','TEXT'),
        ('cnh','TEXT'),('cnh_categoria','TEXT'),
        ('tipo_conta','TEXT'),('foto','TEXT'),('path_documentos','TEXT'),
        ('jornada_entrada','TEXT'),('jornada_saida','TEXT'),('jornada_intervalo','TEXT'),
        ('centro_custo_id','INTEGER'),('matricula','TEXT'),('tipo_contrato','TEXT'),
        ('status','TEXT'),('usuario_id','INTEGER'),('empresa_id','INTEGER'),
        ('cargo_id','INTEGER'),('setor_id','INTEGER'),('cidade','TEXT'),('uf','TEXT')
    ]
    
    for n, t in cols:
        try:
            c.execute(f"ALTER TABLE funcionarios ADD COLUMN {n} {t}")
            print(f"✅ Column {n} added.")
        except sqlite3.OperationalError as e:
            if "duplicate" in str(e).lower(): pass
            else: print(f"❌ Error adding column {n}: {e}")
                
    # Patch Catálogos (SKU e Estrutura)
    catalog_patches = [
        ('cat_insumos', 'sku', 'TEXT'),
        ('cat_insumos', 'preco_custo', 'REAL DEFAULT 0.0'),
        ('cat_embalagens', 'sku', 'TEXT'),
        ('cat_materiaprima', 'preco_custo', 'REAL DEFAULT 0.0'),
        ('cat_acessorios', 'classificacao_id', 'INTEGER'),
        ('cat_acessorios', 'unidade_id', 'INTEGER'),
        ('cat_embalagens', 'classificacao_id', 'INTEGER'),
        ('cat_tamanhos', 'fator_consumo', 'REAL DEFAULT 1.0'),
        ('cat_produtos_variacoes', 'custo_producao', 'REAL DEFAULT 0.0')
    ]
    for table, col, dtype in catalog_patches:
        try:
            c.execute(f"ALTER TABLE {table} ADD COLUMN {col} {dtype}")
            print(f"✅ Column {col} added to {table}.")
        except sqlite3.OperationalError:
            pass

    # Patch Orçamentos de Venda
    orc_patches = [
        ('op_vendas_orcamentos', 'vendedor_id', 'INTEGER'),
        ('op_vendas_orcamentos', 'tipo_venda', 'TEXT DEFAULT "Produtos"'),
        ('op_vendas_orcamentos', 'data_entrega', 'DATE'),
        ('op_vendas_orcamentos', 'hora_entrega', 'TEXT'),
        ('op_vendas_orcamentos', 'valor_desconto', 'REAL DEFAULT 0.0'),
        ('op_vendas_orcamentos', 'outros_custos', 'REAL DEFAULT 0.0'),
        ('op_vendas_orcamentos', 'total_frete', 'REAL DEFAULT 0.0'),
        ('op_vendas_orcamentos', 'total_liquido', 'REAL DEFAULT 0.0'),
        ('op_vendas_orcamentos', 'forma_envio', 'TEXT'),
        ('op_vendas_orcamentos', 'ent_cep', 'TEXT'),
        ('op_vendas_orcamentos', 'ent_logradouro', 'TEXT'),
        ('op_vendas_orcamentos', 'ent_numero', 'TEXT'),
        ('op_vendas_orcamentos', 'ent_bairro', 'TEXT'),
        ('op_vendas_orcamentos', 'ent_cidade', 'TEXT'),
        ('op_vendas_orcamentos', 'ent_uf', 'TEXT'),
        ('op_vendas_orcamentos', 'ent_complemento', 'TEXT'),
        ('op_vendas_orcamentos', 'observacoes', 'TEXT')
    ]
    for table, col, dtype in orc_patches:
        try:
            c.execute(f"ALTER TABLE {table} ADD COLUMN {col} {dtype}")
            print(f"✅ Column {col} added to {table}.")
        except sqlite3.OperationalError:
            pass

    # Patch Pedidos de Venda
    ped_patches = [
        ('op_vendas_pedidos', 'vendedor_id', 'INTEGER'),
        ('op_vendas_pedidos', 'tipo_venda', 'TEXT DEFAULT "Produtos"'),
        ('op_vendas_pedidos', 'valor_desconto', 'REAL DEFAULT 0.0'),
        ('op_vendas_pedidos', 'outros_custos', 'REAL DEFAULT 0.0'),
        ('op_vendas_pedidos', 'total_frete', 'REAL DEFAULT 0.0'),
        ('op_vendas_pedidos', 'total_bruto', 'REAL DEFAULT 0.0'),
        ('op_vendas_pedidos', 'total_liquido', 'REAL DEFAULT 0.0'),
        ('op_vendas_pedidos', 'forma_envio', 'TEXT'),
        ('op_vendas_pedidos', 'ent_cep', 'TEXT'),
        ('op_vendas_pedidos', 'ent_logradouro', 'TEXT'),
        ('op_vendas_pedidos', 'ent_numero', 'TEXT'),
        ('op_vendas_pedidos', 'ent_bairro', 'TEXT'),
        ('op_vendas_pedidos', 'ent_cidade', 'TEXT'),
        ('op_vendas_pedidos', 'ent_uf', 'TEXT'),
        ('op_vendas_pedidos', 'ent_complemento', 'TEXT')
    ]
    for table, col, dtype in ped_patches:
        try:
            c.execute(f"ALTER TABLE {table} ADD COLUMN {col} {dtype}")
            print(f"✅ Column {col} added to {table}.")
        except sqlite3.OperationalError:
            pass

    # Patch Financeiro Lançamentos
    fin_patches = [
        ('financeiro_lancamentos', 'numero_documento', 'TEXT'),
        ('financeiro_lancamentos', 'data_lancamento', 'DATETIME'),
        ('financeiro_lancamentos', 'rateio_multiplo', 'BOOLEAN DEFAULT 0')
    ]
    for table, col, dtype in fin_patches:
        try:
            c.execute(f"ALTER TABLE {table} ADD COLUMN {col} {dtype}")
            print(f"✅ Column {col} added to {table}.")
        except sqlite3.OperationalError:
            pass
            
    # Criação da tabela de Rateios Múltiplos
    try:
        c.execute("""CREATE TABLE IF NOT EXISTS financeiro_lancamentos_rateio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lancamento_id INTEGER NOT NULL,
            plano_contas_id INTEGER NOT NULL,
            centro_custo_id INTEGER,
            valor REAL NOT NULL,
            FOREIGN KEY(lancamento_id) REFERENCES financeiro_lancamentos(id) ON DELETE CASCADE,
            FOREIGN KEY(plano_contas_id) REFERENCES financeiro_plano_contas(id),
            FOREIGN KEY(centro_custo_id) REFERENCES hcm_centro_custo(id)
        )""")
        print("✅ Table financeiro_lancamentos_rateio verified/created.")
    except Exception as e:
        print(f"❌ Error creating financeiro_lancamentos_rateio table: {e}")

    # Tabelas Auxiliares Acessórios
    try:
        c.execute("""CREATE TABLE IF NOT EXISTS cat_acessorios_classificacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            ativa BOOLEAN DEFAULT 1
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS cat_embalagens_classificacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS cat_acessorios_fornecedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            acessorio_id INTEGER NOT NULL,
            fornecedor_id INTEGER NOT NULL,
            preco_compra REAL DEFAULT 0.0,
            prazo_entrega INTEGER DEFAULT 1,
            modalidade TEXT DEFAULT 'PRESENCIAL',
            FOREIGN KEY(acessorio_id) REFERENCES cat_acessorios(id),
            FOREIGN KEY(fornecedor_id) REFERENCES fornecedores(id)
        )""")
        
        # Tabelas de Preços (Comercial)
        c.execute("""CREATE TABLE IF NOT EXISTS com_tabelas_precos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            base_calculo TEXT DEFAULT 'venda_base',
            ajuste_tipo TEXT DEFAULT 'porcentagem',
            ajuste_valor REAL DEFAULT 0.0,
            data_inicio DATE,
            data_fim DATE,
            perfil_cliente TEXT DEFAULT 'todos',
            ativa BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )""")
        
        c.execute("""CREATE TABLE IF NOT EXISTS com_tabelas_precos_itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tabela_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            variacao_id INTEGER,
            preco_fixo REAL,
            ajuste_especifico REAL,
            ativa BOOLEAN DEFAULT 1,
            FOREIGN KEY(tabela_id) REFERENCES com_tabelas_precos(id),
            FOREIGN KEY(produto_id) REFERENCES cat_produtos(id)
        )""")
    except Exception as e:
        print(f"❌ Error creating accessory tables: {e}")


    conn.commit()
    conn.close()
    print("✨ HCM MASTER SYNC FINISHED.")

if __name__ == "__main__":
    with app.app_context():
        patch_db_hcm()
        
    port = int(os.getenv("FLASK_PORT", 8081))
    debug = os.getenv("DEBUG_MODE", "True").lower() == "true"
    use_https = os.getenv("USE_HTTPS", "False").lower() == "true"
    
    ssl_context = 'adhoc' if use_https else None
    
    if use_https:
        print("🔒 RUNNING WITH AD-HOC HTTPS (Self-signed)")
    
    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug,
        ssl_context=ssl_context
    )